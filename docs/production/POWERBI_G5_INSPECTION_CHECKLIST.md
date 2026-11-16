# POWERBI_G5_INSPECTION_CHECKLIST

Orden: **OWNER-PBI-REN-001** · Preguntas a resolver inspeccionando el dashboard
Fecha: 2026-11-15 · Para: OWNER · Gate objetivo: **G5** (y los pasos de **G7**)

Los valores esperados **no** son estimaciones: se leyeron del motor de Power BI
Desktop el 2026-11-15. Ver
[`POWERBI_DESKTOP_RUNTIME_EVIDENCE.md`](POWERBI_DESKTOP_RUNTIME_EVIDENCE.md).

Clave: **🔴 BLOQUEANTE** = una respuesta negativa detiene el trabajo y hay que
investigar antes de seguir. **🟡** = registrar la desviación y continuar.

---

## Bloque 0 — Antes de tocar nada

| # | Pregunta | Esperado |
|---|---|---|
| 0.1 🔴 | ¿Hay alguna barra amarilla o roja en la parte superior? | ninguna |
| 0.2 🔴 | ¿Aparece algún diálogo de credenciales o de origen de datos? | ninguno |
| 0.3 | ¿El título de la ventana dice `steel-plates-quality-mlops-powerbi`? | sí |
| 0.4 🔴 | ¿El panel de campos lista 7 tablas? | `_Medidas`, `Dim_Acero`, `Dim_BandaTamano`, `Dim_TipoDefecto`, `Fact_Defecto`, `ML_Holdout`, `Param_Especificacion` |
| 0.5 🔴 | ¿Alguna medida o campo tiene un icono de advertencia o error? | ninguno |
| 0.6 | ¿Cuántas pestañas de página hay abajo? | **5** |
| 0.7 | ¿`Tooltip Pareto` aparece con el icono de página oculta? | sí — está configurada `HiddenInViewMode` |

## Bloque 1 — Página «Resumen ejecutivo» (activa al abrir)

10 visuales. Lienzo 1280×720.

| # | Pregunta | Esperado |
|---|---|---|
| 1.1 🔴 | ¿Renderiza completa, sin visuales en blanco ni con aspa de error? | sí |
| 1.2 🔴 | Tarjeta **Defectos** | **1.941** |
| 1.3 🔴 | Tarjeta **COPQ MXN** | **2.242.600** |
| 1.4 | Tarjeta **Cpk** | ≈ **0,0873** |
| 1.5 | Tarjeta **Defectos Grandes** | **289** |
| 1.6 | Tarjeta **Media Log Area** | ≈ **2,4924** |
| 1.7 | Tarjeta **USL px2** | **500** |
| 1.8 | Tarjeta **Texto ISO 10.2** | texto que acaba en «…Otros defectos (30% del COPQ).» |
| 1.9 🔴 | Tabla (tipo_defecto · Defectos · COPQ % del Total · % Fuera de USL · Cpk): ¿cuántas filas? | **7** |
| 1.10 | ¿La columna **Defectos** de esa tabla suma 1.941? | sí |
| 1.11 🔴 | Gráfico combinado Pareto: ¿la **línea acumulada** termina en **100 %**? | sí |
| 1.12 | ¿Las barras del Pareto están ordenadas de mayor a menor? | sí |
| 1.13 | ¿El botón de la esquina superior izquierda es legible y no tapa nada? | sí |

> **Por qué 1.11 importa:** `COPQ Acumulado %` devuelve BLANK sin contexto de
> visual (comprobado en el motor). Dentro del gráfico **debe** tener valores y
> cerrar en 100 %. Si la línea sale vacía, la medida no está recibiendo el
> contexto de categoría.

## Bloque 2 — Página «Control y capacidad»

8 visuales. Lienzo 1280×720.

| # | Pregunta | Esperado |
|---|---|---|
| 2.1 🔴 | ¿Renderiza completa, sin visuales en blanco? | sí |
| 2.2 | ¿Se lee el cuadro de texto «Control y capacidad: esta página muestra si el tamaño del defecto…»? | sí, legible |
| 2.3 | Tarjeta **% Fuera de USL** | ≈ **30,09 %** (0,3009) |
| 2.4 | Tarjeta **Cpk** | ≈ **0,0873** — igual que en la página 1 |
| 2.5 🔴 | Tarjeta **Grupos Fuera de Limites** | **7** |
| 2.6 🔴 | Tarjeta **Semaforo Cpk Texto** | **`No capaz`** |
| 2.7 🔴 | Gráfico de control (espesor): ¿se ven las **4 series**? | Media Log Area + **Linea Central** + **UCL** + **LCL** |
| 2.8 | ¿UCL está por encima de la línea central y LCL por debajo? | UCL ≈ 2,5461 · Centro ≈ 2,4924 · LCL ≈ 2,4387 |
| 2.9 | Tabla (espesor · n Grupo): ¿la columna **n Grupo** suma 1.941? | sí |
| 2.10 | Tabla (tipo_defecto · Cpk): ¿cuántas filas? | **7** |

> **Nota de interpretación:** `Cpk ≈ 0,087` y `Semaforo = No capaz` son el
> resultado correcto del proceso, no un fallo del informe. Y `COPQ` usa **costes
> supuestos**, no ahorros demostrados: no lo presentes como ahorro.

## Bloque 3 — Página «Exploracion»

13 visuales. Es además **página de drillthrough** sobre `Fact_Defecto[id_defecto]`.

| # | Pregunta | Esperado |
|---|---|---|
| 3.1 🔴 | ¿Renderiza completa, sin visuales en blanco? | sí |
| 3.2 🔴 | ¿Hay **4 segmentadores**? | `tipo_defecto`, `tipo_acero`, `espesor`, `banda_tamano` |
| 3.3 🔴 | ¿Los 4 segmentadores tienen valores (no vacíos)? | sí |
| 3.4 | Tarjetas sin filtro: **Defectos** / **COPQ MXN** / **Cpk** | **1.941** / **2.242.600** / ≈ **0,0873** |
| 3.5 | Tarjeta **Accion Recomendada** | `Contención (ISO 8.7) + causa raíz (ISO 10.2)` |
| 3.6 🔴 | Selecciona `tipo_acero = A300`: ¿**bajan** las tarjetas Defectos y COPQ MXN? | sí, deben bajar |
| 3.7 🔴 | Con ese filtro puesto, ¿cambia la tabla de detalle? | sí |
| 3.8 | ¿El gráfico de dispersión (log_area vs índice de luminosidad) pinta puntos por tipo de defecto? | sí |
| 3.9 | ¿El gráfico de columnas por banda de tamaño responde a los segmentadores? | sí |
| 3.10 | **Limpia todos los filtros.** ¿Vuelven las tarjetas a 1.941 / 2.242.600? | sí |
| 3.11 🟡 | Clic derecho en un punto de dato de otra página → *Obtener detalles* → ¿aparece `Exploracion`? | sí |

## Bloque 4 — Página «Tooltip Pareto»

3 visuales. Lienzo 320×240. Está **oculta en modo vista** (`HiddenInViewMode`) y
declarada `"type": "Tooltip"`.

| # | Pregunta | Esperado |
|---|---|---|
| 4.1 | ¿Se abre su pestaña en modo edición y renderiza? | sí |
| 4.2 | ¿Tiene tarjeta **Defectos**, tarjeta **COPQ MXN** y un gráfico de barras por banda de tamaño? | sí, 3 visuales |
| 4.3 | Tarjetas sin filtro | **1.941** y **2.242.600** |
| 4.4 🟡 | Pasa el ratón sobre un visual de otra página: ¿aparece este tooltip flotante? | sí, si el visual lo tiene asignado |

> 4.4 puede salir «no» legítimamente: una página tooltip sólo aparece en los
> visuales donde se haya configurado. Registra en **cuáles** aparece.

## Bloque 5 — Página «MODEL PERFORMANCE & REVIEW»

12 componentes. Lienzo 1280×**1040** — más alto que las demás, probablemente
tendrás que desplazarte o usar *Ajustar a la página*.

### 5.1 Conteo de componentes

| # | Pregunta | Esperado |
|---|---|---|
| 5.1.1 🔴 | ¿Hay **4 tarjetas** arriba? | sí |
| 5.1.2 🔴 | ¿Hay **3 segmentadores** en la banda central? | `steel_type`, `steel_plate_thickness`, `actual_defect` |
| 5.1.3 🔴 | ¿Hay **4 tablas** en los dos bloques inferiores? | sí |
| 5.1.4 🔴 | ¿Hay **1 nota de texto** arriba, a todo lo ancho? | sí |
| 5.1.5 🔴 | ¿Total de elementos visibles = **12**? | sí |

### 5.2 Las cuatro tarjetas, sin filtros

| # | Tarjeta | Esperado en pantalla |
|---|---|---|
| 5.2.1 🔴 | `Final Macro-F1 (389)` | **0,8147** (formato `0.0000`) |
| 5.2.2 🔴 | `Final Balanced Accuracy (389)` | **0,8048** |
| 5.2.3 🔴 | `Candidate Review Rate` | **67,10 %** |
| 5.2.4 🔴 | `ML Rows` | **389** |

### 5.3 La nota contextual

| # | Pregunta | Esperado |
|---|---|---|
| 5.3.1 🔴 | ¿Se lee completa, sin recortar? | sí, 14 px |
| 5.3.2 🔴 | ¿Empieza por «FINAL HOLDOUT: 389 known-defect observations»? | sí |
| 5.3.3 🔴 | ¿Contiene «Final scores always refer to all 389 rows»? | sí |
| 5.3.4 🔴 | ¿Contiene «Small segments are descriptive; no prospective validation»? | sí |

> Si la nota sale recortada, **no la borres ni la abrevies**: agranda el visual.
> Son las calificaciones científicas del informe.

### 5.4 Tabla de confusión (abajo izquierda, primer bloque)

Columnas: `actual_defect` · `predicted_defect` · `ML Confusion Errors`.

| # | Pregunta | Esperado |
|---|---|---|
| 5.4.1 🔴 | ¿Existe la fila **Bumps → Other_Faults**? ¿Qué valor? | **21** |
| 5.4.2 | ¿Las celdas sin errores salen **vacías** en vez de 0? | sí — `ML Confusion Errors` devuelve BLANK si no hay errores |
| 5.4.3 | ¿La suma de toda la columna es 82? | sí |

### 5.5 Tabla de error por clase (abajo derecha, primer bloque)

Columnas: `actual_defect` · `ML Rows` · `ML Errors` · `Observed Error Rate` · `Segment Support`.

| # | Pregunta | Esperado |
|---|---|---|
| 5.5.1 🔴 | ¿Cuántas filas? | **7** |
| 5.5.2 🔴 | `Bumps` | 81 registros · **26** errores |
| 5.5.3 🔴 | `Other_Faults` | 135 · **29** |
| 5.5.4 🔴 | `Pastry` | 32 · **12** |
| 5.5.5 | `K_Scatch` | 78 · **7** |
| 5.5.6 | `Z_Scratch` | 38 · **5** |
| 5.5.7 | `Stains` | 14 · **2** |
| 5.5.8 | `Dirtiness` | 11 · **1** |
| 5.5.9 🔴 | ¿`Segment Support` dice **`INSUFFICIENT_DATA`** en `Dirtiness` (11) y `Stains` (14)? | sí — son las dos clases con menos de 30 filas |
| 5.5.10 🔴 | ¿Dice **`DESCRIPTIVE`** en las otras cinco? | sí |
| 5.5.11 | ¿`ML Rows` suma 389 y `ML Errors` suma 82? | sí |

> 5.5.9 y 5.5.10 son la prueba visible de la salvaguarda de soporte pequeño. Si
> todas dicen lo mismo, la medida `Segment Support` no está respondiendo al
> contexto de fila.

### 5.6 Tabla por tramo de confianza (abajo izquierda, segundo bloque)

Columnas: `confidence_bin` · `ML Rows` · `Mean Confidence` · `Observed Accuracy` · `Segment Support`.

| # | Pregunta | Esperado |
|---|---|---|
| 5.6.1 🔴 | ¿Cuántos tramos aparecen? | hasta **6**: `[0.00,0.50)` … `[0.90,1.00]` |
| 5.6.2 | ¿`ML Rows` suma 389? | sí |
| 5.6.3 | ¿La `Observed Accuracy` **crece** al subir el tramo de confianza? | debería; si no, anótalo |
| 5.6.4 | ¿`Mean Confidence` de cada fila cae dentro de su propio tramo? | sí |

### 5.7 Tabla por estado de revisión (abajo derecha, segundo bloque)

Columnas: `review_status` · `ML Rows` · `ML Errors` · `Observed Error Rate`.

| # | Pregunta | Esperado |
|---|---|---|
| 5.7.1 🔴 | `HIGH_CONFIDENCE` | **128** registros · **1** error |
| 5.7.2 🔴 | `REVIEW_REQUIRED` | **173** |
| 5.7.3 🔴 | `LOW_CONFIDENCE` | **88** |
| 5.7.4 | ¿173 + 88 = 261 y 128 + 261 = 389? | sí |

> 5.7.1: ese **único error en `HIGH_CONFIDENCE`** es `row_id` 1277. Es el error
> que la política no captura, y debe seguir visible.

### 5.8 Comportamiento de los filtros — el control más importante

| # | Pregunta | Esperado |
|---|---|---|
| 5.8.1 🔴 | Selecciona `steel_type = A300`. ¿`ML Rows` pasa a **156**? | sí |
| 5.8.2 🔴 | Con A300 puesto, ¿`Final Macro-F1 (389)` **sigue siendo 0,8147**? | **sí — no debe cambiar** |
| 5.8.3 🔴 | ¿`Final Balanced Accuracy (389)` sigue en **0,8048**? | **sí — no debe cambiar** |
| 5.8.4 | ¿`Candidate Review Rate` **cambia**? | sí |
| 5.8.5 | ¿Las 4 tablas cambian? | sí |
| 5.8.6 🔴 | Cambia a `A400`. ¿`ML Rows` = **233**? | sí |
| 5.8.7 | Limpia acero, selecciona `actual_defect = Pastry`. ¿`ML Rows` = **32**? | sí |
| 5.8.8 | ¿El segmentador `steel_plate_thickness` filtra al usarlo? | sí |
| 5.8.9 🔴 | Limpia todo. ¿`ML Rows` vuelve a **389**? | sí |

> **5.8.2 y 5.8.3 son el requisito científico de §8 de la orden.** En el motor ya
> está demostrado que no cambian. Si en pantalla **sí** cambian, hay un visual mal
> enlazado y es un FAIL que debe investigarse, no justificarse.

### 5.9 Aislamiento entre el holdout y el análisis original

| # | Pregunta | Esperado |
|---|---|---|
| 5.9.1 🔴 | Con un segmentador ML activo, vuelve a «Resumen ejecutivo». ¿`Defectos` sigue en **1.941**? | **sí** |
| 5.9.2 🔴 | Con un segmentador de `Exploracion` activo, vuelve a la página ML. ¿`ML Rows` sigue en **389**? | **sí** |

> Esto comprueba en pantalla que `ML_Holdout` está desconectada. En el motor ya
> consta que no tiene ninguna relación. Si aquí se contaminan los números,
> Desktop creó una relación y hay que localizarla en la vista de Modelo.

## Bloque 6 — Vista de Modelo

| # | Pregunta | Esperado |
|---|---|---|
| 6.1 🔴 | ¿Hay exactamente **3 líneas** de relación? | sí, de `Fact_Defecto` a las 3 dimensiones |
| 6.2 🔴 | ¿`ML_Holdout` está **suelta, sin ninguna línea**? | **sí** |
| 6.3 | Al pulsar cada relación, ¿dice *Muchos a uno* y dirección *Única*? | sí |

> Si 6.2 sale «no», **anota la relación antes de borrarla**: su nombre, sus dos
> columnas y su cardinalidad. Es el riesgo nº 1 del expediente.

## Bloque 7 — Guardado y PBIX (G7)

| # | Paso | Qué registrar |
|---|---|---|
| 7.1 | **Guardar** el PBIP | sin error |
| 7.2 | `Archivo → Guardar como` → formato **.pbix** | ruta: `powerbi\artifacts\steel-plates-quality-mlops-powerbi.pbix` |
| 7.3 🔴 | ¿Se sobrescribe un archivo de 131 bytes? | sí, es correcto: ese archivo es un puntero LFS, **no** un informe |
| 7.4 | **Cerrar** Power BI Desktop por completo | — |
| 7.5 🔴 | **Reabrir el PBIP**: ¿carga bien, con los mismos números? | sí |
| 7.6 🔴 | **Reabrir el PBIX**: ¿carga bien? | sí |
| 7.7 🔴 | ¿El **PBIX** contiene la página `MODEL PERFORMANCE & REVIEW`? | **sí** — es el motivo de la incidencia #2 |
| 7.8 🔴 | En el PBIX, ¿`ML Rows` = 389 y `Final Macro-F1 (389)` = 0,8147? | sí |
| 7.9 | SHA256 y tamaño del PBIX | `Get-FileHash -LiteralPath "...\steel-plates-quality-mlops-powerbi.pbix" -Algorithm SHA256` |
| 7.10 | Versión exacta de Desktop usada | `Ayuda → Acerca de` |

## Bloque 8 — Después de guardar

```powershell
Set-Location "<REPO>"
git status --porcelain
git diff --stat
git lfs ls-files
python -B -m pytest -q --basetemp="$env:TEMP\pytest-post-desktop"
python -B docs/production/evidence/powerbi_static_validation.py
```

| # | Pregunta | Interpretación |
|---|---|---|
| 8.1 | ¿Qué archivos reescribió Desktop? | clasificar cada uno; los previsibles están en [`POWERBI_PBIP_PBIX_INTEGRITY.md`](POWERBI_PBIP_PBIX_INTEGRITY.md) §3.7 |
| 8.2 | ¿`git lfs ls-files` muestra el PBIX con un **oid nuevo**? | debe dejar de ser `0a87a4e33b` |
| 8.3 | ¿Aparece algún `.pbi/localSettings.json` o `cache.abf` en `git status`? | **no deben aparecer**: están en `.gitignore` |
| 8.4 | ¿Falla `test_previous_powerbi_preserved`? | **es su diseño** si Desktop reescribió archivos de la línea base. Clasificar el diff; **no** debilitar la prueba |
| 8.5 | ¿Sigue la validación estática en 77/77? | si baja, revisar qué cambió |

---

## Resumen de lo verdaderamente bloqueante

Si cualquiera de estas sale mal, para e investiga:

1. **0.1 / 0.2** — avisos o diálogos al abrir.
2. **5.2.1 / 5.2.2** — las dos métricas finales no dan 0,8147 y 0,8048.
3. **5.8.2 / 5.8.3** — las métricas finales **cambian** al filtrar.
4. **5.9.1 / 5.9.2 / 6.2** — contaminación entre el holdout y el análisis original.
5. **5.7.1** — `HIGH_CONFIDENCE` sin su único error (`row_id` 1277).
6. **5.5.9** — `Segment Support` no marca `INSUFFICIENT_DATA` en `Dirtiness` y `Stains`.
7. **7.7** — el PBIX no contiene la página ML.

Los puntos 2, 3 y 4 ya están demostrados en el motor; que fallen en pantalla
significaría un visual mal enlazado, no un problema del modelo.
