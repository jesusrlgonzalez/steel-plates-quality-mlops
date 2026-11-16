# POWERBI_PBIP_PBIX_INTEGRITY

Orden: **OWNER-PBI-REN-001** · Fase 7 — Generación del PBIX definitivo
Fecha: 2026-11-14 · Responsable: PRODUCCIÓN
Gates: **G2 ✅ · G3 ✅ · G5 ✅ · G7 ✅** — **todos superados** (actualizado 2026-11-15)

> **ACTUALIZACIÓN FINAL 2026-11-15 — EL PBIX EXISTE Y ESTÁ CERTIFICADO.**
> OWNER ejecutó la validación en Desktop y guardó el PBIX. PRODUCCIÓN lo verificó,
> corrigió su ubicación (se había guardado en `artifacts\` en vez de
> `powerbi\artifacts\`) y lo certificó:
> **252 387 bytes · SHA256 `91f89ff2d8ce7605e9b54d9c2c45a6d5cf2511649498e9c70ed82abfe7d86260`**.
>
> Todo lo que este documento declara más abajo como `NO EJECUTADO` o
> `NO_GENERADO` **ha quedado superado**. Documento vigente:
> [`POWERBI_PBIX_CERTIFICATION.md`](POWERBI_PBIX_CERTIFICATION.md).
>
> Se conserva como el procedimiento que se siguió y como registro del estado
> previo a la ejecución.

> **ACTUALIZACIÓN 2026-11-15.** Desktop **sí** abrió el PBIP renombrado y se
> validó su motor en vivo: **G2, G3, G4 y G6 pasaron**. Ver
> [`POWERBI_DESKTOP_RUNTIME_EVIDENCE.md`](POWERBI_DESKTOP_RUNTIME_EVIDENCE.md).
>
> Quedan **dos** cosas, ambas en la GUI y ambas tuyas:
> **G5** — mirar las cinco páginas (los visuales no son consultables por XMLA), y
> **G7** — `Archivo → Guardar como` para generar el PBIX.
>
> Del procedimiento del §3, los pasos **1–2 y 5–7 ya están cubiertos** por la
> evidencia del motor. Lo que falta de verdad: los pasos **13–17** (páginas) y
> **29–35** (guardado y reapertura). Los pasos 18–28 de reconciliación están
> verificados en el motor; repetirlos en pantalla los confirma visualmente.
>
> El apartado 1 que sigue conserva su redacción original: era exacto cuando se
> escribió, y sigue siendo exacto en lo que importa — **el PBIX no existe**.

---

## 1. Declaración

**PRODUCCIÓN no ha generado el PBIX y no declara la validación de Desktop.**

La generación del PBIX exige accionar la interfaz gráfica de Power BI Desktop
(**Archivo → Guardar como**). Las herramientas de PRODUCCIÓN no accionan
aplicaciones de escritorio: no hay forma de pulsar ese menú, leer el lienzo ni
capturar una pantalla auténtica. Power BI Desktop **está instalado** en el equipo
(`C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe`, versión
`2.156.951.0 (26.07)`), pero su presencia no sustituye a una ejecución.

Conforme a §20 de la orden, PRODUCCIÓN entrega el PBIP preparado, las
correcciones textuales verificadas y el procedimiento exacto de intervención
externa, **sin declarar generado el PBIX**.

| Estado | Valor |
|---|---|
| `PBIX_SHA256` | `NO_GENERADO` |
| `PBIX_BYTES` | `NO_GENERADO` |
| `DESKTOP_VERSION_USADA` | `NO_EJECUTADO` |
| Estado oficial | `READY_FOR_DESKTOP_VALIDATION` |

No se ha intentado —ni se intentará— edición binaria, renombrado de extensión,
reconstrucción ZIP ni ninguna herramienta que simule un guardado de Desktop.

## 2. Advertencia crítica: no existe ningún PBIX binario

| Ubicación | Contenido | Tamaño |
|---|---|---:|
| `powerbi/artifacts/steel-plates-quality-mlops-powerbi.pbix` (este repositorio) | puntero Git LFS | 131 B |
| Objeto LFS `0a87a4e3…` en el servidor | **404 — no existe** | — |
| `Steel_Plates_PowerBI_Lista_Para_Desktop_Local\powerbi\artifacts\…pbix` | puntero Git LFS | 131 B |
| `STEEL_PLATES_QUALITY_MLOPS_PARA_WINDOWS\…\…pbix` | puntero Git LFS | 131 B |

El objeto LFS del PBIX anterior **no existe en el almacenamiento del servidor**
(error 404 reproducible con `git lfs pull`; evidencia en
[`POWERBI_RENAME_BASELINE.md`](POWERBI_RENAME_BASELINE.md) §4). El PBIX histórico
es **irrecuperable** y no hay ninguna copia binaria en el disco local.

Consecuencias:

1. La comparación «PBIX anterior ↔ PBIX nuevo» de la Fase 0 es inejecutable.
2. El PBIX que produzca este procedimiento será el **único** PBIX real del
   proyecto. No habrá versión previa contra la que contrastarlo.
3. **No intentar abrir ningún `.pbix` de 131 bytes.** No es un informe.

El paso 8 del handoff histórico (`git lfs install`, `git lfs pull` antes de
comparar) **no es aplicable**: ya se ejecutó y el objeto no está en el servidor.

## 3. Procedimiento exacto de intervención externa

### 3.0 Antes de empezar

| # | Acción |
|---|---|
| 1 | Cerrar **todas** las instancias de Power BI Desktop. |
| 2 | **No** usar la carpeta `Steel_Plates_PowerBI_Lista_Para_Desktop_Local`: es otra distribución, sin este renombrado ni la corrección de `RutaCSV`. Si Desktop la tiene abierta (se observó el PID 34952), cerrarla. |
| 3 | Confirmar la rama: `git -C "C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\steel-plates-quality-mlops" rev-parse --abbrev-ref HEAD` → `fix/powerbi-canonical-naming-pbix`. |
| 4 | Confirmar el árbol limpio: `git status --porcelain` sin salida. |

### 3.1 Abrir y actualizar

| # | Acción | Qué registrar |
|---|---|---|
| 1 | Abrir `C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\steel-plates-quality-mlops\powerbi\project\steel-plates-quality-mlops-powerbi.pbip` | versión exacta de Desktop; **todo** mensaje de error o aviso al abrir |
| 2 | Comprobar que el proyecto carga: 5 páginas en el panel inferior, 7 tablas en el panel de campos | captura del panel de campos |
| 3 | **Transformar datos** → expresión `RutaCSV` → **Editor avanzado** | el valor mostrado debe ser exactamente `"C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\steel-plates-quality-mlops\data\raw\steel_plates_faults.csv"` con **una** barra invertida por separador |
| 4 | Expresión `RutaMLCSV` → comprobar su **valor resuelto** (no sólo el texto) | debe resolver a `…/powerbi/data/ml_holdout_evaluation.csv`, sin el error `"Set RutaCSV to this repository…"` |
| 5 | Actualizar vista previa de ambas consultas | cero errores de Power Query; cero avisos de credenciales |
| 6 | **Cerrar y aplicar** → **Actualizar** | tiempo, errores, avisos |
| 7 | Recuento de filas | hecho original **1 941**; `ML_Holdout` **389** |

Si el paso 4 muestra el error `"Set RutaCSV to this repository
data/raw/steel_plates_faults.csv"`, **detenerse**: significa que `RutaCSV` volvió
a un valor con separadores doblados. Causa y corrección en
[`POWERBI_POWERQUERY_VALIDATION.md`](POWERBI_POWERQUERY_VALIDATION.md) §3.

### 3.2 Modelo

| # | Acción | Qué registrar |
|---|---|---|
| 8 | Vista de Modelo: confirmar las 3 relaciones del esquema estrella | captura del diagrama |
| 9 | Propiedades de cada relación: cardinalidad **muchos a uno**, filtrado **unidireccional** | los 3 pares de valores |
| 10 | **Confirmar que `ML_Holdout` no tiene ninguna relación** | captura. Si Desktop autodetectó alguna: **registrarla antes de eliminarla**. Control de mayor riesgo científico de esta fase |
| 11 | Panel de campos: las 34 medidas sin marca de error (22 en `_Medidas`, 12 en `ML_Holdout`) | captura |
| 12 | Tipos de datos de las 16 columnas de `ML_Holdout` | captura |

### 3.3 Páginas

| # | Acción | Qué registrar |
|---|---|---|
| 13 | Abrir las 5 páginas una a una | captura de cada una, completa |
| 14 | `MODEL PERFORMANCE & REVIEW`: contar 4 tarjetas, 3 segmentadores, 4 tablas, 1 nota | captura |
| 15 | Ejercitar los segmentadores de las 4 páginas originales | comportamiento previo conservado |
| 16 | Ejercitar los 3 segmentadores ML | las 2 tarjetas de métrica final **no cambian**; `ML Rows`/`ML Errors` y las 4 tablas **sí** cambian |
| 17 | Confirmar que ningún visual aparece en blanco, con error o recortado | captura |

### 3.4 Reconciliación científica

Sin filtros aplicados, contrastar contra
[`POWERBI_RECONCILIATION_RESULTS.md`](POWERBI_RECONCILIATION_RESULTS.md):

| # | Acción | Valor obligatorio |
|---|---|---|
| 18 | `ML Rows` | 389 |
| 19 | `ML Correct` / `ML Errors` | 307 / 82 |
| 20 | `ML Review Rows` / aceptados | 261 / 128 |
| 21 | Macro-F1 **sin redondeo de presentación** | 0.8146728101764369 |
| 22 | Balanced Accuracy **sin redondeo de presentación** | 0.8048726799979933 |
| 23 | Seleccionar A300 | 156 / 121 / 122 |
| 24 | Seleccionar A400 | 233 / 186 / 139 |
| 25 | Limpiar acero, seleccionar Pastry | 32 / 20 / 29 |
| 26 | Tabla de confusión: Bumps → Other_Faults | 21 |
| 27 | Vista de Datos, `row_id` 1277 | `Other_Faults` → `K_Scatch`, confianza 1.0, `HIGH_CONFIDENCE`, `correct_prediction` = 0, `review_required` = 0 |
| 28 | Tabla de estados de revisión | 128 / 173 / 88 |

El formato de tarjeta `0.0000` muestra `0.8147`. La tolerancia `1e-12` exige el
valor sin redondear: exportar los datos del visual o usar el panel de
rendimiento. **Leer la tarjeta no es suficiente** para los pasos 21 y 22.

### 3.5 Guardado y reapertura

| # | Acción |
|---|---|
| 29 | **Guardar** el proyecto PBIP desde Desktop |
| 30 | **Archivo → Guardar como** → formato **Power BI Desktop (`.pbix`)** |
| 31 | Guardar en `C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\steel-plates-quality-mlops\powerbi\artifacts\steel-plates-quality-mlops-powerbi.pbix` — sobrescribe el puntero LFS de 131 bytes (es correcto: el puntero no es un informe) |
| 32 | **Cerrar** Power BI Desktop por completo |
| 33 | **Reabrir el PBIP**: comprobar datos, 5 páginas, medidas y filtros |
| 34 | **Reabrir el PBIX**: comprobar datos, 5 páginas, medidas y filtros |
| 35 | Confirmar que el PBIX **contiene** la página `MODEL PERFORMANCE & REVIEW` y no es una versión anterior |

El paso 35 es esencial: la incidencia #2 existe porque el PBIX publicado no
contenía la página ML.

### 3.6 Integridad

```powershell
Get-FileHash `
  -LiteralPath "<REPO>\powerbi\artifacts\steel-plates-quality-mlops-powerbi.pbix" `
  -Algorithm SHA256
```

Registrar SHA256, tamaño en bytes y la versión de Desktop. Después, revisar el
diff originado por Desktop:

```powershell
Set-Location "<REPO>"
git status --porcelain
git diff --stat
git lfs ls-files        # el PBIX debe aparecer con un oid nuevo, ya no 0a87a4e33b
python -B -m pytest -q --basetemp="$env:TEMP\pytest-post-desktop"
python -B docs/production/evidence/powerbi_static_validation.py
```

### 3.7 Diffs de Desktop previsibles (no son defectos)

Al guardar, Desktop puede reescribir archivos del PBIP. Registrar y clasificar,
no borrar:

| Cambio probable | Interpretación |
|---|---|
| `PBI_QueryOrder` en `model.tmdl` incorpora `RutaMLCSV` y `ML_Holdout` | esperado; la anotación estaba incompleta (ver [`POWERBI_MODEL_DAX_VALIDATION.md`](POWERBI_MODEL_DAX_VALIDATION.md) §1.1) |
| `displayName` de `.platform` pasa a `steel-plates-quality-mlops-powerbi` | esperado; exclusión deliberada de la Fase 2 que Desktop puede resolver por sí mismo |
| Reformateo de TMDL o `lineageTag` nuevos | esperado en un guardado nativo |
| `diagramLayout.json` modificado | esperado si se abre la vista de Modelo |
| `.pbi/localSettings.json`, `.pbi/cache.abf` | **ignorados por `.gitignore`**; no deben entrar en Git |

**Importante.** Si Desktop reescribe archivos cubiertos por
`pre_ml_powerbi_hashes.json`, `test_previous_powerbi_preserved` **fallará a
propósito**: ése es su diseño, detectar ediciones posteriores de Desktop sobre
objetos existentes. Clasificar cada diff y documentarlo. **No** borrar la línea
base ni debilitar la prueba para forzar un PASS.

No reejecutar `tools/prepare_ml_powerbi.py` sobre una página ya refinada en
Desktop: el script la regenera y sobrescribiría el refinamiento.

## 4. Plantilla de registro de evidencias

Rellenar con resultados reales. `NOT_EXECUTED` mientras no se ejecute. Registrar
los fallos de forma explícita.

> **Actualización posterior (vigente):** los controles marcados `NOT_EXECUTED` (G3 inspección visual de RutaCSV y G5 renderizado de páginas) se completaron después mediante la inspección visual del OWNER el 15 nov 2026 (evidencia de parte), registrada en [POWERBI_PRODUCTION_CLOSEOUT.md](POWERBI_PRODUCTION_CLOSEOUT.md). La plantilla se conserva tal como se rellenó.

Estado al 2026-11-15. `PASS (motor)` = verificado consultando el motor en vivo;
`NOT_EXECUTED` = pendiente, requiere la GUI.

```
DESKTOP_VERSION          = 2.156.951.0 (26.07)
FECHA_HORA_EJECUCION     = 2026-11-15 05:42 (apertura), PID 39352

G2  Desktop abre el PBIP sin errores        = PASS (motor)
G3  RutaCSV correcta en el Editor avanzado  = NOT_EXECUTED  (inspeccion visual)
G3  RutaMLCSV resuelve (valor, no texto)    = PASS (motor)  ML_Holdout cargo 389 filas
G3  Cerrar y aplicar sin errores            = PASS (motor)  7/7 particiones en Ready
G3  Hecho original = 1941                   = PASS (motor)  1941
G3  ML_Holdout = 389                        = PASS (motor)  389
G4  3 relaciones del esquema estrella       = PASS (motor)  3, Fact -> 3 dimensiones
G4  Cardinalidad muchos a uno / unidirecc.  = PASS (motor)  From=2 To=1 CrossFilter=1
G4  ML_Holdout SIN relacion                 = PASS (motor)  TableID 28 ausente de TMSCHEMA_RELATIONSHIPS
G4  34 medidas compilan                     = PASS (motor)  34/34 evaluadas sin error
G5  5 paginas renderizan completas          = NOT_EXECUTED
G5  12 componentes de la pagina ML          = NOT_EXECUTED
G5  Tarjetas finales inmunes al filtro      = PASS (motor)  semantica DAX; falta en pantalla
G5  Paginas 1-4 sin regresion               = NOT_EXECUTED
G6  389 / 307 / 82 / 261 / 128 / 81 / 1     = PASS (motor)  389/307/82/261/128; 173+88=261
G6  Macro-F1 sin redondeo                   = PASS (motor)  0.81467281017643689, dif = 0
G6  Balanced accuracy sin redondeo          = PASS (motor)  0.80487267999799328, dif = 0
G6  A300 156/121/122                        = PASS (motor)  156/121/122
G6  A400 233/186/139                        = PASS (motor)  233/186/139
G6  Pastry 32/20/29                         = PASS (motor)  32/20/29
G6  Bumps -> Other_Faults = 21              = PASS (motor)  21
G6  row_id 1277 (6 atributos)               = PASS (motor)  Other_Faults->K_Scatch, 1.0, HIGH_CONFIDENCE, 0, 0
G7  Guardar PBIP desde Desktop              = NOT_EXECUTED
G7  Guardar como PBIX                       = NOT_EXECUTED
G7  Cerrar Desktop                          = NOT_EXECUTED
G7  Reabrir PBIP correctamente              = NOT_EXECUTED
G7  Reabrir PBIX correctamente              = NOT_EXECUTED
G7  El PBIX contiene la pagina ML           = NOT_EXECUTED
G7  PBIX_SHA256                             = NOT_EXECUTED
G7  PBIX_BYTES                              = NOT_EXECUTED
G8  pytest tras el guardado                 = NOT_EXECUTED
G8  validacion estatica tras el guardado    = NOT_EXECUTED
G8  Diff de Desktop clasificado             = NOT_EXECUTED
```

Las filas `PASS (motor)` están respaldadas por
[`evidence/powerbi_live_engine_transcript.txt`](evidence/powerbi_live_engine_transcript.txt).
Ninguna proviene de una captura: **no se ha fabricado ninguna**.

## 5. Condición de bloqueo (orden §19)

Si el proyecto renombrado no abre:

1. Registrar el mensaje de error literal y los archivos afectados.
2. Comparar `.pbip` y `definition.pbir` con la línea base:
   `git diff be46d0c -- "powerbi/project/*"`.
3. Determinar el origen: ruta, esquema, versión de Desktop o cambio de modelo.
   La comprobación más rápida es si `.pbip` y `.pbir` resuelven en disco; la
   validación estática ya lo confirma (77/77 PASS), de modo que un fallo de
   apertura apuntaría a la versión de Desktop o al esquema, no a las rutas.
4. Restaurar la última versión funcional con Git **sin borrar la evidencia del
   intento**: `git checkout main` conserva la rama del renombrado.
5. Corregir la causa demostrada.
6. Repetir las pruebas pertinentes.

Si el renombrado impidiera de forma persistente la carga, **priorizar la
funcionalidad del PBIP sobre la uniformidad del nombre** y elevar la decisión a
OWNER. Reversión completa en
[`POWERBI_RENAME_BASELINE.md`](POWERBI_RENAME_BASELINE.md) §10.

## 6. Estado de los gates

| Gate | Condición | Estado |
|---|---|---|
| G2 | PBIP abre sin errores | ⛔ NO EJECUTADO |
| G3 | Power Query actualiza correctamente | ⛔ NO EJECUTADO (expresiones y datos ✅ verificados) |
| G4 | Modelo semántico y DAX validados | ⛔ NO EJECUTADO (estructura ✅ verificada) |
| G5 | Cinco páginas funcionales | ⛔ NO EJECUTADO (estructura ✅ verificada) |
| G6 | Reconciliación científica satisfactoria | ⛔ NO EJECUTADO (origen ✅ reconciliado) |
| G7 | PBIX generado, cerrado y reabierto | ⛔ **NO EJECUTADO** |

Estado oficial: **`READY_FOR_DESKTOP_VALIDATION`**.

No se promueve a `DESKTOP_VALIDATED` ni a `PBIX_GENERATED_AND_REOPENED`.
`PBIX_GENERATED_AND_REOPENED` sería además un estado técnico que **no**
sustituye la aceptación OWNER. La publicación en Power BI Service constituye una
autorización posterior e independiente, **no solicitada**.
