# Scripts recuperados da etapa exploratória (capítulo 7)

Originais do autor, recuperados de conversas anteriores com o Claude e guardados na pasta `scripts_monografia` (de onde vieram, byte a byte). O `LEIA-ME_original.txt` é o texto que acompanhava a pasta. Não foram editados.

## Como executar

De dentro de `testes/`, com Python 3, pandas, numpy e scipy: `python3 org.py`, e assim por diante. Os scripts leem os arquivos de dados da própria pasta (`post.txt`, `relp.txt`, `v24.txt`, `v5.txt`). Os blocos `bloco_cmd*` executam o código de `org.py` até a linha `D={0:1.0}` e reaproveitam suas funções (`ustats` e `conv`).

## Conteúdo

| Arquivo | O que faz | Seção da monografia (numeração provisória) |
|---|---|---|
| `post.txt` | 94 unidades do controle posterior: Rcl, data, V13 (`R` reconhecida, `N` não) e órgão (V8) | Dados de entrada |
| `relp.txt` | Relator de cada uma das 94 unidades | Dados de entrada |
| `v24.txt` | V2 e V4 de cada unidade | Dados de entrada |
| `v5.txt` | V5 de cada unidade | Dados de entrada |
| `org.py` | Mann-Whitney exato por permutação, com postos médios, e estratificado por órgão (van Elteren, p por permutação exata) | 7.3 (rival 3, órgão julgador) |
| `bloco_cmd14_relator_vencidos.py` | Tabela por relator (n, 13-A, pares, probabilidade de superioridade) | 7.3 |
| `bloco_cmd15_a.py` | Estratificado por relator, com o voto do relator no lugar do desfecho. Cenário A: vencido no acórdão prevalente. Cenário B: também vencido no 1º acórdão das Rcl 45.682 e 46.059 | 7.3 |
| `bloco_cmd16_b.py` | Mesmo teste excluindo Moraes, Toffoli ou ambos | 7.3 |
| `bloco_cmd17_c.py` | Estratificado por cadeira (ministro aposentado e sucessor no mesmo estrato) e sensibilidades | 7.3 |
| `bloco_cmd22_reclamante_e_meio_estratificado.py` | Análise por reclamante (V4) e por meio (V5), com proporções até 2021 e de 2022 em diante | 7.2 (rival 2) |
| `bloco_cmd02_reclamante_x_meio_fisher.py` | Cruzamento reclamante profissional × meio digital (Fisher). **Não roda**: depende de `strat.py`, não recuperado | 7.2 |
| `sensibilidade_sem_2020_aproximada.py` | Sensibilidade aproximada sem 2020 e sem 2020–2021, com a data trocada pelo ano | 7.1 (rival 1) |

## Conferência feita neste repositório

- Os dados de entrada conferem com `../matriz_consolidada_v3.xlsx` (aba `Unidades`): as 94 unidades do controle posterior com V13 determinada coincidem em Rcl, data, V13 e órgão; o relator coincide em todas (16 relatores, com as contagens por ministro iguais às de `V10_REL`); `v24.txt` traz a V2 e a V4, e `v5.txt` a V5, todas iguais às da matriz.
- Todos os scripts rodaram, exceto `bloco_cmd02_*`. As saídas estão em `saidas/`. Valores principais: estratificado por órgão, PS 0,625, p 0,0217 (1.017 pares); por relator com o voto do relator, cenário A PS 0,71, p 0,0085 (131 pares), cenário B PS 0,735, p 0,0053 (113 pares), e sem 2020, p 0,0934 (A) e 0,0259 (B); por cadeira, PS 0,644, p 0,040 (160 pares); sem 2020, p 0,187; sem Toffoli, p 0,191. Sensibilidade aproximada: PS 0,609 e p 0,036 (todas as unidades), 0,562 e 0,18 (sem 2020), 0,536 e 0,305 (sem 2020 e 2021).
- O Mann-Whitney por ano do `sensibilidade_sem_2020_aproximada.py` dá p = 0,036, e o exato, com datas, dá 0,032 (capítulo 6). A diferença vem de a versão aproximada usar o ano como data. A versão exata dessa sensibilidade seria `org.py` aplicado sem as unidades de 2020 (e 2021), e não está depositada como script.
- Confira esses valores com as tabelas e o texto do capítulo 7, que não estão no projeto.

## O que não foi recuperado (segundo o autor)

`strat.py` (estratificação por remoção × reclamante profissional, Tabela 16), séries e fluxos de agravo do Corte Aberta, o gráfico de colegiadas e taxa de provimento, as redes de citação da V16, `mapa_remissivo_V16.xlsx` e o teste por cadeira como script isolado (o `bloco_cmd17_c.py` o inclui). Os scripts de `docx/` (geração de seções em Word com o pacote Node `docx`) não foram depositados: não fazem parte da análise.
