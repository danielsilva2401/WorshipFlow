# WorshipFlow PWA — sugestões inteligentes de músicas

Esta feature pertence exclusivamente à linha PWA.

## Objetivo

Durante a criação ou edição de uma escala, mostrar até seis músicas sugeridas antes da biblioteca completa e permitir adicioná-las ao repertório com um toque.

## Critérios do primeiro modelo

- histórico de escalas publicadas;
- dias desde a última vez em que a música foi usada;
- penalidade para repetição nos últimos 30 e 60 dias;
- bônus quando a música já possui cifra e/ou YouTube;
- músicas que nunca entraram em uma escala recebem destaque;
- a escala atualmente editada não conta contra ela mesma;
- músicas já escolhidas desaparecem da lista de sugestões.

A pontuação é usada apenas para ordenar. Ela não é exibida ao usuário.

## Segurança do escopo

Nada desta branch altera o workflow de APK. O build de validação gera apenas a aplicação web/PWA.
