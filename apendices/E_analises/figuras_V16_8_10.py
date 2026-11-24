"""Figuras 8 a 10 da seção 6.3 (rede de citações internas da V16).

RECONSTRUÇÃO escrita neste repositório a partir da descrição da conversa "Hipóteses rivais para
padrão confirmatório" (claude.ai, 19/11/2026); os scripts originais não foram conservados, e o
aspecto gráfico pode diferir das figuras do texto. Convenções: Fig. 8 (diagrama de arcos), unidades em
uma linha do tempo, arco do citante (à direita) ao citado (à esquerda), acima da linha as citações feitas
por reconhecimentos (azul) e abaixo as feitas por negativas (laranja), cor do ponto pelo desfecho,
tamanho pelo número de citações recebidas, contorno para adesão à teoria no voto condutor, forma pelo
órgão (círculo, 1ª Turma; quadrado, 2ª Turma; triângulo, Plenário). Fig. 9: julgados citados ao menos
cinco vezes, por ano e desfecho do citante. Fig. 10: citações acumuladas desses julgados, com a data
candidata de Pettitt (26/11/2021).
Uso: python3 figuras_V16_8_10.py matriz_consolidada_v3.xlsx [pasta_saida]
"""
import re, sys, os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

ARQ = sys.argv[1]; OUT = sys.argv[2] if len(sys.argv) > 2 else "saidas_figuras_V16"; os.makedirs(OUT, exist_ok=True)
u = pd.read_excel(ARQ, sheet_name="Unidades", dtype=str, keep_default_na=False)
u["Rcl"] = u["Reclamação"].astype(int); u["data"] = pd.to_datetime(u.V9_DATA.str.slice(0, 10))
D = u.set_index("Rcl"); pop = set(u.Rcl); ADES = {22328, 23899, 40565, 42273, 59482}
E = pd.DataFrame([(r.Rcl, int(n)) for r in u.itertuples() for n in set(re.findall(r"\bRcl[-\w]*\s*(\d+)", r.V16_JURIS)) if int(n) in pop and int(n) != r.Rcl], columns=["citante", "citado"])
E["des"] = E.citante.map(D.V13_ADER); E["dc"] = E.citante.map(D.data); E["dd"] = E.citado.map(D.data)
AZ, LA, CZ = "#1f6fb4", "#d9822b", "#8a8a8a"
orgf = lambda o: {"a": "^", "b": "o", "c": "s"}[o]  # V8: a Plenário, b Primeira Turma, c Segunda Turma
print("citações internas (pares únicos):", len(E)); rec = E.citado.value_counts()
print("mais citados:", rec.head(8).to_dict()); top = rec[rec >= 5].index.tolist(); print("citados >=5 vezes:", len(top), top)

# Figura 8: arcos
fig, ax = plt.subplots(figsize=(13, 6.2)); x = lambda d: (d - u.data.min()).days
for r in E.itertuples():
    x0, x1 = x(r.dd), x(r.dc); w = abs(x1 - x0); h = 2 * 0.05 * np.sqrt(w); s = 1 if r.des == "reconhecida" else -1
    t_ = np.linspace(0, np.pi, 60); ax.plot((x0 + x1) / 2 + (x1 - x0) / 2 * np.cos(t_), s * h * np.sin(t_), color=AZ if s > 0 else LA, lw=0.6, alpha=0.45)
for r in u.itertuples():
    n = int((E.citado == r.Rcl).sum()); ax.scatter(x(r.data), 0, s=18 + 20 * n, marker=orgf(r.V8_ORG), c=AZ if r.V13_ADER == "reconhecida" else (LA if r.V13_ADER != "ND" else CZ),
        edgecolors="black" if r.Rcl in ADES else "white", linewidths=1.8 if r.Rcl in ADES else 0.4, zorder=3)
    if n >= 8: ax.annotate(f"Rcl {r.Rcl:,}".replace(",", "."), (x(r.data), 0), xytext=(0, 12 + 9 * (hash(r.Rcl) % 3) if r.V13_ADER == "reconhecida" else -16 - 9 * (hash(r.Rcl) % 3)), textcoords="offset points", ha="center", fontsize=7)
anos = range(u.data.dt.year.min(), u.data.dt.year.max() + 1); ax.set_xticks([x(pd.Timestamp(f"{a}-01-01")) for a in anos]); ax.set_xticklabels(list(anos), fontsize=8)
ax.axhline(0, color="black", lw=0.5); ax.set_yticks([]); ax.text(0.01, 0.97, "Citações feitas por acórdãos que reconheceram a aderência", transform=ax.transAxes, color=AZ, fontsize=9, va="top")
ax.text(0.01, 0.03, "Citações feitas por acórdãos que a negaram", transform=ax.transAxes, color=LA, fontsize=9)
for sp in ["top", "right", "left"]: ax.spines[sp].set_visible(False)
for ext in ("png", "pdf"): fig.savefig(f"{OUT}/arcos_citacoes_V16.{ext}", dpi=300, bbox_inches="tight")

# Figura 9: citações por ano, desfecho do citante, julgados citados >= 5 vezes
ordem = sorted(top, key=lambda r: D.data[r]); fig, ax = plt.subplots(figsize=(11, 0.5 * len(ordem) + 1.5))
for i, r in enumerate(ordem):
    ax.axhline(i, color="#dddddd", lw=0.5); ax.scatter(D.data[r].year + (D.data[r].dayofyear / 366), i, marker="D", c="black", s=25, zorder=3)
    for yr, g in E[E.citado == r].groupby(E.dc.dt.year):
        for k, des in enumerate(["reconhecida", "não reconhecida"]):
            n = int((g.des == des).sum())
            if n: ax.scatter(yr + 0.5 + (0.12 if k else -0.12), i, s=40 * n, c=AZ if k == 0 else LA, alpha=.8, zorder=2)
ax.set_yticks(range(len(ordem))); ax.set_yticklabels([f"Rcl {r:,}".replace(",", ".") + (" *" if r in ADES else "") for r in ordem], fontsize=8)
ax.set_xlim(2013, 2027); ax.set_title("Julgados citados pelo menos cinco vezes, por ano e desfecho do acórdão citante (azul, reconhecimento; laranja, negativa)", fontsize=9)
fig.savefig(f"{OUT}/julgados_citados_5vezes_por_ano_V16.png", dpi=300, bbox_inches="tight")

# Figura 10: citações acumuladas
fig, axs = plt.subplots(1, 2, figsize=(12, 4.2), sharey=False); P = pd.Timestamp("2021-11-26")
for ax, des, cor, tit in [(axs[0], "reconhecida", AZ, "Citados por reconhecimentos"), (axs[1], "não reconhecida", LA, "Citados por negativas")]:
    for r in top:
        g = E[(E.citado == r) & (E.des == des)].sort_values("dc")
        if len(g) >= 1: ax.step(g.dc, np.arange(1, len(g) + 1), where="post", lw=1.2, label=f"Rcl {r:,}".replace(",", "."))
    ax.axvline(P, color="gray", lw=8, alpha=.2); ax.set_title(tit, fontsize=9, color=cor); ax.legend(fontsize=6, ncol=2, frameon=False)
fig.savefig(f"{OUT}/evolucao_julgados_citados_5vezes_V16.png", dpi=300, bbox_inches="tight")
print("figuras em", OUT)
