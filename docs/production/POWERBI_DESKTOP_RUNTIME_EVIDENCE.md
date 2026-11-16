# POWERBI_DESKTOP_RUNTIME_EVIDENCE

Orden: **OWNER-PBI-REN-001** · Evidencia de runtime del motor de Power BI Desktop
Fecha: 2026-11-15 · Responsable: PRODUCCIÓN
Gates afectados: **G2 ✅ · G3 ✅ · G4 ✅ · G6 ✅** · G5 y G7 siguen abiertos

Este documento **actualiza** el alcance declarado en
[`POWERBI_POWERQUERY_VALIDATION.md`](POWERBI_POWERQUERY_VALIDATION.md),
[`POWERBI_MODEL_DAX_VALIDATION.md`](POWERBI_MODEL_DAX_VALIDATION.md),
[`POWERBI_RECONCILIATION_RESULTS.md`](POWERBI_RECONCILIATION_RESULTS.md) y
[`POWERBI_PBIP_PBIX_INTEGRITY.md`](POWERBI_PBIP_PBIX_INTEGRITY.md), donde esos
gates figuraban como no ejecutados.

---

## 1. Qué se hizo y por qué es válido

Power BI Desktop abrió el PBIP renombrado y levantó su propio motor de Analysis
Services en espacio de trabajo local. **Ese motor es consultable**: expone un
extremo XMLA en `localhost` y acepta DAX y vistas DMV.

PRODUCCIÓN conectó a ese extremo en **solo lectura** y consultó el modelo que
Desktop había cargado. Las cifras de este documento provienen del **motor real
de Power BI**, no de los CSV ni de los archivos TMDL.

Esto **no** es una simulación ni una reconstrucción: es el mismo motor que
calcula los visuales. Tampoco es una edición: no se ejecutó ningún comando de
escritura, y el árbol de trabajo quedó sin modificar (apartado 8).

### 1.1 Trazabilidad de la sesión

| Dato | Valor |
|---|---|
| Power BI Desktop | `2.156.951.0 (26.07)` · `C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe` |
| PID de Desktop | **39352** |
| Título de ventana | `steel-plates-quality-mlops-powerbi` |
| Proyecto abierto | `powerbi\project\steel-plates-quality-mlops-powerbi.pbip` |
| Motor | `msmdsrv.exe` PID **9204**, padre **39352** |
| Extremo | `localhost:57045` (`::1` y `127.0.0.1`, estado Listen, propietario PID 9204) |
| Base de datos | `da6145ee-e092-4cca-8861-d0cfbd3aae14` |
| Cliente | `Microsoft.PowerBI.AdomdClient.dll` v15.0.0.0, namespace `Microsoft.AnalysisServices.AdomdClient` |

La correlación puerto → PID 9204 → padre 39352 establece que el motor consultado
es el de **este** proyecto y no el de los otros tres Desktop abiertos en el
equipo (PIDs 33100, 33276, 34952, con sus propios `msmdsrv` 38472, 36856, 37764).

Transcripción íntegra: [`evidence/powerbi_live_engine_transcript.txt`](evidence/powerbi_live_engine_transcript.txt).
Scripts: [`evidence/query_live_model.ps1`](evidence/query_live_model.ps1),
[`evidence/query_precision.ps1`](evidence/query_precision.ps1),
[`evidence/query_all_measures.ps1`](evidence/query_all_measures.ps1).

## 2. G2 — El PBIP renombrado abre

| Control | Resultado |
|---|---|
| Desktop lanza el proyecto sin cuelgue | ✅ `Responding = True` |
| Título derivado del nombre canónico nuevo | ✅ `steel-plates-quality-mlops-powerbi` |
| Motor instanciado para el proyecto | ✅ `msmdsrv` 9204, hijo de 39352 |
| Modelo alojado y consultable | ✅ conexión XMLA aceptada |
| Las rutas `.pbip → .Report → .SemanticModel` resuelven | ✅ implícito: el modelo cargó |

**G2: PASS.** El renombrado no rompió la apertura.

## 3. G3 — Power Query actualiza

### 3.1 Estado de las particiones (DMV `TMSCHEMA_PARTITIONS`)

| TableID | Partición | State | Mode |
|---:|---|---:|---:|
| 10 | `Dim_TipoDefecto` | **1** | 0 |
| 13 | `Dim_Acero` | **1** | 0 |
| 16 | `Dim_BandaTamano` | **1** | 0 |
| 19 | `Fact_Defecto` | **1** | 0 |
| 22 | `Param_Especificacion` | **1** | 0 |
| 25 | `_Medidas` | **1** | 0 |
| 28 | `ML_Holdout` | **1** | 0 |

`State = 1` es *Ready*: la partición se procesó con éxito. `Mode = 0` es
*Import*. **Las siete particiones están en Ready**, ninguna en error.

### 3.2 Recuento de filas (DAX `COUNTROWS`)

| Tabla | Exigido | Observado en el motor | Resultado |
|---|---:|---:|---|
| `Fact_Defecto` | 1 941 | **1 941** | ✅ |
| `ML_Holdout` | 389 | **389** | ✅ |
| `Dim_TipoDefecto` | 7 clases | **7** | ✅ |
| `Dim_Acero` | — | 32 | registrado |
| `Dim_BandaTamano` | — | 5 | registrado |
| `Param_Especificacion` | — | 1 | registrado |

### 3.3 Por qué esto demuestra que la corrección de `RutaCSV` funcionó

No existe caché: `.pbi/` contiene únicamente `editorSettings.json` (243 bytes).
No hay `cache.abf`. Por tanto Desktop **ejecutó las consultas Power Query contra
los CSV al abrir**, no leyó un modelo almacenado.

Que `ML_Holdout` tenga 389 filas en Ready significa que:

1. `RutaCSV` resolvió un archivo real;
2. `Text.Replace` produjo `/data/raw/` y `Text.Contains` fue **verdadero**;
3. `RutaMLCSV` devolvió una ruta y **no** lanzó
   `error "Set RutaCSV to this repository data/raw/steel_plates_faults.csv"`;
4. la guarda `Table.RowCount(Tipos) = 389` se cumplió;
5. la guarda `List.Distinct(Tipos[dataset_role]) = {"FINAL_HOLDOUT_EVALUATION"}` se cumplió;
6. la validación de esquema de las 16 columnas pasó.

**Con el valor doblado de la línea base, el paso 2 habría sido falso y la tabla
no existiría.** El defecto descrito en
[`POWERBI_POWERQUERY_VALIDATION.md`](POWERBI_POWERQUERY_VALIDATION.md) §3 queda
confirmado por contraste: corregido, carga; sin corregir, no podía cargar.

**G3: PASS.**

## 4. G4 — Modelo semántico y DAX

### 4.1 Tablas (DMV `TMSCHEMA_TABLES`)

Siete, las esperadas: `_Medidas`, `Dim_Acero`, `Dim_BandaTamano`,
`Dim_TipoDefecto`, `Fact_Defecto`, `ML_Holdout`, `Param_Especificacion`. ✅

### 4.2 Relaciones (DMV `TMSCHEMA_RELATIONSHIPS`)

| FromTableID | ToTableID | FromCardinality | ToCardinality | CrossFilteringBehavior | IsActive |
|---:|---:|---:|---:|---:|---|
| 19 (`Fact_Defecto`) | 10 (`Dim_TipoDefecto`) | **2** | **1** | **1** | True |
| 19 (`Fact_Defecto`) | 13 (`Dim_Acero`) | **2** | **1** | **1** | True |
| 19 (`Fact_Defecto`) | 16 (`Dim_BandaTamano`) | **2** | **1** | **1** | True |

Lectura de los códigos TOM: `FromCardinality = 2` es *Many*,
`ToCardinality = 1` es *One*, `CrossFilteringBehavior = 1` es *OneDirection*.

| Control | Resultado |
|---|---|
| Exactamente 3 relaciones | ✅ |
| Cardinalidad **muchos a uno** en las tres | ✅ confirmado en el motor |
| Filtrado **unidireccional** en las tres | ✅ confirmado en el motor |
| Las tres activas | ✅ |

Esto sustituye la inferencia estática «por defecto, sin anulaciones» de
`POWERBI_MODEL_DAX_VALIDATION.md` §2.1 por una **lectura directa del motor**.

### 4.3 `ML_Holdout` desconectada — regla científica inalterable

`ML_Holdout` es **TableID 28**. No aparece en ninguna fila de
`TMSCHEMA_RELATIONSHIPS`, ni como origen ni como destino.

**Desktop NO autodetectó ninguna relación hacia `ML_Holdout` al cargar.** Era el
riesgo nº 1 del expediente. Queda descartado para esta sesión de carga.

Los 389 registros del holdout **no** se incorporan a los 1 941: sin ruta de
filtrado, el motor no puede propagar contexto entre ambos conjuntos. ✅

### 4.4 Las 34 medidas compilan

Cada medida se evaluó **individualmente**, para que un fallo no enmascarase los
demás. Resultado: **34 de 34 sin error.**

Las 22 originales de `_Medidas`:

| Medida | Valor en el motor |
|---|---|
| `Defectos` | 1941 |
| `COPQ MXN` | 2242600 |
| `COPQ % del Total` | 1 |
| `COPQ por Placa MXN` | 1155.3838227717672 |
| `Defectos % del Total` | 1 |
| `COPQ Acumulado %` | *(BLANK)* |
| `Media Log Area` | 2.4923888467857553 |
| `Linea Central` | 2.4923888467857553 |
| `Sigma Global` | 0.788930015464038 |
| `n Grupo` | 1941 |
| `UCL` | 2.5461102028053268 |
| `LCL` | 2.4386674907661838 |
| `Fuera de Limites` | 0 |
| `Grupos Fuera de Limites` | 7 |
| `USL px2` | 500 |
| `Cpk` | 0.087283262774056139 |
| `Semaforo Cpk Color` | `#C62828` |
| `Semaforo Cpk Texto` | `No capaz` |
| `% Fuera de USL` | 0.30087583719732097 |
| `Accion Recomendada` | `Contención (ISO 8.7) + causa raíz (ISO 10.2)` |
| `Defectos Grandes` | 289 |
| `Texto ISO 10.2` | `ISO 9001:2015 · 10.2 No conformidad y acción correctiva…` |

`COPQ Acumulado %` devuelve BLANK sin contexto de visual: es una medida de total
acumulado y ese es su comportamiento correcto fuera de una matriz ordenada. **No
es un error de compilación** — evaluó sin excepción.

Las 12 de `ML_Holdout`: valores en el apartado 5.

**G4: PASS.**

## 5. G6 — Reconciliación científica contra el motor

### 5.1 Indicadores obligatorios

| Indicador | Obligatorio | Motor | Diferencia | Resultado |
|---|---:|---:|---:|---|
| Holdout (`ML Rows`) | 389 | **389** | 0 | ✅ |
| Aciertos (`ML Correct`) | 307 | **307** | 0 | ✅ |
| Errores (`ML Errors`) | 82 | **82** | 0 | ✅ |
| Revisión candidata (`ML Review Rows`) | 261 | **261** | 0 | ✅ |
| Exactitud (`Observed Accuracy`) | 0.7892030848329049 | 0.78920308483290491 | **0** | ✅ |
| Macro-F1 | 0.8146728101764369 | 0.81467281017643689 | **0** | ✅ |
| Balanced accuracy | 0.8048726799979933 | 0.80487267999799328 | **0** | ✅ |
| `Candidate Review Rate` | 0.6709511568123393 | 0.6709511568123393 | **0** | ✅ |

### 5.2 La tolerancia `1e-12`, calculada por el propio motor

Para que ningún formateo del cliente pudiera ocultar una diferencia, se pidió al
motor que calculase él mismo el valor absoluto de la resta contra los literales
congelados:

```
difMacroF1     0
difBalanced    0
difAccuracy    0
difReview      0
igualMacroF1   EXACTO
igualBalanced  EXACTO
```

Las cuatro diferencias son **exactamente 0**, y la comparación de igualdad en DAX
devuelve `EXACTO`. Muy por debajo de la tolerancia `1e-12` exigida.

Los valores a precisión completa (`0.81467281017643689`,
`0.80487267999799328`) son la representación de ida y vuelta de los mismos
`double` que los literales de la orden; no son valores distintos.

### 5.3 Casos aceptados y errores capturados

| Indicador | Obligatorio | Motor | Resultado |
|---|---:|---:|---|
| Casos aceptados (`HIGH_CONFIDENCE`) | 128 | **128** | ✅ |
| `REVIEW_REQUIRED` | 173 | **173** | ✅ |
| `LOW_CONFIDENCE` | 88 | **88** | ✅ |

173 + 88 = 261 ✅ · 128 + 261 = 389 ✅

### 5.4 Comprobaciones por segmento

| Segmento | Registros | Aciertos | Revisiones | Resultado |
|---|---:|---:|---:|---|
| A300 (exigido 156 / 121 / 122) | **156** | **121** | **122** | ✅ |
| A400 (exigido 233 / 186 / 139) | **233** | **186** | **139** | ✅ |
| Pastry (exigido 32 / 20 / 29) | **32** | **20** | **29** | ✅ |

156 + 233 = 389 ✅

### 5.5 Por clase real, contra la evidencia congelada

| Clase | Registros | Aciertos | Errores (esperado) | Revisiones |
|---|---:|---:|---:|---:|
| Bumps | 81 | 55 | **26** (26) ✅ | 71 |
| Dirtiness | 11 | 10 | **1** (1) ✅ | 5 |
| K_Scatch | 78 | 71 | **7** (7) ✅ | 18 |
| Other_Faults | 135 | 106 | **29** (29) ✅ | 114 |
| Pastry | 32 | 20 | **12** (12) ✅ | 29 |
| Stains | 14 | 12 | **2** (2) ✅ | 5 |
| Z_Scratch | 38 | 33 | **5** (5) ✅ | 19 |
| **Total** | **389** | **307** | **82** | **261** |

Los siete soportes y los siete recuentos de error coinciden exactamente con
`reports/ml/integration/reconciliation_expected.json`. ✅

### 5.6 Confusión y caso de alta confianza

| Control | Obligatorio | Motor | Resultado |
|---|---|---|---|
| Bumps → Other_Faults | 21 | **21** | ✅ |

`row_id = 1277`, leído del motor:

| Atributo | Obligatorio | Motor | Resultado |
|---|---|---|---|
| `actual_defect` | `Other_Faults` | `Other_Faults` | ✅ |
| `predicted_defect` | `K_Scatch` | `K_Scatch` | ✅ |
| `confidence` | 1.0 | 1 | ✅ |
| `review_status` | `HIGH_CONFIDENCE` | `HIGH_CONFIDENCE` | ✅ |
| `correct_prediction` | 0 | 0 | ✅ |
| `review_required` | 0 | 0 | ✅ |

### 5.7 Inmunidad de las métricas finales al contexto de filtro

Con `steel_type = "A300"` aplicado por `CALCULATETABLE`:

| Medida | Sin filtro | Con A300 | Comportamiento |
|---|---:|---:|---|
| `Final Macro-F1 (389)` | 0.81467281017643689 | **0.81467281017643689** | **no cambia** ✅ |
| `ML Rows` | 389 | **156** | cambia ✅ |

Es exactamente el requisito de §8 de la orden: las tarjetas de métrica final
conservan las métricas globales del holdout, y las medidas analíticas por
segmentos responden a sus filtros. **Verificado en el motor, no deducido.**

**G6: PASS.**

## 6. Lo que esta evidencia NO acredita

Hay que ser preciso sobre el límite:

| No acreditado | Por qué |
|---|---|
| **G5 — renderización de las cinco páginas** | Los visuales viven en la capa de informe (`.Report`), **no** en el modelo semántico. El motor no sabe nada del lienzo. No he visto la pantalla |
| Legibilidad, visuales recortados o en blanco | ídem |
| Interacción real de los segmentadores en el lienzo | se demostró la **semántica** de filtrado en DAX, no el clic en el visual |
| Avisos en la interfaz de Desktop | una barra amarilla de «cambios pendientes» o un diálogo no es visible por esta vía |
| Drillthrough de `Exploracion`, tooltip de `Tooltip Pareto` | comportamiento de la capa de informe |
| **G7 — el PBIX** | exige **Archivo → Guardar como**, una acción de la GUI |

La orden es explícita en §9: «no se aceptará una inspección JSON como sustituto
de una prueba en Desktop». Esta evidencia es mejor que una inspección JSON para
el modelo, pero **no cubre el lienzo**. G5 sigue abierto.

## 7. Advertencia sobre la persistencia

Todo lo anterior describe el estado del modelo **en memoria**. Desktop no ha
guardado nada aún. Al guardar, puede reescribir archivos del PBIP (anotación
`PBI_QueryOrder`, `displayName` de `.platform`, `lineageTag`, `diagramLayout.json`)
y entonces `test_previous_powerbi_preserved` **fallará a propósito**. Ese diff
debe clasificarse, no suprimirse. Ver
[`POWERBI_PBIP_PBIX_INTEGRITY.md`](POWERBI_PBIP_PBIX_INTEGRITY.md) §3.7.

## 8. El árbol de trabajo no se modificó

Tras abrir Desktop y ejecutar las tres consultas:

```
git status --porcelain
?? docs/production/evidence/powerbi_live_engine_transcript.txt
?? docs/production/evidence/query_all_measures.ps1
?? docs/production/evidence/query_live_model.ps1
?? docs/production/evidence/query_precision.ps1
```

Las únicas entradas son los archivos de evidencia que PRODUCCIÓN acaba de
escribir. **Ningún archivo del proyecto fue modificado.** `.pbi/` sigue
conteniendo sólo `editorSettings.json`: no hay `cache.abf` ni
`localSettings.json`.

## 9. Estado de los gates tras esta evidencia

| Gate | Antes | Ahora |
|---|---|---|
| G0 Línea base | ✅ | ✅ |
| G1 Nombres y dependencias | ✅ | ✅ |
| G2 PBIP abre sin errores | ⛔ | ✅ **PASS** |
| G3 Power Query actualiza | ⛔ | ✅ **PASS** |
| G4 Modelo semántico y DAX | ⛔ | ✅ **PASS** |
| G5 Cinco páginas funcionales | ⛔ | ⛔ **sigue abierto** |
| G6 Reconciliación científica | ⛔ | ✅ **PASS** |
| G7 PBIX generado y reabierto | ⛔ | ⛔ **sigue abierto** |
| G8 Pruebas y hashes | ✅ pruebas | ✅ pruebas · ⛔ hash PBIX |

Estado oficial: **`DESKTOP_VALIDATED` para la capa de modelo**;
`READY_FOR_DESKTOP_VALIDATION` para la capa de informe (G5) y el PBIX (G7).

No se promueve a `PBIX_GENERATED_AND_REOPENED`. No sustituye la aceptación OWNER.
Las incidencias #1 y #2 permanecen **OPEN**: #1 requiere además G5, y #2 requiere
un PBIX que todavía no existe.

## 10. Reproducción

Con el PBIP abierto en Desktop:

```powershell
# 1. Localizar el puerto del motor (el archivo esta en UTF-16)
$ws = "$env:LOCALAPPDATA\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces"
Get-ChildItem -LiteralPath $ws -Recurse -Filter msmdsrv.port.txt |
  Sort-Object LastWriteTime -Descending |
  ForEach-Object { (Get-Content -LiteralPath $_.FullName -Raw).Trim() }

# 2. Confirmar que ese puerto pertenece al Desktop correcto
Get-NetTCPConnection -LocalPort <puerto> -State Listen | Select-Object OwningProcess
Get-CimInstance Win32_Process -Filter "Name='msmdsrv.exe'" | Select-Object ProcessId,ParentProcessId

# 3. Consultar (Windows PowerShell 5.1: LoadFrom sondea el directorio hermano)
$ps = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
& $ps -NoProfile -ExecutionPolicy Bypass -File docs\production\evidence\query_live_model.ps1   -Port <puerto>
& $ps -NoProfile -ExecutionPolicy Bypass -File docs\production\evidence\query_precision.ps1    -Port <puerto>
& $ps -NoProfile -ExecutionPolicy Bypass -File docs\production\evidence\query_all_measures.ps1 -Port <puerto>
```

Notas de implementación, por si hay que repetirlo:

- El ensamblado es `Microsoft.PowerBI.AdomdClient.dll` pero su namespace es
  `Microsoft.AnalysisServices.AdomdClient`; los dos nombres no coinciden.
- Hay que ejecutarlo bajo **Windows PowerShell 5.1**. En `pwsh` (.NET 8) el
  cargador no sondea el directorio del ensamblado, y un manejador
  `AssemblyResolve` que invoque cmdlets se recursa a sí mismo hasta desbordar la
  pila.
- Los `double` se imprimen con formato `R` para no perder dígitos.
