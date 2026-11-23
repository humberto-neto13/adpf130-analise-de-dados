"""
Figuras da etapa confirmatória. Requer testes.py e matriz_consolidada_v3.xlsx na mesma pasta.
Bibliotecas adicionais: matplotlib, statsmodels (só para a curva logística).
Execução:  python figuras.py   (as figuras são gravadas na pasta do script)
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from testes import ARQ, carregar, tabela_anual, wilson, pettitt

PASTA = Path(__file__).resolve().parent
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
                     "font.size": 11})


def _pontos(ax, x, a, rot):
    ax.errorbar(x, a["p"], yerr=[a["p"] - a["lo"], a["hi"] - a["p"]], fmt="o", color="black",
                ecolor="0.55", capsize=3, ms=5, lw=1)
    for xi, (_, r) in zip(x, a.iterrows()):
        ax.annotate(f"n={int(r['n'])}", (xi, r["hi"]), textcoords="offset points", xytext=(0, 4),
                    ha="center", fontsize=8)
    ax.set_ylim(-0.05, 1.15)
    ax.set_ylabel("Proporção de aderência reconhecida")
    ax.set_xlabel(rot)
    ax.spines[["top", "right"]].set_visible(False)


def _anual(t):
    a = tabela_anual(t).rename(columns={"proporção": "p", "IC_inf": "lo", "IC_sup": "hi"})
    return a.reset_index()


def _salvar(fig, nome):
    fig.tight_layout()
    fig.savefig(PASTA / nome, dpi=300)
    plt.close(fig)


def anual_posterior(curva=None):
    """Proporção anual no controle posterior; curva = None, 'degrau' ou 'logistica'."""
    t = carregar("controle posterior")
    a = _anual(t)
    fig, ax = plt.subplots(figsize=(6.3, 3.6))
    desloc = 0.5 if curva else 0.0  # com curva, pontos no meio do ano
    if curva == "degrau":
        pt = pettitt(t)
        k = pt["posicao"] - 1
        tx = t["ano"] + (t["data"].dt.dayofyear - 1) / 365.25
        corte = (tx[k] + tx[k + 1]) / 2
        p0, p1 = pt["antes"][0] / pt["antes"][1], pt["depois"][0] / pt["depois"][1]
        ax.hlines(p0, a["ano"].min(), corte, color="0.3", lw=1.2)
        ax.hlines(p1, corte, a["ano"].max() + 1, color="0.3", lw=1.2)
        ax.vlines(corte, p0, p1, color="0.3", lw=0.8, ls=":")
    elif curva == "logistica":
        import statsmodels.api as sm
        tx = t["ano"] + (t["data"].dt.dayofyear - 1) / 365.25
        fit = sm.Logit(t["y"], sm.add_constant(tx - 2020)).fit(disp=0)
        g = np.linspace(a["ano"].min(), a["ano"].max() + 1, 300)
        Xg = sm.add_constant(g - 2020)
        eta = Xg @ fit.params.values
        se = np.sqrt(np.einsum("ij,jk,ik->i", Xg, fit.cov_params().values, Xg))
        sig = lambda v: 1 / (1 + np.exp(-v))
        ax.fill_between(g, sig(eta - 1.96 * se), sig(eta + 1.96 * se), color="0.88", lw=0)
        ax.plot(g, sig(eta), color="0.3", lw=1.2)
    else:
        pt = pettitt(t)
        ax.axvline(pt["ultima_antes"][1].year + 0.5, color="0.4", ls="--", lw=0.8)
    _pontos(ax, a["ano"] + desloc, a, "Ano do julgamento")
    ax.set_xticks(a["ano"] + desloc)
    ax.set_xticklabels(a["ano"], fontsize=9)
    nome = {None: "figura_controle_posterior.png", "degrau": "figura_controle_posterior_degrau.png",
            "logistica": "figura_controle_posterior_logistica.png"}[curva]
    _salvar(fig, nome)


def bienal_posterior(inicio, nome):
    t = carregar("controle posterior")
    b = inicio + ((t["ano"] - inicio) // 2) * 2
    linhas = []
    for s, g in t.groupby(b):
        fim = min(s + 1, t["ano"].max())
        lo, hi = wilson(g["y"].sum(), len(g))
        linhas.append({"rot": f"{s}–{fim}" if fim > s else f"{s}", "n": len(g),
                       "p": g["y"].mean(), "lo": lo, "hi": hi})
    a = pd.DataFrame(linhas)
    fig, ax = plt.subplots(figsize=(6.3, 3.6))
    x = np.arange(len(a))
    _pontos(ax, x, a, "Biênio do julgamento")
    ax.set_xticks(x)
    ax.set_xticklabels(a["rot"], fontsize=9)
    _salvar(fig, nome)


def casos_previo():
    t = carregar("controle prévio")
    fig, ax = plt.subplots(figsize=(6.3, 2.2))
    for _, r in t.iterrows():
        ax.plot(r["data"], r["y"], "o" if r["y"] else "s", color="black" if r["y"] else "white",
                mec="black", ms=6)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["não reconhecida", "reconhecida"])
    ax.set_ylim(-0.6, 1.6)
    ax.set_xlabel("Data do julgamento")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", color="0.9")
    _salvar(fig, "figura_controle_previo.png")


def censo_geral():
    u = pd.read_excel(ARQ, sheet_name="Unidades", dtype=str, keep_default_na=False)
    u = u[u["V13_ADER"] != "ND"].copy()
    u["ano"] = pd.to_datetime(u["V9_DATA"]).dt.year
    u["y"] = (u["V13_ADER"] == "reconhecida").astype(int)
    a = _anual(u)
    fig, ax = plt.subplots(figsize=(6.3, 3.6))
    _pontos(ax, a["ano"], a, "Ano do julgamento")
    ax.set_xticks(range(a["ano"].min(), a["ano"].max() + 1))
    ax.tick_params(axis="x", labelsize=8, rotation=45)
    _salvar(fig, "figura_censo_geral.png")


if __name__ == "__main__":
    anual_posterior()
    anual_posterior("degrau")
    anual_posterior("logistica")
    bienal_posterior(2014, "figura_controle_posterior_bienal.png")
    bienal_posterior(2013, "figura_controle_posterior_bienal_alternativo.png")
    casos_previo()
    censo_geral()
    print("Figuras gravadas em", PASTA)
