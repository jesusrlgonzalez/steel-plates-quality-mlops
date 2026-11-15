# POWERBI_PACKAGE_CONTENTS

Contenido del paquete entregado · Orden **OWNER-PBI-REN-001**
Fecha: 2026-11-15 · Para: equipo de desarrollo

---

## 1. Dónde está

```
C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\steel-plates-quality-mlops
```

Es un repositorio Git completo y autocontenido. **No hay remoto configurado** y
no se ha hecho push: todo está local.

| Dato | Valor |
|---|---|
| Rama de trabajo | `fix/powerbi-canonical-naming-pbix` |
| Rama base | `main` |
| Commits en la rama | **13** |
| Commits totales | 15 |
| Autor (único) | `Jesús R. L. González <285482007+jesusrlgonzalez@users.noreply.github.com>` |
| Archivos rastreados | **314** |
| Árbol de trabajo | limpio |

Parche aplicable, **fuera** del árbol para no versionarse a sí mismo:

```
C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\powerbi-canonical-naming.patch
```

## 2. Lo que se abre

| Qué | Ruta |
|---|---|
| **Proyecto editable (PBIP)** | `powerbi\project\steel-plates-quality-mlops-powerbi.pbip` |
| **Informe ejecutable (PBIX)** | `powerbi\artifacts\steel-plates-quality-mlops-powerbi.pbix` |

**No uses «Archivos recientes» de Power BI**: esa lista puede apuntar a copias
antiguas. Abre por ruta.

### 2.1 Identidad del PBIX

| Dato | Valor |
|---|---|
| Tamaño | **252 387 bytes** |
| **SHA256** | **`91f89ff2d8ce7605e9b54d9c2c45a6d5cf2511649498e9c70ed82abfe7d86260`** |
| Power BI Desktop | `2.156.951.0 (26.07)` |
| Git LFS oid | `91f89ff2…` (coincide con el SHA256) |

## 3. Reparto por áreas

**314 archivos rastreados.**

| Área | Archivos | Qué contiene |
|---|---:|---|
| `powerbi/` | **88** | el componente Power BI completo (apartado 4) |
| `docs/` | **69** | documentación, evidencia científica y el expediente de producción |
| `reports/` | 35 | métricas congeladas, holdout, incertidumbre, interpretabilidad |
| raíz | 33 | README, licencia, requirements, Dockerfile, Streamlit |
| `src/` | 25 | `quality_ml`: datos, modelos, evaluación, inferencia |
| `tests/` | 20 | suite de pruebas |
| `dbt/` | 11 | modelos y pruebas dbt |
| `tools/` | 10 | utilidades de línea de comandos |
| `data/` | 5 | CSV crudo y esquema estrella |
| otros | 18 | `examples/`, `qbi/`, `site/`, `deploy/`, `artifacts/`, `etl/` |

## 4. El componente Power BI

### 4.1 Estructura

```
powerbi/
├── project/
│   ├── steel-plates-quality-mlops-powerbi.pbip          <- se abre esto
│   ├── steel-plates-quality-mlops-powerbi.Report/        57 archivos
│   └── steel-plates-quality-mlops-powerbi.SemanticModel/ 16 archivos
├── artifacts/
│   └── steel-plates-quality-mlops-powerbi.pbix          <- 252 387 B, vía Git LFS
├── data/
│   └── ml_holdout_evaluation.csv                        <- 389 filas, origen de ML_Holdout
├── dax/
│   ├── measures.dax
│   └── revision_humana.dax
├── powerquery/                                           7 archivos .pq de referencia
└── theme.json
```

### 4.2 El informe — 5 páginas, 46 visuales

| # | Identificador | Nombre | Lienzo | Visuales |
|---|---|---|---|---:|
| 1 | `5ee9939d0101076d3381` | Resumen ejecutivo | 1280×720 | 10 |
| 2 | `f50491653678cb19a699` | Control y capacidad | 1280×720 | 8 |
| 3 | `1f75dde540a696f2b18f` | Exploracion *(drillthrough)* | 1280×720 | 13 |
| 4 | `cb973d91eb46886907c2` | Tooltip Pareto *(oculta en modo vista)* | 320×240 | 3 |
| 5 | `ml_performance_review` | **MODEL PERFORMANCE & REVIEW** | 1280×**1040** | 12 |

La página 5 son 4 tarjetas + 3 segmentadores + 4 tablas + 1 nota contextual.

Formato **PBIR**: cada visual es su propio `visual.json`. Ya está habilitado en
el Desktop de esta máquina (el proyecto `P26_Dashboard_Dinamico` usa el mismo
formato), así que no hay que activar ninguna característica en versión preliminar.

### 4.3 El modelo semántico — 7 tablas, 34 medidas, 3 relaciones

| Tabla | Rol | Filas |
|---|---|---:|
| `Fact_Defecto` | hecho | **1 941** |
| `Dim_TipoDefecto` | dimensión | 7 |
| `Dim_Acero` | dimensión | 32 |
| `Dim_BandaTamano` | dimensión | 5 |
| `Param_Especificacion` | parámetro | 1 |
| `_Medidas` | 22 medidas DAX | — |
| **`ML_Holdout`** | evaluación ML, **12 medidas** | **389** |

Las 3 relaciones van de `Fact_Defecto` a las tres dimensiones, **muchos a uno** y
**unidireccionales**.

> **Regla científica inalterable.** `ML_Holdout` **no tiene ninguna relación** y
> debe seguir así. Los 389 registros del holdout no se incorporan a los 1 941 del
> análisis original. Si al abrir aparece una relación autodetectada hacia
> `ML_Holdout`, **regístrala antes de borrarla**.

Las dos tarjetas `Final Macro-F1 (389)` y `Final Balanced Accuracy (389)` son
**literales DAX**, no agregaciones: ningún contexto de filtro puede alterarlas.
Es intencionado, y hay prueba de ello en el motor.

### 4.4 `RutaCSV` es un parámetro

```
expression RutaCSV = "…\data\raw\steel_plates_faults.csv" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
```

Para cambiar la ruta en otra máquina: **Inicio → Transformar datos → Editar
parámetros**. Un campo de texto, sin tocar código M.

Dos reglas que hay que respetar:

1. **Una sola barra invertida por separador.** TMDL guarda el código M literal y
   no escapa la barra. Con el separador doblado, `File.Contents` sobrevive pero
   `RutaMLCSV` produce `//data//raw//`, su `Text.Contains` falla y **`ML_Holdout`
   no carga** — la página ML entera queda sin datos. Fue un defecto real,
   corregido; detalle en `POWERBI_POWERQUERY_VALIDATION.md` §3.
2. **La ruta debe contener el segmento `\data\raw\`**: es lo que `RutaMLCSV` usa
   para derivar la raíz y localizar el CSV del holdout. No hay que tocar
   `RutaMLCSV`, se recalcula sola.

## 5. El expediente de producción — `docs/production/`

### 5.1 Los documentos de esta orden (16)

| Documento | Para qué |
|---|---|
| `POWERBI_PRODUCTION_CLOSEOUT.md` | **empieza aquí**: cierre, estado y pasos de publicación |
| `POWERBI_PACKAGE_CONTENTS.md` | este documento |
| `POWERBI_PBIX_CERTIFICATION.md` | identidad del PBIX y clasificación del diff de Desktop |
| `POWERBI_DESKTOP_RUNTIME_EVIDENCE.md` | consultas al motor real: G2, G3, G4, G6 |
| `POWERBI_G5_INSPECTION_CHECKLIST.md` | cuestionario de inspección visual, con los valores esperados |
| `POWERBI_RENAME_BASELINE.md` | línea base certificada y procedimiento de reversión |
| `POWERBI_RENAME_DEPENDENCY_MATRIX.md` | las 14 ubicaciones del nombre antiguo, en 4 clases |
| `POWERBI_RENAME_CHANGELOG.md` | qué se renombró y qué referencias se actualizaron |
| `POWERBI_POWERQUERY_VALIDATION.md` | el defecto del separador doblado, con su demostración |
| `POWERBI_MODEL_DAX_VALIDATION.md` | tablas, relaciones, cardinalidades y las 34 medidas |
| `POWERBI_VISUAL_REGRESSION.md` | las 5 páginas y los 12 componentes de la ML |
| `POWERBI_RECONCILIATION_RESULTS.md` | reconciliación científica, indicador por indicador |
| `POWERBI_PRODUCTION_TEST_REPORT.md` | resultados de regresión, antes y después del guardado |
| `POWERBI_SECURITY_PORTABILITY.md` | rutas, fuentes, portabilidad y datos sensibles |
| `POWERBI_RELEASE_MANIFEST.md` | manifiesto de entrega y hashes |
| `POWERBI_PBIP_PBIX_INTEGRITY.md` | el procedimiento de Fase 7 que se siguió |
| `POWERBI_PRODUCTION_HANDOFF_TO_OWNER.md` | entrega a OWNER y desvíos declarados |

Los 11 archivos `PRODUCTION_*.md` / `.json` son el expediente **anterior**, de la
preparación del 2026-11-14. Se conservan como historia; `PRODUCTION_POWERBI_HANDOFF.md`
lleva una cabecera **SUPERSEDED**.

### 5.2 Evidencia ejecutable — `docs/production/evidence/` (22 archivos)

Todo script deriva la raíz del repositorio de su propia ubicación: ninguno lleva
rutas codificadas.

**Validación**

| Script | Qué hace |
|---|---|
| `powerbi_static_validation.py` | **78 comprobaciones** de las Fases 3 a 6. Exit 0 = todo PASS |
| `compare_pbix_pbip.py` | equivalencia funcional PBIX ↔ PBIP |
| `inspect_pbix.py` | inspección de solo lectura del paquete PBIX |
| `check_rutacsv.py` | reproduce la resolución de `RutaCSV`/`RutaMLCSV` leyendo el valor real |

**Consultas al motor en vivo** (con el proyecto abierto en Desktop)

| Script | Qué devuelve |
|---|---|
| `query_live_model.ps1` | tablas, relaciones, particiones, recuentos, segmentos, `row_id` 1277 |
| `query_all_measures.ps1` | evalúa las 34 medidas una por una |
| `query_precision.ps1` | la tolerancia `1e-12` calculada por el propio motor |
| `query_pareto_and_counts.ps1` | cierre del Pareto al 100 % y recuentos |
| `query_expressions.ps1` | si el modelo lleva una ruta personal |

**Integridad y manifiestos**

| Archivo | Qué es |
|---|---|
| `powerbi_rename_baseline_inventory.json` | SHA256 de los 274 archivos recibidos |
| `powerbi_rename_post_inventory.json` | SHA256 del estado actual |
| `powerbi_desktop_save_hashes.json` | identidad post-guardado de los 15 objetos que Desktop reescribió |
| `powerbi_live_engine_transcript.txt` | salida cruda de las consultas XMLA |
| `build_manifest.py` | regenera el manifiesto SHA256 |
| `build_desktop_save_hashes.py` | genera el manifiesto certificado y **rechaza** cambios semánticos |
| `compare_zip_vs_commit.py` | compara la distribución con el commit `e19cd1af` |
| `classify_desktop_diff.py` | separa cambios de contenido de los de fin de línea |

**Auditoría y mantenimiento**

| Script | Qué hace |
|---|---|
| `audit_repo_leaks.py` | busca rutas, cuentas, secretos y correos en los archivos rastreados |
| `audit_pbix_leaks.py` | busca cadenas personales dentro del paquete PBIX |
| `scrub_docs.py` | generaliza rutas personales en el expediente |
| `remap_commit_hashes.py` | actualiza los hashes citados tras reescribir el historial |
| `revert_powerbi_rename.ps1` | **reversión guiada en 3 niveles**, con verificación SHA256 |

### 5.3 Evidencia científica congelada — `docs/evidence/`

| Archivo | Estado |
|---|---|
| `pre_ml_powerbi_hashes.json` | **inmutable**. Guarda el informe pre-ML byte a byte. No se modifica ni se recalcula |
| `powerbi_runtime_handoff.md` | acta congelada de la puerta humana. Superseded, no editada |
| `powerbi_ml_reconciliation.md` | reconciliación esperada |

## 6. Cómo verificar el paquete

```powershell
Set-Location "<REPO>"

# 1. Comprobaciones del proyecto
python -B -m tools.project_checks lint
python -B -m tools.project_checks validate-data
python -B -m tools.project_checks validate-artifact
python -B -m tools.project_checks batch-smoke
python -B -m tools.project_checks validate-evidence

# 2. Validación estática del componente Power BI (78 comprobaciones)
python -B docs/production/evidence/powerbi_static_validation.py

# 3. Suite completa. --basetemp es OBLIGATORIO en esta máquina:
#    la ACL de %LOCALAPPDATA%\Temp\pytest-of-<USUARIO> deniega el listado y sin
#    el parámetro aparecen 27 errores de entorno ajenos al proyecto.
python -B -m pytest -q --basetemp="$env:TEMP\pytest-verificacion"

# 4. Integridad del PBIX
Get-FileHash -LiteralPath "powerbi\artifacts\steel-plates-quality-mlops-powerbi.pbix" -Algorithm SHA256
git lfs ls-files
```

Resultados esperados: `project_checks` 5/5 · estática **78/78** ·
`tests/test_bi_integration.py` 5/5 · suite completa **151 passed, 2 skipped**.

## 7. Cifras que el informe debe mostrar

Sin filtros aplicados. Verificadas contra el motor de Power BI.

| Indicador | Valor |
|---|---:|
| `Fact_Defecto` | 1 941 |
| `ML_Holdout` | 389 |
| Aciertos / errores | 307 / 82 |
| Revisión candidata / aceptados | 261 / 128 |
| Errores enviados a revisión / no capturados | 81 / 1 |
| `Final Macro-F1 (389)` | `0.81467281017643689` |
| `Final Balanced Accuracy (389)` | `0.80487267999799328` |
| Exactitud observada | `0.78920308483290491` |
| Estados de revisión | 128 / 173 / 88 |
| A300 · A400 · Pastry | 156/121/122 · 233/186/139 · 32/20/29 |
| Confusión Bumps → Other_Faults | 21 |
| Cierre del Pareto | exactamente **1** |

El error no capturado es `row_id = 1277`: `Other_Faults` clasificado como
`K_Scatch` con confianza 1.0, `HIGH_CONFIDENCE` y fuera de la revisión candidata.
**Debe seguir visible** en la tabla de estados de revisión.

## 8. Lo que el equipo debe saber antes de tocar nada

| # | Advertencia |
|---|---|
| 1 | **No ejecutar `tools/prepare_ml_powerbi.py`** sobre el proyecto actual: regenera la página ML y sobrescribiría el refinamiento que Desktop le aplicó |
| 2 | **No modificar `docs/evidence/pre_ml_powerbi_hashes.json`.** Es evidencia inmutable; `snapshot_powerbi()` ya se niega a sobrescribirla |
| 3 | **No tocar `RUTA_CSV_BASELINE` en `tests/test_bi_integration.py`.** Es una constante de bytes que reconstruye el hash histórico: un byte distinto rompe la verificación |
| 4 | Si `test_previous_powerbi_preserved` falla tras un guardado de Desktop, **es su diseño**. Clasificar el diff con `build_desktop_save_hashes.py`; **no** debilitar la prueba |
| 5 | `pytest` necesita `--basetemp` en esta máquina (ACL del perfil) |
| 6 | `git checkout` puede reescribir los CSV congelados por `text eol=crlf`. `core.autocrlf` está en `false`; verificar SHA256 tras cualquier checkout |
| 7 | El PBIX lleva la ruta local en su expresión `RutaCSV`. Receta para eliminarla en `POWERBI_PRODUCTION_CLOSEOUT.md` §5bis.4 |
| 8 | Las fuentes son `File.Contents` sobre `C:`. **No se actualizan en Power BI Service** sin puerta de enlace o migración de las fuentes |

## 9. Copias que NO son este paquete

En la misma máquina existen dos copias más. **Ninguna es el entregable.**

| Ruta | Qué es |
|---|---|
| `…\STEEL_PLATES_QUALITY_MLOPS_PARA_WINDOWS\steel-plates-quality-mlops` | línea base intacta del estado recibido. Respaldo de reversión; **no editar** |
| `…\Steel_Plates_PowerBI_Lista_Para_Desktop_Local` | distribución divergente, **sin** el renombrado ni la corrección de `RutaCSV` |

Forma rápida de distinguirlas: el nombre del `.pbip`. Si se llama
`steel-plates-quality-bi.pbip` (nombre corto, antiguo), **es la carpeta
equivocada**. El entregable se llama `steel-plates-quality-mlops-powerbi.pbip`.

## 10. Estado

| Gate | Estado |
|---|---|
| G0 línea base · G1 nombres | ✅ |
| G2 abre · G3 actualiza · G4 modelo y DAX | ✅ |
| G5 páginas · G6 reconciliación · G7 PBIX | ✅ |
| G8 pruebas y hashes | ✅ |
| G9 Pull Request | ⛔ **no abierto** |
| G10 aceptación OWNER | ⛔ **pendiente** |

**Nada se ha subido a GitHub.** Nada se ha publicado en Power BI Service. Las
incidencias **#1** y **#2** siguen **OPEN**.
