"""Mapa remissivo das menções a reclamações na Variável 16 (JURIS).

RECONSTRUÇÃO escrita neste repositório. O script original, que gerou `mapa_remissivo_V16.xlsx`
na conversa "Hipóteses rivais para padrão confirmatório" (claude.ai, 19/11/2026), não foi
conservado. As regras seguem as notas da planilha original: só se contam menções a reclamações
(Rcl); os citantes são os 137 acórdãos, inclusive os não prevalentes; a aba Remissivo tem uma
linha por unidade de análise (133), com data, V3 e V13 do acórdão prevalente; "citações
recebidas na população" conta só as feitas por acórdãos da população.

Uso: python3 mapa_remissivo_V16.py matriz_consolidada_v3.xlsx
Saída: mapa_remissivo_V16_reconstruido.xlsx (valores, sem fórmulas)
"""
import re, sys
import pandas as pd

ARQ = sys.argv[1] if len(sys.argv) > 1 else "matriz_consolidada_v3.xlsx"
m = pd.read_excel(ARQ, sheet_name="Matriz", dtype=str, keep_default_na=False)
u = pd.read_excel(ARQ, sheet_name="Unidades", dtype=str, keep_default_na=False)
m["Rcl"] = m["Reclamação"].astype(int)
u["Rcl"] = u["Reclamação"].astype(int)
u["data"] = pd.to_datetime(u["V9_DATA"].str.slice(0, 10))
m["data"] = pd.to_datetime(m["V9_DATA"].str.slice(0, 10))
pop = set(u.Rcl)
V13 = {"reconhecida": "13-A", "não reconhecida": "13-B", "ND": "ND"}

linhas = []
for _, r in m.iterrows():
    for n in re.findall(r"\bRcl[-\w]*\s*(\d+)", r.V16_JURIS):
        linhas.append(dict(citante=r.Rcl, acordao=int(r["Acórdão"]), data=r.data, v13_citante=V13[r.V13_ADER],
                           citado=int(n), citado_na_populacao="sim" if int(n) in pop else "não"))
c = pd.DataFrame(linhas).sort_values(["data", "citante"]).reset_index(drop=True)

interno = c[c.citado_na_populacao == "sim"]
rem = u[["Rcl", "data", "Estrato", "V13_ADER"]].copy()
rem["citacoes_recebidas_na_populacao"] = rem.Rcl.map(interno.citado.value_counts()).fillna(0).astype(int)
rem["citantes"] = rem.Rcl.map(lambda r: "; ".join(f"Rcl {x.citante} ({x.data:%d/%m/%Y}, {x.v13_citante})"
                                                    for x in interno[interno.citado == r].itertuples()))
rem = rem.sort_values("citacoes_recebidas_na_populacao", ascending=False)
ext = c[c.citado_na_populacao == "não"].groupby("citado").agg(
    citacoes=("citante", "size"), citado_por=("citante", lambda s: "; ".join(f"Rcl {x}" for x in s))
).sort_values("citacoes", ascending=False).reset_index()

with pd.ExcelWriter("mapa_remissivo_V16_reconstruido.xlsx") as w:
    rem.to_excel(w, "Remissivo", index=False)
    c.to_excel(w, "Citações", index=False)
    ext.to_excel(w, "Rcl externas", index=False)
print(f"menções a reclamações: {len(c)} | internas: {len(interno)} | unidades citadas: {interno.citado.nunique()} de {len(pop)}")
print("mais citadas na população:", interno.citado.value_counts().head(6).to_dict())
print("mais citadas fora da população:", ext.head(5).set_index("citado").citacoes.to_dict())
