# Piloto de codificação — Fase 1

Dois scripts para a fase de contagem por estrato, cega aos desfechos.

## Requisitos

- Python 3.10 ou superior
- Chave da API Anthropic

## Instalação

```bash
pip install -r requirements.txt
```

No Windows, se `pip` não for reconhecido:

```bash
py -m pip install -r requirements.txt
```

## Estrutura de pastas

```
piloto/
├── converter_pdfs.py
├── piloto_fase1.py
├── requirements.txt
├── pdfs/                            (pasta com os inteiros teores em PDF)
│   ├── 12345.pdf
│   ├── 45682.1.pdf
│   ├── 45682.2.pdf
│   └── ...
└── textos/                          (gerada pelo converter_pdfs.py)
    ├── 12345.txt
    ├── 45682.1.txt
    ├── 45682.2.txt
    └── ...
```

A pasta `textos` deve conter apenas os acórdãos das reclamações pertinentes (excluídos previamente as não pertinentes, identificadas pelo filtro de pertinência).

## Etapa 1 — Conversão dos PDFs para .txt

Execute uma única vez, antes do piloto:

```bash
py converter_pdfs.py
```

O script lê todos os PDFs em `pdfs/` e gera arquivos .txt correspondentes em `textos/`. A conversão é local, sem custo. Se algum PDF exigir OCR (extração escassa de texto), o script sinaliza para tratamento manual.

## Etapa 2 — Execução do piloto Fase 1

Configure a chave da API.

No Windows (Prompt de Comando):
```bash
set ANTHROPIC_API_KEY=sk-ant-...
```

No Mac/Linux:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Execute:

```bash
py piloto_fase1.py
```

O script lê todos os arquivos .txt da pasta `textos`, submete cada um à API em requisição independente, e codifica as Variáveis 3 (MOM_REST), 4 (SUJ_COM) e 5 (MEIO).

## Saídas

- `piloto_fase1.csv` — codificação por acórdão, com colunas: `arquivo`, `momento_restricao`, `sujeito_comunicativo`, `meio_comunicativo`, justificativas de cada variável, contadores de tokens e coluna de erro.
- `log_piloto_fase1.txt` — log completo da execução, com custo total estimado.

## Parâmetros técnicos

- Modelo: `claude-opus-5`
- Prompt caching: aplicado às definições operacionais das três variáveis
- Ordem de submissão: aleatorizada (semente 42, para reprodutibilidade)
- Requisições independentes: cada acórdão em chamada separada, sem histórico
- Tentativas: até 3 por acórdão em caso de erro transitório

## Convenção de nomenclatura dos arquivos

- Reclamação com um único acórdão exauriente: `{numero_reclamacao}.pdf` (e `.txt`)
- Reclamação com múltiplos acórdãos, em ordem cronológica:
  - `{numero_reclamacao}.1.pdf` — mais antigo
  - `{numero_reclamacao}.2.pdf` — mais recente

Cinco reclamações têm múltiplos acórdãos exaurientes na base do STF:

| Reclamação | Acórdão .1 (mais antigo) | Acórdão .2 (mais recente) |
|---|---|---|
| 9977 | Rcl-ED (27/10/2017) | Rcl-AgR-ED (29/03/2019) |
| 23899 | Rcl (02/10/2023) | Rcl-ED (19/11/2024) |
| 43110 | Rcl-AgR (27/04/2021) | Rcl-AgR-ED (16/08/2022) |
| 45682 | Rcl-AgR (22/03/2021) | Rcl (14/03/2022) |
| 46059 | Rcl-AgR (27/04/2021) | Rcl (09/03/2022) |

## Custo estimado

Aproximadamente USD 2-4 para o universo de acórdãos pertinentes (estimativa depende do número de arquivos pertinentes na pasta e do tamanho médio dos inteiros teores). Custo real reportado no log ao final da execução.
