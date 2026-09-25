from pathlib import Path
import os, re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else os.environ['APP_DIR'])
app = root / 'src' / 'App.jsx'
utils = root / 'src' / 'utils.js'
style = root / 'src' / 'style.css'

s = app.read_text()

if 'ENSAIO DA EQUIPE' in s and 'rehearsal_date' in s and 'rehearsal-focus-card' in style.read_text():
    print('Melhorias v55 de Escalas e Ensaios já presentes.')
    raise SystemExit(0)

old_editor = '''        <h3 className="spaced">ENSAIO</h3>
        <div className="grid2">
          <label>
            Horário do ensaio
            <input
              type="time"
              value={v.rehearsal_time || ""}
              onChange={(e) => set({ ...v, rehearsal_time: e.target.value })}
            />
          </label>
          <label>
            Local do ensaio
            <input
              value={v.rehearsal_location || ""}
              onChange={(e) =>
                set({ ...v, rehearsal_location: e.target.value })
              }
              placeholder="Ex.: Templo principal"
            />
          </label>
        </div>'''
new_editor = '''        <h3 className="spaced">ENSAIO</h3>
        <p className="muted rehearsal-editor-hint">Defina os detalhes que aparecerão na aba de ensaio da equipe.</p>
        <div className="grid2">
          <label>
            Data do ensaio
            <input
              type="date"
              value={v.rehearsal_date || ""}
              onChange={(e) => set({ ...v, rehearsal_date: e.target.value })}
            />
          </label>
          <label>
            Horário do ensaio
            <input
              type="time"
              value={v.rehearsal_time || ""}
              onChange={(e) => set({ ...v, rehearsal_time: e.target.value })}
            />
          </label>
        </div>
        <label>
          Local do ensaio
          <input
            value={v.rehearsal_location || ""}
            onChange={(e) =>
              set({ ...v, rehearsal_location: e.target.value })
            }
            placeholder="Ex.: Templo principal"
          />
        </label>'''
if old_editor not in s:
    raise SystemExit('Bloco do editor de ensaio não encontrado')
s = s.replace(old_editor, new_editor, 1)

old_tabs = '''              <button
                className={tab === "chords" ? "active" : ""}
                onClick={() => setTab("chords")}
              >
                <Music2 size={17} /> Cifra
              </button>'''
new_tabs = '''              <button
                className={tab === "rehearsal" ? "active" : ""}
                onClick={() => setTab("rehearsal")}
              >
                <Clock3 size={17} /> Ensaio
              </button>
              <button
                className={tab === "chords" ? "active" : ""}
                onClick={() => setTab("chords")}
              >
                <Music2 size={17} /> Cifra
              </button>'''
if old_tabs not in s:
    raise SystemExit('Bloco de abas da escala não encontrado')
s = s.replace(old_tabs, new_tabs, 1)

needle = '''              </>
            ) : (
              <>
                <section className="card scale-card">'''
rehearsal_view = '''              </>
            ) : tab === "rehearsal" ? (
              <>
                <section className="card rehearsal-focus-card">
                  <div className="rehearsal-focus-head">
                    <div>
                      <span className="badge">ENSAIO DA EQUIPE</span>
                      <h1>{current.title}</h1>
                      <p className="muted">Preparação para {dateLabel(current.date)}</p>
                    </div>
                    <Clock3 size={30} />
                  </div>
                  {(current.rehearsal_date || current.rehearsal_time || current.rehearsal_location) ? (
                    <div className="rehearsal-grid">
                      <div className="rehearsal-detail">
                        <CalendarDays size={20} />
                        <span><small>Data</small><strong>{dateLabel(current.rehearsal_date || current.date)}</strong></span>
                      </div>
                      <div className="rehearsal-detail">
                        <Clock3 size={20} />
                        <span><small>Horário</small><strong>{current.rehearsal_time || "A definir"}</strong></span>
                      </div>
                      <div className="rehearsal-detail rehearsal-location-detail">
                        <MapPin size={20} />
                        <span><small>Local</small><strong>{current.rehearsal_location || "A definir"}</strong></span>
                      </div>
                    </div>
                  ) : (
                    <Empty icon={Clock3}>O ensaio desta escala ainda não foi configurado.</Empty>
                  )}
                </section>

                <section className="card rehearsal-team-card">
                  <h3>EQUIPE DO ENSAIO</h3>
                  {["instrument", "vocal"].map((c) => (
                    <div className="group" key={c}>
                      <h3>
                        {c === "instrument" ? <Music2 size={16} /> : <Mic2 size={16} />} {c === "instrument" ? "BANDA" : "VOCAIS"}
                      </h3>
                      <div className="chips">
                        {current.assignments.filter((m) => m.category === c).map((m) => (
                          <span className="chip" key={m.member_id}>
                            {m.member_name}<small>{roleLabel(m)}</small>
                          </span>
                        ))}
                        {!current.assignments.some((m) => m.category === c) && <span className="muted">Ninguém escalado.</span>}
                      </div>
                    </div>
                  ))}
                </section>

                <section className="card rehearsal-setlist-card">
                  <div className="section-top rehearsal-section-top">
                    <div><h3>REPERTÓRIO DO ENSAIO</h3><p className="muted">Acesse a cifra ou ouça cada música antes do ensaio.</p></div>
                    <span className="count">{current.setlist.length} músicas</span>
                  </div>
                  <div className="list">
                    {current.setlist.length ? current.setlist.map((song, i) => (
                      <div className="list-row" key={song.song_id}>
                        <span className="rehearsal-song-number">{i + 1}</span>
                        <div className="grow"><strong>{song.title}</strong><small>{song.artist}{song.tone ? ` · Tom ${song.tone}` : ""}</small></div>
                        <IconButton
                          icon={Music2}
                          label={"Ver cifra de " + song.title}
                          onClick={() => { setSongId(song.song_id); setTab("chords"); }}
                        />
                        <IconButton
                          icon={Play}
                          label={"Ouvir " + song.title}
                          onClick={() => setModal({ type: "youtube", value: { ...song, ...data.songs.find((x) => x.id === song.song_id) } })}
                        />
                      </div>
                    )) : <Empty>Sem repertório definido para esta escala.</Empty>}
                  </div>
                </section>
              </>
            ) : (
              <>
                <section className="card scale-card">'''
if needle not in s:
    raise SystemExit('Ponto de inserção da aba Ensaio não encontrado')
s = s.replace(needle, rehearsal_view, 1)

old_default = '''                    time: "",
                    rehearsal_time: "",
                    rehearsal_location: "",'''
new_default = '''                    time: "",
                    rehearsal_date: "",
                    rehearsal_time: "",
                    rehearsal_location: "",'''
if old_default not in s:
    raise SystemExit('Defaults de nova escala não encontrados')
s = s.replace(old_default, new_default, 1)

old_meta = '''                      {current.time && <span><Clock3 size={15}/>{current.time}</span>}
                      {current.rehearsal_location && <span><MapPin size={15}/>{current.rehearsal_location}</span>}'''
new_meta = '''                      {current.time && <span><Clock3 size={15}/>{current.time}</span>}
                      {current.rehearsal_time && <span><Clock3 size={15}/>Ensaio {current.rehearsal_time}</span>}
                      {current.rehearsal_location && <span><MapPin size={15}/>{current.rehearsal_location}</span>}'''
if old_meta not in s:
    raise SystemExit('Metadados do dashboard não encontrados')
s = s.replace(old_meta, new_meta, 1)

app.write_text(s)

u = utils.read_text()
old_scale_text = "export function scaleText(scale){const rehearsal=scale.rehearsal_time||scale.rehearsal_location?['','ENSAIO',scale.rehearsal_time?`Horário: ${scale.rehearsal_time}`:'',scale.rehearsal_location?`Local: ${scale.rehearsal_location}`:''].filter(Boolean):[];return [`🎵 Worship Flow`,`${scale.title} — ${dateLabel(scale.date)}${scale.time?' • '+scale.time:''}`,...rehearsal,'', 'EQUIPE',...scale.assignments.map(m=>`${m.member_name} — ${roleLabel(m)}`),'','REPERTÓRIO',...scale.setlist.map((s,i)=>`${i+1}. ${s.title} — ${s.artist}${s.tone?' (Tom: '+s.tone+')':''}`)].join('\\n');}"
new_scale_text = "export function scaleText(scale){const rehearsal=scale.rehearsal_date||scale.rehearsal_time||scale.rehearsal_location?['','ENSAIO',scale.rehearsal_date?`Data: ${dateLabel(scale.rehearsal_date)}`:'',scale.rehearsal_time?`Horário: ${scale.rehearsal_time}`:'',scale.rehearsal_location?`Local: ${scale.rehearsal_location}`:''].filter(Boolean):[];return [`🎵 Worship Flow`,`${scale.title} — ${dateLabel(scale.date)}${scale.time?' • '+scale.time:''}`,...rehearsal,'', 'EQUIPE',...scale.assignments.map(m=>`${m.member_name} — ${roleLabel(m)}`),'','REPERTÓRIO',...scale.setlist.map((s,i)=>`${i+1}. ${s.title} — ${s.artist}${s.tone?' (Tom: '+s.tone+')':''}`)].join('\\n');}"
if old_scale_text not in u:
    raise SystemExit('scaleText não encontrado em utils.js')
u = u.replace(old_scale_text, new_scale_text, 1)
u = u.replace("['title','date','time','rehearsal_time','rehearsal_location','status','created_date','updated_date']", "['title','date','time','rehearsal_date','rehearsal_time','rehearsal_location','status','created_date','updated_date']", 1)
utils.write_text(u)

css = style.read_text()
css = css.replace('.tabs button{width:50%;display:flex;', '.tabs button{flex:1;min-width:0;display:flex;', 1)
append = r'''

/* v55 — Escalas e Ensaios */
.rehearsal-editor-hint{margin:-10px 0 16px;font-size:10px}
.rehearsal-focus-card{position:relative;overflow:hidden;border-color:rgba(63,211,255,.24);background:linear-gradient(145deg,rgba(12,31,49,.98),rgba(20,18,51,.96))}
.rehearsal-focus-card::after{content:"";position:absolute;width:190px;height:190px;border-radius:50%;right:-70px;top:-80px;background:rgba(87,72,255,.2);filter:blur(30px);pointer-events:none}
.rehearsal-focus-head{position:relative;z-index:1;display:flex;align-items:flex-start;justify-content:space-between;gap:18px;margin-bottom:20px}
.rehearsal-focus-head h1{margin:12px 0 5px}.rehearsal-focus-head>svg{color:#60e5ff;opacity:.82}
.rehearsal-grid{position:relative;z-index:1;display:grid;grid-template-columns:1fr 1fr;gap:10px}
.rehearsal-detail{display:flex;align-items:center;gap:12px;min-height:82px;padding:14px;border:1px solid rgba(101,177,235,.14);border-radius:13px;background:rgba(7,20,34,.62)}
.rehearsal-detail>svg{color:#4bdcf5;flex:0 0 auto}.rehearsal-detail span{display:flex;flex-direction:column;gap:5px;min-width:0}.rehearsal-detail small{font-size:8px;letter-spacing:.8px;color:#7189a9;text-transform:uppercase}.rehearsal-detail strong{font-size:12px;line-height:1.45;overflow-wrap:anywhere}.rehearsal-location-detail{grid-column:1/-1}
.rehearsal-team-card .group:first-of-type{margin-top:16px}.rehearsal-section-top{margin-bottom:12px}.rehearsal-section-top h3{margin-bottom:4px}.rehearsal-section-top p{margin:0;font-size:10px}.rehearsal-song-number{width:30px;height:30px;display:grid;place-items:center;border-radius:9px;background:rgba(28,184,255,.1);color:#64e5ff;font:700 11px "Space Grotesk";flex:0 0 auto}
@media(max-width:600px){.tabs button{padding:11px 7px;font-size:10px}.rehearsal-grid{grid-template-columns:1fr}.rehearsal-location-detail{grid-column:auto}.rehearsal-focus-head h1{font-size:24px}.rehearsal-section-top{align-items:flex-start}.rehearsal-section-top .count{padding:7px 9px;font-size:9px}}
'''
if '/* v55 — Escalas e Ensaios */' not in css:
    css += append
style.write_text(css)

pkg = root / 'package.json'
ps = pkg.read_text()
ps = re.sub(r'"version"\s*:\s*"[^"]+"', '"version": "1.0.55"', ps, count=1)
pkg.write_text(ps)

print('Melhorias v55 de Escalas e Ensaios aplicadas.')
