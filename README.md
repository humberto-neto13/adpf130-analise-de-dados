# adpf130-monografia

Material de replicação do Trabalho de Conclusão de Curso de Humberto Guimarães Souto Neto, *Uma aplicação extraordinária da teoria da transcendência dos motivos? Estudo acerca do cabimento de reclamação por descumprimento do paradigma da ADPF nº 130*, apresentado à Faculdade de Direito da Universidade de Brasília (FD-UnB) em 2026, sob orientação do Prof. Dr. Juliano Zaiden Benvindo.

Este repositório documenta a pesquisa de forma integral. Reúne, por procedimento, os scripts, os prompts, o manual de codificação, as saídas do modelo, as planilhas de verificação humana e o código das análises, conforme anunciado nas notas 36, 40, 41, 42, 45, 47 e 49 da monografia.

## Comece por aqui

| Se você quer | Abra |
|---|---|
| Ver os dados finais da pesquisa | [`apendices/E_analises/matriz_consolidada_v3.xlsx`](apendices/E_analises/matriz_consolidada_v3.xlsx). Aba `Unidades`: uma linha por reclamação (133). Aba `Matriz`: uma linha por acórdão (137) |
| Ver o código das análises estatísticas | [`apendices/E_analises/`](apendices/E_analises/). Os capítulos 5 e 6 estão em `scripts_cap5_6/` e `testes.py`, e o capítulo 7 em `scripts_cap7_recuperados/` e nos demais `.py` da pasta |
| Encontrar de onde sai uma tabela ou figura da monografia | A seção "Mapa por tabela e figura", abaixo |
| Ver o prompt e o manual de codificação dados ao modelo | [`apendices/B_piloto_calibracao/manual/`](apendices/B_piloto_calibracao/manual/) e [`apendices/D_codificacao/`](apendices/D_codificacao/) |
| Ver como a codificação do modelo foi verificada | [`apendices/D_codificacao/dados/verificacao_humana/`](apendices/D_codificacao/dados/verificacao_humana/) |

Para abrir um arquivo no GitHub, clique no nome dele. Os `.xlsx` e os `.csv` podem ser baixados pelo botão de download no canto superior direito da página do arquivo. Não é preciso instalar nada para consultar o material, e só é preciso Python para reexecutar as análises.

## Sobre a pesquisa

Estudo empírico-dogmático da jurisprudência do Supremo Tribunal Federal em reclamações constitucionais que invocam a ADPF 130 como paradigma. A pesquisa investiga se houve flexibilização do requisito de aderência estrita ao longo do tempo e se essa flexibilização corresponde a uma aplicação extraordinária da transcendência dos motivos determinantes.

O universo bruto compreende 142 acórdãos colegiados exaurientes, referentes a 137 reclamações. Após o filtro de pertinência e a verificação humana, a população analisada compreende 133 reclamações (137 acórdãos). A coleta foi encerrada em 17/08/2026.

## Estrutura do repositório

```
apendices/
├── A_filtro_pertinencia/      # nota 40 e 41. Filtro de pertinência (Claude Opus 5) e verificação humana
├── B_piloto_calibracao/       # nota 42. Piloto de calibração e manual de codificação (v3)
├── C_piloto_estratificacao/   # nota 45. Piloto do desenho de oito estratos, abandonado
├── D_codificacao/             # nota 47. Codificação integral, verificação humana e matriz de dados
└── E_analises/                # nota 49. Matriz consolidada e código das análises dos capítulos 5 a 7
docs/
└── esboco_apendices_A_B_C.pdf # esboço em PDF a partir do qual os quadros de A, B e C foram recuperados
```

Cada pasta traz um `README.md` com o conteúdo, as pendências e as inconsistências conhecidas. A ordem alfabética dos apêndices não é a ordem cronológica de execução. O piloto de estratificação (C, Fase 1) antecede o piloto de calibração (B, Fase 2), e ambos antecedem a codificação integral (D).

## Mapa por tabela e figura

A numeração segue a versão final da monografia, com tabelas e figuras numeradas em sequência. Os scripts, as saídas e os registros do repositório foram escritos com a numeração de versões anteriores, indicada na coluna "Numeração anterior". Por exemplo, o script `tabela15_corte_aberta.py` gera a atual Tabela 14.

| Monografia | Origem | Numeração anterior |
|---|---|---|
| Figura 1 (árvore de decisão do filtro) | `apendices/A_filtro_pertinencia/prompt_sistema.txt` (a árvore está descrita no prompt) | |
| Quadro 3 (síntese das variáveis) | `apendices/B_piloto_calibracao/manual/manual_codificacao_v3.md` | |
| Tabela 1 (unidades por ano e estrato) | `apendices/E_analises/scripts_cap5_6/01_tabelas_descritivas.py` | Tabela 1 |
| Tabelas 2, 3, 4 e Figura 2 (verificação humana) | Calculadas diretamente da planilha `apendices/D_codificacao/dados/verificacao_humana/verificacao_codificacao_v3.xlsx`. Não há script próprio depositado | Figura 3 |
| Tabela 5 (frequência das classes das V1, V2, V4 e V5) | `scripts_cap5_6/01_tabelas_descritivas.py` | Tabela 3 |
| Tabelas 6, 7 e 8 (demais variáveis) | `scripts_cap5_6/01_tabelas_descritivas.py` (abas `Contagens univariadas` e `Tabela 4` da saída). A Variável 12 (votos vencidos) não está nessa saída | |
| Tabela 9 (V13 por estrato) | `scripts_cap5_6/01_tabelas_descritivas.py` | Tabela 5 |
| Tabela 10 e Figuras 3 e 4 (proporção anual com Wilson) | `scripts_cap5_6/01_tabelas_descritivas.py`, `figuras.py` e `scripts_cap5_6/03_figuras.py` | Tabela 6; Figuras 4 e 5 (nos scripts, Figura 3) |
| Tabela 11 (escala de Fisher) | Reprodução de tabela de livro (Fisher, 1954 apud Morettin e Bussab, 2010). Não há cálculo | |
| Tabela 12 (síntese da etapa confirmatória) | `testes.py` e `scripts_cap5_6/02_analise_confirmatoria.py` | Tabela 7 |
| Figura 5 (controle prévio, caso a caso) | `figuras.py` e `scripts_cap5_6/03_figuras.py` | Figura 6 (em `figuras.py`) e Figura 4 (em `03_figuras.py`) |
| Tabela 13 (sensibilidade sem 2020 e 2021) | `apendices/E_analises/sensibilidade_e_ligacao_cap7.py` | |
| Tabela 14 e Figura 6 (agravos, virtualização e taxa de provimento) | `apendices/E_analises/tabela15_corte_aberta.py` e `figura7_colegiadas_provimento.py` | Tabela 15 e Figura 7 |
| Tabelas 15 e 16 (Mann-Whitney estratificado) | `apendices/E_analises/scripts_cap7_recuperados/testes/strat.py` (Tabela 15), `bloco_cmd15_a.py` e `org.py` (Tabela 16) | Tabelas 16 e 18 |
| Tabela 17 (voto do relator por cadeira) | `scripts_cap7_recuperados/testes/bloco_cmd17_c.py` | Tabela 19 |
| Tabela 18 (controle negativo) | `scripts_cap7_recuperados/testes/controle_negativo_imune.py` | Tabela 21 |
| Figuras 7, 8 e 9 (rede de remissões) | `apendices/E_analises/figuras_V16_8_10.py` | Figuras 8, 9 e 10 |
| Tabela 19 (ligação dos reconhecimentos posteriores a 2023) | `apendices/E_analises/sensibilidade_e_ligacao_cap7.py` | Tabela 24 |

Os scripts de `scripts_cap7_recuperados/` são originais do autor recuperados de conversas anteriores. Os demais scripts do capítulo 7 são reconstruções escritas neste repositório e conferidas contra os números da monografia. Cada `README.md` das pastas indica o que é original e o que é reconstrução.

## Mapa entre a monografia e as pastas


| Monografia | Promessa | Pasta |
|---|---|---|
| Cap. 4 (abertura) e nota 36 | Todos os procedimentos com modelo de linguagem, e a matriz consolidada | A, B, C, D, E |
| Subseção 4.2.3, nota 40 | Instrução padronizada, prompt e registro integral das classificações do filtro | A |
| Subseção 4.2.3, nota 41 | Cotejo entre a classificação da IA e a verificação humana | A |
| Subseção 4.4.1, nota 42 | Piloto, material de submissão, padrões de discordância e manual final | B |
| Subseção 4.5.1, nota 45 | Piloto de estratificação e diagnóstico de massa insuficiente | C |
| Seção 5.2, nota 47 | Protocolo de codificação, resultados do modelo e planilha de verificação | D |
| Subseção 6.1.2.1, nota 49 | Código das análises, matriz consolidada, dados das figuras e registros de execução | E |

## Requisitos

- Python 3.13 (versão da reexecução)
- Bibliotecas listadas em `requirements.txt` (`anthropic`, `pandas` e `openpyxl` vêm do original do autor; `pypdf` e `numpy` foram acrescentadas a partir dos imports)
- Chave de API da Anthropic (`ANTHROPIC_API_KEY`). Nenhum passo usa a Voyage AI ou embeddings

As chaves devem ser definidas como variáveis de ambiente (`ANTHROPIC_API_KEY`) e nunca escritas no código.

## Como reproduzir

A sequência abaixo reproduz a pesquisa do filtro até as análises. Quem quer apenas conferir os números pode partir direto do passo 4, com a matriz consolidada, sem usar a API.

1. Filtro de pertinência (`apendices/A_filtro_pertinencia/filtro_pertinencia.py`).
2. Codificação integral com o manual v3 (`apendices/D_codificacao/`).
3. Conferência humana (planilha em `apendices/D_codificacao/`) e agregação em 133 reclamações.
4. Análises (`apendices/E_analises/`). Com a matriz e as versões de `apendices/E_analises/requirements.txt`, execute `python testes.py` e `python figuras.py` de dentro da pasta.

Os pilotos (B e C) estão preservados como registro e não precisam ser reexecutados.

## Nota sobre a codificação assistida por IA

O filtro de pertinência foi executado com o modelo Claude Opus 5 (Anthropic), e a codificação, com o Claude Sonnet 5, por requisições independentes à API, com prompt caching e ordem de submissão aleatorizada. Modelos de linguagem não produzem respostas idênticas a cada execução, de modo que uma nova rodada pode gerar resultados ligeiramente diferentes. Por isso, as respostas brutas obtidas na pesquisa estão preservadas neste repositório, e são elas que fundamentam as análises do trabalho.

O filtro foi conferido pelo pesquisador em todos os acórdãos classificados como não pertinentes e nos três de Passo 3 (Apêndice A), e a codificação foi verificada integralmente (Apêndice D). Em divergência, prevaleceu a codificação do pesquisador.

## Como citar

SOUTO NETO, Humberto Guimarães. *Uma aplicação extraordinária da teoria da transcendência dos motivos? Estudo acerca do cabimento de reclamação por descumprimento do paradigma da ADPF nº 130*. 2026. Trabalho de Conclusão de Curso (Bacharelado em Direito) – Faculdade de Direito, Universidade de Brasília, Brasília, 2026. Código e dados disponíveis em: https://github.com/humberto-neto13/adpf130-monografia.

## Licença

Código distribuído sob a licença MIT.
