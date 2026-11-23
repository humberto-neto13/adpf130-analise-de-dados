# Apêndice D. Codificação integral

Corresponde à nota 47 da monografia (seção 5.2). Documenta a rodada completa de codificação dos 137 acórdãos com o manual v3.

## Conteúdo

- `scripts/submeter_batch_v3.py`: gera as requisições e as submete à Batch API. Modelo `claude-sonnet-5`, `max_tokens` 32000, semente 42 para a ordem aleatória, prompt de sistema (instruções gerais, manual v3 e formato de saída) com prompt caching. As requisições não passam `temperature`.
- `scripts/processar_batch_v3.py`: recupera o lote, valida o formato das respostas, aplica verificações de consistência entre variáveis (os "alertas") e grava o CSV, o JSONL completo e o arquivo de alertas.
- `scripts/converter_pdfs.py`: converte os PDFs do inteiro teor em `.txt` (pypdf), com aviso de extração escassa que pode exigir OCR.
- `dados/entrada/lista_unidades_analise.csv`: **lista das 137 unidades de análise** (acórdãos) em vez dos PDFs, que não foram depositados por decisão do autor. Uma linha por acórdão, com o arquivo de texto correspondente, a reclamação, o número do acórdão, a data do julgamento (V9), o relator (V10), o órgão (V8), se o acórdão prevalece na unidade (133 "sim", 4 "não"), a regra de agregação e o estrato. Gerada a partir de `matriz_consolidada_v3.xlsx` (derivado). Não traz a classe processual nem a identificação do acórdão no portal do STF, que não constam da matriz.
- `dados/entrada/textos/`: os 137 textos submetidos (um `.txt` por acórdão; os quatro pares de reclamações com dois acórdãos aparecem como `9977.1`, `9977.2`, `23899.1`, `23899.2`, `45682.1`, `45682.2`, `46059.1`, `46059.2`).
- `dados/saidas_originais/`:
  - `requisicoes_batch_v3.jsonl.gz`: requisições exatamente como enviadas (23,3 MB descompactadas; a compactação preserva o conteúdo, sha256 do original `e318ecf0…8d6`).
  - `mapa_custom_id_v3.json`: metadados da rodada (modelo, `max_tokens`, semente, arquivo do manual), ordem de envio e relação `custom_id` → arquivo.
  - `batch_id_v3.txt`: `msgbatch_01TajHJmYShqCoz3VhdgwQ3r`.
  - `log_codificacao_v3.txt`: log do processamento.
  - `codificacao_v3.csv`, `codificacao_v3_completo.jsonl`, `alertas_v3.csv`: saída do modelo, sem alteração humana.

## Manual

O manual usado na rodada (`manual-codificacao-v3.md`) é idêntico byte a byte a `../B_piloto_calibracao/manual/manual_codificacao_v3.md` (sha256 `2132630410bbcd84…b71`), que permanece como cópia única no repositório.

## Resultado bruto da rodada

- 137 acórdãos codificados, 0 falhas, 0 sem resultado; `stop_reason` `end_turn` em todos.
- Tokens: 5.841.476 de entrada, 1.579.862 de saída, 4.065.192 lidos de cache, 186.192 de criação de cache.
- 11 acórdãos com alerta (12 alertas): 9 de consistência entre V2 e V3 (V3 = "posterior" com V2 combinando a hipótese g com outras), 1 de consistência entre V13 e V15 (91198), 2 de formato em V16 (16492, 43110). Ver `dados/saidas_originais/alertas_v3.csv`.

## Execução

Dentro de uma pasta com os scripts, o manual e `textos/`: `py submeter_batch_v3.py`, depois `py processar_batch_v3.py`, com `ANTHROPIC_API_KEY` definida. Os scripts usam caminhos relativos a essa pasta.

## Verificação humana

`dados/verificacao_humana/verificacao_codificacao_v3.xlsx` (original do autor). Abas: `Verificação` (2.192 itens: variável, arquivo, valor IA, alerta automático, situação, valor correto, categoria do erro, observação), `Resumo` (fórmulas por variável), `Dados IA (CSV original)` e `Listas`. Os valores da coluna "Valor IA" coincidem integralmente com `codificacao_v3.csv`.

Totais da planilha: 2.003 itens confirmados e 189 corrigidos (91,4%), em 97 dos 137 acórdãos. Por variável, ver `resumo_por_variavel_derivado.csv`; distribuição das categorias de erro em `categorias_erro_derivado.csv`. Os dois CSV são derivados da planilha por contagem, sem outra intervenção.

Pontos de atenção:
- **Divergência entre a monografia e a planilha (seção 5.2).** O texto informa 2.000 confirmados e 192 corrigidos (91,2%) e, para a V15, 94,9%. A planilha dá 2.003 e 189 (91,4%) e, para a V15, 96,4% (5 correções). Recontada linha a linha na aba `Verificação`, a planilha é internamente consistente: 2.192 itens, 2.003 `Confirmado` e 189 `Corrigido`, com o mesmo total na aba `Resumo`. O valor 94,9% pertence à V8 (7 correções), e o texto o atribui à V15, o que indica troca na transcrição. A diferença de 3 correções no total (192 contra 189) não se explica por nenhuma variável isolada e sugere que o texto reflete uma contagem anterior da planilha. Os demais percentuais citados no texto conferem (V1 73,0%, V4 75,9%, V6, V9 a V12 acima de 98%, V13 93,4% e V14 95,6%). Decisão do autor: prevalece a planilha, e o texto deve ser corrigido para 2.003 confirmados, 189 corrigidos, 91,4% e V15 96,4%.
- **Tabela 2 da monografia (em branco).** Valores da planilha, com 137 codificações conferidas por variável: V1 37 alterações (27,0%), V2 23 (16,8%), V3 16 (11,7%), V4 33 (24,1%), V5 22 (16,1%), V6 2 (1,5%), V7 11 (8,0%), V13 9 (6,6%), V14 6 (4,4%) e V15 5 (3,6%). As variáveis omitidas da tabela (V8 a V12 e V16) somam 25 alterações, e as dez listadas somam 164.
- Das 189 correções, 102 têm categoria de erro preenchida e 87 não têm. A tipologia, portanto, cobre pouco mais da metade das correções (ver a observação da seção 5.2 sobre categorização "ainda incompleta").

## Agregação de 137 acórdãos em 133 reclamações

Operação manual, sem código, segundo o autor. Descreve-se aqui a regra tal como aplicada (seção 5.1 da monografia), conferida contra a codificação bruta. Quatro reclamações geraram dois acórdãos cada (arquivos `.1` e `.2` em `dados/entrada/textos/`):

| Reclamação | Acórdão 1 (data; V13/V14) | Acórdão 2 (data; V13/V14) | Registro mantido |
| --- | --- | --- | --- |
| Rcl 9.977 | 26/10/2017; não reconhecida / negado | 28/03/2019; ND / ND | Acórdão 1 (o segundo julgou embargos de declaração sem alterar o pronunciamento sobre a aderência) |
| Rcl 23.899 | 29/09/2023; reconhecida / dado | 18/11/2024; ND / ND | Acórdão 1 (idem) |
| Rcl 45.682 | 19/03/2021; ND / dado | 11/03/2022; reconhecida / dado | Acórdão 2, com a data do segundo julgamento (o primeiro apenas determinou o seguimento, sem julgar o mérito) |
| Rcl 46.059 | 26/04/2021; ND / dado | 08/03/2022; reconhecida / dado | Acórdão 2, idem |

As datas e os valores acima são os da codificação bruta do modelo, antes da verificação humana; a planilha de verificação pode tê-los corrigido. A aba `Unidades` de `../E_analises/matriz_consolidada_v3.xlsx` registra o acórdão prevalente de cada reclamação e o motivo. As regras gerais ali anotadas são: embargos de declaração x agravo regimental, prevalece o agravo, salvo embargos acolhidos com efeitos modificativos; embargos convertidos em agravo x embargos, prevalece o agravo, com a mesma ressalva; agravo provido apenas para dar seguimento x acórdão de mérito, prevalece o de mérito, com a data do julgamento do mérito.

## Matriz de dados

`dados/matriz/modelo_de_dados.xlsx` (original do autor, aba `Modelo`). Uma linha por acórdão (137), com as colunas Reclamação, Acórdão (1 ou 2) e Arquivo, seguidas das 16 variáveis já com as correções da verificação humana. Tem 133 reclamações distintas; a escolha do acórdão que representa cada uma das quatro reclamações duplas (seção anterior) não está marcada na planilha e se aplica sobre ela.

Conferência feita neste repositório:
- Contra a planilha de verificação: os valores finais (valor do modelo, ou valor correto quando corrigido) coincidem em todas as células, salvo diferenças de forma (caixa alta em nomes de ministros em V10 e V11, espaço depois da vírgula e ordem das letras em V2, V4 e V5, ponto e vírgula final em V16, e a data de 9428, que aparece em formatos distintos).
- Contra o capítulo 5 da monografia, após aplicar a regra de agregação (133 unidades, de 10/12/2009 a 05/08/2026): batem V13 (76 não reconhecidas, 53 reconhecidas, 4 ND), a Tabela 4 (V13 × V14), a Tabela 5 (V13 por estrato de V3: 96 posteriores, 20 prévias, 17 ND), V14 (67/63/2/1), V15 (49 procedentes, 16 improcedentes, 7 ND, 61 NA), V8 (64, 63 e 6), V7 (86 unânimes e 31 com voto vencido quanto ao seguimento), 16 unidades com redator distinto, 109 unidades com julgados citados (V16) e a distribuição por ano da Tabela 1 (24 até 2019, 25 em 2020, 109 de 2020 a 2026).
- A matriz consolidada usada nas análises, com a aba `Unidades` (uma linha por reclamação, 133) e o registro das normalizações de forma, está em `../E_analises/matriz_consolidada_v3.xlsx`. Sua aba `Matriz` é idêntica a `modelo_de_dados.xlsx`.

## Ressalva sobre o texto da Rcl 9.428

O arquivo `dados/entrada/textos/9428.txt` tem 852 bytes e contém apenas os títulos das seções (Ementa e Acórdão, Relatório, Voto), sem o corpo. A conversão do PDF falhou nesse acórdão: `9428.pdf` tem 112 páginas e é um documento digitalizado (imagem), do qual o `pypdf` extrai apenas 397 caracteres, os títulos das seções. O `converter_pdfs.py` avisa de extração escassa, que exige OCR. O modelo codificou, portanto, sem o inteiro teor, e 13 dos 16 itens dessa Rcl foram corrigidos na verificação humana. O mesmo vale para o piloto de estratificação (a justificativa do modelo para a Rcl 9.428 já registrava que só havia os títulos). Convém registrar isso no texto da monografia (seção 5.2) e, se possível, depositar o texto corrigido ou indicar que a verificação supriu a falha.

## A depositar

- ~~Tipologia de erros e critérios de atribuição de categoria~~ decisão do autor: os 87 erros sem categoria ficam registrados como **não classificados**. A tipologia cobre, portanto, 102 das 189 correções, e o texto da monografia deve dizê-lo (a observação da seção 5.2 já fala em categorização incompleta). Os critérios de atribuição das 102 categorias não estão documentados fora da planilha de verificação.
- ~~Uso de embeddings (Voyage AI)~~ não foram usados. Segundo o autor, a chave da Voyage AI vinha de uma ideia anterior de usar clustering (agrupamento por embeddings) para formar categorias, que não foi adotada. A menção ficou na primeira versão do README raiz (modelo com "Python [versão]" em branco), e nenhum script, saída ou texto da monografia usa embeddings. Retirada dos requisitos.
