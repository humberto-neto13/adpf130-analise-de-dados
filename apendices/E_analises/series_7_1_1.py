"""Fundamentação em série (análise que não consta do texto da versão atual da monografia; antiga seção 7.1.1): agrupa unidades em séries e refaz o Mann-Whitney exato.

RECONSTRUÇÃO escrita neste repositório, a partir da regra descrita na conversa "Hipóteses
rivais para padrão confirmatório" (claude.ai, 19/11/2026); o script original não foi conservado.
Regra principal: mesmo relator, mesmo desfecho na V13, no máximo 180 dias entre os julgamentos
e sobreposição >= 0,5 dos julgados da V16 (compartilhados / total distinto), com formação por
encadeamento (componentes conexos); unidades sem julgados citados ficam isoladas; cada série
vale uma observação, datada pelo primeiro julgamento. Regra estrita: mesmo relator, mesmo
desfecho e mesma data.
Uso: python3 series_7_1_1.py matriz_consolidada_v3.xlsx
"""
import sys
import numpy as np
import pandas as pd

ARQ = sys.argv[1] if len(sys.argv) > 1 else "matriz_consolidada_v3.xlsx"
u = pd.read_excel(ARQ, sheet_name="Unidades", dtype=str, keep_default_na=False)
u["Rcl"] = u["Reclamação"].astype(int)
u["data"] = pd.to_datetime(u["V9_DATA"].str.slice(0, 10))
t = u[(u.Estrato == "controle posterior") & (u.V13_ADER != "ND")].copy()
t["y"] = (t.V13_ADER == "reconhecida").astype(int)
t = t.sort_values(["data", "Rcl"]).reset_index(drop=True)
t["jur"] = t.V16_JURIS.map(lambda s: set() if s.strip() in ("", "(vazio)") else {x.strip() for x in s.split(";") if x.strip()})


def componentes(n, aresta):
    pai = list(range(n))
    def f(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]; i = pai[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            if aresta(i, j):
                pai[f(i)] = f(j)
    return [f(i) for i in range(n)]


def principal(i, j):
    a, b = t.iloc[i], t.iloc[j]
    if a.V10_REL != b.V10_REL or a.y != b.y or abs((a.data - b.data).days) > 180:
        return False
    if not a.jur or not b.jur:
        return False
    return len(a.jur & b.jur) / len(a.jur | b.jur) >= 0.5


def estrita(i, j):
    a, b = t.iloc[i], t.iloc[j]
    return a.V10_REL == b.V10_REL and a.y == b.y and a.data == b.data


def mw_exato(datas, y):
    y = np.asarray(y); n1 = int(y.sum()); n0 = len(y) - n1
    r2 = np.rint(2 * pd.Series(datas).rank(method="average").values).astype(int)
    S = r2.sum(); dp = np.zeros((n1 + 1, S + 1)); dp[0, 0] = 1.0
    for v in r2:
        for j in range(n1, 0, -1):
            dp[j, v:] += dp[j - 1, :S + 1 - v]
    dist = dp[n1] / dp[n1].sum(); W = r2[y == 1].sum()
    return (W / 2 - n1 * (n1 + 1) / 2) / (n1 * n0), dist[W:].sum()


def testar(nome, aresta):
    t["serie"] = componentes(len(t), aresta)
    s = t.groupby("serie").agg(data=("data", "min"), y=("y", "first"), n=("Rcl", "size"), rcls=("Rcl", list)).reset_index()
    ps, p = mw_exato(s.data, s.y)
    print(f"{nome}: {len(s)} observações ({int(s.y.sum())} / {len(s) - int(s.y.sum())}); PS {ps:.2f}; p unilateral {p:.3f}")
    for r in s[s.n > 1].itertuples():
        print(f"   série de {r.n}: Rcl {', '.join(map(str, sorted(r.rcls)))} (primeiro julgamento {r.data:%d/%m/%Y})")
    return s


print(f"Original: {len(t)} observações ({t.y.sum()} / {len(t) - t.y.sum()}); PS {mw_exato(t.data, t.y)[0]:.2f}; p unilateral {mw_exato(t.data, t.y)[1]:.3f}")
sp = testar("Regra principal", principal)
se = testar("Regra estrita", estrita)
sp2020 = sp[sp.data.dt.year == 2020]
print(f"2020 pela regra principal: {len(sp2020)} observações, {int(sp2020.y.sum())} com 13-A ({100 * sp2020.y.mean():.0f}%)")
