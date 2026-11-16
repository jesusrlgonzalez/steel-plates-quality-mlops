"""Read-only inspection of a PBIX package: does it carry the five pages?

Opens the file as the OPC/ZIP package it is and never writes to it. This verifies
content; it does not and cannot create a PBIX.
"""
import json
import sys
import zipfile

path = sys.argv[1]

with zipfile.ZipFile(path) as package:
    names = package.namelist()
    print(f"entradas en el paquete: {len(names)}")
    for name in sorted(names):
        print(f"  {package.getinfo(name).file_size:>9,}  {name}")

    print()
    layout_name = next((n for n in names if n.lower().endswith("report/layout")), None)
    if not layout_name:
        print("No hay Report/Layout: el informe puede venir en formato PBIR.")
        pbir = [n for n in names if "/pages/" in n.lower()]
        print(f"entradas con /pages/: {len(pbir)}")
        sys.exit(0)

    # Report/Layout is UTF-16 JSON in every PBIX Desktop writes.
    layout = json.loads(package.read(layout_name).decode("utf-16-le").lstrip("﻿"))

sections = layout.get("sections", [])
print(f"paginas en el PBIX: {len(sections)}")
print()
for index, section in enumerate(sections, 1):
    visuals = section.get("visualContainers", [])
    kinds = {}
    for container in visuals:
        try:
            config = json.loads(container["config"])
            kind = config.get("singleVisual", {}).get("visualType", "?")
        except (KeyError, ValueError):
            kind = "?"
        kinds[kind] = kinds.get(kind, 0) + 1
    print(f"{index}. {section.get('displayName')!r}")
    print(f"   name={section.get('name')}  {section.get('width')}x{section.get('height')}  "
          f"visuales={len(visuals)}")
    print(f"   tipos={kinds}")
