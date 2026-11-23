"""Leitura do modelo de dados, agregação em reclamações e estratos.

Usado por 01_tabelas_descritivas.py e 02_analise_confirmatoria.py.
"""
import numpy as np
import pandas as pd

# Seção 5.1: acórdão prevalente nas reclamações com dois acórdãos.
# 45682 e 46059: prevalece o acórdão de mérito (2º), com a data dele.
# 9977 e 23899: o 2º acórdão não altera a aderência; prevalece o 1º.
PREVALENTE = {9977: 1, 23899: 1, 45682: 2, 46059: 2}

# Subseção 4.7.1: "anterior e posterior" vai para o controle prévio; ND fica fora.
ESTRATO = {'posterior': 'controle posterior',
           'anterior': 'controle prévio',
           'anterior e posterior': 'controle prévio'}


def ler_acordaos(arq):
    """Uma linha por acórdão (137). keep_default_na=False preserva o código NA."""
    m = pd.read_excel(arq, sheet_name='Modelo', dtype=str, keep_default_na=False)
    m['Rcl'] = m['Reclamação'].astype(int)
    m['Acórdão'] = m['Acórdão'].astype(int)
    m['data'] = pd.to_datetime(m['V9_DATA'].str.slice(0, 10), errors='coerce')
    falha = m['data'].isna()
    if falha.any():  # datas gravadas como texto dd/mm/aaaa
        m.loc[falha, 'data'] = pd.to_datetime(m.loc[falha, 'V9_DATA'], format='%d/%m/%Y')
    return m


def ler_unidades(arq):
    """Uma linha por reclamação (133), com estrato e ano."""
    m = ler_acordaos(arq)
    u = m[[PREVALENTE.get(r, a) == a for r, a in zip(m.Rcl, m['Acórdão'])]].copy()
    assert len(u) == u.Rcl.nunique() == 133, len(u)
    u['Estrato'] = u.V3_MOM_REST.map(ESTRATO).fillna('ND')
    u['ano'] = u.data.dt.year
    return u.reset_index(drop=True)


def wilson(k, n, z=1.959964):
    """Intervalo de confiança de Wilson a 95%."""
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(c - h, 0.0), min(c + h, 1.0)


def classes(serie):
    """Explode classes múltiplas ('b,e') em linhas, para contagem."""
    return serie.astype(str).str.split(',').explode().str.strip()
