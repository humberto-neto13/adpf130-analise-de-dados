"""
Codificação da população — processamento dos resultados (manual v3).

Gera:
    codificacao_v3.csv             só as respostas, mais a coluna "alertas"
    codificacao_v3_completo.jsonl  resposta integral, com justificativas
    alertas_v3.csv                 um alerta por linha
    log_codificacao_v3.txt

O script NÃO corrige nenhum valor. Só sinaliza o que exige atenção na verificação humana.

Uso:
    py processar_batch_v3.py
"""

import csv
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import anthropic

ARQUIVO_BATCH_ID = "batch_id_v3.txt"
ARQUIVO_MAPA = "mapa_custom_id_v3.json"
SAIDA_CSV = "codificacao_v3.csv"
SAIDA_JSONL = "codificacao_v3_completo.jsonl"
SAIDA_ALERTAS = "alertas_v3.csv"
ARQUIVO_LOG = "log_codificacao_v3.txt"

MULTIPLAS = {  # variável -> (letras admitidas, aceita ["ND"])
    "V1_FUND":     ("abcdef",  True),
    "V2_MOD_REST": ("abcdefg", True),
    "V4_RECLTE":   ("abcdefg", True),
    "V5_MEIO":     ("abcdefg", True),
    "V6_TRANSC":   ("abcdef",  False),
    "V7_DIVERG":   ("abcdef",  True),
}
UNICAS = {
    "V3_MOM_REST": {"anterior", "posterior", "anterior e posterior", "ND"},
    "V13_ADER":    {"reconhecida", "não reconhecida", "ND"},
    "V14_SEGUIM":  {"negado", "dado", "prejudicada ou extinta", "ND"},
    "V15_MERITO":  {"procedente", "improcedente", "ND", "NA"},
}
ORDEM = ["V1_FUND", "V2_MOD_REST", "V3_MOM_REST", "V4_RECLTE", "V5_MEIO",
         "V6_TRANSC", "V7_DIVERG", "V8_ORG", "V9_DATA", "V10_REL", "V11_RED",
         "V12_VENCIDOS", "V13_ADER", "V14_SEGUIM", "V15_MERITO", "V16_JURIS"]

RE_DATA = re.compile(r"^(0[1-9]|[12]\d|3[01])/(0[1-9]|1[0-2])/(19|20)\d\d$")
RE_JURIS = re.compile(
    r"^(Súmula Vinculante \d+|Súmula \d+|Tema \d+|"
    r"(?!(?:Lei|Art|Artigo|Portaria|Decreto|Emenda|Medida)\s)[A-Za-z][A-Za-z\- ]{0,15}\s\d+)$")


def data_valida(s):
    if not (isinstance(s, str) and RE_DATA.match(s)):
        return False
    try:
        datetime.strptime(s, "%d/%m/%Y")
    except ValueError:
        return False
    return True


def texto_da_resposta(content):
    partes = [b["text"] for b in content if b.get("type") == "text"]
    return "\n".join(partes).strip() if partes else None


def _aberturas_de_nivel_zero(t):
    """Posições de '{' que não estão dentro de outro objeto ainda aberto. Um sub-objeto
    completo dentro de uma resposta truncada não pode passar por resposta inteira."""
    nivel, em_str, esc = 0, False, False
    for i, ch in enumerate(t):
        if nivel > 0 and em_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                em_str = False
            continue
        if ch == '"' and nivel > 0:
            em_str = True
        elif ch == "{":
            if nivel == 0:
                yield i
            nivel += 1
        elif ch == "}" and nivel > 0:
            nivel -= 1


def extrair_json(texto):
    t = texto.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t)
    dec = json.JSONDecoder()
    primeiro = None
    for ini in _aberturas_de_nivel_zero(t):
        try:
            return dec.raw_decode(t, ini)[0]
        except json.JSONDecodeError as e:
            primeiro = primeiro or e
    if primeiro:
        raise primeiro
    raise json.JSONDecodeError("objeto JSON não encontrado", t, 0)

def validar_formato(d, alertas):
    def a(var, msg):
        alertas.append((var, "formato", msg))

    for var in ORDEM:
        if var not in d:
            a(var, "variável ausente na resposta")
    for var in d:
        if var not in ORDEM:
            a(var, "chave não prevista no esquema")

    for var, (letras, aceita_nd) in MULTIPLAS.items():
        campo = d.get(var)
        cl = campo.get("classes") if isinstance(campo, dict) else None
        if not isinstance(cl, list) or not cl:
            a(var, "campo 'classes' ausente ou vazio")
            continue
        if not all(isinstance(c, str) for c in cl):
            a(var, f"classes com valor que não é texto: {cl}")
            continue
        if len(set(cl)) != len(cl):
            a(var, f"classe repetida: {cl}")
        if "ND" in cl:
            if not aceita_nd:
                a(var, "ND não previsto para esta variável")
            elif len(cl) > 1:
                a(var, "ND combinado com outras classes")
        invalidas = [c for c in cl if c != "ND" and c not in letras]
        if invalidas:
            a(var, f"classe fora do esquema: {invalidas}")

    for var, validos in UNICAS.items():
        campo = d.get(var)
        c = campo.get("classe") if isinstance(campo, dict) else None
        if not isinstance(c, str) or c not in validos:
            a(var, f"valor fora do esquema: {c!r}")

    v8 = d.get("V8_ORG")
    if not isinstance(v8, str) or v8 not in {"a", "b", "c", "ND"}:
        a("V8_ORG", f"valor fora do esquema: {v8!r}")

    v9 = d.get("V9_DATA")
    if v9 != "ND" and not data_valida(v9):
        a("V9_DATA", f"data fora do formato DD/MM/AAAA: {v9!r}")

    v10 = d.get("V10_REL")
    if not isinstance(v10, str) or not v10.strip():
        a("V10_REL", "nome ausente")
    elif v10.lower().startswith("min"):
        a("V10_REL", "nome registrado com 'Min.'")

    v11 = d.get("V11_RED")
    if not isinstance(v11, dict) or not isinstance(v11.get("classe"), str) \
            or v11.get("classe") not in {"a", "b"}:
        a("V11_RED", f"valor fora do esquema: {v11!r}")
    elif v11["classe"] == "a" and not (isinstance(v11.get("nome"), str) and v11["nome"].strip()):
        a("V11_RED", "classe a sem nome do redator")

    v12 = d.get("V12_VENCIDOS")
    if not (v12 in ("NA", "ND") or (isinstance(v12, list) and v12
                                    and all(isinstance(n, str) and n.strip() for n in v12))):
        a("V12_VENCIDOS", f"valor fora do esquema: {v12!r}")

    v16 = d.get("V16_JURIS")
    cit = v16.get("citacoes") if isinstance(v16, dict) else None
    if not isinstance(cit, list):
        a("V16_JURIS", "campo 'citacoes' ausente ou não é lista")
    else:
        strs = [c for c in cit if isinstance(c, str)]
        if len(set(strs)) != len(strs):
            a("V16_JURIS", "citação repetida")
        for c in cit:
            if not isinstance(c, str) or not RE_JURIS.match(c.strip()):
                a("V16_JURIS", f"citação fora do formato 'classe número': {c!r}")


def classes(d, var):
    c = d.get(var)
    cl = c.get("classes") if isinstance(c, dict) else None
    return {x for x in cl if isinstance(x, str)} if isinstance(cl, list) else set()


def classe(d, var):
    c = d.get(var)
    return c.get("classe") if isinstance(c, dict) else None


def v3_esperado(v2):
    """Tabela de derivação de V3. None quando depende do texto (classe g)."""
    if not v2 or v2 == {"ND"}:
        return "ND"
    if "f" in v2:
        return "anterior e posterior"
    if "a" in v2 and v2 != {"a"}:
        return "anterior e posterior"
    if "g" in v2:
        return None
    if "a" in v2:
        return "anterior"
    return "posterior"


def verificar_consistencia(d, nome_arquivo, alertas):
    def a(var, msg):
        alertas.append((var, "consistência", msg))

    # 1. V3 derivada de V2
    v2, v3 = classes(d, "V2_MOD_REST"), classe(d, "V3_MOM_REST")
    esp = v3_esperado(v2)
    if esp is not None and v3 != esp:
        a("V3_MOM_REST", f"V2={sorted(v2)} leva a V3='{esp}', mas V3='{v3}'")
    if "g" in v2 and esp is None and v2 != {"g"}:
        a("V3_MOM_REST", f"V2 combina (g) com {sorted(v2 - {'g'})}; conferir V3='{v3}' no texto")

    v13, v14, v15 = classe(d, "V13_ADER"), classe(d, "V14_SEGUIM"), classe(d, "V15_MERITO")

    # 2. Procedência exige aderência reconhecida
    if v15 == "procedente" and v13 != "reconhecida":
        a("V13_ADER", f"V15 procedente com V13='{v13}'")

    # 3. Seguimento negado admite só NA ou improcedente
    if v14 == "negado" and v15 not in ("NA", "improcedente"):
        a("V15_MERITO", f"V14 negado com V15='{v15}' (esperado NA ou improcedente)")
    if v15 == "procedente" and v14 != "dado":
        a("V15_MERITO", f"V15 procedente com V14='{v14}'")

    # NA em V15 é "seguimento negado sem afirmar improcedência"
    if v14 == "dado" and v15 == "NA":
        a("V15_MERITO", "V14 dado com V15='NA' (NA só vale com seguimento negado)")

    # 4. Prejudicada ou extinta leva V15 a ND
    if v14 == "prejudicada ou extinta" and v15 != "ND":
        a("V15_MERITO", f"V14 prejudicada ou extinta com V15='{v15}'")

    # 5. Vencidos e divergência
    v7, v12 = classes(d, "V7_DIVERG"), d.get("V12_VENCIDOS")
    if v12 == "NA" and v7 & {"d", "e"}:
        a("V12_VENCIDOS", f"V12 NA com voto vencido em V7={sorted(v7)}")
    if isinstance(v12, list) and v12 and "a" in v7:
        a("V7_DIVERG", f"V7 unânime (a) com vencidos em V12: {v12}")
    if v12 == "ND" and "a" in v7:
        a("V7_DIVERG", "V7 unânime (a) com V12 ND (ND pressupõe decisão por maioria)")

    # 6. Redator
    v11 = d.get("V11_RED")
    if isinstance(v11, dict):
        if v11.get("classe") == "b" and v11.get("nome"):
            a("V11_RED", f"classe b com nome preenchido: {v11.get('nome')!r}")
        if v11.get("classe") == "a" and v11.get("nome") and \
                str(v11["nome"]).strip().lower() == str(d.get("V10_REL", "")).strip().lower():
            a("V11_RED", "redator igual ao relator com classe a")

    # 7. Classes exclusivas
    for var, excl in (("V1_FUND", "f"), ("V6_TRANSC", "d"), ("V7_DIVERG", "a")):
        c = classes(d, var)
        if excl in c and len(c) > 1:
            a(var, f"classe exclusiva ({excl}) combinada: {sorted(c)}")
    if len(classes(d, "V6_TRANSC") & {"a", "b", "c"}) > 1:
        a("V6_TRANSC", "mais de uma posição do voto condutor (a, b, c)")

    # V16: paradigma e a própria reclamação não se registram
    v16 = d.get("V16_JURIS")
    cit = v16.get("citacoes", []) if isinstance(v16, dict) else []
    num = re.match(r"\d+", nome_arquivo)
    for c in cit if isinstance(cit, list) else []:
        if not isinstance(c, str):
            continue
        if re.fullmatch(r"ADPF\s*130", c.strip()):
            a("V16_JURIS", "paradigma (ADPF 130) registrado")
        if num and re.fullmatch(rf"Rcl\s*{num.group()}", c.strip()):
            a("V16_JURIS", f"a própria reclamação registrada: {c}")


def celula(d, var):
    v = d.get(var)
    if var in MULTIPLAS:
        cl = v.get("classes") if isinstance(v, dict) else None
        return ",".join(str(x) for x in cl) if isinstance(cl, list) else ""
    if var in UNICAS:
        return str(v.get("classe") or "") if isinstance(v, dict) else ""
    if var == "V11_RED":
        if not isinstance(v, dict):
            return ""
        return f"a: {v.get('nome')}" if v.get("classe") == "a" else (v.get("classe") or "")
    if var == "V12_VENCIDOS":
        return "; ".join(str(x) for x in v) if isinstance(v, list) else str(v or "")
    if var == "V16_JURIS":
        c = v.get("citacoes") if isinstance(v, dict) else None
        return "; ".join(str(x) for x in c) if isinstance(c, list) else ""
    return "" if v is None else str(v)


def main():
    # o log usa ✓ ✗ ⚠; com stdout em cp1252 (pipe, console legado) print falharia
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    linhas_log = []

    def log(msg=""):
        print(msg)
        linhas_log.append(msg)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ERRO: variável ANTHROPIC_API_KEY não configurada.")
    for p in (ARQUIVO_BATCH_ID, ARQUIVO_MAPA):
        if not Path(p).exists():
            sys.exit(f"ERRO: {p} não encontrado. Rode antes submeter_batch_v3.py.")

    batch_id = Path(ARQUIVO_BATCH_ID).read_text(encoding="utf-8").strip()
    mapa = json.loads(Path(ARQUIVO_MAPA).read_text(encoding="utf-8"))["arquivos"]

    client = anthropic.Anthropic()
    batch = client.messages.batches.retrieve(batch_id)
    rc = batch.request_counts
    log(f"[{time.strftime('%H:%M:%S')}] Lote {batch_id}: {batch.processing_status}")
    log(f"Em processamento: {rc.processing} | sucesso: {rc.succeeded} | "
        f"erro: {rc.errored} | expiradas: {rc.expired} | canceladas: {rc.canceled}")
    if batch.processing_status != "ended":
        log("\nLote ainda em processamento. Rode o script novamente mais tarde.")
        return

    linhas_csv, linhas_jsonl, todos_alertas = [], [], []
    tokens = {"input": 0, "output": 0, "cache_read": 0, "cache_creation": 0}
    ok = falhas = com_alerta = 0
    vistos = set()

    for item in client.messages.batches.results(batch_id):
        r = item.model_dump()
        cid = r.get("custom_id", "")
        vistos.add(cid)
        nome = mapa.get(cid, f"[custom_id desconhecido: {cid}]")
        res = r.get("result") or {}

        if res.get("type") != "succeeded":
            falhas += 1
            msg = f"{res.get('type')}: {res.get('error')}"
            linhas_csv.append({"arquivo": nome, "status": "falha", "alertas": msg})
            todos_alertas.append((nome, "", "falha", msg))
            log(f"  ✗ {nome}: {msg}")
            continue

        msg_api = res["message"]
        u = msg_api.get("usage") or {}
        tokens["input"] += u.get("input_tokens") or 0
        tokens["output"] += u.get("output_tokens") or 0
        tokens["cache_read"] += u.get("cache_read_input_tokens") or 0
        tokens["cache_creation"] += u.get("cache_creation_input_tokens") or 0

        stop = msg_api.get("stop_reason")
        texto = texto_da_resposta(msg_api.get("content") or [])
        try:
            if texto is None:
                raise json.JSONDecodeError("resposta sem bloco de texto", "", 0)
            dados = extrair_json(texto)
        except json.JSONDecodeError as e:
            falhas += 1
            msg = f"JSON inválido ({e.msg}); stop_reason={stop}"
            linhas_csv.append({"arquivo": nome, "status": "falha", "alertas": msg})
            todos_alertas.append((nome, "", "falha", msg))
            linhas_jsonl.append({"arquivo": nome, "custom_id": cid, "erro": msg, "texto_bruto": texto})
            log(f"  ✗ {nome}: {msg}")
            continue

        alertas = []
        try:
            if stop != "end_turn":
                alertas.append(("", "formato", f"stop_reason={stop}"))
            validar_formato(dados, alertas)
            verificar_consistencia(dados, nome, alertas)

            linha = {"arquivo": nome, "status": "ok"}
            for var in ORDEM:
                linha[var] = celula(dados, var)
            linha["alertas"] = " | ".join(f"{v}: {m}" if v else m for v, _, m in alertas)
        except Exception as e:  # um item malformado não pode derrubar o lote
            falhas += 1
            msg = f"erro de processamento ({type(e).__name__}: {e}); stop_reason={stop}"
            linhas_csv.append({"arquivo": nome, "status": "falha", "alertas": msg})
            todos_alertas.append((nome, "", "falha", msg))
            linhas_jsonl.append({"arquivo": nome, "custom_id": cid, "erro": msg, "texto_bruto": texto})
            log(f"  ✗ {nome}: {msg}")
            continue
        linhas_csv.append(linha)
        linhas_jsonl.append({"arquivo": nome, "custom_id": cid, "stop_reason": stop,
                             "codificacao": dados,
                             "alertas": [{"variavel": v, "tipo": t, "mensagem": m}
                                         for v, t, m in alertas]})
        todos_alertas += [(nome, v, t, m) for v, t, m in alertas]
        ok += 1
        if alertas:
            com_alerta += 1
        log(f"  {'⚠' if alertas else '✓'} {nome}" + (f" ({len(alertas)} alerta(s))" if alertas else ""))

    faltantes = [mapa[c] for c in mapa if c not in vistos]
    for nome in faltantes:
        linhas_csv.append({"arquivo": nome, "status": "falha", "alertas": "sem resultado no lote"})
        todos_alertas.append((nome, "", "falha", "sem resultado no lote"))

    linhas_csv.sort(key=lambda l: l["arquivo"])
    colunas = ["arquivo", "status"] + ORDEM + ["alertas"]
    # utf-8-sig para o Excel reconhecer os acentos
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
    log(f"Codificados: {ok} (com alerta: {com_alerta}) | falhas: {falhas} | sem resultado: {len(faltantes)}")
    log(f"Tokens — input: {tokens['input']:,} | output: {tokens['output']:,} | "
        f"cache read: {tokens['cache_read']:,} | cache creation: {tokens['cache_creation']:,}")
    log(f"\nArquivos: {SAIDA_CSV}, {SAIDA_JSONL}, {SAIDA_ALERTAS}")
    if falhas or faltantes:
        log("Há falhas: resubmeta só esses acórdãos (coloque-os sozinhos em ./textos).")

    Path(ARQUIVO_LOG).write_text("\n".join(linhas_log), encoding="utf-8")


if __name__ == "__main__":
    main()
