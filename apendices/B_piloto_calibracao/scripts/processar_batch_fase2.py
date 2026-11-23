"""
Piloto Fase 2 — Processamento dos resultados da Batch API.

Baixa os resultados do lote submetido, extrai as codificações das 16 variáveis
e gera um CSV com apenas as respostas (sem justificativas), no formato adequado
para verificação humana em paralelo.

Além do CSV principal, salva também um arquivo JSONL com os resultados brutos
(incluindo justificativas) para consulta em caso de dúvida sobre alguma
codificação.

Uso (depois que o lote estiver pronto):
    py processar_batch_fase2.py
"""

import csv
import json
import os
import sys
import time
from pathlib import Path

import anthropic

ARQUIVO_BATCH_ID = "batch_id_fase2.txt"
ARQUIVO_SAIDA_CSV = "piloto_fase2.csv"
ARQUIVO_SAIDA_JSONL = "piloto_fase2_completo.jsonl"
ARQUIVO_ERROS_BRUTOS = "piloto_fase2_respostas_com_erro.txt"
ARQUIVO_LOG = "log_piloto_fase2.txt"


def extrair_texto_resposta(content):
    """Localiza o bloco de texto (pode haver ThinkingBlock antes)."""
    for bloco in content:
        if bloco.get("type") == "text":
            return bloco["text"].strip()
    return None


def limpar_json(texto):
    """Remove fences de código eventualmente presentes."""
    if texto.startswith("```"):
        texto = texto.split("```")[1]
        if texto.startswith("json"):
            texto = texto[4:]
        texto = texto.strip()
    return texto


def formatar_multiplo(valor):
    """Converte lista de classes em string separada por vírgula."""
    if isinstance(valor, list):
        return ",".join(str(v) for v in valor)
    return str(valor) if valor is not None else ""


def extrair_classe(campo):
    """Extrai a classe ou classes de um campo do JSON."""
    if campo is None:
        return ""
    if isinstance(campo, dict):
        if "classes" in campo:
            return formatar_multiplo(campo["classes"])
        if "classe" in campo:
            return str(campo["classe"]) if campo["classe"] is not None else ""
    if isinstance(campo, list):
        return formatar_multiplo(campo)
    return str(campo)


def formatar_v16(campo):
    """Formata V16 como string sintética para o CSV.
    O detalhe (citação, localização) fica no JSONL completo."""
    if campo is None or not isinstance(campo, dict):
        return ""
    if not campo.get("aplicavel", False):
        return "não aplicável"
    razoes = campo.get("razoes", [])
    if not razoes:
        return "aplicável mas sem razões extraídas"
    descricoes = [r.get("descricao", "") for r in razoes if isinstance(r, dict)]
    return " || ".join(descricoes)


def formatar_vencidos(campo):
    """Formata V12 como string separada por ponto e vírgula."""
    if campo is None:
        return ""
    if isinstance(campo, list):
        if not campo:
            return "unânime"
        return "; ".join(str(m) for m in campo)
    return str(campo)


def estimar_custo_batch(input_tokens, output_tokens, cache_read, cache_creation):
    """Estima custo Sonnet 5 Batch (50% desconto)."""
    return (
        (input_tokens / 1_000_000) * 3.00 * 0.5
        + (output_tokens / 1_000_000) * 15.00 * 0.5
        + (cache_creation / 1_000_000) * 3.75 * 0.5
        + (cache_read / 1_000_000) * 0.30 * 0.5
    )


def main():
    log_lines = []
    def log(msg):
        print(msg)
        log_lines.append(msg)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERRO: variável ANTHROPIC_API_KEY não configurada.", file=sys.stderr)
        sys.exit(1)

    if not Path(ARQUIVO_BATCH_ID).exists():
        print(f"ERRO: arquivo {ARQUIVO_BATCH_ID} não encontrado.", file=sys.stderr)
        sys.exit(1)

    batch_id = Path(ARQUIVO_BATCH_ID).read_text(encoding="utf-8").strip()
    log(f"[{time.strftime('%H:%M:%S')}] Consultando lote {batch_id}")

    client = anthropic.Anthropic()
    batch = client.messages.batches.retrieve(batch_id)

    log(f"\nStatus atual: {batch.processing_status}")
    log(f"Requisições em processamento: {batch.request_counts.processing}")
    log(f"Requisições bem-sucedidas:    {batch.request_counts.succeeded}")
    log(f"Requisições com erro:         {batch.request_counts.errored}")

    if batch.processing_status != "ended":
        log(f"\nLote ainda em processamento. Aguarde e rode este script novamente.")
        sys.exit(0)

    log(f"\nLote concluído! Baixando resultados...")
    resultados_stream = client.messages.batches.results(batch_id)

    # Colunas do CSV (só respostas, sem justificativas)
    colunas_csv = [
        "arquivo",
        "V1_FUND", "V2_MOD_REST", "V3_MOM_REST", "V4_SUJ_COM", "V5_MEIO",
        "V6_TRANSC", "V7_DIVERG",
        "V8_ORG", "V9_DATA", "V10_REL", "V11_RED", "V12_VENCIDOS",
        "V13_ADER", "V14_CONHEC", "V15_MERITO", "V16_DIST",
        "erro"
    ]

    linhas_csv = []
    linhas_jsonl = []
    respostas_com_erro = []
    contagem_ok = 0
    contagem_erro = 0

    total_input = 0
    total_output = 0
    total_cache_read = 0
    total_cache_creation = 0

    for linha in resultados_stream:
        linha_dict = linha.model_dump() if hasattr(linha, "model_dump") else dict(linha)
        custom_id = linha_dict.get("custom_id", "")
        nome_arquivo = f"{custom_id.replace('_', '.')}.txt"
        result_type = linha_dict.get("result", {}).get("type", "")

        if result_type == "succeeded":
            content = linha_dict["result"]["message"]["content"]
            usage = linha_dict["result"]["message"]["usage"]

            total_input += usage.get("input_tokens", 0)
            total_output += usage.get("output_tokens", 0)
            total_cache_read += usage.get("cache_read_input_tokens", 0) or 0
            total_cache_creation += usage.get("cache_creation_input_tokens", 0) or 0

            texto = extrair_texto_resposta(content)
            if texto is None:
                log(f"  ✗ {nome_arquivo}: sem bloco de texto")
                linhas_csv.append({"arquivo": nome_arquivo, "erro": "sem bloco de texto"})
                respostas_com_erro.append(
                    f"=== {nome_arquivo} ===\n"
                    f"Erro: sem bloco de texto\n"
                    f"Blocos de conteúdo brutos:\n{json.dumps(content, ensure_ascii=False, indent=2)}\n"
                )
                contagem_erro += 1
                continue

            texto_original = texto
            texto = limpar_json(texto)

            try:
                dados = json.loads(texto)
            except json.JSONDecodeError as e:
                log(f"  ✗ {nome_arquivo}: JSON inválido ({e})")
                linhas_csv.append({"arquivo": nome_arquivo, "erro": f"JSON inválido: {e}"})
                respostas_com_erro.append(
                    f"=== {nome_arquivo} ===\n"
                    f"Erro: JSON inválido: {e}\n"
                    f"Texto bruto da resposta:\n{texto_original}\n"
                )
                contagem_erro += 1
                continue

            # Linha completa (com justificativas) no JSONL
            linhas_jsonl.append({"arquivo": nome_arquivo, "codificacao": dados})

            # Linha simplificada (só respostas) no CSV
            linha_csv = {
                "arquivo": nome_arquivo,
                "V1_FUND": extrair_classe(dados.get("V1_FUND")),
                "V2_MOD_REST": extrair_classe(dados.get("V2_MOD_REST")),
                "V3_MOM_REST": extrair_classe(dados.get("V3_MOM_REST")),
                "V4_SUJ_COM": extrair_classe(dados.get("V4_SUJ_COM")),
                "V5_MEIO": extrair_classe(dados.get("V5_MEIO")),
                "V6_TRANSC": extrair_classe(dados.get("V6_TRANSC")),
                "V7_DIVERG": extrair_classe(dados.get("V7_DIVERG")),
                "V8_ORG": extrair_classe(dados.get("V8_ORG")),
                "V9_DATA": str(dados.get("V9_DATA", "")),
                "V10_REL": str(dados.get("V10_REL", "")),
                "V11_RED": str(dados.get("V11_RED", "")),
                "V12_VENCIDOS": formatar_vencidos(dados.get("V12_VENCIDOS")),
                "V13_ADER": extrair_classe(dados.get("V13_ADER")),
                "V14_CONHEC": extrair_classe(dados.get("V14_CONHEC")),
                "V15_MERITO": extrair_classe(dados.get("V15_MERITO")),
                "V16_DIST": formatar_v16(dados.get("V16_DIST")),
                "erro": "",
            }
            linhas_csv.append(linha_csv)
            log(f"  ✓ {nome_arquivo}")
            contagem_ok += 1
        else:
            erro_msg = linha_dict.get("result", {}).get("error", {})
            linhas_csv.append({"arquivo": nome_arquivo, "erro": f"{result_type}: {erro_msg}"})
            log(f"  ✗ {nome_arquivo}: {result_type}")
            contagem_erro += 1

    # Salvar CSV
    with open(ARQUIVO_SAIDA_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=colunas_csv)
        writer.writeheader()
        for linha in linhas_csv:
            # Preencher campos faltantes com string vazia
            linha_completa = {c: linha.get(c, "") for c in colunas_csv}
            writer.writerow(linha_completa)
    log(f"\nCSV salvo em: {ARQUIVO_SAIDA_CSV}")

    # Salvar JSONL completo (com justificativas)
    with open(ARQUIVO_SAIDA_JSONL, "w", encoding="utf-8") as f:
        for linha in linhas_jsonl:
            f.write(json.dumps(linha, ensure_ascii=False) + "\n")
    log(f"JSONL completo (com justificativas) salvo em: {ARQUIVO_SAIDA_JSONL}")

    # Salvar respostas brutas dos casos com erro de parsing (para diagnóstico)
    if respostas_com_erro:
        with open(ARQUIVO_ERROS_BRUTOS, "w", encoding="utf-8") as f:
            f.write("\n\n".join(respostas_com_erro))
        log(f"Respostas brutas dos erros salvas em: {ARQUIVO_ERROS_BRUTOS}")

    log(f"\n=== Estatísticas ===")
    log(f"Codificações bem-sucedidas: {contagem_ok}")
    log(f"Codificações com erro:      {contagem_erro}")
    log(f"\nTokens input:              {total_input:,}")
    log(f"Tokens output:             {total_output:,}")
    log(f"Tokens cache_read:         {total_cache_read:,}")
    log(f"Tokens cache_creation:     {total_cache_creation:,}")

    custo = estimar_custo_batch(total_input, total_output, total_cache_read, total_cache_creation)
    log(f"Custo estimado (Sonnet 5 Batch): USD {custo:.4f}")

    Path(ARQUIVO_LOG).write_text("\n".join(log_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
