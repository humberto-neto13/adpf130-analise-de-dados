# Apêndice B. Texto do esboço

## B.1 Nota introdutória

Este apêndice reúne o material relativo à execução do piloto de calibração das dezesseis variáveis descritas na seção 4.3. O piloto compreendeu cinco etapas sucessivas. Primeira, a codificação das dezesseis variáveis, pelo modelo Claude Sonnet 5, de uma amostra de vinte reclamações (vinte e três acórdãos, já que duas das reclamações amostradas possuíam dois acórdãos cada) selecionadas aleatoriamente dentre as reclamações pertinentes. Segunda, a verificação humana dessa amostra, nos mesmos moldes descritos na subseção 4.4.2. Terceira, o isolamento das divergências entre a codificação automatizada e a verificação humana que decorressem de ambiguidade do próprio manual de codificação, depurando-as das divergências atribuíveis a equívoco interpretativo do modelo — depuração que envolveu a releitura das respostas humanas discordantes, de modo a garantir que a divergência registrada não resultasse, ela própria, de equívoco do verificador. Quarta, a identificação de padrões e direções do erro interpretativo do modelo a partir das divergências assim depuradas. Quinta, a elaboração de ajustes ao manual de codificação e ao script de submissão, orientados a mitigar as distorções, os erros interpretativos e as falhas operacionais identificados ao longo do piloto.

A seção B.2 apresenta o material de submissão utilizado na execução do piloto; a seção B.3 documenta o escalonamento do parâmetro técnico que limitou a taxa de sucesso nas primeiras tentativas de submissão; a seção B.4 apresenta o diagnóstico dos padrões de discordância entre a codificação automatizada e a verificação humana; a seção B.5 sintetiza os ajustes decorrentes desse diagnóstico; a seção B.6 reproduz, na íntegra, o manual de codificação em sua versão revisada (versão 2); a seção B.7 registra a situação do protocolo ao término do piloto e os passos seguintes previstos.

## B.2 Material de submissão utilizado no piloto

A execução do piloto de calibração foi automatizada por dois scripts em Python, reproduzidos nas subseções B.2.1 e B.2.2. O primeiro script monta o prompt de sistema a partir da concatenação de instruções gerais de consistência, do texto integral do manual de codificação então vigente (versão 1, anterior aos ajustes descritos na seção B.5) e da especificação do formato de saída, e submete as requisições à Batch API da Anthropic. O segundo script consulta o lote submetido e, uma vez concluído o processamento, extrai e consolida as codificações em arquivo CSV, preservando também um arquivo JSONL com as justificativas textuais completas.

Observa-se que o schema do campo de saída da Variável 2 (MOD_REST), no script então em uso, já especificava codificação múltipla ("classes", no plural) — o que se revelaria, no diagnóstico relatado na seção B.4, incompatível com a definição operacional da variável então vigente no manual, que a tratava como classe única. Essa incompatibilidade entre o prompt de submissão e o manual é examinada em detalhe na seção B.5.

## B.2.1 Script de submissão (submeter_batch_fase2.py)

## B.2.2 Script de processamento dos resultados (processar_batch_fase2.py)

## B.3 Escalonamento do parâmetro max_tokens

A execução do piloto de calibração exigiu, ao todo, cinco tentativas de submissão até que a totalidade dos vinte e três acórdãos da amostra fosse codificada com sucesso. O gargalo identificado foi o parâmetro max_tokens da requisição à API, inicialmente fixado em valor insuficiente. É importante precisar a natureza técnica desse parâmetro: max_tokens não limita a leitura do acórdão pelo modelo (entrada, ou input), que nunca foi fator limitante — o modelo processa documentos consideravelmente mais longos que qualquer acórdão da base —, mas sim o teto de geração da resposta (saída, ou output), incluindo o raciocínio interno (extended thinking) que precede a produção do texto final. Para acórdãos mais longos ou complexos, o modelo por vezes consome parcela substancial desse teto no raciocínio interno, restando margem insuficiente para completar o objeto JSON de saída — o que produz exatamente os dois padrões de erro observados na primeira tentativa: ausência de bloco de texto na resposta, ou texto truncado a meio de uma cadeia de caracteres ("Unterminated string").

O Quadro B.1 documenta a sequência de tentativas, com o valor do parâmetro em cada uma e o resultado obtido. A reclamação Rcl 45682.1 funciona como caso-limite ilustrativo do próprio fenômeno diagnosticado: permaneceu sem codificação bem-sucedida até a quinta tentativa, com o parâmetro elevado a 32.000 — o valor final, adotado no script de submissão vigente (seção B.2.1 e, na versão corrigida, seção B.5).

## Quadro B.1 — Escalonamento do parâmetro max_tokens ao longo das tentativas de submissão

> **Nota de conferência.** O quadro do esboço não sobreviveu à conversão do PDF. A versão em `dados/quadro_B1_escalonamento_max_tokens.csv` foi refeita a partir dos arquivos de `execucoes/` e difere do esboço em alguns pontos, listados no README desta pasta. Em particular, o `max_tokens` da 3ª tentativa foi 16.000, e todos os valores estão agora documentados nos arquivos de requisição, de modo que a ressalva sobre valores "não confirmados" deixa de se aplicar.

*Linhas destacadas em amarelo: evidência documental direta do valor de max_tokens (arquivo de requisição* *JSONL preservado). Nas demais tentativas, o valor não pôde ser confirmado por ausência do arquivo de*

*requisição correspondente nesta base documental. Elaboração própria.*

## B.4 Diagnóstico dos padrões de discordância

O cotejo entre a codificação automatizada e a verificação humana da amostra de vinte e três acórdãos, variável a variável, identificou taxas de discordância acentuadamente heterogêneas — de 0% (Variáveis 6, 10 e 11) a 61% (Variável 2). O Quadro B.2 sintetiza o resultado desse cotejo, já depurado segundo o procedimento descrito na seção B.1 (releitura das respostas humanas discordantes, de modo a assegurar que a divergência registrada não resultasse de equívoco do próprio verificador).

## Quadro B.2 — Diagnóstico das discordâncias entre codificação automatizada e verificação

**humana (23 acórdãos, 16 variáveis)**

*Elaboração própria a partir do cotejo integral entre a codificação do piloto de calibração e a verificação*

*humana.*

Um padrão adicional, transversal a variáveis distintas, foi observado no acórdão da Rcl 44616: as Variáveis 1, 13, 14 e 15 divergiram simultaneamente nesse único caso, configurando efeito em cadeia — a leitura equivocada do fundamento normativo do ato reclamado (Variável 1) parece ter se propagado às variáveis interpretativas subsequentes (aderência, conhecimento e mérito), que dependem logicamente da caracterização correta do ato reclamado. A investigação desse caso revelou sua causa: citação aninhada de três camadas (acórdão, decisão agravada, ato reclamado), em que o modelo confundiu o ato efetivamente reclamado com a decisão agravada que o transcrevia dentro do próprio acórdão do agravo interno. Essa causa está na origem da nova regra de leitura de citação aninhada incorporada às convenções gerais do manual de codificação (seção B.6, nota de rodapé 1).

Sete das dezesseis variáveis (V1, V2, V3, V4, V7, V9, além da regra geral de leitura de citação aninhada) tiveram sua definição operacional revisada em consequência direta do diagnóstico, conforme detalhado na seção B.5 e documentado, com fundamentação própria, no quadro de alterações da versão 2, reproduzido na seção B.6. As demais variáveis com discordância residual — V5, V8, V12, V13, V14, V15 e V16 — não foram objeto de alteração do manual, por não terem revelado padrão sistemático atribuível a ambiguidade da definição operacional, e sim ocorrências isoladas ou concentradas no efeito cascata acima descrito.

## B.5 Ajustes decorrentes do diagnóstico

O diagnóstico relatado na seção B.4 motivou a revisão do manual de codificação, resultando em sua versão 2, cujas alterações estão documentadas no quadro que antecede o manual, na seção B.6. Em síntese, as alterações incidiram sobre: a fusão de duas classes da Variável 1 (FUND), que produziam confusão sistemática sem contrariar o texto do manual então vigente; a correção da Variável 2 (MOD_REST) de classe única para codificação múltipla, sanando incompatibilidade entre a definição operacional e o schema de submissão já em uso; um critério novo para a fronteira da Variável 3 (MOM_REST) entre restrição posterior simples e restrição cumulada com proibição prospectiva; um critério novo para a fronteira da Variável 4 (SUJ_COM) entre profissional individual e sujeito privado não profissional; uma classe residual nova e uma regra de prevalência determinística para a Variável 7 (DIVERG); a alteração da fonte textual prioritária da Variável 9 (DATA), do cabeçalho do acórdão para o Extrato de Ata; e uma nova regra de leitura para citação aninhada nas convenções gerais da Parte 1 do manual.

Concomitantemente à revisão do manual, o script de submissão foi corrigido para refletir a definição revisada da Variável 2, com o campo de saída correspondente alterado de classe única para lista de classes, no mesmo molde já empregado para as Variáveis 1, 5 e 7. O script corrigido, reproduzido a seguir, é o que será empregado na codificação da população (seção B.7).

## B.5.1 Script de submissão corrigido (versão destinada à codificação integral)

Optou-se por não realizar nova rodada do piloto após a incorporação desses ajustes. A decisão se justifica por dois motivos. Primeiro, o padrão de discordância diagnosticado nas sete variáveis revisadas foi, em cada caso, direcional e concentrado — não disperso ou aleatório —, o que permite atribuir a divergência à ambiguidade da definição então vigente, e não a limitação intrínseca do modelo que uma segunda rodada de piloto pudesse revelar de forma distinta. Segundo, o custo de uma nova rodada de calibração, com a mesma amostra ou com amostra distinta, não se justificaria à luz da regra já estabelecida de verificação humana integral (subseção 4.4.2), que constitui salvaguarda permanente contra eventuais erros residuais na codificação em escala. A aplicação do manual revisado à totalidade da população prossegue, portanto, diretamente para a codificação, sem nova etapa intermediária de piloto.

## B.6 Manual de codificação (versão 3, íntegra)

O manual reproduzido a seguir corresponde à versão 3, que responde a duas exigências sucessivas. A primeira é o diagnóstico do piloto de calibração (seções B.4 e B.5), que revelou definições operacionais ambíguas em sete variáveis. A segunda é a medição de confiabilidade descrita na subseção 4.4.2, que pressupõe um manual aplicável por codificador sem formação jurídica prévia e levou à reescrita integral do texto, com explicação dos conceitos jurídicos pressupostos, sequências de decisão e casos-fronteira ampliados. Os quadros de alterações documentam as mudanças em relação às versões anteriores.

## B.7 Estado do protocolo ao fim do piloto

Ao término do piloto de calibração, o protocolo de codificação assistida por inteligência artificial reúne os elementos necessários à codificação da população (subseção 4.2.1). Essa etapa emprega o manual de codificação em sua versão 3 (seção B.6) e o *script* de submissão corrigido (seção B.5.1), com o parâmetro max_tokens fixado em 32.000 , valor que se revelou suficiente para a integralidade da amostra do piloto, incluindo o caso-limite da Rcl 45682.1 (seção B.3).

A codificação será então submetida a conferência humana integral, nos termos já descritos na subseção 4.4.2, o que preserva a confiabilidade da codificação independentemente de eventuais divergências residuais não capturadas pelo diagnóstico do piloto.
