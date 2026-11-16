"""Search a PBIX package for personal strings. Read-only."""
import sys
import zipfile
from pathlib import Path

PBIX = Path(sys.argv[1])
NEEDLES = ["Lowo", "EJERCICIO_POWER-BI", "steel-plates-quality-bi-main",
           "Downloads", "RutaCSV", "steel_plates_faults.csv", "C:\\Users"]

with zipfile.ZipFile(PBIX) as package:
    for entry in sorted(package.namelist()):
        data = package.read(entry)
        hits = {}
        for needle in NEEDLES:
            for label, encoded in (("utf8", needle.encode("utf-8")),
                                   ("utf16", needle.encode("utf-16-le"))):
                count = data.count(encoded)
                if count:
                    hits[f"{needle} [{label}]"] = count
        if hits:
            print(f"{entry}  ({len(data):,} bytes)")
            for key, count in hits.items():
                print(f"    {key}: {count}")

    print()
    print("=== contexto alrededor de la primera aparicion en DataModel ===")
    data = package.read("DataModel")
    for label, encoded in (("utf8", b"EJERCICIO_POWER-BI"),
                           ("utf16", "EJERCICIO_POWER-BI".encode("utf-16-le"))):
        index = data.find(encoded)
        if index == -1:
            print(f"  {label}: no aparece")
            continue
        chunk = data[max(0, index - 200):index + 200]
        text = chunk.decode("utf-16-le", "replace") if label == "utf16" else chunk.decode("utf-8", "replace")
        printable = "".join(c if c.isprintable() else "." for c in text)
        print(f"  {label} en offset {index}:")
        print(f"    {printable}")
