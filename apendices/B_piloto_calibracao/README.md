# Apêndice B. Piloto de calibração do manual

Corresponde à nota 42 da monografia (subseção 4.4.1). Reúne o procedimento do piloto (20 reclamações, 23 acórdãos, Claude Sonnet 5), o material de submissão, os padrões de discordância e o manual de codificação.

> **Origem do material.** São originais do autor, idênticos byte a byte: `scripts/submeter_batch_fase2.py`, `scripts/processar_batch_fase2.py`, `manual/manual_codificacao_v1.txt` (o manual lido pelo script, com a marca de ordem de bytes que entrou no prompt) e `manual/manual_codificacao_v3.md`, além de tudo em `execucoes/` (requisições, identificadores de lote, saídas e logs das cinco tentativas). Os arquivos em `prompts/` foram extraídos das constantes do script original. `scripts/submeter_batch_fase2_corrigido.py` foi reconstruído a partir do original, com as duas alterações descritas no esboço (Variável 2 como lista, e V2 na regra de codificação múltipla), e coincide com o texto do PDF, salvo as quebras de linha. Os quadros B.1 e B.2 e `manual/registro_alteracoes.md` vêm do PDF do esboço, e o Quadro B.1 foi **corrigido** com os dados de `execucoes/` (ver abaixo).

## Conteúdo

| Arquivo | O que é | Seção do esboço |
|---|---|---|
| `scripts/submeter_batch_fase2.py` | Script de submissão do piloto (manual v1) | B.2.1 |
| `scripts/processar_batch_fase2.py` | Processamento dos resultados do lote | B.2.2 |
| `scripts/submeter_batch_fase2_corrigido.py` | Script corrigido, destinado à codificação integral (reconstruído, ver nota acima) | B.5.1 |
| `prompts/instrucoes_gerais.txt` | `INSTRUCOES_GERAIS` (idêntica nas duas versões do script) | B.2.1, B.5.1 |
| `prompts/formato_saida_v1.txt`, `prompts/formato_saida_corrigido.txt` | `FORMATO_SAIDA` antes e depois do ajuste da Variável 2 (classe única → lista) | B.2.1, B.5.1 |
| `manual/manual_codificacao_v1.txt` | Manual de codificação, versão 1 (lido por `submeter_batch_fase2.py`), com Partes 1 a 3 | B.2 |
| `manual/manual_codificacao_v3.md` | Manual de codificação, versão 3, íntegra | B.6 |
| `manual/registro_alteracoes.md` | Registro de alterações V1 → V2 e V2 → V3 | B.6 |
| `execucoes/tentativa_1/` a `tentativa_5/` | Registro das cinco submissões à Batch API: `requisicoes_*.jsonl` (o que foi enviado), `batch_id_*.txt`, `piloto_fase2_*.csv`, `piloto_fase2_completo_*.jsonl` (com justificativas), `log_*.txt` e, na 4ª, `piloto_fase2_respostas_com_erro(4).txt` | B.3 |
| `dados/quadro_B1_escalonamento_max_tokens.csv` | Escalonamento de `max_tokens` (8.000, 8.000, 16.000, 16.000, 32.000), refeito a partir de `execucoes/` | B.3 |
| `dados/quadro_B2_diagnostico_discordancias.csv` | Discordâncias por variável (23 acórdãos) | B.4 |
| `NOTAS.md` | Texto explicativo do esboço | B.1 a B.5, B.7 |

O `prompt de sistema` do piloto é montado em tempo de execução por `INSTRUCOES_GERAIS` + texto do manual + `FORMATO_SAIDA`. O manual reproduzido em `manual/manual_codificacao_v3.md` corresponde à versão 3. O registro das alterações entre versões está em `manual/registro_alteracoes.md`.

## Execuções do piloto

As cinco tentativas usaram o mesmo prompt de sistema (75.711 caracteres, mesma soma de verificação nos cinco arquivos de requisição): `INSTRUCOES_GERAIS` + `manual_codificacao_v1.txt` + `FORMATO_SAIDA`, com o Sonnet 5 via Batch API. Só o `max_tokens` mudou. O `submeter_batch_fase2.py` depositado traz o valor da última tentativa (32.000). Nas anteriores, o valor foi editado no script entre uma submissão e outra, e consta nos arquivos de requisição.

| Tentativa | max_tokens | Submetidos | Sucesso | Erros |
|---|---|---|---|---|
| 1ª | 8.000 | 23 | 15 | 8 (6 sem bloco de texto, 2 JSON inválido) |
| 2ª | 8.000 | 13 | 4 | 9 |
| 3ª | 16.000 | 13 | 12 | 1 (Rcl 45682.1) |
| 4ª | 16.000 | 1 | 0 | 1 (saída de 16.000 tokens, igual ao teto) |
| 5ª | 32.000 | 1 | 1 | 0 |

A 4ª tentativa sustenta o diagnóstico de B.3: a resposta consumiu exatamente o teto de saída (16.000 tokens) e não chegou a produzir o texto final. A 5ª, com 32.000, usou 14.700 tokens de saída.

## Divergências entre o esboço (B.3 e Quadro B.1) e os arquivos de `execucoes/`

- A 3ª tentativa usou `max_tokens` = 16.000. O esboço indica 8.000.
- A 1ª tentativa teve 6 erros "sem bloco de texto" e 2 "JSON inválido". O esboço indica 5 e 3.
- A 2ª tentativa submeteu 13 acórdãos, não 8, e o arquivo de requisição foi preservado. Cinco deles (Rcl 23899.1, 70430, 45682.2, 9977.2 e 91263) já tinham sido codificados com sucesso na 1ª. A 9977.2, que tinha dado certo na 1ª, falhou na 2ª, e depois deu certo na 3ª.
- Os acórdãos 23899.1, 91263, 45682.2 e 70430 foram codificados com sucesso nas três primeiras tentativas, e o 9977.2 em duas. Os arquivos preservam essas repetições. Falta registrar qual resultado entrou na comparação com a verificação humana.
- O esboço descreve a 5ª tentativa como a que "encerra a rodada com os 23 acórdãos codificados". Isso procede apenas somando os êxitos das cinco tentativas, que cobrem os 23.
- `execucoes/tentativa_4/piloto_fase2_completo(4).jsonl` tem 0 bytes, porque a tentativa não produziu codificação válida.

## Cotejo item a item (piloto × verificação humana)

`dados/cotejo/piloto_fase2_cotejo.xlsx` (original do autor). Aba `piloto_fase2`: codificação do modelo para os 23 acórdãos, já normalizada. Aba `Verificação Humana`: valores do verificador. Uma aba por variável (V1 a V16) com as duas respostas lado a lado e, em V1, V2, V3, V7, V8 e V9, observações do autor sobre o que a discordância revela no manual (fusão das classes b e c da V1, classe penal, proibição de republicação como controle prévio, desempate entre mérito e conhecimento na V7, data do Extrato de Ata na V9).

Conferência feita neste repositório:
- **Proveniência da codificação do cotejo.** Comparando a aba `piloto_fase2` com os CSV de `execucoes/`, a codificação de cada acórdão provém de uma ou mais tentativas: da 1ª tentativa, 12 acórdãos; da 3ª, 7; da última, a Rcl 45.682.1; três acórdãos têm saída idêntica em mais de uma tentativa (ver `dados/cotejo_origem_codificacao_derivado.csv`). Para os dois acórdãos codificados mais de uma vez com resultados distintos (23899.1 e 9977.2), a planilha usa a saída da 1ª tentativa. Isso indica que, havendo repetição, valeu a primeira codificação obtida.
- **Contagem de discordâncias.** Recontadas, coincidem com o Quadro B.2 as variáveis V3 (8), V4 (6), V7 (7), V8 (2), V9 (8), V12 (1), V13 (1), V14 (2), V15 (3), V2 (14, descontando a anotação textual da classe h) e V6, V10 e V11 (0). Divergem por pouco V1 (13 pelo cotejo, 12 no quadro) e V5 (7 contra 5). As diferenças desaparecem se, na V1 da Rcl 91263 (modelo g, humano n/a) e na V5 das duas partes da Rcl 9.977 (modelo ND, humano n/a), os pares forem tratados como equivalentes. O autor confirmou que esse foi o critério adotado (ND ou g, no modelo, contra n/a, no humano, contam como concordância); convém dizê-lo no quadro B.2.
- A V16 não pode ser comparada por contagem simples: o modelo registra a razão de distinção em texto livre e o verificador registra outro texto. O quadro B.2 informa só um caso de aplicabilidade.

Problemas na planilha:
- Nas abas `piloto_fase2` e `Verificação Humana`, o Excel converteu os números `9977.1` e `9977.2` em datas (9977-01-01 e 9977-02-01). As demais abas trazem o texto correto. Convém corrigir a célula.
- Na aba `piloto_fase2`, a coluna `erro` marca a Rcl 28262 com "sem bloco de texto", embora a codificação dela venha da 3ª tentativa, que teve sucesso. A marca parece resíduo da tentativa anterior.

## Pendências de conteúdo

- Explicar por que a 2ª tentativa reenviou 5 acórdãos já codificados. Que codificação entrou no cotejo, já está respondido acima (a da 1ª tentativa, quando havia repetição com resultados distintos; falta o autor confirmar o critério).
- **Manual v2 não existe mais.** Segundo o autor, o texto revisado depois do piloto (a "versão 2" do esboço) serviu de base para a redação da v3 e se perdeu. O registro de alterações (`manual/registro_alteracoes.md`) é o único documento remanescente das alterações V1 → V2. O texto de B.6 e o da monografia devem dizer isso expressamente, em vez de apresentar a v2 como reproduzida.
- **Sorteio da amostra: procedimento a registrar como declaração do autor.** Segundo o autor, a população sorteada foi a dos 137 acórdãos, dispostos em ordem crescente de número, e o gerador de números aleatórios do random.org recebeu vários pedidos de números entre 1 e 137, até se completarem 20 reclamações (23 acórdãos). Não há registro da geração. Ordenados os 137 arquivos de `../D_codificacao/dados/entrada/textos/` por número da reclamação (o `.1` antes do `.2`), as posições da amostra são: 3 (9977.1); 4 (9977.2); 6 (15243); 10 (16329); 21 (21504); 27 (23899.1); 28 (23899.2); 31 (28262); 43 (35549); 54 (41768); 62 (44616); 64 (45682.1); 65 (45682.2); 76 (51153); 88 (61746); 91 (62174); 95 (65002); 97 (65925); 106 (70430); 109 (71028); 116 (79022); 119 (79907); 132 (91263). Os três pares (9977, 23899 e 45682) ocupam posições consecutivas. Quando o número sorteado correspondia a um acórdão de reclamação com dois acórdãos, ambos entraram na amostra (confirmado pelo autor), o que explica 23 acórdãos para 20 reclamações. O sorteio foi feito em 25/08/2026 (data informada pelo autor). Observe-se que, nesse desenho, a probabilidade de seleção de uma reclamação com dois acórdãos é um pouco maior que a das demais.
- ~~Planilha de confronto item a item~~ depositada (ver acima).
- Acrescentar a fundamentação de cada alteração V2 → V3, que a nota 42 promete e o registro cobre só em parte.
- O script efetivamente usado na codificação integral (a monografia o descreve em 4.4.1) deve constar do Apêndice D. O de B.5.1 é descrito como "destinado" a ela, e foi reconstruído por falta do original.

## Inconsistências a resolver

- B.1 diz que B.6 reproduz a "versão 2". B.6 reproduz a versão 3.
- B.6 justifica a v3 por uma "medição de confiabilidade" com codificador sem formação jurídica (subseção 4.4.2). A monografia não a descreve, e o capítulo 7 afirma que não houve confiabilidade entre codificadores independentes.
- A nota 42 fala em "sete variáveis" revisadas. B.4 lista seis variáveis (V1, V2, V3, V4, V7, V9) e uma regra geral de leitura de citação aninhada.
- A subseção 4.4.1 diz que o manual traz as regras de agregação. A v1 as traz (Parte 3), mas a v3 não tem essa parte.
- A subseção 4.4.1 diz que o pesquisador codificou a amostra em paralelo. B descreve a verificação da saída do modelo.
- B.5.1 declara que não se fez nova rodada do piloto após os ajustes da v2. O esboço não informa se a v3, reescrita integralmente depois, foi testada antes da codificação integral.
- B.7 está no futuro ("será submetida").
- As siglas de B.4 seguem a versão antiga (V14 CONHEC, V15 MERITO, V16 DIST). No Quadro 3 da monografia são SEG, MER e JURIS.
