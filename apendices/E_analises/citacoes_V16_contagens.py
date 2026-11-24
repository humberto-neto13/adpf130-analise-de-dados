"""Contagens das citações internas da V16 (seção 6.3): rede de citações entre unidades da população.

RECONSTRUÇÃO escrita neste repositório. Os scripts originais dos Figuras 8 a 10 e das contagens
não foram conservados. Reproduz os números do texto da conversa "Hipóteses rivais para padrão
confirmatório" (claude.ai, 19/11/2026): citações internas por desfecho do acórdão citante e do
citado (diagrama de arcos) e a parcela de acórdãos de reconhecimento que citam a Rcl 22.328 por
período. Citantes: os 137 acórdãos; só menções a reclamações da população.
Uso: python3 citacoes_V16_contagens.py matriz_consolidada_v3.xlsx
"""
import re, sys
import pandas as pd

ARQ = sys.argv[1] if len(sys.argv) > 1 else "matriz_consolidada_v3.xlsx"
x = pd.ExcelFile(ARQ)
m = x.parse("Matriz", dtype=str, keep_default_na=False)
u = x.parse("Unidades", dtype=str, keep_default_na=False)
pop = set(u["Reclamação"].astype(int))
desfecho = dict(zip(u["Reclamação"].astype(int), u.V13_ADER))
m["Rcl"] = m["Reclamação"].astype(int)
m["data"] = pd.to_datetime(m.V9_DATA.str.slice(0, 10))
linhas = [(r.Rcl, r.V13_ADER, int(n), desfecho[int(n)])
          for r in m.itertuples() for n in re.findall(r"\bRcl[-\w]*\s*(\d+)", r.V16_JURIS) if int(n) in pop]
c = pd.DataFrame(linhas, columns=["citante", "v13_citante", "citado", "v13_citado"])
print(f"Citações internas: {len(c)}")
print(pd.crosstab(c.v13_citante, c.v13_citado, margins=True))
r = m[m.V13_ADER == "reconhecida"].copy()
r["cita"] = r.V16_JURIS.str.contains(r"\bRcl 22328\b")
r["periodo"] = r.data.map(lambda d: "até 2019" if d.year <= 2019 else "2020-2021" if d.year <= 2021 else "2022-2023" if d.year <= 2023 else "2024 em diante")
print("\nAcórdãos de reconhecimento que citam a Rcl 22.328, por período:")
print(r.groupby("periodo").cita.agg(["sum", "size"]).reindex(["até 2019", "2020-2021", "2022-2023", "2024 em diante"]))
