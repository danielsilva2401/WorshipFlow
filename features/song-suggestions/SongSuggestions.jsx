import React, { useRef, useState } from 'react';
import { suggestionPayload } from './suggestions';
export default function SongSuggestions({ admin, user, access, items, submit, loading, loadError }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const lock = useRef(false);
  async function send(event) {
    event.preventDefault();
    if (lock.current) return;
    const form = event.currentTarget;
    lock.current = true; setBusy(true); setError(''); setSuccess('');
    try {
      const values = Object.fromEntries(new FormData(form));
      suggestionPayload(values, user, access, null);
      await submit(values);
      form.reset(); setSuccess('Sugestão enviada! Ela já está disponível nas notificações do administrador.');
    } catch (e) { setError(e.message || 'Não foi possível enviar. Tente novamente.'); }
    finally { lock.current = false; setBusy(false); }
  }
  return <section className="suggestions-page">
    <h1>{admin ? 'Sugestões da equipe' : 'Sugerir músicas'}</h1>
    <p className="muted">{admin ? 'Músicas que a equipe gostaria de cantar.' : 'Compartilhe uma música com o administrador.'}</p>
    {!admin && <form className="dash-card suggestion-form" onSubmit={send}>
      <label>Música<input name="title" required maxLength={160} disabled={busy} /></label>
      <label>Cantor ou banda<input name="artist" required maxLength={160} disabled={busy} /></label>
      <label>Observação (opcional)<textarea name="note" maxLength={1000} rows={3} disabled={busy} /></label>
      <button type="submit" className="primary" disabled={busy}>{busy ? 'Enviando…' : 'Enviar sugestão'}</button>
      {error && <p role="alert">{error}</p>}{success && <p role="status">{success}</p>}
    </form>}
    <h2>{admin ? 'Sugestões recebidas' : 'Minhas sugestões'}</h2>
    {loading && <p role="status">Carregando sugestões…</p>}
    {loadError && <p role="alert">Não foi possível carregar as sugestões. {loadError}</p>}
    {!loading && !loadError && !items.length && <p className="muted">Nenhuma sugestão por enquanto.</p>}
    {items.map(s => <article key={s.id} className="dash-card suggestion-item"><h3>{s.title}</h3><p>{s.artist}</p>{admin && <small>Enviada por {s.user_name || s.user_email}</small>}{s.note && <p className="suggestion-note">{s.note}</p>}</article>)}
  </section>;
}
