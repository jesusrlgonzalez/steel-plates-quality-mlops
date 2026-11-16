# POWERBI_RENAME_DEPENDENCY_MATRIX

Orden: **OWNER-PBI-REN-001** · Fase 1 — Inventario de dependencias
Fecha: 2026-11-14 · Responsable: PRODUCCIÓN
Línea base: commit `be46d0c` · Referencia: [`POWERBI_RENAME_BASELINE.md`](POWERBI_RENAME_BASELINE.md)

Búsqueda ejecutada: literal `steel-plates-quality-bi` sobre todo el árbol
(`git grep` / ripgrep, sin filtro de extensión, incluidos binarios y ocultos).

**14 ubicaciones** contienen el literal, con **160 apariciones**. No se aplica
reemplazo global: cada ubicación se clasifica y se trata según su clase.

---

## 1. Resumen por clase

| Clase | Significado | Ubicaciones | Acción |
|---|---|---:|---|
| **A** | Ruta operativa activa — el proyecto no abre/compila/exporta sin corregirla | 7 | **Actualizar** |
| **B** | Instrucción operativa vigente en documentación | 3 | **Actualizar** |
| **C** | Referencia al **antiguo repositorio GitHub**, entidad distinta del artefacto Power BI | 4 | **No tocar** |
| **D** | Evidencia histórica protegida o constante de reconstrucción de hash | 4 | **No tocar** |

Varias ubicaciones pertenecen a más de una clase (p. ej. `powerbi/powerquery/00_Parametros.pq`
es C y D a la vez). El recuento por clase suma más de 14 por ese motivo.

## 2. Clase A — Rutas operativas activas (actualizar)

| # | Ubicación | Apariciones | Qué resuelve a través del nombre | Acción |
|---|---|---:|---|---|
| A1 | `powerbi/project/steel-plates-quality-bi.pbip` | nombre de archivo | Punto de entrada del proyecto | Renombrar a `steel-plates-quality-mlops-powerbi.pbip` |
| A2 | `powerbi/project/steel-plates-quality-bi.pbip` → `artifacts[0].report.path` | 1 | PBIP → directorio `.Report` | Reescribir el valor |
| A3 | `powerbi/project/steel-plates-quality-bi.Report/` | nombre de directorio | Contiene `definition/`, `StaticResources/` | Renombrar directorio |
| A4 | `…Report/definition.pbir` → `datasetReference.byPath.path` | 1 | Informe → modelo semántico (`../…SemanticModel`) | Reescribir el valor |
| A5 | `powerbi/project/steel-plates-quality-bi.SemanticModel/` | nombre de directorio | Contiene TMDL, `.pbi/`, `definition.pbism` | Renombrar directorio |
| A6 | `powerbi/artifacts/steel-plates-quality-bi.pbix` | nombre de archivo | Artefacto de salida (hoy puntero LFS) | Renombrar a `steel-plates-quality-mlops-powerbi.pbix` |
| A7 | `.gitattributes` líneas 9–11 | 3 | Fija `eol=lf` para `pages.json`, la página ML y `ML_Holdout.tmdl` | Reescribir las 3 rutas; **preservar** `*.pbix filter=lfs` (línea 1) |
| A8 | `tools/prepare_ml_powerbi.py` línea 15 (`PROJECT`) | 1 | Raíz desde la que se derivan `REPORT` y `SEMANTIC`; genera la página ML y `ML_Holdout.tmdl` | Reescribir la constante |
| A9 | `tests/test_bi_integration.py` — recorrido de `baseline["files"]` | indirecta | Lee del disco cada clave del manifiesto histórico, escrita con el nombre antiguo | Añadir **correspondencia trazable** antigua→nueva (apartado 5) |

`REPORT` y `SEMANTIC` en `tests/test_bi_integration.py` se importan de
`tools.prepare_ml_powerbi`, por lo que se corrigen solos al actualizar A8. Lo que
**no** se corrige solo es el recorrido de las claves del manifiesto (A9).

### 2.1 Exclusión deliberada: `displayName` en `.platform`

`powerbi/project/steel-plates-quality-bi.Report/.platform` y
`…SemanticModel/.platform` contienen `"displayName": "steel-plates-quality-bi"`
(1 aparición cada uno). **No se modifican.** Justificación:

1. Es el nombre de presentación del elemento Fabric, **no una ruta**: ningún
   componente resuelve a través de él, y su valor no impide abrir, actualizar,
   compilar ni guardar el proyecto.
2. §3 de la orden autoriza renombrar **archivos y directorios**, y prohíbe
   renombrar objetos internos «únicamente para conseguir uniformidad estética».
3. `test_previous_powerbi_preserved` compara `.platform` byte a byte contra
   `pre_ml_powerbi_hashes.json` **sin excepción**. Modificarlo exigiría abrir una
   excepción nueva en un control de preservación sin ninguna necesidad funcional,
   lo que §12 y §15 prohíben.

Se eleva a OWNER como punto de decisión: si se desea alinear el `displayName`,
debe hacerse **en Power BI Desktop** y clasificarse como diff originado por
Desktop, con su propia excepción documentada. Power BI Desktop podría reescribir
este valor por sí mismo al guardar; en tal caso el diff se registrará en la
Fase 7, no aquí.

## 3. Clase B — Instrucciones operativas vigentes (actualizar)

| # | Ubicación | Apariciones | Naturaleza | Acción |
|---|---|---:|---|---|
| B1 | `docs/construir_en_power_bi.md` línea 221 | 1 | Nombra el PBIX entregable | Actualizar al nombre nuevo |
| B2 | `docs/production/PRODUCTION_POWERBI_HANDOFF.md` línea 8 | 1 | Ruta de apertura del PBIP **que se ejecuta hoy** | Marcar como superseded y apuntar al handoff nuevo |
| B3 | `README.md` / `README.es.md` — enlaces al handoff de Desktop | 0 del literal | No contienen el literal, pero dirigen al procedimiento de Desktop | Añadir puntero al entregable nuevo en la Fase 10 |

B2 es el único documento de la clase B que da una instrucción **accionable hoy**
con el nombre antiguo; dejarlo intacto induciría a abrir una ruta inexistente.

## 4. Clase C — Antiguo repositorio GitHub, no el artefacto Power BI (no tocar)

`steel-plates-quality-bi` fue también el nombre de un **repositorio GitHub
anterior**, absorbido por `steel-plates-quality-mlops`. Esas apariciones
designan una entidad distinta del artefacto Power BI y renombrarlas falsearía la
historia o rompería una URL.

| # | Ubicación | Apariciones | Por qué no se toca |
|---|---|---:|---|
| C1 | `CHANGELOG.md` línea 20 | 1 | «This repository absorbs `steel-plates-quality-bi` as its reporting layer» — hecho histórico |
| C2 | `README.md` línea 78 | 1 | Misma frase en inglés |
| C3 | `README.es.md` línea 73 | 1 | Misma frase en español |
| C4 | `powerbi/powerquery/00_Parametros.pq` líneas 2–4 | 3 | Comentario + **URL de datos** `raw.githubusercontent.com/jesusrlgonzalez/steel-plates-quality-bi/main/…`. Reescribirla rompería la fuente de datos en línea. También es Clase D (apartado 5.2) |

## 5. Clase D — Evidencia histórica y constantes de hash (no tocar)

| # | Ubicación | Apariciones | Protección |
|---|---|---:|---|
| D1 | `docs/evidence/pre_ml_powerbi_hashes.json` | 61 | **§5 de la orden, explícito.** Evidencia de preservación pre-ML. No se modifica ni se recalcula. `snapshot_powerbi()` ya se niega a sobrescribirla (`raise ValueError("Pre-ML baseline already exists")`) |
| D2 | `docs/evidence/powerbi_runtime_handoff.md` | 4 | Acta congelada de la puerta humana, con `PRE_ML_PBIX_SHA256` y la tabla `NOT_EXECUTED`. Documenta el estado en su fecha. Queda **superseded** por los entregables nuevos, no editada |
| D3 | `docs/production/PRODUCTION_RELEASE_MANIFEST.json` (78) y `.md` (1) | 79 | Manifiesto SHA256 de la distribución recibida. Alterarlo invalidaría la comprobación de la Fase 0 |
| D4 | `docs/production/PRODUCTION_CHANGELOG.md` línea 6 | 1 | Acta de un cambio ya realizado sobre el archivo con su nombre de entonces |

### 5.1 Trampa crítica: `tests/test_bi_integration.py` línea 34–35

```python
RUTA_CSV_BASELINE = (b'expression RutaCSV = "C:\\\\Users\\\\Lowo\\\\Downloads\\\\'
                     b'steel-plates-quality-bi-main\\\\data\\\\raw\\\\steel_plates_faults.csv"')
```

Esta aparición **parece** un objetivo de renombrado y **no lo es**. Es una
constante de bytes que reconstruye el contenido histórico de `expressions.tmdl`
para validar su `lf_sha256` contra `pre_ml_powerbi_hashes.json`. Corresponde a
`C:\Users\Lowo\Downloads\steel-plates-quality-bi-main\…`, la ruta local del
autor original cuando se tomó la línea base (nombre del ZIP descargado del
repositorio antiguo).

**Modificar un solo byte de esta constante rompe irreversiblemente la
verificación de integridad histórica.** Un reemplazo global `steel-plates-quality-bi`
→ `steel-plates-quality-mlops-powerbi` la habría destruido en silencio. Es la
razón principal por la que §5 de la orden prohíbe el reemplazo indiscriminado.

### 5.2 Doble protección de `00_Parametros.pq`

Además de ser Clase C, este archivo está cubierto por una excepción de hash ya
existente y muy estrecha en `test_previous_powerbi_preserved`:

```python
assert current.count(RAW_URL_OWNER_NOW) == 2 and RAW_URL_OWNER_BASELINE not in current
original = current.replace(RAW_URL_OWNER_NOW, RAW_URL_OWNER_BASELINE)
assert hashlib.sha256(original).hexdigest() == identity["lf_sha256"]
```

Sólo se tolera la renombrada de cuenta GitHub
(`jesusgonzalezmexdata-ux` → `jesusrlgonzalez`, commit `fecb642`); **todos los
demás bytes deben coincidir con la línea base**. Cualquier cambio al segmento
`steel-plates-quality-bi` haría fallar la prueba. Confirmado: **no se toca**.

## 6. Correspondencia trazable antigua → nueva (A9)

`pre_ml_powerbi_hashes.json` es inmutable (D1) pero sus claves deben seguir
resolviendo a archivos reales. Se establece esta correspondencia, aplicada en la
prueba y **sin alterar ninguna comprobación de integridad**:

| Clave histórica (en el manifiesto) | Ruta tras el renombrado |
|---|---|
| `powerbi/project/steel-plates-quality-bi.pbip` | `powerbi/project/steel-plates-quality-mlops-powerbi.pbip` |
| `powerbi/project/steel-plates-quality-bi.Report/**` | `powerbi/project/steel-plates-quality-mlops-powerbi.Report/**` |
| `powerbi/project/steel-plates-quality-bi.SemanticModel/**` | `powerbi/project/steel-plates-quality-mlops-powerbi.SemanticModel/**` |
| `powerbi/artifacts/steel-plates-quality-bi.pbix` | `powerbi/artifacts/steel-plates-quality-mlops-powerbi.pbix` |
| `powerbi/dax/**`, `powerbi/powerquery/**`, `powerbi/data/**`, `powerbi/theme.json` | **sin cambio** |

Reglas de la correspondencia:

1. Se aplica **sólo** a claves bajo `powerbi/project/` y `powerbi/artifacts/`.
2. Sustituye **una sola** aparición del segmento de nombre, nunca un reemplazo global.
3. Los hashes esperados (`sha256`, `lf_sha256`) **no se recalculan**: se siguen
   exigiendo los valores históricos sobre el contenido del archivo renombrado.
4. Se añade un control **nuevo y más estricto**: ninguna ruta antigua bajo esos
   prefijos puede seguir existiendo en disco (detecta un renombrado incompleto).

Para 73 de los 75 archivos el renombrado es un cambio de contenedor y no de
contenido, luego los hashes históricos siguen siendo exigibles tal cual.

### 6.1 Excepción: los dos archivos de referencia cruzada

Los únicos dos archivos cuyo **contenido** debe cambiar por el propio
renombrado son los que resuelven una ruta hacia un directorio renombrado:

| Archivo | Campo | Apariciones del nombre |
|---|---|---:|
| `…-powerbi.pbip` | `artifacts[0].report.path` | 1 |
| `…-powerbi.Report/definition.pbir` | `datasetReference.byPath.path` | 1 |

Para ellos la prueba sustituye el nombre nuevo por el histórico **antes** de
calcular el hash y exige **exactamente una** aparición. Así, todos los bytes
restantes de ambos archivos siguen sometidos a igualdad exacta contra la línea
base. Verificado en ejecución: ver
[`POWERBI_PRODUCTION_TEST_REPORT.md`](POWERBI_PRODUCTION_TEST_REPORT.md).

## 7. Conflicto preexistente entre Fase 3 y Fase 8 de la orden

Independiente del renombrado, pero debe resolverse en el mismo trabajo.

`test_previous_powerbi_preserved` exige que `expressions.tmdl` contenga
exactamente el marcador neutro:

```python
RUTA_CSV_PLACEHOLDER = (b'expression RutaCSV = "C:\\\\path\\\\to\\\\steel-plates-quality-mlops'
                        b'\\\\data\\\\raw\\\\steel_plates_faults.csv"')
assert original.count(RUTA_CSV_PLACEHOLDER) == 1
```

La distribución Windows lo sustituyó por una ruta absoluta real (único original
divergente de la Fase 0), porque §7 de la orden exige que `RutaCSV` **contenga
la ubicación válida del CSV**. Las dos exigencias son incompatibles tal cual:

| Exigencia | Fuente | Implica |
|---|---|---|
| `RutaCSV` debe resolver un CSV existente | Orden §7 (Fase 3), Gate G3 | ruta absoluta local |
| `RutaCSV` debe ser el marcador neutro | `test_previous_powerbi_preserved` | sin ruta local |

Resolución adoptada, conforme a §12 («correspondencia trazable, sin desactivar
controles de preservación»): la prueba aceptará **dos** valores explícitos y
nominados en su código fuente — el marcador neutro **o** el valor local
documentado — y normalizará el que encuentre al valor de la línea base antes de
la comprobación de hash. **Todos los demás bytes siguen sujetos a igualdad
exacta contra la línea base.** No se amplía a «cualquier ruta»: sólo esos dos
literales.

Detalle de ejecución y resultado: [`POWERBI_PRODUCTION_TEST_REPORT.md`](POWERBI_PRODUCTION_TEST_REPORT.md).

## 8. Ubicaciones verificadas como NO afectadas

Comprobado explícitamente que **no** contienen el literal y no requieren cambio:

- `.gitignore` (no contiene el nombre; sus reglas `**/.pbi/*` son genéricas).
- Todos los `page.json` y `visual.json` del informe (5 páginas, 36 visuales).
- Todos los TMDL: `model.tmdl`, `relationships.tmdl`, `expressions.tmdl`,
  `database.tmdl`, `cultures/es-ES.tmdl`, las 7 tablas.
- `definition.pbism`, `diagramLayout.json`, `.pbi/editorSettings.json`,
  `report.json`, `version.json`, `pages.json`, `CY26SU07.json`, `theme.json`.
- `powerbi/dax/measures.dax`, `powerbi/dax/revision_humana.dax`.
- `powerbi/powerquery/01_…pq` a `06_…pq`.
- `.github/workflows/**` — ningún workflow referencia rutas Power BI.
- `src/quality_ml/**` — `BASELINE_PATH` y `EXPORT_PATH` no dependen del nombre.
- Scripts PowerShell de la raíz del paquete: no presentes en esta distribución.

Sólo `definition.pbir` enlaza el informe con el modelo semántico; no existe
ninguna otra referencia cruzada por ruta dentro del PBIP.

## 9. Gate G1 — criterio de aceptación

Tras la Fase 2 debe cumplirse:

1. Cero referencias **activas** (clases A y B) al nombre antiguo.
2. Las clases C y D conservan el nombre antiguo **íntegro y byte a byte**.
3. `pre_ml_powerbi_hashes.json` sin modificar (SHA256 idéntico a la línea base).
4. La constante `RUTA_CSV_BASELINE` de la prueba sin modificar.
5. Ninguna ruta antigua bajo `powerbi/project/` o `powerbi/artifacts/` en disco.
6. `*.pbix filter=lfs diff=lfs merge=lfs -text` intacta en `.gitattributes`.

Resultado registrado en [`POWERBI_RENAME_CHANGELOG.md`](POWERBI_RENAME_CHANGELOG.md).
