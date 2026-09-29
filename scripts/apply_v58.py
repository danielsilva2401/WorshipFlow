from pathlib import Path
import sys, shutil, json
root = Path(sys.argv[1])
features = Path(__file__).resolve().parent.parent / 'features/song-suggestions'
p = root / 'src/App.jsx'
s = p.read_text()
if 'SongSuggestions from' in s:
    raise SystemExit('v58 already applied')
def replace(old, new):
    global s
    if old not in s: raise SystemExit('Missing anchor: '+old[:100])
    s = s.replace(old,new,1)
replace('const empty = {', 'import SongSuggestions from "./SongSuggestions";\nimport { suggestionPayload, suggestionNotifications } from "./suggestions";\nimport { serverTimestamp } from "firebase/firestore";\n\nconst empty = {')
replace('  const admin = access?', '  const [suggestions, setSuggestions] = useState([]);\n  const [suggestionsLoading, setSuggestionsLoading] = useState(false);\n  const [suggestionsError, setSuggestionsError] = useState("");\n  const admin = access?')
replace('  async function action(fn, success) {', '''  useEffect(() => {
    setSuggestions([]); setSuggestionsError("");
    if (demo || !access || access.status === "inactive" || !user?.emailVerified) { setSuggestionsLoading(false); return; }
    setSuggestionsLoading(true);
    const ref = collection(db, "songSuggestions");
    return onSnapshot(admin ? ref : query(ref, where("user_uid", "==", user.uid)), snapshot => {
      setSuggestions(snapshot.docs.map(d => ({...d.data(), id:d.id})).sort((a,b)=>(b.createdAt?.toMillis?.() || 0)-(a.createdAt?.toMillis?.() || 0)));
      setSuggestionsLoading(false);
    }, error => { setSuggestionsError(errorText(error)); setSuggestionsLoading(false); });
  }, [user?.uid, user?.emailVerified, access?.role, access?.status]);
  async function submitSuggestion(values) {
    const id = crypto.randomUUID();
    const payload = suggestionPayload(values, user, access, demo ? null : serverTimestamp());
    if (demo) setSuggestions(items => [{...payload,id},...items]);
    else await setDoc(doc(db, "songSuggestions", id), payload);
  }
  async function action(fn, success) {''')
replace('["home", "scales", "songs"].includes(page)', '["home", "scales", "songs", "suggestions"].includes(page)')
replace('...data.registrationRequests.filter', '...suggestions.map(s => `suggestion:${s.id}`),\n        ...data.registrationRequests.filter')
replace('...pending.map((r)', '...suggestionNotifications(suggestions),\n          ...pending.map((r)')
# Add navigation to both roles.
s=s.replace('["songs", "Repertório", Music2],','["songs", "Repertório", Music2],\n        ["suggestions", "Sugestões", Music2],')
replace('{page === "songs" && (', '{page === "suggestions" && <SongSuggestions admin={admin} user={user} access={access} items={suggestions} submit={submitSuggestion} loading={suggestionsLoading} loadError={suggestionsError} />}\n        {page === "songs" && (')
replace('else if (admin) setPage("admin");','else if (admin && n.type === "suggestion") setPage("suggestions");\n                    else if (admin) setPage("admin");')
s=s.replace('<nav className="mobile-nav">', '<nav className="mobile-nav" style={{gridTemplateColumns: `repeat(${navigation.length}, minmax(0, 1fr))`}}>')
p.write_text(s)
for name in ['SongSuggestions.jsx','suggestions.js']: shutil.copy(features/name,root/'src'/name)
with (root/'src/style.css').open('a') as f: f.write('\n.suggestions-page{max-width:850px;margin:auto}.suggestion-form{display:grid;gap:16px}.suggestion-form label{display:grid;gap:8px}.suggestion-form input,.suggestion-form textarea{width:100%;box-sizing:border-box}.suggestion-item{margin:12px 0;overflow-wrap:anywhere}.suggestion-note{white-space:pre-wrap}.mobile-nav{grid-template-columns:repeat(6,minmax(0,1fr))}.mobile-nav button{min-width:0}.mobile-nav span{font-size:10px}\n')
for script in ['v57-postinstall.mjs','v57-after-sync.mjs']:
    target=root/'scripts'/script
    target.write_text(target.read_text().replace('570','580').replace('1.0.57','1.0.58'))
pkg=root/'package.json'; data=json.loads(pkg.read_text()); data['version']='1.0.58'; pkg.write_text(json.dumps(data,indent=2)+'\n')
print('v58: sugestões e notificações aplicadas.')
