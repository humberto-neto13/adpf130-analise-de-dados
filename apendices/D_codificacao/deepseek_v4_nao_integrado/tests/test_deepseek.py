"""Testes da versão DeepSeek. Nenhuma rede: a chamada à API é substituída por uma função simulada."""
import csv
import json
import re
import shutil
import sys
import urllib.error
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import codificar_deepseek_v4 as cod  # noqa: E402
import processar_deepseek_v4 as pdeep  # noqa: E402
import submeter_batch_v3 as sub  # noqa: E402

RE_CID = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


def json_ok(**mudancas):
    """Codificação completa e internamente coerente (nenhum alerta esperado)."""
    d = {
        "V1_FUND": {"classes": ["b"], "justificativa": "x"},
        "V2_MOD_REST": {"classes": ["b"], "justificativa": "x"},
        "V3_MOM_REST": {"classe": "posterior", "justificativa": "x"},
        "V4_RECLTE": {"classes": ["b"], "justificativa": "x"},
        "V5_MEIO": {"classes": ["e"], "justificativa": "x"},
        "V6_TRANSC": {"classes": ["d"], "justificativa": "x"},
        "V7_DIVERG": {"classes": ["d"], "justificativa": "x"},
        "V16_JURIS": {"citacoes": ["Rcl 3014", "Súmula 734"]},
        "V13_ADER": {"classe": "reconhecida", "justificativa": "x"},
        "V14_SEGUIM": {"classe": "dado", "justificativa": "x"},
        "V15_MERITO": {"classe": "procedente", "justificativa": "x"},
        "V8_ORG": "b", "V9_DATA": "22/03/2021", "V10_REL": "Alexandre de Moraes",
        "V11_RED": {"classe": "a", "nome": "Marco Aurélio"},
        "V12_VENCIDOS": ["Alexandre de Moraes"],
    }
    d.update(mudancas)
    return d


def como_texto(d):
    return json.dumps(d, ensure_ascii=False)


@pytest.fixture
def proj(tmp_path, monkeypatch):
    shutil.copy(RAIZ / cod.ARQUIVO_MANUAL, tmp_path / cod.ARQUIVO_MANUAL)
    (tmp_path / "textos").mkdir()
    for n, t in {"15243.txt": "Ementa A\r\nAcórdão um.\r\n", "45682.1.txt": "Ementa B com ção.\n",
                 "45682_1.txt": "colide no custom_id\n", "16074.txt": "Terceiro.\n"}.items():
        (tmp_path / "textos" / n).write_bytes(t.encode("utf-8"))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-FALSA")
    return tmp_path


def resposta(content, finish="stop", usage=None, reasoning=None):
    msg = {"role": "assistant", "content": content}
    if reasoning is not None:
        msg["reasoning_content"] = reasoning
    return {"choices": [{"message": msg, "finish_reason": finish}],
            "usage": usage or {"prompt_tokens": 100, "completion_tokens": 50,
                               "prompt_cache_hit_tokens": 60, "prompt_cache_miss_tokens": 40,
                               "completion_tokens_details": {"reasoning_tokens": 20}}}


class Servidor:
    """Função `chamar` simulada: registra os corpos e devolve/levanta o que o roteiro mandar."""
    def __init__(self, roteiro=None, padrao=None):
        self.corpos, self.roteiro = [], roteiro or {}
        self.padrao = padrao or (lambda corpo: resposta(como_texto(json_ok())))

    def __call__(self, corpo, chave):
        self.corpos.append((corpo, chave))
        nome = re.match(r"Arquivo: (.*)\n", corpo["messages"][1]["content"]).group(1)
        passo = self.roteiro.get(nome)
        if isinstance(passo, list):
            passo = passo.pop(0) if passo else None
        if isinstance(passo, Exception):
            raise passo
        if callable(passo):
            return passo(corpo)
        return passo if passo is not None else self.padrao(corpo)

    def nomes(self):
        return [re.match(r"Arquivo: (.*)\n", c["messages"][1]["content"]).group(1)
                for c, _ in self.corpos]


def http(codigo):
    return urllib.error.HTTPError("u", codigo, f"erro {codigo}", {}, None)


def rodar(*args, servidor=None):
    s = servidor or Servidor()
    cod.main(list(args), chamar=s, dormir=lambda t: None)
    return s


def respostas():
    return {r["custom_id"]: r for r in map(json.loads, open(cod.ARQUIVO_RESPOSTAS, encoding="utf-8"))}


# ----------------------------------------------------------------------------
# --simular e requisições
# ----------------------------------------------------------------------------

def test_simular_nao_chama_a_api_nem_exige_chave(proj, monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY")
    s = rodar("--simular")
    assert s.corpos == [] and not Path(cod.ARQUIVO_RESPOSTAS).exists()
    reqs = [json.loads(l) for l in open(cod.ARQUIVO_JSONL, encoding="utf-8")]
    m = json.loads(Path(cod.ARQUIVO_MAPA).read_text(encoding="utf-8"))
    cids = [r["custom_id"] for r in reqs]
    assert len(cids) == len(set(cids)) == 4 and all(RE_CID.match(c) for c in cids)
    assert m["ordem"] == cids and sorted(m["arquivos"].values()) == \
        ["15243.txt", "16074.txt", "45682.1.txt", "45682_1.txt"]
    assert (m["modelo"], m["max_tokens"], m["semente"]) == ("deepseek-v4-pro", sub.MAX_TOKENS, sub.SEMENTE)


def test_corpo_da_requisicao(proj):
    rodar("--simular")
    manual = (proj / cod.ARQUIVO_MANUAL).read_text(encoding="utf-8")
    for l in open(cod.ARQUIVO_JSONL, encoding="utf-8"):
        c = json.loads(l)["corpo"]
        assert c["model"] == "deepseek-v4-pro" and c["max_tokens"] == sub.MAX_TOKENS
        assert c["response_format"] == {"type": "json_object"} and c["stream"] is False
        assert "thinking" not in c and "reasoning_effort" not in c
        sistema, usuario = c["messages"]
        assert sistema["role"] == "system" and manual.strip() in sistema["content"]
        assert "JSON" in sistema["content"]          # exigido pelo modo json_object
        assert usuario["role"] == "user"


def test_mesmo_prompt_e_mesma_ordem_que_a_versao_claude(proj, monkeypatch):
    """A única diferença entre as duas execuções deve ser o modelo."""
    rodar("--simular")
    monkeypatch.setattr(sys, "argv", ["submeter_batch_v3.py", "--simular"])
    sub.main()
    claude = [json.loads(l) for l in open(sub.ARQUIVO_JSONL, encoding="utf-8")]
    deep = [json.loads(l) for l in open(cod.ARQUIVO_JSONL, encoding="utf-8")]
    assert [r["custom_id"] for r in claude] == [r["custom_id"] for r in deep]
    for a, b in zip(claude, deep):
        assert a["params"]["system"][0]["text"] == b["corpo"]["messages"][0]["content"]
        assert a["params"]["messages"][0]["content"] == b["corpo"]["messages"][1]["content"]


@pytest.mark.parametrize("modo,esperado", [
    ("padrao", {}),
    ("desligado", {"thinking": {"type": "disabled"}}),
    ("max", {"thinking": {"type": "enabled"}, "reasoning_effort": "max"}),
])
def test_modos_de_raciocinio(proj, modo, esperado):
    rodar("--simular", "--raciocinio", modo)
    for l in open(cod.ARQUIVO_JSONL, encoding="utf-8"):
        c = json.loads(l)["corpo"]
        for k, v in esperado.items():
            assert c[k] == v
        if not esperado:
            assert "thinking" not in c


def test_erros_de_entrada(proj, monkeypatch):
    (proj / cod.ARQUIVO_MANUAL).write_text("", encoding="utf-8")
    with pytest.raises(SystemExit):
        rodar("--simular")
    shutil.copy(RAIZ / cod.ARQUIVO_MANUAL, proj / cod.ARQUIVO_MANUAL)
    (proj / "textos" / "00001.txt").write_bytes("Acórdão".encode("latin-1"))
    with pytest.raises(SystemExit):
        rodar("--simular")


def test_sem_chave_no_modo_real(proj, monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY")
    with pytest.raises(SystemExit):
        rodar()


def test_acordao_vazio_omitido(proj, capsys):
    (proj / "textos" / "00001.txt").write_text("  \n", encoding="utf-8")
    rodar("--simular")
    assert "00001.txt" in capsys.readouterr().out
    assert "00001.txt" not in json.loads(Path(cod.ARQUIVO_MAPA).read_text(encoding="utf-8"))["arquivos"].values()


# ----------------------------------------------------------------------------
# Envio (função simulada)
# ----------------------------------------------------------------------------

def test_envio_grava_uma_resposta_por_acordao(proj):
    s = rodar()
    r = respostas()
    assert len(r) == 4 and all(x["status"] == "ok" for x in r.values())
    assert {c for _, c in s.corpos} == {"sk-FALSA"}
    x = next(iter(r.values()))
    assert x["finish_reason"] == "stop" and x["usage"]["cache_hit"] == 60
    assert x["usage"]["reasoning_tokens"] == 20 and json.loads(x["content"])["V8_ORG"] == "b"


def test_primeira_requisicao_vai_sozinha_para_formar_o_cache(proj):
    s = rodar("--conc", "1")
    m = json.loads(Path(cod.ARQUIVO_MAPA).read_text(encoding="utf-8"))
    assert s.nomes() == [m["arquivos"][c] for c in m["ordem"]]


def test_retomada_nao_reenvia_o_que_ja_esta_ok(proj):
    rodar()
    s = rodar()
    assert s.corpos == []
    assert len(open(cod.ARQUIVO_RESPOSTAS, encoding="utf-8").readlines()) == 4


def test_interrupcao_e_retomada(proj):
    rodar("--simular")
    m = json.loads(Path(cod.ARQUIVO_MAPA).read_text(encoding="utf-8"))
    primeiro = m["arquivos"][m["ordem"][0]]
    with open(cod.ARQUIVO_RESPOSTAS, "w", encoding="utf-8") as f:
        f.write(json.dumps({"custom_id": m["ordem"][0], "status": "ok", "finish_reason": "stop",
                            "content": como_texto(json_ok()), "usage": {}}) + "\n")
        f.write('{"custom_id": "cortada", "sta')      # linha cortada pela interrupção
    s = rodar()
    assert primeiro not in s.nomes() and len(s.nomes()) == 3


@pytest.mark.parametrize("codigo", [429, 500, 503])
def test_erro_transitorio_tem_nova_tentativa(proj, codigo):
    s = rodar(servidor=Servidor({"15243.txt": [http(codigo), None]}))
    assert respostas()[next(c for c, r in respostas().items())]["status"] == "ok"
    assert s.nomes().count("15243.txt") == 2
    assert all(r["status"] == "ok" for r in respostas().values())


def test_erro_transitorio_persistente_vira_falha(proj):
    s = rodar(servidor=Servidor({"15243.txt": [http(503)] * 5}))
    assert s.nomes().count("15243.txt") == cod.TENTATIVAS
    falhos = [r for r in respostas().values() if r["status"] == "falha"]
    assert len(falhos) == 1 and "503" in falhos[0]["erro"]


def test_erro_400_nao_e_reenviado(proj):
    s = rodar(servidor=Servidor({"15243.txt": [http(400)] * 5}))
    assert s.nomes().count("15243.txt") == 1


@pytest.mark.parametrize("erro", [urllib.error.URLError("sem rede"), TimeoutError("lento"),
                                  ConnectionResetError("caiu")])
def test_falhas_de_rede_tem_nova_tentativa(proj, erro):
    s = rodar(servidor=Servidor({"15243.txt": [erro, None]}))
    assert s.nomes().count("15243.txt") == 2


@pytest.mark.parametrize("codigo", [401, 402])
def test_erro_fatal_interrompe_e_preserva_o_que_ha(proj, codigo):
    srv = Servidor({n: [http(codigo)] * 5 for n in
                    ("15243.txt", "16074.txt", "45682.1.txt", "45682_1.txt")})
    with pytest.raises(SystemExit):
        rodar("--conc", "1", servidor=srv)
    assert len(srv.corpos) == 1          # parou na primeira; nada mais foi enviado


def test_resposta_vazia_e_repetida_e_depois_falha(proj):
    vazia = lambda corpo: resposta("")
    s = rodar(servidor=Servidor({"15243.txt": vazia}))
    assert s.nomes().count("15243.txt") == cod.TENTATIVAS
    f = [r for r in respostas().values() if r["status"] == "falha"]
    assert len(f) == 1 and "vazia" in f[0]["erro"]


def test_resposta_vazia_que_se_resolve_na_segunda(proj):
    s = rodar(servidor=Servidor({"15243.txt": [resposta(""), None]}))
    assert all(r["status"] == "ok" for r in respostas().values())
    assert s.nomes().count("15243.txt") == 2


def test_truncada_por_length_e_gravada_sem_repetir(proj):
    trunc = lambda corpo: resposta('{"V1_FUND": {"classes": ["a"', finish="length")
    s = rodar(servidor=Servidor({"15243.txt": trunc}))
    assert s.nomes().count("15243.txt") == 1
    assert any(r["finish_reason"] == "length" and r["status"] == "ok" for r in respostas().values())


def test_length_sem_conteudo_nao_e_repetido(proj):
    so_raciocinio = lambda corpo: resposta("", finish="length", reasoning="pensando…")
    s = rodar(servidor=Servidor({"15243.txt": so_raciocinio}))
    assert s.nomes().count("15243.txt") == 1


def test_falha_anterior_e_reenviada_na_proxima_execucao(proj):
    rodar(servidor=Servidor({"15243.txt": [http(400)]}))
    assert sum(r["status"] == "falha" for r in respostas().values()) == 1
    s = rodar()
    assert s.nomes() == ["15243.txt"]
    assert respostas()  # a última linha de cada custom_id prevalece
    assert all(r["status"] == "ok" for r in respostas().values())


# ----------------------------------------------------------------------------
# chamar_api (sem rede: urlopen substituído)
# ----------------------------------------------------------------------------

def test_chamar_api_monta_requisicao_http(monkeypatch):
    vistos = {}

    class R:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def read(self): return json.dumps({"ok": 1}).encode()

    def falso(req, timeout):
        vistos.update(url=req.full_url, metodo=req.get_method(), auth=req.get_header("Authorization"),
                      corpo=json.loads(req.data), timeout=timeout)
        return R()

    monkeypatch.setattr(cod.urllib.request, "urlopen", falso)
    assert cod.chamar_api({"a": "ç"}, "sk-X") == {"ok": 1}
    assert vistos == {"url": "https://api.deepseek.com/chat/completions", "metodo": "POST",
                      "auth": "Bearer sk-X", "corpo": {"a": "ç"}, "timeout": cod.TIMEOUT}


# ----------------------------------------------------------------------------
# Processador
# ----------------------------------------------------------------------------

def linhas_csv():
    with open(pdeep.SAIDA_CSV, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def test_processar_sem_arquivos(proj):
    with pytest.raises(SystemExit):
        pdeep.main()


def test_processar_ciclo_completo_com_acentos(proj):
    rodar()
    pdeep.main()
    rows = linhas_csv()
    assert [r["arquivo"] for r in rows] == ["15243.txt", "16074.txt", "45682.1.txt", "45682_1.txt"]
    assert all(r["status"] == "ok" and r["alertas"] == "" for r in rows)
    assert rows[0]["V11_RED"] == "a: Marco Aurélio" and rows[0]["V16_JURIS"] == "Rcl 3014; Súmula 734"
    for n in (pdeep.SAIDA_CSV, pdeep.SAIDA_ALERTAS):
        assert open(n, "rb").read().startswith(b"\xef\xbb\xbf")
    bruto = open(pdeep.SAIDA_JSONL, "rb").read()
    assert b"\\u" not in bruto and "Aurélio".encode() in bruto
    log = open(pdeep.ARQUIVO_LOG, encoding="utf-8").read()
    assert "Codificados: 4 (com alerta: 0) | falhas: 0" in log
    assert "cache hit: 240 | miss: 160" in log and "raciocínio: 80" in log


def test_processar_casos_de_resposta(proj):
    rodar("--simular")
    m = json.loads(Path(cod.ARQUIVO_MAPA).read_text(encoding="utf-8"))
    por_nome = {n: c for c, n in m["arquivos"].items()}
    dados = {
        "15243.txt": resposta(f"```json\n{como_texto(json_ok())}\n```"),                    # cercas
        "16074.txt": resposta("Segue:\n" + como_texto(json_ok(V13_ADER={"classe": "não reconhecida"}))),
        "45682.1.txt": resposta('{"V1_FUND": {"classes": ["a"', finish="length"),           # truncada
        "45682_1.txt": resposta(como_texto(json_ok(V8_ORG=["b"]))),                          # tipo errado
    }
    with open(cod.ARQUIVO_RESPOSTAS, "w", encoding="utf-8") as f:
        for n, r in dados.items():
            f.write(json.dumps({"custom_id": por_nome[n], "status": "ok", **cod.resumir(r)}) + "\n")
    pdeep.main()
    rows = {r["arquivo"]: r for r in linhas_csv()}
    assert rows["15243.txt"]["status"] == "ok" and rows["15243.txt"]["alertas"] == ""
    assert "V13_ADER: V15 procedente com V13='não reconhecida'" in rows["16074.txt"]["alertas"]
    assert rows["45682.1.txt"]["status"] == "falha" and "finish_reason=length" in rows["45682.1.txt"]["alertas"]
    assert rows["45682_1.txt"]["status"] == "ok" and "V8_ORG" in rows["45682_1.txt"]["alertas"]


def test_processar_finish_reason_diferente_de_stop_vira_alerta(proj):
    rodar("--simular")
    m = json.loads(Path(cod.ARQUIVO_MAPA).read_text(encoding="utf-8"))
    cid = m["ordem"][0]
    with open(cod.ARQUIVO_RESPOSTAS, "w", encoding="utf-8") as f:
        f.write(json.dumps({"custom_id": cid, "status": "ok",
                            **cod.resumir(resposta(como_texto(json_ok()), finish="length"))}) + "\n")
    pdeep.main()
    r = next(r for r in linhas_csv() if r["arquivo"] == m["arquivos"][cid])
    assert r["status"] == "ok" and r["alertas"] == "finish_reason=length"


def test_processar_falha_de_api_ausente_e_desconhecida(proj):
    rodar(servidor=Servidor({"15243.txt": [http(400)]}))
    with open(cod.ARQUIVO_RESPOSTAS, "a", encoding="utf-8") as f:
        f.write(json.dumps({"custom_id": "intruso", "status": "ok", "content": "{}"}) + "\n")
    lin = [l for l in open(cod.ARQUIVO_RESPOSTAS, encoding="utf-8")]
    ok = [l for l in lin if json.loads(l)["status"] == "ok"][:2] + [lin[-1]]
    open(cod.ARQUIVO_RESPOSTAS, "w", encoding="utf-8").write("".join(l for l in lin if l in ok or json.loads(l)["status"] == "falha"))
    pdeep.main()
    rows = {r["arquivo"]: r for r in linhas_csv()}
    assert rows["15243.txt"]["alertas"].startswith("falha na API: HTTP 400")
    assert any(a.startswith("[custom_id desconhecido: intruso]") for a in rows)
    assert any(r["alertas"] == "sem resposta gravada" for r in rows.values())
