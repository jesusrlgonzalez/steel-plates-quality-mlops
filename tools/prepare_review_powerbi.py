"""Build the additive P02 human-review tracking page (PBIR/TMDL) from existing repository structures.

Adds, without touching the certified pages or tables:
- table ``Seguimiento_Revision`` loaded from ``powerbi/data/seguimiento_revision.csv`` (a byte copy of the
  P02 export ``reports/pilots/P02/seguimiento_revision.csv``) with the measures of ``powerbi/dax/revision_humana.dax``;
- page ``review_tracking`` ("SEGUIMIENTO DE REVISIÓN HUMANA").

The generated text is a draft until Power BI Desktop opens, refreshes and saves it. Once the page exists,
the committed files are the Desktop-saved ones (validated on 2026-11-17) and only the data copy is refreshed.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from quality_ml.inference.artifact import write_json  # noqa: E402

PROJECT = "powerbi/project/steel-plates-quality-mlops-powerbi"
REPORT = PROJECT + ".Report/definition/pages"
SEMANTIC = PROJECT + ".SemanticModel/definition"
PAGE = "review_tracking"
TABLE = "Seguimiento_Revision"
SOURCE_CSV = "reports/pilots/P02/seguimiento_revision.csv"
DATA_CSV = "powerbi/data/seguimiento_revision.csv"
DAX = "powerbi/dax/revision_humana.dax"
# fecha_corte stays ISO text (YYYY-MM-DD): it sorts like a date, and a date column would make Desktop
# add auto date tables and a relationship to the certified model (seen on the first Desktop save).
TYPES = {"fecha_corte": "string", "escenario": "string", "politica": "string", "clase": "string",
         "piezas": "int64", "a_revision": "int64", "aceptadas": "int64", "retenidas": "int64",
         "errores_en_aceptadas": "int64", "costo_revision": "double", "costo_escape": "double",
         "costo_errores": "double", "suspendido": "boolean", "clausula_iso9001": "string"}
M_TYPES = {"dateTime": "type date", "string": "type text", "int64": "Int64.Type", "double": "type number",
           "boolean": "type logical"}
FORMATS = {"Piezas Totales": "#,0", "Piezas a Revision": "#,0", "% a Revision": "0.0%", "Errores en Aceptadas": "#,0",
           "Escapes por 1000 Aceptadas": "#,0.0", "Costo de Revision MXN": "#,0", "Costo de Escapes MXN": "#,0",
           "Costo Total MXN": "#,0", "Costo Revisar Todo MXN": "#,0", "Ahorro vs Revisar Todo MXN": "#,0",
           "Piezas Retenidas": "#,0"}
EXTRA = {  # trazabilidad de alertas de la capa P02; no cambian las medidas de revision_humana.dax
    "Piezas Retenidas": "SUM ( Seguimiento_Revision[retenidas] )",
    "Estado del Corte": 'IF ( CALCULATE ( COUNTROWS ( Seguimiento_Revision ), Seguimiento_Revision[suspendido] = TRUE () ) > 0, "suspendido", "normal" )',
}


def dax_measures(root=ROOT) -> dict[str, str]:
    """Measures of ``revision_humana.dax`` as {name: expression}, comments removed, whitespace kept."""
    text = (Path(root) / DAX).read_text(encoding="utf-8")
    body = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("//"))
    parts = re.split(r"^(?!VAR |RETURN)([^\s=][^=\n]*?) =", body, flags=re.M)
    return {parts[i].strip(): parts[i + 1].strip() for i in range(1, len(parts), 2)}


def _tmdl_measure(name: str, expression: str) -> list[str]:
    lines = expression.splitlines()
    if len(lines) == 1:
        out = [f"\tmeasure '{name}' = {lines[0]}"]
    else:
        out = [f"\tmeasure '{name}' =", *[f"\t\t\t{line}" for line in lines]]
    if name in FORMATS:
        out.append(f"\t\tformatString: {FORMATS[name]}")
    return out


def prepare(root=ROOT):
    root = Path(root)
    base = root / REPORT
    (root / DATA_CSV).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / SOURCE_CSV, root / DATA_CSV)
    header = (root / DATA_CSV).read_text(encoding="utf-8").splitlines()[0].split(",")
    if header != list(TYPES):
        raise ValueError(f"Unexpected export schema: {header}")
    if PAGE in json.loads((base / "pages.json").read_text(encoding="utf-8-sig"))["pageOrder"]:
        return dict(status="DESKTOP_SAVED_KEPT", page=PAGE, table=TABLE, runtime_validation="DESKTOP_VALIDATED")

    templates = {
        "card": "5ee9939d0101076d3381/visuals/083e0e977408b7b77e25/visual.json",
        "table": "f50491653678cb19a699/visuals/53f9fbf278a14f1de6b6/visual.json",
        "slicer": "1f75dde540a696f2b18f/visuals/a3a0702d79cc235356ad/visual.json",
        "text": "1f75dde540a696f2b18f/visuals/b8db3c0b614b3b22017e/visual.json",
        "line": "f50491653678cb19a699/visuals/0da48ade3c8f1735058c/visual.json",
        "column": "1f75dde540a696f2b18f/visuals/10dded7886b093c43cd7/visual.json",
    }
    templates = {k: json.loads((base / v).read_text(encoding="utf-8-sig")) for k, v in templates.items()}
    page = json.loads((base / "ml_performance_review/page.json").read_text(encoding="utf-8-sig"))
    page.update(name=PAGE, displayName="SEGUIMIENTO DE REVISIÓN HUMANA", height=1200)
    if (base / PAGE).exists():
        shutil.rmtree(base / PAGE)
    write_json(base / PAGE / "page.json", page)

    def field(name, measure=False):
        return {("Measure" if measure else "Column"): {
            "Expression": {"SourceRef": {"Entity": TABLE}}, "Property": name}}

    def projection(name, measure):
        return dict(field=field(name, measure), queryRef=f"{TABLE}.{name}", nativeQueryRef=name)

    def visual(key, kind, roles, x, y, w, h, order):
        item = copy.deepcopy(templates[kind])
        identity = hashlib.sha256(("p02-" + key).encode()).hexdigest()[:20]
        item["name"] = identity
        item["position"] = dict(x=x, y=y, width=w, height=h, z=order, tabOrder=order)
        item.pop("filterConfig", None)
        view = item["visual"]
        view.pop("objects", None)
        view.pop("visualContainerObjects", None)
        view["query"] = dict(queryState={role: dict(projections=[projection(n, m) for n, m in fields])
                                         for role, fields in roles.items()})
        write_json(base / PAGE / "visuals" / identity / "visual.json", item)

    text = copy.deepcopy(templates["text"])
    text["name"] = hashlib.sha256(b"p02-context").hexdigest()[:20]
    text["position"] = dict(x=20, y=10, width=1240, height=95, z=0, tabOrder=0)
    text["visual"].pop("visualContainerObjects", None)
    run = text["visual"]["objects"]["general"][0]["properties"]["paragraphs"][0]["textRuns"][0]
    run["value"] = ("P02 · NIVEL A · flujo operativo SINTÉTICO de una planta ficticia; cifras en MXN de escenario, no beneficios "
                    "observados. Cada fila = corte diario × escenario × política × clase predicha. Filtre UN escenario y UNA "
                    "política para leer un caso. Escapes = placas liberadas con clase equivocada (clase real simulada). "
                    "'Revisar todo' supone revisar todas las piezas sin límite de inspectores. Clasificación de defectos "
                    "ya detectados: no es detección temprana, prevención ni causa. Fuente: reports/pilots/P02.")
    run["textStyle"]["fontSize"] = "13px"
    run["textStyle"]["fontStyle"] = "normal"
    write_json(base / PAGE / "visuals" / text["name"] / "visual.json", text)

    for i, column in enumerate(["escenario", "politica", "clase"]):
        visual("filter-" + column, "slicer", {"Values": [(column, False)]}, 20 + 415 * i, 115, 395, 150, i + 1)
    for i, measure in enumerate(["Piezas Totales", "Piezas a Revision", "% a Revision", "Errores en Aceptadas",
                                  "Escapes por 1000 Aceptadas", "Costo Total MXN"]):
        visual("card-" + measure, "card", {"Data": [(measure, True)]}, 20 + 207 * i, 280, 195, 105, i + 4)
    visual("trend", "line", {"Category": [("fecha_corte", False)], "Y": [("Escapes por 1000 Aceptadas", True)]},
           20, 400, 610, 300, 10)
    visual("by-class", "column", {"Category": [("clase", False)], "Y": [("Piezas a Revision", True)]},
           650, 400, 610, 300, 11)
    visual("by-cut", "table", {"Values": [("fecha_corte", False), ("Piezas Totales", True), ("Piezas a Revision", True),
                                          ("Piezas Retenidas", True), ("Errores en Aceptadas", True),
                                          ("Costo Total MXN", True), ("Semaforo Escapes", True), ("Estado del Corte", True)]},
           20, 715, 610, 300, 12)
    visual("costs", "table", {"Values": [("politica", False), ("Costo de Revision MXN", True), ("Costo de Escapes MXN", True),
                                         ("Costo Total MXN", True), ("Costo Revisar Todo MXN", True),
                                         ("Ahorro vs Revisar Todo MXN", True)]},
           650, 715, 610, 300, 13)
    visual("class-table", "table", {"Values": [("clase", False), ("Piezas Totales", True), ("Piezas a Revision", True),
                                               ("% a Revision", True), ("Errores en Aceptadas", True),
                                               ("Escapes por 1000 Aceptadas", True)]},
           20, 1030, 1240, 150, 14)

    index_path = base / "pages.json"
    index = json.loads(index_path.read_text(encoding="utf-8-sig"))
    if PAGE not in index["pageOrder"]:
        index["pageOrder"].append(PAGE)
    write_json(index_path, index)

    measures = dax_measures(root) | EXTRA
    clash = {m for m in measures if m.lower() in {c.lower() for c in TYPES}}
    if clash:
        raise ValueError(f"Measures named like columns (Power BI rejects them): {sorted(clash)}")
    lines = [f"table {TABLE}"]
    for name, expression in measures.items():
        lines += ["", *_tmdl_measure(name, expression)]
    for name, kind in TYPES.items():
        lines += ["", f"\tcolumn {name}", f"\t\tdataType: {kind}"]
        lines += ["\t\tsummarizeBy: none", f"\t\tsourceColumn: {name}"]
    headers = ", ".join(f'"{name}"' for name in TYPES)
    conversions = ", ".join('{"' + n + '", ' + M_TYPES[k] + "}" for n, k in TYPES.items())
    query = (
        'let\n'
        '    Origen = Csv.Document(File.Contents(RutaRevisionCSV), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n'
        '    Cabecera = Table.PromoteHeaders(Origen, [PromoteAllScalars=true]),\n'
        f'    Esperadas = {{{headers}}},\n'
        '    Schema = if Table.ColumnNames(Cabecera) = Esperadas then Cabecera else error "Seguimiento schema mismatch",\n'
        f'    Tipos = Table.TransformColumnTypes(Schema, {{{conversions}}}, "en-US"),\n'
        '    Validado = if List.ContainsAll({"S1", "S2", "S3"}, List.Distinct(Tipos[escenario])) and Table.RowCount(Tipos) > 0\n'
        '        then Tipos else error "Expected P02 scenarios S1-S3"\n'
        'in\n'
        '    Validado'
    )
    lines += ["", f"\tpartition {TABLE} = m", "\t\tmode: import", "\t\tsource ="]
    lines += ["\t\t\t\t" + line for line in query.splitlines()]
    (root / SEMANTIC / f"tables/{TABLE}.tmdl").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    model_path = root / SEMANTIC / "model.tmdl"
    model = model_path.read_bytes()
    if f"ref table {TABLE}".encode() not in model:
        eol = b"\r\n" if b"\r\n" in model else b"\n"
        anchor = b"ref table ML_Holdout" + eol
        if model.count(anchor) != 1:
            raise ValueError("model.tmdl: ML_Holdout reference not found exactly once")
        model_path.write_bytes(model.replace(anchor, anchor + f"ref table {TABLE}".encode() + eol, 1))
    expression_path = root / SEMANTIC / "expressions.tmdl"
    expressions = expression_path.read_bytes()
    if b"expression RutaRevisionCSV =" not in expressions:
        addition = ('\nexpression RutaRevisionCSV =\n'
                    '\t\tlet\n'
                    '\t\t    Normalized = Text.Replace(Text.Trim(RutaCSV), "\\", "/"),\n'
                    '\t\t    Root = if Text.Contains(Normalized, "/data/raw/") then Text.BeforeDelimiter(Normalized, "/data/raw/")\n'
                    '\t\t        else error "Set RutaCSV to this repository data/raw/steel_plates_faults.csv",\n'
                    '\t\t    Result = Root & "/powerbi/data/seguimiento_revision.csv"\n'
                    '\t\tin\n'
                    '\t\t    Result\n')
        eol = b"\r\n" if b"\r\n" in expressions else b"\n"
        expression_path.write_bytes(expressions.rstrip(b"\r\n") + eol + eol + addition.lstrip("\n").encode("utf-8").replace(b"\n", eol))
    return dict(status="TEXT_DRAFT_CREATED", page=PAGE, table=TABLE, measures=len(measures), visuals=15,
                runtime_validation="PENDING_DESKTOP")


if __name__ == "__main__":
    print(json.dumps(prepare(), indent=2, ensure_ascii=False))
