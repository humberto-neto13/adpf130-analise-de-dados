"""
Processa os resultados do lote da Batch API e gera o CSV final.

Uso (depois que verificar_batch.py reportar status 'ended'):
    py processar_batch.py

Baixa o arquivo de resultados, extrai a codificação de cada acórdão e gera
piloto_fase1.csv no mesmo formato do script síncrono.
"""

import csv
import json
import os
import sys
import time
from pathlib import Path

import anthropic

ARQUIVO_BATCH_ID = "batch_id_sonnet.txt"
ARQUIVO_SAIDA = "piloto_fase1_sonnet.csv"
ARQUIVO_LOG = "log_piloto_fase1_sonnet.txt"


def extrair_codificacao(resultado_json):
    """Extrai a codificação de uma resposta bem-sucedida do batch."""
    try:
        # Localiza o bloco de texto (pode haver ThinkingBlock antes)
        content = resultado_json["result"]["message"]["content"]
        texto = None
        for bloco in content:
            if bloco.get("type") == "text":
                texto = bloco["text"].strip()
                break
        if texto is None:
            return None, "Nenhum bloco de texto encontrado"

        # Remover fences de código se houver
        if texto.startswith("```"):
            texto = texto.split("```")[1]
            if texto.startswith("json"):
                texto = texto[4:]
            texto = texto.strip()

        dados = json.loads(texto)

        usage = resultado_json["result"]["message"]["usage"]

        return {
            "momento_restricao": dados.get("momento_restricao", "ERRO"),
            "momento_restricao_justificativa":
dados.get("momento_restricao_justificativa", ""),
            "sujeito_comunicativo": dados.get("sujeito_comunicativo", "ERRO"),
            "sujeito_comunicativo_justificativa":
dados.get("sujeito_comunicativo_justificativa", ""),
            "meio_comunicativo": dados.get("meio_comunicativo", []),
            "meio_comunicativo_justificativa":
dados.get("meio_comunicativo_justificativa", ""),
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "cache_read_tokens": usage.get("cache_read_input_tokens", 0) or 0,
            "cache_creation_tokens": usage.get("cache_creation_input_tokens", 0) or 0,
        }, None
    except Exception as e:
        return None, f"Erro ao extrair: {e}"


def estimar_custo_batch(input_tokens, output_tokens, cache_read, cache_creation):
    """Estima custo da Batch API para Claude Sonnet 5 (50% de desconto)."""
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

    resultados = []
    for linha in resultados_stream:
        # linha é uma MessageBatchIndividualResponse
        linha_dict = linha.model_dump() if hasattr(linha, "model_dump") else dict(linha)

        custom_id = linha_dict.get("custom_id", "")
        # O custom_id teve pontos substituídos por underscores para atender ao
        # padrão da Batch API. Aqui revertemos para reconstruir o nome do arquivo.
        # Nomes originais podem ter até dois pontos (ex.: 45682.1.txt),
        # substituídos para 45682_1. Como underscores não aparecem em nomes
        # originais, a reversão é segura.
        nome_arquivo = f"{custom_id.replace('_', '.')}.txt"
        result_type = linha_dict.get("result", {}).get("type", "")

        if result_type == "succeeded":
            dados, erro = extrair_codificacao(linha_dict)
            if dados:
                resultados.append({
                    "arquivo": nome_arquivo,
                    "momento_restricao": dados["momento_restricao"],
                    "sujeito_comunicativo": dados["sujeito_comunicativo"],
                    "meio_comunicativo": ",".join(dados["meio_comunicativo"]) if
isinstance(dados["meio_comunicativo"], list) else dados["meio_comunicativo"],
                    "momento_restricao_justificativa":
dados["momento_restricao_justificativa"],
                    "sujeito_comunicativo_justificativa":
dados["sujeito_comunicativo_justificativa"],
                    "meio_comunicativo_justificativa":
dados["meio_comunicativo_justificativa"],
                    "input_tokens": dados["input_tokens"],
                    "output_tokens": dados["output_tokens"],
                    "cache_read_tokens": dados["cache_read_tokens"],
                    "cache_creation_tokens": dados["cache_creation_tokens"],
                    "erro": None,
                })
                log(f"  ✓ {custom_id}: mom={dados['momento_restricao']} suj={dados['sujeito_comunicativo']} meio={','.join(dados['meio_comunicativo']) if
isinstance(dados['meio_comunicativo'], list) else '?'}")
            else:
                resultados.append({
                    "arquivo": nome_arquivo,
                    "momento_restricao": "ERRO",
                    "sujeito_comunicativo": "ERRO",
                    "meio_comunicativo": "",
                    "momento_restricao_justificativa": "",
                    "sujeito_comunicativo_justificativa": "",
                    "meio_comunicativo_justificativa": "",
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cache_read_tokens": 0,
                    "cache_creation_tokens": 0,
                    "erro": erro,
                })
                log(f"  ✗ {custom_id}: {erro}")
        else:
            # error, canceled, expired
            erro_msg = linha_dict.get("result", {}).get("error", {})
            resultados.append({
                "arquivo": nome_arquivo,
                "momento_restricao": "ERRO",
                "sujeito_comunicativo": "ERRO",
                "meio_comunicativo": "",
                "momento_restricao_justificativa": "",
                "sujeito_comunicativo_justificativa": "",
                "meio_comunicativo_justificativa": "",
                "input_tokens": 0,
                "output_tokens": 0,
                "cache_read_tokens": 0,
                "cache_creation_tokens": 0,
                "erro": f"{result_type}: {erro_msg}",
            })
            log(f"  ✗ {custom_id}: {result_type}")

    # Salvar CSV
    if resultados:
        with open(ARQUIVO_SAIDA, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
            writer.writeheader()
            writer.writerows(resultados)
        log(f"\nResultado salvo em: {ARQUIVO_SAIDA}")

    # Estatísticas
    log("\n=== Estatísticas ===")
    total_input = sum(r["input_tokens"] for r in resultados)
    total_output = sum(r["output_tokens"] for r in resultados)
    total_cache_read = sum(r["cache_read_tokens"] for r in resultados)
    total_cache_creation = sum(r["cache_creation_tokens"] for r in resultados)
    custo = estimar_custo_batch(total_input, total_output, total_cache_read,
total_cache_creation)

    log(f"Tokens input total: {total_input:,}")
    log(f"Tokens output total: {total_output:,}")
    log(f"Tokens cache_read: {total_cache_read:,}")
    log(f"Tokens cache_creation: {total_cache_creation:,}")
    log(f"Custo estimado (Batch API Sonnet 5, 50% desconto): USD {custo:.4f}")

    n_erros = sum(1 for r in resultados if r["momento_restricao"] == "ERRO")
    n_nd = sum(1 for r in resultados if r["momento_restricao"] == "ND")
    log(f"\nAcórdãos codificados com sucesso: {len(resultados) - n_erros}")
    log(f"Acórdãos com erro: {n_erros}")
    log(f"Casos com pelo menos uma variável ND: {n_nd}")

    Path(ARQUIVO_LOG).write_text("\n".join(log_lines), encoding="utf-8")


if __name__ == "__main__":
    main()

