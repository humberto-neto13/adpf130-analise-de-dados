"""Figura 7: decisões colegiadas por ano e taxa de provimento dos agravos (subseção 6.2.1.1).

RECONSTRUÇÃO escrita neste repositório a partir da descrição da conversa "Hipóteses rivais para
padrão confirmatório" (claude.ai, 19/11/2026). Fonte: exportação do Corte Aberta com as decisões da
classe Rcl (colunas Processo, Data, Descrição, Subgrupo, Tipo Decisão), baixada em 23/11/2026.
Definições, conferidas contra a Tabela 15 da subseção 6.2.1.1: decisões colegiadas = 'Tipo Decisão'
COLEGIADA; agravos julgados = colegiadas com Subgrupo 'Decisão em recurso interno' e Descrição
iniciada por 'Agravo regimental' (provido, provido em parte, não provido e não conhecido); taxa de
provimento = (providos + providos em parte) / (providos + providos em parte + não providos), sem os
não conhecidos. Eixo esquerdo 0 a 5.500; eixo direito 0 a 40%; linha tracejada na ER nº 53/2020.
Conferência: 2018 a 2023 reproduzem exatamente 635, 1.062, 1.647, 1.707, 1.363 e 1.727 agravos e
taxas de 13,8%, 4,8%, 9,0%, 13,4%, 8,2% e 6,0%.
Uso: python3 figura7_colegiadas_provimento.py decisoes_rcl.csv [pasta_saida]
"""
import sys
import pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

arq = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else "saidas"
d = pd.read_csv(arq, dtype=str, keep_default_na=False)
d = d[(d.Data != "-") & (d["Tipo Decisão"] == "COLEGIADA")].copy(); d["ano"] = pd.to_datetime(d.Data.str[:10], format="%d/%m/%Y").dt.year
ag = d[(d.Subgrupo == "Decisão em recurso interno") & d.Descrição.str.lower().str.startswith("agravo regimental")]
dsc = ag.Descrição.str.lower()
t = pd.DataFrame({"colegiadas": d.groupby("ano").size(), "agravos": ag.groupby("ano").size(),
                  "providos": ag[dsc.str.contains("provido") & ~dsc.str.contains("não provido")].groupby("ano").size(),
                  "nao_providos": ag[dsc.str.contains("não provido")].groupby("ano").size()}).fillna(0)
t = t[t.index >= 2009]; t["taxa_provimento"] = 100 * t.providos / (t.providos + t.nao_providos)
print(t.round(1).to_string()); t.to_csv(f"{out}/figura7_dados.csv")
fig, ax = plt.subplots(figsize=(11, 5.5))
l1, = ax.plot(t.index, t.colegiadas, color="#3d6a94", marker="o", lw=2, label="Decisões colegiadas em reclamações (eixo esquerdo)")
ax.set_ylabel("Decisões colegiadas (nº)", fontsize=10); ax.set_ylim(0, 5500)
ax2 = ax.twinx(); l2, = ax2.plot(t.index, t.taxa_provimento, color="#b5451b", marker="s", lw=2, label="Taxa de provimento dos agravos (%) (eixo direito)")
ax2.set_ylabel("Taxa de provimento dos agravos (%)", fontsize=10); ax2.set_ylim(0, 40)
ax.axvline(2019.5, color="#777777", ls="--", lw=1); ax.text(2019.6, 5350, "ER nº 53/2020", fontsize=8.5, color="#555555", va="top")
ax.set_xticks(t.index); ax.set_xticklabels([str(int(y)) for y in t.index], fontsize=8.5); ax.grid(axis="y", color="#eeeeee", lw=0.8)
for x in (ax, ax2): x.spines["top"].set_visible(False)
ax.legend(handles=[l1, l2], loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2, fontsize=8.5, frameon=False); plt.tight_layout()
for e in ("png", "pdf"): plt.savefig(f"{out}/colegiadas_e_taxa_de_provimento.{e}", dpi=300, bbox_inches="tight")
