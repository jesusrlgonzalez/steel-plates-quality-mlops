"""Piloto P02 (Nivel A): criterios de aceptación C1-C10 sobre la capa operativa sintética."""
import hashlib
import json
import re
from pathlib import Path

import pandas as pd
import pytest

from quality_ml import pilot_p02 as p

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "pilots" / "P02"


@pytest.fixture(scope="module")
def runs():
    return {sc.id: p.operate(sc) for sc in p.SCENARIOS}


def test_c1_every_manifest_rule_is_detected_corrected_or_excluded():
    rec = p.check_reconciliation()
    assert all(rec[f"D{i}"] for i in range(1, 8)) and rec["resto_igual"], rec


def test_manifest_covers_all_rules_and_keeps_the_original():
    truth = p.truth_history()
    raw, log = p.inject(truth, p.Imperfections(), seed=21, pending_from=p.HIST_DAYS - p.PENDING_DAYS)
    assert {r["regla"] for r in log} == {f"D{i}" for i in range(1, 8)} and all(r["filas"] > 0 for r in log)
    assert truth.equals(p.truth_history())
    assert len(raw) == len(truth) + next(r["filas"] for r in log if r["regla"] == "D1")


def test_c2_cuts_use_only_reviews_closed_before_operation(runs):
    for r in runs.values():
        assert r["ajuste"].ultimo_dia < p.HIST_DAYS - p.PENDING_DAYS


def test_c3_daily_human_reviews_never_exceed_capacity(runs):
    for r in runs.values():
        per_day = r["decisiones"].query("decision == 'revisar'").groupby(["politica", "dia"]).size()
        assert per_day.le(r["escenario"].capacidad).all()


def test_c4_stream_comes_only_from_cross_validation_predictions(runs):
    src = pd.read_csv(p.SOURCE)
    holdout_rows = set(src.index[src["origen"] != "validación cruzada"])
    assert len(holdout_rows) == 389
    assert set(p.source()["fila_base"]).isdisjoint(holdout_rows)
    for sc in p.SCENARIOS:
        assert set(p.truth_ops(sc)["fila_base"]).isdisjoint(holdout_rows)
    dec = pd.concat([r["decisiones"] for r in runs.values()])
    assert dec["origen"].eq(p.ORIGEN).all()


def test_c7_unknown_classes_never_released_and_gates_suspend(runs):
    dec = pd.concat([r["decisiones"] for r in runs.values()])
    unknown = dec[dec["clase_predicha"] == p.NEW_CLASS]
    assert len(unknown) > 0 and unknown["decision"].isin(["revisar", "retenida"]).all()
    d3 = runs["S3"]["dias"].set_index("dia")
    assert d3.loc[[7, 8], "suspendido"].all() and "confianza" in d3.loc[7, "motivo"]   # confianza descalibrada
    assert d3.loc[10, "suspendido"] and "inválidas" in d3.loc[10, "motivo"]
    assert not runs["S1"]["dias"]["suspendido"].any()                                    # sin falsas alarmas
    # Observado y reportado como reserva: el cambio de mezcla (días 3-5) no se detecta.
    assert not d3.loc[[3, 4, 5], "suspendido"].any()


def test_c8_every_decision_is_traceable(runs):
    dec = pd.concat([r["decisiones"] for r in runs.values()])
    cols = ["escenario", "politica", "dia", "id_placa", "clase_predicha", "decision", "motivo", "cortes"]
    assert dec[cols].notna().all().all()
    assert set(dec["decision"]) <= {"revisar", "aceptar", "liberada_sin_cupo", "retenida"}
    assert dec.groupby("escenario")["cortes"].nunique().eq(1).all()


def test_c9_costs_recompute_from_the_decision_log(runs):
    for r in runs.values():
        dec, truth = r["decisiones"], p.truth_ops(r["escenario"]).set_index("id_placa")["clase_real"]
        for pol in p.POLICIES:
            d = dec[dec["politica"] == pol]
            released = d["decision"].isin(["aceptar", "liberada_sin_cupo"])
            errors = sum(p.costo_error(truth[i], c) for i, c in zip(d.loc[released, "id_placa"], d.loc[released, "clase_predicha"]))
            assert r["resumen"][f"{pol}_costo"] == pytest.approx(p.COSTO_REVISION * (d["decision"] == "revisar").sum() + errors)


def test_c10_power_bi_export_matches_dax_and_reconciles(runs):
    bi = p.bi_export(runs)
    dax = (ROOT / "powerbi" / "dax" / "revision_humana.dax").read_text(encoding="utf-8")
    assert set(re.findall(r"Seguimiento_Revision\[(\w+)\]", dax)) <= set(bi.columns)
    dec = pd.concat([r["decisiones"] for r in runs.values()])
    assert bi["piezas"].sum() == len(dec)
    assert bi["a_revision"].sum() == (dec["decision"] == "revisar").sum()
    assert (bi["errores_en_aceptadas"] * bi["costo_escape"]).sum() == pytest.approx(dec["costo_error"].sum(), rel=1e-6)


def test_committed_outputs_match_evidence_hashes():
    ev = json.loads((OUT / "evidence.json").read_text(encoding="utf-8"))
    sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()  # noqa: E731
    for name, h in ev["salidas"].items():
        assert sha(OUT / name) == h, name
    for path, h in ev["codigo_y_fuente"].items():
        assert sha(ROOT / path) == h, path
    assert all(ev["criterios"].values())


def test_results_report_quotes_the_generated_numbers():
    res = json.loads((OUT / "results.json").read_text(encoding="utf-8"))
    text = (ROOT / "docs" / "pilots" / "P02" / "03_resultados.md").read_text(encoding="utf-8")
    for sc in ("S1", "S2", "S3"):
        r = res["escenarios"][sc]["resumen"]
        for key in ("revisar_todas_costo", "umbral_unico_costo", "priorizada_costo", "ahorro_vs_revisar_todas",
                    "ahorro_vs_revisar_todas_lo", "ahorro_vs_revisar_todas_hi", "ahorro_vs_umbral_unico"):
            assert f"{r[key]:,.0f}" in text, (sc, key)
