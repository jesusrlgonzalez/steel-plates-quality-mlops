"""Separate real content changes from pure line-ending churn after a Desktop save.

The preservation test normalises CRLF to LF before hashing, so a file whose only
change is the line ending is invisible to it. This reports the two groups apart.
"""
import hashlib
import subprocess
from pathlib import Path

# docs/production/evidence/<this file> -> repository root
ROOT = Path(__file__).resolve().parents[3]


def run(*args):
    return subprocess.run(args, cwd=ROOT, capture_output=True)


changed = [line[3:] for line in run("git", "status", "--porcelain").stdout
           .decode("utf-8", "replace").splitlines() if line.startswith(" M")]

eol_only, real = [], []
for name in changed:
    head = run("git", "show", f"HEAD:{name}").stdout
    disk = (ROOT / name).read_bytes()
    if hashlib.sha256(head).hexdigest() == hashlib.sha256(disk).hexdigest():
        continue
    normalise = lambda data: data.replace(b"\r\n", b"\n")
    if hashlib.sha256(normalise(head)).hexdigest() == hashlib.sha256(normalise(disk)).hexdigest():
        eol_only.append(name)
    else:
        real.append((name, len(head), len(disk)))

print(f"archivos modificados: {len(changed)}")
print(f"  solo finales de linea (invisibles para la prueba de hash): {len(eol_only)}")
print(f"  con cambio real de contenido: {len(real)}")
print()
print("=== CAMBIO REAL DE CONTENIDO ===")
for name, before, after in real:
    print(f"  {before:>7} -> {after:>7} B   {name}")
print()
print("=== SOLO FINALES DE LINEA ===")
for name in eol_only:
    print(f"  {name}")
