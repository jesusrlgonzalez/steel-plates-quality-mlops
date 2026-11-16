# POWERBI_PBIX_CERTIFICATION

Orden: **OWNER-PBI-REN-001** · Fase 7 — Certificación del PBIX definitivo
Fecha: 2026-11-15 · Responsable: PRODUCCIÓN
Gate: **G7** · Resultado: **✅ CERTIFICADO**

El PBIX fue guardado por OWNER desde Power BI Desktop. PRODUCCIÓN lo ha
verificado, corregido de ubicación y certificado. Sustituye la declaración
«NO GENERADO» de
[`POWERBI_PBIP_PBIX_INTEGRITY.md`](POWERBI_PBIP_PBIX_INTEGRITY.md).

---

## 1. Identidad del artefacto

| Dato | Valor |
|---|---|
| Ruta | `powerbi\artifacts\steel-plates-quality-mlops-powerbi.pbix` |
| Tamaño | **252 387 bytes** |
| **SHA256** | **`91f89ff2d8ce7605e9b54d9c2c45a6d5cf2511649498e9c70ed82abfe7d86260`** |
| Guardado | 2026-11-15 08:10:44 |
| Power BI Desktop | **`2.156.951.0 (26.07)`** |
| Firma de archivo | `50 4B 03 04` (paquete ZIP/OPC) — **no** un puntero LFS |

```powershell
Get-FileHash -LiteralPath "<REPO>\powerbi\artifacts\steel-plates-quality-mlops-powerbi.pbix" -Algorithm SHA256
```

### 1.1 Desviación corregida: se guardó en la carpeta equivocada

El cuadro de diálogo «Guardar como» dejó el archivo en **`artifacts\`** (la
carpeta de artefactos de ML, junto a `manifest.json` y el modelo entrenado) en
lugar de **`powerbi\artifacts\`**, que es la ruta que fija §3 de la orden.

PRODUCCIÓN lo movió a su ubicación canónica. El traslado se hizo **con Power BI
Desktop cerrado**: el primer intento falló con *«The process cannot access the
file because it is being used by another process»*, porque tras «Guardar como»
Desktop pasa a tener abierto el PBIX y mantiene un bloqueo sobre él.

| Antes | Después |
|---|---|
| `artifacts\…pbix` (252 387 B, real) | *(eliminado de ahí)* |
| `powerbi\artifacts\…pbix` (131 B, puntero LFS muerto) | `powerbi\artifacts\…pbix` (252 387 B, real) |

El puntero de 131 bytes que se sobrescribió (`a89d3c1c…`) sigue recuperable del
histórico Git. No era un informe.

## 2. Contenido del paquete

Inspección de solo lectura del paquete OPC. **64 entradas.** No se modificó
ningún byte: leer un ZIP no es reconstruirlo.

| Entrada | Bytes | Qué es |
|---|---:|---|
| `DataModel` | 207 684 | modelo semántico compilado con los datos |
| `Report/definition/pages/**` | — | **52 entradas**, informe en formato PBIR |
| `Report/StaticResources/…/CY26SU07.json` | 19 872 | tema base |
| `DiagramLayout` | 3 090 | vista de modelo |
| `DAXQueries/Consulta%201.dax` | 318 | la consulta de verificación del Pareto |
| `SecurityBindings`, `Settings`, `Metadata`, `Version`, `[Content_Types].xml` | — | estructura OPC |

### 2.1 Las cinco páginas están en el PBIX

| Página | Lienzo | Visuales en el PBIX |
|---|---|---:|
| `Resumen ejecutivo ` | 1280×720 | **10** |
| `Control y capacidad` | 1280×720 | **8** |
| `Exploracion` | 1280×720 | **13** |
| `Tooltip Pareto` | 320×240 | **3** |
| **`MODEL PERFORMANCE & REVIEW`** | 1280×**1040** | **12** |

`MODEL PERFORMANCE & REVIEW` **está presente con sus 12 componentes**. Esta es
la condición de fondo de la incidencia **#2**: el PBIX publicado anteriormente no
contenía la página ML.

### 2.2 Equivalencia funcional PBIX ↔ PBIP

| Comprobación | Resultado |
|---|---|
| `pageOrder` idéntico | ✅ |
| Conjunto de identificadores de visual en las 5 páginas | ✅ **idéntico** en las cinco |
| `activePageName` | idéntico en ambos (`ml_performance_review`) |

Script: [`evidence/compare_pbix_pbip.py`](evidence/compare_pbix_pbip.py).

## 3. Cerrado y reabierto

Power BI Desktop se cerró de forma **ordenada** (`CloseMainWindow`, nunca
`Kill`). Salió en **3 segundos sin ningún diálogo de cambios sin guardar**, lo
que confirma que todo estaba persistido. Su motor (`msmdsrv` PID 9204) terminó
con él.

Después se reabrieron **los dos formatos, cada uno en su propia instancia**, y se
consultó su motor en solo lectura:

| Formato | Desktop PID | Motor PID | Puerto | Base de datos |
|---|---|---|---|---|
| PBIP | 32968 | 44144 | 56409 | `c0f580be-3918-484e-982f-2910913fdc04` |
| PBIX | 49016 | 50188 | 62404 | `56c2960f-1c5a-46cd-b4f3-ea8c57428e56` |

### 3.1 Resultados — idénticos en PBIP y en PBIX

| Control | PBIP reabierto | PBIX reabierto |
|---|---|---|
| `Fact_Defecto` | **1 941** | **1 941** |
| `ML_Holdout` | **389** | **389** |
| Relaciones | 3, `Fact_Defecto` → 3 dimensiones | ídem |
| Cardinalidad / filtrado | muchos a uno · unidireccional | ídem |
| `ML_Holdout` (TableID 28) en relaciones | **ausente** | **ausente** |
| `Final Macro-F1 (389)` | `0.81467281017643689` | ídem |
| `Final Balanced Accuracy (389)` | `0.80487267999799328` | ídem |
| Diferencia contra los literales congelados | **0** y **0** | **0** y **0** |
| Cierre del Pareto | **1** (distancia a 1 = **0**) | **1** |

Ninguna divergencia entre los dos formatos.

### 3.2 El 100 % final del Pareto, confirmado

`COPQ Acumulado %` devuelve BLANK sin contexto de categoría, de modo que hay que
evaluarlo dentro de una agrupación, que es lo que hace el gráfico:

| tipo_defecto | Defectos | COPQ | Acumulado |
|---|---:|---:|---|
| Otros defectos | 673 | 673 000 | 0.30009810041915636 |
| Rayón en K (K_Scatch) | 391 | 586 500 | 0.56162489967002582 |
| Abolladuras (Bumps) | 402 | 482 400 | 0.77673236422010172 |
| Pastelado (Pastry) | 158 | 284 400 | 0.90354945152947475 |
| Rayón en Z | 190 | 171 000 | 0.979800231873718 |
| Manchas | 72 | 28 800 | 0.99264246856327476 |
| **Suciedad** | 55 | 16 500 | **1** |

Máximo del acumulado = **1**, distancia a 1 = **0**. Las categorías quedan
ordenadas de mayor a menor COPQ, como exige un Pareto. Coincide con la consulta
DAX que OWNER dejó guardada en el proyecto (`DAXQueries/Consulta 1.dax`), que
evaluaba precisamente la última categoría.

Script: [`evidence/query_pareto_and_counts.ps1`](evidence/query_pareto_and_counts.ps1).

## 4. Git LFS

| Comprobación | Resultado |
|---|---|
| Atributos aplicados | `filter: lfs` · `diff: lfs` · `merge: lfs` · `text: unset` ✅ |
| `git lfs ls-files -l` | `91f89ff2d8ce…` ✅ coincide con el SHA256 del archivo |
| Objeto en el índice | puntero de 3 líneas con `size 252387` ✅ |
| Archivo en el árbol de trabajo | 252 387 bytes, el PBIX real ✅ |
| Transición registrada | `LFS: 0a87a4e -> LFS: 91f89ff` |

### 4.1 Esto repara el objeto LFS roto

El puntero anterior referenciaba el oid `0a87a4e3…`, **que no existe en el
almacenamiento del servidor** (error 404 reproducible; ver
[`POWERBI_RENAME_BASELINE.md`](POWERBI_RENAME_BASELINE.md) §4). Cualquier clon con
LFS activo fallaba al hacer checkout.

El puntero nuevo referencia `91f89ff2…`, **que sí existe en el almacén LFS
local**. Al hacer push con `git lfs push`, el objeto subirá y el repositorio
dejará de estar roto. **Es la primera vez que el repositorio tendrá un PBIX
materializable.**

## 5. Clasificación del diff originado por Desktop

El guardado reescribió **74 archivos** del PBIP. Era lo previsto
([`POWERBI_PBIP_PBIX_INTEGRITY.md`](POWERBI_PBIP_PBIX_INTEGRITY.md) §3.7), y la
orden exige **clasificarlo, no aceptarlo**.

| Clase | Nº |
|---|---:|
| Solo finales de línea (LF → CRLF), invisibles para las comprobaciones de hash | **42** |
| Con cambio real de contenido | **32** |

De los 69 archivos cubiertos por el manifiesto congelado `pre_ml_powerbi_hashes.json`:

| Clase | Nº |
|---|---:|
| Idénticos a la línea base (módulo CRLF) | **48** |
| Reescritos por Desktop, **certificados sin cambio semántico** | **15** |
| **Con cambio semántico** | **0** |

**Sin cambios semánticos: cero.** Lo garantiza
[`evidence/build_desktop_save_hashes.py`](evidence/build_desktop_save_hashes.py),
que se **niega** a certificar un objeto cuyo tipo de visual, campos vinculados o
geometría de página difieran de la línea base. Si lo hubiera, el script falla y
lo eleva a OWNER.

Manifiesto resultante:
[`evidence/powerbi_desktop_save_hashes.json`](evidence/powerbi_desktop_save_hashes.json).

### 5.1 Qué cambió exactamente en los 15

| Motivo | Objetos |
|---|---|
| Formato por defecto materializado (clave `objects`) | 6 visuales |
| Geometría del visual reajustada | 4 visuales |
| `displayOption` `FitToPage`/`ActualSize` → `FitToWidth` | 2 páginas |
| Reserialización sin cambio estructural | `5c4ce3f8…`, `.pbi/editorSettings.json`, `diagramLayout.json` |
| Marcador del panel de filtros, sin condiciones | 1 visual |

**En los 15, el tipo de visual y los campos vinculados son idénticos.** Ningún
visual cambió qué mide o qué columna muestra.

El único filtro nuevo (tarjeta `% Fuera de USL` en «Control y capacidad») es una
declaración `Advanced` **sin condiciones, sin operador y sin valores** — un
marcador del panel de filtros. Es estructuralmente idéntico a los que ya existían
en la línea base sobre las tarjetas `COPQ MXN` y `Texto ISO 10.2`. No filtra
nada, y el valor medido en el motor (`0.30087583719732097`) lo confirma.

### 5.2 TMDL

| Archivo | Cambio | Veredicto |
|---|---|---|
| `relationships.tmdl` | **solo finales de línea** | 3 relaciones intactas, `ML_Holdout` ausente ✅ |
| `_Medidas.tmdl` | **solo finales de línea** | las 22 medidas originales intactas ✅ |
| `Fact_Defecto.tmdl`, las 3 `Dim_*`, `Param_Especificacion.tmdl` | **solo finales de línea** | intactas ✅ |
| `database.tmdl`, `cultures/es-ES.tmdl` | **solo finales de línea** | intactas ✅ |
| `model.tmdl` | `PBI_QueryOrder` completada con `ML_Holdout` y `RutaMLCSV`; `PBI_ProTooling` añade `DaxQueryView_Desktop`; `ref table ML_Holdout` movido al bloque principal | previsto en [`POWERBI_MODEL_DAX_VALIDATION.md`](POWERBI_MODEL_DAX_VALIDATION.md) §1.1 ✅ |
| `expressions.tmdl` | una línea en blanco colapsada; `lineageTag` asignado a `RutaMLCSV` | `RutaCSV` y `Raw_SteelPlates` intactos ✅ |
| `ML_Holdout.tmdl` | `lineageTag` y anotaciones por columna | 16 columnas, 12 medidas y los dos literales congelados intactos ✅ |

`RutaCSV` conserva el valor corregido, con **una sola** barra invertida por
separador:

```
expression RutaCSV = "C:\path\to\steel-plates-quality-mlops\data\raw\steel_plates_faults.csv"
```

### 5.3 `activePageName` — decisión de OWNER

Al guardar quedaba seleccionada la página ML, de modo que `activePageName` pasó
de `5ee9939d0101076d3381` (Resumen ejecutivo) a `ml_performance_review`, **en el
PBIP y en el PBIX**. El informe abre mostrando MODEL PERFORMANCE & REVIEW.

**OWNER lo aceptó el 2026-11-15** como página de entrada. Registrado con
correspondencia trazable en la prueba y en el validador: ambos aceptan los **dos**
valores, nombrados explícitamente, y `pageOrder` sigue exigiéndose exacto.

Si en el futuro se prefiere volver al resumen ejecutivo: abrir el PBIP,
seleccionar esa pestaña, guardar y repetir «Guardar como» PBIX. **Eso cambia el
SHA256 del PBIX** y obliga a recertificar.

## 6. Pruebas tras el guardado

| Suite | Resultado |
|---|---|
| `tools.project_checks` (5) | **5 PASS** |
| `powerbi_static_validation.py` | **78/78 PASS** |
| `tests/test_bi_integration.py` | **5 PASS** |
| `pytest -q` completo | ver [`POWERBI_PRODUCTION_TEST_REPORT.md`](POWERBI_PRODUCTION_TEST_REPORT.md) §8 |

`validate-artifact` y `validate-evidence` devuelven **los mismos hashes y las
mismas cuatro cifras** (389/307/82/261) que en la línea base: el guardado de
Desktop no alteró ningún artefacto ni evidencia científica.

### 6.1 Correspondencias trazables añadidas, y por qué no debilitan nada

Cuatro ajustes en `tests/test_bi_integration.py`, cada uno con su invariante
documentada en el propio código:

| Ajuste | Por qué | Qué sigue exigiéndose |
|---|---|---|
| El PBIX acepta la línea base **o** `91f89ff2…` | regenerar el PBIX **es** el objetivo de la orden | los dos valores están fijados; un tercero falla |
| Objetos reescritos por Desktop: hash del manifiesto certificado | el guardado autorizado los reserializó | el hash nuevo **y** la igualdad del núcleo semántico con la línea base |
| `model.tmdl`: aserción estructural en vez de hash del prefijo | Desktop movió `ref table ML_Holdout`, el prefijo ya no existe | las 7 tablas en orden, la cultura, el bloque de cabecera y los 7 primeros elementos de `PBI_QueryOrder` |
| `expressions.tmdl`: tolerancia en el recuento de saltos finales | Desktop colapsó una línea en blanco | todos los demás bytes de la definición pre-ML, exactos |

Un quinto ajuste, en `test_text_generation_idempotent`: comparaba el estado
comprometido contra el resultado de `prepare()`, lo que equivalía a exigir que
`prepare()` fuera un **no-op**. Tras el guardado autorizado Desktop enriqueció la
página (estado de segmentador, formato), así que `prepare()` ya **no** es un
no-op sobre ella — precisamente la sobrescritura de la que advierte
`docs/evidence/powerbi_runtime_handoff.md`. La prueba compara ahora la primera
ejecución contra la segunda, que es la **idempotencia** que su nombre declara. El
contenido de la página sigue cubierto por
`test_draft_structure_and_field_bindings` y por el validador estático.

`pre_ml_powerbi_hashes.json` **no se modificó**. Ningún hash histórico se
recalculó.

## 7. Gate G7

| Condición | Resultado |
|---|---|
| El PBIX existe en `powerbi\artifacts` | ✅ (tras corregir la ubicación) |
| Generado por Power BI Desktop real | ✅ `2.156.951.0 (26.07)` |
| Sin edición binaria, renombrado de extensión ni reconstrucción ZIP | ✅ |
| Desktop cerrado | ✅ cierre ordenado, sin diálogos pendientes |
| PBIP reabierto correctamente | ✅ |
| PBIX reabierto correctamente | ✅ |
| El PBIX contiene la página ML | ✅ 12 componentes |
| Datos: 1 941 y 389 | ✅ en ambos formatos |
| Medidas y filtros | ✅ métricas congeladas con diferencia 0 |
| Pareto al 100 % | ✅ exactamente 1 |
| SHA256, tamaño y versión de Desktop registrados | ✅ |
| Git LFS verificado | ✅ y el objeto roto queda reparado |

**G7: CERTIFICADO.**

## 8. Límite que se mantiene

Esta certificación cubre el modelo, el paquete y la persistencia. **No** sustituye
la inspección visual de **G5**: los visuales viven en la capa de informe y no son
consultables por XMLA, de modo que la renderización, la legibilidad y el clic real
en los segmentadores los ha comprobado OWNER en pantalla, no PRODUCCIÓN.
Cuestionario: [`POWERBI_G5_INSPECTION_CHECKLIST.md`](POWERBI_G5_INSPECTION_CHECKLIST.md).

Estado tras esta fase: **`PBIX_GENERATED_AND_REOPENED`**. Es un estado técnico y
**no** sustituye la aceptación OWNER. No se ha publicado nada en Power BI Service.
