"""Etapa confirmatória (capítulo 6): Mann-Whitney exato e Pettitt no controle posterior.

Uso: py 02_analise_confirmatoria.py modelo_de_dados.xlsx
Reprodutível: semente fixa. Reproduz os valores das seções 6.3 e 6.4, da
Tabela 7 e das notas de rodapé (empates no Pettitt; Rcl 23.899; Rcl 9.068).
"""
import sys
import numpy as np
import pandas as pd
from comum import ler_unidades

SEED = 20261012
N_PERM = 10000
ARQ = sys.argv[1] if len(sys.argv) > 1 else 'modelo_de_dados.xlsx'
u = ler_unidades(ARQ)


def serie(df):
    t = df[df.V13_ADER != 'ND'].copy()
    t['y'] = (t.V13_ADER == 'reconhecida').astype(int)
    return t.sort_values(['data', 'Rcl']).reset_index(drop=True)


def mann_whitney_exato(datas, y):
    """Distribuição exata da soma de postos (postos médios nos empates).

    Devolve U, p unilateral (13-A mais recentes), p bilateral e
    probabilidade de superioridade U/(n1*n0).
    """
    y = np.asarray(y); n1 = int(y.sum()); n0 = len(y) - n1
    r2 = np.rint(2 * pd.Series(datas).rank(method='average').values).astype(int)
    S = r2.sum()
    dp = np.zeros((n1 + 1, S + 1)); dp[0, 0] = 1.0
    for v in r2:
        for j in range(n1, 0, -1):
            dp[j, v:] += dp[j - 1, :S + 1 - v]
    dist = dp[n1] / dp[n1].sum()
    W = r2[y == 1].sum()
    p_sup = dist[W:].sum(); p_inf = dist[:W + 1].sum()
    U = W / 2 - n1 * (n1 + 1) / 2
    return U, p_sup, min(1.0, 2 * min(p_sup, p_inf)), U / (n1 * n0)


def pettitt(x):
    """Estatística K de Pettitt e posição do ponto de mudança."""
    m = len(x); s = np.sign(x[None, :] - x[:, None])
    Ut = np.array([s[:k + 1, k + 1:].sum() for k in range(m - 1)])
    k = np.abs(Ut).argmax()
    return np.abs(Ut[k]), k, Ut[k]


def pettitt_rapido(x):
    """Mesmo K, por soma acumulada (série binária); usado nas 300 ordenações."""
    n = len(x); c = np.cumsum(x)[:-1]; k = np.arange(1, n)
    return np.abs(k * (x.sum() - c) - (n - k) * c).max()


# ================= controle posterior =================
t = serie(u[u.Estrato == 'controle posterior'])
y = t.y.values; n = len(y); n1 = int(y.sum())
print(f'Controle posterior: n={n}  13-A={n1}  13-B={n - n1}  proporção={n1 / n:.3f}')
print(f'Mediana das datas: 13-A {t.data[y == 1].median().date()} | 13-B {t.data[y == 0].median().date()}')

U, p_uni, p_bi, ps = mann_whitney_exato(t.data, y)
print(f'\nMann-Whitney exato: U={U:.1f}  p unilateral={p_uni:.4f}  p bilateral={p_bi:.4f}')
print(f'  probabilidade de superioridade={ps:.3f}  bisserial de postos={2 * ps - 1:.3f}')

K, kpos, Uk = pettitt(y)
rng = np.random.default_rng(SEED)
Ks = np.array([pettitt(rng.permutation(y))[0] for _ in range(N_PERM)])
p_pet = (np.sum(Ks >= K) + 1) / (N_PERM + 1)
p_aprox = min(1, 2 * np.exp(-6 * K ** 2 / (n ** 3 + n ** 2)))
print(f'\nPettitt: K={K:.0f}  posição={kpos + 1}  p permutação ({N_PERM})={p_pet:.4f}  p aproximado={p_aprox:.3f}')
print(f'  última antes: Rcl {t.Rcl[kpos]} ({t.data[kpos].date()}) | primeira depois: Rcl {t.Rcl[kpos + 1]} ({t.data[kpos + 1].date()})')
print(f'  proporção antes={y[:kpos + 1].mean():.3f} ({y[:kpos + 1].sum()}/{kpos + 1})'
      f'  depois={y[kpos + 1:].mean():.3f} ({y[kpos + 1:].sum()}/{n - kpos - 1})')

# ---- nota de rodapé: ordem arbitrária entre datas empatadas
emp = int(t.data.duplicated(keep=False).sum())
rng2 = np.random.default_rng(1)
res = []
for _ in range(300):
    o = t.assign(r=rng2.random(n)).sort_values(['data', 'r'])
    xo = o.y.values.astype(float)
    res.append((pettitt_rapido(xo), o.data.iloc[pettitt(xo)[1]]))
Kv = {k for k, _ in res}; Dv = {d for _, d in res}
print(f'\nEmpates: {emp} unidades com data repetida; 300 ordenações -> '
      f'K={[int(k) for k in sorted(Kv)]}, ponto={[str(d.date()) for d in Dv]}')

# ---- nota de rodapé: sensibilidade à Rcl 23.899 e à Rcl 9.068
def p_unilateral(df):
    return mann_whitney_exato(df.data, df.y)[1]

s1 = t.copy(); s1.loc[s1.Rcl == 23899, 'data'] = pd.Timestamp('2024-11-18')
s2 = t[t.Rcl != 23899]
s3 = t.copy(); s3.loc[s3.Rcl == 23899, 'y'] = 0
r9068 = u[u.Rcl == 9068].assign(y=0)
s4 = pd.concat([t, r9068[t.columns.intersection(r9068.columns)]], ignore_index=True)
print('\nSensibilidade (p unilateral do Mann-Whitney):')
print(f'  Rcl 23.899 com a data do 2º acórdão: {p_unilateral(s1):.4f}')
print(f'  Rcl 23.899 excluída:                 {p_unilateral(s2):.4f}')
print(f'  Rcl 23.899 recodificada como 13-B:   {p_unilateral(s3):.4f}')
print(f'  Rcl 9.068 incluída como posterior:   {p_unilateral(s4):.4f}')

# ================= controle prévio (só descritivo, seção 6.5) =================
pv = serie(u[u.Estrato == 'controle prévio'])
print(f'\nControle prévio: n={len(pv)}  13-A={pv.y.sum()}  13-B={len(pv) - pv.y.sum()}')
print(f'  13-A a partir de 2020: {int(pv[(pv.y == 1) & (pv.data.dt.year >= 2020)].shape[0])}')
print(pv[['Rcl', 'data', 'V3_MOM_REST', 'V13_ADER']].assign(data=pv.data.dt.date).to_string(index=False))
