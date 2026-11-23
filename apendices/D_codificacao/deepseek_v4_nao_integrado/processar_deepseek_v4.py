"""
Codificação da população — processamento dos resultados da DeepSeek (manual v3).

Lê respostas_deepseek_v4.jsonl e mapa_custom_id_deepseek_v4.json (gerados por
codificar_deepseek_v4.py). Não usa rede nem chave de API. Reaproveita as validações
de processar_batch_v3.py, de modo que os alertas sejam idênticos aos da versão Claude.

Gera:
    codificacao_deepseek_v4.csv             só as respostas, mais a coluna "alertas"
    codificacao_deepseek_v4_completo.jsonl  resposta integral, com justificativas
    alertas_deepseek_v4.csv                 um alerta por linha
    log_codificacao_deepseek_v4.txt

O script NÃO corrige nenhum valor. Só sinaliza o que exige atenção na verificação humana.

Uso:
    py processar_deepseek_v4.py
"""

import csv
import json
import sys
import time
from pathlib import Path

import processar_batch_v3 as proc

ARQUIVO_MAPA = "mapa_custom_id_deepseek_v4.json"
ARQUIVO_RESPOSTAS = "respostas_deepseek_v4.jsonl"
SAIDA_CSV = "codificacao_deepseek_v4.csv"
SAIDA_JSONL = "codificacao_deepseek_v4_completo.jsonl"
SAIDA_ALERTAS = "alertas_deepseek_v4.csv"
ARQUIVO_LOG = "log_codificacao_deepseek_v4.txt"

ORDEM = proc.ORDEM


def ler_respostas():
    out = {}
    for linha in Path(ARQUIVO_RESPOSTAS).read_text(encoding="utf-8").splitlines():
        if linha.strip():
            try:
                r = json.loads(linha)
                out[r["custom_id"]] = r
            except (json.JSONDecodeError, KeyError):
                pass
    return out


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    linhas_log = []

    def log(msg=""):
        print(msg)
        linhas_log.append(msg)

    for p in (ARQUIVO_MAPA, ARQUIVO_RESPOSTAS):
        if not Path(p).exists():
            sys.exit(f"ERRO: {p} não encontrado. Rode antes codificar_deepseek_v4.py.")

    info = json.loads(Path(ARQUIVO_MAPA).read_text(encoding="utf-8"))
    mapa = info["arquivos"]
    respostas = ler_respostas()
    log(f"[{time.strftime('%H:%M:%S')}] Modelo {info.get('modelo')} | "
        f"raciocínio: {info.get('raciocinio')} | acórdãos no mapa: {len(mapa)} | "
        f"respostas gravadas: {len(respostas)}")

    linhas_csv, linhas_jsonl, todos_alertas = [], [], []
    tokens = {"prompt": 0, "completion": 0, "reasoning": 0, "cache_hit": 0, "cache_miss": 0}
    ok = falhas = com_alerta = 0

    for cid, nome in mapa.items():
        r = respostas.get(cid)
        if r is None:
            falhas += 1
            msg = "sem resposta gravada"
            linhas_csv.append({"arquivo": nome, "status": "falha", "alertas": msg})
            todos_alertas.append((nome, "", "falha", msg))
            log(f"  ✗ {nome}: {msg}")
            continue
        if r.get("status") != "ok":
            falhas += 1
            msg = f"falha na API: {r.get('erro')}"
            linhas_csv.append({"arquivo": nome, "status": "falha", "alertas": msg})
            todos_alertas.append((nome, "", "falha", msg))
            log(f"  ✗ {nome}: {msg}")
            continue

        u = r.get("usage") or {}
        tokens["prompt"] += u.get("prompt_tokens") or 0
        tokens["completion"] += u.get("completion_tokens") or 0
        tokens["reasoning"] += u.get("reasoning_tokens") or 0
        tokens["cache_hit"] += u.get("cache_hit") or 0
        tokens["cache_miss"] += u.get("cache_miss") or 0

        fim = r.get("finish_reason")
        texto = (r.get("content") or "").strip() or None
        try:
            if texto is None:
                raise json.JSONDecodeError("resposta sem conteúdo", "", 0)
            dados = proc.extrair_json(texto)
        except json.JSONDecodeError as e:
            falhas += 1
            msg = f"JSON inválido ({e.msg}); finish_reason={fim}"
            linhas_csv.append({"arquivo": nome, "status": "falha", "alertas": msg})
            todos_alertas.append((nome, "", "falha", msg))
            linhas_jsonl.append({"arquivo": nome, "custom_id": cid, "erro": msg,
                                 "texto_bruto": texto})
            log(f"  ✗ {nome}: {msg}")
            continue

        alertas = []
        try:
            if fim != "stop":
                alertas.append(("", "formato", f"finish_reason={fim}"))
            proc.validar_formato(dados, alertas)
            proc.verificar_consistencia(dados, nome, alertas)
            linha = {"arquivo": nome, "status": "ok"}
            for var in ORDEM:
                linha[var] = proc.celula(dados, var)
            linha["alertas"] = " | ".join(f"{v}: {m}" if v else m for v, _, m in alertas)
        except Exception as e:  # um item malformado não pode derrubar o lote
            falhas += 1
            msg = f"erro de processamento ({type(e).__name__}: {e}); finish_reason={fim}"
            linhas_csv.append({"arquivo": nome, "status": "falha", "alertas": msg})
            todos_alertas.append((nome, "", "falha", msg))
            linhas_jsonl.append({"arquivo": nome, "custom_id": cid, "erro": msg,
                                 "texto_bruto": texto})
            log(f"  ✗ {nome}: {msg}")
            continue

        linhas_csv.append(linha)
        linhas_jsonl.append({"arquivo": nome, "custom_id": cid, "finish_reason": fim,
                             "codificacao": dados,
                             "alertas": [{"variavel": v, "tipo": t, "mensagem": m}
                                         for v, t, m in alertas]})
        todos_alertas += [(nome, v, t, m) for v, t, m in alertas]
        ok += 1
        if alertas:
            com_alerta += 1
        log(f"  {'⚠' if alertas else '✓'} {nome}"
            + (f" ({len(alertas)} alerta(s))" if alertas else ""))

    for cid, r in respostas.items():   # respostas de custom_id que o mapa não conhece
        if cid not in mapa:
            msg = f"resposta com custom_id fora do mapa: {cid}"
            linhas_csv.append({"arquivo": f"[custom_id desconhecido: {cid}]",
                               "status": "falha", "alertas": msg})
            todos_alertas.append((f"[custom_id desconhecido: {cid}]", "", "falha", msg))

    linhas_csv.sort(key=lambda l: l["arquivo"])
    colunas = ["arquivo", "status"] + ORDEM + ["alertas"]
    with open(SAIDA_CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=colunas)
        w.writeheader()
        for l in linhas_csv:
            w.writerow({c: l.get(c, "") for c in colunas})

    with open(SAIDA_JSONL, "w", encoding="utf-8") as f:
        for l in sorted(linhas_jsonl, key=lambda l: l["arquivo"]):
            f.write(json.dumps(l, ensure_ascii=False) + "\n")

    with open(SAIDA_ALERTAS, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["arquivo", "variavel", "tipo", "mensagem"])
        w.writerows(sorted(todos_alertas))

    log("\n=== Resumo ===")
    log(f"Codificados: {ok} (com alerta: {com_alerta}) | falhas: {falhas}")
    log(f"Tokens — entrada: {tokens['prompt']:,} (cache hit: {tokens['cache_hit']:,} | "
        f"miss: {tokens['cache_miss']:,}) | saída: {tokens['completion']:,} "
        f"(raciocínio: {tokens['reasoning']:,})")
    log(f"\nArquivos: {SAIDA_CSV}, {SAIDA_JSONL}, {SAIDA_ALERTAS}")
    if falhas:
        log("Há falhas. Falhas de API e acórdãos sem resposta são reenviados ao rodar "
            "codificar_deepseek_v4.py de novo. Respostas que chegaram mas vieram com JSON "
            "inválido ou truncadas ficam salvas (reenviar custa de novo): para refazê-las, "
            "apague a linha do custom_id em respostas_deepseek_v4.jsonl antes de rodar.")

    Path(ARQUIVO_LOG).write_text("\n".join(linhas_log), encoding="utf-8")


if __name__ == "__main__":
    main()
