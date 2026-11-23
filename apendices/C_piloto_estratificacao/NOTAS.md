# Apêndice C. Texto do esboço

## C.1 Nota introdutória

Este apêndice reúne o material relativo à execução da Fase 1 do piloto de estratificação descrito na subseção 4.5.1. O piloto foi executado com o objetivo de calibrar os contornos da partição analítica adotada pela pesquisa, especificamente quanto à definição dos estratos materiais e à fixação dos pontos de corte temporais, sem que essa calibração pudesse ser contaminada por conhecimento prévio dos desfechos das reclamações. Para tanto, foi realizada apenas a codificação das três variáveis materiais que compõem a estratificação (Variáveis 3, 4 e 5 do esquema apresentado na seção 4.3), deixando de fora as variáveis de desfecho (Variáveis 13, 14 e 15).

O piloto de estratificação documentado neste apêndice foi conduzido sob desenho de pesquisa anterior, que estratificava as unidades de análise por momento da restrição, meio comunicativo e sujeito comunicativo, combinados em oito estratos reduzidos a seis. Esse desenho foi posteriormente abandonado em favor de uma estratificação binária, exclusivamente pelo momento da restrição, pelas razões expostas na subseção 4.5.1. O conteúdo deste apêndice é preservado como registro do procedimento e das razões que motivaram sua substituição.

A codificação foi executada pela API da Anthropic, com o modelo Claude Sonnet 5, por meio da Batch API. As seções C.2 e C.3 apresentam, respectivamente, o material de submissão ao sistema (scripts e prompt) e o registro integral dos outputs; a seção C.4 documenta as regras de desempate aplicadas na consolidação dos dados; as seções C.5 e C.6 apresentam a distribuição resultante e a matriz de deslocamentos temporais avaliados; a seção C.7 sintetiza a justificativa da agregação de estratos que fixou a partição analítica final da pesquisa.

## C.2 Material de submissão à inteligência artificial

A execução da Fase 1 do piloto foi automatizada por meio de dois scripts em Python, apresentados nas subseções C.2.1 e C.2.2, e de um prompt de sistema, apresentado na subseção C.2.3. O primeiro script (C.2.1) prepara o arquivo de requisições, submete-o à Batch API da Anthropic e registra o identificador do lote. O segundo (C.2.2) consulta o lote e, uma vez concluído seu processamento, baixa os resultados e os consolida em arquivo CSV. O prompt de sistema (C.2.3) foi mantido em cache entre as requisições, o que reduz o custo computacional sem comprometer a independência entre as chamadas, na medida em que o cache não transfere conteúdo semântico de uma requisição para outra.

## C.2.1 Script de submissão à Batch API (submeter_batch_sonnet.py)

## C.2.2 Script de processamento dos resultados (processar_batch_sonnet.py)

## C.2.3 Prompt de sistema

O prompt reproduzido a seguir corresponde à constante SYSTEM_PROMPT do script de submissão (C.2.1). Foi enviado uma única vez por requisição, mantido em cache pela API, e acompanhou o inteiro teor de cada acórdão submetido à codificação.

## C.3 Registro dos outputs

O registro dos outputs divide-se em duas partes complementares. A primeira (C.3.1) apresenta a tabela sinóptica com a codificação atribuída pelo sistema a cada um dos 137 acórdãos submetidos, em três colunas correspondentes às três variáveis materiais. A segunda (C.3.2) reproduz as justificativas textuais emitidas pelo modelo para cada classificação, entrada a entrada.

Em ambas as partes, adotam-se as seguintes convenções de notação: as letras minúsculas correspondem às classes definidas no prompt de sistema (subseção C.2.3); a notação "ND" (não determinável) indica que o próprio modelo entendeu que o conteúdo do acórdão não permitia decisão segura sobre a variável em questão; a notação "ERRO" indica falha técnica na resposta da API, hipótese em que o acórdão não foi codificado. As classificações múltiplas, aplicáveis à variável de meio comunicativo, aparecem separadas por vírgula.

## C.3.1 Tabela sinóptica da codificação

## Casos não codificados por falha técnica na resposta do modelo

Os seguintes acórdãos não puderam ser codificados pelo modelo em razão de falha técnica na resposta retornada pela API — quer por ausência de bloco textual no retorno, quer por resposta em formato JSON inválido —, tendo sido classificados como NC nas três variáveis materiais na base consolidada do piloto: Rcl 9068; Rcl 9977 (acórdão 1); Rcl 11305; Rcl 38782; Rcl 65925; Rcl 83604.

## C.4 Regras de desempate aplicadas na consolidação

A consolidação dos outputs do modelo em uma base analítica única exigiu, além da mera extração das classificações, a adoção de regras de desempate para dois tipos de situação: (i) casos em que o modelo atribuiu à Variável 3 a classe "c" (ambos), que precisa ser resolvida em favor de uma das duas alternativas dicotômicas para efeitos de estratificação; e (ii) casos em que o modelo atribuiu à Variável 4 ou à Variável 5 uma combinação de classes de categorias opostas na dicotomização adotada pela estratificação, hipótese que exige critério explícito para a alocação. As três regras adotadas são as seguintes.

**Regra 1 (Variável 3 — momento da restrição).** Casos classificados como "c" (ambos), isto é, aqueles em que a restrição incide simultaneamente sobre conteúdo já publicado e sobre conteúdo futuro, foram consolidados como "prévia". A regra baseia-se no fato de que o traço estruturalmente distintivo em relação ao paradigma da ADPF nº 130 é a antecipação da restrição em relação à publicação; a incidência simultânea sobre passado e futuro conserva esse traço.

**Regra 2 (Variável 5 — meio comunicativo).** Casos em que o modelo indicou codificação múltipla combinando meio tradicional (classes "a" ou "b") e meio emergente (classes "c" a "g") foram consolidados como "tradicional". A regra baseia-se na constatação de que, nessas hipóteses de codificação múltipla, o veículo tradicional é sempre o canal originário da comunicação, e o meio emergente costuma corresponder à republicação, o que preserva o traço distintivo do meio tradicional para fins da estratificação.

**Regra 3 (Variável 4 — sujeito comunicativo).** Casos em que o modelo indicou codificação múltipla combinando sujeito profissional (classes "a" ou "b") e sujeito não profissional (classes "c" a "g") foram consolidados como "profissional". Trata-se de regra conservadora, orientada por precaução analítica: manter a classificação profissional preserva a proximidade em relação ao núcleo original de proteção do paradigma, evitando alocar em estratos de flexibilização casos que ainda comportam elemento profissional relevante.

## C.5 Distribuição resultante

Apresentam-se a seguir três quadros com a distribuição dos 137 acórdãos do piloto entre estratos e períodos. O Quadro C.1 apresenta a distribuição bruta, isto é, resultante da aplicação direta das regras de desempate documentadas em C.4, sem qualquer ajuste posterior, com os oito estratos originais e os cortes temporais originalmente previstos no projeto (30/04/2015 e 30/04/2021). O Quadro C.2 apresenta a distribuição após o deslocamento dos cortes temporais em um ano à direita (30/04/2016 e 30/04/2022), mantida a partição em oito estratos originais. O Quadro C.3 apresenta a distribuição final, após a agregação dos estratos materialmente próximos (G1+G4 e G2+G6, conforme justificado na seção C.7), configurando a partição analítica de seis grupos efetivamente adotada pela pesquisa.

## Quadro C.1 — Distribuição bruta com cortes temporais originais

*Cortes: Período I até 30/04/2015; Período II até 30/04/2021; Período III até 17/08/2026.* *Unidade de análise: acórdão. Elaboração própria.*

## Quadro C.2 — Distribuição após o deslocamento dos cortes temporais

*Cortes: Período I até 30/04/2016; Período II até 30/04/2022; Período III até 17/08/2026.* *Estratos preservados em sua composição original. Unidade de análise: acórdão. Elaboração* *própria.*

## Quadro C.3 — Distribuição final após deslocamento dos cortes e agregação de estratos

*Cortes: Período I até 30/04/2016; Período II até 30/04/2022; Período III até 17/08/2026.* *Agregação: G1+G4 → G_prev_trad; G2+G6 → G_post_trad. Unidade de análise: acórdão.* *Elaboração própria.*

## C.6 Matriz de deslocamentos temporais testados

A definição dos pontos de corte temporais adotados pela pesquisa foi precedida da avaliação sistemática de 81 configurações alternativas, resultantes da combinação de nove deslocamentos discretos (−12, −6, 0, +6, +12, +18, +24, +30 e +36 meses) aplicados a cada um dos dois pontos de corte, tendo por referência os pontos originalmente previstos no projeto (30/04/2015 e 30/04/2021). Cada configuração foi avaliada segundo dois critérios simultâneos: (i) o equilíbrio da massa amostral entre os três períodos, medido pelo índice de desequilíbrio numérico definido adiante; e (ii) a comparabilidade das durações dos períodos, medida pela razão entre a maior e a menor duração da partição.

O índice de desequilíbrio numérico foi calculado como a raiz quadrada da média dos desvios quadráticos das proporções observadas em cada período em relação à distribuição perfeitamente uniforme (um terço em cada período). O índice varia entre 0 (equilíbrio perfeito) e valores mais altos (maior concentração em um ou dois períodos). Formalmente, para uma partição com contagens (n₁, n₂, n₃) e total N, o índice é dado pela raiz de [((p₁ − 1/3)² + (p₂ − 1/3)² + (p₃ − 1/3)²) / 2], em que pᵢ = nᵢ / N.

O Quadro C.4, reproduzido a seguir, apresenta as 36 configurações em que a razão entre a maior e a menor duração dos três períodos não excede 2,0. Esse limite exclui configurações em que um dos períodos ficaria excessivamente comprimido em relação aos demais, comprometendo a comparabilidade substantiva das unidades temporais. A configuração adotada pela pesquisa aparece destacada em amarelo. Não corresponde à configuração de menor desequilíbrio absoluto, mas configura, entre as opções em que a razão de duração permanece próxima da unidade, o melhor equilíbrio entre os dois critérios.

QuadroC.4—Configuraçõesdedeslocamentotemporaltestadas(razão

deduração≤2,0)

*A linha destacada em amarelo corresponde à configuração adotada pela pesquisa (C1 = 30/04/2016; C2 =*

*30/04/2022). Elaboração própria a partir dos dados do piloto de estratificação (Fase 1).*

## C.7 Justificativa da agregação de estratos

A agregação dos estratos G1 e G4 em um único grupo (G_prev_trad) e dos estratos G2 e G6 em um único grupo (G_post_trad), aplicada à distribuição do Quadro C.3, decorre de constatação empírica combinada a fundamentação dogmática. Sob o aspecto empírico, o piloto revelou que os estratos G4 e G6 apresentaram, cada um, apenas um caso classificado, com massa manifestamente insuficiente para sustentar qualquer comparação temporal. Sob o aspecto dogmático, a agregação se justifica pela observação de que os quatro estratos originais associados a veículos tradicionais (G1, G2, G4 e G6) diferem entre si, dois a dois, apenas pela natureza do sujeito comunicativo (profissional ou não profissional).

A distinção entre sujeito profissional e não profissional, relevante nos meios digitais, perde poder explicativo quando o próprio canal já é institucional. Veículos tradicionais de comunicação — imprensa impressa e radiodifusão — absorvem, em boa medida, a especificidade do sujeito que neles se expressa. Os veículos de radiodifusão sonora e de sons e imagens operam sob regime constitucional de outorga estatal, nos termos do art. 223 da Constituição da República, observado o regime instituído pelo Código Brasileiro de Telecomunicações (Lei nº 4.117, de 1962). Com relação à mídia impressa, embora a Constituição, em seu art. 220, § 6º, vede a exigência de licença para o exercício da atividade, o regime jurídico da responsabilização civil pelo conteúdo veiculado pressupõe a mediação editorial institucionalizada característica das empresas jornalísticas, cuja atividade responde civilmente, ao lado do autor do escrito, pelo dano decorrente de publicação, nos termos consolidados pela Súmula nº 221 do Superior Tribunal de Justiça.

Nesse contexto, a distinção material relevante entre G1 e G4, ou entre G2 e G6, tem baixo peso comparado ao que a distinção entre meio tradicional e meio emergente representa para os fins da estratificação adotada. A agregação, portanto, não é ajuste *ad hoc* à escassez amostral, senão o reconhecimento, autorizado pelos dados do piloto, de que a partição analítica em oito estratos originalmente proposta comportava um recorte que não sustentava a diferenciação material esperada para os casos de veículo tradicional. Os quatro estratos remanescentes, todos caracterizados por meio emergente (G3, G5, G7 e G8), preservam a distinção original entre sujeito profissional e não profissional, na medida em que a ausência de mediação editorial institucionalizada faz da natureza do sujeito variável relevante para a diferenciação dos casos.
