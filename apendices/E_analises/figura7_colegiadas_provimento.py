"""Figura 7 (provisória): decisões colegiadas por ano e taxa de provimento dos agravos (seção 7.1.2).

RECONSTRUÇÃO escrita neste repositório a partir da descrição da conversa "Hipóteses rivais para
padrão confirmatório" (claude.ai, 19/11/2026), onde a figura foi gerada a partir da base de decisões
do Corte Aberta filtrada para a classe Rcl (script original g20/g22/g23.py não conservado).
Definições (da conversa): decisões colegiadas = 'Indicador colegiado' COLEGIADA; agravo julgado =
decisão colegiada em recurso interno, provido (total ou parcialmente) ou não provido, sem os não
conhecidos; taxa de provimento = providos / (providos + não providos). Eixo esquerdo: número de
decisões colegiadas (0 a 5.500); eixo direito: taxa de provimento (0 a 40%); linha tracejada na
ER nº 53/2020 (18/03/2020).
ATENÇÃO: o arquivo de decisões depositado/enviado em 23/11/2026 não tem a classe Rcl. O script foi
testado apenas quanto à mecânica (com --classe ARE) e deve ser rodado sobre a exportação de
decisões da classe Rcl. Confira contra a tabela da seção 7.1.2 (2018: 635 agravos, 13,8%;
2019: 1.062, 4,8%; 2020: 1.647, 9,0%; 2021: 1.707, 13,4%; 2022: 1.363, 8,2%; 2023: 1.727, 6,0%).
Uso: python3 figura7_colegiadas_provimento.py decisoes.csv [--classe Rcl] [pasta_saida]
"""
import sys
import pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

args = [a for a in sys.argv[1:] if not a.startswith("--")]
classe = sys.argv[sys.argv.index("--classe") + 1] if "--classe" in sys.argv else "Rcl"
if "--classe" in sys.argv: args.remove(classe)
arq, out = args[0], (args[1] if len(args) > 1 else "saidas")
d = pd.read_csv(arq, dtype=str, keep_default_na=False, usecols=["Processo", "Indicador colegiado", "Ano da decisão", "Tipo decisão", "Andamento decisão"])
d = d[d.Processo.str.match(rf"^{classe} \d+$")].copy(); d["ano"] = d["Ano da decisão"].astype(int)
print(f"decisões na classe {classe}: {len(d)}")
col = d[d["Indicador colegiado"] == "COLEGIADA"]
andam = col["Andamento decisão"].str.lower()
rec = col[col["Tipo decisão"] == "Decisão em recurso interno"]; a = rec["Andamento decisão"].str.lower()
prov = rec[a.str.contains("provido") & ~a.str.contains("não provido|negado provimento|improvido")]
nao = rec[a.str.contains("não provido|negado provimento")]
t = pd.DataFrame({"colegiadas": col.groupby("ano").size(), "providos": prov.groupby("ano").size(), "nao_providos": nao.groupby("ano").size()}).fillna(0)
t["agravos"] = t.providos + t.nao_providos; t["taxa_provimento"] = 100 * t.providos / t.agravos
print(t.round(1).to_string())
t.to_csv(f"{out}/figura7_dados.csv")
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
