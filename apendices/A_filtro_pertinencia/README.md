# Apêndice A. Filtro de pertinência

Corresponde às notas 40 e 41 da monografia (subseção 4.2.3). Reúne a instrução padronizada, o prompt de submissão, o registro integral das classificações do modelo (Claude Opus 5) e o cotejo com a verificação humana dos casos classificados como não pertinentes.

> **Origem do material.** Os scripts, prompts, manual e quadros desta pasta foram recuperados do PDF do esboço dos apêndices (`docs/esboco_apendices_A_B_C.pdf`) e validados por análise sintática e por contagem de linhas. Linhas de código que o PDF quebrou foram reunidas. Os arquivos originais, que estão na máquina do autor, devem substituir as reconstruções antes do depósito definitivo. As remissões internas do texto (antes `seção 8.x`) foram atualizadas para a numeração atual da monografia (4.x).

## Conteúdo

| Arquivo | O que é | Seção do esboço |
|---|---|---|
| `filtro_pertinencia.py` | Script de submissão e agregação por reclamação | A.2.1 |
| `prompt_sistema.txt` | Prompt de sistema (constante `SYSTEM_PROMPT` do script) | A.2.2 |
| `dados/quadro_A1_output_filtro.csv` | Output do filtro nos 142 acórdãos do universo bruto | A.3, Quadro A.1 |
| `dados/quadro_A2_verificacao_humana.csv` | Verificação humana dos 10 acórdãos classificados como não pertinentes | A.4, Quadro A.2 |
| `dados/quadro_A3_consolidacao.csv` | Consolidação no nível da reclamação (128/9 → 133/4) | A.5, Quadro A.3 |
| `NOTAS.md` | Texto explicativo do esboço | A.1 a A.5 |

## Pendências

- Depositar o CSV de entrada (`export_acordaos_2026-08-17_11-19-17.csv`, 160 acórdãos) e a lista dos 18 acórdãos excluídos por cognição sumária (160 → 142, subseção 4.2.1). Hoje o apêndice começa nos 142.
- Depositar as saídas originais do script (`filtro_por_acordao.csv`, `filtro_por_reclamacao.csv`, `log_execucao.txt`).
- O script aponta para `/mnt/user-data/uploads/...`. Parametrizar o caminho de entrada.
- O texto de A.5 afirma que a população final compreende 142 acórdãos. Após a verificação humana, são 137 acórdãos e 133 reclamações.
- A temperatura zero foi aplicada neste filtro (Opus 5). A nota 43 da monografia trata só do Sonnet 5 e deveria dizê-lo expressamente.
- A docstring do script ainda cita a "seção 8.3 do projeto" (hoje subseção 4.2.3). Não foi alterada, para preservar o código.
