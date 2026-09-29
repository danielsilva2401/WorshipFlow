from pathlib import Path
import json
import sys
import shutil

root = Path(sys.argv[1])
feature = Path(__file__).resolve().parent.parent / "features" / "pwa-smart-song-recommendations"
app = root / "src" / "App.jsx"
style = root / "src" / "style.css"

for name in ["SongRecommendations.jsx", "recommendations.js"]:
    shutil.copy(feature / name, root / "src" / name)

s = app.read_text()

if 'import SongRecommendations from "./SongRecommendations";' not in s:
    anchor = 'const empty = {'
    if anchor not in s:
        raise SystemExit("Anchor const empty não encontrado")
    s = s.replace(anchor, 'import SongRecommendations from "./SongRecommendations";\n\n' + anchor, 1)

panel = '''      <SongRecommendations
        songs={data.songs}
        scales={data.scales}
        referenceDate={v.date || localDate()}
        selectedIds={v.setlist.map((item) => item.song_id)}
        excludeScaleId={v.id || ""}
        onAdd={toggleSong}
      />
      <h3 className="spaced">MÚSICAS</h3>'''

if '<SongRecommendations' not in s:
    anchor = '      <h3 className="spaced">MÚSICAS</h3>'
    if anchor not in s:
        raise SystemExit("Anchor MÚSICAS do ScaleEditor não encontrado")
    s = s.replace(anchor, panel, 1)

app.write_text(s)

css = style.read_text()
marker = "/* PWA smart song recommendations */"
if marker not in css:
    css += r'''

/* PWA smart song recommendations */
.smart-song-suggestions{margin:22px 0 24px;padding:16px;border:1px solid rgba(66,205,255,.18);border-radius:18px;background:linear-gradient(145deg,rgba(16,35,53,.88),rgba(28,22,63,.78))}
.smart-song-head{display:flex;align-items:flex-start;gap:11px;margin-bottom:13px}.smart-song-head h3{margin:1px 0 5px}.smart-song-head p{margin:0;font-size:9px;line-height:1.5}.smart-song-icon{width:36px;height:36px;display:grid;place-items:center;flex:0 0 auto;border-radius:12px;background:rgba(86,210,255,.12);color:#69e8ff}
.smart-song-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.smart-song-card{display:flex;align-items:center;gap:12px;min-width:0;padding:12px;border:1px solid rgba(115,146,193,.13);border-radius:14px;background:rgba(7,18,32,.58)}.smart-song-card strong,.smart-song-card small{display:block}.smart-song-card strong{font-size:11px}.smart-song-card small{margin-top:3px;color:var(--muted);font-size:9px}.smart-song-reasons{display:flex;flex-wrap:wrap;gap:5px;margin-top:8px}.smart-song-reasons span{padding:4px 7px;border-radius:999px;background:rgba(93,91,255,.1);color:#aebcff;font-size:8px;line-height:1.2}.smart-song-add{display:flex;align-items:center;justify-content:center;gap:5px;flex:0 0 auto;padding:9px 10px;border:1px solid rgba(75,220,245,.22);border-radius:10px;background:rgba(38,196,229,.1);color:#6deaff;font:700 9px "Space Grotesk";cursor:pointer}.smart-song-add:hover{background:rgba(38,196,229,.17)}.smart-song-empty{margin:4px 0 0;font-size:9px}
html[data-theme="light"] .smart-song-suggestions{background:linear-gradient(145deg,#f7fcff,#f7f5ff);border-color:rgba(44,144,194,.16)}html[data-theme="light"] .smart-song-card{background:#fff}
@media(max-width:720px){.smart-song-suggestions{padding:13px;margin:18px 0 21px}.smart-song-grid{grid-template-columns:1fr}.smart-song-card{align-items:flex-start}.smart-song-add{min-height:38px}.smart-song-head .count{margin-left:auto}}
'''
    style.write_text(css)

pkg = root / "package.json"
data = json.loads(pkg.read_text())
data["version"] = "1.0.58-pwa.1"
pkg.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")

print("WorshipFlow PWA: sugestões inteligentes aplicadas.")
