# POWERBI_MODEL_DAX_VALIDATION

Orden: **OWNER-PBI-REN-001** · Fase 4 — Validación del modelo semántico
Fecha: 2026-11-14 · Responsable: PRODUCCIÓN
Gate: **G4** · Resultado: **✅ PASS** (actualizado 2026-11-15)

> **ACTUALIZACIÓN 2026-11-15 — G4 SUPERADO.** Se consultó el motor en vivo de
> Power BI Desktop. Resultados: 7 tablas; **3 relaciones** con cardinalidad
> *muchos a uno* y filtrado *unidireccional* **leídos del motor**, no inferidos;
> **`ML_Holdout` sin ninguna relación** (Desktop no la autodetectó); y **34 de 34
> medidas compilan**, evaluadas una por una. Evidencia:
> [`POWERBI_DESKTOP_RUNTIME_EVIDENCE.md`](POWERBI_DESKTOP_RUNTIME_EVIDENCE.md) §4.
>
> Dos puntos de este documento quedan superados por esa evidencia:
> el §2.1 deducía las cardinalidades «por defecto, al no haber anulaciones» —
> ahora están **confirmadas** (`FromCardinality=2`, `ToCardinality=1`,
> `CrossFilteringBehavior=1`); y el §3 advertía del riesgo de autodetección
> hacia `ML_Holdout` — **no ocurrió** en esta carga.
>
> El resto conserva su redacción original como verificación estática previa.

Evidencia ejecutable: [`evidence/powerbi_static_validation.py`](evidence/powerbi_static_validation.py)
(**77/77 PASS**, exit 0).

---

## 1. Tablas

`model.tmdl` referencia 7 tablas y las 7 tienen su archivo TMDL presente:

| Tabla | Rol | Archivo TMDL |
|---|---|---|
| `Dim_TipoDefecto` | dimensión | ✅ |
| `Dim_Acero` | dimensión | ✅ |
| `Dim_BandaTamano` | dimensión | ✅ |
| `Fact_Defecto` | hecho | ✅ |
| `Param_Especificacion` | parámetro | ✅ |
| `_Medidas` | tabla de medidas | ✅ |
| `ML_Holdout` | evaluación ML (**desconectada**) | ✅ |

`model.tmdl` mantiene su SHA256 de línea base
`7a15a4c33068eaf68c5afffa57f3a917daf3bc2c7197799826729c5bb24c5881`: el añadido
`ref table ML_Holdout` sigue siendo un apéndice, y las definiciones previas
permanecen como prefijo byte a byte (verificado por
`test_previous_powerbi_preserved`).

### 1.1 Observación menor

La anotación `PBI_QueryOrder` enumera
`["RutaCSV","Raw_SteelPlates","Dim_TipoDefecto","Dim_Acero","Dim_BandaTamano","Fact_Defecto","Param_Especificacion"]`
y **no** incluye `RutaMLCSV` ni `ML_Holdout`. Es una anotación de ordenación en
la interfaz de Power Query, sin efecto funcional; Desktop la completará al
guardar. Se registra para que el diff originado por Desktop en la Fase 7 no se
interprete como un cambio inesperado.

## 2. Las tres relaciones del esquema estrella

`relationships.tmdl` (SHA256 `df316433fc6cd184d6ddd22011918ac69546275661a62e3883c8bf3e72af66f2`,
idéntico a la línea base):

| Relación | Desde | Hacia |
|---|---|---|
| `AutoDetected_2c7f5146-…` | `Fact_Defecto.id_tipo_defecto` | `Dim_TipoDefecto.id_tipo_defecto` |
| `AutoDetected_d3e16334-…` | `Fact_Defecto.id_acero` | `Dim_Acero.id_acero` |
| `AutoDetected_ad8b0b3a-…` | `Fact_Defecto.id_banda_tamano` | `Dim_BandaTamano.id_banda_tamano` |

| Comprobación | Resultado |
|---|---|
| Relaciones totales | 3 ✅ |
| Todas parten del hecho hacia una dimensión | ✅ |
| Columnas clave con el mismo nombre en ambos lados | ✅ |

### 2.1 Cardinalidades y dirección de filtrado

`relationships.tmdl` **no declara** ninguna propiedad
`fromCardinality`, `toCardinality` ni `crossFilteringBehavior`. En TMDL eso
significa que las tres relaciones usan los valores por defecto:

- cardinalidad **muchos a uno** (`many` en `Fact_Defecto` → `one` en la dimensión);
- filtrado **unidireccional**, de la dimensión hacia el hecho.

Es el patrón correcto de un esquema estrella. No hay filtrado bidireccional ni
relaciones inactivas. Verificado por ausencia de anulaciones explícitas: la lista
de coincidencias de esas tres propiedades está **vacía**.

Confirmación en Desktop (vista de Modelo) sigue siendo necesaria para G4.

## 3. `ML_Holdout` desconectada — regla científica inalterable

| Comprobación | Resultado |
|---|---|
| Apariciones de `ML_Holdout` en `relationships.tmdl` | **0** ✅ |
| Los 389 registros se mezclan con los 1 941 | **No** ✅ |

`ML_Holdout` es la única tabla sin relación. Al no existir ruta de filtrado
entre `ML_Holdout` y el esquema estrella, los segmentadores de las páginas
originales no pueden alterar las cifras ML, ni los segmentadores ML pueden
alterar el análisis original. Los dos conjuntos permanecen separados.

**Riesgo para la Fase 7:** Power BI Desktop puede **autodetectar** una relación
al actualizar (las tres existentes se llaman `AutoDetected_…`, lo que demuestra
que la autodetección está activa en este modelo). En la validación de Desktop
hay que inspeccionar la vista de Modelo y, si apareciera cualquier relación que
implique `ML_Holdout`, **registrarla antes de eliminarla**. Esta es la
comprobación de mayor riesgo científico de toda la Fase 7.

## 4. Medidas DAX

**34 medidas** en total, ninguna renombrada ni eliminada.

### 4.1 Las 22 medidas originales — `_Medidas.tmdl`

SHA256 idéntico a la línea base
(`87a9562427164abebdb8fa911f841444c7df1bac8567e2fc11d43e77c0405f59`).

`Defectos`, `COPQ MXN`, `COPQ % del Total`, `COPQ por Placa MXN`,
`Defectos % del Total`, `COPQ Acumulado %`, `Media Log Area`, `Linea Central`,
`Sigma Global`, `n Grupo`, `UCL`, `LCL`, `Fuera de Limites`,
`Grupos Fuera de Limites`, `USL px2`, `Cpk`, `Semaforo Cpk Color`,
`Semaforo Cpk Texto`, `% Fuera de USL`, `Accion Recomendada`,
`Defectos Grandes`, `Texto ISO 10.2`.

Ninguna fue modificada por este trabajo.

### 4.2 Las 12 medidas ML — `ML_Holdout.tmdl`

SHA256 idéntico a la línea base
(`da20e260a2792dfb71077081c9d6f0f88cb3e8f099b3041758f76039925c237d`).

| Medida | Expresión | Formato | Responde a filtros |
|---|---|---|---|
| `Final Macro-F1 (389)` | `0.8146728101764369` | `0.0000` | **No** — constante |
| `Final Balanced Accuracy (389)` | `0.8048726799979933` | `0.0000` | **No** — constante |
| `ML Rows` | `COUNTROWS ( ML_Holdout )` | `0` | Sí |
| `ML Correct` | `SUM ( ML_Holdout[correct_prediction] )` | `0` | Sí |
| `ML Errors` | `[ML Rows] - [ML Correct]` | `0` | Sí |
| `ML Confusion Errors` | `IF ( [ML Errors] > 0, [ML Errors], BLANK () )` | `0` | Sí |
| `ML Review Rows` | `SUM ( ML_Holdout[review_required] )` | `0` | Sí |
| `Candidate Review Rate` | `DIVIDE ( [ML Review Rows], [ML Rows] )` | `0.00%` | Sí |
| `Observed Accuracy` | `DIVIDE ( [ML Correct], [ML Rows] )` | `0.00%` | Sí |
| `Observed Error Rate` | `DIVIDE ( [ML Errors], [ML Rows] )` | `0.00%` | Sí |
| `Mean Confidence` | `AVERAGE ( ML_Holdout[confidence] )` | `0.00%` | Sí |
| `Segment Support` | `IF ( [ML Rows] < 30, "INSUFFICIENT_DATA", "DESCRIPTIVE" )` | — | Sí |

### 4.3 Cumplimiento de la regla de métricas globales

La orden exige que las tarjetas de Macro-F1 y Balanced Accuracy conserven las
métricas **globales** del holdout, y que las medidas por segmentos respondan a
sus filtros. El diseño lo cumple **estructuralmente**:

- Las dos métricas son **literales DAX**, no agregaciones. Ninguna referencia a
  columna ni función de agregación aparece en su expresión, luego **ningún
  contexto de filtro puede alterarlas**. Son inmunes por construcción, no por
  configuración.
- Las diez medidas restantes agregan sobre `ML_Holdout` y **sí** responden al
  contexto de filtro, que es lo exigido para el análisis por segmentos.
- `Segment Support` marca como `INSUFFICIENT_DATA` todo segmento con menos de
  30 filas, evitando que se lean como conclusiones cifras de soporte pequeño.

Los valores literales coinciden exactamente con la evidencia congelada
(`reports/ml/final_holdout/metrics.json`), con tolerancia `1e-12`. Ver
[`POWERBI_RECONCILIATION_RESULTS.md`](POWERBI_RECONCILIATION_RESULTS.md).

### 4.4 Riesgo de presentación, no de cálculo

El formato `0.0000` redondea `0.8146728101764369` a `0.8147` en la tarjeta. El
valor almacenado conserva los 16 dígitos. La reconciliación con tolerancia
`1e-12` debe hacerse contra el valor **sin redondeo de presentación** (p. ej.
exportando los datos del visual), no leyendo la tarjeta.

## 5. Particiones y expresiones Power Query

| Comprobación | Resultado |
|---|---|
| Partición `ML_Holdout` en `mode: import` | ✅ |
| Usa `File.Contents(RutaMLCSV)` | ✅ |
| Guarda `Table.RowCount(Tipos) = 389` | ✅ |
| Guarda `List.Distinct(Tipos[dataset_role]) = {"FINAL_HOLDOUT_EVALUATION"}` | ✅ |
| Validación de esquema contra las 16 columnas | ✅ |
| 16 columnas declaradas con su tipo y `sourceColumn` | ✅ |

Expresiones de `expressions.tmdl`: `Raw_SteelPlates`, `RutaCSV`, `RutaMLCSV`.
Resolución verificada en
[`POWERBI_POWERQUERY_VALIDATION.md`](POWERBI_POWERQUERY_VALIDATION.md).

Las particiones de las tablas originales (`Fact_Defecto`, las tres dimensiones,
`Param_Especificacion`) conservan sus hashes de línea base y no fueron tocadas.

## 6. Defectos de modelado detectados

Uno, y no está en el modelo semántico sino en el parámetro que lo alimenta:

| # | Defecto | Causa | Cambio mínimo | Prueba de regresión |
|---|---|---|---|---|
| 1 | `ML_Holdout` no podía cargar | `RutaCSV` con separador doblado rompía `Text.Contains(Normalized, "/data/raw/")` en `RutaMLCSV` | separadores simples en el valor de `RutaCSV`; **ninguna** otra línea | `powerbi_static_validation.py` F3 (5 comprobaciones de resolución) + `test_previous_powerbi_preserved` |

Registro completo en
[`POWERBI_POWERQUERY_VALIDATION.md`](POWERBI_POWERQUERY_VALIDATION.md) §3.

**Ningún error de DAX fue detectado** en el análisis estático. No se modificó
ninguna expresión DAX, de ninguna de las 34 medidas.

## 7. Qué falta para cerrar G4

En Power BI Desktop, vista de Modelo y de Datos:

1. Confirmar las 7 tablas y sus recuentos de fila (1 941 en el hecho, 389 en ML).
2. Confirmar las 3 relaciones, su cardinalidad **muchos a uno** y su dirección
   **unidireccional** en el panel de propiedades.
3. **Confirmar que `ML_Holdout` sigue sin ninguna relación.** Registrar antes de
   eliminar cualquier relación autodetectada.
4. Confirmar que las 34 medidas **compilan** sin error (ninguna marca de error en
   el panel de campos).
5. Comprobar los tipos de datos de las 16 columnas de `ML_Holdout`.
6. Comprobar el contexto de filtro: con un segmentador activo, las dos tarjetas
   de métrica final **no cambian**, y `ML Rows` / `ML Errors` **sí** cambian.

| Control de G4 | Estado |
|---|---|
| Tablas originales presentes | ✅ verificado |
| Las tres relaciones del esquema estrella | ✅ verificado |
| Cardinalidades | ✅ verificado (por defecto, sin anulaciones) |
| Direcciones de filtrado | ✅ verificado (por defecto, sin anulaciones) |
| Tipos de datos declarados | ✅ verificado |
| Las 34 medidas DAX presentes e inalteradas | ✅ verificado |
| Particiones y expresiones Power Query | ✅ verificado |
| `ML_Holdout` desconectada | ✅ verificado |
| **DAX compila en el motor** | ⛔ **NO EJECUTADO** |
| **Contexto de filtro evaluado en el motor** | ⛔ **NO EJECUTADO** |
| **Relaciones confirmadas en la vista de Modelo** | ⛔ **NO EJECUTADO** |

**G4: PARCIAL.**
