# Apêndice A. Filtro de pertinência

Corresponde às notas 40 e 41 da monografia (subseção 4.2.3). Reúne a instrução padronizada, o prompt de submissão, o registro integral das classificações do modelo (Claude Opus 5) e o cotejo com a verificação humana dos casos classificados como não pertinentes.

> **Origem do material.** São originais do autor, idênticos byte a byte: `filtro_pertinencia.py`, `requirements.txt`, `dados/entrada/` e `dados/saidas_originais/`. O `prompt_sistema.txt` foi extraído da constante `SYSTEM_PROMPT` do script. Os quadros A.1 a A.3 em `dados/` foram recuperados do PDF do esboço (`docs/esboco_apendices_A_B_C.pdf`) e conferidos contra as saídas originais: o Quadro A.1 coincide em classificação, passo e justificativa nos 142 acórdãos, e os 10 acórdãos do Quadro A.2 são os que o modelo classificou como não pertinentes. As remissões do texto explicativo (antes `seção 8.x`) foram atualizadas para a numeração atual da monografia (4.x).

## Conteúdo

| Arquivo | O que é | Seção do esboço |
|---|---|---|
| `filtro_pertinencia.py` | Script de submissão e agregação por reclamação | A.2.1 |
| `prompt_sistema.txt` | Prompt de sistema (constante `SYSTEM_PROMPT` do script) | A.2.2 |
| `dados/quadro_A1_output_filtro.csv` | Output do filtro nos 142 acórdãos do universo bruto | A.3, Quadro A.1 |
| `dados/quadro_A2_verificacao_humana.csv` | Verificação humana dos 10 acórdãos classificados como não pertinentes | A.4, Quadro A.2 |
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

## Pendências

- **Temperatura.** O log imprime `Temperatura: 0`, mas isso só repete a constante `TEMPERATURA`, que o script declara e nunca passa à chamada `client.messages.create`. O texto de A.1 e o README antigo da pasta dizem que a execução usou temperatura zero. Nem o código nem o log confirmam isso. Se a API rejeitou o parâmetro para o Opus 5 (o `piloto_fase1.py` do Apêndice C registra que o modelo não o aceita), a constante é resíduo e o texto deve ser corrigido, assim como a nota 43 da monografia.
- O texto de A.5 afirma que a população final compreende 142 acórdãos. Após a verificação humana, são 137 acórdãos e 133 reclamações.
- A docstring do script ainda cita a "seção 8.3 do projeto" (hoje subseção 4.2.3). Não foi alterada, para preservar o código original.
- O README antigo da pasta estimava 20 a 40 minutos e USD 3 a 6. O log registra 11,4 minutos e USD 1,41. O README antigo não foi incluído, e os dados acima o substituem.
- A exportação do portal traz o termo de busca e a URL em linhas de metadados no próprio CSV. O script as descarta ao filtrar pela classe `Rcl`.
