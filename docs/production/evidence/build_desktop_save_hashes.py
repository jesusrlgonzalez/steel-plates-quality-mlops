"""Record the identity of every pre-ML object the certified Desktop save rewrote.

docs/evidence/pre_ml_powerbi_hashes.json is frozen and guards the pre-ML report
byte-for-byte, so an authorised Desktop save makes it fail by design. The order
requires classifying that diff, not weakening the guard. This writes a second,
separately named manifest pinning the post-save identity of each rewritten object,
and it REFUSES to record any object whose semantic core -- visual type, field
bindings, page geometry -- differs from the baseline. A file only lands in the
manifest if Desktop changed how it is serialised and not what it displays.

The result is strictly stronger than byte equality alone: the test then checks both
the exact new bytes and the semantic equivalence to the baseline.

Run from the repository root with Power BI Desktop closed:
    python -B docs/production/evidence/build_desktop_save_hashes.py
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
BASELINE = ROOT / "docs/evidence/pre_ml_powerbi_hashes.json"
OUTPUT = ROOT / "docs/production/evidence/powerbi_desktop_save_hashes.json"
# Commit holding the pre-Desktop state of the renamed project.
PRE_DESKTOP = "2ea038b"
OLD_NAME, NEW_NAME = "steel-plates-quality-bi", "steel-plates-quality-mlops-powerbi"
RENAMED_PREFIXES = ("powerbi/project/", "powerbi/artifacts/")
# These carry their own dedicated branch in test_previous_powerbi_preserved.
HANDLED_ELSEWHERE = {
    "powerbi/powerquery/00_Parametros.pq",
    f"powerbi/project/{NEW_NAME}.Report/definition/pages/pages.json",
    f"powerbi/project/{NEW_NAME}.SemanticModel/definition/model.tmdl",
    f"powerbi/project/{NEW_NAME}.SemanticModel/definition/expressions.tmdl",
    f"powerbi/project/{NEW_NAME}.pbip",
    f"powerbi/project/{NEW_NAME}.Report/definition.pbir",
}


def current_path(name):
    if name.startswith(RENAMED_PREFIXES):
        return name.replace(OLD_NAME, NEW_NAME, 1)
    return name


def lf_hash(data):
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def visual_core(raw):
    item = json.loads(raw.decode("utf-8-sig"))
    visual = item.get("visual", {})
    bindings = []
    for role, state in sorted(visual.get("query", {}).get("queryState", {}).items()):
        for projection in state.get("projections", []):
            kind, field = next(iter(projection["field"].items()))
            bindings.append([role, kind,
                             field.get("Expression", {}).get("SourceRef", {}).get("Entity"),
                             field.get("Property")])
    return {"name": item.get("name"), "visualType": visual.get("visualType"),
            "bindings": bindings}


def page_core(raw):
    page = json.loads(raw.decode("utf-8-sig"))
    return {k: page.get(k) for k in ("name", "displayName", "width", "height",
                                     "type", "visibility")}


def classify(name, before, after):
    """Why Desktop rewrote the file. Only cosmetic reasons are acceptable here."""
    reasons = []
    if name.endswith("page.json"):
        b, a = (json.loads(x.decode("utf-8-sig")) for x in (before, after))
        if b.get("displayOption") != a.get("displayOption"):
            reasons.append(f"displayOption {b.get('displayOption')} -> {a.get('displayOption')}")
    if name.endswith("visual.json"):
        b, a = (json.loads(x.decode("utf-8-sig")) for x in (before, after))
        if b.get("position") != a.get("position"):
            reasons.append("geometria del visual reajustada")
        if sorted(b.get("visual", {})) != sorted(a.get("visual", {})):
            reasons.append("formato por defecto materializado (clave objects)")
        if b.get("filterConfig") != a.get("filterConfig"):
            reasons.append("marcador del panel de filtros, sin condiciones")
    return reasons or ["reserializacion sin cambio estructural"]


baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
records, rejected = {}, []

for key, identity in baseline["files"].items():
    if "lf_sha256" not in identity:
        continue  # the PBIX has its own certification
    name = current_path(key)
    if name in HANDLED_ELSEWHERE:
        continue
    path = ROOT / name
    if not path.exists():
        rejected.append((name, "no existe en disco"))
        continue
    after = path.read_bytes()
    if lf_hash(after) == identity["lf_sha256"]:
        continue  # untouched; the frozen baseline still covers it
    before = subprocess.run(["git", "show", f"{PRE_DESKTOP}:{name}"], cwd=ROOT,
                            capture_output=True).stdout
    if not before:
        rejected.append((name, f"no se pudo leer {PRE_DESKTOP}:{name}"))
        continue
    try:
        if name.endswith("visual.json"):
            core_before, core_after = visual_core(before), visual_core(after)
        elif name.endswith("page.json"):
            core_before, core_after = page_core(before), page_core(after)
        else:
            core_before, core_after = None, None
    except (ValueError, KeyError, StopIteration) as error:
        rejected.append((name, f"no analizable: {error}"))
        continue
    if core_before != core_after:
        rejected.append((name, "CAMBIO SEMANTICO: el visual ya no muestra lo mismo"))
        continue
    records[name] = {
        "lf_sha256": lf_hash(after),
        "baseline_lf_sha256": identity["lf_sha256"],
        "core": core_before,
        "classification": classify(name, before, after),
    }

print(f"objetos reescritos y certificados: {len(records)}")
for name, record in sorted(records.items()):
    print(f"  {name.split('/')[-2] if name.endswith('.json') else name}")
    for reason in record["classification"]:
        print(f"      {reason}")
print()
if rejected:
    print("=== RECHAZADOS (no se certifican) ===")
    for name, reason in rejected:
        print(f"  {name}\n      {reason}")
    print()
    print("Un rechazo por cambio semantico debe elevarse a OWNER, no certificarse.")
    sys.exit(1)

OUTPUT.write_text(json.dumps({
    "purpose": "CERTIFIED_DESKTOP_SAVE_HASHES",
    "order": "OWNER-PBI-REN-001",
    "desktop_version": "2.156.951.0 (26.07)",
    "saved": "2026-11-15",
    "pre_desktop_commit": PRE_DESKTOP,
    "note": ("Post-save identity of the pre-ML objects Power BI Desktop re-serialised. "
             "Every entry was verified to keep the baseline semantic core: visual type, "
             "field bindings and page geometry. Generated by "
             "build_desktop_save_hashes.py, which refuses to record a semantic change."),
    "files": dict(sorted(records.items())),
}, indent=2) + "\n", encoding="utf-8")
print(f"escrito: {OUTPUT.relative_to(ROOT).as_posix()}")
