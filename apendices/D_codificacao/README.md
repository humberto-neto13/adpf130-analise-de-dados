# Apêndice D. Codificação integral

Corresponde à nota 47 da monografia (seção 5.2). Documenta a rodada completa de codificação dos 137 acórdãos com o manual v3.

## Conteúdo

- `scripts/submeter_batch_v3.py`: gera as requisições e as submete à Batch API. Modelo `claude-sonnet-5`, `max_tokens` 32000, semente 42 para a ordem aleatória, prompt de sistema (instruções gerais, manual v3 e formato de saída) com prompt caching. As requisições não passam `temperature`.
- `scripts/processar_batch_v3.py`: recupera o lote, valida o formato das respostas, aplica verificações de consistência entre variáveis (os "alertas") e grava o CSV, o JSONL completo e o arquivo de alertas.
- `scripts/converter_pdfs.py`: converte os PDFs do inteiro teor em `.txt` (pypdf), com aviso de extração escassa que pode exigir OCR.
- `dados/entrada/textos/`: os 137 textos submetidos (um `.txt` por acórdão; os quatro pares de reclamações com dois acórdãos aparecem como `9977.1`, `9977.2`, `23899.1`, `23899.2`, `45682.1`, `45682.2`, `46059.1`, `46059.2`).
- `dados/saidas_originais/`:
  - `requisicoes_batch_v3.jsonl.gz`: requisições exatamente como enviadas (23,3 MB descompactadas; a compactação preserva o conteúdo, sha256 do original `e318ecf0…8d6`).
  - `mapa_custom_id_v3.json`: metadados da rodada (modelo, `max_tokens`, semente, arquivo do manual), ordem de envio e relação `custom_id` → arquivo.
  - `batch_id_v3.txt`: `msgbatch_01TajHJmYShqCoz3VhdgwQ3r`.
  - `log_codificacao_v3.txt`: log do processamento.
  - `codificacao_v3.csv`, `codificacao_v3_completo.jsonl`, `alertas_v3.csv`: saída do modelo, sem alteração humana.
- `deepseek_v4_nao_integrado/`: ver adiante.

## Manual

O manual usado na rodada (`manual-codificacao-v3.md`) é idêntico byte a byte a `../B_piloto_calibracao/manual/manual_codificacao_v3.md` (sha256 `2132630410bbcd84…b71`), que permanece como cópia única no repositório.

## Resultado bruto da rodada

- 137 acórdãos codificados, 0 falhas, 0 sem resultado; `stop_reason` `end_turn` em todos.
- Tokens: 5.841.476 de entrada, 1.579.862 de saída, 4.065.192 lidos de cache, 186.192 de criação de cache.
- 11 acórdãos com alerta (12 alertas): 9 de consistência entre V2 e V3 (V3 = "posterior" com V2 combinando a hipótese g com outras), 1 de consistência entre V13 e V15 (91198), 2 de formato em V16 (16492, 43110). Ver `dados/saidas_originais/alertas_v3.csv`.

## Execução

Dentro de uma pasta com os scripts, o manual e `textos/`: `py submeter_batch_v3.py`, depois `py processar_batch_v3.py`, com `ANTHROPIC_API_KEY` definida. Os scripts usam caminhos relativos a essa pasta.

## `deepseek_v4_nao_integrado/`

Scripts, mapa e requisições de uma versão da codificação com o modelo `deepseek-v4-pro` (mesmo prompt, mesma semente), mais um teste. Na pasta de origem não havia arquivo de respostas dessa versão. Material depositado apenas como registro; a monografia reporta somente a rodada com o Claude Sonnet 5. Situação a confirmar pelo autor (executada ou apenas preparada; se executada, onde estão os resultados; se não, se a pasta deve permanecer).

## A depositar

- [ ] Planilha de verificação humana, item a item (137 acórdãos × 16 variáveis = 2.192 itens), com valor do modelo, valor final, decisão e categoria do erro.
- [ ] Tipologia de erros e critérios de atribuição de categoria (sustenta a Figura 3 e as Tabelas 3 e 4).
- [ ] Regra e procedimento de agregação de 137 acórdãos em 133 reclamações (subseção 4.2.1 e nota 46), com o código ou o registro da operação manual.
- [ ] Matriz consolidada (ou, se ficar em `E_analises`, referência cruzada).
- [ ] Se algum passo usou embeddings (o README antigo citava uma chave da Voyage AI), documentar o uso.
