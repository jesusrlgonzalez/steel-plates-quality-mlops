# POWERBI_RECONCILIATION_RESULTS

Orden: **OWNER-PBI-REN-001** · Fase 6 — Reconciliación científica
Fecha: 2026-11-14 · Responsable: PRODUCCIÓN
Gate: **G6** · Resultado: **✅ PASS** (actualizado 2026-11-15)

> **ACTUALIZACIÓN 2026-11-15 — G6 SUPERADO.** Las cifras se leyeron del **motor
> de Power BI Desktop**, no del CSV. Los diez indicadores obligatorios, los tres
> segmentos (A300 156/121/122 · A400 233/186/139 · Pastry 32/20/29), la confusión
> Bumps → Other_Faults = 21, los siete soportes y errores por clase, los tres
> estados de revisión (128/173/88) y los seis atributos de `row_id` 1277
> coinciden **exactamente**.
>
> La tolerancia `1e-12` se verificó haciendo que **el propio motor** calculase la
> resta contra los literales congelados: las cuatro diferencias son
> **exactamente 0** y la igualdad en DAX devuelve `EXACTO`. Se comprobó también
> que `Final Macro-F1 (389)` **no cambia** al filtrar por A300 mientras
> `ML Rows` baja a 156. Evidencia:
> [`POWERBI_DESKTOP_RUNTIME_EVIDENCE.md`](POWERBI_DESKTOP_RUNTIME_EVIDENCE.md) §5.
>
> Lo que sigue conserva su redacción original: reconciliaba el **origen de
> datos**. El motor confirmó cada cifra. El apartado 8 («qué falta para cerrar
> G6») está cumplido salvo la lectura en pantalla, que pertenece a G5.

Evidencia ejecutable: [`evidence/powerbi_static_validation.py`](evidence/powerbi_static_validation.py)
(33 comprobaciones F6, **todas PASS**).

Fuentes de verdad, ninguna modificada:
- `reports/ml/final_holdout/metrics.json` — métricas congeladas
- `reports/ml/integration/reconciliation_expected.json` — reconciliación congelada
- `powerbi/data/ml_holdout_evaluation.csv` — origen de la tabla `ML_Holdout`

**No se reentrenó ni se modificó el modelo.** No se reejecutó la evaluación final
del holdout.

---

## 1. Indicadores obligatorios

| Indicador | Valor obligatorio | Observado | Fuente | Diferencia | Resultado |
|---|---:|---:|---|---:|---|
| Holdout | 389 | 389 | CSV | 0 | ✅ |
| Aciertos | 307 | 307 | CSV (`correct_prediction=1`) | 0 | ✅ |
| Errores | 82 | 82 | CSV (`correct_prediction=0`) | 0 | ✅ |
| Exactitud | ≈ 0.7892030848 | 0.7892030848329049 | `metrics.json` | ≤ 1e-12 | ✅ |
| Macro-F1 | 0.8146728101764369 | 0.8146728101764369 | `metrics.json` | 0 | ✅ |
| Balanced accuracy | 0.8048726799979933 | 0.8048726799979933 | `metrics.json` | 0 | ✅ |
| Casos de revisión candidata | 261 | 261 | CSV (`review_required=1`) | 0 | ✅ |
| Casos aceptados | 128 | 128 | CSV (`review_required=0`) | 0 | ✅ |
| Errores enviados a revisión | 81 | 81 | CSV (`review_required=1 ∧ correct=0`) | 0 | ✅ |
| Errores no capturados | 1 | 1 | CSV (`review_required=0 ∧ correct=0`) | 0 | ✅ |

Criterios aplicados tal como exige la orden: **igualdad exacta** en los conteos
y **tolerancia absoluta `1e-12`** en las métricas numéricas sin redondear.

Comprobaciones cruzadas adicionales superadas:

| Comprobación | Resultado |
|---|---|
| Exactitud recomputada (307/389) coincide con `metrics.json` dentro de 1e-12 | ✅ |
| Macro-F1 de `metrics.json` == `reconciliation_expected.json` | ✅ igualdad exacta |
| Balanced accuracy de `metrics.json` == `reconciliation_expected.json` | ✅ igualdad exacta |
| 307 + 82 = 389 | ✅ |
| 261 + 128 = 389 | ✅ |
| 81 + 1 = 82 | ✅ |
| `row_id` únicos | 389 ✅ |

Los literales DAX de `ML_Holdout.tmdl` son **exactamente**
`0.8146728101764369` y `0.8048726799979933`: coincidencia de cadena, no sólo
numérica.

## 2. Comprobaciones por segmento

| Segmento | Registros | Aciertos | Revisiones | Resultado |
|---|---:|---:|---:|---|
| A300 | 156 / **156** | 121 / **121** | 122 / **122** | ✅ |
| A400 | 233 / **233** | 186 / **186** | 139 / **139** | ✅ |
| Pastry (clase real) | 32 / **32** | 20 / **20** | 29 / **29** | ✅ |

(obligatorio / observado). 156 + 233 = 389 ✅.

| Confusión | Esperado | Observado | Resultado |
|---|---:|---:|---|
| Bumps → Other_Faults | 21 | 21 | ✅ |

## 3. Registro `row_id = 1277`

Error de alta confianza que debe conservarse tal cual:

| Atributo | Valor obligatorio | Observado | Resultado |
|---|---|---|---|
| `actual_defect` | `Other_Faults` | `Other_Faults` | ✅ |
| `predicted_defect` | `K_Scatch` | `K_Scatch` | ✅ |
| `confidence` | 1.0 | 1.0 | ✅ |
| `correct_prediction` | 0 (es un error) | 0 | ✅ |
| `review_required` | 0 (fuera de revisión) | 0 | ✅ |
| `review_status` | `HIGH_CONFIDENCE` | `HIGH_CONFIDENCE` | ✅ |

Este registro **es** el «error no capturado» del apartado 1: el único error que
la política de revisión candidata no envía a revisión, por tener confianza
máxima. Es el ejemplo más importante del límite de la política y debe seguir
visible en la tabla de estados de revisión.

Doble verificación: `test_export_reconciles_frozen_predictions_and_role` lo
comprueba de forma independiente sobre el `DataFrame` reconstruido.

## 4. Conteos por clase real

| Clase | Soporte esperado | Observado | Errores esperados | Observados | Resultado |
|---|---:|---:|---:|---:|---|
| Pastry | 32 | 32 | 12 | 12 | ✅ |
| Z_Scratch | 38 | 38 | 5 | 5 | ✅ |
| K_Scatch | 78 | 78 | 7 | 7 | ✅ |
| Stains | 14 | 14 | 2 | 2 | ✅ |
| Dirtiness | 11 | 11 | 1 | 1 | ✅ |
| Bumps | 81 | 81 | 26 | 26 | ✅ |
| Other_Faults | 135 | 135 | 29 | 29 | ✅ |
| **Total** | **389** | **389** | **82** | **82** | ✅ |

## 5. Conteos por estado de revisión

| Estado | Esperado | Observado | Resultado |
|---|---:|---:|---|
| `HIGH_CONFIDENCE` | 128 | 128 | ✅ |
| `REVIEW_REQUIRED` | 173 | 173 | ✅ |
| `LOW_CONFIDENCE` | 88 | 88 | ✅ |
| **Total** | **389** | **389** | ✅ |

173 + 88 = 261 = casos de revisión candidata ✅.
`HIGH_CONFIDENCE` = 128 = casos aceptados ✅.

## 6. Separación del holdout respecto al análisis original

| Comprobación | Resultado |
|---|---|
| `dataset_role` único `FINAL_HOLDOUT_EVALUATION` en las 389 filas | ✅ |
| `policy_application` = `POST_HOC_ONLY` en las 389 filas | ✅ (`test_export_reconciles…`) |
| `row_id` del holdout disjuntos de las posiciones de entrenamiento | ✅ (`test_export_reconciles…`) |
| `ML_Holdout` sin relación con el esquema estrella | ✅ |
| 1 941 observaciones originales intactas | ✅ |

Los 389 registros **no** se incorporan a los 1 941. Al no haber relación, el
motor no puede propagar filtro entre ambos conjuntos.

## 7. Integridad de la política de revisión

`export_frame` verifica que la huella de la política coincide con
`review_policy_hash` y aborta (`ValueError("Review policy changed")`) si no.
`test_export_reconciles_frozen_predictions_and_role` comprueba además los
umbrales:

| Regla | Comprobación |
|---|---|
| `HIGH_CONFIDENCE` ⟹ confianza ≥ 0.80 | ✅ todas |
| `LOW_CONFIDENCE` ⟹ confianza < 0.50 | ✅ todas |

No se recalibró ninguna política.

## 8. Qué falta para cerrar G6

Con el proyecto actualizado en Desktop, y **sin filtros aplicados**:

1. Leer las 4 tarjetas y las 4 tablas, y comparar contra los apartados 1–5.
2. Obtener Macro-F1 y Balanced Accuracy **sin el redondeo de presentación**
   (el formato `0.0000` muestra `0.8147`): exportar los datos del visual o usar
   el panel de rendimiento. La tolerancia `1e-12` no es verificable leyendo la
   tarjeta.
3. Seleccionar A300, luego A400, luego Pastry, y registrar los tres tríos del
   apartado 2.
4. Confirmar en la tabla de confusión la celda Bumps → Other_Faults = 21.
5. Localizar `row_id` 1277 en la vista de Datos y comprobar los 6 atributos del
   apartado 3.
6. Confirmar que al filtrar, las dos tarjetas de métrica final **no cambian**.
7. Registrar para cada punto: valor esperado, valor observado, fuente,
   diferencia y la captura que lo acredita.

| Control de G6 | Estado |
|---|---|
| 10 indicadores obligatorios | ✅ verificados en el origen |
| Comprobaciones A300 / A400 / Pastry | ✅ verificadas en el origen |
| Bumps → Other_Faults = 21 | ✅ verificada en el origen |
| `row_id` 1277 | ✅ verificado en el origen |
| Igualdad exacta en conteos | ✅ |
| Tolerancia 1e-12 en métricas | ✅ |
| Modelo sin reentrenar | ✅ |
| **Cifras observadas en Power BI Desktop** | ⛔ **NO EJECUTADO** |

**G6: PARCIAL.** Cero divergencias entre el origen de Power BI y la evidencia
congelada. El gate queda abierto hasta la lectura en Desktop.
