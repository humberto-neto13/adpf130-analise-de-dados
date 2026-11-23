"""
Tabela 15 (e série da Figura 7): agravos julgados por órgãos colegiados em reclamações,
parcela de julgamentos virtuais e taxa de provimento, a partir do painel Corte Aberta.

Script escrito neste repositório para reproduzir a Tabela 15 a partir do arquivo depositado
(não é o código original do autor, que não foi localizado). Critérios, conforme a nota da
Tabela 15 e as abas de resumo do próprio arquivo:
- Decisão colegiada: coluna "Tipo Decisão" = COLEGIADA, ano da coluna "Data".
- Agravo julgado: "Descrição" começa com "Agravo regimental" (provido, provido em parte,
  não provido, não conhecido).
- Julgamento virtual: "Origem" contém "SESSÃO VIRTUAL", sobre o total de decisões colegiadas do ano.
- Taxa de provimento: (providos + providos em parte) / (providos + providos em parte + não providos).

Execução:  python tabela15_corte_aberta.py [caminho do .xlsx]
"""
import sys
from pathlib import Path
import pandas as pd

ARQ = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "dados_externos/corte_aberta/dados_publicos_rcl_corte_aberta.xlsx"

d = pd.read_excel(ARQ, sheet_name=0, dtype=str, keep_default_na=False)
d["ano"] = pd.to_datetime(d["Data"], format="%d/%m/%Y %H:%M:%S", errors="coerce").dt.year
c = d[d["Tipo Decisão"] == "COLEGIADA"]
ag = c[c["Descrição"].str.startswith("Agravo regimental")]
PROV = ["Agravo regimental provido", "Agravo regimental provido em parte"]
linhas = []
for ano in range(2009, 2027):
    x, cc = ag[ag["ano"] == ano], c[c["ano"] == ano]
    pr, npv = x["Descrição"].isin(PROV).sum(), (x["Descrição"] == "Agravo regimental não provido").sum()
    linhas.append({"Ano": ano, "Decisões colegiadas": len(cc), "Agravos julgados": len(x),
                   "% virtual (colegiadas)": round(100 * cc["Origem"].str.contains("SESSÃO VIRTUAL").mean(), 1) if len(cc) else None,
                   "Taxa de provimento (%)": round(100 * pr / (pr + npv), 1) if pr + npv else None})
t = pd.DataFrame(linhas)
print(t.to_string(index=False))
