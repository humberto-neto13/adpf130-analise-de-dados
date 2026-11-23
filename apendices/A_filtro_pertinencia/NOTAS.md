# Apêndice A. Texto do esboço

## A.1 Nota introdutória

Este apêndice reúne o material relativo à execução do filtro de pertinência descrito na subseção 4.2.3. O filtro foi executado com o objetivo de isolar, dentro do universo bruto de acórdãos exaurientes coletados na busca de jurisprudência, o subconjunto de casos em que o Supremo Tribunal Federal se manifestou, expressa ou implicitamente, sobre a aderência do ato reclamado ao paradigma da ADPF nº 130. Casos em que o Tribunal decidiu a reclamação sem examinar a aderência foram excluídos, por não gerarem informação útil ao teste da hipótese de flexibilização do requisito.

A operação do filtro segue a árvore de decisão de três passos ilustrada na Figura 1 da subseção 4.2.3: o primeiro passo verifica se a reclamação foi conhecida pelo Tribunal, o segundo, se a ausência de aderência ao paradigma foi o motivo do não conhecimento, e o terceiro, se o acórdão examinou a questão da aderência, ainda que não tenha conhecido da reclamação por razão diversa. A resposta afirmativa a qualquer dos três passos torna o caso pertinente; a resposta negativa aos três, não pertinente.

A codificação foi executada pela API da Anthropic, com o modelo Claude Opus 5, em modo síncrono — uma requisição por acórdão — e com temperatura fixada em zero, à época em que essa fixação era ainda tecnicamente possível no modelo. A seção A.2 apresenta o material de submissão à API (script e prompt de sistema); a seção A.3 apresenta o registro integral dos outputs do modelo; a seção A.4 apresenta a verificação humana dos casos classificados como não pertinentes e o registro das reclassificações que resultaram; a seção A.5 apresenta o resultado consolidado do filtro.

## A.2 Material de submissão à inteligência artificial

A execução do filtro foi automatizada por um script em Python (A.2.1) que carrega o universo bruto de acórdãos, submete cada acórdão à API individualmente, e agrega os resultados por reclamação segundo regra explicitada no próprio script (uma reclamação é considerada pertinente se qualquer de seus acórdãos exaurientes for pertinente). Um prompt de sistema (A.2.2) instrui o modelo a aplicar a árvore de decisão e a responder em formato JSON estruturado. O prompt de sistema foi mantido em cache entre as requisições, o que reduz o custo computacional sem comprometer a independência entre as chamadas, na medida em que o cache não transfere conteúdo semântico de uma requisição para outra.

## A.2.1 Script de submissão (filtro_pertinencia.py)

## A.2.2 Prompt de sistema

O prompt reproduzido a seguir corresponde à constante SYSTEM_PROMPT do script de submissão (A.2.1). Foi enviado uma única vez por requisição, mantido em cache pela API, e acompanhou a ementa e a decisão de cada acórdão submetido à codificação.

## A.3 Registro dos outputs do filtro

O Quadro A.1, reproduzido a seguir, apresenta o output integral do filtro aplicado aos 142 acórdãos exaurientes do universo bruto. Cada linha corresponde a um acórdão colegiado. As colunas registram, respectivamente, o identificador do acórdão, a classificação atribuída pelo modelo quanto à pertinência (sim ou não), o passo da árvore de decisão em que a classificação se fixou (1, 2 ou 3 para casos pertinentes; 0 para casos não pertinentes), e a justificativa textual emitida pelo próprio modelo. A ordem de apresentação é alfabética por classe processual e crescente por número dentro de cada classe.

## Quadro A.1 — Output do filtro de pertinência (universo bruto: 142 acórdãos)

*Codificação da coluna "Passo": 0 = não pertinente; 1 = reclamação conhecida; 2 = ausência de aderência foi* *motivo do não conhecimento; 3 = acórdão examinou a aderência apesar de não conhecer da reclamação.*

*Elaboração própria.*

## A.4 Verificação humana dos casos classificados como não pertinentes

> **Nota de conferência.** A planilha original da verificação humana está em `dados/verificacao_humana/` e cobre 13 acórdãos (os 10 não pertinentes e os 3 de Passo 3). O Quadro A.2 em `dados/` foi refeito a partir dela. Ver o README desta pasta.

Concluída a rodada automatizada, a totalidade dos casos classificados pelo modelo como não pertinentes foi submetida à verificação humana pelo pesquisador. Esse procedimento cumpre a função de resguardar a população contra a exclusão indevida de casos que, por particularidade do texto do acórdão ou por dificuldade interpretativa não superada pelo modelo, tenham sido classificados como não pertinentes quando, na verdade, o Tribunal se manifestou sobre a aderência ao paradigma. Não se estendeu a verificação humana aos casos classificados como pertinentes pelo modelo, decisão orientada por dois motivos convergentes: primeiro, o custo de conferir 132 acórdãos classificados como pertinentes ultrapassaria a capacidade de conferência manual no tempo disponível; em segundo lugar, na eventualidade de haver falsos positivos entre os casos que passaram pelo filtro de pertinência, eles serão posteriormente identificados na etapa de codificação, não havendo prejuízo à análise.

O critério de verificação consistiu na leitura direta, pelo pesquisador, da ementa e da decisão de cada um dos dez acórdãos classificados como não pertinentes, com aplicação independente da árvore de decisão da subseção 4.2.3. Em caso de divergência com a classificação do modelo, prevaleceu a decisão do pesquisador. O Quadro A.2 apresenta o registro integral da verificação humana, com as justificativas de ambas as classificações lado a lado. As linhas destacadas em amarelo correspondem aos casos em que a verificação humana resultou em reclassificação, isto é, mudança do status de pertinência.

## Quadro A.2 — Verificação humana dos casos classificados como não pertinentes pelo

**modelo**

*Codificação da coluna "Passo": 0 = não pertinente; 1 = reclamação conhecida; 2 = ausência de aderência foi* *motivo do não conhecimento; 3 = acórdão examinou a aderência apesar de não conhecer da reclamação.*

*Linhas destacadas em amarelo indicam reclassificação. Elaboração própria.*

## A.5 Resultado consolidado do filtro

A consolidação do *output* do modelo com os resultados da verificação humana produz a composição final da população observada. Com efeito, a população compreende 142 acórdãos exaurientes, correspondentes a 137 reclamações distintas, cinco destas com dois acórdãos cada (Rcl 9977, Rcl 23899, Rcl 43110, Rcl 45682 e Rcl 46059). A unidade de análise da pesquisa é a reclamação, conforme fixado na subseção 4.2.1; a agregação de acórdãos em reclamações segue a Alternativa B, pela qual uma reclamação é considerada pertinente se qualquer de seus acórdãos exaurientes for pertinente.

Nesse nível de agregação, o modelo classificou inicialmente 128 reclamações como pertinentes e 9 como não pertinentes. Entre as cinco reclamações com múltiplos acórdãos, quatro (Rcl 9977, Rcl 23899, Rcl 45682 e Rcl 46059) tiveram ambos os acórdãos classificados como pertinentes pelo modelo, sem divergência interna. A quinta, Rcl 43110, apresentou classificação divergente entre os dois acórdãos exaurientes: o acórdão de agravo regimental foi classificado como pertinente (passo 1), ao passo que o acórdão posterior de embargos de declaração foi classificado como não pertinente (passo 0). Pela regra de agregação adotada, a reclamação como um todo foi consolidada como pertinente; o acórdão de embargos, isoladamente não pertinente, integrou o grupo de dez acórdãos submetidos à verificação humana (seção A.4), na qual sua classificação foi confirmada.

A verificação humana dos dez acórdãos classificados como não pertinentes resultou em cinco reclassificações — isto é, cinco acórdãos que o modelo havia excluído passaram a integrar o conjunto dos casos pertinentes, mediante decisão do pesquisador —, todos eles correspondentes a reclamações de acórdão exauriente único. Os outros cinco casos verificados tiveram a classificação do modelo confirmada, entre os quais o acórdão de embargos da Rcl 43110, mencionado no parágrafo anterior. O Quadro A.3 sintetiza a consolidação, já no nível da reclamação.

## Quadro A.3 — Consolidação do filtro de pertinência (nível reclamação)

*Unidade: reclamação. Elaboração própria.*

A populaçao observada nas etapas subsequentes é, portanto, composto por 133 reclamações.
