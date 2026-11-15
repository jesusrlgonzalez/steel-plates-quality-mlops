# POWERBI_RENAME_BASELINE

Orden: **OWNER-PBI-REN-001** · Fase 0 — Línea base y protección
Fecha de ejecución: 2026-11-14 · Responsable: PRODUCCIÓN
Gate: **G0** · Resultado: **CERTIFICADA**

Autor original del proyecto: Jesús R. L. González.

---

## 1. Origen real: rama y commit

| Dato | Valor | Evidencia |
|---|---|---|
| Remoto | `https://github.com/jesusrlgonzalez/steel-plates-quality-mlops.git` | `git ls-remote --heads` |
| Rama | `main` | `git ls-remote --heads` |
| Commit de `main` | `e19cd1af045ea22e4518f3795f9c5070979a924f` | `git ls-remote`; `git rev-parse HEAD` en clon `--depth 1` |

El `PRODUCTION_CHANGELOG.md` previo declaraba este commit con la marca
`snapshot ZIP commit UNVERIFIED`. **Esa equivalencia queda ahora demostrada**
(apartado 3).

Ramas remotas presentes en el momento de la comprobación: `main`,
`docs/author-name`, `docs/iso-rules-not-audited`,
`docs/site-already-defective-scope`, `feat/decision-value-and-drift`,
`feat/discoverability`, `fix/ci-runner-and-powerbi-baseline`.

## 2. Estado del repositorio local recibido

La copia recibida **no era un repositorio Git**: no existía `.git/`, por lo que
no había rama, commit ni índice local. No había, por tanto, «cambios locales»
en sentido Git que registrar.

Decisión OWNER aplicada: inicializar un repositorio Git local para dar
trazabilidad al renombrado.

| Acción | Valor |
|---|---|
| `git init -b main` | repositorio creado en el directorio canónico |
| `git lfs install --local` | ganchos LFS instalados |
| `core.autocrlf` | `false` (evita reescrituras de la evidencia científica) |
| Commit de línea base | `be46d0c` — *baseline: estado recibido sin modificar (OWNER-PBI-REN-001 Fase 0)* |
| Archivos indexados | **274** |
| `git status` tras el commit | limpio |

El commit `be46d0c` contiene el estado **tal como fue recibido**, sin ninguna
modificación de PRODUCCIÓN. Es el punto de reversión.

## 3. Contenido del ZIP original frente a la distribución Windows

Comparación automática entre el clon de `e19cd1af` (ZIP/commit original) y la
distribución preparada para Windows. Script de evidencia:
`compare_zip_vs_commit.py` (normaliza CRLF→LF además de comparar bytes crudos).

| Métrica | Valor |
|---|---|
| Archivos en la distribución Windows | **274** |
| Archivos en el commit `e19cd1af` | **263** |
| Presentes sólo en el commit | **0** |
| Añadidos por la distribución | **11** (todos bajo `docs/production/`) |
| Originales con bytes distintos | **1** |
| Originales distintos tras normalizar CRLF→LF | **1** |

### 3.1 Archivos añadidos por la distribución (no originales)

`docs/production/PRODUCTION_APPLICATION_VALIDATION.md`,
`PRODUCTION_BASELINE.md`, `PRODUCTION_CHANGELOG.md`,
`PRODUCTION_HANDOFF_TO_OWNER.md`, `PRODUCTION_POWERBI_HANDOFF.md`,
`PRODUCTION_RECONCILIATION.md`, `PRODUCTION_RELEASE_MANIFEST.json`,
`PRODUCTION_RELEASE_MANIFEST.md`, `PRODUCTION_SCIENTIFIC_INTEGRITY.md`,
`PRODUCTION_SECURITY_REVIEW.md`, `PRODUCTION_TEST_RESULTS.md`.

### 3.2 Único archivo original divergente

`powerbi/project/steel-plates-quality-bi.SemanticModel/definition/expressions.tmdl`

Corresponde exactamente a la sustitución de `RutaCSV` declarada en el punto 1
de `PRODUCTION_CHANGELOG.md`. **No hay ninguna otra divergencia**: ni en
artefactos científicos, ni en TMDL, ni en PBIR/PBIP, ni en los CSV, ni en el
puntero PBIX. La declaración del changelog previo queda verificada.

## 4. Git LFS y el PBIX anterior — HALLAZGO BLOQUEANTE

`powerbi/artifacts/steel-plates-quality-bi.pbix` es, en la distribución y en el
commit, un **puntero Git LFS de 131 bytes**:

```
version https://git-lfs.github.com/spec/v1
oid sha256:0a87a4e33b78cf786d1a76250b39f154d19508480f256fa1898e8f818d9bdba5
size 213709
```

Se intentó materializar el binario desde el remoto público
(`git clone --depth 1` + `git lfs pull`). Resultado:

```
Error downloading object: powerbi/artifacts/steel-plates-quality-bi.pbix (0a87a4e):
  Smudge error: [0a87a4e33b78cf786d1a76250b39f154d19508480f256fa1898e8f818d9bdba5]
  Object does not exist on the server: [404] Object does not exist on the server
```

**El objeto LFS no existe en el almacenamiento del servidor.** En consecuencia:

1. El PBIX anterior **no es recuperable** desde el repositorio remoto.
2. No existe ninguna copia del PBIX binario en el disco local.
3. La comparación «PBIX anterior ↔ PBIX nuevo» exigida por la Fase 0 es
   **IMPOSIBLE DE EJECUTAR** por ausencia del objeto en origen, no por decisión
   de PRODUCCIÓN.
4. El PBIX que se genere en la Fase 7 será el **único** PBIX binario real
   disponible del proyecto.

Esto se eleva a OWNER como riesgo material y refuerza la necesidad de la
Fase 7. No se ha intentado ni se intentará fabricar bytes PBIX.

Distinción obligatoria registrada:

| Concepto | Estado |
|---|---|
| PBIX anterior (oid `0a87a4e3…`, 213 709 bytes) | **NO RECUPERABLE** — objeto LFS ausente en el servidor |
| Puntero LFS en disco (SHA256 `a89d3c1c…`, 131 bytes) | presente; **no es un informe ejecutable** |
| PBIX nuevo desde el PBIP renombrado | **NO GENERADO** — Fase 7 pendiente |

La regla `*.pbix filter=lfs diff=lfs merge=lfs -text` de `.gitattributes` está
activa y verificada (`git lfs ls-files` → `0a87a4e33b - powerbi/artifacts/steel-plates-quality-bi.pbix`).
Se preservará en el renombrado.

## 5. Ubicación y protección

| Rol | Ruta |
|---|---|
| Copia de trabajo (canónica, §3 de la orden) | `C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\steel-plates-quality-mlops` |
| Línea base intacta (protección/reversión) | `C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\STEEL_PLATES_QUALITY_MLOPS_PARA_WINDOWS\steel-plates-quality-mlops` |

La copia al directorio canónico se verificó archivo a archivo: **274 archivos,
0 divergencias de SHA256** entre origen y destino. Se excluyeron únicamente
`__pycache__/` y `.pytest_cache/` (artefactos de ejecución, no parte del estado
recibido).

El árbol de origen se conserva **sin modificar** como respaldo físico
independiente de Git. No debe editarse.

## 6. Inventario SHA256 de los archivos originales

Manifiesto completo de los 274 archivos (ruta, tamaño, SHA256):
[`evidence/powerbi_rename_baseline_inventory.json`](evidence/powerbi_rename_baseline_inventory.json).

Archivos afectados por el renombrado y referencias clave:

| SHA256 | Bytes | Ruta original |
|---|---:|---|
| `edef13b31f0e4ad4d7d69e6e49480a2ce999d9c12d94b5a3d81e18092ab530ff` | 183 | `powerbi/project/steel-plates-quality-bi.pbip` |
| `cc8873c86532db0d5e3e66cf7cd41ab88538eb5f0816ba3f0431e4a24bd1b49c` | 130 | `…bi.Report/definition.pbir` |
| `fe85bcb82c5ae82c5886505eb019cf7f8da97ba7e2592972b09f2394c49b14a0` | 307 | `…bi.Report/.platform` |
| `00dc543752fb328e18e9967a25d0b39f5aecef9179ae94e4ed15eb7e078c7944` | 40 | `…bi.SemanticModel/definition.pbism` |
| `b654c065889b1e7cbefa519833e2a882bf90904130f86baf96a00673d24da93b` | 314 | `…bi.SemanticModel/.platform` |
| `7a15a4c33068eaf68c5afffa57f3a917daf3bc2c7197799826729c5bb24c5881` | 621 | `…SemanticModel/definition/model.tmdl` |
| `df316433fc6cd184d6ddd22011918ac69546275661a62e3883c8bf3e72af66f2` | 427 | `…SemanticModel/definition/relationships.tmdl` |
| `e077b5b306cfd5ed9638435be67e985563edfa243bca82948d92f658188a93a1` | 1 361 | `…SemanticModel/definition/expressions.tmdl` |
| `da20e260a2792dfb71077081c9d6f0f88cb3e8f099b3041758f76039925c237d` | 3 962 | `…SemanticModel/definition/tables/ML_Holdout.tmdl` |
| `a89d3c1c8d9bcb1107833c28b8e38908a100776d2d57c60be91df4a3fd96c406` | 131 | `powerbi/artifacts/steel-plates-quality-bi.pbix` (puntero LFS) |
| `cb07fc4284cb1bea5b308ef1822f4440e83e16d53703b5d3254a0b5def76f408` | 315 926 | `data/raw/steel_plates_faults.csv` |
| `5f5fb946b8817fc630059878ea67be4c75e38b1da77c5faf88b9eecf8e671cb5` | 63 243 | `powerbi/data/ml_holdout_evaluation.csv` |
| `e1d73a6aa05b6e7fec56786d7753f79f86f79347b4d7277c29fcaadb8248d510` | 617 | `.gitattributes` |
| `5514ce7c0b50a8d1e0bcf69a32440d2b81730a42cd73095c44354068c97ccf44` | 9 100 | `tools/prepare_ml_powerbi.py` |
| `560632039c3f02efa55954343b7bfc4ce433278170519d7440f0d53db038a2dd` | 7 463 | `tests/test_bi_integration.py` |

Subtotal del componente Power BI: **86 archivos** bajo `powerbi/`.

## 7. Estado de las incidencias #1 y #2

Consulta con `gh issue list --repo jesusrlgonzalez/steel-plates-quality-mlops --state all`:

| # | Título | Estado | Última actualización |
|---|---|---|---|
| 1 | Validate the Power BI layer in Power BI Desktop (runtime gate) | **OPEN** | 2026-11-14T13:25:46Z |
| 2 | Re-save the PBIX so it no longer contains the former local path | **OPEN** | 2026-11-14T13:26:02Z |

Ambas permanecen abiertas, conforme a §14 de la orden. PRODUCCIÓN no las cerrará.

## 8. Pruebas y manifiestos dependientes de los nombres antiguos

Inventariado en detalle en
[`POWERBI_RENAME_DEPENDENCY_MATRIX.md`](POWERBI_RENAME_DEPENDENCY_MATRIX.md).
Resumen de los puntos que condicionan el renombrado:

- `tests/test_bi_integration.py` recorre las claves de
  `docs/evidence/pre_ml_powerbi_hashes.json`, que están escritas con el nombre
  antiguo. Requiere **correspondencia trazable**, no reescritura del manifiesto.
- `docs/evidence/pre_ml_powerbi_hashes.json` es **evidencia histórica protegida**
  (§5 de la orden): no se modifica ni se recalcula.
- `tools/prepare_ml_powerbi.py` define `PROJECT` con el nombre antiguo; es ruta
  operativa y debe actualizarse.
- `.gitattributes` fija tres rutas `eol=lf` con el nombre antiguo; rutas
  operativas, deben actualizarse preservando la regla LFS de `*.pbix`.

## 9. Estado de las pruebas en la línea base (antes de tocar nada)

`tools.project_checks` — **5/5 PASS**:

| Comprobación | Resultado |
|---|---|
| `lint` | PASS (60 archivos, AST) |
| `validate-data` | PASS — 1 941 filas, 27 predictoras |
| `validate-artifact` | PASS — modelo `6f363b2c…`, huella de entrenamiento `bc1b6278…` |
| `batch-smoke` | PASS — 8 filas, `rf-phase8-v1`, entrada `TRAINING_ONLY` |
| `validate-evidence` | PASS — 389 / 307 / 82 / 261 |

`pytest -q` — **123 passed, 1 failed, 2 skipped, 27 errors** (884 s):

| Clase | Nº | Causa |
|---|---:|---|
| Fallo real | 1 | `test_previous_powerbi_preserved`: la prueba exige el marcador neutro `C:\path\to\…` en `RutaCSV`, pero la distribución lo sustituyó por la ruta Windows. Conflicto preexistente entre Fase 3 y Fase 8 de la orden. |
| Errores de entorno | 27 | `PermissionError [WinError 5]` al listar `C:\Users\<USUARIO>\AppData\Local\Temp\pytest-of-<USUARIO>`. ACL del directorio temporal de pytest, ajeno al código del proyecto. |

Ambos quedan abiertos como tareas de la Fase 8. Ninguno es un defecto
científico y ninguno se resolverá desactivando controles de preservación.

## 10. Procedimiento de reversión

Tres niveles independientes, de más barato a más robusto:

**N1 — Revertir el árbol de trabajo al estado recibido (Git):**

```powershell
Set-Location "<REPO>"
git stash list                       # conservar intentos si procede
git checkout main
git reset --hard be46d0c
git clean -fd                        # NO usar -x: preserva .venv y cachés
```

**N2 — Descartar sólo el renombrado, conservando la evidencia del intento:**

```powershell
git checkout main                    # la rama fix/... permanece para auditoría
```

**N3 — Restauración física desde el respaldo intacto** (si Git quedara
inutilizable):

```powershell
robocopy "C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\STEEL_PLATES_QUALITY_MLOPS_PARA_WINDOWS\steel-plates-quality-mlops" `
         "<REPO>" `
         /MIR /XD __pycache__ .pytest_cache .git
```

Verificación obligatoria tras cualquier reversión: recomputar SHA256 contra
`evidence/powerbi_rename_baseline_inventory.json` y exigir 0 divergencias.

Advertencia: `.gitattributes` declara `text eol=crlf` para
`data/raw/steel_plates_faults.csv` y `reports/ml/final_holdout/*.csv`. Un
`git checkout` que reescriba esos archivos puede alterar sus bytes y romper las
huellas científicas. Por eso `core.autocrlf` está en `false` y toda reversión
debe cerrarse con la verificación SHA256 anterior.

## 11. Gate G0

| Condición | Resultado |
|---|---|
| Rama y commit de origen identificados | ✅ `main` @ `e19cd1af` |
| Estado del repositorio local registrado | ✅ no era repositorio Git; línea base creada en `be46d0c` |
| ZIP original vs distribución Windows comparados | ✅ 1 sola divergencia original, documentada |
| Diferencias entre paquetes registradas | ✅ apartado 3 |
| Git LFS comprobado | ✅ regla activa; **objeto PBIX ausente en el servidor (404)** |
| Inventario de archivos afectados | ✅ apartados 6 y 8 |
| SHA256 de los originales registrados | ✅ 274 archivos |
| Incidencias #1 y #2 verificadas | ✅ ambas OPEN |
| Pruebas/manifiestos dependientes identificados | ✅ apartado 8 |
| Procedimiento de reversión preparado | ✅ apartado 10 |

**G0: CERTIFICADA.** Recuperación viable mediante N1/N2/N3.

Salvedad elevada a OWNER: el PBIX anterior no es recuperable (apartado 4). La
línea base del *proyecto* es completa; la línea base del *binario PBIX* no
existe en ninguna parte.

Estado tras la Fase 0: `SOURCE_INSPECTED`.
