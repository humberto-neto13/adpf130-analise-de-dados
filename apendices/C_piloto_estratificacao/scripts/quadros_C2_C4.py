"""Reproduz os Quadros C.2 e C.4 a partir de piloto_fase1_cruzamento.xlsx (aba Dados).

Uso: python quadros_C2_C4.py piloto_fase1_cruzamento.xlsx
Escrito no repositório (não é o código original do autor). Parâmetros inferidos e conferidos
contra os quadros do esboço: início do período de análise em 30/04/2009 (data da ADPF 130),
fim em 06/08/2026 (última decisão), durações em anos de 365,25 dias, desequilíbrio numérico
= desvio-padrão amostral (ddof=1) das três proporções de acórdãos por período, razão de duração
= maior duração / menor duração, calculada sobre as durações arredondadas a uma casa. O quadro do
esboço lista só as combinações com razão de duração menor que 2,0, em ordem crescente de desequilíbrio.
"""
import sys
import numpy as np
import pandas as pd

ARQ = sys.argv[1] if len(sys.argv) > 1 else "piloto_fase1_cruzamento.xlsx"
INI, FIM = pd.Timestamp("2009-04-30"), pd.Timestamp("2026-08-06")

d = pd.read_excel(ARQ, sheet_name="Dados", header=2, dtype=str, keep_default_na=False)
d["dt"] = pd.to_datetime(d["data"], format="%d/%m/%Y")
N = len(d)


def periodos(a, b):
    n = [int((d.dt < a).sum()), int(((d.dt >= a) & (d.dt < b)).sum()), int((d.dt >= b).sum())]
    dur = [(a - INI).days / 365.25, (b - a).days / 365.25, (FIM - b).days / 365.25]
    return n, dur


# ---- Quadro C.4: malha de cortes semestrais (30/04 e 30/10)
cortes_I = [pd.Timestamp(f"{y}-{m}-30") for y in range(2014, 2018) for m in ("04", "10")]
cortes_II = [pd.Timestamp(f"{y}-{m}-30") for y in range(2020, 2023) for m in ("04", "10")]
linhas = []
for a in cortes_I:
    for b in cortes_II:
        n, dur = periodos(a, b)
        linhas.append(dict(corte_I_II=a.strftime("%d/%m/%Y"), corte_II_III=b.strftime("%d/%m/%Y"),
                           n_PI=n[0], n_PII=n[1], n_PIII=n[2],
                           dur_PI_anos=dur[0], dur_PII_anos=dur[1], dur_PIII_anos=dur[2],
                           desequilibrio_numerico=float(np.std(np.array(n) / N, ddof=1)),
                           razao_duracao_max_min=max(round(x, 1) for x in dur) / min(round(x, 1) for x in dur)))
m = pd.DataFrame(linhas).sort_values(["desequilibrio_numerico", "razao_duracao_max_min"]).reset_index(drop=True)
m = m[m.razao_duracao_max_min < 2.0].reset_index(drop=True)
m.round(3).to_csv("C4_reproduzido.csv", index=False)
print(f"C.4: {len(m)} combinações com razão de duração < 2,0 (de {len(cortes_I) * len(cortes_II)})")

# ---- Quadro C.2: estrato x período nos cortes deslocados (30/04/2016 e 30/04/2022)
A, B = pd.Timestamp("2016-04-30"), pd.Timestamp("2022-04-30")
d["per"] = np.where(d.dt < A, "I", np.where(d.dt < B, "II", "III"))
c2 = pd.crosstab(d["grupo (recalc)"], d["per"], margins=True, margins_name="Total")
c2.to_csv("C2_reproduzido.csv")
print(c2.to_string())
