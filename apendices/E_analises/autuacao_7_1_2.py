"""Julgamento represado e datação pela autuação (antiga seção 7.1.2; no texto atual, só as datações pela autuação das subseções 6.2.1.2 e 6.2.2.2) e sensibilidade do controle negativo (subseção 6.2.2.2).

RECONSTRUÇÃO escrita neste repositório. Usa as datas de autuação da base de processos da classe
Rcl do Corte Aberta (autuacao_133.csv, extraída em 23/11/2026) e a matriz consolidada.
Uso: python3 autuacao_7_1_2.py matriz_consolidada_v3.xlsx autuacao_133.csv
"""
import sys
import numpy as np, pandas as pd
from scipy.stats import fisher_exact, mannwhitneyu

u = pd.read_excel(sys.argv[1], sheet_name="Unidades", dtype=str, keep_default_na=False)
a = pd.read_csv(sys.argv[2], parse_dates=["autuacao"])
u["Rcl"] = u["Reclamação"].astype(int)
u["data"] = pd.to_datetime(u["V9_DATA"].str.slice(0, 10))
t = u[(u.Estrato == "controle posterior") & (u.V13_ADER != "ND")].merge(a, left_on="Rcl", right_on="Reclamação", how="left")
t["y"] = (t.V13_ADER == "reconhecida").astype(int)
t["tram"] = (t.data - t.autuacao).dt.days / 365.25
t["per"] = np.where(t.data.dt.year <= 2019, "até 2019", np.where(t.data.dt.year == 2020, "2020", np.where(t.data.dt.year == 2021, "2021", "2022+")))
t["longo"] = t.tram > 3
print("Unidades:", len(t), "sem autuação:", int(t.autuacao.isna().sum()))
g = t.groupby("per").agg(n=("longo", "size"), longos=("longo", "sum"), mediana=("tram", "median"))
print(g)
x, y = t[t.per == "2020"], t[t.per != "2020"]
tab = [[int(x.longo.sum()), len(x) - int(x.longo.sum())], [int(y.longo.sum()), len(y) - int(y.longo.sum())]]
print("Fisher 2020 vs demais (>3 anos):", tab, "p unilateral =", round(fisher_exact(tab, alternative="greater")[1], 3), "bicaudal =", round(fisher_exact(tab)[1], 3))
print("Mann-Whitney unilateral, tramitação 2020 maior que demais, p =", round(mannwhitneyu(x.tram, y.tram, alternative="greater").pvalue, 3))
print("Medianas de tramitação por desfecho:\n", t.groupby(["per", "y"]).tram.median().unstack().round(2))
print("Negativas julgadas em até 6 meses da autuação:\n", t[t.y == 0].assign(r=lambda d: d.tram <= 0.5).groupby("per").r.agg(["sum", "size"]))
print("Casos longos de 2020:", sorted(x[x.longo].Rcl.tolist()))


def ps_p(df, col):
    # Mann-Whitney exato (mesma lógica de series_7_1_1.py), datando pela coluna indicada
    r2 = np.rint(2 * df[col].rank(method="average").values).astype(int); yy = df.y.values
    n1 = int(yy.sum()); n0 = len(yy) - n1; S = r2.sum(); dp = np.zeros((n1 + 1, S + 1)); dp[0, 0] = 1.0
    for v in r2:
        for j in range(n1, 0, -1):
            dp[j, v:] += dp[j - 1, :S + 1 - v]
    dist = dp[n1] / dp[n1].sum(); W = r2[yy == 1].sum()
    return (W / 2 - n1 * (n1 + 1) / 2) / (n1 * n0), dist[W:].sum()


for col in ["data", "autuacao"]:
    ps, p = ps_p(t, col)
    print(f"Teste principal datado por {col}: PS {ps:.3f}, p unilateral {p:.3f}")

# O controle negativo (7.4.1) datado pela autuação está em scripts_cap7_recuperados/saidas/saida_controle_negativo_autuacao.txt (PS 0,861; p 0,0037)
