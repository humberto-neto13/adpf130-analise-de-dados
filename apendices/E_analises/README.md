# Apêndice E. Análises

Corresponde à nota 49 da monografia (subseção 6.1.2.1). Contém os scripts e a matriz da etapa confirmatória (seção 6.1). O resto das análises ainda não foi depositado.

## Conteúdo

| Arquivo | O que faz | Onde aparece na monografia |
|---|---|---|
| `matriz_consolidada_v3.xlsx` | Matriz consolidada. Aba `Matriz`: 137 acórdãos. Aba `Unidades`: 133 reclamações agregadas, com estrato. Abas `Registro de alterações` (75 normalizações de forma em relação à planilha de verificação) e `Notas` (origem, regras de agregação, regra de estrato) | Base de todas as análises |
| `testes.py` | Mann-Whitney exato (unilateral e bilateral), probabilidade de superioridade, Pettitt com p-valor por 10.000 permutações (semente 20261012), tabela anual com intervalos de Wilson | Subseções 6.1.1, 6.1.2.1, 6.1.2.2 e 6.1.2.3; Tabelas 10 e 12; notas 49, 50 e 52 |
| `figuras.py` | Gera as figuras a partir de `testes.py` | Figura 4 (`figura_controle_posterior.png`) e Figura 6 (`figura_controle_previo.png`) |
| `scripts_cap5_6/` | **Originais do autor** (`LEIAME.txt`, `comum.py`, `01_tabelas_descritivas.py`, `02_analise_confirmatoria.py`, `03_figuras.py`). Leem a aba `Modelo` de `modelo_de_dados.xlsx` (cópia em `../D_codificacao/dados/matriz/`), agregam as 137 linhas em 133 reclamações e aplicam os estratos pela V3. Saídas da reexecução em `scripts_cap5_6/saidas/` | Capítulo 5 (Tabelas 1, 3, 4, 5), Tabela 6, Tabela 7, seções 6.3 a 6.5, notas 51 e de sensibilidade, Figuras 3 e 4 |
| `scripts_cap7_recuperados/` | **Originais do autor**, recuperados de conversas anteriores: testes da etapa exploratória por órgão, relator (com o voto do relator), cadeira, reclamante e meio, e sensibilidade sem 2020. Dados de entrada, saídas e README próprio | Capítulo 7 (seções 7.1 a 7.3) |
| `registro_testes.txt` | Saída de `testes.py` na reexecução de 23/11/2026 | Confere com os valores reportados |
| `dados_externos/corte_aberta/dados_publicos_rcl_corte_aberta.xlsx` | Exportação do painel Corte Aberta (transparencia.stf.jus.br), consulta de 27/10/2026. Aba 1: 157.276 decisões em reclamações (colunas Processo, Número Único, Descrição, Data, Origem, Observação, Subgrupo, Tipo Decisão). As demais abas são resumos com fórmulas feitos a partir dela | Tabela 15, Figura 7, nota 56 |
| `tabela15_corte_aberta.py` | Reproduz a Tabela 15 e a série anual da Figura 7 a partir do arquivo acima. **Escrito neste repositório**, não é o código original do autor | Tabela 15, Figura 7 |
| `registro_tabela15.txt` | Saída de `tabela15_corte_aberta.py` (2009 a 2026) | Confere com a Tabela 15 |
| `requirements.txt` | Versões das bibliotecas da reexecução (Python 3.13) | Nota 49 |

`figuras.py` também grava cinco figuras que não entraram no texto (degrau, logística, bienais e censo geral). A curva logística exige `statsmodels`.

## Como executar

Com os arquivos na mesma pasta: `py -m pip install -r requirements.txt`, `py testes.py` e `py figuras.py`.

## Conferência feita neste repositório

- `testes.py` foi reexecutado com `matriz_consolidada_v3.xlsx` e as versões de `requirements.txt` (numpy 2.5.3, pandas 3.0.5, openpyxl 3.1.5). A saída coincide linha a linha com `registro_testes.txt`.
- Os valores do estrato de controle posterior conferem com a Tabela 7 do capítulo 6: 94 unidades (38 / 56), U = 1.304,5, p unilateral 0,032, p bilateral 0,064, probabilidade de superioridade 0,61, Pettitt K = 562 com p = 0,068, ponto candidato entre 26/11/2021 e 18/02/2022, proporções de 11/42 antes e 27/52 depois.
- A aba `Matriz` é idêntica a `../D_codificacao/dados/matriz/modelo_de_dados.xlsx`, e o estrato resulta em 96 unidades de controle posterior, 20 de controle prévio e 17 fora do teste.
- A Tabela 15 foi reproduzida a partir do arquivo do Corte Aberta: agravos julgados (635, 1.062, 1.647, 1.707, 1.363 e 1.727 em 2018 a 2023), parcela de julgamentos virtuais (0,5%, 55,5%, 93,3%, 94,8%, 98,3% e 99,6%) e taxa de provimento (13,8%, 4,8%, 9,0%, 13,4%, 8,2% e 6,0%). Os critérios de contagem estão no cabeçalho do script. O texto de 6.2.1.1 também confere: crescimento de 55% em 2020 sobre 2019 e patamar superado a partir de 2024 (3.018 agravos).
- `figuras.py` gerou a Figura 4 e a versão com degrau; a versão logística não rodou aqui por falta de `statsmodels`.

- `01_tabelas_descritivas.py` reproduz a Tabela 1 (133 unidades: 20 de controle prévio, 96 de controle posterior, 17 ND), a Tabela 4 (V13 × V14), a Tabela 5 (13-A em 55,0% do controle prévio, 11/20, e 40,4% do posterior, 38/94) e a Tabela 6 (proporções anuais com Wilson, de 2014 a 2026). Os números conferem com os de `testes.py` e `matriz_consolidada_v3.xlsx`. A Tabela 3 e as contagens univariadas saem na planilha `tabelas_capitulos_5_6.xlsx`, e devem ser conferidas com o texto das seções 5.1, 5.3 e 5.4.
- A numeração das figuras difere entre os dois conjuntos de scripts: `03_figuras.py` rotula o controle posterior como Figura 3 e o prévio como Figura 4, enquanto `figuras.py` os grava como Figuras 4 e 6. O docstring de `03_figuras.py` o chama de `figuras_modelo.py`. Convém confirmar a numeração final na monografia.
- Os três scripts de `scripts_cap5_6/` foram executados com `modelo_de_dados.xlsx` (Python 3.13). `02_analise_confirmatoria.py` coincide com `testes.py` no controle posterior (U = 1.304,5; p unilateral 0,0320; p bilateral 0,0640; K = 562, p = 0,0680; 11/42 antes e 27/52 depois). As 300 ordenações dos empates (24 unidades com data repetida) produziram sempre K = 562 e o mesmo ponto de mudança (26/11/2021), o que sustenta a nota 51. Sensibilidade do p unilateral do Mann-Whitney: 0,0268 (Rcl 23.899 com a data do 2º acórdão), 0,0323 (excluída), 0,0331 (recodificada como 13-B) e 0,0243 (Rcl 9.068 incluída como posterior). Confira esses valores com as notas de rodapé do capítulo 6. O controle prévio lista 20 unidades (11 com adesão reconhecida, 10 delas a partir de 2020).

## O que não está nesta pasta

Segundo o autor, os scripts abaixo foram executados em outras sessões e precisam ser recuperados ou reconstruídos:

- [ ] Figura 5 (proporção anual em barras).
- [ ] Capítulo 5: Tabela 2 (verificação humana, que sai da planilha de verificação), Tabelas 7 e 8 (conferir se a 7 sai de `02_analise_confirmatoria.py`; a 8 não foi localizada). As Tabelas 1, 3, 4, 5 e 6 e as Figuras 3 e 4 saem dos scripts originais depositados.
- [ ] Capítulo 7 (etapa exploratória; as tabelas e figuras eram listadas aqui como das "seções 6.2 e 6.3", o que estava errado). Recuperados e depositados: testes por órgão, relator, cadeira, reclamante e meio e a sensibilidade aproximada (ver `scripts_cap7_recuperados/`). Faltam: `strat.py` e a Tabela 16 (Mann-Whitney estratificado por remoção × reclamante), a Tabela 13 exata (sensibilidade à exclusão de 2020 e de 2020–2021, só há a versão aproximada), o código original da Figura 7 (a Tabela 15 foi reproduzida, ver acima), as séries da seção 7.1.1, a tabela de empresas jornalísticas e meio clássico da seção 7.4, e a rede de citações da V16 (gráficos de citações por ano, citações acumuladas e diagrama de arcos, e o mapa remissivo).
- [ ] Datas de autuação das reclamações (Tabela 21 e datação por autuação). O arquivo do Corte Aberta depositado traz só a data das decisões, não a de autuação; indicar a fonte das datas de autuação.
- [ ] Classe processual de cada acórdão, extraída da planilha do filtro (A).
- [ ] Matriz de citações (Variável 16 invertida, subseção 6.3, nota 70), com a conferência do pesquisador.
- [ ] Registro da leitura dirigida dos acórdãos com menção à transcendência em votos distintos do condutor (subseção 4.5.2).
- [ ] Programa da etapa exploratória, com os critérios de veredito e data anterior aos cálculos.

## Observações sobre o arquivo do Corte Aberta

- A nota 56 e a referência bibliográfica falam em arquivo `.csv`, o gerado pelo painel. O arquivo depositado é uma conversão desse CSV para `.xlsx` feita pelo autor, com abas de resumo acrescentadas. O CSV original não foi localizado nesta pasta.
- Na aba de dados, a coluna `Número Único` está como número de ponto flutuante (por exemplo `1.89e+18`), com perda de precisão, provavelmente efeito da conversão. Não é usada na Tabela 15.
- O arquivo tem 13,8 MB. Se for preciso reduzir o repositório, ele pode ser substituído por um CSV compactado.
