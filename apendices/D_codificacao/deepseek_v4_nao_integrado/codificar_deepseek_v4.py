"""
Codificação da população — versão DeepSeek V4 Pro (manual de codificação, versão 3).

Equivale a submeter_batch_v3.py, mas a API da DeepSeek não tem Batch API: as
requisições são enviadas uma a uma (com concorrência limitada), em ordem aleatória
com a mesma semente, e cada resposta é gravada assim que chega. Se o script for
interrompido, rode de novo: os acórdãos já respondidos não são reenviados.

Reaproveita de submeter_batch_v3.py o prompt de sistema (manual + instruções +
formato de saída), a geração de custom_id e a semente, para que a única diferença
entre as duas execuções seja o modelo.

Uso:
    set DEEPSEEK_API_KEY=sk-...
    py codificar_deepseek_v4.py --simular   (só gera o JSONL e o mapa, sem chamar a API)
    py codificar_deepseek_v4.py             (codifica; retoma de onde parou)
    py processar_deepseek_v4.py             (gera CSV, JSONL completo e alertas)

Opções:
    --conc N                   requisições simultâneas (padrão 8; limite da conta: 500)
    --raciocinio padrao|desligado|max   modo de raciocínio (padrão: o do modelo)

Estrutura esperada: a mesma do submeter_batch_v3.py (na mesma pasta), mais este script.
"""

import argparse
import json
import os
import random
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import submeter_batch_v3 as base

# -----------------------------------------------------------------------------
# Configuração
# -----------------------------------------------------------------------------

URL_API = "https://api.deepseek.com/chat/completions"
MODELO = "deepseek-v4-pro"
MAX_TOKENS = base.MAX_TOKENS
SEMENTE = base.SEMENTE

PASTA_TXT = base.PASTA_TXT
ARQUIVO_MANUAL = base.ARQUIVO_MANUAL
ARQUIVO_JSONL = "requisicoes_deepseek_v4.jsonl"
ARQUIVO_MAPA = "mapa_custom_id_deepseek_v4.json"
ARQUIVO_RESPOSTAS = "respostas_deepseek_v4.jsonl"

TIMEOUT = 3600          # s; com raciocínio, uma resposta pode demorar
TENTATIVAS = 3          # por acórdão, para erros transitórios e resposta vazia
ESPERA_BASE = 5         # s; espera = ESPERA_BASE * 2**(tentativa-1)
CONCORRENCIA = 8
FATAIS = {401, 402, 403}   # chave inválida, saldo insuficiente: não adianta insistir


class ErroFatal(Exception):
    pass


# -----------------------------------------------------------------------------
# Requisições
# -----------------------------------------------------------------------------

def parametros_raciocinio(modo):
    if modo == "desligado":
        return {"thinking": {"type": "disabled"}}
    if modo == "max":
        return {"thinking": {"type": "enabled"}, "reasoning_effort": "max"}
    return {}


def montar_conteudo(nome, texto):
    """Idêntico ao conteúdo de usuário de submeter_batch_v3.py."""
    return (
        f"Arquivo: {nome}\n\n"
        "=================== INTEIRO TEOR DO ACÓRDÃO ===================\n\n"
        f"{texto}\n\n"
        "=================== FIM DO INTEIRO TEOR ===================\n\n"
        "Aplique o manual de codificação às dezesseis variáveis e responda "
        "somente com o objeto JSON no formato especificado."
    )


def montar_requisicoes(modo_raciocinio="padrao"):
    """Devolve (requisicoes, mapa, vazios); encerra o programa em caso de erro de entrada."""
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

    system_prompt = base.montar_system_prompt(texto_manual)
    requisicoes, mapa, usados, vazios = [], {}, set(), []
    for arquivo in arquivos:
        try:
            texto = arquivo.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            sys.exit(f"ERRO: {arquivo.name} não está em UTF-8. Converta antes de enviar.")
        if not texto.strip():
            vazios.append(arquivo.name)
            continue
        cid = base.gerar_custom_id(arquivo.name, usados)
        mapa[cid] = arquivo.name
        corpo = {
            "model": MODELO,
            "max_tokens": MAX_TOKENS,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": montar_conteudo(arquivo.name, texto)},
            ],
            "response_format": {"type": "json_object"},
            "stream": False,
        }
        corpo.update(parametros_raciocinio(modo_raciocinio))
        requisicoes.append({"custom_id": cid, "corpo": corpo})
    return requisicoes, mapa, vazios, system_prompt


# -----------------------------------------------------------------------------
# Chamada à API (stdlib; substituível nos testes)
# -----------------------------------------------------------------------------

def chamar_api(corpo, chave):
    """POST em /chat/completions. Devolve o JSON da resposta. Levanta
    urllib.error.HTTPError, urllib.error.URLError ou TimeoutError."""
    req = urllib.request.Request(
        URL_API, data=json.dumps(corpo).encode("utf-8"), method="POST",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {chave}"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))


def resumir(resposta):
    """Extrai o que interessa de uma resposta de chat.completions."""
    ch = (resposta.get("choices") or [{}])[0]
    msg = ch.get("message") or {}
    u = resposta.get("usage") or {}
    return {
        "finish_reason": ch.get("finish_reason"),
        "content": msg.get("content"),
        "reasoning_content": msg.get("reasoning_content"),
        "usage": {
            "prompt_tokens": u.get("prompt_tokens") or 0,
            "completion_tokens": u.get("completion_tokens") or 0,
            "cache_hit": u.get("prompt_cache_hit_tokens") or 0,
            "cache_miss": u.get("prompt_cache_miss_tokens") or 0,
            "reasoning_tokens": ((u.get("completion_tokens_details") or {})
                                 .get("reasoning_tokens") or 0),
        },
    }


def codificar_um(req, chave, chamar, dormir):
    """Envia uma requisição, com novas tentativas. Devolve o registro a gravar.
    Levanta ErroFatal para chave inválida ou saldo insuficiente."""
    ultimo_erro = "sem tentativa"
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            r = resumir(chamar(req["corpo"], chave))
        except urllib.error.HTTPError as e:
            if e.code in FATAIS:
                raise ErroFatal(f"HTTP {e.code}: {e.reason}") from e
            ultimo_erro = f"HTTP {e.code}: {e.reason}"
            if e.code not in (429, 500, 502, 503, 504):
                break                       # 400 etc.: reenviar não adianta
        except (urllib.error.URLError, TimeoutError, socket.timeout, ConnectionError,
                json.JSONDecodeError) as e:
            ultimo_erro = f"{type(e).__name__}: {e}"
        else:
            if (r["content"] or "").strip():
                return {"custom_id": req["custom_id"], "status": "ok", **r}
            ultimo_erro = f"resposta vazia (finish_reason={r['finish_reason']})"
            if r["finish_reason"] == "length":
                # truncou dentro do raciocínio: repetir gasta de novo e tende ao mesmo fim
                return {"custom_id": req["custom_id"], "status": "ok", **r}
        if tentativa < TENTATIVAS:
            dormir(ESPERA_BASE * 2 ** (tentativa - 1))
    return {"custom_id": req["custom_id"], "status": "falha", "erro": ultimo_erro}


def ler_respostas(caminho=None):
    """custom_id -> último registro gravado."""
    caminho = Path(caminho or ARQUIVO_RESPOSTAS)
    out = {}
    if caminho.exists():
        for linha in caminho.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                try:
                    r = json.loads(linha)
                    out[r["custom_id"]] = r
                except (json.JSONDecodeError, KeyError):
                    pass   # linha cortada por interrupção: o acórdão será reenviado
    return out


# -----------------------------------------------------------------------------
# Execução
# -----------------------------------------------------------------------------

def main(argv=None, chamar=chamar_api, dormir=time.sleep):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Codificação com DeepSeek V4 Pro")
    ap.add_argument("--simular", action="store_true")
    ap.add_argument("--conc", type=int, default=CONCORRENCIA)
    ap.add_argument("--raciocinio", choices=["padrao", "desligado", "max"], default="padrao")
    args = ap.parse_args(argv)

    chave = os.environ.get("DEEPSEEK_API_KEY", "")
    if not args.simular and not chave:
        sys.exit("ERRO: variável DEEPSEEK_API_KEY não configurada.")
    if args.conc < 1:
        sys.exit("ERRO: --conc deve ser pelo menos 1.")

    requisicoes, mapa, vazios, system_prompt = montar_requisicoes(args.raciocinio)
    print(f"[{time.strftime('%H:%M:%S')}] Codificação da população — manual v3 — DeepSeek")
    print(f"Modelo: {MODELO} | max_tokens: {MAX_TOKENS} | semente: {SEMENTE} | "
          f"raciocínio: {args.raciocinio}")
    print(f"Prompt de sistema: {len(system_prompt):,} caracteres")
    print(f"Acórdãos: {len(requisicoes)}")
    if vazios:
        print(f"\nATENÇÃO: {len(vazios)} arquivo(s) vazio(s) não enviado(s): {', '.join(vazios)}")

    with open(ARQUIVO_JSONL, "w", encoding="utf-8") as f:
        for r in requisicoes:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    Path(ARQUIVO_MAPA).write_text(json.dumps(
        {"modelo": MODELO, "max_tokens": MAX_TOKENS, "semente": SEMENTE,
         "raciocinio": args.raciocinio, "manual": ARQUIVO_MANUAL,
         "ordem": [r["custom_id"] for r in requisicoes], "arquivos": mapa},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{len(requisicoes)} requisições gravadas em {ARQUIVO_JSONL}")
    print(f"Mapa de arquivos e ordem em {ARQUIVO_MAPA}")

    if args.simular:
        print("\nModo --simular: nada foi enviado.")
        return

    feitas = ler_respostas()
    # só a resposta "ok" é definitiva; falhas anteriores são reenviadas a cada execução
    pendentes = [r for r in requisicoes if feitas.get(r["custom_id"], {}).get("status") != "ok"]
    ja = len(requisicoes) - len(pendentes)
    print(f"Já respondidos: {ja} | a enviar agora: {len(pendentes)}")
    if not pendentes:
        print("\nNada a fazer. Rode: py processar_deepseek_v4.py")
        return

    trava, parar = threading.Lock(), threading.Event()
    contagem = {"ok": 0, "falha": 0}
    fatal = []

    def trabalho(req):
        if parar.is_set():
            return
        try:
            reg = codificar_um(req, chave, chamar, dormir)
        except ErroFatal as e:
            fatal.append(str(e))
            parar.set()
            return
        with trava:
            with open(ARQUIVO_RESPOSTAS, "a", encoding="utf-8") as f:
                f.write(json.dumps(reg, ensure_ascii=False) + "\n")
            contagem[reg["status"]] += 1
            marca = "✓" if reg["status"] == "ok" else "✗"
            extra = "" if reg["status"] == "ok" else f" — {reg['erro']}"
            print(f"  {marca} {mapa[req['custom_id']]}{extra}", flush=True)

    # a primeira requisição vai sozinha para formar o cache do prefixo (manual)
    trabalho(pendentes[0])
    resto = pendentes[1:]
    if resto and not parar.is_set():
        with ThreadPoolExecutor(max_workers=args.conc) as ex:
            list(ex.map(trabalho, resto))

    if fatal:
        print(f"\nERRO FATAL: {fatal[0]}. Execução interrompida; rode de novo depois de "
              "corrigir. O que já foi respondido está salvo.")
    print(f"\nRespondidos agora: {contagem['ok']} | falhas: {contagem['falha']}")
    if contagem["falha"]:
        print("Rode o script de novo para reenviar as falhas.")
    print("Depois rode: py processar_deepseek_v4.py")
    if fatal:
        sys.exit(1)


if __name__ == "__main__":
    main()
