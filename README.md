# adpf130-analise-de-dados

Material de replicação do Trabalho de Conclusão de Curso de Humberto Guimarães Souto Neto, *Uma aplicação extraordinária da teoria da transcendência dos motivos? Estudo acerca do cabimento de reclamação por descumprimento do paradigma da ADPF nº 130*, apresentado à Faculdade de Direito da Universidade de Brasília (FD-UnB) em 2026, sob orientação do Prof. Dr. Juliano Zaiden Benvindo.

Este repositório documenta a pesquisa de forma integral. Reúne, por procedimento, os scripts, os prompts, o manual de codificação, as saídas do modelo, as planilhas de verificação humana e o código das análises, conforme anunciado nas notas 36, 40, 41, 42, 45, 47 e 49 da monografia.

## Sobre a pesquisa

Estudo empírico-dogmático da jurisprudência do Supremo Tribunal Federal em reclamações constitucionais que invocam a ADPF 130 como paradigma. A pesquisa investiga se houve flexibilização do requisito de aderência estrita ao longo do tempo e se essa flexibilização corresponde a uma aplicação extraordinária da transcendência dos motivos determinantes.

O universo bruto compreende 142 acórdãos colegiados exaurientes, referentes a 137 reclamações. Após o filtro de pertinência e a verificação humana, a população analisada compreende 133 reclamações (137 acórdãos). A coleta foi encerrada em 17/08/2026.

## Estrutura do repositório

```
apendices/
├── A_filtro_pertinencia/      # nota 40 e 41. Filtro de pertinência (Claude Opus 5) e verificação humana
├── B_piloto_calibracao/       # nota 42. Piloto de calibração e manual de codificação (v3)
├── C_piloto_estratificacao/   # nota 45. Piloto do desenho de oito estratos, abandonado
├── D_codificacao/             # nota 47. Codificação integral e planilha de verificação (a depositar)
└── E_analises/                # nota 49. Código das análises, dados e matriz consolidada (a depositar)
docs/
└── esboco_apendices_A_B_C.pdf # esboço em PDF a partir do qual A, B e C foram reconstruídos
testes.py                      # etapa confirmatória (a mover para apendices/E_analises/)
```

Cada pasta traz um `README.md` com o conteúdo, as pendências e as inconsistências conhecidas. A ordem alfabética dos apêndices não é a ordem cronológica de execução. O piloto de estratificação (C, Fase 1) antecede o piloto de calibração (B, Fase 2), e ambos antecedem a codificação integral (D).

## Mapa entre a monografia e o repositório

| Monografia | Promessa | Pasta |
|---|---|---|
| Cap. 4 (abertura) e nota 36 | Todos os procedimentos com modelo de linguagem, e a matriz consolidada | A, B, C, D, E |
| Subseção 4.2.3, nota 40 | Instrução padronizada, prompt e registro integral das classificações do filtro | A |
| Subseção 4.2.3, nota 41 | Cotejo entre a classificação da IA e a verificação humana | A |
| Subseção 4.4.1, nota 42 | Piloto, material de submissão, padrões de discordância e manual final | B |
| Subseção 4.5.1, nota 45 | Piloto de estratificação e diagnóstico de massa insuficiente | C |
| Seção 5.2, nota 47 | Protocolo de codificação, resultados do modelo e planilha de verificação | D |
| Subseção 6.1.2.1, nota 49 | Código das análises, matriz consolidada, dados das figuras e registros de execução | E |

## Requisitos

- Python 3 (versão a confirmar)
- Bibliotecas listadas em `requirements.txt` (a criar)
- Chave de API da Anthropic. Se algum passo usou a Voyage AI, indicar a chave exigida e o passo (ver `apendices/D_codificacao/README.md`)

As chaves devem ser definidas como variáveis de ambiente (`ANTHROPIC_API_KEY`) e nunca escritas no código.

## Como reproduzir

A ordem de execução e os caminhos serão consolidados quando as pastas D e E estiverem completas. A sequência prevista é a seguinte.

1. Filtro de pertinência (`apendices/A_filtro_pertinencia/filtro_pertinencia.py`).
2. Codificação integral com o manual v3 (`apendices/D_codificacao/`).
3. Conferência humana (planilha em `apendices/D_codificacao/`) e agregação em 133 reclamações.
4. Análises (`apendices/E_analises/`).

Os pilotos (B e C) estão preservados como registro e não precisam ser reexecutados.

## Nota sobre a codificação assistida por IA

O filtro de pertinência foi executado com o modelo Claude Opus 5 (Anthropic), e a codificação, com o Claude Sonnet 5, por requisições independentes à API, com prompt caching e ordem de submissão aleatorizada. Modelos de linguagem não produzem respostas idênticas a cada execução, de modo que uma nova rodada pode gerar resultados ligeiramente diferentes. Por isso, as respostas brutas obtidas na pesquisa estão preservadas neste repositório, e são elas que fundamentam as análises do trabalho.

O filtro foi conferido pelo pesquisador em todos os acórdãos classificados como não pertinentes (Apêndice A), e a codificação foi verificada integralmente (Apêndice D). Em divergência, prevaleceu a codificação do pesquisador.

## Como citar

SOUTO NETO, Humberto Guimarães. *Uma aplicação extraordinária da teoria da transcendência dos motivos? Estudo acerca do cabimento de reclamação por descumprimento do paradigma da ADPF nº 130*. 2026. Trabalho de Conclusão de Curso (Bacharelado em Direito) – Faculdade de Direito, Universidade de Brasília, Brasília, 2026. Código e dados disponíveis em: https://github.com/humberto-neto13/adpf130-analise-de-dados.

## Licença

Código distribuído sob a licença MIT.
