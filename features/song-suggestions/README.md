# v58 — Sugestões de músicas

Incremento sobre a v57 nativa, sem alterações no PWA publicado.

- Usuário aprovado: aba Sugestões, formulário música/cantor/observação e lista própria.
- Admin: lista de toda a equipe, aviso em tempo real no sino e acesso pela notificação.
- Abrir o sino mantém o comportamento v56: alertas atuais ficam vistos neste dispositivo.
- Não inclui push com o app fechado nem adiciona automaticamente ao repertório.
- Falhas de envio preservam o formulário. Envio simultâneo é bloqueado.

## Implantação pendente

Antes de distribuir o APK, inserir `firestore.rules.fragment` no bloco
`match /databases/{database}/documents` das regras ATUAIS do projeto
`worshipflow-f99f6`, revisar sobreposições permissivas e testar no emulador.
O repositório não contém as regras atuais. Não substituir pelas regras antigas
que acompanharam versões PWA, pois isso pode reverter permissões da v57.
Nenhuma regra foi publicada por esta alteração.

A nova coleção é `songSuggestions`. A consulta do usuário filtra `user_uid`;
o admin consulta todas. O próprio documento origina a notificação, sem uma
segunda gravação que possa falhar. Horário fornecido por serverTimestamp.

## Validação

`node --test features/song-suggestions/suggestions.test.mjs`

Reconstruir a base conforme o workflow, aplicar v54, v55, v56 (encadeia v57),
e depois `python3 scripts/apply_v58.py appsrc`; `npm install` e `npm run build`.
Validar com duas contas: comum envia, admin recebe; comum não lê sugestões
alheias; abrir sino zera contador; nova sugestão volta a incrementar.
