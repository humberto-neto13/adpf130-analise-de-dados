# Apêndice C. Piloto de estratificação (Fase 1)

Corresponde à nota 45 da monografia (subseção 4.5.1). Documenta o desenho **abandonado** de oito estratos (momento da restrição, meio e sujeito comunicativo), a codificação das Variáveis 3, 4 e 5 nos 137 acórdãos, sem acesso aos desfechos, e a escolha dos cortes temporais. A estratificação final é binária e usa só o momento da restrição.

> **Origem do material.** São originais do autor, idênticos byte a byte: `scripts/piloto_fase1.py` e o texto de `prompt_sistema.txt` (extraído dele). `scripts/submeter_batch_sonnet.py` e `scripts/processar_batch_sonnet.py` foram recuperados do PDF do esboço; no primeiro, o `SYSTEM_PROMPT` foi substituído pelo do script original, e os dois textos coincidem salvo as quebras de linha. Os quadros em `dados/` vêm do PDF.

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
| `dados/quadro_C4_matriz_deslocamentos.csv` | 36 configurações com razão de duração ≤ 2,0 (de 81 avaliadas) | C.6 |
| `NOTAS.md` | Texto explicativo do esboço, incluindo regras de desempate e justificativa da agregação | C.1 a C.7 |

Os seis acórdãos não codificados por falha técnica (Rcl 9068, 9977 acórdão 1, 11305, 38782, 65925 e 83604) constam da tabela sinóptica como `ERRO`, e não de `C3_2_justificativas.csv`.

## README original da Fase 1

`docs/README_original_fase1.md` e `docs/requirements_original_fase1.txt` (originais do autor, da pasta `piloto`). O README descreve a Fase 1 como dois scripts, `converter_pdfs.py` e `piloto_fase1.py`, com o modelo `claude-opus-5`, chamadas síncronas independentes, semente 42, até três tentativas por acórdão, codificação de V3, V4 e V5, e saídas `piloto_fase1.csv` e `log_piloto_fase1.txt`. `piloto_fase1.py` e `converter_pdfs.py` da pasta são idênticos, byte a byte, aos depositados neste repositório. Nenhuma das saídas (`piloto_fase1.csv`, log) estava na pasta.

Observações a esclarecer:
- O README fala em Opus 5 síncrono, e o esboço do Apêndice C em Sonnet 5 via Batch API. A pasta não traz scripts do Sonnet em lote. Se as duas execuções existiram, convém dizer qual produziu os quadros C.1 a C.4.
- O README lista cinco reclamações com mais de um acórdão exauriente, entre elas a Rcl 43.110 (Rcl-AgR de 27/04/2021 e Rcl-AgR-ED de 16/08/2022). Na população final há quatro (9.977, 23.899, 45.682 e 46.059), e a Rcl 43.110 tem um só acórdão. As datas do README também diferem das da codificação da população final (por exemplo, Rcl 23.899: 02/10/2023 no README, 29/09/2023 na codificação), compatível com a diferença entre a data do cabeçalho e a do Extrato de Ata.

## Pendências de conteúdo

- **Esclarecer qual execução produziu os dados de `dados/`.** O esboço descreve a execução com Sonnet 5 via Batch API (`submeter_batch_sonnet.py`). Existe também `piloto_fase1.py`, com Opus 5, síncrono. Se esse script foi rodado, convém depositar a saída dele e dizer que papel teve (execução preliminar, descartada ou comparativa).
- Depositar as saídas brutas (CSV e JSONL) e os textos de entrada usados. A justificativa do modelo para a Rcl 9428 informa que o arquivo continha apenas os títulos das seções. Convém conferir o arquivo de entrada.
- Registrar expressamente o diagnóstico de massa insuficiente da partição de seis grupos, que a nota 45 invoca. C.7 só justifica a agregação de G4 e G6 (um caso cada). O Quadro C.3 já mostra a evidência (G_prev_trad com um caso no Período I, e 25 acórdãos não classificados).

## Inconsistências a resolver

- C.1 diz que o desenho foi abandonado em favor da estratificação binária. O último parágrafo de C.1 e o início de C.5 dizem que a partição de seis grupos "fixou a partição analítica final" e foi "efetivamente adotada". As duas afirmações são incompatíveis entre si e com a subseção 4.5.1.
- A matriz de deslocamentos (C.6) e a escolha dos cortes de 30/04/2016 e 30/04/2022 não são usadas na análise final, que trata o tempo de forma contínua. Convém dizê-lo.
