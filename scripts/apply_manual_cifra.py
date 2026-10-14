from pathlib import Path
import json
import re
import sys

root = Path(sys.argv[1])
app = root / "src" / "App.jsx"
style = root / "src" / "style.css"

s = app.read_text()

manual_viewer = r'''function ChordViewer({ song, admin, edit }) {
  const [steps, setSteps] = useState(0),
    [selectedChord, setSelectedChord] = useState(""),
    [capo, setCapo] = useState(Math.max(0, Math.min(12, Number(song?.cifra_capo || 0))));

  const sourceCapo = Math.max(0, Math.min(12, Number(song?.cifra_capo || 0))),
    tone = transposeTone(song.tone, steps),
    chordSteps = steps + sourceCapo - capo,
    chart = String(song.chords || song.cifra_club_chords || "").trim(),
    club = cifraClubUrl(song),
    clubSearch = cifraClubSearchUrl(song),
    isClubSearch = Boolean(club && clubSearch && club === clubSearch);

  useEffect(() => {
    setCapo(sourceCapo);
    setSteps(0);
  }, [song?.id, sourceCapo]);

  return (
    <>
      <div className="section-top">
        <div>
          <h2>{song.title}</h2>
          <p className="muted">
            {song.artist}
            {tone ? " · Tom: " + tone : ""}{sourceCapo ? ` · Capotraste original: ${sourceCapo}ª casa` : ""}
          </p>
        </div>
      </div>
      {chart ? (
        <>
          <div className="transpose">
            <button onClick={() => setSteps((v) => v - 1)} aria-label="Diminuir tom">−</button>
            <span>{steps === 0 ? "Tom original" : `${steps > 0 ? "+" : ""}${steps} semitom${Math.abs(steps) === 1 ? "" : "s"}`}</span>
            <button onClick={() => setSteps((v) => v + 1)} aria-label="Aumentar tom">+</button>
            <button className="reset" onClick={() => { setSteps(0); setCapo(sourceCapo); }}>Restaurar</button>
          </div>
          <div className="cifra-play-controls manual-cifra-controls">
            <div className="cifra-capo-control">
              <span className="cifra-control-label">Capotraste</span>
              <div className="cifra-capo-stepper">
                <button type="button" onClick={() => setCapo(v => Math.max(0, v - 1))} disabled={capo <= 0} aria-label="Diminuir casa do capotraste">−</button>
                <strong>{capo === 0 ? "Sem capotraste" : `${capo}ª casa`}</strong>
                <button type="button" onClick={() => setCapo(v => Math.min(12, v + 1))} disabled={capo >= 12} aria-label="Aumentar casa do capotraste">+</button>
              </div>
              {capo !== sourceCapo && <small>Os desenhos dos acordes foram ajustados para manter o mesmo tom da música.</small>}
            </div>
          </div>
          <div className="cifra-source-note cifra-saved-note">
            <Save size={16} />
            <span><strong>Cifra cadastrada no WorshipFlow</strong><small>A cifra é mantida manualmente no repertório. O WorshipFlow não faz busca automática de letra ou acordes.</small></span>
          </div>
          <InteractiveChordText text={chart} steps={chordSteps} onChord={setSelectedChord} automatic={false} />
        </>
      ) : (
        <Empty>
          Nenhuma cifra foi cadastrada para esta música. A cifra pode ser adicionada manualmente pelo administrador.
        </Empty>
      )}
      {club && (
        <a className="btn cifraclub" href={club} target="_blank" rel="noreferrer">
          <Music2 size={17} /> {isClubSearch ? "Pesquisar manualmente no Cifra Club" : "Abrir link do Cifra Club"} <ExternalLink size={14} />
        </a>
      )}
      <a className="btn secondary" href={cifraUrl(song)} target="_blank" rel="noreferrer">
        <Search size={17} /> Pesquisar manualmente na internet <ExternalLink size={14} />
      </a>
      {admin && (
        <Button className="secondary" icon={Pencil} onClick={edit}>
          Adicionar/editar cifra manualmente
        </Button>
      )}
      {selectedChord && <ChordDiagram chord={selectedChord} close={() => setSelectedChord("")} />}
    </>
  );
}'''

start = s.find("function ChordViewer(")
end = s.find("\nfunction YouTubePlayer", start)
if start < 0 or end < 0:
    raise SystemExit("ChordViewer não encontrado")
s = s[:start] + manual_viewer + s[end:]

# Remove importadores/alinhadores automáticos da tela de edição.
s = re.sub(
    r'\s*\[songSelectImport, setSongSelectImport\] = useState\(\{ type: "", message: "" \}\),\n'
    r'\s*\[lyricsDraft, setLyricsDraft\] = useState\(""\),\n'
    r'\s*\[lyricsAlignStatus, setLyricsAlignStatus\] = useState\(\{ type: "", message: "" \}\),\n'
    r'\s*\[lyricsAlignBusy, setLyricsAlignBusy\] = useState\(false\),',
    "",
    s,
    count=1,
)

helper_start = s.find("  const importChordPro = async (file) => {", s.find("function RecordForm"))
form_return = s.find("  return (\n    <form", helper_start)
if helper_start >= 0 and form_return >= 0:
    s = s[:helper_start] + s[form_return:]

s = s.replace(
    'if (type === "song") { result.chords = sanitizeCompleteCifraText(result.chords || ""); result = prepareCifraClubSong(result); }',
    'if (type === "song") result.chords = sanitizeCompleteCifraText(result.chords || "");',
)

song_start = s.find('{input("cifra_club_url", "Link exato do Cifra Club (opcional)"')
full_editor = s.find('          <div className="full-cifra-editor">', song_start)
if song_start >= 0 and full_editor >= 0:
    manual_chunk = r'''{input("cifra_club_url", "Link do Cifra Club (opcional)", {
            type: "url",
            placeholder: "Cole o link manualmente, se quiser",
          })}
          <div className="cifra-manual-box">
            <Pencil size={17} />
            <span>
              <strong>Cifra somente manual</strong>
              <small>O WorshipFlow não pesquisa nem preenche letra ou acordes automaticamente. Digite ou cole a cifra completa no campo abaixo.</small>
            </span>
          </div>
'''
    s = s[:song_start] + manual_chunk + s[full_editor:]

s = s.replace(
    "Esta versão fica permanente no repertório e tem prioridade sobre a busca automática.",
    "Esta versão fica permanente no repertório e é usada exatamente como foi cadastrada.",
)

# Cadastro/edição de música: salva apenas o que foi informado manualmente.
save_anchor = s.find('                  if (modal.type === "song") {')
save_end_token = '\n                    return;\n                  }'
save_end = s.find(save_end_token, save_anchor)
if save_anchor >= 0 and save_end >= 0:
    save_end += len(save_end_token)
    manual_save = r'''                  if (modal.type === "song") {
                    v.youtube_id = youtubeIdFromUrl(v.youtube_url);
                    v.chords = sanitizeCompleteCifraText(v.chords || "");
                    v.cifra_club_url = String(v.cifra_club_url || "").trim();
                    v.lyrics_search_status = "manual";
                    v.lyrics_search_url = "";
                    v.lyrics_searched_at = "";
                    v.cifra_club_chords = "";
                    v.cifra_line_map = [];
                    v.cifra_generated_simplified = false;
                    v.cifra_source_name = "";
                    v.cifra_source_url = "";

                    let initial = { ...v };
                    if (!initial.id) {
                      const existingSong = data.songs.find((item) => isSameSong(item, initial));
                      if (existingSong) initial = { ...existingSong, ...initial, id: existingSong.id };
                    }
                    const key = await save("songs", initial);
                    await collapseSongDuplicates(key, { ...initial, id: key });
                    if (modal.suggestionId) await reviewSongSuggestion(modal.suggestionId, "added", key);
                    setRuntimeSongs((current) => {
                      const next = { ...current };
                      delete next[key];
                      return next;
                    });
                    setModal(null);
                    setNotice(initial.chords?.trim() ? "Música e cifra salvas." : "Música cadastrada. A cifra pode ser adicionada manualmente quando quiser.");
                    return;
                  }'''
    s = s[:save_anchor] + manual_save + s[save_end:]

# Remove resolvedor automático que não deve mais ser chamado.
resolve_start = s.find("  async function resolveCifraForViewer(")
resolve_end = s.find("\n  async function remove(", resolve_start)
if resolve_start >= 0 and resolve_end >= 0:
    s = s[:resolve_start] + s[resolve_end:]

# Limpa props antigos nas duas telas que exibem a cifra.
s = re.sub(
    r'\n\s*saveCifra=\{persistCifra\}\n\s*autoLookup=\{resolveCifraForViewer\}',
    "",
    s,
)
s = s.replace(
    's.cifra_saved ? "Cifra salva" : s.cifra_club_chords ? "Acordes automáticos" : "Sem cifra salva"',
    's.cifra_saved || s.cifra_club_chords ? "Cifra salva" : "Sem cifra salva"',
)

# Remove imports que só existiam para a busca/alinhamento automático.
s = s.replace('import { isChordProText, parseChordPro } from "./chordpro";\n', "")
s = s.replace('import { alignLyricsWithChordChart, alignmentQuality, normalizeLyricsText } from "./lyricsAlign";\n', "")
s = s.replace('import { automaticLyricsSearchUrl } from "./internetLyrics";\n', "")
s = s.replace('import { resolveSongFromInternet } from "./autoSong";\n', "")
s = s.replace(
    'import { CIFRA_FORMAT_VERSION, cifraClubSearchUrl, cifraClubUrl, isIncompleteAutomaticCifra, lookupCifraClubSong, prepareCifraClubSong, sanitizeAutomaticChart, sanitizeCompleteCifraText } from "./cifraclub";',
    'import { cifraClubSearchUrl, cifraClubUrl, sanitizeAutomaticChart, sanitizeCompleteCifraText } from "./cifraclub";',
)

# YouTube continua automático, mas usa somente a chave própria do YouTube.
s = s.replace(
    'import.meta.env.VITE_YOUTUBE_API_KEY ||\n        import.meta.env.VITE_FIREBASE_API_KEY,',
    'import.meta.env.VITE_YOUTUBE_API_KEY,',
)

# Remove função de persistência de cifra automática, se tiver ficado sem uso.
persist_start = s.find("  async function persistCifra(activeSong) {")
persist_end = s.find("\n  async function remove(", persist_start)
if persist_start >= 0 and persist_end >= 0 and "persistCifra" not in s[persist_end:]:
    s = s[:persist_start] + s[persist_end:]

app.write_text(s)

css = style.read_text()
if ".cifra-manual-box" not in css:
    css += r'''
.cifra-manual-box{display:flex;gap:12px;align-items:flex-start;padding:14px;border:1px solid var(--line);border-radius:14px;background:rgba(80,110,150,.06);margin:4px 0 16px}.cifra-manual-box>svg{flex:0 0 auto;color:var(--cyan)}.cifra-manual-box span{display:flex;flex-direction:column;gap:4px}.cifra-manual-box strong{font-size:11px}.cifra-manual-box small{font-size:9px;color:var(--muted);line-height:1.5}.manual-cifra-controls{grid-template-columns:1fr}
'''
style.write_text(css)

pkg = root / "package.json"
data = json.loads(pkg.read_text())
data["version"] = "1.0.57.1"
pkg.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")

# Mantém a atualização instalável por cima da v57.
post = root / "scripts" / "v57-postinstall.mjs"
if post.exists():
    text = post.read_text().replace(": 570", ": 571").replace('"1.0.57"', '"1.0.57.1"').replace("WorshipFlow v57:", "WorshipFlow v57.1:")
    post.write_text(text)

after = root / "scripts" / "v57-after-sync.mjs"
if after.exists():
    text = after.read_text().replace("versionCode 570", "versionCode 571").replace('versionName "1.0.57"', 'versionName "1.0.57.1"').replace("WorshipFlow v57:", "WorshipFlow v57.1:")
    after.write_text(text)

print("WorshipFlow v57.1: cifra automática removida; fluxo manual aplicado.")
