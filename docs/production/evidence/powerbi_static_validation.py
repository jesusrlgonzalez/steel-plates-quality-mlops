"""Static validation of the renamed Power BI project (OWNER-PBI-REN-001, Fases 3-6).

Checks everything that is decidable from the PBIP sources, the two CSVs and the
frozen evidence, without Power BI Desktop. It never writes and never recomputes a
frozen metric: expectations are read from the committed evidence files.

Desktop runtime behaviour (render, refresh, save) is out of scope by construction;
see POWERBI_PBIP_PBIX_INTEGRITY.md.

Usage:  python -B docs/production/evidence/powerbi_static_validation.py
Exit 0 = every check passed.
"""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "powerbi/project/steel-plates-quality-mlops-powerbi"
REPORT = PROJECT.with_name(PROJECT.name + ".Report")
MODEL = PROJECT.with_name(PROJECT.name + ".SemanticModel")
SEMANTIC = MODEL / "definition"
PAGES = REPORT / "definition/pages"
ML_PAGE = "ml_performance_review"
BS = chr(92)

results: list[tuple[str, str, object, object]] = []


def check(phase, name, expected, observed):
    results.append((phase, name, expected, observed))


# ---------------------------------------------------------------- Fase 3: datos
raw_text = (ROOT / "data/raw/steel_plates_faults.csv").read_text(encoding="utf-8")
raw_lines = raw_text.splitlines()
raw_header = raw_lines[0].split(",")
ONE_HOT = ["Pastry", "Z_Scratch", "K_Scatch", "Stains", "Dirtiness", "Bumps", "Other_Faults"]

check("F3", "data/raw filas de datos", 1941, len(raw_lines) - 1)
check("F3", "data/raw mediciones predictoras", 27,
      len([c for c in raw_header if c not in ONE_HOT and c != "id"]))
check("F3", "data/raw clases one-hot", ONE_HOT, [c for c in raw_header if c in ONE_HOT])
check("F3", "data/raw filas duplicadas", 0, len(raw_lines) - len(set(raw_lines)))

expressions = (SEMANTIC / "expressions.tmdl").read_text(encoding="utf-8")
found_ruta = re.search(r'expression RutaCSV = "([^"]+)"', expressions)
check("F3", "expressions.tmdl declara RutaCSV", True, found_ruta is not None)
ruta_csv = found_ruta.group(1) if found_ruta else ""
check("F3", "RutaCSV sin separador doblado", True, BS * 2 not in ruta_csv)
# El arbol publicado lleva el parametro portatil (A2-12 par. 6): un marcador neutro
# que el usuario sustituye en Inicio > Transformar datos > Editar parametros. Con el
# marcador, las comprobaciones de sistema de archivos se ejecutan contra los archivos
# del repositorio, que es lo que la ruta configurada debe resolver; con cualquier
# otro valor se exige que la ruta exista de verdad. Solucion explicita, no omision.
PORTABLE = "C:" + BS + BS.join(["path", "to", "steel-plates-quality-mlops",
                                "data", "raw", "steel_plates_faults.csv"])
published = ruta_csv == PORTABLE
check("F3", "RutaCSV es el parametro portatil publicado o una ruta real", True,
      published or Path(ruta_csv).is_file())
resolved = (ROOT / "data/raw/steel_plates_faults.csv") if published else Path(ruta_csv)
check("F3", "RutaCSV resuelve un archivo existente", True, resolved.is_file())
check("F3", "RutaCSV apunta al CSV crudo del repositorio", True,
      resolved.resolve() == (ROOT / "data/raw/steel_plates_faults.csv").resolve())

# Reproduce the RutaMLCSV expression step by step, exactly as written in the TMDL.
normalised = ruta_csv.strip().replace(BS, "/")
derivable = "/data/raw/" in normalised
check("F3", "RutaMLCSV: Text.Contains('/data/raw/')", True, derivable)
ruta_ml = (normalised.split("/data/raw/")[0] + "/powerbi/data/ml_holdout_evaluation.csv"
           if derivable else None)
ruta_ml_real = ((ROOT / "powerbi/data/ml_holdout_evaluation.csv") if published
                else Path(ruta_ml) if ruta_ml else None)
check("F3", "RutaMLCSV resuelve un archivo existente", True,
      bool(ruta_ml) and ruta_ml_real.is_file())
check("F3", "RutaMLCSV apunta al export del holdout", True,
      bool(ruta_ml) and ruta_ml_real.resolve()
      == (ROOT / "powerbi/data/ml_holdout_evaluation.csv").resolve())

ml_lines = (ROOT / "powerbi/data/ml_holdout_evaluation.csv").read_text(encoding="utf-8").splitlines()
# confidence_bin holds values such as "[0.50,0.60)": the delimiter appears inside a
# quoted field, so this file must be parsed as CSV and never split on commas.
ml_reader = csv.DictReader(io.StringIO("\n".join(ml_lines)))
ml_header = list(ml_reader.fieldnames or [])
rows = list(ml_reader)
sys.path.insert(0, str(ROOT / "src"))
from quality_ml.inference.bi_export import COLUMNS  # noqa: E402

check("F3", "ml_holdout_evaluation filas", 389, len(rows))
check("F3", "ml_holdout_evaluation encabezados", list(COLUMNS), ml_header)
check("F3", "ml_holdout dataset_role unico", ["FINAL_HOLDOUT_EVALUATION"],
      sorted({row["dataset_role"] for row in rows}))
check("F3", "ml_holdout filas duplicadas", 0, len(ml_lines) - len(set(ml_lines)))

# ----------------------------------------------- Fase 4: modelo semantico y DAX
pbip = json.loads((PROJECT.with_suffix(".pbip")).read_text(encoding="utf-8-sig"))
pbir = json.loads((REPORT / "definition.pbir").read_text(encoding="utf-8-sig"))
check("F4", "PBIP -> directorio .Report", REPORT.name, pbip["artifacts"][0]["report"]["path"])
check("F4", "PBIP resuelve el .Report en disco", True, REPORT.is_dir())
check("F4", "PBIR -> directorio .SemanticModel", "../" + MODEL.name,
      pbir["datasetReference"]["byPath"]["path"])
check("F4", "PBIR resuelve el .SemanticModel en disco", True,
      (REPORT / pbir["datasetReference"]["byPath"]["path"]).resolve().is_dir())

model = (SEMANTIC / "model.tmdl").read_text(encoding="utf-8")
refs = re.findall(r"^ref table (\w+)$", model, re.M)
check("F4", "tablas referenciadas por el modelo",
      ["Dim_TipoDefecto", "Dim_Acero", "Dim_BandaTamano", "Fact_Defecto",
       "Param_Especificacion", "_Medidas", "ML_Holdout"], refs)
check("F4", "archivos TMDL de tabla presentes", sorted(refs),
      sorted(p.stem for p in (SEMANTIC / "tables").glob("*.tmdl")))

rel = (SEMANTIC / "relationships.tmdl").read_text(encoding="utf-8")
pairs = sorted(zip(re.findall(r"fromColumn: (\S+)", rel), re.findall(r"toColumn: (\S+)", rel)))
check("F4", "relaciones del esquema estrella", [
    ("Fact_Defecto.id_acero", "Dim_Acero.id_acero"),
    ("Fact_Defecto.id_banda_tamano", "Dim_BandaTamano.id_banda_tamano"),
    ("Fact_Defecto.id_tipo_defecto", "Dim_TipoDefecto.id_tipo_defecto")], pairs)
check("F4", "relaciones totales", 3, len(pairs))
# Default TMDL cardinality is many-to-one single-direction; any override is explicit.
check("F4", "cardinalidad/direccion sin anulaciones explicitas", [],
      re.findall(r"^\s*(fromCardinality|toCardinality|crossFilteringBehavior).*$", rel, re.M))
check("F4", "ML_Holdout desconectada del esquema estrella", 0, rel.count("ML_Holdout"))

ml_tmdl = (SEMANTIC / "tables/ML_Holdout.tmdl").read_text(encoding="utf-8")
ml_columns = re.findall(r"^\tcolumn (\w+)$", ml_tmdl, re.M)
ml_measures = re.findall(r"^\tmeasure '([^']+)' =", ml_tmdl, re.M)
check("F4", "columnas de ML_Holdout", list(COLUMNS), ml_columns)
check("F4", "medidas de ML_Holdout", 12, len(ml_measures))
check("F4", "particion ML_Holdout en modo import", True, "mode: import" in ml_tmdl)
check("F4", "particion ML_Holdout usa RutaMLCSV", True, "File.Contents(RutaMLCSV)" in ml_tmdl)
check("F4", "guardia de 389 filas en la particion", True,
      "Table.RowCount(Tipos) = 389" in ml_tmdl)
check("F4", "Macro-F1 congelada en la medida", True, "0.8146728101764369" in ml_tmdl)
check("F4", "Balanced Accuracy congelada en la medida", True, "0.8048726799979933" in ml_tmdl)

medidas = (SEMANTIC / "tables/_Medidas.tmdl").read_text(encoding="utf-8")
originales = re.findall(r"^\tmeasure '?([^'=\n]+?)'? =", medidas, re.M)
check("F4", "medidas originales conservadas en _Medidas", True, len(originales) > 0)

# ------------------------------------------------------ Fase 5: las cinco paginas
index = json.loads((PAGES / "pages.json").read_text(encoding="utf-8-sig"))
check("F5", "orden de paginas", ["5ee9939d0101076d3381", "f50491653678cb19a699",
      "1f75dde540a696f2b18f", "cb973d91eb46886907c2", ML_PAGE], index["pageOrder"])
# activePageName records which tab was selected when Desktop last saved, so it is
# the one page property a genuine save is expected to move. OWNER accepted the ML
# page as the landing page on 2026-11-15. Both values are listed explicitly: the
# page *order* above is what must never drift, and it is still asserted exactly.
ACTIVE_PAGE_ACCEPTED = ("5ee9939d0101076d3381", ML_PAGE)
check("F5", "pagina activa (resumen ejecutivo o pagina ML)", True,
      index["activePageName"] in ACTIVE_PAGE_ACCEPTED)
check("F5", "pagina activa: valor observado", ML_PAGE, index["activePageName"])

names, counts = {}, {}
for page_name in index["pageOrder"]:
    page = json.loads((PAGES / page_name / "page.json").read_text(encoding="utf-8-sig"))
    names[page_name] = page.get("displayName")
    counts[page_name] = len(list((PAGES / page_name / "visuals").glob("*/visual.json")))
check("F5", "las 5 paginas existen en disco", 5, len(counts))
check("F5", "nombre de la pagina ML", "MODEL PERFORMANCE & REVIEW", names[ML_PAGE])
check("F5", "visuales por pagina (las 4 originales)", [13, 8, 10, 3],
      [counts["1f75dde540a696f2b18f"], counts["f50491653678cb19a699"],
       counts["5ee9939d0101076d3381"], counts["cb973d91eb46886907c2"]])
check("F5", "componentes de la pagina ML", 12, counts[ML_PAGE])

kinds, bindings = [], []
for path in sorted((PAGES / ML_PAGE / "visuals").glob("*/visual.json")):
    item = json.loads(path.read_text(encoding="utf-8-sig"))
    kinds.append(item["visual"]["visualType"])
    for role in item["visual"].get("query", {}).get("queryState", {}).values():
        for projection in role["projections"]:
            kind, field = next(iter(projection["field"].items()))
            bindings.append((field["Expression"]["SourceRef"]["Entity"],
                             kind, field["Property"]))
check("F5", "4 tarjetas", 4, kinds.count("cardVisual"))
check("F5", "3 segmentadores", 3, kinds.count("listSlicer"))
check("F5", "4 tablas analiticas", 4, kinds.count("tableEx"))
check("F5", "1 nota contextual", 1, kinds.count("textbox"))
check("F5", "todo campo apunta a ML_Holdout", {"ML_Holdout"}, {e for e, _, _ in bindings})
check("F5", "todo campo existe en el modelo", [], sorted(
    p for _, k, p in bindings
    if p not in (ml_measures if k == "Measure" else ml_columns)))

# --------------------------------------------- Fase 6: reconciliacion cientifica
expected = json.loads((ROOT / "reports/ml/integration/reconciliation_expected.json").read_text())
metrics = json.loads((ROOT / "reports/ml/final_holdout/metrics.json").read_text())["metrics"]


def count(predicate):
    return sum(1 for row in rows if predicate(row))


correct = count(lambda r: r["correct_prediction"] == "1")
review = count(lambda r: r["review_required"] == "1")
check("F6", "holdout", 389, len(rows))
check("F6", "aciertos", 307, correct)
check("F6", "errores", 82, len(rows) - correct)
check("F6", "casos de revision candidata", 261, review)
check("F6", "casos aceptados", 128, len(rows) - review)
check("F6", "errores enviados a revision", 81,
      count(lambda r: r["review_required"] == "1" and r["correct_prediction"] == "0"))
check("F6", "errores no capturados", 1,
      count(lambda r: r["review_required"] == "0" and r["correct_prediction"] == "0"))
check("F6", "exactitud (tol 1e-12)", True, abs(metrics["accuracy"] - correct / len(rows)) <= 1e-12)
check("F6", "exactitud = 0.7892030848329049", True,
      abs(metrics["accuracy"] - 0.7892030848329049) <= 1e-12)
check("F6", "Macro-F1 = 0.8146728101764369", True,
      abs(metrics["macro_f1"] - 0.8146728101764369) <= 1e-12)
check("F6", "Balanced accuracy = 0.8048726799979933", True,
      abs(metrics["balanced_accuracy"] - 0.8048726799979933) <= 1e-12)
check("F6", "Macro-F1 congelada == evidencia", expected["macro_f1"], metrics["macro_f1"])
check("F6", "Balanced accuracy congelada == evidencia",
      expected["balanced_accuracy"], metrics["balanced_accuracy"])

for steel, (n, ok, rev) in {"A300": (156, 121, 122), "A400": (233, 186, 139)}.items():
    subset = [r for r in rows if r["steel_type"] == steel]
    check("F6", f"{steel}: registros", n, len(subset))
    check("F6", f"{steel}: aciertos", ok, sum(1 for r in subset if r["correct_prediction"] == "1"))
    check("F6", f"{steel}: revisiones", rev,
          sum(1 for r in subset if r["review_required"] == "1"))

pastry = [r for r in rows if r["actual_defect"] == "Pastry"]
check("F6", "Pastry: registros", 32, len(pastry))
check("F6", "Pastry: aciertos", 20, sum(1 for r in pastry if r["correct_prediction"] == "1"))
check("F6", "Pastry: revisiones", 29, sum(1 for r in pastry if r["review_required"] == "1"))
check("F6", "confusion Bumps -> Other_Faults", 21,
      count(lambda r: r["actual_defect"] == "Bumps" and r["predicted_defect"] == "Other_Faults"))

row1277 = next(r for r in rows if r["row_id"] == "1277")
check("F6", "row_id 1277: clase real", "Other_Faults", row1277["actual_defect"])
check("F6", "row_id 1277: clase predicha", "K_Scatch", row1277["predicted_defect"])
check("F6", "row_id 1277: confianza 1.0", True, float(row1277["confidence"]) == 1.0)
check("F6", "row_id 1277: es un error", "0", row1277["correct_prediction"])
check("F6", "row_id 1277: fuera de revision candidata", "0", row1277["review_required"])
check("F6", "row_id 1277: alta confianza", "HIGH_CONFIDENCE", row1277["review_status"])

check("F6", "conteos por clase real == evidencia congelada",
      {c["actual_class"]: c["support"] for c in expected["class_counts"]},
      {c["actual_class"]: count(lambda r, a=c["actual_class"]: r["actual_defect"] == a)
       for c in expected["class_counts"]})
check("F6", "errores por clase == evidencia congelada",
      {c["actual_class"]: c["errors"] for c in expected["class_counts"]},
      {c["actual_class"]: count(
          lambda r, a=c["actual_class"]: r["actual_defect"] == a and r["correct_prediction"] == "0")
       for c in expected["class_counts"]})
check("F6", "conteos por estado de revision == evidencia congelada", expected["review_counts"],
      {k: count(lambda r, s=k: r["review_status"] == s) for k in expected["review_counts"]})

# ------------------------------------------------------------------------ salida
failed = [r for r in results if r[2] != r[3]]
for phase, name, exp, obs in results:
    mark = "PASS" if exp == obs else "FAIL"
    detail = "" if exp == obs else f"  esperado={exp!r} observado={obs!r}"
    print(f"[{mark}] {phase}  {name}{detail}")
print(f"\n{len(results) - len(failed)}/{len(results)} comprobaciones PASS")
print("ALCANCE: validacion estatica de fuentes y evidencia. "
      "El runtime de Power BI Desktop NO esta validado por este script.")
sys.exit(1 if failed else 0)
