"""Figuras da etapa confirmatória, lidas diretamente do modelo de dados.

Uso: py figuras_modelo.py modelo_de_dados.xlsx
Gera figura_controle_posterior.png, figura_controle_previo.png e figura_geral.png na pasta atual.
"""
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

ARQ = sys.argv[1] if len(sys.argv) > 1 else 'modelo_de_dados.xlsx'

# ---- leitura (keep_default_na=False preserva "NA" como código)
m = pd.read_excel(ARQ, sheet_name='Modelo', dtype=str, keep_default_na=False)
m['Rcl'] = m['Reclamação'].astype(int)
m['Acórdão'] = m['Acórdão'].astype(int)
m['data'] = pd.to_datetime(m['V9_DATA'].str.slice(0, 10), errors='coerce')
falha = m['data'].isna()
if falha.any():  # datas gravadas como texto dd/mm/aaaa
    m.loc[falha, 'data'] = pd.to_datetime(m.loc[falha, 'V9_DATA'], format='%d/%m/%Y')

# ---- agregação em reclamações (seção 5.1)
# 45682 e 46059: prevalece o acórdão de mérito (2º); 9977 e 23899: prevalece o 1º
PREVALENTE = {9977: 1, 23899: 1, 45682: 2, 46059: 2}
u = m[[PREVALENTE.get(r, a) == a for r, a in zip(m.Rcl, m['Acórdão'])]].copy()
assert len(u) == u.Rcl.nunique() == 133, len(u)

# ---- estratos pela V3 (subseção 4.7.1)
ESTRATO = {'posterior': 'controle posterior',
           'anterior': 'controle prévio', 'anterior e posterior': 'controle prévio'}
u['Estrato'] = u.V3_MOM_REST.map(ESTRATO).fillna('ND')

plt.rcParams.update({'font.family': 'serif',
                     'font.serif': ['Times New Roman', 'Liberation Serif'],
                     'font.size': 11})
virgula = mticker.FuncFormatter(lambda v, _: f'{v:.1f}'.replace('.', ','))

# ---- Figura 3: controle posterior, proporção anual com intervalo de Wilson
t = u[(u.Estrato == 'controle posterior') & (u.V13_ADER != 'ND')].copy()
t['y'] = (t.V13_ADER == 'reconhecida').astype(int)
t['ano'] = t.data.dt.year

def wilson(k, n, z=1.959964):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h

a = t.groupby('ano').y.agg(n='count', k='sum').reset_index()
a['p'] = a.k / a.n
a['lo'], a['hi'] = zip(*[wilson(k, n) for k, n in zip(a.k, a.n)])

ini = int(u.data.dt.year.min())          # primeiro ano da população (2009)
fim = int(u.data.dt.year.max())
fig, ax = plt.subplots(figsize=(6.3, 3.6), dpi=300)
vazio = [y for y in range(ini, fim + 1) if y not in set(a.ano)]
if vazio:  # anos sem unidades no estrato, sombreados
    ax.axvspan(min(vazio) - 0.4, max(vazio) + 0.5, color='0.94', lw=0)
    ax.text((min(vazio) + max(vazio)) / 2, 0.5, 'sem unidades\nno estrato',
            ha='center', va='center', fontsize=8, color='0.35')
ax.errorbar(a.ano, a.p, yerr=[a.p - a.lo, a.hi - a.p], fmt='o', color='black',
            ecolor='0.55', capsize=3, ms=5, lw=1)
for _, r in a.iterrows():
    ax.annotate(f'n={int(r.n)}', (r.ano, r.hi), textcoords='offset points',
                xytext=(0, 4), ha='center', fontsize=8)
ax.axvline(2021.5, color='0.4', ls='--', lw=0.8)   # ponto candidato de Pettitt
ax.text(2021.55, 1.13, 'Pettitt', fontsize=8, color='0.3', va='top')
ax.set_xlim(ini - 0.5, fim + 0.5); ax.set_xticks(range(ini, fim + 1))
ax.tick_params(axis='x', labelsize=8, rotation=45)
ax.set_ylim(-0.05, 1.18); ax.yaxis.set_major_formatter(virgula)
ax.set_ylabel('Proporção de aderência reconhecida'); ax.set_xlabel('Ano do julgamento')
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout(); fig.savefig('figura_controle_posterior.png'); plt.close(fig)

# ---- Figura 4: controle prévio, caso a caso
p = u[u.Estrato == 'controle prévio'].sort_values(['data', 'Rcl'])
fig, ax = plt.subplots(figsize=(6.3, 2.2), dpi=300)
for _, r in p.iterrows():
    if r.V13_ADER == 'reconhecida':
        ax.plot(r.data, 1, 'o', color='black', ms=6)
    elif r.V13_ADER == 'não reconhecida':
        ax.plot(r.data, 0, 's', color='white', mec='black', ms=6)
ax.set_xlim(pd.Timestamp(f'{ini}-01-01'), pd.Timestamp(f'{fim}-12-31'))
ax.set_yticks([0, 1]); ax.set_yticklabels(['não reconhecida', 'reconhecida'])
ax.set_ylim(-0.6, 1.6)
ax.set_xlabel('Data do julgamento'); ax.spines[['top', 'right', 'left']].set_visible(False)
ax.grid(axis='x', color='0.9')
fig.tight_layout(); fig.savefig('figura_controle_previo.png'); plt.close(fig)

# ---- Figura geral: toda a população, proporção anual com intervalo de Wilson
g = u[u.V13_ADER != 'ND'].copy()
g['y'] = (g.V13_ADER == 'reconhecida').astype(int)
g['ano'] = g.data.dt.year
b = g.groupby('ano').y.agg(n='count', k='sum').reset_index()
b['p'] = b.k / b.n
b['lo'], b['hi'] = zip(*[wilson(k, n) for k, n in zip(b.k, b.n)])
fig, ax = plt.subplots(figsize=(6.3, 3.6), dpi=300)
for y in range(ini, fim + 1):  # anos sem nenhuma unidade
    if y not in set(b.ano):
        ax.axvspan(y - 0.5, y + 0.5, color='0.94', lw=0)
ax.errorbar(b.ano, b.p, yerr=[b.p - b.lo, b.hi - b.p], fmt='o', color='black',
            ecolor='0.55', capsize=3, ms=5, lw=1)
for _, r in b.iterrows():
    ax.annotate(f'n={int(r.n)}', (r.ano, r.hi), textcoords='offset points',
                xytext=(0, 4), ha='center', fontsize=8)
ax.set_xlim(ini - 0.5, fim + 0.5); ax.set_xticks(range(ini, fim + 1))
ax.tick_params(axis='x', labelsize=8, rotation=45)
ax.set_ylim(-0.05, 1.18); ax.yaxis.set_major_formatter(virgula)
ax.set_ylabel('Proporção de aderência reconhecida'); ax.set_xlabel('Ano do julgamento')
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout(); fig.savefig('figura_geral.png'); plt.close(fig)
print('População (V13 determinada):', len(g), '| reconhecidas:', g.y.sum())
print(b[['ano', 'n', 'k', 'p', 'lo', 'hi']].round(3).to_string(index=False))

# ---- conferência
print('Unidades por estrato:', u.Estrato.value_counts().to_dict())
print('Controle posterior (V13 determinada):', len(t), '| reconhecidas:', t.y.sum())
print(a[['ano', 'n', 'k', 'p', 'lo', 'hi']].round(3).to_string(index=False))
print('Controle prévio:', p.V13_ADER.value_counts().to_dict())
