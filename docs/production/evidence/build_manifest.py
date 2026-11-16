"""Write the post-rename SHA256 manifest from the Git index."""
import hashlib
import json
from pathlib import Path
import subprocess

# docs/production/evidence/<this file> -> repository root
ROOT = Path(__file__).resolve().parents[3]
SELF = "docs/production/evidence/powerbi_rename_post_inventory.json"

tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
entries = []
for name in sorted(n for n in tracked if n and n != SELF):
    data = (ROOT / name).read_bytes()
    entries.append(dict(path=name, size=len(data), sha256=hashlib.sha256(data).hexdigest()))

(ROOT / SELF).write_text(json.dumps(dict(
    note=("Post-rename SHA256 manifest (OWNER-PBI-REN-001). Excludes itself; "
          "see POWERBI_RELEASE_MANIFEST.md."),
    files=entries), indent=2) + "\n", encoding="utf-8")
print(f"files in manifest: {len(entries)}")
