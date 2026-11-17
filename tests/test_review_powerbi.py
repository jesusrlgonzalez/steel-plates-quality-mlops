"""P02 human-review tracking page: additive PBIR/TMDL text checks (Owner order A5, A5-D10).

These are textual checks. Desktop validation is recorded separately, in
docs/production/POWERBI_P02_REVIEW_PAGE.md, with the PBIX identity it produced.
"""
import json
import re
import shutil
from pathlib import Path

from tools.prepare_review_powerbi import (DATA_CSV, PAGE, REPORT, SEMANTIC, SOURCE_CSV, TABLE, TYPES, EXTRA,
                                          dax_measures, prepare)

ROOT = Path(__file__).resolve().parents[1]
TMDL = ROOT / SEMANTIC / f"tables/{TABLE}.tmdl"


def _norm(text):
    return " ".join(text.split())


def test_page_data_is_the_p02_export_byte_for_byte():
    assert (ROOT / DATA_CSV).read_bytes() == (ROOT / SOURCE_CSV).read_bytes()


def test_table_schema_and_measures_match_the_dax_file():
    table = TMDL.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    assert re.findall(r"^\tcolumn (\w+)$", table, re.M) == list(TYPES)
    for name, kind in TYPES.items():
        assert re.search(rf"^\tcolumn {name}\n\t\tdataType: {kind}$", table, re.M), name
    found = dict(re.findall(r"^\tmeasure '([^']+)' =\s*(.*?)(?=\n\t\t(?:formatString|lineageTag|annotation)|\n\n|\n\tcolumn|\n\tpartition|\Z)",
                            table, re.M | re.S))
    expected = dax_measures(ROOT) | EXTRA
    assert set(found) == set(expected)
    # Desktop refuses a measure named like a column (case-insensitive); found when opening in Desktop.
    assert not {m.lower() for m in found} & {c.lower() for c in TYPES}
    for name, expression in expected.items():
        assert _norm(found[name]) == _norm(expression), name
    assert "File.Contents(RutaRevisionCSV)" in table and "mode: import" in table


def test_page_layout_and_bindings():
    base = ROOT / REPORT / PAGE
    page = json.loads((base / "page.json").read_text(encoding="utf-8-sig"))
    assert page["displayName"] == "SEGUIMIENTO DE REVISIÓN HUMANA"
    table = TMDL.read_text(encoding="utf-8-sig")
    columns = set(re.findall(r"^\tcolumn (\w+)\s*$", table, re.M))
    measures = set(re.findall(r"^\tmeasure '([^']+)' =", table, re.M))
    visuals = [json.loads(p.read_text(encoding="utf-8-sig")) for p in (base / "visuals").glob("*/visual.json")]
    types = [v["visual"]["visualType"] for v in visuals]
    assert sorted(types) == sorted(["textbox"] + ["listSlicer"] * 3 + ["cardVisual"] * 6 + ["lineChart",
                                    "clusteredColumnChart"] + ["tableEx"] * 3)
    boxes = []
    for item in visuals:
        p = item["position"]
        assert 0 <= p["x"] <= page["width"] - p["width"] and 0 <= p["y"] <= page["height"] - p["height"]
        for o in boxes:
            assert (p["x"] + p["width"] <= o["x"] or o["x"] + o["width"] <= p["x"]
                    or p["y"] + p["height"] <= o["y"] or o["y"] + o["height"] <= p["y"])
        boxes.append(p)
        for role in item["visual"].get("query", {}).get("queryState", {}).values():
            for projection in role["projections"]:
                kind, field = next(iter(projection["field"].items()))
                assert field["Expression"]["SourceRef"]["Entity"] == TABLE
                assert field["Property"] in (measures if kind == "Measure" else columns)
    text = next(v for v in visuals if v["visual"]["visualType"] == "textbox")
    note = json.dumps(text, ensure_ascii=False)
    for phrase in ("NIVEL A", "SINTÉTICO", "no beneficios observados", "no es detección temprana"):
        assert phrase in note


def test_review_page_is_appended_after_the_certified_pages():
    index = json.loads((ROOT / REPORT / "pages.json").read_text(encoding="utf-8-sig"))
    assert index["pageOrder"][-1] == PAGE and index["pageOrder"].count(PAGE) == 1


def test_generation_is_idempotent(tmp_path):
    shutil.copytree(ROOT / "powerbi", tmp_path / "powerbi", ignore=shutil.ignore_patterns(".pbi", "*.pbix"))
    (tmp_path / SOURCE_CSV).parent.mkdir(parents=True)
    shutil.copyfile(ROOT / SOURCE_CSV, tmp_path / SOURCE_CSV)
    shutil.copyfile(ROOT / "powerbi/dax/revision_humana.dax", tmp_path / "powerbi/dax/revision_humana.dax")
    before = {p: p.read_bytes() for p in (tmp_path / "powerbi").rglob("*") if p.is_file()}
    prepare(tmp_path)
    once = {p: p.read_bytes() for p in (tmp_path / "powerbi").rglob("*") if p.is_file()}
    assert once == before  # the Desktop-saved page and table are never regenerated over
    prepare(tmp_path)
    assert once == {p: p.read_bytes() for p in (tmp_path / "powerbi").rglob("*") if p.is_file()}


def test_no_host_dependency():
    for path in [TMDL, ROOT / DATA_CSV, *(ROOT / REPORT / PAGE).rglob("*.json")]:
        contents = path.read_text(encoding="utf-8-sig").lower()
        assert "c:\\users\\" not in contents and "c:/users/" not in contents and "downloads\\" not in contents
