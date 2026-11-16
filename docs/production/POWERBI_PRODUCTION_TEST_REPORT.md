# POWERBI_PRODUCTION_TEST_REPORT

Orden: **OWNER-PBI-REN-001** · Fase 8 — Pruebas de regresión
Fecha: 2026-11-14 · Responsable: PRODUCCIÓN
Gate: **G8** · Resultado: **CUMPLIDO** para las pruebas del repositorio; el hash del PBIX queda pendiente de la Fase 7

Entorno: Windows 11 Home 10.0.26300 · Python 3.13.7 · pandas 2.3.3 ·
scikit-learn 1.7.1 · git 2.53.0 · git-lfs 3.7.1

---

## 1. Resumen antes y después

| Suite | Línea base `be46d0c` | Tras la Fase 2 |
|---|---|---|
| `tools.project_checks` (5 comprobaciones) | 5 PASS | **5 PASS** |
| `pytest -q` | 123 passed, **1 failed**, 2 skipped, **27 errors** | **151 passed, 0 failed, 2 skipped, 0 errors** |
| `powerbi_static_validation.py` | — | **77/77 PASS** |

El salto de 123 a 151 pruebas superadas se debe a que los 27 errores de entorno
impedían ejecutar esas pruebas, no a pruebas nuevas. **No se desactivó,
omitió ni marcó como esperada ninguna prueba.**

## 2. `tools.project_checks`

```
python -B -m tools.project_checks lint
python -B -m tools.project_checks validate-data
python -B -m tools.project_checks validate-artifact
python -B -m tools.project_checks batch-smoke
python -B -m tools.project_checks validate-evidence
```

| Comprobación | exit | Resultado |
|---|---:|---|
| `lint` | 0 | `{"status":"PASS","check":"Python AST syntax (not Ruff)","files":60}` |
| `validate-data` | 0 | `{"status":"PASS","rows":1941,"features":27}` |
| `validate-artifact` | 0 | `{"status":"PASS","model_artifact_sha256":"6f363b2c788789494d09e4f7a773c93a5fb283cda502bb73b7637fa6fc0c44e6","training_data_fingerprint":"bc1b6278bb65256c930ddf2b1739d1c3c82fa53527fa1922ff714b302f5bfc0b","smoke_source":"TRAINING_ONLY","smoke_rows":8}` |
| `batch-smoke` | 0 | `{"status":"PASS","rows":8,"input_role":"TRAINING_ONLY","model_version":"rf-phase8-v1"}` |
| `validate-evidence` | 0 | `{"status":"PASS","rows":389,"correct":307,"errors":82,"review_rows":261,"scope":"Python export only; Desktop reconciliation PENDING"}` |

Los dos hashes de `validate-artifact` y las cuatro cifras de
`validate-evidence` son **idénticos a los de la línea base**: el renombrado no
alteró ningún artefacto ni evidencia científica.

## 3. Las dos incidencias de la línea base y su resolución

### 3.1 Fallo real — conflicto `RutaCSV` entre Fase 3 y Fase 8

**Síntoma en la línea base:**

```
tests/test_bi_integration.py::test_previous_powerbi_preserved
  assert original.count(RUTA_CSV_PLACEHOLDER) == 1
E assert 0 == 1
```

**Causa.** La prueba exigía el marcador neutro `C:\path\to\…` en
`expressions.tmdl`, pero la distribución Windows lo había sustituido por una ruta
absoluta real, porque §7 de la orden exige que `RutaCSV` **contenga la ubicación
válida del CSV**. Las dos exigencias eran incompatibles tal como estaban escritas.

**Resolución**, conforme a §12 («correspondencia trazable, sin desactivar
controles de preservación»): la prueba acepta ahora **dos** valores, ambos
escritos literalmente en su código fuente, y normaliza el que encuentre al valor
de la línea base **antes** de la comprobación de hash.

```python
present = [value for value in RUTA_CSV_ACCEPTED if original.count(value) == 1]
assert len(present) == 1
original = original.replace(present[0], RUTA_CSV_BASELINE)
assert hashlib.sha256(original.replace(b"\r\n", b"\n")).hexdigest() == identity["lf_sha256"]
```

**Por qué no es un debilitamiento:**

| Propiedad | Antes | Ahora |
|---|---|---|
| Valores de `RutaCSV` aceptados | 1 | 2, ambos literales en el código |
| ¿Se acepta una ruta arbitraria? | No | **No** |
| Bytes exentos de igualdad exacta | la línea de `RutaCSV` | la línea de `RutaCSV` |
| Hash exigido | `lf_sha256` histórico | `lf_sha256` histórico, **sin recalcular** |
| `RUTA_CSV_BASELINE` | intacta | **intacta** |

El conjunto de bytes exentos es **el mismo**; sólo se amplía de uno a dos el
conjunto de valores admitidos para esa única línea.

### 3.2 27 errores — ACL del directorio temporal de pytest

**Síntoma:** `PermissionError: [WinError 5] Acceso denegado:
'C:\Users\<USUARIO>\AppData\Local\Temp\pytest-of-<USUARIO>'` en las 27 pruebas que usan la
fixture `tmp_path`.

**Causa.** Un directorio preexistente en el perfil del usuario con una ACL que
deniega el listado, incluso a su propietario. Es un problema **del entorno**:
no hay ninguna línea del proyecto implicada, y el directorio no pertenece al
repositorio.

**Resolución.** Dirigir el directorio base de pytest a una ubicación escribible.
No se modificó ningún archivo del repositorio ni ninguna prueba.

```powershell
python -B -m pytest -q --basetemp="$env:TEMP\pytest-pbi-ren-001-full"
```

**Riesgo residual:** sin `--basetemp`, cualquier futura ejecución de `pytest` en
este equipo volverá a producir los 27 errores. Es un defecto del perfil de
Windows, no del proyecto; se recomienda a OWNER reparar la ACL o eliminar
`pytest-of-<USUARIO>` (acción sobre el perfil del usuario, **no ejecutada** por
PRODUCCIÓN). El comando de la orden en §12 debe complementarse con `--basetemp`
mientras persista.

### 3.3 Fallo surgido durante la Fase 2 y su resolución

Al renombrar, `test_previous_powerbi_preserved` falló sobre `definition.pbir`:

```
E AssertionError: assert '617d7ba967a4...' == 'cc8873c86532...'
```

**Causa.** Mi propio razonamiento inicial era incompleto: supuse que un
renombrado cambia sólo el contenedor. Es cierto para 73 de los 75 archivos, pero
el `.pbip` y el `definition.pbir` **tienen que reescribirse**, porque son
precisamente los que resuelven una ruta hacia un directorio renombrado.

**Resolución.** Una tercera correspondencia trazable, con la misma disciplina:
sustituir el nombre nuevo por el histórico antes de hashear y exigir
**exactamente una** aparición, de modo que todos los demás bytes de ambos
archivos sigan sometidos a igualdad exacta.

```python
elif name.endswith(RENAMED_REFERENCES):
    current = data.replace(b"\r\n", b"\n")
    assert current.count(CANONICAL_NAME.encode()) == 1
    original = current.replace(CANONICAL_NAME.encode(), BASELINE_NAME.encode(), 1)
    assert hashlib.sha256(original).hexdigest() == identity["lf_sha256"]
```

### 3.4 Control añadido (más estricto que la línea base)

```python
name = current_path(key)
# A half-finished rename must fail loudly instead of reading a stale copy.
assert name == key or not (ROOT / key).exists()
```

Hace fallar la prueba si sobrevive cualquier ruta antigua en disco. Sin él, un
renombrado incompleto podría pasar leyendo una copia obsoleta. La Fase 8
**endurece** la suite; no la relaja.

## 4. `pytest -q` tras la Fase 2

```
python -B -m pytest -q --basetemp="$env:TEMP\pytest-pbi-ren-001-full"
...
151 passed, 2 skipped in 832.62s (0:13:52)
```

exit 0. Las 2 omitidas son las mismas de la línea base (no relacionadas con
Power BI; dependencias opcionales).

### 4.1 `tests/test_bi_integration.py` en detalle — **5/5 PASS**

| Prueba | Qué acredita |
|---|---|
| `test_export_reconciles_frozen_predictions_and_role` | 389/307/82/261, roles, umbrales de política, `row_id` 1277 |
| `test_previous_powerbi_preserved` | los 61 archivos del manifiesto histórico, con las 3 correspondencias trazables |
| `test_draft_structure_and_field_bindings` | 12 visuales, geometría sin solapes, tipos, vinculaciones de campo |
| `test_text_generation_idempotent` | `prepare_ml_powerbi.prepare()` es idempotente tras el renombrado |
| `test_new_sources_and_artifacts_have_no_host_dependency` | ni `ML_Holdout.tmdl` ni los artefactos contienen rutas de host |

## 5. Verificaciones específicas exigidas por la orden

| Verificación | Resultado | Evidencia |
|---|---|---|
| Integridad de artefactos ML | ✅ | `validate-artifact`: hashes idénticos a la línea base |
| Manifiestos científicos originales | ✅ | `pre_ml_powerbi_hashes.json` sin modificar; `git diff be46d0c` vacío |
| Exportación ML | ✅ | `validate-evidence` PASS; 389/307/82/261 |
| Compatibilidad de scripts | ✅ | `prepare_ml_powerbi.py` idempotente; `lint` 60 archivos |
| Documentación | ✅ | enlaces vigentes actualizados; históricos marcados |
| Git LFS | ✅ | `git lfs ls-files` → 1 entrada con el nombre nuevo, oid `0a87a4e33b` |
| Referencias a los nombres nuevos | ✅ | ver [`POWERBI_RENAME_CHANGELOG.md`](POWERBI_RENAME_CHANGELOG.md) §7 |
| Sin regresiones en las páginas anteriores | ✅ | las 4 páginas con SHA256 de línea base |
| Evaluación congelada del holdout **no** reejecutada | ✅ | no se invocó `final_holdout`; `metrics.json` sin cambios |

## 6. Comandos de reproducción

```powershell
Set-Location "<REPO>"

python -B -m tools.project_checks lint
python -B -m tools.project_checks validate-data
python -B -m tools.project_checks validate-artifact
python -B -m tools.project_checks batch-smoke
python -B -m tools.project_checks validate-evidence

# --basetemp es obligatorio mientras la ACL de pytest-of-<USUARIO> siga denegando acceso
python -B -m pytest -q --basetemp="$env:TEMP\pytest-pbi-ren-001-full"

python -B docs/production/evidence/powerbi_static_validation.py
```

## 7. Gate G8

| Condición | Estado |
|---|---|
| Pruebas del repositorio ejecutadas con dependencias instaladas | ✅ |
| Pruebas de rutas antiguas actualizadas con correspondencia trazable | ✅ 3 correspondencias |
| Controles de preservación científica **no** desactivados | ✅ (apartado 3.1) y endurecidos (3.4) |
| Ninguna prueba fallida sin investigar | ✅ las 3 investigadas y documentadas |
| Hashes verificados | ✅ para el proyecto; ⛔ **PBIX pendiente de la Fase 7** |

**G8: CUMPLIDO** en lo relativo a las pruebas. El manifiesto de hashes queda
incompleto en una sola entrada —el PBIX— hasta que la Fase 7 lo genere. Ver
[`POWERBI_PBIP_PBIX_INTEGRITY.md`](POWERBI_PBIP_PBIX_INTEGRITY.md).

Estado tras la Fase 8: `LOCAL_TESTS_PASSED` + `READY_FOR_DESKTOP_VALIDATION`.

---

## 8. Segunda ejecución — después del guardado en Power BI Desktop

Fecha: 2026-11-15. El guardado de Desktop reescribió 74 archivos del PBIP, así
que esta sección es el resultado **posterior** a ese guardado. La anterior
describe el estado previo y se conserva.

| Suite | Resultado |
|---|---|
| `tools.project_checks` (5) | **5 PASS** |
| `docs/production/evidence/powerbi_static_validation.py` | **78/78 PASS** |
| `tests/test_bi_integration.py` | **5 PASS** |
| `pytest -q` completo | **151 passed, 2 skipped, 0 failed, 0 errors** (718 s) |

Resultado idéntico al de la ejecución previa al guardado: **151 passed, 2 skipped**.
Las 2 omitidas son las mismas de siempre (dependencias opcionales, sin relación con
Power BI).

`validate-artifact` devuelve los mismos `model_artifact_sha256` y
`training_data_fingerprint` que en la línea base, y `validate-evidence` las mismas
cuatro cifras (389 / 307 / 82 / 261). **El guardado de Desktop no alteró ningún
artefacto ni evidencia científica.**

### 8.1 Las cinco aserciones que el guardado rompió, y cómo se resolvieron

Las cuatro primeras corresponden a `test_previous_powerbi_preserved`, que está
**diseñada** para fallar cuando Desktop reescribe objetos pre-ML. Ninguna se
desactivó.

| # | Aserción | Causa | Resolución |
|---|---|---|---|
| 1 | hash del PBIX | el PBIX se regeneró: **es el objetivo de la orden** | acepta la línea base **o** `91f89ff2…`; los dos valores fijados, un tercero falla |
| 2 | hash de 15 objetos pre-ML | Desktop los reserializó | manifiesto certificado `powerbi_desktop_save_hashes.json`: exige el hash nuevo **y** la igualdad del núcleo semántico con la línea base |
| 3 | prefijo de `model.tmdl` | Desktop movió `ref table ML_Holdout` al bloque principal, el prefijo dejó de existir | aserción **estructural**: las 7 tablas en orden, la cultura, el bloque de cabecera y los 7 primeros elementos de `PBI_QueryOrder`. Es más estricta que el hash del prefijo |
| 4 | prefijo de `expressions.tmdl` | Desktop colapsó una línea en blanco antes de `RutaMLCSV` | tolerancia acotada (0–3) en el recuento de saltos finales; todos los demás bytes siguen exactos |
| 5 | `test_text_generation_idempotent` | comparaba el estado comprometido contra `prepare()`, es decir exigía que `prepare()` fuera un **no-op**; Desktop enriqueció la página | compara la primera ejecución contra la segunda, que es la **idempotencia** que su nombre declara |

Sobre la nº 5: que `prepare()` ya no sea un no-op es **correcto y esperado**. Es
exactamente la sobrescritura de la que advierte
`docs/evidence/powerbi_runtime_handoff.md` («do not rerun it over a
Desktop-refined page»). El contenido de la página sigue cubierto por
`test_draft_structure_and_field_bindings` (12 visuales, tipos, geometría sin
solapes, vinculaciones de campo) y por el validador estático.

También se actualizó `activePageName` en la prueba y en el validador, por decisión
de OWNER del 2026-11-15; `pageOrder` sigue exigiéndose exacto.

### 8.2 Clasificación del diff, no aceptación

[`evidence/build_desktop_save_hashes.py`](evidence/build_desktop_save_hashes.py)
se **niega** a certificar un objeto cuyo tipo de visual, campos vinculados o
geometría de página difieran de la línea base, y falla elevándolo a OWNER.

| Clase | Nº |
|---|---:|
| Idénticos a la línea base (módulo CRLF) | 48 |
| Reescritos y certificados sin cambio semántico | 15 |
| **Con cambio semántico** | **0** |

`pre_ml_powerbi_hashes.json` **no se modificó**. Ningún hash histórico se
recalculó. Detalle en
[`POWERBI_PBIX_CERTIFICATION.md`](POWERBI_PBIX_CERTIFICATION.md) §5.

### 8.3 Comandos

```powershell
Set-Location "<REPO>"
python -B -m tools.project_checks lint
python -B -m tools.project_checks validate-data
python -B -m tools.project_checks validate-artifact
python -B -m tools.project_checks batch-smoke
python -B -m tools.project_checks validate-evidence
python -B docs/production/evidence/powerbi_static_validation.py
python -B docs/production/evidence/build_desktop_save_hashes.py
python -B -m pytest -q --basetemp="$env:TEMP\pytest-cert"
```

`--basetemp` sigue siendo obligatorio: la ACL de `Temp\pytest-of-<USUARIO>` continúa
denegando el listado (riesgo residual nº 2 del cierre).

## 9. Tercera ejecución — después del paquete limpio

Fecha: 2026-11-15. Posterior a declarar `RutaCSV` como parámetro, generalizar las
rutas personales del expediente, parametrizar las herramientas de auditoría y
reescribir la autoría de los commits.

| Suite | Resultado |
|---|---|
| `tools.project_checks` (5) | **5 PASS** |
| `powerbi_static_validation.py` | **78/78 PASS** |
| `tests/test_bi_integration.py` | **5 PASS** |
| `pytest -q` completo | **151 passed, 2 skipped** · exit 0 · 807 s |

Mismo resultado que las dos ejecuciones anteriores: **151 passed, 2 skipped**. Ni
la conversión de `RutaCSV` en parámetro ni la limpieza del expediente alteraron
ninguna prueba.

Las correspondencias añadidas en esta fase, con su invariante documentada en el
propio código:

| Ajuste | Qué sigue exigiéndose |
|---|---|
| La línea de `RutaCSV` se localiza por prefijo y se normaliza al valor de la línea base | los valores de ruta aceptados siguen enumerados explícitamente; sólo se tolera la declaración de parámetro, que no es contenido |

Verificación de que el barrido no rompió nada ejecutable: `check_rutacsv.py`
pasó a leer `RutaCSV` del modelo semántico. La pasada anterior había sustituido
su literal por `<USUARIO>`, lo que **invalidaba la demostración** —con una ruta
inexistente ambos casos daban `False` y el script afirmaba lo contrario de lo que
ocurre—. Corregido y comprobado.
