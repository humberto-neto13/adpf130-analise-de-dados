"""
Piloto Fase 2 — Submissão via Batch API.

Codifica as 16 variáveis da matriz nos acórdãos presentes na pasta ./textos,
usando o manual de codificação completo como SYSTEM_PROMPT (aplicando prompt
caching para reduzir custo).

Uso:
    set ANTHROPIC_API_KEY=sk-ant-...
    py submeter_batch_fase2.py

Requisitos:
    - Pasta ./textos com os arquivos .txt dos acórdãos da amostra (a seleção
      é feita externamente pelo pesquisador antes da execução).
    - Arquivo manual_codificacao.txt na mesma pasta do script.
"""

import json
import os
import random
import sys
import time
from pathlib import Path

import anthropic

# -----------------------------------------------------------------------------
# Configuração
# -----------------------------------------------------------------------------

MODELO = "claude-sonnet-5"
MAX_TOKENS = 32000  # teto elevado: alguns acórdãos consomem muito raciocínio interno (extended thinking) antes de produzir o texto final

PASTA_TXT = "./textos"
ARQUIVO_MANUAL = "manual_codificacao.txt"
ARQUIVO_JSONL = "requisicoes_batch_fase2.jsonl"
ARQUIVO_BATCH_ID = "batch_id_fase2.txt"


# -----------------------------------------------------------------------------
# Construção do SYSTEM_PROMPT
# -----------------------------------------------------------------------------

INSTRUCOES_GERAIS = """Você é um assistente especializado em análise de decisões do Supremo Tribunal Federal. Sua tarefa é codificar dezesseis variáveis de um acórdão em reclamação constitucional fundada na ADPF nº 130, seguindo estritamente as definições operacionais do manual de codificação transcrito abaixo.

## Instruções para maximizar consistência

Estas instruções são essenciais para a qualidade e a reprodutibilidade da codificação.

Primeira. Aplique as definições operacionais literalmente. Não infira além do que o texto do acórdão sustenta explicitamente. Se o texto do acórdão não menciona um dado, ou o menciona de forma ambígua, prefira marcar "ND" (não determinável) em vez de forçar classificação a partir de indícios fracos.

Segunda. Não introduza raciocínio criativo ou associações que ultrapassem o que o manual autoriza. As classes das variáveis são exaustivas dentro do escopo de cada uma; se um caso parece não se encaixar em nenhuma classe, revise se você está lendo corretamente o manual antes de considerar a possibilidade de que o caso seja atípico.

Terceira. Antes de finalizar cada codificação, releia a classe atribuída e confirme que o caso satisfaz a definição operacional em todos os elementos. Verifique cada palavra da definição contra o caso, não apenas o sentido geral.

Quarta. Preserve a linguagem do Tribunal quando pertinente. Nas variáveis com codificação aberta ou com registro textual (notadamente V16), reproduza a formulação empregada pelo Tribunal, sem reformulação em sua linguagem própria.

Quinta. Trate cada acórdão como caso isolado. Não use informações que você poderia ter sobre outros acórdãos da mesma reclamação, ou sobre a jurisprudência do STF em geral, para codificar variáveis que devem ser extraídas do acórdão específico submetido.

## Manual de codificação

O texto abaixo é o manual de codificação. Aplique-o na íntegra."""

FORMATO_SAIDA = """
## Formato de saída

Responda EXCLUSIVAMENTE com um objeto JSON válido, sem qualquer texto adicional (nem antes, nem depois), no seguinte formato:

{
  "V1_FUND": {
    "classes": ["a", "b"],
    "justificativa": "frase breve indicando quais fundamentos foram identificados"
  },
  "V2_MOD_REST": {
    "classes": ["a", "c"],
    "justificativa": "frase breve indicando quais modalidades de restrição foram identificadas"
  },
  "V3_MOM_REST": {
    "classe": "a" | "b" | "c" | "ND",
    "justificativa": "frase breve"
  },
  "V4_SUJ_COM": {
    "classe": "a" | "b" | "c" | "d" | "e" | "f" | "g" | "ND",
    "justificativa": "frase breve"
  },
  "V5_MEIO": {
    "classes": ["a", "c"],
    "justificativa": "frase breve indicando quais meios foram identificados"
  },
  "V6_TRANSC": {
    "classe": "a" | "b" | "c" | "d" | "e" | "ND",
    "justificativa": "frase breve; se houver menção, indicar a passagem em que aparece"
  },
  "V7_DIVERG": {
    "classes": ["a"] | ["b", "d"] | etc,
    "justificativa": "frase breve"
  },
  "V8_ORG": "a" | "b" | "c" | "ND",
  "V9_DATA": "DD/MM/AAAA" ou "ND",
  "V10_REL": "Nome completo do relator" ou "ND",
  "V11_RED": "Nome completo do redator" ou "coincide" ou "ND",
  "V12_VENCIDOS": ["Nome 1", "Nome 2"] ou [] (lista vazia se decisão unânime) ou "ND",
  "V13_ADER": {
    "classe": "a" | "b" | "c" | "ND",
    "justificativa": "frase breve"
  },
  "V14_CONHEC": {
    "classe": "a" | "b" | "c" | "ND",
    "justificativa": "frase breve"
  },
  "V15_MERITO": {
    "classe": "a" | "b" | "c" | "ND",
    "justificativa": "frase breve"
  },
  "V16_DIST": {
    "aplicavel": true | false,
    "razoes": [
      {
        "descricao": "razão de distinção em linguagem sintética preservando o núcleo argumentativo do Tribunal",
        "citacao": "passagem literal do acórdão em que a razão é articulada",
        "localizacao": "página ou parágrafo, quando identificável"
      }
    ]
  }
}

Observações sobre o formato:

Para variáveis com codificação múltipla (V1, V2, V5, V7), o campo é "classes" (plural, lista); para variáveis com codificação única, o campo é "classe" (singular, string).

Para V8 a V12, não é necessária justificativa (dado autoevidente).

Para V16, se a variável não for aplicável ao caso, retorne {"aplicavel": false, "razoes": []}. Se for aplicável, preencha as razões conforme o schema, com uma entrada por razão autônoma.

Justificativas devem ser breves (uma frase) e apontar diretamente ao texto do acórdão que sustenta a classificação. Não repita a definição do manual; indique o elemento do caso concreto que faz a definição se aplicar."""


def montar_system_prompt():
    manual = Path(ARQUIVO_MANUAL).read_text(encoding='utf-8')
    return INSTRUCOES_GERAIS + "\n\n" + manual + "\n\n" + FORMATO_SAIDA


# -----------------------------------------------------------------------------
# Execução
# -----------------------------------------------------------------------------

def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERRO: variável ANTHROPIC_API_KEY não configurada.", file=sys.stderr)
        sys.exit(1)

    if not Path(ARQUIVO_MANUAL).exists():
        print(f"ERRO: arquivo {ARQUIVO_MANUAL} não encontrado.", file=sys.stderr)
        print("Coloque o manual de codificação na mesma pasta do script.", file=sys.stderr)
        sys.exit(1)

    print(f"[{time.strftime('%H:%M:%S')}] Preparando submissão à Batch API (Fase 2)")
    print(f"Modelo: {MODELO}")

    pasta = Path(PASTA_TXT)
    if not pasta.exists():
        print(f"ERRO: pasta {PASTA_TXT} não encontrada.", file=sys.stderr)
        sys.exit(1)

    arquivos = sorted(pasta.glob("*.txt"))
    if not arquivos:
        print(f"ERRO: nenhum arquivo .txt encontrado em {PASTA_TXT}.", file=sys.stderr)
        sys.exit(1)

    random.seed(42)
    random.shuffle(arquivos)

    print(f"Submetendo {len(arquivos)} arquivos.")

    system_prompt = montar_system_prompt()
    print(f"SYSTEM_PROMPT: {len(system_prompt):,} caracteres (será cacheado)")

    print(f"\nGerando {ARQUIVO_JSONL}...")
    requests_list = []
    for arquivo in arquivos:
        try:
            texto = arquivo.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  ✗ {arquivo.name}: erro ao ler ({e})")
            continue

        conteudo = f"""Arquivo: {arquivo.name}

=================== INTEIRO TEOR DO ACÓRDÃO ===================

{texto}

=================== FIM DO INTEIRO TEOR ===================

Aplique o manual de codificação às dezesseis variáveis e responda no formato JSON especificado."""

        custom_id = arquivo.stem.replace(".", "_")

        requisicao = {
            "custom_id": custom_id,
            "params": {
                "model": MODELO,
                "max_tokens": MAX_TOKENS,
                "system": [
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                "messages": [{"role": "user", "content": conteudo}],
            }
        }
        requests_list.append(requisicao)

    # Salvar JSONL local para referência
    with open(ARQUIVO_JSONL, "w", encoding="utf-8") as f:
        for r in requests_list:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    tamanho = Path(ARQUIVO_JSONL).stat().st_size
    print(f"Arquivo gerado: {tamanho:,} bytes")

    print(f"\nSubmetendo à Batch API...")
    client = anthropic.Anthropic()
    batch = client.messages.batches.create(requests=requests_list)

    print(f"\n=== Lote criado ===")
    print(f"ID: {batch.id}")
    print(f"Status: {batch.processing_status}")

    Path(ARQUIVO_BATCH_ID).write_text(batch.id, encoding="utf-8")
    print(f"\nID salvo em: {ARQUIVO_BATCH_ID}")
    print(f"\nUse 'py processar_batch_fase2.py' para baixar e processar os resultados.")


if __name__ == "__main__":
    main()
