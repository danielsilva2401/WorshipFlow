export function suggestionPayload(values, user, access, createdAt) {
  const title = String(values.title || '').trim();
  const artist = String(values.artist || '').trim();
  const note = String(values.note || '').trim();
  if (!title || !artist) throw new Error('Informe a música e o cantor.');
  if (title.length > 160 || artist.length > 160 || note.length > 1000) throw new Error('Revise o tamanho dos campos.');
  if (!user?.uid || !user?.email) throw new Error('Entre novamente para enviar.');
  return { title, artist, note, user_uid: user.uid, user_email: user.email.toLowerCase(), user_name: String(access?.name || user.displayName || user.email).slice(0,160), createdAt };
}
export function suggestionNotifications(items = []) {
  return items.map(s => ({ key: `suggestion:${s.id}`, type: 'suggestion', title: s.user_name || s.user_email, detail: `sugeriu ${s.title} · ${s.artist}`, sortAt: s.createdAt?.toDate?.().toISOString() || '' }));
}
