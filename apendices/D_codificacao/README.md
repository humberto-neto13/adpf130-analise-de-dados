# Apêndice D. Codificação integral

Corresponde à nota 47 da monografia (seção 5.2). **Ainda vazio.** Segundo a monografia, deve documentar o processo de codificação em sua inteireza, incluindo o protocolo, os resultados do modelo e a planilha de verificação item a item.

## A depositar

- [ ] Script da rodada completa de codificação (Claude Sonnet 5, Batch API, semente de ordenação), com a versão do manual efetivamente usada (v3, ver `../B_piloto_calibracao/manual/`). Indicar se é o script de B.5.1.
- [ ] Manual de codificação e prompt exatamente como submetidos, com somas de verificação.
- [ ] Saída bruta do modelo para os 137 acórdãos (JSONL e CSV) e logs de execução (tokens, custo, erros e reenvios).
- [ ] Textos de entrada (inteiro teor) ou, se houver restrição, lista dos acórdãos e do procedimento de obtenção (portal do STF, nota 38).
- [ ] Planilha de verificação humana, item a item (137 acórdãos × 16 variáveis = 2.192 itens), com valor do modelo, valor final, decisão e categoria do erro.
- [ ] Tipologia de erros e critérios de atribuição de categoria. Sustenta a Figura 3 e as Tabelas 3 e 4, e hoje não está documentada.
- [ ] Regra e procedimento de agregação de 137 acórdãos em 133 reclamações (subseção 4.2.1 e nota 46), com o código ou o registro da operação manual.
- [ ] Matriz consolidada (se não ficar em `E_analises`, ver abaixo).
- [ ] Se algum passo usou embeddings (o README antigo citava uma chave da Voyage AI), documentar o uso aqui.
