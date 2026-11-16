"""Update the commit hashes quoted in the dossier after an authorship rewrite.

Rewriting the author of a commit changes its hash, so every short hash cited in the
documents and scripts has to be remapped. Matching is anchored on word boundaries: a
7-character hex run sitting inside a 64-character SHA256 is surrounded by hex digits,
which are word characters, so it cannot match and the integrity manifests are safe.

Pass --apply to write; the default is a dry run.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

# old -> new, from the filter-branch run of 2026-11-15.
REMAP = {
    "1096d82": "be46d0c",
    "f03dc7b": "ea40f4a",
    "f675d06": "5583c8e",
    "1243900": "2ea038b",
    "57cc51b": "35e49f5",
    "ce92e38": "52f6d4f",
    "4be4af3": "ede9007",
    "b7b1d22": "1b4f70a",
    "1aa2697": "2c7ce67",
    "b1889a1": "d28c790",
    "b279464": "8487e0c",
    "71a59cb": "9003f01",
}
PATTERN = re.compile(r"\b(" + "|".join(REMAP) + r")\b")

apply = "--apply" in sys.argv
tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True,
                                  encoding="utf-8").splitlines()
total = 0
for name in tracked:
    path = ROOT / name
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue  # binary or unreadable: no hashes to remap
    if path.resolve() == Path(__file__).resolve():
        continue  # rewriting REMAP here would destroy the mapping
    replaced = PATTERN.sub(lambda m: REMAP[m.group(1)], text)
    if replaced == text:
        continue
    count = len(PATTERN.findall(text))
    total += count
    print(f"{count:>4}  {name}")
    if apply:
        path.write_text(replaced, encoding="utf-8")

print()
print(f"referencias remapeadas: {total}")
print("modo:", "APLICADO" if apply else "SECO (usa --apply)")
