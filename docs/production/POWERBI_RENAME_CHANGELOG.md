# POWERBI_RENAME_CHANGELOG

Orden: **OWNER-PBI-REN-001** · Fase 2 — Renombrado atómico y referencias
Fecha: 2026-11-14 · Responsable: PRODUCCIÓN
Rama: `fix/powerbi-canonical-naming-pbix` · Base: `ea40f4a` · Línea base: `be46d0c`
Gate: **G1** · Resultado: **CUMPLIDO**

Power BI Desktop no tenía abierto este proyecto durante el renombrado
(comprobado por línea de comandos de los procesos `PBIDesktop.exe`; ver §6).

---

## 1. Commits

| Commit | Contenido |
|---|---|
| `be46d0c` | Línea base: estado recibido sin modificar (en `main`) |
| `ea40f4a` | Fase 0: línea base certificada, inventario SHA256, evidencia ZIP↔commit (en `main`) |
| `5583c8e` | Fase 1: matriz de dependencias |
| `2ea038b` | Fase 2: renombrado canónico + corrección de `RutaCSV` |

## 2. Renombrados ejecutados

Todos mediante `git mv`, con detección de renombrado verificada en el diff.

| Elemento | Nombre anterior | Nombre nuevo |
|---|---|---|
| Archivo PBIP | `steel-plates-quality-bi.pbip` | `steel-plates-quality-mlops-powerbi.pbip` |
| Directorio del informe | `steel-plates-quality-bi.Report` | `steel-plates-quality-mlops-powerbi.Report` |
| Directorio semántico | `steel-plates-quality-bi.SemanticModel` | `steel-plates-quality-mlops-powerbi.SemanticModel` |
| Artefacto PBIX | `steel-plates-quality-bi.pbix` | `steel-plates-quality-mlops-powerbi.pbix` |

**75 archivos** movidos en total. Clasificación del diff frente a la línea base
(`git diff -M --find-renames=100% be46d0c HEAD`):

| Clase | Nº |
|---|---:|
| Renombrados puros, contenido idéntico (`R100`) | **72** |
| Renombrados con cambio de contenido | **3** |
| Cambios de contenido sin renombrado | **4** |

Ningún archivo interno fue renombrado: `definition.pbir`, `definition.pbism`,
`model.tmdl`, `relationships.tmdl`, `expressions.tmdl`, `ML_Holdout.tmdl` y los
demás conservan sus nombres convencionales. No se renombró ninguna tabla,
columna, medida, página ni identificador de visual.

## 3. Referencias actualizadas

### 3.1 PBIP

```diff
-        "path": "steel-plates-quality-bi.Report"
+        "path": "steel-plates-quality-mlops-powerbi.Report"
```

`artifacts[0].report.path`. Verificado: resuelve a un directorio existente.

### 3.2 PBIR

```diff
-      "path": "../steel-plates-quality-bi.SemanticModel"
+      "path": "../steel-plates-quality-mlops-powerbi.SemanticModel"
```

`datasetReference.byPath.path`, ruta relativa. Verificado: resuelve a un
directorio existente desde la ubicación del `.Report`.

### 3.3 `.gitattributes`

Las tres rutas `eol=lf` actualizadas. La regla LFS **no se tocó**:

```
*.pbix filter=lfs diff=lfs merge=lfs -text
```

Verificado tras el commit: `git lfs ls-files` devuelve una sola entrada,
`0a87a4e33b - powerbi/artifacts/steel-plates-quality-mlops-powerbi.pbix`.

### 3.4 `tools/prepare_ml_powerbi.py`

```diff
-PROJECT = "powerbi/project/steel-plates-quality-bi"
+PROJECT = "powerbi/project/steel-plates-quality-mlops-powerbi"
```

`REPORT` y `SEMANTIC` se derivan de `PROJECT`, por lo que quedan corregidos. La
lógica de generación no se modificó: `test_text_generation_idempotent` sigue
demostrando que dos ejecuciones consecutivas no alteran ningún byte.

### 3.5 `tests/test_bi_integration.py`

Tres correspondencias trazables, sin desactivar ningún control. Detalle en
[`POWERBI_PRODUCTION_TEST_REPORT.md`](POWERBI_PRODUCTION_TEST_REPORT.md) §3.
Se añadió además un control **nuevo** que hace fallar la prueba si queda una
ruta antigua en disco (renombrado incompleto). **Ninguna aserción científica fue
modificada.**

### 3.6 Documentación

| Archivo | Cambio |
|---|---|
| `docs/construir_en_power_bi.md` | nombre del PBIX entregable (línea 221) |
| `docs/production/PRODUCTION_POWERBI_HANDOFF.md` | cabecera **SUPERSEDED** + corrección de la nota `UNVERIFIED` |

## 4. TMDL: conservación de definiciones

Hashes SHA256 **idénticos a la línea base** tras el renombrado:

| SHA256 | Archivo |
|---|---|
| `7a15a4c33068eaf68c5afffa57f3a917daf3bc2c7197799826729c5bb24c5881` | `model.tmdl` |
| `df316433fc6cd184d6ddd22011918ac69546275661a62e3883c8bf3e72af66f2` | `relationships.tmdl` |
| `da20e260a2792dfb71077081c9d6f0f88cb3e8f099b3041758f76039925c237d` | `tables/ML_Holdout.tmdl` |

Igualmente sin cambios: `database.tmdl`, `cultures/es-ES.tmdl`, `_Medidas.tmdl`,
`Dim_Acero.tmdl`, `Dim_BandaTamano.tmdl`, `Dim_TipoDefecto.tmdl`,
`Fact_Defecto.tmdl`, `Param_Especificacion.tmdl`, `definition.pbism`,
`diagramLayout.json`, `.pbi/editorSettings.json` y los 57 archivos del informe
salvo `definition.pbir`.

Resolubilidad verificada estáticamente (77/77 comprobaciones): 7 tablas
referenciadas con su TMDL presente, 3 relaciones del esquema estrella,
`ML_Holdout` sin relación alguna, 16 columnas y 12 medidas, partición en modo
import apuntando a `RutaMLCSV`. Ver
[`POWERBI_MODEL_DAX_VALIDATION.md`](POWERBI_MODEL_DAX_VALIDATION.md).

## 5. Corrección funcional independiente del renombrado

`expressions.tmdl` cambió por una segunda razón, **no** por el renombrado:

```diff
-expression RutaCSV = "C:\\path\\to\\steel-plates-quality-mlops\\data\\raw\\steel_plates_faults.csv"
+expression RutaCSV = "C:\path\to\steel-plates-quality-mlops\data\raw\steel_plates_faults.csv"
```

Defecto demostrado, causa y prueba en
[`POWERBI_POWERQUERY_VALIDATION.md`](POWERBI_POWERQUERY_VALIDATION.md) §3.
Resumen: TMDL almacena el código M literalmente y no escapa la barra invertida,
de modo que el separador doblado rompía la derivación de `RutaMLCSV` y
`ML_Holdout` nunca cargaba. Autorizado por §1.4 de la orden («corregir los
problemas técnicos comprobados que impidan abrir, actualizar, compilar o
guardar el proyecto»).

| SHA256 | Bytes | Estado |
|---|---:|---|
| `e077b5b306cfd5ed9638435be67e985563edfa243bca82948d92f658188a93a1` | 1 361 | línea base (separador doblado) |
| `e5be356403c918b50419e0967a0b0a22dbdcc0866ac25cb89a68a5b575420862` | 1 354 | tras la corrección |

## 6. Power BI Desktop cerrado durante la operación

Tres procesos `PBIDesktop.exe` estaban activos, **ninguno con este proyecto**:

| PID | Proyecto abierto |
|---|---|
| 33100 | `Proyecto_1\…\P30_Publicacion_RLS.pbip` |
| 33276 | `P26_Dashboard_Dinamico_PBIR\…\P26_Dashboard_Dinamico.pbip` |
| 34952 | `Steel_Plates_PowerBI_Lista_Para_Desktop_Local\…\steel-plates-quality-bi.pbip` |

Los cuatro `git mv` se completaron sin bloqueo de archivos, lo que confirma la
ausencia de descriptores abiertos sobre el proyecto canónico.

**Advertencia para OWNER:** el PID 34952 tiene abierta una **tercera
distribución** del proyecto en
`C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\Steel_Plates_PowerBI_Lista_Para_Desktop_Local`,
cuyo `expressions.tmdl` difiere (1 333 bytes) y que **no** ha recibido este
renombrado ni la corrección de `RutaCSV`. Validar en esa carpeta **no** valida
este proyecto. Ver [`POWERBI_SECURITY_PORTABILITY.md`](POWERBI_SECURITY_PORTABILITY.md) §5.

## 7. Gate G1 — verificación de las condiciones

| # | Condición | Resultado |
|---|---|---|
| 1 | Cero referencias activas (clases A y B) al nombre antiguo | ✅ |
| 2 | Clases C y D conservan el nombre antiguo byte a byte | ✅ `git diff be46d0c` vacío para esas rutas |
| 3 | `pre_ml_powerbi_hashes.json` sin modificar | ✅ `ffbfa18bd740df61…` sin cambio |
| 4 | `RUTA_CSV_BASELINE` de la prueba sin modificar | ✅ |
| 5 | Ninguna ruta antigua bajo `powerbi/project/` o `powerbi/artifacts/` | ✅ barrido de disco vacío |
| 6 | Regla LFS `*.pbix` intacta | ✅ |

Referencias restantes al literal `steel-plates-quality-bi`, todas legítimas:

| Archivo | Nº | Clase |
|---|---:|---|
| `docs/evidence/pre_ml_powerbi_hashes.json` | 61 | D — evidencia protegida |
| `docs/production/PRODUCTION_RELEASE_MANIFEST.json` / `.md` | 79 | D — manifiesto histórico |
| `docs/evidence/powerbi_runtime_handoff.md` | 4 | D — acta congelada |
| `docs/production/PRODUCTION_CHANGELOG.md` | 1 | D — acta histórica |
| `powerbi/powerquery/00_Parametros.pq` | 3 | C+D — repositorio antiguo y URL de datos |
| `CHANGELOG.md`, `README.md`, `README.es.md` | 3 | C — repositorio antiguo |
| `powerbi/project/…-powerbi.{Report,SemanticModel}/.platform` | 2 | exclusión deliberada (matriz §2.1) |
| `tests/test_bi_integration.py` | 2 | constantes históricas de hash |
| `docs/production/POWERBI_RENAME_*.md`, `evidence/*.json` | — | entregables que citan el nombre antiguo |

**G1: CUMPLIDO.** Ninguna referencia activa impide abrir o construir el proyecto.

## 8. Lo que este changelog NO acredita

- Que Power BI Desktop abra el proyecto: **no ejecutado** (G2).
- Que Power Query actualice: **no ejecutado** (G3).
- Que las páginas rendericen: **no ejecutado** (G5).
- Que exista un PBIX: **no generado** (G7).

Estado tras la Fase 2: `IMPLEMENTATION_READY`.
