"""
Filtro de pertinência.

Aplica a árvore de decisão da seção 8.3 do projeto sobre cada acórdão
exauriente do universo empírico bruto, retornando classificação binária
(pertinente ou não pertinente) com registro do passo da árvore em que
a decisão foi tomada e justificativa breve.

Opera em Alternativa B: cada acórdão é submetido individualmente ao modelo.
A agregação por reclamação (para reclamações com múltiplos acórdãos
exaurientes) é feita depois, no processamento dos resultados: se qualquer
acórdão da reclamação satisfaz o critério de pertinência, a reclamação
inteira é considerada pertinente.

Uso:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python filtro_pertinencia.py

Saídas:
    filtro_por_acordao.csv    — resultado do filtro por acórdão individual
    filtro_por_reclamacao.csv — resultado agregado por reclamação
    log_execucao.txt          — log com custo, tempo, eventuais erros
"""

import csv
import json
import os
import random
import sys
import time
from pathlib import Path

import anthropic
import pandas as pd

# -----------------------------------------------------------------------------
# Configuração
# -----------------------------------------------------------------------------

MODELO = "claude-opus-5"
TEMPERATURA = 0
MAX_TOKENS = 1024

ARQUIVO_ENTRADA = "/mnt/user-data/uploads/export_acordaos_2026-08-17_11-19-17.csv"
ARQUIVO_SAIDA_ACORDAOS = "filtro_por_acordao.csv"
ARQUIVO_SAIDA_RECLAMACOES = "filtro_por_reclamacao.csv"
ARQUIVO_LOG = "log_execucao.txt"

CLASSES_SUMARIAS = {"Rcl-MC-Ref", "Rcl-MC-AgR", "Rcl-Ref"}

# -----------------------------------------------------------------------------
# Prompt do filtro (cacheado)
# -----------------------------------------------------------------------------

SYSTEM_PROMPT = """Você é um assistente especializado em análise de decisões do Supremo
Tribunal Federal. Sua tarefa é aplicar uma árvore de decisão sobre acórdãos de
reclamações constitucionais, retornando classificação binária de pertinência.

## Árvore de decisão

Analise a Ementa e a Decisão do acórdão fornecido e responda à seguinte sequência de
perguntas, na ordem indicada.

Passo 1. A reclamação foi conhecida pelo Tribunal?
  - Se SIM: acórdão é PERTINENTE. Registrar passo_arvore = 1.
  - Se NÃO: prosseguir ao Passo 2.

Passo 2. A ausência de aderência ao paradigma da ADPF nº 130 foi motivo do não
conhecimento?
  - Se SIM: acórdão é PERTINENTE. Registrar passo_arvore = 2.
  - Se NÃO: prosseguir ao Passo 3.

Passo 3. O acórdão examinou a questão da aderência ao paradigma da ADPF nº 130 (ainda
que não tenha conhecido por outra razão processual)?
  - Se SIM: acórdão é PERTINENTE. Registrar passo_arvore = 3.
  - Se NÃO: acórdão é NÃO PERTINENTE. Registrar passo_arvore = 0.

## Convenções operacionais

Considera-se "conhecimento" a decisão do Tribunal de admitir o processamento da
reclamação. Frases típicas: "conheço da reclamação", "conheço da reclamação e a julgo
procedente", "julgo procedente a reclamação" (que pressupõe conhecimento).

Considera-se "não conhecimento por ausência de aderência" a hipótese em que o Tribunal
expressamente sustenta que o ato reclamado não guarda identidade material com o
paradigma invocado, ou que a matéria discutida difere daquela decidida na ADPF nº 130.
Frases típicas: "não se conhece por ausência de aderência estrita", "o ato reclamado
não guarda aderência ao paradigma".

Considera-se "exame da aderência" a hipótese em que o Tribunal, ainda que não
conhecendo da reclamação por razão diversa (perda de objeto, ilegitimidade, sucedâneo
recursal, etc.), tece considerações substantivas sobre a compatibilidade material entre
o ato reclamado e o paradigma. Não configura exame a mera menção formal ao paradigma
sem análise substantiva.

## Formato de saída

Responda EXCLUSIVAMENTE com um objeto JSON válido, sem qualquer texto adicional, no
seguinte formato:

{
  "pertinente": "sim" ou "não",
  "passo_arvore": 0, 1, 2 ou 3,
  "justificativa": "uma frase breve explicando a classificação"
}"""


# -----------------------------------------------------------------------------
# Funções
# -----------------------------------------------------------------------------

def carregar_base(caminho):
    """Carrega o CSV e filtra o universo empírico (acórdãos exaurientes)."""
    df = pd.read_csv(caminho, delimiter=";", encoding="utf-8", dtype=str)
    df = df[df["Classe"].str.startswith("Rcl", na=False)].copy()
    df = df[~df["Classe"].isin(["sinonimo: sim", "plural: sim", "radicais: não"])]

    # Excluir cognição sumária
    df = df[~df["Classe"].isin(CLASSES_SUMARIAS)].copy()

    # Preencher NaN em ementa/decisão com string vazia
    df["Ementa"] = df["Ementa"].fillna("")
    df["Decisão"] = df["Decisão"].fillna("")

    # Identificador único do acórdão
    df["id_acordao"] = (
        df["Classe"] + " " + df["Número"].astype(str)
        + df.apply(
            lambda r: f" (inc {r['Incidente']})" if pd.notna(r.get("Incidente")) and
r.get("Incidente") else "",
            axis=1
        )
    )

    return df.reset_index(drop=True)


def montar_conteudo(row):
    """Monta a mensagem do usuário com Ementa e Decisão do acórdão."""
    return f"""Acórdão a analisar:

Classe processual: {row["Classe"]}
Número: {row["Número"]}
Data de julgamento: {row.get("Data de julgamento", "não informado")}

==== EMENTA ====
{row["Ementa"] if row["Ementa"] else "(ementa não disponível)"}

==== DECISÃO ====
{row["Decisão"] if row["Decisão"] else "(decisão não disponível)"}

Aplique a árvore de decisão e responda no formato JSON especificado."""


def classificar_acordao(client, row, tentativa=1, max_tentativas=3):
    """Submete um acórdão à API e retorna dict com classificação."""
    conteudo = montar_conteudo(row)
    try:
        resp = client.messages.create(
            model=MODELO,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURA,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=[{"role": "user", "content": conteudo}],
        )
        texto = resp.content[0].text.strip()

        # Remover eventuais fences de código
        if texto.startswith("```"):
            texto = texto.split("```")[1]
            if texto.startswith("json"):
                texto = texto[4:]
            texto = texto.strip()

        dados = json.loads(texto)

        # Extrair custo do uso
        usage = resp.usage
        input_tokens = getattr(usage, "input_tokens", 0)
        output_tokens = getattr(usage, "output_tokens", 0)
        cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
        cache_creation = getattr(usage, "cache_creation_input_tokens", 0) or 0

        return {
            "pertinente": dados.get("pertinente", "").lower(),
            "passo_arvore": dados.get("passo_arvore", -1),
            "justificativa": dados.get("justificativa", ""),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cache_read_tokens": cache_read,
            "cache_creation_tokens": cache_creation,
            "erro": None,
        }

    except json.JSONDecodeError as e:
        if tentativa < max_tentativas:
            time.sleep(2)
            return classificar_acordao(client, row, tentativa + 1, max_tentativas)
        return {
            "pertinente": "ERRO",
            "passo_arvore": -1,
            "justificativa": f"Falha ao parsear JSON: {e}",
            "input_tokens": 0, "output_tokens": 0,
            "cache_read_tokens": 0, "cache_creation_tokens": 0,
            "erro": str(e),
        }
    except Exception as e:
        if tentativa < max_tentativas:
            time.sleep(2 ** tentativa)
            return classificar_acordao(client, row, tentativa + 1, max_tentativas)
        return {
            "pertinente": "ERRO",
            "passo_arvore": -1,
            "justificativa": f"Falha na API: {e}",
            "input_tokens": 0, "output_tokens": 0,
            "cache_read_tokens": 0, "cache_creation_tokens": 0,
            "erro": str(e),
        }


def estimar_custo(input_tokens, output_tokens, cache_read, cache_creation):
    """Estima custo em USD para Claude Opus 5.

    Preços (padrão Opus 5, agosto de 2026):
      Input:            $5.00 / MTok
      Output:          $25.00 / MTok
      Cache write:      $6.25 / MTok  (25% acima do input)
      Cache read:       $0.50 / MTok  (10% do input)
    """
    custo = (
        (input_tokens / 1_000_000) * 5.00
        + (output_tokens / 1_000_000) * 25.00
        + (cache_creation / 1_000_000) * 6.25
        + (cache_read / 1_000_000) * 0.50
    )
    return custo


def agregar_por_reclamacao(resultados_df):
    """Agrega resultados por reclamação. Alternativa B: reclamação é pertinente
    se qualquer de seus acórdãos exaurientes for pertinente."""
    ag = resultados_df.groupby("Número").agg(
        classes_acordaos=("Classe", lambda x: ", ".join(sorted(x.tolist()))),
        n_acordaos=("Classe", "count"),
        pertinente=("pertinente", lambda x: "sim" if any(v == "sim" for v in x) else
("não" if all(v == "não" for v in x) else "ERRO")),
        passos_arvore=("passo_arvore", lambda x: ", ".join(str(v) for v in x)),
        justificativas=("justificativa", lambda x: " | ".join(x)),
    ).reset_index()
    return ag


# -----------------------------------------------------------------------------
# Execução principal
# -----------------------------------------------------------------------------

def main():
    log_lines = []
    def log(msg):
        print(msg)
        log_lines.append(msg)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERRO: variável ANTHROPIC_API_KEY não configurada.", file=sys.stderr)
        sys.exit(1)

    log(f"[{time.strftime('%H:%M:%S')}] Iniciando filtro de pertinência")
    log(f"Modelo: {MODELO} | Temperatura: {TEMPERATURA}")

    df = carregar_base(ARQUIVO_ENTRADA)
    log(f"Universo empírico carregado: {len(df)} acórdãos exaurientes")
    log(f"Reclamações distintas: {df['Número'].nunique()}")

    # Aleatorizar ordem de submissão
    indices = df.index.tolist()
    random.seed(42)  # semente fixa para reprodutibilidade
    random.shuffle(indices)

    client = anthropic.Anthropic()
    resultados = []
    inicio = time.time()

    for i, idx in enumerate(indices, 1):
        row = df.loc[idx]
        t0 = time.time()
        r = classificar_acordao(client, row)
        dt = time.time() - t0

        resultados.append({
            "id_acordao": row["id_acordao"],
            "Classe": row["Classe"],
            "Número": row["Número"],
            "Data de julgamento": row.get("Data de julgamento", ""),
            "pertinente": r["pertinente"],
            "passo_arvore": r["passo_arvore"],
            "justificativa": r["justificativa"],
            "input_tokens": r["input_tokens"],
            "output_tokens": r["output_tokens"],
            "cache_read_tokens": r["cache_read_tokens"],
            "cache_creation_tokens": r["cache_creation_tokens"],
            "erro": r["erro"],
        })

        marca = "✓" if r["pertinente"] in ("sim", "não") else "✗"
        log(f"  [{i:3d}/{len(indices)}] {marca} {row['id_acordao']:30s} → {r['pertinente']:5s} (passo {r['passo_arvore']}, {dt:.1f}s)")

    tempo_total = time.time() - inicio
    log(f"\n[{time.strftime('%H:%M:%S')}] Execução concluída em {tempo_total/60:.1f} minutos")

    # Salvar resultado por acórdão
    resultados_df = pd.DataFrame(resultados)
    resultados_df.to_csv(ARQUIVO_SAIDA_ACORDAOS, index=False, encoding="utf-8")
    log(f"Resultado por acórdão salvo em: {ARQUIVO_SAIDA_ACORDAOS}")

    # Agregar por reclamação
    agregado = agregar_por_reclamacao(resultados_df)
    agregado.to_csv(ARQUIVO_SAIDA_RECLAMACOES, index=False, encoding="utf-8")
    log(f"Resultado por reclamação salvo em: {ARQUIVO_SAIDA_RECLAMACOES}")

    # Estatísticas
    log("\n=== Estatísticas ===")
    total_input = resultados_df["input_tokens"].sum()
    total_output = resultados_df["output_tokens"].sum()
    total_cache_read = resultados_df["cache_read_tokens"].sum()
    total_cache_creation = resultados_df["cache_creation_tokens"].sum()
    custo = estimar_custo(total_input, total_output, total_cache_read,
total_cache_creation)

    log(f"Tokens input total: {total_input:,}")
    log(f"Tokens output total: {total_output:,}")
    log(f"Tokens cache_read: {total_cache_read:,}")
    log(f"Tokens cache_creation: {total_cache_creation:,}")
    log(f"Custo estimado (Claude Opus 5): USD {custo:.4f}")

    log(f"\nAcórdãos pertinentes: {(resultados_df['pertinente'] == 'sim').sum()}")
    log(f"Acórdãos não pertinentes: {(resultados_df['pertinente'] == 'não').sum()}")
    log(f"Acórdãos com erro: {(resultados_df['pertinente'] == 'ERRO').sum()}")

    log(f"\nReclamações pertinentes: {(agregado['pertinente'] == 'sim').sum()}")
    log(f"Reclamações não pertinentes: {(agregado['pertinente'] == 'não').sum()}")

    # Salvar log
    Path(ARQUIVO_LOG).write_text("\n".join(log_lines), encoding="utf-8")


if __name__ == "__main__":
    main()

