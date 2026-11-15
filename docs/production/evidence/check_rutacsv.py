"""Reproduce the RutaCSV / RutaMLCSV resolution exactly as Power Query would.

Shows why a doubled path separator breaks the holdout table: File.Contents survives
repeated separators because Windows collapses them, but Text.Replace then yields
"//data//raw//" and the Text.Contains guard in RutaMLCSV fails, so ML_Holdout never
loads. TMDL stores M verbatim and does not escape the backslash, which is what makes
the doubled form a real pair of characters rather than an escape.

The current value is read from the semantic model, so this script carries no
hardcoded path and always reflects what the project actually holds.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXPRESSIONS = (ROOT / "powerbi/project/steel-plates-quality-mlops-powerbi.SemanticModel"
                      "/definition/expressions.tmdl")
BS = chr(92)  # backslash

found = re.search(r'expression RutaCSV = "([^"]+)"',
                  EXPRESSIONS.read_text(encoding="utf-8"))
if not found:
    raise SystemExit(f"No se encontro la expresion RutaCSV en {EXPRESSIONS}")

current = found.group(1)
single = current.replace(BS * 2, BS)
doubled = single.replace(BS, BS * 2)

print(f"RutaCSV en el modelo: {current}")
print(f"separador doblado   : {'si' if BS * 2 in current else 'no'}")
print()

for label, value in (("doblado", doubled), ("simple", single)):
    print(f"--- separador {label}")
    print(f"  valor literal M     : {value}")
    print(f"  File.Contents abre  : {Path(value).exists()}")
    normalised = value.strip().replace(BS, "/")
    print(f"  Text.Replace ->     : {normalised}")
    resolves = "/data/raw/" in normalised
    print(f"  Text.Contains '/data/raw/': {resolves}")
    if resolves:
        result = normalised.split("/data/raw/")[0] + "/powerbi/data/ml_holdout_evaluation.csv"
        print(f"  RutaMLCSV           : {result}")
        print(f"  File.Contents abre  : {Path(result).exists()}")
    else:
        print('  RutaMLCSV           : error "Set RutaCSV to this repository '
              'data/raw/steel_plates_faults.csv"  <-- ML_Holdout NO CARGA')
    print()
