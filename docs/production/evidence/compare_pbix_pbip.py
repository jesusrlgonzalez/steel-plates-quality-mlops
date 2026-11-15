"""Compare the report layer inside the PBIX against the PBIP on disk (read-only)."""
import json
import zipfile
from pathlib import Path

# docs/production/evidence/<this file> -> repository root
ROOT = Path(__file__).resolve().parents[3]
PBIX = ROOT / "powerbi/artifacts/steel-plates-quality-mlops-powerbi.pbix"
PBIP_REPORT = ROOT / "powerbi/project/steel-plates-quality-mlops-powerbi.Report/definition"

with zipfile.ZipFile(PBIX) as package:
    pbix_pages = json.loads(package.read("Report/definition/pages/pages.json").decode("utf-8-sig"))
    pbix_entries = package.namelist()
    # Report/definition/pages/<page>/visuals/<id>/visual.json
    page_visuals = {}
    for name in pbix_entries:
        parts = name.split("/")
        if len(parts) > 6 and parts[2] == "pages" and parts[4] == "visuals":
            page_visuals.setdefault(parts[3], set()).add(parts[5])
    pbix_display = {}
    for page in pbix_pages["pageOrder"]:
        meta = json.loads(package.read(
            f"Report/definition/pages/{page}/page.json").decode("utf-8-sig"))
        pbix_display[page] = (meta.get("displayName"), meta.get("width"), meta.get("height"))

disk_pages = json.loads((PBIP_REPORT / "pages/pages.json").read_text(encoding="utf-8-sig"))

print("=== pages.json ===")
print(f"PBIX  pageOrder      : {pbix_pages['pageOrder']}")
print(f"PBIP  pageOrder      : {disk_pages['pageOrder']}")
print(f"orden identico       : {pbix_pages['pageOrder'] == disk_pages['pageOrder']}")
print(f"PBIX  activePageName : {pbix_pages.get('activePageName')}")
print(f"PBIP  activePageName : {disk_pages.get('activePageName')}")
print()
print("=== paginas y visuales en el PBIX ===")
for page in pbix_pages["pageOrder"]:
    name, width, height = pbix_display[page]
    disk = {p.name for p in (PBIP_REPORT / "pages" / page / "visuals").iterdir()}
    pbix = page_visuals.get(page, set())
    print(f"{name!r:34} {width}x{height}")
    print(f"   visuales PBIX={len(pbix):2}  PBIP={len(disk):2}  identicos={pbix == disk}")
    if pbix != disk:
        print(f"   solo PBIX: {sorted(pbix - disk)}")
        print(f"   solo PBIP: {sorted(disk - pbix)}")
