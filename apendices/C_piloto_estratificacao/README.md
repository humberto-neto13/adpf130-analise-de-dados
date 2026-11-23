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

## Pendências de conteúdo

- **Esclarecer qual execução produziu os dados de `dados/`.** O esboço descreve a execução com Sonnet 5 via Batch API (`submeter_batch_sonnet.py`). Existe também `piloto_fase1.py`, com Opus 5, síncrono. Se esse script foi rodado, convém depositar a saída dele e dizer que papel teve (execução preliminar, descartada ou comparativa).
- Depositar as saídas brutas (CSV e JSONL) e os textos de entrada usados. A justificativa do modelo para a Rcl 9428 informa que o arquivo continha apenas os títulos das seções. Convém conferir o arquivo de entrada.
- Registrar expressamente o diagnóstico de massa insuficiente da partição de seis grupos, que a nota 45 invoca. C.7 só justifica a agregação de G4 e G6 (um caso cada). O Quadro C.3 já mostra a evidência (G_prev_trad com um caso no Período I, e 25 acórdãos não classificados).

## Inconsistências a resolver

- C.1 diz que o desenho foi abandonado em favor da estratificação binária. O último parágrafo de C.1 e o início de C.5 dizem que a partição de seis grupos "fixou a partição analítica final" e foi "efetivamente adotada". As duas afirmações são incompatíveis entre si e com a subseção 4.5.1.
- A matriz de deslocamentos (C.6) e a escolha dos cortes de 30/04/2016 e 30/04/2022 não são usadas na análise final, que trata o tempo de forma contínua. Convém dizê-lo.
