import base64,zlib
exec(compile(zlib.decompress(base64.b64decode("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")), "<apply_v57>", "exec"))

from pathlib import Path
import json

root = Path(sys.argv[1])
post = root / "scripts" / "v57-postinstall.mjs"
post.parent.mkdir(parents=True, exist_ok=True)
post.write_text(r'''import { readdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

const roots = ["node_modules/@capacitor/cli", "node_modules/@capacitor/android"];
let changed = 0;

async function walk(dir) {
  let entries = [];
  try { entries = await readdir(dir, { withFileTypes: true }); } catch { return; }
  for (const entry of entries) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      await walk(full);
      continue;
    }
    if (entry.name !== "build.gradle") continue;
    let text = "";
    try { text = await readFile(full, "utf8"); } catch { continue; }
    if (!text.includes("versionCode") || !text.includes("versionName")) continue;
    const next = text
      .replace(/versionCode\s+\d+/, 'versionCode project.hasProperty("WF_VERSION_CODE") ? project.property("WF_VERSION_CODE").toInteger() : 570')
      .replace(/versionName\s+"[^"]+"/, 'versionName project.hasProperty("WF_VERSION_NAME") ? project.property("WF_VERSION_NAME") : "1.0.57"');
    if (next !== text) {
      await writeFile(full, next);
      changed++;
    }
  }
}

for (const root of roots) await walk(root);
console.log("WorshipFlow v57: templates Android preparados:", changed);
if (!changed) console.warn("WorshipFlow v57: nenhum template Android precisou de ajuste.");
''')

pkg = root / "package.json"
data = json.loads(pkg.read_text())
data.setdefault("scripts", {})["postinstall"] = "node scripts/v57-postinstall.mjs"
data["version"] = "1.0.57"
pkg.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
print("WorshipFlow v57: versionamento Android preparado.")

after_sync = root / "scripts" / "v57-after-sync.mjs"
after_sync.write_text(r'''import { readFile, writeFile } from "node:fs/promises";

const path = "android/app/build.gradle";
let text = await readFile(path, "utf8");
text = text
  .replace(/versionCode\s+[^\n]+/, "versionCode 570")
  .replace(/versionName\s+[^\n]+/, 'versionName "1.0.57"');
await writeFile(path, text);
console.log("WorshipFlow v57: Android definido como versionCode 570 / versionName 1.0.57");
''')

data = json.loads(pkg.read_text())
data.setdefault("scripts", {})["capacitor:update:after"] = "node scripts/v57-after-sync.mjs"
data.setdefault("scripts", {})["capacitor:sync:after"] = "node scripts/v57-after-sync.mjs"
data["version"] = "1.0.57"
pkg.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
print("WorshipFlow v57: hooks pós-sync configurados.")
