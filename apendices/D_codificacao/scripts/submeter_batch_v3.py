"""
Codificação da população — submissão à Batch API (manual de codificação, versão 3).

Codifica as dezesseis variáveis em todos os acórdãos da pasta ./textos, em ordem
aleatória com semente registrada, usando o manual da versão 3 como parte do
prompt de sistema, com prompt caching.

Uso:
    set ANTHROPIC_API_KEY=sk-ant-...
    py submeter_batch_v3.py            (gera o JSONL e submete)
    py submeter_batch_v3.py --simular  (só gera o JSONL, sem submeter)
    py submeter_batch_v3.py --forcar   (submete mesmo com batch_id_v3.txt já existente)

Estrutura esperada:
    submeter_batch_v3.py
    processar_batch_v3.py
    manual-codificacao-v3.md
    textos/   (arquivos .txt dos acórdãos, um por acórdão)
"""

import json
import os
import random
import re
import sys
import time
from pathlib import Path

import anthropic

# -----------------------------------------------------------------------------
# Configuração (mesmos modelo e max_tokens da versão final do piloto de calibração)
# -----------------------------------------------------------------------------

MODELO = "claude-sonnet-5"
MAX_TOKENS = 32000  # valor final do piloto de calibração (8.000 -> 16.000 -> 32.000); teto de saída, incluído o raciocínio interno
SEMENTE = 42

PASTA_TXT = "./textos"
ARQUIVO_MANUAL = "manual-codificacao-v3.md"
ARQUIVO_JSONL = "requisicoes_batch_v3.jsonl"
ARQUIVO_MAPA = "mapa_custom_id_v3.json"   # custom_id -> nome real do arquivo
ARQUIVO_BATCH_ID = "batch_id_v3.txt"


# -----------------------------------------------------------------------------
# Prompt de sistema
# -----------------------------------------------------------------------------

INSTRUCOES_GERAIS = """Sua tarefa é codificar dezesseis variáveis de um acórdão do Supremo Tribunal Federal em reclamação constitucional fundada na ADPF nº 130, seguindo estritamente as definições do manual de codificação transcrito abaixo.

## Instruções para maximizar consistência

Primeira. Aplique as definições do manual literalmente. Não infira além do que o texto do acórdão sustenta explicitamente. Use ND e NA exatamente nas hipóteses que o manual prevê para cada variável, e não como saída para dúvidas que o manual resolve.

Segunda. Não introduza raciocínio criativo ou associações que ultrapassem o que o manual autoriza. Não crie classes, códigos ou campos que o manual não preveja.

Terceira. Antes de finalizar cada variável, releia a definição da classe atribuída e os casos-fronteira da variável, e confirme que o caso satisfaz a definição em todos os elementos.

Quarta. Identifique a voz de cada trecho (ato reclamado, voto, relatório, partes) conforme o item 1.3 do manual antes de extrair qualquer informação. Muitas variáveis dependem de saber se um trecho é do ato reclamado transcrito, da decisão monocrática transcrita ou do voto atual.

Quinta. Trate cada acórdão como caso isolado. Não use informações que você possa ter sobre outros acórdãos da mesma reclamação ou sobre a jurisprudência do STF em geral.

## Manual de codificação

O texto abaixo é o manual de codificação. Aplique-o na íntegra."""

FORMATO_SAIDA = """
## Formato de saída

Responda EXCLUSIVAMENTE com um objeto JSON válido, sem texto antes ou depois e sem cercas de código, com exatamente as chaves abaixo. Os valores permitidos em cada campo estão indicados; nenhum outro valor é aceito.

{
  "V1_FUND":      {"classes": [...], "justificativa": "..."},
  "V2_MOD_REST":  {"classes": [...], "justificativa": "..."},
  "V3_MOM_REST":  {"classe": "...",  "justificativa": "..."},
  "V4_RECLTE":    {"classes": [...], "justificativa": "..."},
  "V5_MEIO":      {"classes": [...], "justificativa": "..."},
  "V6_TRANSC":    {"classes": [...], "justificativa": "..."},
  "V7_DIVERG":    {"classes": [...], "justificativa": "..."},
  "V16_JURIS":    {"citacoes": [...]},
  "V13_ADER":     {"classe": "...",  "justificativa": "..."},
  "V14_SEGUIM":   {"classe": "...",  "justificativa": "..."},
  "V15_MERITO":   {"classe": "...",  "justificativa": "..."},
  "V8_ORG":       "...",
  "V9_DATA":      "...",
  "V10_REL":      "...",
  "V11_RED":      {"classe": "...", "nome": "..."},
  "V12_VENCIDOS": [...] ou "NA" ou "ND"
}

Valores permitidos:

V1_FUND: lista com uma ou mais letras entre "a", "b", "c", "d", "e", "f", sem repetição; ou ["ND"]. A classe "f" não se combina com outra.
V2_MOD_REST: lista com uma ou mais letras entre "a" e "g", sem repetição; ou ["ND"].
V3_MOM_REST: "anterior", "posterior", "anterior e posterior" ou "ND".
V4_RECLTE: lista com uma ou mais letras entre "a" e "g", sem repetição; ou ["ND"].
V5_MEIO: lista com uma ou mais letras entre "a" e "g", sem repetição; ou ["ND"].
V6_TRANSC: lista com uma ou mais letras entre "a" e "f", sem repetição. Das classes "a", "b" e "c", no máximo uma. A classe "d" não se combina com outra.
V7_DIVERG: lista com uma ou mais letras entre "a" e "f", sem repetição; ou ["ND"]. A classe "a" não se combina com outra.
V16_JURIS: lista de strings no formato do manual ("Rcl 3014", "RE 511961", "Súmula 734", "Súmula Vinculante 38", "Tema 995"), sem repetição; lista vazia [] quando não houver citação.
V13_ADER: "reconhecida", "não reconhecida" ou "ND".
V14_SEGUIM: "negado", "dado", "prejudicada ou extinta" ou "ND".
V15_MERITO: "procedente", "improcedente", "ND" ou "NA".
V8_ORG: "a", "b", "c" ou "ND".
V9_DATA: data no formato "DD/MM/AAAA", ou "ND".
V10_REL: nome completo do relator, como aparece no documento, sem "Min."; ou "ND".
V11_RED: {"classe": "a", "nome": "<nome completo do redator>"} ou {"classe": "b", "nome": null}.
V12_VENCIDOS: lista com o nome completo de cada vencido; "NA" se a decisão foi unânime; "ND" se o extrato registra maioria sem nomear os vencidos.

Justificativas: uma ou duas frases que apontem o trecho do acórdão que sustenta a classificação e digam de que seção ou voz ele vem (por exemplo, "decisão monocrática transcrita no voto do relator", "extrato de ata"). Não repita a definição do manual. Quando registrar ND ou NA, diga por quê."""


def montar_system_prompt(texto_manual):
    return INSTRUCOES_GERAIS + "\n\n" + texto_manual.strip() + "\n\n" + FORMATO_SAIDA


def gerar_custom_id(nome_arquivo, usados):
    """A Batch API exige ^[a-zA-Z0-9_-]{1,64}$. Substitui o resto por '_'
    e garante unicidade. O nome real fica no mapa, e não é reconstruído."""
    base = re.sub(r"[^a-zA-Z0-9_-]", "_", Path(nome_arquivo).stem)[:60] or "doc"
    cid, n = base, 1
    while cid in usados:
        n += 1
        cid = f"{base[:56]}-{n}"
    usados.add(cid)
    return cid


# -----------------------------------------------------------------------------
# Execução
# -----------------------------------------------------------------------------

def main():
    simular = "--simular" in sys.argv

    if not simular and not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ERRO: variável ANTHROPIC_API_KEY não configurada.")

    if not simular and Path(ARQUIVO_BATCH_ID).exists() and "--forcar" not in sys.argv:
        sys.exit(f"ERRO: {ARQUIVO_BATCH_ID} já existe (lote "
                 f"{Path(ARQUIVO_BATCH_ID).read_text(encoding='utf-8').strip()}). "
                 "Reenviar sobrescreveria o ID e o mapa do lote anterior. Processe ou "
                 "renomeie esses arquivos, ou use --forcar.")

    manual_path = Path(ARQUIVO_MANUAL)
    if not manual_path.exists():
        sys.exit(f"ERRO: {ARQUIVO_MANUAL} não encontrado na pasta do script.")
    texto_manual = manual_path.read_text(encoding="utf-8")
    linhas_manual = texto_manual.splitlines()
    if not linhas_manual or "versão 3" not in linhas_manual[0]:
        sys.exit(f"ERRO: a primeira linha de {ARQUIVO_MANUAL} não indica a versão 3.")

    pasta = Path(PASTA_TXT)
    if not pasta.is_dir():
        sys.exit(f"ERRO: pasta {PASTA_TXT} não encontrada.")
    arquivos = sorted(pasta.glob("*.txt"))
    if not arquivos:
        sys.exit(f"ERRO: nenhum .txt em {PASTA_TXT}.")

    random.seed(SEMENTE)
    random.shuffle(arquivos)

    system_prompt = montar_system_prompt(texto_manual)
    print(f"[{time.strftime('%H:%M:%S')}] Codificação da população — manual v3")
    print(f"Modelo: {MODELO} | max_tokens: {MAX_TOKENS} | semente: {SEMENTE}")
    print(f"Prompt de sistema: {len(system_prompt):,} caracteres (cacheado)")
    print(f"Acórdãos na pasta: {len(arquivos)}")

    requisicoes, mapa, usados, vazios = [], {}, set(), []
    for arquivo in arquivos:
        try:
            texto = arquivo.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            sys.exit(f"ERRO: {arquivo.name} não está em UTF-8. Converta antes de submeter.")
        if not texto.strip():
            vazios.append(arquivo.name)
            continue

        cid = gerar_custom_id(arquivo.name, usados)
        mapa[cid] = arquivo.name

        conteudo = (
            f"Arquivo: {arquivo.name}\n\n"
            "=================== INTEIRO TEOR DO ACÓRDÃO ===================\n\n"
            f"{texto}\n\n"
            "=================== FIM DO INTEIRO TEOR ===================\n\n"
            "Aplique o manual de codificação às dezesseis variáveis e responda "
            "somente com o objeto JSON no formato especificado."
        )

        requisicoes.append({
            "custom_id": cid,
            "params": {
                "model": MODELO,
                "max_tokens": MAX_TOKENS,
                "system": [{
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }],
                "messages": [{"role": "user", "content": conteudo}],
            },
        })

    if vazios:
        print(f"\nATENÇÃO: {len(vazios)} arquivo(s) vazio(s) não submetido(s): {', '.join(vazios)}")

    with open(ARQUIVO_JSONL, "w", encoding="utf-8") as f:
        for r in requisicoes:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    Path(ARQUIVO_MAPA).write_text(json.dumps(
        {"modelo": MODELO, "max_tokens": MAX_TOKENS, "semente": SEMENTE,
         "manual": ARQUIVO_MANUAL, "ordem": [r["custom_id"] for r in requisicoes],
         "arquivos": mapa},
        ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{len(requisicoes)} requisições gravadas em {ARQUIVO_JSONL} "
          f"({Path(ARQUIVO_JSONL).stat().st_size:,} bytes)")
    print(f"Mapa de arquivos e ordem de submissão em {ARQUIVO_MAPA}")

    if simular:
        print("\nModo --simular: nada foi submetido.")
        return

    client = anthropic.Anthropic()
    batch = client.messages.batches.create(requests=requisicoes)
    Path(ARQUIVO_BATCH_ID).write_text(batch.id, encoding="utf-8")

    print(f"\n=== Lote criado ===")
    print(f"ID: {batch.id} (salvo em {ARQUIVO_BATCH_ID})")
    print(f"Status: {batch.processing_status}")
    print("\nQuando terminar, rode: py processar_batch_v3.py")


if __name__ == "__main__":
    main()
