# Apêndice B. Piloto de calibração do manual

Corresponde à nota 42 da monografia (subseção 4.4.1). Reúne o procedimento do piloto (20 reclamações, 23 acórdãos, Claude Sonnet 5), o material de submissão, os padrões de discordância e o manual de codificação.

> **Origem do material.** Os scripts, prompts, manual e quadros desta pasta foram recuperados do PDF do esboço dos apêndices (`docs/esboco_apendices_A_B_C.pdf`) e validados por análise sintática e por contagem de linhas. Linhas de código que o PDF quebrou foram reunidas. Os arquivos originais, que estão na máquina do autor, devem substituir as reconstruções antes do depósito definitivo. As remissões internas do texto (antes `seção 8.x`) foram atualizadas para a numeração atual da monografia (4.x).

## Conteúdo

| Arquivo | O que é | Seção do esboço |
|---|---|---|
| `scripts/submeter_batch_fase2_v1.py` | Script de submissão do piloto (manual v1) | B.2.1 |
| `scripts/processar_batch_fase2.py` | Processamento dos resultados do lote | B.2.2 |
| `scripts/submeter_batch_fase2_corrigido.py` | Script corrigido, destinado à codificação integral | B.5.1 |
| `prompts/instrucoes_gerais.txt` | `INSTRUCOES_GERAIS` (idêntica nas duas versões do script) | B.2.1, B.5.1 |
| `prompts/formato_saida_v1.txt`, `prompts/formato_saida_corrigido.txt` | `FORMATO_SAIDA` antes e depois do ajuste da Variável 2 (classe única → lista) | B.2.1, B.5.1 |
| `manual/manual_codificacao_v3.md` | Manual de codificação, versão 3, íntegra | B.6 |
| `manual/registro_alteracoes.md` | Registro de alterações V1 → V2 e V2 → V3 | B.6 |
| `dados/quadro_B1_escalonamento_max_tokens.csv` | Escalonamento de `max_tokens` (8.000 → 32.000) | B.3 |
| `dados/quadro_B2_diagnostico_discordancias.csv` | Discordâncias por variável (23 acórdãos) | B.4 |
| `NOTAS.md` | Texto explicativo do esboço | B.1 a B.5, B.7 |

O `prompt de sistema` do piloto é montado em tempo de execução por `INSTRUCOES_GERAIS` + texto do manual + `FORMATO_SAIDA`. O manual reproduzido em `manual/manual_codificacao_v3.md` corresponde à versão 3. O registro das alterações entre versões está em `manual/registro_alteracoes.md`.

## Pendências de conteúdo

- Depositar os manuais **v1** e **v2**. O piloto rodou com a v1, e só a v3 está reproduzida.
- Depositar a lista das 20 reclamações da amostra e o procedimento do sorteio. Os scripts leem a pasta `./textos`, preenchida "externamente".
- Depositar as saídas brutas do piloto (`piloto_fase2_*.csv`, `requisicoes_batch_fase2*.jsonl`) e a planilha de confronto item a item com a verificação humana. Hoje existe só o quadro agregado.
- Acrescentar a fundamentação de cada alteração V2 → V3, que a nota 42 promete e o registro cobre só em parte.
- O script efetivamente usado na codificação integral (a monografia o descreve em 4.4.1) deve constar do Apêndice D. O de B.5.1 é descrito como "destinado" a ela.

## Inconsistências a resolver

- B.1 diz que B.6 reproduz a "versão 2". B.6 reproduz a versão 3.
- B.6 justifica a v3 por uma "medição de confiabilidade" com codificador sem formação jurídica (subseção 4.4.2). A monografia não a descreve, e o capítulo 7 afirma que não houve confiabilidade entre codificadores independentes.
- A nota 42 fala em "sete variáveis" revisadas. B.4 lista seis variáveis (V1, V2, V3, V4, V7, V9) e uma regra geral de leitura de citação aninhada.
- A subseção 4.4.1 diz que o manual traz as regras de agregação. A v3 as suprimiu (Parte 3 passou ao capítulo metodológico).
- A subseção 4.4.1 diz que o pesquisador codificou a amostra em paralelo. B descreve a verificação da saída do modelo.
- B.5.1 declara que não se fez nova rodada do piloto após os ajustes da v2. O esboço não informa se a v3, reescrita integralmente depois, foi testada antes da codificação integral.
- B.7 está no futuro ("será submetida").
- As siglas de B.4 seguem a versão antiga (V14 CONHEC, V15 MERITO, V16 DIST). No Quadro 3 da monografia são SEG, MER e JURIS.
