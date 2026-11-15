# POWERBI_SECURITY_PORTABILITY

Orden: **OWNER-PBI-REN-001** · Fase 9 — Seguridad y portabilidad
Fecha: 2026-11-14 · Responsable: PRODUCCIÓN
Resultado: **CUMPLIDO** para el PBIP; la revisión del PBIX queda pendiente de la Fase 7

---

## 1. Rutas personales en archivos rastreados

Barrido del patrón `C:[\\/]Users[\\/]` sobre todo el repositorio, sin
exclusiones.

| Archivo | Nº | Naturaleza | Veredicto |
|---|---:|---|---|
| `powerbi/project/…SemanticModel/definition/expressions.tmdl` | 1 | valor de `RutaCSV` | **necesario por diseño** |
| `tests/test_bi_integration.py` | 3 | constantes de hash: baseline, marcador, valor local | necesario para la verificación de integridad |
| `docs/production/POWERBI_RENAME_BASELINE.md` y otros entregables | varias | rutas de trabajo y comandos de reversión | documentación operativa |
| `docs/production/PRODUCTION_POWERBI_HANDOFF.md` | 3 | acta histórica, marcada SUPERSEDED | histórico |
| `docs/production/evidence/compare_zip_vs_commit.py` | 1 | script de evidencia de la Fase 0 | evidencia reproducible |
| `docs/production/POWERBI_RENAME_DEPENDENCY_MATRIX.md` | 1 | cita la ruta `Downloads` del autor original | documenta por qué no se renombra |

**Ningún archivo de código o artefacto funcional contiene una ruta personal**
salvo `RutaCSV`, que debe contenerla: Power Query necesita una ruta absoluta
que resuelva en la máquina.

Verificación automática ya existente en la suite:
`test_new_sources_and_artifacts_have_no_host_dependency` exige que
`ML_Holdout.tmdl`, `artifacts/manifest.json`, el export ML y los módulos de
`src/quality_ml/inference/` **no** contengan `c:\users\`, `c:/users/` ni
`downloads\`. **PASS.**

### 1.1 Ruta personal antigua — estado de la incidencia #2

La incidencia #2 («Re-save the PBIX so it no longer contains the former local
path») se refiere a la ruta del autor original,
`C:\Users\Lowo\Downloads\steel-plates-quality-bi-main\…`.

| Ubicación | Estado |
|---|---|
| `expressions.tmdl` (PBIP) | ✅ **ya no la contiene**; contiene la ruta canónica actual |
| `tests/test_bi_integration.py` (`RUTA_CSV_BASELINE`) | presente **a propósito**: constante de reconstrucción de hash histórico |
| PBIX | ⛔ **no verificable** — no existe ningún PBIX binario (ver abajo) |

**La incidencia #2 no puede cerrarse.** Su verificación exige inspeccionar un
PBIX, y no existe: el objeto LFS devuelve 404 y no hay copia binaria local. Sólo
podrá comprobarse sobre el PBIX que genere la Fase 7.

## 2. Fuentes de datos

| Fuente | Expresión | Mecanismo | Autorizada |
|---|---|---|---|
| CSV crudo | `RutaCSV` → `Raw_SteelPlates` | `File.Contents` local | ✅ |
| Export del holdout | `RutaMLCSV` → `ML_Holdout` | `File.Contents` local | ✅ |

No hay ninguna otra fuente. **Ningún servicio en la nube, ninguna base de datos,
ninguna credencial.** `Raw_SteelPlates` contempla una rama `Web.Contents` para
valores `http(s)://`, inactiva con el valor actual.

`powerbi/powerquery/00_Parametros.pq` documenta una alternativa en línea
(`raw.githubusercontent.com/jesusrlgonzalez/steel-plates-quality-bi/main/…`). Es
una URL pública de sólo lectura, sin credenciales. No se modificó (protegida por
una comprobación de hash; ver
[`POWERBI_RENAME_DEPENDENCY_MATRIX.md`](POWERBI_RENAME_DEPENDENCY_MATRIX.md) §5.2).

## 3. Local frente a portable

La ruta `C:\Users\<USUARIO>\…` **funciona en este equipo** y **no** constituye una
configuración portátil. Distinción explícita:

| Aspecto | Esta instalación | Otro equipo |
|---|---|---|
| `RutaCSV` | válida tal cual | **requiere reconfiguración manual** |
| `RutaMLCSV` | se deriva de `RutaCSV` | se deriva sola, sin tocar nada |
| Power BI Service | **no funcionará** una actualización automática basada en `C:` | requiere puerta de enlace o migración autorizada de la fuente |

`RutaMLCSV` deriva la raíz del repositorio de `RutaCSV`, de modo que
**reconfigurar una sola expresión basta**.

### 3.1 Instrucciones de reconfiguración en otra instalación

1. Clonar o extraer el repositorio en cualquier ubicación, conservando la
   estructura interna (`data/raw/` y `powerbi/data/` deben seguir siendo
   hermanos bajo la raíz).
2. Abrir `powerbi/project/steel-plates-quality-mlops-powerbi.pbip` en Power BI
   Desktop.
3. **Transformar datos** → expresión `RutaCSV` → **Editor avanzado**.
4. Sustituir el valor por la ruta absoluta local de
   `data/raw/steel_plates_faults.csv`, en una sola línea entre comillas:

   ```powerquery
   "D:\mi\ruta\steel-plates-quality-mlops\data\raw\steel_plates_faults.csv"
   ```

   **Usar una sola barra invertida por separador.** TMDL/M no escapan la barra:
   un separador doblado sobrevive a `File.Contents` pero rompe la derivación de
   `RutaMLCSV` y `ML_Holdout` no cargará. Detalle en
   [`POWERBI_POWERQUERY_VALIDATION.md`](POWERBI_POWERQUERY_VALIDATION.md) §3.

   La ruta **debe** contener el segmento `/data/raw/` (o `\data\raw\`): es lo que
   `RutaMLCSV` usa para localizar la raíz del repositorio.

5. **No** tocar `RutaMLCSV`: se recalcula sola.
6. **Cerrar y aplicar**. Verificar 1 941 filas en el hecho y 389 en `ML_Holdout`.

Alternativa sin ruta local: poner en `RutaCSV` la URL pública de
`00_Parametros.pq`. **Advertencia:** `RutaMLCSV` exige el segmento `/data/raw/`,
que la URL contiene, pero la raíz derivada apuntaría al repositorio remoto y el
export ML debe existir también allí. No verificado por PRODUCCIÓN.

## 4. Archivos de configuración local y caché

| Archivo | En disco | Rastreado por Git | Regla |
|---|---|---|---|
| `.pbi/editorSettings.json` | sí (243 B) | **sí** | parte de la línea base; no contiene datos personales |
| `.pbi/localSettings.json` | **no** | no | ignorado por `.gitignore` línea 6 |
| `.pbi/cache.abf` | **no** | no | ignorado por `.gitignore` línea 7 |

`git check-ignore -v` confirma que ambas rutas quedarían ignoradas si Desktop
las crease. **Tras la Fase 7 hay que volver a comprobarlo**, porque Desktop
genera ambos al abrir y guardar:

```powershell
git status --porcelain | Select-String "\.pbi/"
```

La salida debe estar vacía salvo `editorSettings.json`, si Desktop lo modifica.

`.gitignore` también excluye `.venv/`, `__pycache__/`, `.pytest_cache/`,
`dbt/target/`, `dbt/logs/`, `dbt/.user.yml`, `artifacts/onnx/` y
`node_modules/`. Verificado: el índice contiene **278** archivos y ninguno de
esas rutas.

## 5. Riesgo de distribuciones divergentes

Existen **tres** copias del proyecto en este equipo. Es el riesgo operativo más
probable de esta entrega:

| Ruta | Estado | Uso |
|---|---|---|
| `<CARPETA_DE_TRABAJO>\steel-plates-quality-mlops` | **canónica, renombrada, corregida** | la única válida |
| `<CARPETA_DE_TRABAJO>\STEEL_PLATES_QUALITY_MLOPS_PARA_WINDOWS\steel-plates-quality-mlops` | línea base intacta | respaldo; **no editar** |
| `<CARPETA_DE_TRABAJO>\Steel_Plates_PowerBI_Lista_Para_Desktop_Local` | **divergente**, sin renombrar ni corregir | **no usar** |

La tercera tiene un `expressions.tmdl` distinto (1 333 B frente a 1 354 B), un
`test_bi_integration.py` distinto, su propio `MANIFEST_SHA256_LOCAL.json` y una
carpeta `deploy_local/`. Su `RutaCSV` apunta a
`C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\data\raw\steel_plates_faults.csv` —una
ruta que **no existe**— y con separadores doblados.

**Se observó Power BI Desktop (PID 34952) con esa tercera copia abierta.**
Validar ahí **no** valida este proyecto. Antes de la Fase 7, cerrarla.

Recomendación a OWNER: tras aceptar esta entrega, eliminar o archivar las dos
copias no canónicas para evitar validar la equivocada. PRODUCCIÓN **no las ha
eliminado**: la segunda es el respaldo de reversión y la tercera no es suya.

## 6. Datos sensibles

| Comprobación | Resultado |
|---|---|
| Credenciales, tokens, secretos | ✅ ninguno |
| Cadenas de conexión con usuario y contraseña | ✅ ninguna |
| Identificadores privados o datos personales en los CSV | ✅ ninguno: mediciones geométricas de placas y etiquetas de defecto |
| Claves de API | ✅ ninguna |
| Nombre de usuario de Windows (`<USUARIO>`) | presente en las rutas; es el nombre de la cuenta local del propietario del repositorio |

El único identificador personal expuesto es el nombre de cuenta `<USUARIO>`, inherente
a cualquier ruta absoluta de este equipo. Si OWNER quiere evitar publicarlo en
GitHub, debe revertir `RutaCSV` al marcador neutro **antes** del Pull Request:

```
expression RutaCSV = "C:\path\to\steel-plates-quality-mlops\data\raw\steel_plates_faults.csv"
```

La prueba acepta ese valor sin ningún otro cambio (es el primero de
`RUTA_CSV_ACCEPTED`). **Pero entonces el PBIP deja de abrir con datos en este
equipo**, de modo que la reversión debe hacerse **después** de completar la
Fase 7. Decisión de OWNER; ver
[`POWERBI_PRODUCTION_HANDOFF_TO_OWNER.md`](POWERBI_PRODUCTION_HANDOFF_TO_OWNER.md) §5.

Nota: si se revierte al marcador neutro, usar **una sola** barra invertida por
separador, no la forma doblada de la línea base.

## 7. Power BI Service

**No se ha publicado nada y no se publicará sin autorización OWNER expresa.**

Para una publicación futura hay que resolver antes:

1. Las fuentes `File.Contents` sobre `C:` **no** se actualizan en el Service sin
   una puerta de enlace de datos local con acceso a los archivos.
2. Alternativa: migrar las fuentes a un almacenamiento accesible desde la nube
   (decisión autorizada, no tomada).
3. Licencias, permisos de área de trabajo y estrategia de actualización.
4. Revisar si publicar los datos del holdout es aceptable para el destinatario.

## 8. Resumen

| Control | Estado |
|---|---|
| El PBIP no conserva rutas personales antiguas | ✅ |
| Fuentes de datos autorizadas y sin credenciales | ✅ |
| Ruta local distinguida de configuración portátil | ✅ |
| Instrucciones de reconfiguración de `RutaCSV` | ✅ apartado 3.1 |
| Sin datos sensibles, secretos ni identificadores privados | ✅ |
| `.pbi/` de configuración y caché fuera de Git | ✅ (reverificar tras la Fase 7) |
| Sin publicación en Power BI Service | ✅ |
| **El PBIX no conserva rutas antiguas** | ⛔ **no verificable: no existe ningún PBIX** |
