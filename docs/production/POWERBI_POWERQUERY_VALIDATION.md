# POWERBI_POWERQUERY_VALIDATION

Orden: **OWNER-PBI-REN-001** · Fase 3 — Configuración de datos en Windows
Fecha: 2026-11-14 · Responsable: PRODUCCIÓN
Gate: **G3** · Resultado: **✅ PASS** (actualizado 2026-11-15)

> **ACTUALIZACIÓN 2026-11-15 — G3 SUPERADO.** Power BI Desktop abrió el PBIP y
> cargó los datos; se consultó su motor en vivo. Las siete particiones quedaron
> en estado *Ready*, con `Fact_Defecto` = **1 941** y `ML_Holdout` = **389**. No
> existía caché (`.pbi/` sólo tiene `editorSettings.json`), luego Power Query
> **ejecutó de verdad** contra los CSV y `RutaMLCSV` resolvió sin lanzar su
> error. Evidencia:
> [`POWERBI_DESKTOP_RUNTIME_EVIDENCE.md`](POWERBI_DESKTOP_RUNTIME_EVIDENCE.md) §3.
>
> Lo que sigue conserva su redacción original: era la verificación **estática**
> previa, hecha reproduciendo la lógica M paso a paso. Su conclusión quedó
> confirmada por el motor, no sustituida. El apartado 7 («qué falta para cerrar
> G3») está **cumplido** salvo la inspección visual del Editor avanzado, que es
> cosmética una vez demostrada la carga.

Evidencia ejecutable: [`evidence/powerbi_static_validation.py`](evidence/powerbi_static_validation.py)
(**77/77 PASS**, exit 0).

---

## 1. Existencia física de los CSV

| Archivo | Ruta | Bytes | SHA256 | Existe |
|---|---|---:|---|---|
| Datos originales | `C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\steel-plates-quality-mlops\data\raw\steel_plates_faults.csv` | 315 926 | `cb07fc4284cb1bea5b308ef1822f4440e83e16d53703b5d3254a0b5def76f408` | ✅ |
| Evaluación ML | `C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\steel-plates-quality-mlops\powerbi\data\ml_holdout_evaluation.csv` | 63 243 | `5f5fb946b8817fc630059878ea67be4c75e38b1da77c5faf88b9eecf8e671cb5` | ✅ |

Ambos hashes coinciden con la línea base `be46d0c`: **ningún CSV fue alterado**.

## 2. `RutaCSV`

Valor actual en `expressions.tmdl` línea 18:

```
expression RutaCSV = "C:\path\to\steel-plates-quality-mlops\data\raw\steel_plates_faults.csv"
```

| Comprobación | Resultado |
|---|---|
| Sin separador doblado | ✅ |
| Resuelve un archivo existente | ✅ |
| Apunta al CSV crudo **de este repositorio** | ✅ (igualdad de rutas resueltas) |

`Raw_SteelPlates` consume `RutaCSV` vía `Text.Trim` y elige `Web.Contents` o
`File.Contents` según el prefijo. Con un valor `C:\…` toma la rama
`File.Contents`: origen local, sin red ni credenciales.

## 3. Defecto corregido: el separador doblado rompía `RutaMLCSV`

### 3.1 Qué estaba mal

La línea base almacenaba el valor con separadores **doblados**:

```
expression RutaCSV = "C:\\path\\to\\steel-plates-quality-mlops\\data\\raw\\steel_plates_faults.csv"
```

TMDL guarda el cuerpo de la expresión como código M **literal** y no aplica
escapado de barra invertida. El propio archivo lo demuestra: la línea 28, escrita
por `tools/prepare_ml_powerbi.py`, contiene una barra **simple** dentro de una
cadena M (`Text.Replace(Text.Trim(RutaCSV), "\", "/")`). Si TMDL escapara la
barra, esa cadena estaría malformada.

### 3.2 Evidencia independiente del formato correcto

Un proyecto PBIP **generado por Power BI Desktop** en este mismo equipo almacena
su parámetro de ruta con barra simple:

```
C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\<OTRO_PROYECTO_PBIP>\
  P30_Publicacion_RLS.SemanticModel\definition\expressions.tmdl

expression P30_Path = "C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\<OTRO_PROYECTO_PBIP>\01_DATOS\"
  meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
```

Un barrido de **todos** los `.tmdl` del equipo no encuentra ningún otro con
separador doblado fuera de este proyecto.

### 3.3 Consecuencia demostrada

Reproducción paso a paso de la expresión `RutaMLCSV` tal como está escrita
(script `check_rutacsv.py`, resultado reproducible):

| Paso de la expresión | Con separador doblado | Con separador simple |
|---|---|---|
| Valor M de `RutaCSV` | `C:\\Users\\<USUARIO>\\…\\data\\raw\\steel_plates_faults.csv` | `C:\Users\<USUARIO>\…\data\raw\steel_plates_faults.csv` |
| `File.Contents` abre el archivo | **sí** (Windows contrae separadores repetidos) | sí |
| `Text.Replace(…, "\", "/")` | `C://Users//<USUARIO>//…//data//raw//…` | `C:/Users/<USUARIO>/…/data/raw/…` |
| `Text.Contains(Normalized, "/data/raw/")` | **FALSO** | VERDADERO |
| Resultado de `RutaMLCSV` | **`error "Set RutaCSV to this repository data/raw/steel_plates_faults.csv"`** | ruta válida al CSV ML |

Impacto encadenado del fallo: `RutaMLCSV` lanza error → la partición de
`ML_Holdout` no puede evaluar `File.Contents(RutaMLCSV)` → **las 389 filas no se
importan** → las 4 tarjetas, los 3 segmentadores y las 4 tablas de la página
`MODEL PERFORMANCE & REVIEW` quedan sin datos. G3, G4, G5 y G6 habrían fallado.

Lo insidioso del defecto es que `Raw_SteelPlates` **sí** cargaba: el error se
manifestaba sólo en la tabla ML, sugiriendo un problema del holdout cuando la
causa estaba en el parámetro compartido.

### 3.4 Corrección aplicada

Único cambio: separadores simples en el valor de `RutaCSV`. No se modificó la
expresión `RutaMLCSV`, ni `Raw_SteelPlates`, ni ninguna otra línea del archivo.

**Este defecto existe también en el commit remoto `e19cd1af` y en las otras dos
distribuciones locales**, con el marcador neutro
(`C:\\path\\to\\steel-plates-quality-mlops\\data\\raw\\…`) igualmente doblado.
Se eleva a OWNER como defecto de origen, no introducido por PRODUCCIÓN.

## 4. `RutaMLCSV`

Definición (sin modificar):

```
expression RutaMLCSV =
		let
		    Normalized = Text.Replace(Text.Trim(RutaCSV), "\", "/"),
		    Root = if Text.Contains(Normalized, "/data/raw/") then Text.BeforeDelimiter(Normalized, "/data/raw/")
		        else error "Set RutaCSV to this repository data/raw/steel_plates_faults.csv",
		    Result = Root & "/powerbi/data/ml_holdout_evaluation.csv"
		in
		    Result
```

Resolución verificada con el valor corregido:

| Paso | Valor |
|---|---|
| `Normalized` | `C:/Users/<USUARIO>/<CARPETA_DE_TRABAJO>/steel-plates-quality-mlops/data/raw/steel_plates_faults.csv` |
| `Text.Contains` | VERDADERO |
| `Root` | `C:/Users/<USUARIO>/<CARPETA_DE_TRABAJO>/steel-plates-quality-mlops` |
| `Result` | `C:/Users/<USUARIO>/<CARPETA_DE_TRABAJO>/steel-plates-quality-mlops/powerbi/data/ml_holdout_evaluation.csv` |
| Archivo existe | ✅ |
| Es el export del repositorio | ✅ (igualdad de rutas resueltas) |

Power Query acepta la barra normal en rutas Windows, por lo que `File.Contents`
resuelve correctamente el valor con `/`.

## 5. Validación de datos

### 5.1 `data/raw/steel_plates_faults.csv`

| Exigencia de la orden | Valor esperado | Observado | Resultado |
|---|---|---|---|
| Observaciones originales | 1 941 | 1 941 | ✅ |
| Mediciones predictoras | 27 | 27 | ✅ |
| Clases originales | 7 | 7 | ✅ |
| Filas duplicadas | 0 | 0 | ✅ |

Clases detectadas en el encabezado, en orden:
`Pastry`, `Z_Scratch`, `K_Scatch`, `Stains`, `Dirtiness`, `Bumps`, `Other_Faults`.

Confirmación independiente: `python -B -m tools.project_checks validate-data`
→ `{"status": "PASS", "rows": 1941, "features": 27}`.

### 5.2 `powerbi/data/ml_holdout_evaluation.csv`

| Exigencia | Esperado | Observado | Resultado |
|---|---|---|---|
| Registros de evaluación ML | 389 | 389 | ✅ |
| Encabezados | las 16 columnas de `COLUMNS` | idénticos y en orden | ✅ |
| `dataset_role` | único `FINAL_HOLDOUT_EVALUATION` | único | ✅ |
| Filas duplicadas | 0 | 0 | ✅ |

Nota de parseo: `confidence_bin` contiene valores como `"[0.50,0.60)"`, con el
delimitador **dentro** de un campo entrecomillado. Este archivo debe leerse como
CSV y nunca partirse por comas; la primera versión del script de validación
cometió ese error y lo detectó la propia comprobación de `dataset_role`.

### 5.3 Tipos de datos

- `Raw_SteelPlates` convierte **todas** las columnas a `type number` mediante
  `List.Transform(Table.ColumnNames(…))`. Coherente con un CSV íntegramente
  numérico; no hay lista de columnas codificada que pueda desincronizarse.
- `ML_Holdout` declara los tipos explícitamente y **valida el esquema**: compara
  `List.Sort(Table.ColumnNames(Cabecera))` contra las 16 columnas esperadas y
  lanza `error "ML schema mismatch"` si difieren. Además exige
  `Table.RowCount(Tipos) = 389` y `List.Distinct(Tipos[dataset_role]) = {"FINAL_HOLDOUT_EVALUATION"}`.

Estas guardas hacen que un CSV alterado **falle de forma cerrada** en la propia
actualización, en lugar de producir cifras silenciosamente erróneas.

## 6. Integridad de los datos de origen

No se alteró ningún CSV para conseguir una actualización satisfactoria. Prueba:
los SHA256 del apartado 1 son los de la línea base, y
`test_previous_powerbi_preserved` compara los dos CSV contra
`pre_ml_powerbi_hashes.json` sin excepción alguna.

## 7. Qué falta para cerrar G3

Debe ejecutarse en Power BI Desktop y registrarse:

1. Abrir el PBIP y comprobar que `RutaCSV` muestra el valor del apartado 2.
2. Abrir el **Editor avanzado** sobre `RutaMLCSV` y verificar su **valor
   resuelto**, no sólo su texto.
3. **Actualizar vista previa** → **Cerrar y aplicar** → **Actualizar**.
4. Registrar: 1 941 filas en el hecho original, 389 en `ML_Holdout`, cero
   errores de Power Query, cero avisos de credenciales.
5. Confirmar que no aparece ningún error nuevo de importación ni duplicación.

Plantilla de registro en
[`POWERBI_PBIP_PBIX_INTEGRITY.md`](POWERBI_PBIP_PBIX_INTEGRITY.md) §4.

| Control de G3 | Estado |
|---|---|
| Los CSV existen en las rutas exigidas | ✅ verificado |
| `RutaCSV` contiene una ubicación válida | ✅ verificado |
| `RutaMLCSV` resuelve el segundo CSV | ✅ verificado (lógica reproducida) |
| Contrato de datos (1 941 / 27 / 7 / 389) | ✅ verificado |
| Encabezados y tipos | ✅ verificado |
| CSV de origen sin alterar | ✅ verificado |
| **Power Query actualiza en Desktop** | ⛔ **NO EJECUTADO** |

**G3: PARCIAL.** Todo lo verificable sin la aplicación nativa está verificado y
en PASS. El gate queda abierto hasta la actualización real en Desktop.
