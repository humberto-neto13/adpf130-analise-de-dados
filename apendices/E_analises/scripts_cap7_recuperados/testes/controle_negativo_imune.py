"""Controle negativo da rival 4 (seção 7.4.1): Mann-Whitney exato no subconjunto imune à ressignificação.

RECONSTRUÇÃO escrita neste repositório, a partir da descrição da conversa "Hipóteses rivais
para padrão confirmatório" (claude.ai, 19/11/2026). Subconjunto: reclamações de empresa
jornalística (V4 classe a) contra restrições a meios clássicos (V5 só a, b ou c, sem ND), entre
as 94 unidades do controle posterior. Omite a repetição com a data de autuação, não depositada.
Uso (de dentro desta pasta): python3 controle_negativo_imune.py
"""
exec(open('strat.py').read().split("# passo 1")[0])
from scipy.stats import rankdata
def ustats(df):
    r = rankdata(df.dt.values.astype('int64')); x = (df.A == 1).values; m = int(x.sum()); k = len(x) - m
    r2 = (2 * r).astype(int); W2 = int(r2[x].sum())
    dp = [dict() for _ in range(m + 1)]; dp[0][0] = 1
    for v in r2:
        for j in range(m, 0, -1):
            for s, c in dp[j - 1].items(): dp[j][s + v] = dp[j].get(s + v, 0) + c
    tot = sum(dp[m].values()); return W2 - m * (m + 1), m * k, {s - m * (m + 1): c / tot for s, c in dp[m].items()}
emp = p.rcl.map(lambda r: 'a' in m4[r])
cls = p.rcl.map(lambda r: (set(m5[r]) <= {'a', 'b', 'c'}) and m5[r] != ['ND'])
s = p[emp & cls]
u2, pares, dist = ustats(s); pv = sum(v for k, v in dist.items() if k >= u2 - 1e-9)
print(f"Subconjunto imune: {len(s)} unidades, {int(s.A.sum())} com 13-A, {pares} pares, PS {u2 / 2 / pares:.3f}, p unilateral {pv:.3f}")
print(s.groupby('per').A.agg(['sum', 'size']))
print(s.groupby(['REM', 'per']).A.agg(['sum', 'size']))
