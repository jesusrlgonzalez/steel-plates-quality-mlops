# POWERBI_PRODUCTION_CLOSEOUT

Orden: **OWNER-PBI-REN-001** · Cierre de producción
Fecha: 2026-11-15 · Responsable: PRODUCCIÓN
Rama: `fix/powerbi-canonical-naming-pbix` · Base: `main` @ `ea40f4a`
Estado: **`PBIX_GENERATED_AND_REOPENED`** · **`READY_FOR_OWNER_REVIEW`**

**Nada se ha subido a GitHub.** No hay remoto configurado en el repositorio
local, no se ha hecho push y no se ha abierto Pull Request. Todo queda local, a
la espera de que OWNER publique lo que corresponda.

---

## 1. Gates — estado final

| Gate | Condición | Estado |
|---|---|---|
| G0 | Línea base certificada | ✅ |
| G1 | Nombres y dependencias coherentes | ✅ |
| G2 | PBIP abre sin errores | ✅ |
| G3 | Power Query actualiza correctamente | ✅ |
| G4 | Modelo semántico y DAX validados | ✅ |
| G5 | Cinco páginas funcionales | ✅ *(inspección visual por OWNER)* |
| G6 | Reconciliación científica satisfactoria | ✅ |
| G7 | PBIX generado, cerrado y reabierto | ✅ |
| G8 | Pruebas y hashes verificados | ✅ |
| G9 | Pull Request revisado | ⛔ **no abierto** — corresponde a OWNER |
| G10 | Aceptación formal OWNER | ⛔ **pendiente** |

Cada gate se evaluó por separado. G9 y G10 no son de PRODUCCIÓN.

## 2. El artefacto

| Dato | Valor |
|---|---|
| PBIX | `powerbi\artifacts\steel-plates-quality-mlops-powerbi.pbix` |
| Tamaño | **252 387 bytes** |
| **SHA256** | **`91f89ff2d8ce7605e9b54d9c2c45a6d5cf2511649498e9c70ed82abfe7d86260`** |
| Power BI Desktop | `2.156.951.0 (26.07)` |
| PBIP | `powerbi\project\steel-plates-quality-mlops-powerbi.pbip` |
| Git LFS oid | `91f89ff2…` (coincide con el SHA256) |

Certificación: [`POWERBI_PBIX_CERTIFICATION.md`](POWERBI_PBIX_CERTIFICATION.md).

## 3. Lo que se resolvió en esta sesión de cierre

| # | Hallazgo | Resolución |
|---|---|---|
| 1 | El PBIX se guardó en `artifacts\` en vez de `powerbi\artifacts\` | movido a la ruta canónica, con Desktop cerrado (el primer intento falló por bloqueo de archivo) |
| 2 | El puntero LFS apuntaba a un objeto inexistente (404) | sustituido por `91f89ff2…`, que **sí** existe en el almacén local; al hacer push el repositorio deja de estar roto |
| 3 | Desktop reescribió 74 archivos del PBIP | clasificados: 42 solo finales de línea, 15 certificados sin cambio semántico, **0 cambios semánticos** |
| 4 | `activePageName` pasó a la página ML | aceptado por OWNER; correspondencia trazable en prueba y validador |
| 5 | 5 aserciones rotas por el guardado legítimo | actualizadas con correspondencia trazable, sin desactivar controles |

## 4. Pruebas

| Suite | Resultado |
|---|---|
| `tools.project_checks` | **5/5 PASS** |
| `docs/production/evidence/powerbi_static_validation.py` | **78/78 PASS** |
| `tests/test_bi_integration.py` | **5/5 PASS** |
| `pytest -q` completo | ver §8 de [`POWERBI_PRODUCTION_TEST_REPORT.md`](POWERBI_PRODUCTION_TEST_REPORT.md) |

`validate-artifact` y `validate-evidence` devuelven los mismos hashes y las
mismas cuatro cifras (389/307/82/261) que en la línea base. **El guardado de
Desktop no alteró ningún artefacto ni evidencia científica.**

Reproducción:

```powershell
Set-Location "<REPO>"
python -B -m tools.project_checks lint
python -B -m tools.project_checks validate-data
python -B -m tools.project_checks validate-artifact
python -B -m tools.project_checks batch-smoke
python -B -m tools.project_checks validate-evidence
python -B docs/production/evidence/powerbi_static_validation.py
python -B -m pytest -q --basetemp="$env:TEMP\pytest-cert"
```

`--basetemp` sigue siendo necesario: la ACL de
`%LOCALAPPDATA%\Temp\pytest-of-<USUARIO>` deniega el listado y sin el parámetro
aparecen 27 errores ajenos al proyecto.

## 5. Qué está intacto

| Elemento | Verificación |
|---|---|
| `docs/evidence/pre_ml_powerbi_hashes.json` | sin modificar; ningún hash recalculado |
| `reports/ml/final_holdout/metrics.json` | sin modificar |
| `reports/ml/integration/reconciliation_expected.json` | sin modificar |
| `artifacts/manifest.json`, `artifacts/model/*.joblib` | sin modificar |
| `data/raw/steel_plates_faults.csv` | `cb07fc4284cb1bea…` |
| `powerbi/data/ml_holdout_evaluation.csv` | `5f5fb946b8817fc6…` |
| Las 22 medidas originales (`_Medidas.tmdl`) | solo finales de línea |
| `relationships.tmdl` | solo finales de línea; `ML_Holdout` sigue desconectada |
| `powerbi/powerquery/*.pq`, `powerbi/dax/*.dax` | sin modificar |

El modelo **no** se reentrenó. La evaluación congelada del holdout **no** se
reejecutó. Las políticas **no** se recalibraron.

## 5bis. Paquete limpio para publicación

Trabajo ejecutado el 2026-11-15 tras la certificación, para que el repositorio
pueda publicarse sin datos comprometidos.

### 5bis.1 Auditoría: qué había y qué queda

| Elemento | Antes | Ahora | Nota |
|---|---:|---:|---|
| Nombre de cuenta de Windows | 75 | **12** | las 12 son intencionadas (5bis.2) |
| Rutas fijas en scripts de evidencia | 6 | **0** | derivan la raíz de `__file__` / `$PSScriptRoot` |
| Autores distintos en los commits | 1 sintético | **1 real** | `Jesús R. L. González <285482007+jesusrlgonzalez@users.noreply.github.com>` |
| Secretos reales | **0** | **0** | los 31 avisos son referencias `${{ secrets.* }}` de Actions |
| Credenciales, tokens, contraseñas | **0** | **0** | — |
| Datos personales en los CSV | **0** | **0** | mediciones de placas y etiquetas de defecto |

Correos presentes, ambos preexistentes a este trabajo:
`285482007+jesusgonzalezmexdata-ux@users.noreply.github.com` en
`docs/PROJECT_EXECUTION_STATE.md` (un *noreply* de GitHub, público por
naturaleza), y `S@989.eSF`, que es ruido binario del `.joblib` coincidiendo con el
patrón de correo — un falso positivo.

Auditoría reproducible:

```powershell
python -B docs/production/evidence/audit_repo_leaks.py --account <nombre>
python -B docs/production/evidence/audit_pbix_leaks.py powerbi\artifacts\steel-plates-quality-mlops-powerbi.pbix
```

### 5bis.2 Las 12 apariciones que permanecen, y por qué

| Nº | Dónde | Por qué no se generaliza |
|---:|---|---|
| 6 | líneas `expression RutaCSV = "…"` en el expediente | declaran el valor que el PBIP publicado **realmente** contiene; generalizarlas haría que el documento mintiera |
| 4 | `Downloads\steel-plates-quality-bi-main` del autor original | constante de reconstrucción del hash congelado: **un solo byte distinto rompe** la verificación de integridad histórica |
| 1 | `expressions.tmdl` | es el valor funcional de `RutaCSV` |
| 1 | resto | contexto inmediato de los anteriores |

En los bloques de comandos la raíz del repositorio pasa a `<REPO>`, y el nombre
de cuenta a `<USUARIO>` en el resto. Herramienta:
[`evidence/scrub_docs.py`](evidence/scrub_docs.py), que recibe la cuenta y la raíz
por argumento y por tanto no lleva ninguna cadena personal propia.

### 5bis.3 `RutaCSV` es ahora un parámetro

```
expression RutaCSV = "…\data\raw\steel_plates_faults.csv" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
```

Mismo formato que usa un proyecto PBIP real generado por Desktop. Quien abra el
proyecto cambia la ruta en **Inicio → Transformar datos → Editar parámetros**, un
campo de texto, sin tocar código M ni el Editor avanzado.

La prueba de preservación localiza ahora la línea de `RutaCSV` por su prefijo y la
normaliza al valor de la línea base antes de hashear. Los valores de ruta
aceptados siguen enumerados explícitamente —ninguna otra ruta pasa—; lo que se
tolera es la declaración de parámetro, que no es contenido.

**Nota de desfase:** el PBIX se guardó **antes** de este cambio, así que su copia
de `RutaCSV` no lleva la declaración de parámetro. No afecta a nada: el PBIX trae
los datos en caché y abre igual. El próximo guardado desde Desktop los sincroniza.

### 5bis.4 Lo que sigue expuesto, y cómo eliminarlo

El PBIX **sí** lleva la ruta personal. Verificado contra su motor y no supuesto:
el `DataModel` está comprimido, así que buscar texto plano en el paquete no prueba
nada. Está en **un solo sitio** —la expresión `RutaCSV`— y **ninguna partición la
repite**. Script: [`evidence/query_expressions.ps1`](evidence/query_expressions.ps1).

No se puede neutralizar sin más: **Cerrar y aplicar refresca**, y con una ruta
inexistente el refresco falla y no hay guardado limpio. La ruta tiene que ser
neutra **y real**. Receta, si OWNER decide aplicarla:

1. Dejar el proyecto en una raíz sin nombre de cuenta, p. ej. `D:\steel-plates-quality-mlops`.
2. Abrir el PBIP, poner `RutaCSV` a esa raíz, **Cerrar y aplicar**, comprobar 1 941 / 389.
3. **Guardar como** PBIX. Nace sin ruta personal.
4. Recertificar: el SHA256 del PBIX **cambia** y hay que regenerar el manifiesto.

OWNER decidió el 2026-11-15 **no** hacerlo por ahora y publicar con la ruta
actual. Queda como riesgo residual nº 1.

## 6. Lo que OWNER debe decidir antes de publicar

### 6.1 `RutaCSV` contiene tu ruta personal

```
expression RutaCSV = "C:\path\to\steel-plates-quality-mlops\data\raw\steel_plates_faults.csv"
```

Es **necesario** para que el PBIP abra con datos en este equipo, e **indeseable**
en un repositorio público: expone el nombre de cuenta `<USUARIO>` y es una ruta que no
existe en otras máquinas.

| Opción | Efecto |
|---|---|
| **A — mantenerla** | el proyecto abre aquí sin tocar nada; publica la ruta |
| **B — marcador neutro antes del PR** | repositorio portátil; quien clone debe configurar `RutaCSV` antes de abrir |

Valor para la opción B (**una sola** barra invertida por separador — la forma
doblada es el defecto que se corrigió):

```
expression RutaCSV = "C:\path\to\steel-plates-quality-mlops\data\raw\steel_plates_faults.csv"
```

La prueba acepta ese valor sin ningún otro cambio. **Importante:** el PBIX ya
está generado y certificado, así que aplicar B ahora **no** invalida el PBIX —
sólo cambia el PBIP. Este es el momento adecuado para hacerlo.

### 6.2 Las dos copias no canónicas

| Ruta | Qué es |
|---|---|
| `…\STEEL_PLATES_QUALITY_MLOPS_PARA_WINDOWS\steel-plates-quality-mlops` | línea base intacta (respaldo de reversión) |
| `…\Steel_Plates_PowerBI_Lista_Para_Desktop_Local` | distribución divergente, sin renombrar ni corregir |

Conviene archivarlas o eliminarlas para no validar la equivocada en el futuro.
PRODUCCIÓN no las ha tocado.

### 6.3 Power BI Service

**No** se ha publicado nada. Antes de hacerlo hay que resolver que las fuentes
son `File.Contents` sobre `C:`, que **no** se actualizan en el Service sin una
puerta de enlace de datos local o sin migrar las fuentes a almacenamiento
accesible desde la nube. Es una autorización independiente.

## 7. Publicación en GitHub — pasos para OWNER

PRODUCCIÓN **no ejecuta** nada de esto.

### 7.1 Historia local

```
2c7ce67 … d28c790  (rama fix/powerbi-canonical-naming-pbix)
ea40f4a  Fase 0: linea base certificada
be46d0c  baseline: estado recibido sin modificar
```

El repositorio local se creó con `git init` propio, de modo que **su historia no
comparte ancestro con `origin/main` (`e19cd1af`)**. Un push directo produciría un
PR ilegible.

### 7.2 Vía recomendada: aplicar el parche sobre un clon real

```powershell
# 1. Generar el parche
Set-Location "<REPO>"
git format-patch main --stdout > "..\powerbi-canonical-naming.patch"

# 2. Clonar el repositorio de verdad, en otra carpeta
Set-Location "C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>"
git clone https://github.com/jesusrlgonzalez/steel-plates-quality-mlops.git pr-work
Set-Location pr-work
git lfs install

# 3. Rama sobre origin/main y aplicar el parche
git checkout -b fix/powerbi-canonical-naming-pbix origin/main
git am "..\powerbi-canonical-naming.patch"

# 4. El PBIX debe subir como objeto LFS
git lfs ls-files        # debe mostrar oid 91f89ff2...
git push -u origin fix/powerbi-canonical-naming-pbix
```

Si `git clone` falla al materializar el PBIX antiguo, es el objeto LFS roto
(oid `0a87a4e3…`, 404). Clonar saltando el smudge y luego aplicar el parche
resuelve el problema, porque el parche sustituye ese puntero:

```powershell
git -c filter.lfs.smudge= -c filter.lfs.process= -c filter.lfs.required=false `
    clone https://github.com/jesusrlgonzalez/steel-plates-quality-mlops.git pr-work
```

### 7.3 Contenido del Pull Request

- Renombrado canónico a `steel-plates-quality-mlops-powerbi` (75 archivos).
- Corrección del separador doblado en `RutaCSV`, que impedía cargar `ML_Holdout`.
- PBIX certificado: `91f89ff2…`, 252 387 B, Desktop `2.156.951.0 (26.07)`.
- Reparación del objeto LFS roto.
- Clasificación del diff de Desktop: 0 cambios semánticos.
- Resultados de regresión: 5/5 · 78/78 · 5/5.
- Riesgos residuales y procedimiento de reversión.

### 7.4 Las incidencias #1 y #2

| # | Título | Qué aporta este trabajo |
|---|---|---|
| 1 | Validate the Power BI layer in Power BI Desktop (runtime gate) | **satisfecha**: G2–G7 con evidencia del motor y del paquete |
| 2 | Re-save the PBIX so it no longer contains the former local path | **satisfecha en el fondo**: existe un PBIX real, guardado por Desktop, sin la ruta `Downloads\steel-plates-quality-bi-main` del autor original |

**PRODUCCIÓN no las cierra.** Enlázalas en el PR con `refs #1` y `refs #2`, no
con `closes`, y ciérralas tú cuando aceptes el trabajo.

Sobre #2, conviene dejar constancia explícita en el PR: el PBIX lleva la ruta
local **actual** (`C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\…`) embebida en su
`DataModel`, porque es el parámetro con el que se refrescó. Lo que la incidencia
pedía era eliminar la ruta **antigua** del autor original, y eso está hecho. Si
quieres un PBIX sin ninguna ruta personal, habría que aplicar la opción B de §6.1
y volver a guardar el PBIX desde Desktop, lo que **cambiaría su SHA256** y
obligaría a recertificar.

## 8. Reversión

Tres niveles, en [`POWERBI_RENAME_BASELINE.md`](POWERBI_RENAME_BASELINE.md) §10,
con script guiado:

```powershell
docs\production\evidence\revert_powerbi_rename.ps1 -Level 2
```

Toda reversión termina recomputando SHA256 contra
`evidence/powerbi_rename_baseline_inventory.json` y exige 0 divergencias.

## 9. Riesgos residuales

| # | Riesgo | Nota |
|---|---|---|
| 1 | El PBIX embebe la ruta local actual en su `DataModel` | §7.4; decisión de OWNER |
| 2 | Sin `--basetemp`, `pytest` da 27 errores de ACL | reparar `Temp\pytest-of-<USUARIO>` o usar siempre el parámetro |
| 3 | Un futuro guardado de Desktop volverá a mover hashes | regenerar con `build_desktop_save_hashes.py` y clasificar; **no** debilitar pruebas |
| 4 | Reejecutar `tools/prepare_ml_powerbi.py` sobrescribiría la página ya refinada en Desktop | no ejecutarlo |
| 5 | `git checkout` puede reescribir los CSV congelados por `text eol=crlf` | `core.autocrlf=false` fijado; verificar SHA256 tras cualquier checkout |
| 6 | Las dos copias no canónicas invitan a validar la equivocada | §6.2 |
| 7 | El informe abre en la página ML, no en el resumen ejecutivo | aceptado por OWNER; §5.3 de la certificación |

## 10. Declaración de cierre

PRODUCCIÓN ha completado el alcance de la orden OWNER-PBI-REN-001 que le
correspondía. El criterio final —«el PBIP abre, actualiza, compila, presenta las
métricas esperadas, conserva las páginas originales y permite generar un PBIX que
se puede cerrar y reabrir sin errores»— **está cumplido y documentado con
evidencia ejecutable**.

No se ha publicado nada en GitHub ni en Power BI Service. No se ha cerrado
ninguna incidencia. No se han añadido coautores. No se ha fabricado ninguna
captura ni resultado.

Autor original del proyecto: Jesús R. L. González.

Se solicita la **aceptación formal de OWNER** (G10).
