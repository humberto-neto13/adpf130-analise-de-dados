# adpf130-analise-de-dados

Código utilizado no Trabalho de Conclusão de Curso de Humberto Guimarães Souto Neto, apresentado à Faculdade de Direito da Universidade de Brasília (FD-UnB) em 2026, sob orientação do Professor Dr. Juliano Zaiden.

## Sobre a pesquisa

Estudo empírico-dogmático da jurisprudência do Supremo Tribunal Federal em reclamações constitucionais que invocam a ADPF 130 como paradigma. A pesquisa investiga se houve flexibilização do requisito de aderência estrita ao longo do tempo e se essa flexibilização corresponde a uma aplicação extraordinária da transcendência dos motivos determinantes.

O universo empírico compreende 142 acórdãos exaurientes, referentes a 137 reclamações distintas. A coleta foi encerrada em 17/08/2026.

## Estrutura do repositório

```
├── converter_pdfs.py        # converte os inteiros teores em PDF para texto
├── filtro_pertinencia.py    # aplica a árvore de decisão de pertinência
├── piloto_fase1.py          # codificação piloto conforme a matriz de variáveis
├── prompts/                 # prompts enviados ao modelo
├── resultados/              # respostas brutas da API e codificações finais
└── README.md
```

## Requisitos

- Python [versão]
- Bibliotecas listadas em `requirements.txt`
- Chave de API da Anthropic e da Voyage AI

As chaves devem ser definidas como variáveis de ambiente (`ANTHROPIC_API_KEY` e `VOYAGE_API_KEY`) e nunca escritas no código.

## Como reproduzir

1. Instale as dependências com `pip install -r requirements.txt`
2. Coloque os PDFs dos acórdãos na pasta `[nome da pasta]`
3. Execute `converter_pdfs.py`
4. Execute `filtro_pertinencia.py`
5. Execute `piloto_fase1.py`

## Nota sobre a codificação assistida por IA

A filtragem e a codificação foram feitas com o modelo Claude Opus 5 (Anthropic), por chamadas independentes à API, com prompt caching e ordem de submissão aleatorizada. Modelos de linguagem não produzem respostas idênticas a cada execução, de modo que uma nova rodada pode gerar resultados ligeiramente diferentes. Por isso, as respostas brutas obtidas na pesquisa estão preservadas na pasta `resultados/`, e são elas que fundamentam as análises do trabalho.

O filtro de pertinência foi verificado manualmente em uma amostra de 23 acórdãos.

## Como citar

[SOBRENOME, Nome]. *[Título do TCC]*. Trabalho de Conclusão de Curso (Bacharelado em Direito). Universidade de Brasília, Brasília, [ano]. Código disponível em: [link do repositório].

## Licença

Código distribuído sob a licença MIT.
