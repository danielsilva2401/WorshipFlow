from pathlib import Path
import os
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else os.environ["APP_DIR"])
app = root / "src" / "App.jsx"
style = root / "src" / "style.css"

s = app.read_text()
css = style.read_text()

if "notification-center" in s and "v56 — notificações e UX mobile" in css:
    print("Melhorias v56 de notificações e UX mobile já presentes.")
    raise SystemExit(0)

old = 'function Dashboard({ admin, user, data, current, blocks, pending, setPage, setModal }) {'
new = 'function Dashboard({ admin, user, data, visibleScales, current, blocks, pending, notifications, openNotifications, setPage, setModal }) {'
if old not in s:
    raise SystemExit("Assinatura do Dashboard não encontrada")
s = s.replace(old, new, 1)

old = '''  const upcoming = sortedScales(
    data.scales.filter((s) => s.status === "published" && s.date >= localDate()),
  ).slice(0, 4);'''
new = '''  const upcoming = sortedScales(
    visibleScales.filter((s) => s.status === "published" && s.date >= localDate()),
  ).slice(0, 4);'''
if old not in s:
    raise SystemExit("Agenda do Dashboard não encontrada")
s = s.replace(old, new, 1)

old = '''        <article className="dash-card notifications-card">
          <div className="dash-title"><span><Bell size={18}/> Notificações recentes</span>{admin && <button onClick={() => setPage("admin")}>Ver todas <ChevronRight size={15}/></button>}</div>
          <div className="notification-list">
            {pending.slice(0,2).map((r)=><div key={r.id}><span className="notification-dot cyan-dot"/><UserCheck/><p><strong>{r.name}</strong><small>solicitou acesso à equipe</small></p></div>)}
            {blocks.slice(0,3).map((b)=><div key={b.id}><span className="notification-dot violet-dot"/><CalendarDays/><p><strong>{b.member_name || "Membro"}</strong><small>bloqueou {dateLabel(b.date)}</small></p></div>)}
            {!pending.length && !blocks.length && <p className="muted">Tudo tranquilo por aqui.</p>}
          </div>
        </article>'''
new = '''        <article className="dash-card notifications-card">
          <div className="dash-title"><span><Bell size={18}/> Notificações recentes</span><button onClick={openNotifications}>Ver todas <ChevronRight size={15}/></button></div>
          <div className="notification-list">
            {notifications.slice(0,4).map((n)=><button type="button" className="dashboard-notification" key={n.key} onClick={openNotifications}><span className={"notification-dot " + (n.type === "registration" ? "cyan-dot" : "violet-dot")}/>{n.type === "registration" ? <UserCheck/> : <CalendarDays/>}<p><strong>{n.title}</strong><small>{n.detail}</small></p><ChevronRight size={15}/></button>)}
            {!notifications.length && <p className="muted">Tudo tranquilo por aqui.</p>}
          </div>
        </article>'''
if old not in s:
    raise SystemExit("Card de notificações do Dashboard não encontrado")
s = s.replace(old, new, 1)

old = '''  useEffect(() => {
    if (!admin) return;
    const count =
      data.registrationRequests.filter((r) => r.status === "pending").length +
      data.unavailability.filter((u) => u.date >= localDate()).length;
    if (prior.current && count > prior.current)
      setNotice("Você recebeu uma nova notificação da equipe.");
    prior.current = count;
  }, [admin, data.registrationRequests, data.unavailability]);'''
new = '''  const notificationSignature = admin
    ? [
        ...data.registrationRequests.filter((r) => r.status === "pending").map((r) => `registration:${r.id}:${r.createdAt || ""}`),
        ...data.unavailability.filter((u) => u.date >= localDate()).map((u) => `block:${u.id}:${u.createdAt || ""}`),
      ].join("|")
    : data.scales
        .filter((scale) => scale.status === "published" && scale.date >= localDate() && scale.participant_emails?.includes(user?.email?.toLowerCase()))
        .map((scale) => `scale:${scale.id}:${scale.updated_date || scale.date || ""}`)
        .sort()
        .join("|");
  useEffect(() => {
    if (!access || !user?.email) return;
    if (prior.current && notificationSignature && notificationSignature !== prior.current)
      setNotice(admin ? "Você recebeu uma nova notificação da equipe." : "Sua escala foi publicada ou atualizada.");
    prior.current = notificationSignature;
  }, [access, admin, notificationSignature, user?.email]);'''
if old not in s:
    raise SystemExit("Efeito antigo de notificação não encontrado")
s = s.replace(old, new, 1)

old = '''    pending = data.registrationRequests.filter((r) => r.status === "pending"),
    notificationKeys = [...pending.map(r=>'registration:'+r.id+':'+(r.createdAt||'')), ...blocks.map(b=>'block:'+b.id+':'+(b.createdAt||''))],
    notificationCount = notificationKeys.filter(k=>!seen.includes(k)).length;'''
new = '''    pending = data.registrationRequests.filter((r) => r.status === "pending"),
    notificationItems = (admin
      ? [
          ...pending.map((r) => ({
            key: `registration:${r.id}:${r.createdAt || ""}`,
            type: "registration",
            title: r.name || r.email || "Novo integrante",
            detail: "solicitou acesso à equipe",
            sortAt: r.createdAt || "",
          })),
          ...blocks.map((b) => ({
            key: `block:${b.id}:${b.createdAt || ""}`,
            type: "block",
            title: b.member_name || "Membro",
            detail: `indisponível em ${dateLabel(b.date)}${b.reason ? " · " + b.reason : ""}`,
            sortAt: b.createdAt || b.date || "",
          })),
        ]
      : visibleScales
          .filter((scale) => scale.status === "published" && scale.date >= localDate())
          .map((scale) => ({
            key: `scale:${scale.id}:${scale.updated_date || scale.date || ""}`,
            type: "scale",
            scaleId: scale.id,
            title: scale.title || "Escala",
            detail: `Escala de ${dateLabel(scale.date)}${scale.time ? " · " + scale.time : ""}${scale.rehearsal_time ? " · Ensaio " + scale.rehearsal_time : ""}`,
            sortAt: scale.updated_date || scale.date || "",
          })))
      .sort((a, b) => String(b.sortAt).localeCompare(String(a.sortAt))),
    notificationKeys = notificationItems.map((item) => item.key),
    notificationCount = notificationKeys.filter((key) => !seen.includes(key)).length;
  const openNotifications = () => {
    const nextSeen = unique([...seen, ...notificationKeys]).slice(-500);
    setSeen(nextSeen);
    try { localStorage.setItem("wf-seen-" + user.uid, JSON.stringify(nextSeen)); } catch {}
    setModal({ type: "notifications" });
  };'''
if old not in s:
    raise SystemExit("Cálculo antigo do sino não encontrado")
s = s.replace(old, new, 1)

old = '''          {admin && (
            <button
              className="notification"
              onClick={() => {setSeen(notificationKeys);localStorage.setItem("wf-seen-"+user.uid,JSON.stringify(notificationKeys));setPage("admin");}}
              aria-label={notificationCount + " notificações"}
            >
              <Bell size={19} />
              {notificationCount > 0 && <span>{notificationCount}</span>}
            </button>
          )}'''
new = '''          {access && (
            <button
              className="notification"
              onClick={openNotifications}
              aria-label={notificationCount + " notificações"}
            >
              <Bell size={19} />
              {notificationCount > 0 && <span>{notificationCount}</span>}
            </button>
          )}'''
if old not in s:
    raise SystemExit("Botão antigo do sino não encontrado")
s = s.replace(old, new, 1)

old = '<Dashboard admin={admin} user={user} data={data} current={current} blocks={blocks} pending={pending} setPage={setPage} setModal={setModal}/>'
new = '<Dashboard admin={admin} user={user} data={data} visibleScales={visibleScales} current={current} blocks={blocks} pending={pending} notifications={notificationItems} openNotifications={openNotifications} setPage={setPage} setModal={setModal}/>'
if old not in s:
    raise SystemExit("Uso do Dashboard não encontrado")
s = s.replace(old, new, 1)

old = 'className={modal.type === "chords" ? "cifra-dialog" : ""}'
new = 'className={modal.type === "chords" ? "cifra-dialog" : modal.type === "notifications" ? "notifications-dialog" : ""}'
if old not in s:
    raise SystemExit("Classe do modal não encontrada")
s = s.replace(old, new, 1)

old = '''              profile: "Meu perfil",
            }[modal.type]'''
new = '''              profile: "Meu perfil",
              notifications: "Notificações",
            }[modal.type]'''
if old not in s:
    raise SystemExit("Mapa de títulos do modal não encontrado")
s = s.replace(old, new, 1)

old = '''          {error && <div className="alert error">{error}</div>}
          {modal.type === "profile" ? (
            <ProfileForm user={user} access={access} busy={busy} action={action} saveProfile={saveProfile} />'''
new = '''          {error && <div className="alert error">{error}</div>}
          {modal.type === "notifications" ? (
            <div className="notification-center">
              <div className="notification-center-intro">
                <Bell size={20}/><div><strong>{notificationItems.length ? "Atualizações da equipe" : "Tudo em dia"}</strong><small>{notificationItems.length ? "Ao abrir esta central, os alertas do sino são marcados como vistos." : "Não há notificações ativas no momento."}</small></div>
              </div>
              <div className="notification-center-list">
                {notificationItems.map((n) => (
                  <button type="button" className="notification-center-item" key={n.key} onClick={() => {
                    setModal(null);
                    if (n.type === "scale") { setSelected(n.scaleId); setTab("scale"); setPage("scales"); }
                    else if (admin) setPage("admin");
                  }}>
                    <span className={"notification-center-icon " + n.type}>{n.type === "registration" ? <UserCheck size={18}/> : <CalendarDays size={18}/>}</span>
                    <span className="grow"><strong>{n.title}</strong><small>{n.detail}</small></span>
                    <ChevronRight size={17}/>
                  </button>
                ))}
                {!notificationItems.length && <Empty icon={Bell}>Nenhuma notificação ativa.</Empty>}
              </div>
            </div>
          ) : modal.type === "profile" ? (
            <ProfileForm user={user} access={access} busy={busy} action={action} saveProfile={saveProfile} />'''
if old not in s:
    raise SystemExit("Corpo inicial do modal não encontrado")
s = s.replace(old, new, 1)

app.write_text(s)

css += r'''

/* v56 — notificações e UX mobile */
.notification-list .dashboard-notification{width:100%;display:grid;grid-template-columns:auto auto minmax(0,1fr) auto;align-items:center;gap:9px;padding:8px 0;border:0;border-bottom:1px solid rgba(110,147,194,.08);background:transparent;color:inherit;text-align:left;cursor:pointer}
.notification-list .dashboard-notification:last-child{border-bottom:0}.notification-list .dashboard-notification>svg{color:#7992b2}.notification-list .dashboard-notification p{margin:0;min-width:0}.notification-list .dashboard-notification strong,.notification-list .dashboard-notification small{display:block}.notification-list .dashboard-notification small{margin-top:3px;color:var(--muted);font-size:8px;line-height:1.4}
.notifications-dialog{width:min(620px,calc(100vw - 28px))}
.notification-center{display:grid;gap:14px;min-width:min(540px,78vw)}.notification-center-intro{display:flex;align-items:center;gap:12px;padding:14px;border:1px solid rgba(54,199,255,.18);border-radius:15px;background:linear-gradient(135deg,rgba(22,168,255,.08),rgba(103,71,255,.08))}.notification-center-intro>svg{color:var(--cyan);flex:0 0 auto}.notification-center-intro div{display:flex;flex-direction:column;gap:4px}.notification-center-intro strong{font-size:12px}.notification-center-intro small{color:var(--muted);font-size:9px;line-height:1.5}.notification-center-list{display:flex;flex-direction:column;gap:8px;max-height:min(58vh,520px);overflow:auto}.notification-center-item{width:100%;display:flex;align-items:center;gap:11px;padding:12px;border:1px solid var(--line);border-radius:13px;background:rgba(10,20,35,.72);color:inherit;text-align:left;cursor:pointer;transition:.18s}.notification-center-item:hover{border-color:rgba(58,201,255,.28);background:rgba(13,27,46,.9)}.notification-center-item strong{display:block;font-size:11px}.notification-center-item small{display:block;margin-top:4px;color:var(--muted);font-size:9px;line-height:1.45}.notification-center-icon{width:38px;height:38px;display:grid;place-items:center;border-radius:12px;flex:0 0 auto;background:rgba(92,82,255,.11);color:#a68bff}.notification-center-icon.registration{background:rgba(31,205,255,.1);color:#58e6ff}.notification-center-icon.scale{background:rgba(45,211,154,.1);color:#55e7ae}
html[data-theme="light"] .notification-center-item{background:rgba(247,251,255,.94)}
@media(max-width:680px){.topbar-actions .notification{width:40px;height:40px}.notifications-dialog{width:calc(100vw - 18px);max-width:none;margin:auto 9px max(9px,env(safe-area-inset-bottom));border-radius:22px 22px 16px 16px}.notification-center{min-width:0;width:100%;gap:10px}.notification-center-item{min-height:62px;padding:11px}.notification-center-item strong{font-size:12px}.notification-center-item small{font-size:9px}.notification-center-icon{width:40px;height:40px}.mobile-nav button{min-height:54px}.mobile-nav button svg{width:22px;height:22px}.app-main{padding-bottom:calc(112px + env(safe-area-inset-bottom))}}
'''
style.write_text(css)

pkg = root / "package.json"
ps = pkg.read_text()
ps = re.sub(r'"version"s*:s*"[^"]+"', '"version": "1.0.56"', ps, count=1)
pkg.write_text(ps)

print("Melhorias v56 de notificações e UX mobile aplicadas.")
