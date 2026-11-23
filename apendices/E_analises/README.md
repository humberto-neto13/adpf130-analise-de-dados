# Apêndice E. Análises

Corresponde à nota 49 da monografia (subseção 6.1.2.1). Contém os scripts e a matriz da etapa confirmatória (seção 6.1). O resto das análises ainda não foi depositado.

## Conteúdo

| Arquivo | O que faz | Onde aparece na monografia |
|---|---|---|
| `matriz_consolidada_v3.xlsx` | Matriz consolidada. Aba `Matriz`: 137 acórdãos. Aba `Unidades`: 133 reclamações agregadas, com estrato. Abas `Registro de alterações` (75 normalizações de forma em relação à planilha de verificação) e `Notas` (origem, regras de agregação, regra de estrato) | Base de todas as análises |
| `testes.py` | Mann-Whitney exato (unilateral e bilateral), probabilidade de superioridade, Pettitt com p-valor por 10.000 permutações (semente 20261012), tabela anual com intervalos de Wilson | Subseções 6.1.1, 6.1.2.1, 6.1.2.2 e 6.1.2.3; Tabelas 10 e 12; notas 49, 50 e 52 |
| `figuras.py` | Gera as figuras a partir de `testes.py` | Figura 4 (`figura_controle_posterior.png`) e Figura 6 (`figura_controle_previo.png`) |
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

## O que não está nesta pasta

Segundo o autor, os scripts abaixo foram executados em outras sessões e precisam ser recuperados ou reconstruídos:

- [ ] Nota 51: repetição do Pettitt com 300 ordenações aleatórias dos empates de data.
- [ ] Figura 5 (proporção anual em barras).
- [ ] Capítulo 5: Tabelas 1 a 8 e Figura 3 (verificação humana e descrição da população).
- [ ] Seções 6.2 e 6.3: Tabela 13 (sensibilidade à exclusão de 2020 e de 2020–2021), código original da Figura 7 (a Tabela 15 foi reproduzida, ver acima), Tabela 16 (Mann-Whitney estratificado), Tabelas 18 a 21 (relator, cadeira, órgão, empresas jornalísticas), Figuras 8 a 10 e Tabela 24 (rede de citações da Variável 16).
- [ ] Datas de autuação das reclamações (Tabela 21 e datação por autuação). O arquivo do Corte Aberta depositado traz só a data das decisões, não a de autuação; indicar a fonte das datas de autuação.
- [ ] Classe processual de cada acórdão, extraída da planilha do filtro (A).
- [ ] Matriz de citações (Variável 16 invertida, subseção 6.3, nota 70), com a conferência do pesquisador.
- [ ] Registro da leitura dirigida dos acórdãos com menção à transcendência em votos distintos do condutor (subseção 4.5.2).
- [ ] Programa da etapa exploratória, com os critérios de veredito e data anterior aos cálculos.

## Observações sobre o arquivo do Corte Aberta

- A nota 56 e a referência bibliográfica falam em arquivo `.csv`; o arquivo depositado é `.xlsx`. Convém conferir a redação.
- Na aba de dados, a coluna `Número Único` está gravada como número de ponto flutuante (por exemplo `1.89e+18`), e perde precisão. Não é usada na Tabela 15.
- O arquivo tem 13,8 MB. Se for preciso reduzir o repositório, ele pode ser substituído por um CSV compactado.
