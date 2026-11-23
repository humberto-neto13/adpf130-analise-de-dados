"""Tabelas e contagens do capítulo 5 e Tabela 6 do capítulo 6.

Uso: py 01_tabelas_descritivas.py modelo_de_dados.xlsx
Gera tabelas_capitulos_5_6.xlsx (uma aba por tabela) na pasta atual
e imprime no terminal as contagens citadas no texto.
"""
import sys
import pandas as pd
from comum import ler_unidades, wilson, classes

ARQ = sys.argv[1] if len(sys.argv) > 1 else 'modelo_de_dados.xlsx'
u = ler_unidades(ARQ)
N = len(u)
pct = lambda x: round(100 * x / N, 1)
abas = {}

# ---- Tabela 1: unidades por ano e estrato
t1 = pd.crosstab(u.ano, u.Estrato, margins=True, margins_name='Total')
t1 = t1[['controle prévio', 'controle posterior', 'ND', 'Total']]
abas['Tabela 1'] = t1

# ---- Tabela 3: frequência das classes das V1, V2, V4 e V5
linhas = []
for var in ['V1_FUND', 'V2_MOD_REST', 'V4_RECLTE', 'V5_MEIO']:
    s = classes(u[var]).value_counts()
    for k in sorted(s.index, key=lambda c: (c == 'ND', c)):
        linhas.append([var, k, int(s[k]), pct(s[k])])
    multi = int(u[var].astype(str).str.contains(',').sum())
    linhas.append([var, 'mais de uma classe', multi, pct(multi)])
abas['Tabela 3'] = pd.DataFrame(linhas, columns=['Variável', 'Classe', 'Unidades', '% das unidades'])

# ---- Tabela 4: V13 x V14
abas['Tabela 4'] = pd.crosstab(u.V13_ADER, u.V14_SEGUIM, margins=True, margins_name='Total')

# ---- Tabela 5: V13 por estrato
t5 = pd.crosstab(u.Estrato, u.V13_ADER, margins=True, margins_name='Total')
det = t5['reconhecida'] + t5['não reconhecida']
t5['% de 13-A (V13 determinada)'] = (100 * t5['reconhecida'] / det).round(1)
abas['Tabela 5'] = t5

# ---- Tabela 6: proporção anual de 13-A no controle posterior, com Wilson
t = u[(u.Estrato == 'controle posterior') & (u.V13_ADER != 'ND')].copy()
t['y'] = (t.V13_ADER == 'reconhecida').astype(int)
t6 = t.groupby('ano').y.agg(Unidades='count', **{'13-A': 'sum'})
t6['Proporção'] = (t6['13-A'] / t6.Unidades).round(2)
ic = [wilson(k, n) for k, n in zip(t6['13-A'], t6.Unidades)]
t6['IC 95% inf'] = [round(a, 2) for a, _ in ic]
t6['IC 95% sup'] = [round(b, 2) for _, b in ic]
abas['Tabela 6'] = t6

# ---- contagens univariadas citadas no texto (seções 5.1, 5.3 e 5.4)
uni = []
for var in ['V3_MOM_REST', 'V6_TRANSC', 'V7_DIVERG', 'V8_ORG', 'V10_REL',
            'V13_ADER', 'V14_SEGUIM', 'V15_MERITO']:
    alvo = classes(u[var]) if var in ('V6_TRANSC', 'V7_DIVERG') else u[var]
    for k, n in alvo.value_counts().items():
        uni.append([var, k, int(n), pct(n)])
uni.append(['V11_RED', 'redator distinto do relator', int(u.V11_RED.str.startswith('a').sum()), None])
uni.append(['V16_JURIS', 'cita ao menos um julgado', int((u.V16_JURIS != '(vazio)').sum()), None])
abas['Contagens univariadas'] = pd.DataFrame(uni, columns=['Variável', 'Classe', 'Unidades', '% das unidades'])

# ---- listas de casos citados nominalmente
abas['Casos citados'] = pd.concat([
    u[u.V13_ADER == 'ND'].assign(Motivo='V13 não determinável (fora do teste)'),
    u[u.Estrato == 'ND'].assign(Motivo='V3 não determinável (fora do teste)'),
    u[(u.V13_ADER == 'não reconhecida') & (u.V14_SEGUIM == 'dado')].assign(Motivo='seguimento dado sem aderência reconhecida'),
    u[u.V14_SEGUIM == 'prejudicada ou extinta'].assign(Motivo='reclamação prejudicada'),
    u[u.V8_ORG == 'a'].assign(Motivo='julgamento pelo Plenário'),
])[['Motivo', 'Rcl', 'data', 'V3_MOM_REST', 'V13_ADER', 'V14_SEGUIM', 'V15_MERITO']]

with pd.ExcelWriter('tabelas_capitulos_5_6.xlsx') as w:
    for nome, df in abas.items():
        df.to_excel(w, sheet_name=nome[:31])

print(f'Unidades: {N} | período: {u.data.min().date()} a {u.data.max().date()}')
for nome in ['Tabela 1', 'Tabela 4', 'Tabela 5', 'Tabela 6']:
    print(f'\n== {nome}\n{abas[nome].to_string()}')
print('\nGravado: tabelas_capitulos_5_6.xlsx')
