"""Inventory personal and sensitive strings across every tracked file.

The account name is an argument, so this script carries no personal string of its own.

    python -B docs/production/evidence/audit_repo_leaks.py --account <nombre>
"""
import argparse
import re
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--account", help="Windows account name to look for")
args = parser.parse_args()

PATTERNS = {
    "ruta personal": re.compile(rb"C:[\\/]+Users[\\/]+", re.I),
    "carpeta del ejercicio": re.compile(rb"EJERCICIO_POWER-BI", re.I),
    "Downloads": re.compile(rb"Downloads[\\/]", re.I),
    "posible secreto": re.compile(
        rb"(api[_-]?key|secret|password|passwd|token|bearer\s|private[_-]key)", re.I),
    "correo": re.compile(rb"[\w.+-]+@[\w-]+\.[\w.]+"),
}
if args.account:
    PATTERNS["nombre de cuenta"] = re.compile(
        re.escape(args.account).encode("utf-8"), re.I)

tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True,
                                  encoding="utf-8").splitlines()

by_pattern = defaultdict(list)
for name in tracked:
    path = ROOT / name
    try:
        data = path.read_bytes()
    except OSError:
        continue
    for label, pattern in PATTERNS.items():
        hits = pattern.findall(data)
        if hits:
            by_pattern[label].append((name, len(hits)))

for label in PATTERNS:
    entries = by_pattern.get(label, [])
    total = sum(count for _, count in entries)
    print(f"=== {label}: {total} apariciones en {len(entries)} archivos")
    for name, count in sorted(entries, key=lambda e: -e[1])[:18]:
        print(f"    {count:>4}  {name}")
    if len(entries) > 18:
        print(f"    ... y {len(entries) - 18} archivos mas")
    print()

print("=== correos distintos encontrados ===")
emails = set()
for name, _ in by_pattern.get("correo", []):
    emails.update(m.decode("utf-8", "replace")
                  for m in PATTERNS["correo"].findall((ROOT / name).read_bytes()))
for value in sorted(emails):
    print(f"    {value}")

print()
print("=== autores de los commits ===")
print(subprocess.check_output(["git", "log", "--all", "--format=%an <%ae>"], cwd=ROOT,
                              text=True, encoding="utf-8").strip().splitlines()
      and "\n".join(sorted(set(subprocess.check_output(
          ["git", "log", "--all", "--format=%an <%ae>"], cwd=ROOT, text=True,
          encoding="utf-8").strip().splitlines()))))
