from pathlib import Path
import os
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else os.environ["APP_DIR"])
app = root / "src" / "App.jsx"
s = app.read_text()

# O pacote reconstruído pode já conter as melhorias da v54.
# Nesse caso, não aplica o mesmo patch pela segunda vez.
already_v54 = (
    '[lookupError, setLookupError] = useState("")' in s
    and '[lookupAttempt, setLookupAttempt] = useState(0)' in s
    and 'Tempo limite da busca atingido.' in s
    and 'Tentando uma rota alternativa de acordes.' in s
)
if already_v54:
    cifra = root / "src" / "cifraclub.js"
    c = cifra.read_text()
    if "v54: consulta as fontes principais em paralelo" not in c and "v54: fontes principais em paralelo" not in c:
        raise SystemExit("App.jsx já está em v54, mas cifraclub.js não contém o resolvedor v54")

    pkg = root / "package.json"
    ps = pkg.read_text()
    ps = re.sub(r'"version"\s*:\s*"[^"]+"', '"version": "1.0.54"', ps, count=1)
    pkg.write_text(ps)

    cap = root / "capacitor.config.json"
    cfg = cap.read_text().replace('"skipNativeAuth": true', '"skipNativeAuth": false')
    cap.write_text(cfg)

    print("Melhorias v54 já presentes no fonte reconstruído. Validação concluída.")
    raise SystemExit(0)

s, n = re.subn(
    r'\[lookingUp,\s*setLookingUp\]\s*=\s*useState\(false\),\s*\n\s*\[savingCifra,\s*setSavingCifra\]\s*=\s*useState\(false\),',
    '[lookingUp, setLookingUp] = useState(false),\n    [lookupError, setLookupError] = useState(""),\n    [lookupAttempt, setLookupAttempt] = useState(0),\n    [savingCifra, setSavingCifra] = useState(false),',
    s,
    count=1,
)
if n != 1:
    raise SystemExit("Estado lookingUp da cifra não encontrado")

pattern = re.compile(
    r'setLookingUp\(!hasSavedChartForVariant\);\s*\n\s*\(async \(\) => \{.*?\}\)\(\)\.finally\(\(\) => \{\s*if \(active\) \{\s*setLookingUp\(false\);\s*\}\s*\}\);',
    re.S,
)
new_lookup = """setLookingUp(!hasSavedChartForVariant);
    setLookupError("");
    setLookupAttempt(0);

    const withTimeout = (promise, ms) => Promise.race([
      promise,
      new Promise((_, reject) => setTimeout(() => reject(new Error("Tempo limite da busca atingido.")), ms)),
    ]);

    (async () => {
      let current = song;
      const attempts = hasSavedChartForVariant ? 1 : 2;
      let lastError = null;
      for (let attempt = 0; attempt < attempts && active; attempt += 1) {
        setLookupAttempt(attempt + 1);
        try {
          const next = await withTimeout(autoLookup(current, {
            force: !hasSavedChartForVariant,
            variant,
            lyricsTimeoutMs: hasSavedChartForVariant ? 3500 : 5200,
          }), hasSavedChartForVariant ? 5500 : 9000);
          if (!active) return;
          if (next) {
            current = next;
            setResolvedSong(next);
            if (hasSavedChartForVariant || hasUsableChords(next)) {
              setLookupError("");
              return;
            }
          }
        } catch (error) {
          lastError = error;
          console.warn(`Tentativa ${attempt + 1} de cifra não concluiu:`, error);
        }
        if (attempt < attempts - 1 && active) await wait(900);
      }
      if (active && !hasSavedChartForVariant && !hasUsableChords(current)) {
        setLookupError(lastError?.message || "Não encontramos acordes automaticamente agora.");
      }
    })().finally(() => {
      if (active) {
        setLookingUp(false);
        setLookupAttempt(0);
      }
    });"""
s, n = pattern.subn(new_lookup, s, count=1)
if n != 1:
    raise SystemExit("Rotina assíncrona da cifra não encontrada")

old_status = '<span><strong>Buscando letra + cifra automaticamente…</strong><small>Localizando a letra, identificando o título correto e preparando os acordes para o WorshipFlow.</small></span>'
new_status = '<span><strong>Buscando letra + cifra automaticamente…</strong><small>{lookupAttempt > 1 ? "Tentando uma rota alternativa de acordes. Isso leva só mais alguns segundos." : "Consultando as fontes disponíveis em paralelo e preparando os acordes para o WorshipFlow."}</small></span>'
if old_status not in s:
    raise SystemExit("Texto de carregamento da cifra não encontrado")
s = s.replace(old_status, new_status, 1)

retry_pattern = re.compile(
    r'\{!lookingUp\s*&&\s*transientInternetLyrics\s*&&\s*activeSong\.lyrics_runtime_kind\s*!==\s*"lyrics\+chords"\s*&&\s*\(\s*<Button className="secondary wide" icon=\{RefreshCw\} onClick=\{\(\) => setLookupNonce\(\(value\) => value \+ 1\)\}>\s*Tentar buscar acordes novamente\s*</Button>\s*\)\}',
    re.S,
)
new_retry = """{!lookingUp && lookupError && !chart && (
        <div className="cifra-source-note cifra-lookup-error">
          <RefreshCw size={16} />
          <span><strong>A busca automática não concluiu</strong><small>{lookupError} Você pode tentar novamente agora ou abrir a busca do Cifra Club abaixo.</small></span>
        </div>
      )}
      {!lookingUp && ((transientInternetLyrics && activeSong.lyrics_runtime_kind !== "lyrics+chords") || (lookupError && !chart)) && (
        <Button className="secondary wide" icon={RefreshCw} onClick={() => { setLookupError(""); setLookupNonce((value) => value + 1); }}>
          Tentar buscar acordes novamente
        </Button>
      )}"""
s, n = retry_pattern.subn(new_retry, s, count=1)
if n != 1:
    raise SystemExit("Botão de retry da cifra não encontrado")

s = s.replace(
    'setVariant("simplified");\n                if (!song.chords)',
    'setVariant("simplified");\n                setLookupError("");\n                if (!song.chords)',
    1,
)
s = s.replace(
    'setVariant("principal");\n                if (!song.chords)',
    'setVariant("principal");\n                setLookupError("");\n                if (!song.chords)',
    1,
)
app.write_text(s)

cifra = root / "src" / "cifraclub.js"
c = cifra.read_text()
lookup_pattern = re.compile(
    r'// v44: primeiro usa o Cloudflare Worker gratuito\..*?if\(!found\) found=await tryRawProxyPages\(base,fetcher,Math\.min\(timeoutMs,6000\)\);',
    re.S,
)
new_resolver = """// v54: fontes principais em paralelo para não prender a interface numa fonte lenta.
            const primary=await Promise.allSettled([
              tryCloudflareBackend(base,fetcher,Math.min(timeoutMs,8000),requestedVariant),
              tryReader(base,fetcher,Math.min(timeoutMs,7000)),
              tryRecifraReader(base,fetcher,Math.min(timeoutMs,7000)),
            ]);
            const primaryResults=primary
              .filter(item=>item.status==='fulfilled' && item.value)
              .map(item=>item.value)
              .sort((a,b)=>cifraCompletenessScore(b)-cifraCompletenessScore(a));
            let found=primaryResults[0] || null;
            if(!found) found=await tryLegacyApi(base,fetcher,Math.min(timeoutMs,3500));
            if(!found) found=await tryRawProxyPages(base,fetcher,Math.min(timeoutMs,4500));"""
c, n = lookup_pattern.subn(new_resolver, c, count=1)
if n != 1:
    raise SystemExit("Resolvedor Cifra Club não encontrado")
cifra.write_text(c)

css = root / "src" / "style.css"
cs = css.read_text()
if ".cifra-lookup-error" not in cs:
    cs += '\n.cifra-lookup-error{border-color:rgba(255,168,76,.28);background:rgba(255,168,76,.08)}.cifra-lookup-error>svg{color:#ffb35c}html[data-theme="light"] .cifra-lookup-error{background:#fff7ed;border-color:rgba(234,88,12,.2)}\n'
css.write_text(cs)

pkg = root / "package.json"
ps = pkg.read_text()
ps = re.sub(r'"version"\s*:\s*"[^"]+"', '"version": "1.0.54"', ps, count=1)
pkg.write_text(ps)

cap = root / "capacitor.config.json"
cfg = cap.read_text().replace('"skipNativeAuth": true', '"skipNativeAuth": false')
cap.write_text(cfg)

print("Melhorias v54 aplicadas com sucesso.")
