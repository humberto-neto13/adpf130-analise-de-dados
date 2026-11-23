# Apêndice E. Análises

Corresponde à nota 49 da monografia (subseção 6.1.2.1). Contém os scripts e a matriz da etapa confirmatória (seção 6.1). O resto das análises ainda não foi depositado.

## Conteúdo

| Arquivo | O que faz | Onde aparece na monografia |
|---|---|---|
| `matriz_consolidada_v3.xlsx` | Matriz consolidada. Aba `Matriz`: 137 acórdãos. Aba `Unidades`: 133 reclamações agregadas, com estrato. Abas `Registro de alterações` (75 normalizações de forma em relação à planilha de verificação) e `Notas` (origem, regras de agregação, regra de estrato) | Base de todas as análises |
| `testes.py` | Mann-Whitney exato (unilateral e bilateral), probabilidade de superioridade, Pettitt com p-valor por 10.000 permutações (semente 20261012), tabela anual com intervalos de Wilson | Subseções 6.1.1, 6.1.2.1, 6.1.2.2 e 6.1.2.3; Tabelas 10 e 12; notas 49, 50 e 52 |
| `figuras.py` | Gera as figuras a partir de `testes.py` | Figura 4 (`figura_controle_posterior.png`) e Figura 6 (`figura_controle_previo.png`) |
| `registro_testes.txt` | Saída de `testes.py` na reexecução de 23/11/2026 | Confere com os valores reportados |
| `requirements.txt` | Versões das bibliotecas da reexecução (Python 3.13) | Nota 49 |

`figuras.py` também grava cinco figuras que não entraram no texto (degrau, logística, bienais e censo geral). A curva logística exige `statsmodels`.

## Como executar

Com os arquivos na mesma pasta: `py -m pip install -r requirements.txt`, `py testes.py` e `py figuras.py`.

## Conferência feita neste repositório

- `testes.py` foi reexecutado com `matriz_consolidada_v3.xlsx` e as versões de `requirements.txt` (numpy 2.5.3, pandas 3.0.5, openpyxl 3.1.5). A saída coincide linha a linha com `registro_testes.txt`.
- Os valores do estrato de controle posterior conferem com a Tabela 7 do capítulo 6: 94 unidades (38 / 56), U = 1.304,5, p unilateral 0,032, p bilateral 0,064, probabilidade de superioridade 0,61, Pettitt K = 562 com p = 0,068, ponto candidato entre 26/11/2021 e 18/02/2022, proporções de 11/42 antes e 27/52 depois.
- A aba `Matriz` é idêntica a `../D_codificacao/dados/matriz/modelo_de_dados.xlsx`, e o estrato resulta em 96 unidades de controle posterior, 20 de controle prévio e 17 fora do teste.
- `figuras.py` gerou a Figura 4 e a versão com degrau; a versão logística não rodou aqui por falta de `statsmodels`.

## O que não está nesta pasta

Segundo o autor, os scripts abaixo foram executados em outras sessões e precisam ser recuperados ou reconstruídos:

- [ ] Nota 51: repetição do Pettitt com 300 ordenações aleatórias dos empates de data.
- [ ] Figura 5 (proporção anual em barras).
- [ ] Capítulo 5: Tabelas 1 a 8 e Figura 3 (verificação humana e descrição da população).
- [ ] Seções 6.2 e 6.3: Tabela 13 (sensibilidade à exclusão de 2020 e de 2020–2021), Tabela 15 e Figura 7 (painel Corte Aberta), Tabela 16 (Mann-Whitney estratificado), Tabelas 18 a 21 (relator, cadeira, órgão, empresas jornalísticas), Figuras 8 a 10 e Tabela 24 (rede de citações da Variável 16).
- [ ] Dados externos da etapa exploratória, com fonte, critério de coleta e período (subseção 4.5.2): CSV do painel Corte Aberta (nota 56, consulta em 27/10/2026) e datas de autuação da Tabela 21.
- [ ] Classe processual de cada acórdão, extraída da planilha do filtro (A).
- [ ] Matriz de citações (Variável 16 invertida, subseção 6.3, nota 70), com a conferência do pesquisador.
- [ ] Registro da leitura dirigida dos acórdãos com menção à transcendência em votos distintos do condutor (subseção 4.5.2).
- [ ] Programa da etapa exploratória, com os critérios de veredito e data anterior aos cálculos.
