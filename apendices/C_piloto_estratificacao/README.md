# Apêndice C. Piloto de estratificação (Fase 1)

Corresponde à nota 45 da monografia (subseção 4.5.1). Documenta o desenho **abandonado** de oito estratos (momento da restrição, meio e sujeito comunicativo), a codificação das Variáveis 3, 4 e 5 nos 137 acórdãos, sem acesso aos desfechos, e a escolha dos cortes temporais. A estratificação final é binária e usa só o momento da restrição.

> **Origem do material.** São originais do autor, idênticos byte a byte: `scripts/piloto_fase1.py`, `scripts/submeter_batch_sonnet.py`, `scripts/processar_batch_sonnet.py`, o texto de `prompt_sistema.txt` (extraído do primeiro), os logs e as requisições em `execucoes/` e as planilhas e o CSV em `dados/originais/`. Os quadros C.1 a C.4 em `dados/` vêm do PDF do esboço. O C.1 e o C.3 foram conferidos com os dados originais (ver abaixo).

Cronologicamente, a Fase 1 (este apêndice) antecede a Fase 2 (Apêndice B). A ordem alfabética dos apêndices não é a ordem de execução.

## Conteúdo

| Arquivo | O que é | Seção do esboço |
|---|---|---|
| `scripts/piloto_fase1.py` | Versão síncrona do piloto, com Claude Opus 5 e requisição por acórdão (original) | |
| `scripts/submeter_batch_sonnet.py` | Preparação e submissão à Batch API (Sonnet 5) | C.2.1 |
| `scripts/processar_batch_sonnet.py` | Download e consolidação dos resultados | C.2.2 |
| `prompt_sistema.txt` | Prompt de sistema da Fase 1 (Variáveis 3, 4 e 5) | C.2.3 |
| `dados/C3_1_sinoptica_codificacao.csv` | Classes atribuídas a cada um dos 137 acórdãos | C.3.1 |
| `dados/C3_2_justificativas.csv` | Justificativas textuais do modelo (131 acórdãos codificados, 3 variáveis) | C.3.2 |
| `dados/quadro_C1_distribuicao_bruta.csv` | Oito estratos, cortes originais (30/04/2015 e 30/04/2021) | C.5 |
| `dados/quadro_C2_cortes_deslocados.csv` | Oito estratos, cortes deslocados um ano | C.5 |
| `dados/quadro_C3_distribuicao_final.csv` | Seis grupos após agregação (G1+G4, G2+G6) | C.5 |
| `dados/quadro_C4_matriz_deslocamentos.csv` | 36 configurações com razão de duração menor que 2,0 (o esboço diz 81 avaliadas) | C.6 |
| `scripts/quadros_C2_C4.py` | Reproduz os Quadros C.2 e C.4 a partir de `dados/originais/piloto_fase1_cruzamento.xlsx`. **Escrito neste repositório**, não é código original do autor | C.5, C.6 |
| `dados/reproduzidos/C2_reproduzido.csv`, `C4_reproduzido.csv` e `execucoes/registro_quadros_C2_C4.txt` | Saídas do script acima | C.5, C.6 |
| `NOTAS.md` | Texto explicativo do esboço, incluindo regras de desempate e justificativa da agregação | C.1 a C.7 |

Os seis acórdãos não codificados por falha técnica (Rcl 9068, 9977 acórdão 1, 11305, 38782, 65925 e 83604) constam da tabela sinóptica como `ERRO`, e não de `C3_2_justificativas.csv`.

## README original da Fase 1

`docs/README_original_fase1.md` e `docs/requirements_original_fase1.txt` (originais do autor, da pasta `piloto`). O README descreve a Fase 1 como dois scripts, `converter_pdfs.py` e `piloto_fase1.py`, com o modelo `claude-opus-5`, chamadas síncronas independentes, semente 42, até três tentativas por acórdão, codificação de V3, V4 e V5, e saídas `piloto_fase1.csv` e `log_piloto_fase1.txt`. `piloto_fase1.py` e `converter_pdfs.py` da pasta são idênticos, byte a byte, aos depositados neste repositório. Nenhuma das saídas (`piloto_fase1.csv`, log) estava na pasta.

Observações a esclarecer:
- O README fala em Opus 5 síncrono, e o esboço do Apêndice C em Sonnet 5 via Batch API. Segundo o autor, o Opus 5 chegou a rodar em duas ou três codificações e foi abandonado por erros sistemáticos do script, e toda a classificação da Fase 1 provém do Sonnet 5 em lote (os scripts e as saídas estão depositados).
- O README lista cinco reclamações com mais de um acórdão exauriente, entre elas a Rcl 43.110 (Rcl-AgR de 27/04/2021 e Rcl-AgR-ED de 16/08/2022). Na população final há quatro (9.977, 23.899, 45.682 e 46.059), e a Rcl 43.110 tem um só acórdão. As datas do README também diferem das da codificação da população final (por exemplo, Rcl 23.899: 02/10/2023 no README, 29/09/2023 na codificação), compatível com a diferença entre a data do cabeçalho e a do Extrato de Ata.

## Planilhas originais da Fase 1

`dados/originais/` (originais do autor):
- `piloto_fase1_sonnet.xlsx` (aba `piloto_fase1_sonnet.csv`) e `piloto_fase1_sonnet_58-137.csv`: saída da execução com Sonnet 5, em duas partes, de **57** e **80** acórdãos, que somam os 137 sem repetição. A primeira parte tem as seguintes características. Colunas: classes e justificativas de V3, V4 e V5, contadores de tokens (2.230.106 de entrada, 45.221 de saída, 7.638 lidos de cache, 132.392 de criação de cache) e erro. Dois acórdãos falharam: 83604 ("Nenhum bloco de texto encontrado") e 9977.1 ("Erro ao extrair", JSON truncado).
- `piloto_fase1_cruzamento.xlsx`: abas `Cruzamento 8 grupos`, `Cruzamento agregado` (seis grupos), `Diagnóstico NC` e `Dados` (137 acórdãos, com data, período e grupo recalculado).

Conferência feita neste repositório:
- Os 137 acórdãos das duas partes do Sonnet têm classes idênticas, nas três variáveis, às da aba `Dados` e, por consequência, às do Quadro C.1. Toda a classificação da Fase 1 provém, portanto, da execução com Sonnet 5. Somadas as duas partes: 5.536.529 tokens de entrada, 97.088 de saída, 198.588 lidos de cache e 134.938 de criação de cache; 6 falhas (83604, 9068 e 11305 sem bloco de texto; 9977.1, 65925 e 38782 com JSON inválido), todas viradas NC no cruzamento. Em 129 dos 137 acórdãos, a aba `Dados` coincide com `C3_1_sinoptica_codificacao.csv` (os oito restantes não casam por diferença de rótulo, como "Rcl 9977 (acórdão 1)").
- `Cruzamento 8 grupos` coincide com o Quadro C.1 em todas as células (G1 6, G2 17, G3 7, G4 1, G5 37, G6 1, G7 11, G8 32 e NC 25; 137 acórdãos; Períodos I, II e III com 7, 48 e 82). Os períodos da aba `Dados` são: I de 10/12/2009 a 09/09/2014; II de 30/06/2015 a 27/04/2021; III de 21/06/2021 a 06/08/2026.
- `Cruzamento agregado` (seis grupos, com os cortes originais) dá G_prev_trad 7, G_post_trad 18, G3 7, G5 37, G7 11, G8 32 e NC 25. Esses valores diferem do Quadro C.3 (G_prev_trad 1/3/3, G_post_trad 3/8/7 etc.; Períodos 12, 56 e 69), que usa os cortes deslocados do Quadro C.2. As duas tabelas são, portanto, de cortes diferentes e não de erro.
- Os Quadros C.2 e C.4 foram reproduzidos com `scripts/quadros_C2_C4.py`, a partir da aba `Dados`. O C.2 (cortes de 30/04/2016 e 30/04/2022) coincide em todas as células. No C.4, as 36 combinações de cortes, as contagens por período, as durações e o desequilíbrio numérico coincidem integralmente. O desequilíbrio é o desvio-padrão amostral das três proporções de acórdãos por período, e as durações contam de 30/04/2009 (data do julgamento da ADPF 130) a 06/08/2026 (última decisão). A razão de duração coincide em 26 das 36 linhas, e nas outras 10 difere em 0,01 (arredondamento das durações). A ordem do quadro é a crescente de desequilíbrio. O quadro lista apenas combinações com razão **menor que** 2,0 (a combinação 30/04/2017 e 30/04/2021 tem razão exatamente 2,0 e não consta), e não "≤ 2,0" como diz a descrição. O script avalia 48 combinações (cortes semestrais de 2014 a 2017 e de 2020 a 2022). O esboço fala em 81 avaliadas, e a malha original não pôde ser recuperada. Todas as 36 combinações do quadro estão na malha reproduzida.
- `Diagnóstico NC` documenta a causa de cada um dos 25 casos não classificados: 6 por erro técnico (11305, 38782, 65925, 83604, 9068 e 9977.1), 9 só por meio ND (V5), 1 só por momento ND (48882), 5 por ND em todas as três variáveis (48589, 59320, 71380, 9428 e 9977.2), 1 só por sujeito ND (82228) e 3 por sujeito e meio ND (49816, 67543 e 93341). Isso fornece o registro do "diagnóstico de massa insuficiente" que a nota 45 invoca, em parte: a causa dos NC está documentada, mas a análise da massa insuficiente por grupo continua só no Quadro C.3.
- A Rcl 9.428 está entre os NC por ND em todas as variáveis, pela mesma falha de extração do texto digitalizado registrada no Apêndice D.

## Execução dos lotes (originais)

Os scripts `scripts/submeter_batch_sonnet.py` e `scripts/processar_batch_sonnet.py` foram substituídos pelos **originais do autor** (antes eram recuperações do PDF; coincidiam com eles, a menos de uma linha em branco final). `execucoes/log_piloto_fase1_sonnet_1-57.txt` e `execucoes/log_piloto_fase1_sonnet_58-137.txt` são os logs originais do processamento.

| Lote | Identificador | Hora do log | Requisições | Sucesso na extração | Tokens de entrada | Tokens de saída | Custo estimado (Batch, 50%) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `msgbatch_01SyG7Nmx6meoprCkFHGhRXj` | 09:04 | 57 | 55 | 2.230.106 | 45.221 | USD 3,93 |
| 2 | `msgbatch_01YMy7CJZRUCGrPwkGwCqW2g` | 09:41 | 80 | 76 | 3.306.423 | 51.867 | USD 5,38 |

Os dois lotes terminaram com todas as requisições bem-sucedidas na API (0 erros de lote). As seis falhas são de extração do JSON no `processar_batch_sonnet.py` (três sem bloco de texto e três com JSON inválido). Custo total estimado: USD 9,32. Os totais dos logs coincidem com os dos CSV (5.536.529 tokens de entrada e 97.088 de saída).

Observações:
- O script lê todos os `.txt` de `./textos` e embaralha com semente 42. Nada nele separa 57 de 80 arquivos. Segundo o autor, a primeira submissão precisou ser interrompida por causa de um erro, e por isso as submissões ficaram divididas em dois lotes (1–57 e 58–137).
- O `custom_id` troca o ponto por sublinhado (`9977_1`), e as requisições depositadas trazem `custom_id` sem sufixo para os acórdãos únicos.
- O script e o processador mencionam um `verificar_batch.py`, que o autor não conservou. O acompanhamento do lote não deixou script próprio, e o `processar_batch_sonnet.py` é o único que lida com o resultado.
- O processador estima o custo com preços unitários fixos no código (USD 3, 15, 3,75 e 0,30 por milhão de tokens, com 50% de desconto). Os valores em dólar acima são essas estimativas, não faturamento.

## Requisições do Batch (Sonnet 5)

`execucoes/requisicoes_batch_sonnet_1-57.jsonl.gz` e `execucoes/requisicoes_batch_sonnet_58-137.jsonl.gz` (originais do autor, compactados; o conteúdo descompactado é idêntico). São duas submissões à Batch API, de 57 e 80 requisições, que somam os 137 acórdãos sem repetição (`custom_id` = número do acórdão). Em todas: `claude-sonnet-5`, `max_tokens` 2048, sem `temperature` e sem `thinking`, e o mesmo prompt de sistema (6.265 caracteres). Esse prompt é igual, a menos de espaços e quebras de linha, ao `prompt_sistema.txt` extraído do `piloto_fase1.py` (Opus 5) e à constante `SYSTEM_PROMPT` de `scripts/submeter_batch_sonnet.py`. Portanto, as duas versões do script usam o mesmo prompt, e a diferença entre elas é o modelo e o modo de submissão.

Essas requisições confirmam que as classificações da Fase 1 vieram de **Sonnet 5 via Batch API**, como o esboço descreve, e não do `piloto_fase1.py` (Opus 5, síncrono).

## Pendências de conteúdo

- O `piloto_fase1.py` (Opus 5) chegou a rodar, mas após poucas codificações (duas ou três) o script apresentou erros sistemáticos. Na correção, decidiu-se trocar o Opus pelo Sonnet 5 e migrar para a Batch API (scripts `submeter_batch_sonnet.py` e `processar_batch_sonnet.py`). Dessa execução inicial não há saída depositada.
- Depositar o log da execução e, se existir, o JSONL bruto. O CSV das duas partes está depositado. A Rcl 9.428 tem como causa um PDF digitalizado (ver D). Os PDFs (137 arquivos, 70 MB) não serão depositados, por decisão do autor. No lugar, consta a lista das unidades de análise em `../D_codificacao/dados/entrada/lista_unidades_analise.csv`.
- Registrar expressamente o diagnóstico de massa insuficiente da partição de seis grupos, que a nota 45 invoca. C.7 só justifica a agregação de G4 e G6 (um caso cada). O Quadro C.3 já mostra a evidência (G_prev_trad com um caso no Período I, e 25 acórdãos não classificados).

## Inconsistências a resolver

- C.1 diz que o desenho foi abandonado em favor da estratificação binária. O último parágrafo de C.1 e o início de C.5 dizem que a partição de seis grupos "fixou a partição analítica final" e foi "efetivamente adotada". As duas afirmações são incompatíveis entre si e com a subseção 4.5.1.
- A matriz de deslocamentos (C.6) e a escolha dos cortes de 30/04/2016 e 30/04/2022 não são usadas na análise final, que trata o tempo de forma contínua. Convém dizê-lo.
