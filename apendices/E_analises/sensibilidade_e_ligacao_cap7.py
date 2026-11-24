"""Tabela de sensibilidade sem 2020 / sem 2020-2021 (subseção 6.2.1.1, Tabela 13) e ligação dos reconhecimentos
posteriores a setembro de 2023 com os julgados que aderiram à teoria (seção 6.3, Tabela 24).

RECONSTRUÇÃO escrita neste repositório a partir da descrição da conversa "Hipóteses rivais para
padrão confirmatório" (claude.ai, 19/11/2026). Julgados com adesão à teoria no voto condutor
(lista da conversa): Rcl 22328, 23899, 40565, 42273 e 59482. Corte: 29/09/2023.
Uso: python3 sensibilidade_e_ligacao_cap7.py matriz_consolidada_v3.xlsx
"""
import re, sys
import numpy as np, pandas as pd, networkx as nx

u = pd.read_excel(sys.argv[1], sheet_name="Unidades", dtype=str, keep_default_na=False)
u["Rcl"] = u["Reclamação"].astype(int); u["data"] = pd.to_datetime(u.V9_DATA.str.slice(0, 10))

# ---- Parte 1: sensibilidade do Mann-Whitney exato ----
t = u[(u.Estrato == "controle posterior") & (u.V13_ADER != "ND")].copy(); t["y"] = (t.V13_ADER == "reconhecida").astype(int)

def mw(df):
    r2 = np.rint(2 * df.data.rank(method="average").values).astype(int); y = df.y.values
    n1 = int(y.sum()); n0 = len(y) - n1; S = r2.sum(); dp = np.zeros((n1 + 1, S + 1)); dp[0, 0] = 1.0
    for v in r2:
        for j in range(n1, 0, -1): dp[j, v:] += dp[j - 1, :S + 1 - v]
    dist = dp[n1] / dp[n1].sum(); W = r2[y == 1].sum(); U = W / 2 - n1 * (n1 + 1) / 2
    return n1, n0, U, dist[W:].sum(), U / (n1 * n0)

print("Tabela de sensibilidade (Mann-Whitney exato, p unilateral)")
for nome, d in [("Série completa", t), ("Sem 2020", t[t.data.dt.year != 2020]), ("Sem 2020 e 2021", t[~t.data.dt.year.isin([2020, 2021])])]:
    n1, n0, U, p, ps = mw(d)
    md = lambda yy: d[d.y == yy].data.median().strftime("%d/%m/%Y")
    print(f"{nome}: {n1 + n0} ({n1} / {n0}); U {U:,.1f}; p {p:.3f}; PS {ps:.2f}; mediana 13-A {md(1)}; mediana 13-B {md(0)}")

# ---- Parte 2: ligação dos reconhecimentos posteriores a setembro de 2023 ----
pop = set(u.Rcl); ttmd = {22328, 23899, 40565, 42273, 59482}
cit = {r.Rcl: sorted({int(n) for n in re.findall(r"\bRcl[-\w]*\s*(\d+)", r.V16_JURIS) if int(n) in pop and int(n) != r.Rcl}) for r in u.itertuples()}
G = nx.DiGraph([(a, b) for a, bs in cit.items() for b in bs])
post = u[(u.V13_ADER == "reconhecida") & (u.data > pd.Timestamp("2023-09-29"))]
res = {"Citação direta": [], "Por um julgado intermediário": [], "Sem citação a julgados da população": [], "Apenas por caminho espúrio": []}
for r in post.itertuples():
    cs = cit[r.Rcl]
    if not cs: res["Sem citação a julgados da população"].append(r.Rcl); continue
    if set(cs) & ttmd: res["Citação direta"].append(r.Rcl); continue
    # caminho legítimo: só por acórdãos de reconhecimento anteriores (exclui negativas)
    H = nx.DiGraph([(a, b) for a, b in G.edges if u.set_index("Rcl").V13_ADER[a] == "reconhecida" and u.set_index("Rcl").V13_ADER[b] == "reconhecida"])
    ok = any(r.Rcl in H and t_ in H and nx.has_path(H, r.Rcl, t_) and nx.shortest_path_length(H, r.Rcl, t_) <= 2 for t_ in ttmd)
    (res["Por um julgado intermediário"] if ok else res["Apenas por caminho espúrio"]).append(r.Rcl)
print(f"\nLigação dos {len(post)} reconhecimentos posteriores a 29/09/2023")
for k, v in res.items(): print(f"{k}: {len(v)}  Rcl {', '.join(map(str, sorted(v)))}")
