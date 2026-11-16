# POWERBI_VISUAL_REGRESSION

Orden: **OWNER-PBI-REN-001** · Fase 5 — Comprobación de las cinco páginas
Fecha: 2026-11-14 · Responsable: PRODUCCIÓN
Gate: **G5** · Resultado: **NO ALCANZADO** — estructura verificada; **renderización NO comprobada**

> **ACTUALIZACIÓN 2026-11-15 — G5 sigue abierto, y es el único gate de validación
> que queda.** Power BI Desktop abrió el proyecto y se validó su motor (G2, G3,
> G4 y G6 pasaron; ver
> [`POWERBI_DESKTOP_RUNTIME_EVIDENCE.md`](POWERBI_DESKTOP_RUNTIME_EVIDENCE.md)).
> Eso **no** alcanza a esta fase: los visuales viven en la capa de informe
> (`.Report`) y el motor no sabe nada del lienzo. Sigue sin verificarse la
> renderización, la legibilidad y el clic real en los segmentadores.
>
> Lo que sí quedó demostrado y refuerza la predicción del apartado 4: en el motor,
> `Final Macro-F1 (389)` **no cambia** al filtrar por A300 mientras `ML Rows`
> baja de 389 a 156. La semántica de filtrado es la esperada; falta confirmar que
> los visuales la reflejan en pantalla.

> **La orden es explícita: «no se aceptará una inspección JSON como sustituto de
> una prueba en Desktop».** PRODUCCIÓN no dispone de la interfaz nativa, de modo
> que este documento **no** declara G5 superado. Acredita únicamente que la
> estructura de las cinco páginas está íntegra y que todo campo de la página ML
> resuelve a un objeto existente del modelo — condición necesaria para que
> rendericen, no prueba de que lo hagan.

Evidencia ejecutable: [`evidence/powerbi_static_validation.py`](evidence/powerbi_static_validation.py)
(**77/77 PASS**) y `tests/test_bi_integration.py::test_draft_structure_and_field_bindings`.

---

## 1. Las cinco páginas

`pages.json` (SHA256 de línea base, sin cambios por el renombrado):

| # | Identificador | `displayName` | Lienzo | Visuales | Tipo de página |
|---|---|---|---|---:|---|
| 1 | `5ee9939d0101076d3381` | `Resumen ejecutivo ` | 1280×720 | 10 | Default (activa) |
| 2 | `f50491653678cb19a699` | `Control y capacidad` | 1280×720 | 8 | None |
| 3 | `1f75dde540a696f2b18f` | `Exploracion` | 1280×720 | 13 | Drillthrough |
| 4 | `cb973d91eb46886907c2` | `Tooltip Pareto` | 320×240 | 3 | None |
| 5 | `ml_performance_review` | `MODEL PERFORMANCE & REVIEW` | 1280×1040 | 12 | None |

`activePageName` = `5ee9939d0101076d3381`. Orden de páginas conforme a la
línea base. **46 visuales** en total.

Los `displayName` corresponden a las cinco páginas enumeradas en §9 de la orden
(resumen ejecutivo, control y capacidad, exploración, tooltip Pareto, MODEL
PERFORMANCE & REVIEW). El espacio final de `Resumen ejecutivo ` es original y se
conserva tal cual; no se corrige para no alterar un identificador de
presentación sin necesidad funcional.

## 2. Conservación de las cuatro páginas anteriores

| Comprobación | Resultado |
|---|---|
| Las 4 páginas existen con su identificador original | ✅ |
| Recuento de visuales (10, 8, 13, 3) | ✅ sin cambios |
| `page.json` y los 34 `visual.json` con SHA256 de línea base | ✅ |
| `pageBinding` (Default / None / Drillthrough / None) | ✅ sin cambios |
| Tema base `CY26SU07.json` | ✅ sin cambios |

Estructura y narrativa conservadas: **ningún byte** de las cuatro páginas
anteriores fue modificado. Lo garantiza
`test_previous_powerbi_preserved`, que las compara contra
`pre_ml_powerbi_hashes.json` sin excepción alguna.

## 3. Página `MODEL PERFORMANCE & REVIEW` — los 12 componentes

Composición verificada: **4 tarjetas + 3 segmentadores + 4 tablas + 1 nota = 12**.

| Tipo | x | y | Ancho×Alto | Identificador | Campos |
|---|---:|---:|---|---|---|
| `textbox` | 20 | 10 | 1240×95 | `dec66923be3e0ce1773b` | nota contextual (sin campos) |
| `cardVisual` | 20 | 115 | 290×110 | `41016657f394c4a32f9d` | `Final Macro-F1 (389)` |
| `cardVisual` | 330 | 115 | 290×110 | `1966e8a2cbc5a1f35d63` | `Final Balanced Accuracy (389)` |
| `cardVisual` | 640 | 115 | 290×110 | `959d3d8818f13287914c` | `Candidate Review Rate` |
| `cardVisual` | 950 | 115 | 290×110 | `911dd523ba116fd6b8e7` | `ML Rows` |
| `listSlicer` | 20 | 240 | 395×170 | `9a92b3499d88046e9e2d` | `steel_type` |
| `listSlicer` | 435 | 240 | 395×170 | `58417b2a223783b58382` | `steel_plate_thickness` |
| `listSlicer` | 850 | 240 | 395×170 | `7b2b9998ac1edc630a60` | `actual_defect` |
| `tableEx` | 20 | 430 | 600×250 | `d0bbe55d7de7f662f82e` | `actual_defect`, `predicted_defect`, `ML Confusion Errors` |
| `tableEx` | 640 | 430 | 620×250 | `86aa80aa4ec94df84fcc` | `actual_defect`, `ML Rows`, `ML Errors`, `Observed Error Rate`, `Segment Support` |
| `tableEx` | 20 | 700 | 600×300 | `ff0139d07c592e9ae929` | `confidence_bin`, `ML Rows`, `Mean Confidence`, `Observed Accuracy`, `Segment Support` |
| `tableEx` | 640 | 700 | 620×300 | `c97ace4c8fef2cee8fa0` | `review_status`, `ML Rows`, `ML Errors`, `Observed Error Rate` |

### 3.1 Comprobaciones estructurales superadas

| Comprobación | Resultado |
|---|---|
| Componentes totales | 12 ✅ |
| 4 tarjetas (`cardVisual`) | ✅ |
| 3 segmentadores (`listSlicer`) | ✅ |
| 4 tablas analíticas (`tableEx`) | ✅ |
| 1 nota contextual (`textbox`) | ✅ |
| Todo campo apunta a la entidad `ML_Holdout` | ✅ |
| Todo campo existe como columna o medida del modelo | ✅ (lista de huérfanos vacía) |
| El nombre de cada visual coincide con su directorio | ✅ |
| Ningún visual sale del lienzo 1280×1040 | ✅ |
| Ningún par de visuales se solapa | ✅ |

Las dos últimas las verifica `test_draft_structure_and_field_bindings` con
comprobación geométrica par a par.

### 3.2 Ausencia de elementos rotos — alcance real

«Ningún elemento roto» se ha verificado en el único sentido comprobable sin la
aplicación: **ningún visual referencia un campo inexistente**. Las 29 vinculaciones
de campo de los 11 visuales con consulta resuelven a una de las 16 columnas o a
una de las 12 medidas de `ML_Holdout`.

Esto descarta la causa más común de visual en blanco tras un renombrado. **No**
descarta un fallo de renderización, un visual recortado, texto ilegible ni un
error del motor. Eso exige Desktop.

### 3.3 Nota contextual

Texto conservado íntegro, con sus calificaciones científicas:

> FINAL HOLDOUT: 389 known-defect observations. Full-observation classification.
> Review is a development-only candidate, applied post-hoc: confidence >=0.80
> high; 0.50-0.80 review; <0.50 low (also review). Final scores always refer to
> all 389 rows; other visuals follow ML filters. Small segments are descriptive;
> no prospective validation.

Advierte expresamente de que las métricas finales se refieren siempre a las 389
filas y que los segmentos pequeños son descriptivos. **No debe eliminarse ni
abreviarse.**

## 4. Interacción de filtros — predicción estructural

De la definición de las medidas (ver
[`POWERBI_MODEL_DAX_VALIDATION.md`](POWERBI_MODEL_DAX_VALIDATION.md) §4) se
deduce el comportamiento que **debe** observarse en Desktop:

| Al activar un segmentador | Comportamiento esperado |
|---|---|
| Tarjeta `Final Macro-F1 (389)` | **no cambia** (literal DAX) |
| Tarjeta `Final Balanced Accuracy (389)` | **no cambia** (literal DAX) |
| Tarjeta `Candidate Review Rate` | **cambia** |
| Tarjeta `ML Rows` | **cambia** |
| Las 4 tablas analíticas | **cambian** |
| Las páginas 1–4 | **no cambian** (`ML_Holdout` desconectada) |

Cualquier desviación respecto a esta tabla en Desktop es un **FAIL** de G5 que
debe investigarse antes de continuar, no justificarse.

## 5. Qué falta para cerrar G5

Debe ejecutarse en Power BI Desktop, con captura auténtica de cada punto:

1. Abrir cada una de las cinco páginas y confirmar que **renderiza completa**.
2. Confirmar que ningún visual aparece en blanco, con error o recortado.
3. Comprobar la legibilidad de la nota contextual (14 px) y de las 4 tablas.
4. Ejercitar los segmentadores de las cuatro páginas originales y confirmar que
   su comportamiento es el previo.
5. Ejercitar los 3 segmentadores ML y verificar la tabla del apartado 4.
6. Comprobar la consistencia numérica entre tarjetas y tablas.
7. Confirmar el drillthrough de `Exploracion` y el tooltip de `Tooltip Pareto`.
8. Confirmar que las cifras coinciden con
   [`POWERBI_RECONCILIATION_RESULTS.md`](POWERBI_RECONCILIATION_RESULTS.md).

| Control de G5 | Estado |
|---|---|
| Las 5 páginas existen con su estructura | ✅ verificado |
| Las 4 páginas anteriores inalteradas byte a byte | ✅ verificado |
| Los 12 componentes de la página ML | ✅ verificado |
| Todo campo resuelve a un objeto del modelo | ✅ verificado |
| Geometría dentro del lienzo y sin solapes | ✅ verificado |
| **Renderización** | ⛔ **NO EJECUTADO** |
| **Interacción y filtros** | ⛔ **NO EJECUTADO** |
| **Legibilidad** | ⛔ **NO EJECUTADO** |
| **Consistencia numérica en pantalla** | ⛔ **NO EJECUTADO** |

**G5: NO ALCANZADO.** La orden impide declararlo con inspección estructural.
