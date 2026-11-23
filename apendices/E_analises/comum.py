"""RECONSTRUÇÃO de `comum.py` (o original do autor não foi localizado).

Fornece apenas `ler_unidades`, usada por 02_analise_confirmatoria.py. Lê a aba
"Unidades" da matriz consolidada, preservando o texto "NA", e devolve as colunas
`Rcl` (int), `data` (V9_DATA como data) e as variáveis codificadas.
"""
import pandas as pd


def ler_unidades(arq):
    u = pd.read_excel(arq, sheet_name="Unidades", dtype=str, keep_default_na=False)
    u["data"] = pd.to_datetime(u["V9_DATA"])
    u["Rcl"] = u["Reclamação"].astype(int)
    return u
