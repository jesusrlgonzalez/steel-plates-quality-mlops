# POWERBI_RELEASE_MANIFEST

Orden: **OWNER-PBI-REN-001** · Manifiesto de entrega
Fecha: 2026-11-14 · Responsable: PRODUCCIÓN
Rama: `fix/powerbi-canonical-naming-pbix` · Estado: **`READY_FOR_DESKTOP_VALIDATION`**

---

## 1. Manifiestos SHA256

| Momento | Archivos rastreados | Manifiesto |
|---|---:|---|
| Estado recibido (línea base `be46d0c`) | 274 | [`evidence/powerbi_rename_baseline_inventory.json`](evidence/powerbi_rename_baseline_inventory.json) |
| Tras el renombrado (`HEAD`) | 293 | [`evidence/powerbi_rename_post_inventory.json`](evidence/powerbi_rename_post_inventory.json) |

El manifiesto posterior lista **292** entradas: excluye su propio archivo, cuyo
hash no puede contenerse a sí mismo. Se regenera con
[`evidence/build_manifest.py`](evidence/build_manifest.py) y converge en una
pasada (una segunda ejecución no produce cambios).

Diferencia de recuento: **+19 archivos**, todos entregables y evidencia de esta
orden bajo `docs/production/`. **Ningún archivo original fue eliminado.**

Verificación independiente de que sólo cambió lo previsto:

```powershell
git diff --name-status -M --find-renames=100% be46d0c HEAD
```

| Clase | Nº |
|---|---:|
| Renombrados puros, contenido idéntico | 72 |
| Renombrados con cambio de contenido | 3 |
| Contenido modificado sin renombrado | 4 |
| Añadidos (entregables y evidencia) | 19 |
| **Eliminados** | **0** |

## 2. Entregables Power BI — hashes actuales

| SHA256 | Bytes | Archivo |
|---|---:|---|
| `a872517270cca6600bf6c2e7847cc3d62a261ff2a88f00ccbdadf316bd37e0c6` | 194 | `powerbi/project/steel-plates-quality-mlops-powerbi.pbip` |
| `617d7ba967a48e3325fc5694cd6dafec0a5acc55a9722c23de4a6c2c52744c59` | 141 | `…-powerbi.Report/definition.pbir` |
| `e5be356403c918b50419e0967a0b0a22dbdcc0866ac25cb89a68a5b575420862` | 1 354 | `…-powerbi.SemanticModel/definition/expressions.tmdl` |
| `7a15a4c33068eaf68c5afffa57f3a917daf3bc2c7197799826729c5bb24c5881` | 621 | `…-powerbi.SemanticModel/definition/model.tmdl` |
| `df316433fc6cd184d6ddd22011918ac69546275661a62e3883c8bf3e72af66f2` | 427 | `…-powerbi.SemanticModel/definition/relationships.tmdl` |
| `da20e260a2792dfb71077081c9d6f0f88cb3e8f099b3041758f76039925c237d` | 3 962 | `…-powerbi.SemanticModel/definition/tables/ML_Holdout.tmdl` |
| **`91f89ff2d8ce7605e9b54d9c2c45a6d5cf2511649498e9c70ed82abfe7d86260`** | **252 387** | **`powerbi/artifacts/steel-plates-quality-mlops-powerbi.pbix`** |
| `4e633443f873449454833fdbdf10bc498aef2428e3b4bb25b89b853df18d7c87` | 650 | `.gitattributes` |
| `b525d415b88d12af26479da025b457e4ae3d41237786d8de954105fd82205c7a` | 9 111 | `tools/prepare_ml_powerbi.py` |
| `5e8b965986a3e3f2d336cc5c1bd01d5e1e997af858a44ce0845fa78a9f80be91` | 10 158 | `tests/test_bi_integration.py` |

`model.tmdl`, `relationships.tmdl` y `ML_Holdout.tmdl` conservan **exactamente**
el hash de la línea base.

### 2.1 El PBIX — certificado el 2026-11-15

Guardado por OWNER desde Power BI Desktop `2.156.951.0 (26.07)`, verificado,
reubicado y certificado por PRODUCCIÓN. Paquete OPC real (firma `50 4B 03 04`),
con `DataModel` de 207 684 bytes y las cinco páginas en formato PBIR, incluida
`MODEL PERFORMANCE & REVIEW` con sus 12 componentes. Cerrado y reabierto con
resultados idénticos al PBIP.

Git LFS lo rastrea con oid `91f89ff2…`, que coincide con su SHA256. **Esto repara
el objeto LFS roto**: el puntero anterior (`0a87a4e3…`, 213 709 bytes declarados)
apuntaba a un objeto inexistente en el servidor y hacía fallar cualquier
`git lfs pull`.

Certificación completa:
[`POWERBI_PBIX_CERTIFICATION.md`](POWERBI_PBIX_CERTIFICATION.md).

## 3. Evidencia científica — sin alterar

| Archivo | Verificación |
|---|---|
| `docs/evidence/pre_ml_powerbi_hashes.json` | ✅ sin cambios (§5 de la orden) |
| `reports/ml/final_holdout/metrics.json` | ✅ sin cambios |
| `reports/ml/integration/reconciliation_expected.json` | ✅ sin cambios |
| `artifacts/manifest.json` | ✅ sin cambios |
| `artifacts/model/final_random_forest.joblib` | ✅ sin cambios |
| `data/raw/steel_plates_faults.csv` | ✅ `cb07fc4284cb1bea5b308ef1822f4440e83e16d53703b5d3254a0b5def76f408` |
| `powerbi/data/ml_holdout_evaluation.csv` | ✅ `5f5fb946b8817fc630059878ea67be4c75e38b1da77c5faf88b9eecf8e671cb5` |
| `powerbi/dax/measures.dax`, `revision_humana.dax` | ✅ sin cambios |
| `powerbi/powerquery/*.pq` | ✅ sin cambios |
| `docs/evidence/powerbi_runtime_handoff.md` | ✅ sin cambios (acta congelada) |
| `docs/production/PRODUCTION_RELEASE_MANIFEST.json` | ✅ sin cambios |

Confirmación: `git diff --stat be46d0c -- docs/evidence/ powerbi/powerquery/ powerbi/dax/ reports/ artifacts/ data/`
no devuelve salida.

## 4. Commits

| Commit | Rama | Contenido |
|---|---|---|
| `be46d0c` | `main` | línea base: estado recibido sin modificar |
| `ea40f4a` | `main` | Fase 0: línea base certificada, inventario SHA256, evidencia ZIP↔`e19cd1af` |
| `5583c8e` | `fix/powerbi-canonical-naming-pbix` | Fase 1: matriz de dependencias |
| `2ea038b` | `fix/powerbi-canonical-naming-pbix` | Fase 2: renombrado canónico + corrección de `RutaCSV` |
| (siguiente) | `fix/powerbi-canonical-naming-pbix` | Fases 3–10: entregables y evidencia |

Origen verificado: remoto `main` @ `e19cd1af045ea22e4518f3795f9c5070979a924f`.

## 5. Entregables de la orden

| # | Documento | Estado |
|---|---|---|
| 1 | [`POWERBI_RENAME_BASELINE.md`](POWERBI_RENAME_BASELINE.md) | ✅ |
| 2 | [`POWERBI_RENAME_DEPENDENCY_MATRIX.md`](POWERBI_RENAME_DEPENDENCY_MATRIX.md) | ✅ |
| 3 | [`POWERBI_RENAME_CHANGELOG.md`](POWERBI_RENAME_CHANGELOG.md) | ✅ |
| 4 | [`POWERBI_POWERQUERY_VALIDATION.md`](POWERBI_POWERQUERY_VALIDATION.md) | ✅ parcial (G3 abierto) |
| 5 | [`POWERBI_MODEL_DAX_VALIDATION.md`](POWERBI_MODEL_DAX_VALIDATION.md) | ✅ parcial (G4 abierto) |
| 6 | [`POWERBI_VISUAL_REGRESSION.md`](POWERBI_VISUAL_REGRESSION.md) | ✅ estructural (G5 no alcanzado) |
| 7 | [`POWERBI_RECONCILIATION_RESULTS.md`](POWERBI_RECONCILIATION_RESULTS.md) | ✅ parcial (G6 abierto) |
| 8 | [`POWERBI_PBIP_PBIX_INTEGRITY.md`](POWERBI_PBIP_PBIX_INTEGRITY.md) | ✅ procedimiento; PBIX **NO generado** |
| 9 | [`POWERBI_PRODUCTION_TEST_REPORT.md`](POWERBI_PRODUCTION_TEST_REPORT.md) | ✅ |
| 10 | [`POWERBI_SECURITY_PORTABILITY.md`](POWERBI_SECURITY_PORTABILITY.md) | ✅ |
| 11 | `POWERBI_RELEASE_MANIFEST.md` | ✅ este documento |
| 12 | [`POWERBI_PRODUCTION_HANDOFF_TO_OWNER.md`](POWERBI_PRODUCTION_HANDOFF_TO_OWNER.md) | ✅ |

Material adicional:

| Archivo | Contenido |
|---|---|
| [`evidence/powerbi_rename_baseline_inventory.json`](evidence/powerbi_rename_baseline_inventory.json) | 274 archivos: ruta, tamaño, SHA256 (antes) |
| [`evidence/powerbi_rename_post_inventory.json`](evidence/powerbi_rename_post_inventory.json) | 278 archivos: ruta, tamaño, SHA256 (después) |
| [`evidence/compare_zip_vs_commit.py`](evidence/compare_zip_vs_commit.py) | compara la distribución con el commit `e19cd1af` |
| [`evidence/powerbi_static_validation.py`](evidence/powerbi_static_validation.py) | 77 comprobaciones de las Fases 3–6 |
| [`evidence/check_rutacsv.py`](evidence/check_rutacsv.py) | reproduce la resolución de `RutaCSV`/`RutaMLCSV` con separador doblado y simple |
| [`evidence/build_manifest.py`](evidence/build_manifest.py) | regenera el manifiesto SHA256 posterior |
| [`evidence/revert_powerbi_rename.ps1`](evidence/revert_powerbi_rename.ps1) | reversión guiada en 3 niveles con verificación SHA256 |

| Entregable material | Estado |
|---|---|
| PBIP renombrado y coherente | ✅ |
| `.Report` y `.SemanticModel` coherentes | ✅ |
| **PBIX genuino de Desktop** | ✅ **CERTIFICADO** `91f89ff2…`, 252 387 B |
| Manifiesto SHA256 | ✅ completo, con la entrada del PBIX |
| **Evidencia de apertura y actualización** | ✅ motor en vivo, PBIP y PBIX reabiertos |
| Inspección visual de las 5 páginas | ✅ ejecutada por OWNER |
| Resultados de regresión | ✅ project_checks 5/5 · estáticas 78/78 · `test_bi_integration` 5/5 |
| Parche trazable | ✅ apartado 6 |
| Procedimiento de reversión | ✅ |

Entregables añadidos tras la ejecución en Desktop:

| Archivo | Contenido |
|---|---|
| [`POWERBI_DESKTOP_RUNTIME_EVIDENCE.md`](POWERBI_DESKTOP_RUNTIME_EVIDENCE.md) | consultas al motor en vivo: G2, G3, G4 y G6 |
| [`POWERBI_PBIX_CERTIFICATION.md`](POWERBI_PBIX_CERTIFICATION.md) | certificación del PBIX y clasificación del diff de Desktop |
| [`POWERBI_G5_INSPECTION_CHECKLIST.md`](POWERBI_G5_INSPECTION_CHECKLIST.md) | cuestionario de inspección visual |
| [`evidence/powerbi_desktop_save_hashes.json`](evidence/powerbi_desktop_save_hashes.json) | identidad post-guardado de los 15 objetos reescritos |
| [`evidence/build_desktop_save_hashes.py`](evidence/build_desktop_save_hashes.py) | genera ese manifiesto y rechaza cambios semánticos |
| [`evidence/compare_pbix_pbip.py`](evidence/compare_pbix_pbip.py) | equivalencia funcional PBIX ↔ PBIP |
| [`evidence/inspect_pbix.py`](evidence/inspect_pbix.py) | inspección de solo lectura del paquete PBIX |
| [`evidence/query_pareto_and_counts.ps1`](evidence/query_pareto_and_counts.ps1) | cierre del Pareto al 100 % y recuentos |

## 6. Parche aplicable

Generado fuera del árbol de trabajo, para no versionar un parche de sí mismo:

```powershell
Set-Location "<REPO>"
git format-patch main --stdout > "..\powerbi-canonical-naming.patch"
```

Entregado en
`C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\powerbi-canonical-naming.patch`.

El repositorio local no tiene remoto configurado y PRODUCCIÓN no ha hecho push.
Preparación del Pull Request en
[`POWERBI_PRODUCTION_HANDOFF_TO_OWNER.md`](POWERBI_PRODUCTION_HANDOFF_TO_OWNER.md) §6.

## 7. Estado oficial

**`READY_FOR_DESKTOP_VALIDATION`**

No se declara `DESKTOP_VALIDATED`, ni `PBIX_GENERATED_AND_REOPENED`, ni
`OWNER_ACCEPTED`. Las incidencias #1 y #2 permanecen **OPEN**.
