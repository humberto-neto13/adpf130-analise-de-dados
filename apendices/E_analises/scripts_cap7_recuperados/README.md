# Scripts recuperados da etapa exploratória (capítulo 7)

Originais do autor, recuperados de conversas anteriores com o Claude e guardados na pasta `scripts_monografia` (de onde vieram, byte a byte). O `LEIA-ME_original.txt` é o texto que acompanhava a pasta. Não foram editados.

## Como executar

De dentro de `testes/`, com Python 3, pandas, numpy e scipy: `python3 org.py`, e assim por diante. Os scripts leem os arquivos de dados da própria pasta (`post.txt`, `relp.txt`, `v24.txt`, `v5.txt`). Os blocos `bloco_cmd*` executam o código de `org.py` até a linha `D={0:1.0}` e reaproveitam suas funções (`ustats` e `conv`).

## Conteúdo

| Arquivo | O que faz | Seção da monografia (numeração provisória) |
|---|---|---|
| `post.txt` | 94 unidades do controle posterior: Rcl, data, V13 (`R` reconhecida, `N` não) e órgão (V8) | Dados de entrada |
| `relp.txt` | Relator de cada uma das 94 unidades | Dados de entrada |
| `v24.txt` | V2 e V4 de cada unidade | Dados de entrada |
| `v5.txt` | V5 de cada unidade | Dados de entrada |
| `org.py` | Mann-Whitney exato por permutação, com postos médios, e estratificado por órgão (van Elteren, p por permutação exata) | 7.3 (rival 3, órgão julgador) |
| `bloco_cmd14_relator_vencidos.py` | Tabela por relator (n, 13-A, pares, probabilidade de superioridade) | 7.3 |
| `bloco_cmd15_a.py` | Estratificado por relator, com o voto do relator no lugar do desfecho. Cenário A: vencido no acórdão prevalente. Cenário B: também vencido no 1º acórdão das Rcl 45.682 e 46.059 | 7.3 |
| `bloco_cmd16_b.py` | Mesmo teste excluindo Moraes, Toffoli ou ambos | 7.3 |
| `bloco_cmd17_c.py` | Estratificado por cadeira (ministro aposentado e sucessor no mesmo estrato) e sensibilidades | 7.3 |
| `bloco_cmd22_reclamante_e_meio_estratificado.py` | Análise por reclamante (V4) e por meio (V5), com proporções até 2021 e de 2022 em diante | 7.2 (rival 2) |
| `strat.py` | **Reconstrução** (ver abaixo): estratos por remoção (V2), reclamante profissional (V4) e meio digital (V5), verificação prévia sem o desfecho e Mann-Whitney estratificado exato por pares, com p por permutação dentro dos estratos | 7.2 (rival 2) |
| `bloco_cmd02_reclamante_x_meio_fisher.py` | Cruzamento reclamante profissional × meio digital (Fisher). Depende de `strat.py` | 7.2 |
| `controle_negativo_imune.py` | **Reconstrução.** Mann-Whitney exato no subconjunto de empresas jornalísticas contra meios clássicos (24 unidades), controle negativo da rival 4 | 7.4.1 |
| `sensibilidade_sem_2020_aproximada.py` | Sensibilidade aproximada sem 2020 e sem 2020–2021, com a data trocada pelo ano | 7.1 (rival 1) |

## Conferência feita neste repositório

- Os dados de entrada conferem com `../matriz_consolidada_v3.xlsx` (aba `Unidades`): as 94 unidades do controle posterior com V13 determinada coincidem em Rcl, data, V13 e órgão; o relator coincide em todas (16 relatores, com as contagens por ministro iguais às de `V10_REL`); `v24.txt` traz a V2 e a V4, e `v5.txt` a V5, todas iguais às da matriz.
- Todos os scripts rodam. As saídas estão em `saidas/`. Valores principais: estratificado por órgão, PS 0,625, p 0,0217 (1.017 pares); por relator com o voto do relator, cenário A PS 0,71, p 0,0085 (131 pares), cenário B PS 0,735, p 0,0053 (113 pares), e sem 2020, p 0,0934 (A) e 0,0259 (B); por cadeira, PS 0,644, p 0,040 (160 pares); sem 2020, p 0,187; sem Toffoli, p 0,191. Sensibilidade aproximada: PS 0,609 e p 0,036 (todas as unidades), 0,562 e 0,18 (sem 2020), 0,536 e 0,305 (sem 2020 e 2021).
- `strat.py` foi reconstruído a partir do código que consta da conversa "Hipóteses rivais para padrão confirmatório" (claude.ai, 19/11/2026). O original lia o DataFrame de `/tmp/w/lag2.py`, não recuperado, e repetia o Passo 2 com a data de autuação (Corte Aberta), parte omitida aqui porque as datas de autuação não estão depositadas. A reconstrução reproduz os valores relatados na conversa: verificação prévia com probabilidade de superioridade das datas de 0,59 (remoção), 0,57 (reclamante profissional) e 0,56 (meio digital); estratificado por remoção, PS 0,575 e p 0,124; por reclamante, 0,655 e 0,010; por meio, 0,58 e 0,125; remoção × reclamante, 0,627 e p 0,037, com 539 pares. A tabela por estrato do cruzamento (37, 14, 4, 27, 11 e 1 unidades; pares 322, 45, 0, 162, 10 e 0; PS 0,58, 0,51, 0,75 e 0,80) coincide com a Tabela 10 do texto da seção 7.2 (numeração provisória). Os cruzamentos não previstos dão 0,579 (remoção × meio) e 0,565 (reclamante × meio). O Fisher de reclamante profissional × meio digital dá razão de chances 1,38 e p 0,75.
- `controle_negativo_imune.py` reproduz o valor relatado na conversa: 24 unidades, 18 com 13-A, 108 pares, PS 0,833 e p unilateral 0,007, com 6 de 11 até 2021 e 12 de 13 depois (com remoção, 6 em 6 nos dois períodos; sem remoção, 0 em 5 e 6 em 7). A repetição com a data de autuação (PS 0,86, p 0,004) não foi reproduzida, porque as datas de autuação não estão depositadas.
- O Mann-Whitney por ano do `sensibilidade_sem_2020_aproximada.py` dá p = 0,036, e o exato, com datas, dá 0,032 (capítulo 6). A diferença vem de a versão aproximada usar o ano como data. A versão exata dessa sensibilidade seria `org.py` aplicado sem as unidades de 2020 (e 2021), e não está depositada como script.
- Confira esses valores com as tabelas e o texto do capítulo 7, que não estão no projeto.

## O que não foi recuperado (segundo o autor)

Séries e fluxos de agravo do Corte Aberta (a Tabela de agravos 2018 a 2023 foi reproduzida em `../tabela15_corte_aberta.py`), o gráfico de colegiadas e taxa de provimento e as redes de citação da V16 (o mapa remissivo foi reconstruído em `../mapa_remissivo_V16.py`; o gráfico de citações por ano, o de citações acumuladas e o diagrama de arcos não). O teste por cadeira está em `bloco_cmd17_c.py`. Os scripts de `docx/` (geração de seções em Word com o pacote Node `docx`) não foram depositados: não fazem parte da análise.
