"""
Etapa confirmatória da monografia: testes estatísticos.

Requer, na mesma pasta, o arquivo matriz_consolidada_v3.xlsx (aba "Unidades").
Bibliotecas: numpy, pandas, openpyxl.  Execução:  python testes.py

Protocolo (fixado antes do cruzamento da V13 com as datas):
- Teste da hipótese no estrato de controle posterior, excluídas as unidades com V13 ND.
- Mann-Whitney exato, unilateral (reconhecidas mais recentes), postos médios nas datas empatadas.
- Pettitt sobre a sequência binária ordenada pela data (desempate pelo número da reclamação),
  p-valor por permutação, 10.000 reembaralhamentos, semente fixa.
- Nível de significância de 0,05.
Os testes no controle prévio são exploratórios e não integram o protocolo.
"""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 20261012
N_PERM = 10_000
ARQ = Path(__file__).resolve().parent / "matriz_consolidada_v3.xlsx"


def carregar(estrato):
    """Unidades de um estrato, sem V13 ND, em ordem cronológica (desempate pelo número da Rcl)."""
    u = pd.read_excel(ARQ, sheet_name="Unidades", dtype=str, keep_default_na=False)  # preserva o texto "NA"
    u["data"] = pd.to_datetime(u["V9_DATA"])
    u["Rcl"] = u["Reclamação"].astype(int)
    t = u[(u["Estrato"] == estrato) & (u["V13_ADER"] != "ND")].copy()
    t["y"] = (t["V13_ADER"] == "reconhecida").astype(int)
    t["ano"] = t["data"].dt.year
    return t.sort_values(["data", "Rcl"]).reset_index(drop=True)


def wilson(k, m, z=1.959964):
    """Intervalo de Wilson a 95% para k sucessos em m casos."""
    p = k / m
    d = 1 + z * z / m
    c = (p + z * z / (2 * m)) / d
    h = z * np.sqrt(p * (1 - p) / m + z * z / (4 * m * m)) / d
    return c - h, c + h


def tabela_anual(t):
    a = t.groupby("ano")["y"].agg(["count", "sum"]).rename(columns={"count": "n", "sum": "reconhecida"})
    a["proporção"] = a["reconhecida"] / a["n"]
    a[["IC_inf", "IC_sup"]] = [wilson(k, m) for k, m in zip(a["reconhecida"], a["n"])]
    return a


def mann_whitney_exato(t):
    """Distribuição exata da soma dos postos das reconhecidas, condicionada aos empates observados."""
    y = t["y"].values
    n, n1 = len(y), int(y.sum())
    n0 = n - n1
    r2 = np.rint(2 * t["data"].rank(method="average").values).astype(int)  # postos médios x2 -> inteiros
    S = r2.sum()
    dp = np.zeros((n1 + 1, S + 1))
    dp[0, 0] = 1.0
    for v in r2:  # contagem de subconjuntos de tamanho n1 por soma de postos
        for j in range(n1, 0, -1):
            dp[j, v:] += dp[j - 1, : S + 1 - v]
    dist = dp[n1] / dp[n1].sum()
    W = r2[y == 1].sum()
    centro = n1 * (n + 1)  # valor esperado de W (em postos x2)
    somas = np.arange(S + 1)
    p_uni = dist[W:].sum()
    p_bi = dist[np.abs(somas - centro) >= abs(W - centro) - 1e-9].sum()
    U = W / 2 - n1 * (n1 + 1) / 2
    return {"n1": n1, "n0": n0, "U": U, "U_neutro": n1 * n0 / 2, "p_unilateral": p_uni,
            "p_bilateral": p_bi, "prob_superioridade": U / (n1 * n0)}


def _pettitt_K(x):
    s = np.sign(x[None, :] - x[:, None])  # s[i, j] = sgn(x_j - x_i)
    Ut = np.array([s[: k + 1, k + 1 :].sum() for k in range(len(x) - 1)])
    k = int(np.abs(Ut).argmax())
    return abs(Ut[k]), k


def pettitt(t, n_perm=N_PERM, seed=SEED):
    x = t["y"].values
    K, k = _pettitt_K(x)
    rng = np.random.default_rng(seed)
    Ks = np.array([_pettitt_K(rng.permutation(x))[0] for _ in range(n_perm)])
    n = len(x)
    return {"K": K, "posicao": k + 1,
            "ultima_antes": (t["Rcl"][k], t["data"][k].date()),
            "primeira_depois": (t["Rcl"][k + 1], t["data"][k + 1].date()),
            "p_permutacao": (np.sum(Ks >= K) + 1) / (n_perm + 1),
            "p_aproximado": min(1.0, 2 * np.exp(-6 * K**2 / (n**3 + n**2))),
            "antes": (int(x[: k + 1].sum()), k + 1), "depois": (int(x[k + 1 :].sum()), n - k - 1)}


def relatorio(estrato, rotulo):
    t = carregar(estrato)
    mw, pt = mann_whitney_exato(t), pettitt(t)
    print(f"\n=== {rotulo} ({estrato}) ===")
    print(f"Unidades: {len(t)}  reconhecida: {mw['n1']}  não reconhecida: {mw['n0']}")
    print(tabela_anual(t).round(3).to_string())
    print(f"Mann-Whitney exato: U = {mw['U']}  (neutro = {mw['U_neutro']})  "
          f"p unilateral = {mw['p_unilateral']:.4f}  p bilateral = {mw['p_bilateral']:.4f}  "
          f"prob. de superioridade = {mw['prob_superioridade']:.3f}")
    a, d = pt["antes"], pt["depois"]
    print(f"Pettitt: K = {pt['K']}  p (permutação) = {pt['p_permutacao']:.4f}  "
          f"p (aproximação clássica) = {pt['p_aproximado']:.4f}")
    print(f"  mudança entre Rcl {pt['ultima_antes'][0]} ({pt['ultima_antes'][1]}) e "
          f"Rcl {pt['primeira_depois'][0]} ({pt['primeira_depois'][1]})")
    print(f"  antes: {a[0]}/{a[1]} = {a[0]/a[1]:.3f}   depois: {d[0]}/{d[1]} = {d[0]/d[1]:.3f}")


if __name__ == "__main__":
    relatorio("controle posterior", "Teste da hipótese")
    relatorio("controle prévio", "Exploratório, fora do protocolo")
