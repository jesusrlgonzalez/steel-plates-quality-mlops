"""Piloto demostrativo P02 (Nivel A): revisión humana de la clasificación de defectos con inspectores limitados.

Capa operativa sintética sobre ``review_policy`` (que no se modifica). El flujo diario se simula remuestreando
solo las predicciones **fuera de muestra de validación cruzada** de ``examples/review_triage/inspeccion_placas.csv``;
las 389 filas del holdout no se leen. Los resultados son de escenario de una empresa ficticia, no beneficios
observados, y no cambian la evaluación científica congelada del modelo.

    python -B -m quality_ml.pilot_p02        # regenera reports/pilots/P02/
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field, replace
from pathlib import Path

import numpy as np
import pandas as pd

from quality_ml import review_policy as rp

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "examples" / "review_triage" / "inspeccion_placas.csv"
OUT = ROOT / "reports" / "pilots" / "P02"
EMPRESA = "Aceros Laminados del Golfo, S.A. (empresa ficticia)"
ORIGEN = "simulada: remuestreo de predicción fuera de muestra (validación cruzada)"
START = pd.Timestamp("2026-03-02")
HIST_DAYS, PENDING_DAYS, OPS_DAYS, PER_DAY = 20, 3, 10, 60
B_FROM_DAY = 8                              # la línea B reporta la confianza de 0 a 100 desde este día
COSTO_REVISION = 40.0
MAX_INVALIDAS, MAX_PSI = 0.10, 0.25         # compuertas de suspensión del día
CLASSES = ("Pastry", "Z_Scratch", "K_Scatch", "Stains", "Dirtiness", "Bumps", "Other_Faults")
DISPOSICION = {"Pastry": "retrabajo superficial", "Z_Scratch": "esmerilado", "K_Scatch": "esmerilado", "Stains": "limpieza",
               "Dirtiness": "limpieza", "Bumps": "recorte", "Other_Faults": "inspección especial"}
SEVERAS = {"Bumps", "Other_Faults"}
NEW_CLASS = "Inclusion"
POLICIES = ("revisar_todas", "umbral_unico", "priorizada")

VARIANTS = {"Z_Scratch": ["Z-Scratch", "z scratch", "Rayón Z"], "K_Scatch": ["K_Scratch", "K-Scratch", "Rayón K"],
            "Other_Faults": ["Other Faults", "OTRAS_FALLAS"], "Dirtiness": ["Suciedad"], "Stains": ["Manchas"],
            "Bumps": ["Golpes"], "Pastry": ["PASTRY"]}


def _norm(text) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())


CATALOG = {_norm(c): c for c in CLASSES} | {_norm(v): c for c, vs in VARIANTS.items() for v in vs}


def costo_error(real: str, asignada: str, escala: float = 1.0) -> float:
    """Matriz de costo de una placa que sale con la clase equivocada (supuesto del caso; solo para evaluar)."""
    if real == asignada:
        return 0.0
    if real in SEVERAS:
        return 6_000.0 * escala
    return (150.0 if DISPOSICION.get(real) == DISPOSICION.get(asignada) else 1_500.0) * escala


@dataclass(frozen=True)
class Imperfections:
    duplicados: float = 0.03     # D1 doble lectura de la placa
    sin_confianza: float = 0.05  # D2 confianza ausente
    variantes: float = 0.10      # D4 nomenclatura contradictoria
    tardios: float = 0.04        # D6 registros capturados un día después
    errores: int = 6             # D7 errores de integración


@dataclass(frozen=True)
class Scenario:
    id: str
    nombre: str
    capacidad: int
    ops: Imperfections = Imperfections(errores=2)
    mezcla: tuple[int, ...] = ()             # días operados (1-10) con triple de placas Bumps
    descalibrada: tuple[int, ...] = ()       # días con confianza inflada (c ** 0.25)
    nuevas: tuple[int, ...] = ()             # días con una clase que el catálogo no conoce
    invalidos: dict = field(default_factory=dict)  # {día: fracción de filas con confianza ilegible}


SCENARIOS = (
    Scenario("S1", "Referencia: operación normal", 25),
    Scenario("S2", "Inspectores reducidos a la mitad y registros más incompletos", 12,
             Imperfections(duplicados=0.06, sin_confianza=0.10, variantes=0.15, tardios=0.08, errores=2)),
    Scenario("S3", "Límites: cambio de mezcla, clase nueva, confianza descalibrada y datos inválidos", 25,
             mezcla=(3, 4, 5), descalibrada=(7, 8), nuevas=(2, 9), invalidos={10: 0.15}),
)


# ---------------------------------------------------------------- flujo sintético
def source() -> pd.DataFrame:
    d = pd.read_csv(SOURCE, dtype={"confianza": float})
    return d[d["origen"] == "validación cruzada"].reset_index().rename(columns={"index": "fila_base"})


def _day(base: pd.DataFrame, day: int, rng, bumps_x: float = 1.0) -> pd.DataFrame:
    w = np.where(base["clase_real_oculta"] == "Bumps", bumps_x, 1.0)
    rows = base.iloc[rng.choice(len(base), int(rng.poisson(PER_DAY)), p=w / w.sum())]
    fecha = START + pd.Timedelta(days=day)
    return pd.DataFrame(dict(id_placa=[f"PL-{day:02d}-{i:03d}" for i in range(len(rows))], dia=day, fecha=fecha,
                             linea=np.where(rng.random(len(rows)) < 0.5, "A", "B"), clase_predicha=rows["clase_predicha"].to_numpy(),
                             confianza=rows["confianza"].to_numpy(), clase_real=rows["clase_real_oculta"].to_numpy(),
                             fila_base=rows["fila_base"].to_numpy(), origen=ORIGEN))


def truth_history(seed: int = 3) -> pd.DataFrame:
    """Verdad sintética del historial con la muestra revisada: 30 % al azar dentro de cada decil de confianza."""
    rng, base = np.random.default_rng(seed), source()
    df = pd.concat([_day(base, d, rng) for d in range(HIST_DAYS)], ignore_index=True)
    band = pd.qcut(df["confianza"], 10, labels=False, duplicates="drop")
    df["revisada"] = False
    for _, idx in df.groupby(band).groups.items():
        df.loc[rng.choice(idx, int(round(len(idx) * 0.3)), replace=False), "revisada"] = True
    return df


def truth_ops(sc: Scenario, seed: int = 4) -> pd.DataFrame:
    rng, base = np.random.default_rng(seed), source()
    days = []
    for k in range(1, OPS_DAYS + 1):
        d = _day(base, HIST_DAYS + k - 1, rng, 3.0 if k in sc.mezcla else 1.0)
        if k in sc.descalibrada:
            d["confianza"] = d["confianza"] ** 0.25
        if k in sc.nuevas:
            extra = d.iloc[:3].copy()
            extra["id_placa"] = [f"PL-{HIST_DAYS + k - 1:02d}-N{i}" for i in range(3)]
            extra["clase_predicha"], extra["clase_real"] = NEW_CLASS, "Other_Faults"
            d = pd.concat([d, extra], ignore_index=True)
        days.append(d)
    df = pd.concat(days, ignore_index=True)
    df["revisada"] = False
    return df


def inject(truth: pd.DataFrame, imp: Imperfections, seed: int, pending_from: int | None = None,
           invalid_by_day: dict | None = None) -> tuple[pd.DataFrame, list[dict]]:
    """Exportación tal como llega y manifiesto de cada perturbación (ids afectados). No modifica ``truth``."""
    rng = np.random.default_rng(seed)
    raw = truth.copy()
    raw["confianza"] = raw["confianza"].map(lambda v: f"{v:.4f}")
    raw["clase_real"] = raw["clase_real"].where(raw["revisada"], "")
    raw["fecha_captura"] = raw["fecha"]
    n, pool, used, log = len(raw), [int(i) for i in rng.permutation(len(raw))], set(), []

    def take(k: int, where: np.ndarray | None = None) -> list[int]:  # índices disjuntos entre reglas
        cand = [i for i in pool if i not in used and (where is None or where[i])][:k]
        used.update(cand)
        return cand

    def rec(rid, tipo, ids):
        log.append(dict(regla=rid, tipo=tipo, ids=sorted(raw.loc[ids, "id_placa"].tolist()), filas=len(ids)))

    line_a = (raw["linea"] == "A").to_numpy()
    err = take(imp.errores, line_a)
    for k, i in enumerate(err):
        col, val = [("confianza", "1.7"), ("clase_predicha", ""), ("confianza", "abc")][k % 3]
        raw.at[i, col] = val
    if invalid_by_day:
        for d, frac in invalid_by_day.items():
            rows = np.flatnonzero((raw["dia"] == HIST_DAYS + d - 1).to_numpy() & line_a)
            rows = [int(i) for i in rows if int(i) not in used][: int(round((raw["dia"] == HIST_DAYS + d - 1).sum() * frac))]
            used.update(rows)
            raw.loc[rows, "confianza"] = "abc"
            err += rows
    if err:
        rec("D7", "Errores de integración (confianza fuera de rango o ilegible, clase vacía)", err)

    miss = take(int(round(n * imp.sin_confianza)))
    raw.loc[miss, "confianza"] = ""
    rec("D2", "Confianza ausente", miss)

    b = np.flatnonzero((raw["linea"] == "B").to_numpy() & (raw["dia"].to_numpy() >= B_FROM_DAY) & (raw["confianza"] != "").to_numpy()
                       & ~np.isin(np.arange(n), err))
    raw.loc[b, "confianza"] = (raw.loc[b, "confianza"].astype(float) * 100).map(lambda v: f"{v:.2f}")
    rec("D3", "Escala de confianza mezclada (línea B de 0 a 100)", list(b))

    known = raw["clase_predicha"].isin(VARIANTS).to_numpy()
    var = take(int(round(n * imp.variantes)), known)
    for i in var:
        opts = VARIANTS[raw.at[i, "clase_predicha"]]
        raw.at[i, "clase_predicha"] = opts[int(rng.integers(0, len(opts)))]
    rec("D4", "Nomenclatura de clases inconsistente", var)

    if pending_from is not None:
        pend = list(np.flatnonzero((raw["dia"].to_numpy() >= pending_from) & raw["revisada"].to_numpy()))
        raw.loc[pend, "clase_real"] = ""
        rec("D5", "Revisión humana aún abierta (clase real pendiente)", pend)

    late = take(int(round(n * imp.tardios)), (raw["dia"] < raw["dia"].max()).to_numpy() & ~raw["revisada"].to_numpy())
    raw.loc[late, "fecha_captura"] = raw.loc[late, "fecha"] + pd.Timedelta(days=1)
    rec("D6", "Registro capturado con un día de retraso", late)

    dup = take(int(round(n * imp.duplicados)))
    rec("D1", "Placa leída dos veces", dup)
    raw = pd.concat([raw, raw.loc[dup]], ignore_index=True)

    for c in ("fecha", "fecha_captura"):
        raw[c] = pd.to_datetime(raw[c]).dt.strftime("%Y-%m-%d")
    cols = ["id_placa", "fecha", "fecha_captura", "linea", "clase_predicha", "confianza", "clase_real"]
    return raw[cols], log


# ---------------------------------------------------------------- conciliación
def reconcile(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Fuente conciliada y bitácora. Excluye lo inválido; conserva sin decidir lo desconocido o sin confianza."""
    df = raw.copy()
    bit = dict(filas_recibidas=len(df), duplicados=int(df.duplicated("id_placa").sum()))
    df = df.drop_duplicates("id_placa").reset_index(drop=True)
    canon = df["clase_predicha"].map(lambda t: CATALOG.get(_norm(t)) if str(t).strip() else None)
    empty = df["clase_predicha"].astype(str).str.strip().eq("")
    bit["nomenclatura_corregida"] = int((canon.notna() & (canon != df["clase_predicha"])).sum())
    df["clase_conocida"] = canon.notna()
    df["clase_predicha"] = canon.fillna(df["clase_predicha"].astype(str).str.strip())
    txt = df["confianza"].astype(str).str.strip()
    conf = pd.to_numeric(txt.str.replace(",", "."), errors="coerce")
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["fecha_captura"] = pd.to_datetime(df["fecha_captura"])
    big = conf.groupby([df["linea"], df["fecha"]]).transform(lambda s: s[s.notna()].gt(1).mean() > 0.5)
    conf = conf.where(~big, conf / 100)
    bit["confianza_reescalada"] = int((big & conf.notna()).sum())
    df["sin_confianza"] = txt.eq("")
    invalid = empty | (~txt.eq("") & (conf.isna() | ~conf.between(0, 1)))
    bit.update(filas_invalidas=int(invalid.sum()), sin_confianza=int(df["sin_confianza"].sum()),
               clases_desconocidas=int((~df["clase_conocida"] & ~empty).sum()))
    df["confianza"] = conf
    df["valida"] = ~invalid
    real = df["clase_real"].astype(str).str.strip()
    df["clase_real"] = real.map(lambda t: CATALOG.get(_norm(t), t) if t else None)
    df["dia"] = (df["fecha"] - START).dt.days
    df["dia_captura"] = (df["fecha_captura"] - START).dt.days
    return df, bit


# ---------------------------------------------------------------- política y operación
@dataclass
class Fitted:
    umbrales: dict
    umbral_unico: float
    corte_id: str
    referencia_conf: np.ndarray
    referencia_mezcla: pd.Series
    filas_ajuste: int
    ultimo_dia: int
    umbral_psi_conf: float = MAX_PSI
    umbral_psi_mezcla: float = MAX_PSI


def fit(hist: pd.DataFrame, c: rp.Costos) -> Fitted:
    """Cortes de ``review_policy`` con revisiones cerradas antes del primer día con revisiones abiertas."""
    closed = hist["dia"] < HIST_DAYS - PENDING_DAYS
    d = hist[closed & hist["valida"] & hist["clase_conocida"] & ~hist["sin_confianza"]].reset_index(drop=True)
    d["revisada"] = d["clase_real"].notna()
    d["error"] = d["revisada"] & (d["clase_real"] != d["clase_predicha"])
    w, _ = rp.weights(d)
    thr = rp.fit_thresholds(d, w, c)
    single = rp.fit_thresholds(d, w, c, by_class=False)[rp.GLOBAL]
    ref_conf, ref_mix = d["confianza"].to_numpy(), d["clase_predicha"].value_counts()
    # Umbrales del monitor calibrados solo con el historial cerrado: 1.5 × el mayor PSI diario observado
    # (con ~60 placas por día el PSI es ruidoso), nunca menos que MAX_PSI.
    daily = [(psi(ref_conf, g["confianza"].to_numpy()), psi_mix(ref_mix, g["clase_predicha"])) for _, g in d.groupby("dia")]
    u_conf = max(MAX_PSI, 1.5 * max(x for x, _ in daily))
    u_mix = max(MAX_PSI, 1.5 * max(y for _, y in daily))
    key = dict(umbrales={k: round(v, 6) for k, v in thr.items()}, unico=round(single, 6), costos=[c.revision, c.escape],
               dias=[int(d["dia"].min()), int(d["dia"].max())], n=len(d), psi=[round(u_conf, 6), round(u_mix, 6)])
    return Fitted(thr, single, hashlib.sha256(json.dumps(key, sort_keys=True).encode()).hexdigest()[:12],
                  ref_conf, ref_mix, len(d), int(d["dia"].max()), u_conf, u_mix)


def psi(ref: np.ndarray, cur: np.ndarray, bins: int = 10) -> float:
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    p = np.histogram(ref, edges)[0] / len(ref) + 1e-4
    q = np.histogram(cur, edges)[0] / max(1, len(cur)) + 1e-4
    return float(((q - p) * np.log(q / p)).sum())


def psi_mix(ref_counts: pd.Series, cur: pd.Series) -> float:
    """PSI de la mezcla de clases predichas, con suavizado de Laplace (+0.5 por clase)."""
    cls = sorted(set(ref_counts.index) | set(CLASSES))
    p = ref_counts.reindex(cls, fill_value=0) + 0.5
    q = cur.value_counts().reindex(cls, fill_value=0) + 0.5
    p, q = p / p.sum(), q / q.sum()
    return float(((q - p) * np.log(q / p)).sum())


def decide(day: pd.DataFrame, f: Fitted, policy: str, cap: int, suspend: bool) -> tuple[np.ndarray, np.ndarray]:
    """Decisión por placa: revisar / aceptar / liberada_sin_cupo / retenida, con su motivo."""
    n = len(day)
    forced = (~day["clase_conocida"] | day["sin_confianza"]).to_numpy()
    conf = day["confianza"].fillna(-1).to_numpy()
    order = np.argsort(day["id_placa"].to_numpy(), kind="stable")      # orden de llegada
    if policy == "revisar_todas" or suspend:
        cand, prio = ~forced, None
    elif policy == "umbral_unico":
        cand, prio = ~forced & (conf < f.umbral_unico), None
    else:
        thr = day["clase_predicha"].map(f.umbrales).fillna(f.umbrales[rp.GLOBAL]).to_numpy()
        cand, prio = ~forced & (conf < thr), thr - conf
    queue = [i for i in order if forced[i]]
    rest = [i for i in order if cand[i]]
    if prio is not None:
        rest = sorted(rest, key=lambda i: -prio[i])
    dec = np.full(n, "aceptar", object)
    why = np.full(n, "Confianza sobre el corte de costo", object)
    if policy == "revisar_todas" or suspend:
        why[:] = "Sin aceptación automática: se revisa por orden de llegada"
    slots = cap
    for i in queue:
        if slots > 0:
            dec[i], why[i], slots = "revisar", "Clase desconocida o sin confianza: decide una persona", slots - 1
        else:
            dec[i], why[i] = "retenida", "Clase desconocida o sin confianza y sin cupo: espera revisión"
    for i in rest:
        if slots > 0:
            dec[i], slots = "revisar", slots - 1
            if not (policy == "revisar_todas" or suspend):
                why[i] = "Confianza bajo el corte, dentro del cupo"
        else:
            dec[i], why[i] = "liberada_sin_cupo", "Debía revisarse pero no hubo cupo: aviso al supervisor"
    if suspend and policy != "revisar_todas":
        why = np.array([("Aceptación automática suspendida; " + w) if d != "revisar" or not forced[i] else w
                        for i, (d, w) in enumerate(zip(dec, why))], object)
    return dec, why


def operate(sc: Scenario, c: rp.Costos | None = None, escala: float = 1.0, seed: int = 3) -> dict:
    c = c or rp.Costos(revision=COSTO_REVISION, escape=1_500.0 * escala)
    hist_raw, hist_log = inject(truth_history(seed), Imperfections(), seed=21, pending_from=HIST_DAYS - PENDING_DAYS)
    hist, hist_bit = reconcile(hist_raw)
    f = fit(hist, c)
    truth = truth_ops(sc)
    ops_raw, ops_log = inject(truth, sc.ops, seed=31, invalid_by_day=sc.invalidos)
    ops, _ = reconcile(ops_raw)
    tr = truth.set_index("id_placa")["clase_real"]
    rows, days = [], []
    for k in range(1, OPS_DAYS + 1):
        dnum = HIST_DAYS + k - 1
        day = ops[ops["dia_captura"] == dnum].reset_index(drop=True)
        valid = day[day["valida"]].reset_index(drop=True)
        real = valid["id_placa"].map(tr).to_numpy()
        ok = valid["clase_conocida"] & ~valid["sin_confianza"]
        p_conf = psi(f.referencia_conf, valid.loc[ok, "confianza"].to_numpy())
        p_mix = psi_mix(f.referencia_mezcla, valid.loc[ok, "clase_predicha"])
        gate = []
        if (len(day) - len(valid)) / max(1, len(day)) > MAX_INVALIDAS:
            gate.append(f"{(len(day) - len(valid)) / len(day):.0%} de filas inválidas")
        if p_conf > f.umbral_psi_conf:
            gate.append(f"cambio en la distribución de confianza (PSI {p_conf:.2f})")
        if p_mix > f.umbral_psi_mezcla:
            gate.append(f"cambio en la mezcla de clases (PSI {p_mix:.2f})")
        rec = dict(dia=k, fecha=str((START + pd.Timedelta(days=dnum)).date()), placas=len(day), validas=len(valid),
                   excluidas=len(day) - len(valid), psi_confianza=p_conf, psi_mezcla=p_mix, suspendido=bool(gate),
                   motivo="; ".join(gate), mezcla_inyectada=k in sc.mezcla, descalibrada_inyectada=k in sc.descalibrada,
                   clase_nueva=int((~valid["clase_conocida"]).sum()), tardias=int((day["dia"] < day["dia_captura"]).sum()))
        for pol in POLICIES:
            dec, why = decide(valid, f, pol, sc.capacidad, bool(gate))
            released = np.isin(dec, ["aceptar", "liberada_sin_cupo"])
            wrong = released & (valid["clase_predicha"].to_numpy() != real)
            ec = np.array([costo_error(r, p, escala) for r, p in zip(real, valid["clase_predicha"])]) * released
            rec |= {f"{pol}_revisiones": int((dec == "revisar").sum()), f"{pol}_liberadas_sin_cupo": int((dec == "liberada_sin_cupo").sum()),
                    f"{pol}_retenidas": int((dec == "retenida").sum()), f"{pol}_mal_clasificadas": int(wrong.sum()),
                    f"{pol}_severas": int((wrong & np.isin(real, list(SEVERAS))).sum()),
                    f"{pol}_costo": float(c.revision * (dec == "revisar").sum() + ec.sum())}
            rows.append(pd.DataFrame(dict(escenario=sc.id, politica=pol, dia=k, id_placa=valid["id_placa"], linea=valid["linea"],
                                          fecha=valid["fecha"].dt.strftime("%Y-%m-%d"), clase_predicha=valid["clase_predicha"],
                                          confianza=valid["confianza"].round(4), decision=dec, motivo=why, cortes=f.corte_id,
                                          origen=ORIGEN, costo_error=np.round(ec, 2))))
        days.append(rec)
    dd = pd.DataFrame(days)
    return dict(escenario=sc, costos=c, escala=escala, ajuste=f, historial=hist_bit, manifiesto=dict(historial=hist_log, operacion=ops_log),
                dias=dd, decisiones=pd.concat(rows, ignore_index=True), resumen=summary(dd, c.semilla))


def _boot(s: np.ndarray, seed: int, level: float = 0.90, reps: int = 2000) -> tuple[float, float, str]:
    b = s[np.random.default_rng(seed).integers(0, len(s), size=(reps, len(s)))].sum(axis=1)
    lo, hi = np.quantile(b, [(1 - level) / 2, (1 + level) / 2])
    return float(lo), float(hi), "conviene" if lo > 0 else ("desfavorable" if hi < 0 else "indiferente")


def summary(dd: pd.DataFrame, seed: int) -> dict:
    out = {}
    for pol in POLICIES:
        for m in ("costo", "revisiones", "liberadas_sin_cupo", "retenidas", "mal_clasificadas", "severas"):
            out[f"{pol}_{m}"] = float(dd[f"{pol}_{m}"].sum()) if m == "costo" else int(dd[f"{pol}_{m}"].sum())
    for base in ("revisar_todas", "umbral_unico"):
        s = (dd[f"{base}_costo"] - dd["priorizada_costo"]).to_numpy()
        lo, hi, v = _boot(s, seed)
        out |= {f"ahorro_vs_{base}": float(s.sum()), f"ahorro_vs_{base}_lo": lo, f"ahorro_vs_{base}_hi": hi, f"veredicto_vs_{base}": v}
    out |= dict(dias_suspendidos=int(dd["suspendido"].sum()), max_revisiones_dia=int(dd[[f"{p}_revisiones" for p in POLICIES]].max().max()))
    return out


# ---------------------------------------------------------------- criterios, sensibilidad, Power BI y evidencia
def check_reconciliation(seed: int = 3) -> dict:
    """C1: cada regla del manifiesto del historial, comparada contra la verdad sintética."""
    truth = truth_history(seed)
    raw, log = inject(truth, Imperfections(), seed=21, pending_from=HIST_DAYS - PENDING_DAYS)
    data, bit = reconcile(raw)
    ids = {r["regla"]: set(r["ids"]) for r in log}
    t, d = truth.set_index("id_placa"), data.set_index("id_placa")
    v = d[d["valida"] & ~d["sin_confianza"]]
    sc = v.loc[sorted(ids["D3"] & set(v.index))]
    var = sorted(ids["D4"])
    pend = d.loc[sorted(ids["D5"])]
    late = d.loc[sorted(ids["D6"])]
    rest = v.loc[sorted(set(v.index) - ids["D4"])]
    return dict(
        D1=bool(d.index.is_unique and bit["duplicados"] == len(ids["D1"]) and len(d) == len(t)),
        D2=bool(d.loc[sorted(ids["D2"]), "sin_confianza"].all() and d["sin_confianza"].sum() == len(ids["D2"])),
        D3=bool(np.allclose(sc["confianza"], t.loc[sc.index, "confianza"], atol=5e-5)),
        D4=bool((d.loc[var, "clase_predicha"] == t.loc[var, "clase_predicha"]).all() and set(d.loc[d["clase_conocida"], "clase_predicha"]) <= set(CLASSES)),
        D5=bool(pend["clase_real"].isna().all()),
        D6=bool(((late["dia_captura"] - late["dia"]) == 1).all() and (late["dia"] == t.loc[late.index, "dia"]).all()),
        D7=bool(not d.loc[sorted(ids["D7"]), "valida"].any() and (~d["valida"]).sum() == len(ids["D7"])),
        resto_igual=bool((rest["clase_predicha"] == t.loc[rest.index, "clase_predicha"]).all()
                         and np.allclose(rest["confianza"], t.loc[rest.index, "confianza"], atol=5e-5)),
        filas=len(d), invalidas=int((~d["valida"]).sum()))


def sensitivity(caps=(8, 12, 18, 25, 35, 0), escalas=(0.25, 1.0, 4.0)) -> pd.DataFrame:
    base, out = SCENARIOS[0], []
    grid = [(cap, e, False) for e in escalas for cap in caps] + [(25, e, True) for e in escalas]
    for cap, e, bad in grid:
        sc = replace(base, capacidad=cap or 10_000, descalibrada=tuple(range(1, OPS_DAYS + 1)) if bad else ())
        r = operate(sc, escala=e)["resumen"]
        out.append(dict(capacidad=cap or "sin límite", escala_costo_error=e, confianza_descalibrada=bad,
                        **{k: round(r[k], 2) if isinstance(r[k], float) else r[k] for k in
                           ("ahorro_vs_revisar_todas", "ahorro_vs_revisar_todas_lo", "ahorro_vs_revisar_todas_hi", "veredicto_vs_revisar_todas",
                            "ahorro_vs_umbral_unico", "ahorro_vs_umbral_unico_lo", "ahorro_vs_umbral_unico_hi", "veredicto_vs_umbral_unico",
                            "dias_suspendidos")}))
    return pd.DataFrame(out)


BI_COLUMNS = ("fecha_corte", "escenario", "politica", "clase", "piezas", "a_revision", "aceptadas", "retenidas",
              "errores_en_aceptadas", "costo_revision", "costo_escape", "costo_errores", "suspendido", "clausula_iso9001")


def bi_export(runs: dict) -> pd.DataFrame:
    """``seguimiento_revision.csv`` para Power BI: una fila por fecha de corte, escenario, política y clase.

    ``costo_escape`` es el costo medio por placa mal clasificada liberada, de modo que la medida DAX
    ``errores_en_aceptadas × costo_escape`` reproduce el costo de la matriz."""
    out = []
    for r in runs.values():
        dec = r["decisiones"]
        susp = r["dias"].set_index("dia")["suspendido"]
        for (pol, dia, fecha, cls), g in dec.groupby(["politica", "dia", "fecha", "clase_predicha"], sort=True):
            rel = g["decision"].isin(["aceptar", "liberada_sin_cupo"])
            err, ce = int((g["costo_error"] > 0).sum()), float(g["costo_error"].sum())
            out.append(dict(fecha_corte=fecha, escenario=r["escenario"].id, politica=pol, clase=cls, piezas=len(g),
                            a_revision=int((g["decision"] == "revisar").sum()), aceptadas=int(rel.sum()),
                            retenidas=int((g["decision"] == "retenida").sum()), errores_en_aceptadas=err,
                            costo_revision=r["costos"].revision, costo_escape=round(ce / err, 4) if err else 0.0, costo_errores=round(ce, 2),
                            suspendido=bool(susp[dia]), clausula_iso9001="8.6 Liberación; 8.7 Control de salidas no conformes"))
    return pd.DataFrame(out, columns=BI_COLUMNS)


def acceptance(runs: dict, rec: dict) -> dict:
    s1, s2, s3 = (runs[k]["resumen"] for k in ("S1", "S2", "S3"))
    dec = pd.concat([r["decisiones"] for r in runs.values()])
    d3 = runs["S3"]["dias"]
    unknown = dec[dec["clase_predicha"] == NEW_CLASS]
    gates = d3["motivo"].str.len() > 0
    return dict(
        C1=all(rec[f"D{i}"] for i in range(1, 8)) and rec["resto_igual"],
        C2=all(r["ajuste"].ultimo_dia < HIST_DAYS - PENDING_DAYS for r in runs.values()),
        C3=all((r["dias"][[f"{p}_revisiones" for p in POLICIES]] <= r["escenario"].capacidad).all().all() for r in runs.values()),
        C4=bool(dec["origen"].eq(ORIGEN).all()),
        C5=s1["ahorro_vs_revisar_todas_lo"] > 0,
        C6=s2["priorizada_costo"] <= s2["umbral_unico_costo"],
        C7=bool(len(unknown) > 0 and not unknown["decision"].isin(["aceptar", "liberada_sin_cupo"]).any() and d3.loc[gates, "suspendido"].all()),
        C8=bool(dec[["escenario", "politica", "dia", "id_placa", "clase_predicha", "decision", "motivo", "cortes"]].notna().all().all()),
        C9=all(abs(r["dias"][f"{p}_costo"].sum() - (r["costos"].revision * (r["decisiones"].query("politica == @p")["decision"] == "revisar").sum()
                                                     + r["decisiones"].query("politica == @p")["costo_error"].sum())) < 1e-6
               for r in runs.values() for p in POLICIES),
    )


def _r(x):
    if isinstance(x, (float, np.floating)):
        return round(float(x), 4)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    if isinstance(x, dict):
        return {k: _r(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_r(v) for v in x]
    return x


def run(out: Path = OUT) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    runs = {sc.id: operate(sc) for sc in SCENARIOS}
    rec = check_reconciliation()
    acc = acceptance(runs, rec)
    s1 = runs["S1"]
    f = s1["ajuste"]
    manifest = dict(empresa=EMPRESA, origen=ORIGEN, fuente=str(SOURCE.relative_to(ROOT).as_posix()),
                    filas_fuente_usadas="solo origen == 'validación cruzada' (1,552); el holdout (389) no se lee",
                    semillas=dict(historial=3, imperfecciones_historial=21, operacion=4, imperfecciones_operacion=31),
                    reglas=dict(historial=[dict(regla=r["regla"], tipo=r["tipo"], filas=r["filas"]) for r in s1["manifiesto"]["historial"]])
                    | {k: [dict(regla=r["regla"], tipo=r["tipo"], filas=r["filas"]) for r in v["manifiesto"]["operacion"]] for k, v in runs.items()},
                    conciliacion_historial=s1["historial"])
    results = dict(empresa=EMPRESA, nivel="A (demostración operativa reproducible, datos operativos sintéticos)",
                   costos=dict(revision=COSTO_REVISION, escape_para_ajustar=1_500.0, matriz="150 misma disposición; 1,500 otra; 6,000 si la real es Bumps u Other_Faults",
                               moneda="MXN de escenario"),
                   cortes=dict(id=f.corte_id, por_clase={k: round(v, 4) for k, v in f.umbrales.items()}, unico=round(f.umbral_unico, 4),
                               filas_ajuste=f.filas_ajuste, ultimo_dia_ajuste=f.ultimo_dia),
                   conciliacion=rec, criterios=acc,
                   escenarios={k: dict(nombre=r["escenario"].nombre, capacidad=r["escenario"].capacidad, resumen=r["resumen"],
                                       dias=r["dias"].to_dict("records")) for k, r in runs.items()})
    (out / "manifest.json").write_text(json.dumps(_r(manifest), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (out / "results.json").write_text(json.dumps(_r(results), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    pd.concat([r["decisiones"] for r in runs.values()]).to_csv(out / "decisions.csv", index=False, lineterminator="\n")
    inject(truth_history(), Imperfections(), seed=21, pending_from=HIST_DAYS - PENDING_DAYS)[0].to_csv(
        out / "raw_export_history.csv", index=False, lineterminator="\n")
    bi_export(runs).to_csv(out / "seguimiento_revision.csv", index=False, lineterminator="\n")
    sensitivity().to_csv(out / "sensitivity.csv", index=False, lineterminator="\n")
    files = sorted(p for p in out.iterdir() if p.name != "evidence.json")
    code = [ROOT / "src/quality_ml" / n for n in ("pilot_p02.py", "review_policy.py")] + [SOURCE]
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()  # noqa: E731
    evidence = dict(piloto="P02", nivel="A", comando="python -B -m quality_ml.pilot_p02",
                    python=".".join(map(str, sys.version_info[:2])), pandas=pd.__version__, numpy=np.__version__,
                    codigo_y_fuente={p.relative_to(ROOT).as_posix(): sha(p) for p in code},
                    salidas={p.name: sha(p) for p in files}, criterios=acc)
    (out / "evidence.json").write_text(json.dumps(_r(evidence), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return results


if __name__ == "__main__":
    res = run()
    print(json.dumps(_r(dict(criterios=res["criterios"], **{k: v["resumen"] for k, v in res["escenarios"].items()})), ensure_ascii=False, indent=1))
