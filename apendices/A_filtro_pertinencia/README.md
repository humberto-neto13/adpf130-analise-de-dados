# Apêndice A. Filtro de pertinência

Corresponde às notas 40 e 41 da monografia (subseção 4.2.3). Reúne a instrução padronizada, o prompt de submissão, o registro integral das classificações do modelo (Claude Opus 5) e o cotejo com a verificação humana dos casos classificados como não pertinentes.

> **Origem do material.** São originais do autor, idênticos byte a byte: `filtro_pertinencia.py`, `requirements.txt`, `dados/entrada/`, `dados/saidas_originais/` e `dados/verificacao_humana/`. O `prompt_sistema.txt` foi extraído da constante `SYSTEM_PROMPT` do script. Os quadros A.1 e A.3 em `dados/` foram recuperados do PDF do esboço (`docs/esboco_apendices_A_B_C.pdf`) e conferidos contra as saídas originais: o Quadro A.1 coincide em classificação, passo e justificativa nos 142 acórdãos, e o Quadro A.2 foi refeito a partir da planilha original (ver abaixo). As remissões do texto explicativo (antes `seção 8.x`) foram atualizadas para a numeração atual da monografia (4.x).

## Conteúdo

| Arquivo | O que é | Seção do esboço |
|---|---|---|
| `filtro_pertinencia.py` | Script de submissão e agregação por reclamação | A.2.1 |
| `prompt_sistema.txt` | Prompt de sistema (constante `SYSTEM_PROMPT` do script) | A.2.2 |
| `dados/quadro_A1_output_filtro.csv` | Output do filtro nos 142 acórdãos do universo bruto | A.3, Quadro A.1 |
| `dados/verificacao_humana/verificacao_humana_filtro.xlsx` | Planilha original da verificação humana (13 acórdãos), sem alterações | A.4 |
| `dados/quadro_A2_verificacao_humana.csv` | Transcrição fiel da planilha acima, em CSV, com colunas de pertinência derivadas dos passos | A.4, Quadro A.2 |
| `dados/quadro_A3_consolidacao.csv` | Consolidação no nível da reclamação (128/9 → 133/4) | A.5, Quadro A.3 |
| `dados/entrada/export_acordaos_2026-08-17_11-19-17.csv` | Exportação do portal de jurisprudência do STF em 17/08/2026 (160 acórdãos de reclamação, mais linhas de metadados da busca) | 4.2.1 |
| `dados/acordaos_excluidos_cognicao_sumaria.csv` | Os 18 acórdãos excluídos por cognição sumária (Rcl-MC-Ref, Rcl-MC-AgR, Rcl-Ref), extraídos da exportação pela regra do script (160 → 142). Arquivo derivado | 4.2.1 |
| `dados/saidas_originais/` | `filtro_por_acordao.csv` (142 linhas, com tokens), `filtro_por_reclamacao.csv` (137 linhas) e `log_execucao.txt`, como gerados pelo script | A.3, A.5 |
| `requirements.txt` | Dependências do script (`anthropic`, `pandas`, `openpyxl`) | |
| `NOTAS.md` | Texto explicativo do esboço | A.1 a A.5 |

## Execução

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
python filtro_pertinencia.py     # lê export_acordaos_2026-08-17_11-19-17.csv na pasta de trabalho
```

O script lê o CSV pelo nome, em caminho relativo, de modo que a exportação (`dados/entrada/`) deve ser copiada para a pasta de execução. Ordem de submissão aleatorizada (semente 42), uma requisição por acórdão, até três tentativas, prompt de sistema com `cache_control`.

## O que o log registra (execução original)

- Início às 10:07:27, duração de 11,4 minutos, 142 acórdãos, nenhum erro.
- Tokens: 130.570 de entrada, 27.382 de saída, 139.872 lidos do cache, 992 gravados no cache. Custo estimado: USD 1,4135.
- Resultado: 132 acórdãos pertinentes e 10 não pertinentes. Por reclamação, 128 pertinentes e 9 não pertinentes.

## Verificação humana (planilha original)

A planilha tem 13 acórdãos, com o passo da árvore atribuído pela API e pelo verificador, a justificativa de cada um e o texto do verificador. São os 10 classificados como não pertinentes (Passo 0) e os 3 únicos acórdãos de Passo 3 do filtro (Rcl 81831, 68437 e 42155).

- **Reclassificações.** Cinco acórdãos passaram de não pertinentes a pertinentes: Rcl 36463 (Passo 2), 18776 (3), 46032 (3), 55948 (1) e 41768 (2). Permanecem não pertinentes Rcl 43110 (acórdão de embargos), 40574, 14747, 28007 e 94879. Isso confere com os números da monografia (9 reclamações não pertinentes, 5 reclassificadas, 133 no universo final).
- **Passo 3.** Dos três acórdãos de Passo 3, dois foram confirmados (81831 e 68437), e o verificador mudou o 42155 para o Passo 2. A pertinência não muda. Os três casos de Passo 3 também foram conferidos pelo verificador, e isso deve constar do Quadro A.2 e da subseção 4.2.3, que hoje só mencionam a conferência dos não pertinentes (decisão do autor: registrar).
- **Textos do verificador.** As justificativas do verificador no esboço em PDF estavam reescritas em redação mais elaborada. O CSV reproduz a planilha literalmente, inclusive a caixa baixa e um colchete solto no fim da justificativa da Rcl 43110. As justificativas da API conferem com o `filtro_por_acordao.csv` nos 13 casos.
- **Rcl 55948.** O verificador registrou Passo 1, embora a justificativa fale de menção à ADPF 130 e à Súmula Vinculante 46. Por decisão do autor, prevalece o passo tal como a verificação humana o avaliou (Passo 1), e o registro permanece como na planilha original. A frase do esboço de que a reclamação "foi de fato conhecida" não consta da planilha.

## Pendências

- **Temperatura.** Decisão do autor: o parâmetro não consta dos scripts porque as versões atuais do Sonnet e do Opus não admitem a definição manual da temperatura. Uma primeira versão do script, que a definia, chegou a rodar e gerou erro na codificação, pois a sintaxe desses modelos rejeita o parâmetro. Por isso a constante `TEMPERATURA` do script (e o `Temperatura: 0` impresso no log) é resíduo e **não** foi enviada à API. O texto de A.1 (`NOTAS.md`, que reproduz o esboço e foi mantido como está), a nota 43 da monografia e o README antigo da pasta dizem que a execução usou temperatura zero e devem ser corrigidos para dizer que o parâmetro não é configurável nesses modelos. O mesmo vale para os Apêndices B, C e D, que também não passam temperatura.
- **142 e 137 acórdãos.** Os 142 acórdãos são o universo antes do filtro de pertinência (depois da exclusão de 18 por cognição sumária, 160 → 142). O filtro, com a verificação humana, removeu 5 acórdãos por impertinência, e o universo final tem 137 acórdãos (133 reclamações). O texto de A.5 deve dizer 142 antes do filtro e 137 depois, e não 142 como população final.
- A docstring do script ainda cita a "seção 8.3 do projeto" (hoje subseção 4.2.3). Não foi alterada, para preservar o código original.
- O README antigo da pasta estimava 20 a 40 minutos e USD 3 a 6. O log registra 11,4 minutos e USD 1,41. O README antigo não foi incluído, e os dados acima o substituem.
- A exportação do portal traz o termo de busca e a URL em linhas de metadados no próprio CSV. O script as descarta ao filtrar pela classe `Rcl`.
