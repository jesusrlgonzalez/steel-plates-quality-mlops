"""Generalise personal paths in the production dossier.

Two passes:
  1. Inside command blocks, the repository root becomes <REPO> so the commands are
     copy-pasteable on any checkout.
  2. Everywhere else, the account name becomes <USUARIO>.

Two things are left literal on purpose, because generalising them would make the
document state something false:
  - the line that declares what RutaCSV actually holds in the published PBIP;
  - the original author's `Downloads\\steel-plates-quality-bi-main` path, which the
    frozen baseline hash reconstruction depends on byte for byte.

The account name and repository root are arguments, so this file carries no personal
string of its own. Pass --apply to write; the default is a dry run.

    python -B docs/production/evidence/scrub_docs.py --account <nombre> --root <ruta>
"""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
# A line declaring the real value, or reconstructing the frozen baseline, stays as is.
KEEP_IF = ("expression RutaCSV = ", "RUTA_CSV_", "steel-plates-quality-bi-main")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--account", required=True, help="Windows account name to mask")
parser.add_argument("--root", required=True, help="absolute repository root to mask")
parser.add_argument("--apply", action="store_true", help="write the changes")
args = parser.parse_args()

account = f"C:\\Users\\{args.account}"
repo_subs = account_subs = kept = 0
touched = {}

for path in sorted((ROOT / "docs/production").rglob("*")):
    if path.is_dir() or path.suffix.lower() not in (".md", ".py", ".ps1"):
        continue
    if path.resolve() == Path(__file__).resolve():
        continue
    original = path.read_text(encoding="utf-8")
    lines = original.split("\n")
    fence = False
    for index, line in enumerate(lines):
        if path.suffix.lower() == ".md" and line.strip().startswith("```"):
            fence = not fence
            continue
        if args.account not in line:
            continue
        if any(token in line for token in KEEP_IF):
            kept += line.count(args.account)
            continue
        new = line
        if args.root in new and (fence or path.suffix.lower() != ".md"):
            repo_subs += new.count(args.root)
            new = new.replace(args.root, "<REPO>")
        if account in new:
            account_subs += new.count(account)
            new = new.replace(account, "C:\\Users\\<USUARIO>")
        # Also catch bare uses such as the pytest temp directory name.
        if args.account in new:
            account_subs += new.count(args.account)
            new = new.replace(args.account, "<USUARIO>")
        lines[index] = new
    result = "\n".join(lines)
    if result != original:
        touched[path.relative_to(ROOT).as_posix()] = (
            original.count(args.account) - result.count(args.account))
        if args.apply:
            path.write_text(result, encoding="utf-8")

for name, removed in sorted(touched.items(), key=lambda e: -e[1]):
    print(f"{removed:>4}  {name}")
print()
print(f"raiz del repo -> <REPO>            : {repo_subs}")
print(f"cuenta -> <USUARIO>                 : {account_subs}")
print(f"conservadas (valor real/historico)  : {kept}")
print("modo:", "APLICADO" if args.apply else "SECO (usa --apply)")
