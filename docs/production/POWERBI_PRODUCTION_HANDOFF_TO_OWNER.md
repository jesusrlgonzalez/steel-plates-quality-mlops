# POWERBI_PRODUCTION_HANDOFF_TO_OWNER

Orden: **OWNER-PBI-REN-001** · Entrega de PRODUCCIÓN a OWNER
Fecha: 2026-11-14 · Responsable: PRODUCCIÓN
Rama: `fix/powerbi-canonical-naming-pbix`
Estado oficial: **`PBIX_GENERATED_AND_REOPENED`** · **`READY_FOR_OWNER_REVIEW`**

> **CIERRE 2026-11-15 — TODOS LOS GATES TÉCNICOS SUPERADOS.**
> OWNER ejecutó la inspección visual y guardó el PBIX; PRODUCCIÓN lo verificó,
> reubicó y certificó. **G2 a G8 están en PASS.** Quedan G9 (Pull Request) y G10
> (aceptación), que no son de PRODUCCIÓN.
>
> Documento vigente de cierre, con los pasos de publicación:
> [`POWERBI_PRODUCTION_CLOSEOUT.md`](POWERBI_PRODUCTION_CLOSEOUT.md).
> Certificación del artefacto: [`POWERBI_PBIX_CERTIFICATION.md`](POWERBI_PBIX_CERTIFICATION.md).
>
> Lo que sigue refleja el estado del 2026-11-14/15 **antes** de la ejecución en
> Desktop; las tablas de los apartados 1 y 4 han quedado superadas. Los hallazgos
> del apartado 2 siguen siendo historia útil: el nº 1 (objeto LFS roto) **quedó
> reparado** por el PBIX nuevo, y el nº 3 (tres copias) sigue vigente.

Autor original del proyecto: Jesús R. L. González.
PRODUCCIÓN no ha añadido coautores.

> **ACTUALIZACIÓN 2026-11-15.** Power BI Desktop abrió el PBIP renombrado y
> PRODUCCIÓN validó su motor en vivo por XMLA en solo lectura. **G2, G3, G4 y G6
> pasaron** con cifras del motor real, no de las fuentes. Evidencia completa:
> [`POWERBI_DESKTOP_RUNTIME_EVIDENCE.md`](POWERBI_DESKTOP_RUNTIME_EVIDENCE.md).
>
> Quedan **dos** tareas, ambas en la GUI:
> **G5** mirar las cinco páginas, y **G7** `Archivo → Guardar como` para el PBIX.
>
> Las tablas de los apartados 1 y 4 que siguen reflejan el estado del 2026-11-14
> y han quedado superadas en esos cuatro gates; el apartado 4 lleva su propia
> nota. Los tres hallazgos del apartado 2 **siguen vigentes**, salvo que el
> riesgo de autodetección de relación hacia `ML_Holdout` **no se materializó** en
> esta carga.

---

## 1. Lo que se entrega y lo que no

### Completado y verificado

| Trabajo | Evidencia |
|---|---|
| Línea base certificada, 274 archivos, 0 divergencias | [`POWERBI_RENAME_BASELINE.md`](POWERBI_RENAME_BASELINE.md) |
| Equivalencia ZIP ↔ commit `e19cd1af` **demostrada** | ídem §3 |
| Matriz de dependencias: 14 ubicaciones, 4 clases | [`POWERBI_RENAME_DEPENDENCY_MATRIX.md`](POWERBI_RENAME_DEPENDENCY_MATRIX.md) |
| Renombrado canónico: 75 archivos, `git mv` trazable | [`POWERBI_RENAME_CHANGELOG.md`](POWERBI_RENAME_CHANGELOG.md) |
| Defecto de `RutaCSV` corregido y demostrado | [`POWERBI_POWERQUERY_VALIDATION.md`](POWERBI_POWERQUERY_VALIDATION.md) §3 |
| Validación estática: **77/77 PASS** | [`evidence/powerbi_static_validation.py`](evidence/powerbi_static_validation.py) |
| Regresión: **151 passed, 0 failed, 0 errors** | [`POWERBI_PRODUCTION_TEST_REPORT.md`](POWERBI_PRODUCTION_TEST_REPORT.md) |
| Reconciliación científica del origen: 0 divergencias | [`POWERBI_RECONCILIATION_RESULTS.md`](POWERBI_RECONCILIATION_RESULTS.md) |
| Seguridad y portabilidad | [`POWERBI_SECURITY_PORTABILITY.md`](POWERBI_SECURITY_PORTABILITY.md) |
| Reversión guiada en 3 niveles | [`evidence/revert_powerbi_rename.ps1`](evidence/revert_powerbi_rename.ps1) |

### No ejecutado

| Pendiente | Motivo |
|---|---|
| Apertura del PBIP en Desktop | requiere la interfaz gráfica nativa |
| Actualización real de Power Query | ídem |
| Compilación DAX en el motor | ídem |
| Renderización de las cinco páginas | ídem |
| Lectura de las cifras en pantalla | ídem |
| **Generación del PBIX** | ídem |
| **Capturas de Desktop** | ídem; **no se ha fabricado ninguna** |

Power BI Desktop está instalado (`2.156.951.0 (26.07)`), pero PRODUCCIÓN no
acciona aplicaciones de escritorio. Conforme a §20 de la orden, se entrega el
PBIP preparado, las correcciones verificadas y el procedimiento exacto, **sin
declarar generado el PBIX**.

## 2. Los tres hallazgos que requieren decisión de OWNER

### 2.1 El PBIX histórico es irrecuperable — BLOQUEANTE

El objeto Git LFS del PBIX **no existe en el almacenamiento del servidor**:

```
Error downloading object: powerbi/artifacts/steel-plates-quality-bi.pbix (0a87a4e):
  Object does not exist on the server: [404] Object does not exist on the server
```

El puntero está en el repositorio, pero el binario de 213 709 bytes que declara
nunca llegó al almacenamiento LFS o se perdió. **No hay ninguna copia binaria en
el disco local**, en ninguna de las tres distribuciones.

Consecuencias:

- La comparación «PBIX anterior ↔ PBIX nuevo» de la Fase 0 es **inejecutable**.
- El PBIX de la Fase 7 será el **único** PBIX real que habrá existido.
- La incidencia #2 **no puede cerrarse**: verificar que el PBIX no conserva la
  ruta local antigua exige un PBIX, y no hay ninguno.

**Decisión de OWNER:** aceptar que la Fase 7 se ejecute sin línea base binaria
contra la que contrastar, y decidir si procede corregir el estado de LFS en el
remoto (el puntero actual apunta a un objeto inexistente, lo que hace fallar
cualquier `git lfs pull` del repositorio).

### 2.2 Defecto corregido que impedía cargar los datos ML

`RutaCSV` almacenaba separadores **doblados**. TMDL guarda el código M literal y
no escapa la barra invertida — lo confirma un proyecto PBIP generado por tu
propio Desktop en este equipo, cuyo `P30_Path` usa una sola barra, y el hecho de
que la línea 28 del mismo archivo use una barra simple dentro de una cadena M.

Efecto encadenado demostrado:

| Paso | Resultado con separador doblado |
|---|---|
| `File.Contents(RutaCSV)` | funciona (Windows contrae separadores) |
| `Text.Replace(…, "\", "/")` | `C://Users//…//data//raw//…` |
| `Text.Contains(Normalized, "/data/raw/")` | **FALSO** |
| `RutaMLCSV` | **error**; `ML_Holdout` no carga |
| Página `MODEL PERFORMANCE & REVIEW` | **sin datos** |

Lo insidioso es que la tabla original **sí** cargaba: el síntoma aparecía sólo en
la tabla ML, sugiriendo un problema del holdout cuando la causa estaba en el
parámetro compartido. G3, G4, G5 y G6 habrían fallado en Desktop.

Corrección: separadores simples en el valor de `RutaCSV`. Ninguna otra línea.

**Este defecto está también en el commit remoto `e19cd1af` y en las otras dos
distribuciones locales**, incluido el marcador neutro
(`C:\\path\\to\\steel-plates-quality-mlops\\data\\raw\\…`). No lo introdujo
PRODUCCIÓN.

**Decisión de OWNER:** si se revierte `RutaCSV` al marcador neutro antes del PR
(apartado 5), usar **una sola** barra invertida. Mantener la forma doblada
perpetuaría el defecto para cualquiera que clone el repositorio.

### 2.3 Hay tres copias del proyecto; Desktop tenía abierta la equivocada

| Ruta | Estado |
|---|---|
| `<CARPETA_DE_TRABAJO>\steel-plates-quality-mlops` | **canónica**, renombrada y corregida |
| `…\STEEL_PLATES_QUALITY_MLOPS_PARA_WINDOWS\steel-plates-quality-mlops` | línea base intacta (respaldo) |
| `…\Steel_Plates_PowerBI_Lista_Para_Desktop_Local` | **divergente**, sin renombrar ni corregir |

Se observó Power BI Desktop (PID 34952) con la **tercera** abierta. Su `RutaCSV`
apunta a `C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\data\raw\steel_plates_faults.csv`,
ruta que **no existe**, y con separadores doblados.

**Validar ahí no valida este proyecto.** Cerrarla antes de la Fase 7.

**Decisión de OWNER:** eliminar o archivar las dos copias no canónicas tras
aceptar la entrega. PRODUCCIÓN no las ha eliminado: la segunda es el respaldo de
reversión y la tercera no es suya.

## 3. Desvíos respecto a la orden, declarados

| Punto de la orden | Desvío | Justificación |
|---|---|---|
| §3 — repositorio en el directorio canónico | Se **copió** al directorio canónico en lugar de mover; el árbol original se conserva intacto | El directorio de trabajo del entorno apuntaba al árbol a mover. La copia alcanza el mismo estado final exigido y además aporta el respaldo físico que pide la Fase 0. Verificado: 274 archivos, 0 divergencias de SHA256 |
| §4 — línea base Git | El repositorio recibido **no era un repositorio Git** | Se inicializó uno local con commit de línea base `be46d0c`, previa aprobación. Sin remoto ni push |
| §3 — nomenclatura | El `displayName` de `.platform` **no** se renombró | No es una ruta; nada resuelve a través de él. Cambiarlo exigiría abrir una excepción nueva en un control de preservación sin necesidad funcional. Detalle en la matriz §2.1 |
| §14 — Pull Request | **No** se abrió PR | Sin remoto configurado y sin autorización de push. Se entrega parche aplicable (apartado 6) |
| §12 — comando de pruebas | Se añadió `--basetemp` a `pytest` | ACL del perfil de Windows deniega el acceso a `Temp\pytest-of-<USUARIO>`, provocando 27 errores ajenos al proyecto |
| §1.4 — corregir defectos comprobados | Se corrigió `RutaCSV`, que **no** era parte del renombrado | Defecto demostrado que impedía la actualización. Autorizado explícitamente por §1.4 |

Ninguna restricción absoluta de §15 fue vulnerada: no se reconstruyó el
proyecto, no se creó otro repositorio, no se reentrenó el modelo, no se
recalibraron políticas, no se alteró el holdout, no se cambiaron métricas
congeladas, no se modificaron manifiestos históricos, no se eliminó ninguna
prueba fallida sin investigarla, no se fabricó ninguna captura ni resultado, no
se presentó el PBIP como PBIX, no se presentó el puntero LFS como PBIX
funcional, no se declaró Desktop validado, no se publicó en el Service, no se
cerraron las incidencias y no se añadieron coautores.

## 4. Estado de los gates

Actualizado al 2026-11-15 con la evidencia del motor en vivo.

| Gate | Condición | Estado |
|---|---|---|
| G0 | Línea base certificada | ✅ **CERTIFICADA** |
| G1 | Nombres y dependencias coherentes | ✅ **CUMPLIDO** |
| G2 | PBIP abre sin errores | ✅ **PASS** (motor) |
| G3 | Power Query actualiza correctamente | ✅ **PASS** — 7/7 particiones Ready, 1 941 y 389 |
| G4 | Modelo semántico y DAX validados | ✅ **PASS** — 3 relaciones m:1 unidir., `ML_Holdout` suelta, 34/34 medidas |
| G5 | Cinco páginas funcionales | ⛔ **NO EJECUTADO** · estructura ✅ |
| G6 | Reconciliación científica satisfactoria | ✅ **PASS** — diferencia 0 en las cuatro métricas |
| G7 | PBIX generado, cerrado y reabierto | ⛔ **NO EJECUTADO** |
| G8 | Pruebas y hashes verificados | ✅ pruebas · ⛔ hash del PBIX |
| G9 | Pull Request revisado | ⛔ no abierto |
| G10 | Aceptación formal OWNER | ⛔ pendiente |

Cada gate se evaluó por separado. **No se compensa ningún gate fallido con la
aprobación de otro.** En particular, que G2–G4 y G6 hayan pasado **no** promueve
G5: los visuales están en la capa de informe y el motor no sabe nada del lienzo.
Y nada de esto genera un PBIX.

## 5. Antes del Pull Request: decisión sobre `RutaCSV`

`expressions.tmdl` contiene hoy la ruta local del equipo. Es **necesario** para
que el PBIP abra con datos aquí, y es **indeseable** en un repositorio público.

| Opción | Efecto |
|---|---|
| **A — Mantener la ruta local** | El PBIP abre aquí sin tocar nada. Publica el nombre de cuenta `<USUARIO>` y una ruta que no existe en otros equipos |
| **B — Revertir al marcador neutro antes del PR** | Repositorio portátil y sin ruta personal. Quien clone debe configurar `RutaCSV` antes de abrir |

Recomendación: **ejecutar primero la Fase 7 con la opción A**, y aplicar B
inmediatamente antes de abrir el PR. Así la generación del PBIX se hace sobre un
proyecto que carga, y el repositorio queda portátil.

Valor a usar en la opción B (**una sola** barra invertida):

```
expression RutaCSV = "C:\path\to\steel-plates-quality-mlops\data\raw\steel_plates_faults.csv"
```

La prueba acepta ese valor sin ningún otro cambio. Instrucciones para terceros
en [`POWERBI_SECURITY_PORTABILITY.md`](POWERBI_SECURITY_PORTABILITY.md) §3.1.

## 6. Preparación del Pull Request

PRODUCCIÓN **no** ha hecho push ni abierto PR: no hay remoto configurado en el
repositorio local y no hay autorización de escritura.

```powershell
Set-Location "<REPO>"

# Parche revisable, generado fuera del arbol de trabajo
git format-patch main --stdout > "..\powerbi-canonical-naming.patch"

# Si OWNER autoriza publicar la rama
git remote add origin https://github.com/jesusrlgonzalez/steel-plates-quality-mlops.git
git fetch origin main
git push -u origin fix/powerbi-canonical-naming-pbix
```

Atención al hacer push: la rama local se construyó sobre un `git init` propio,
no sobre un clon de `origin/main`. Su historia **no** comparte ancestro con
`origin/main` (`e19cd1af`). Para un PR limpio hay dos vías:

1. Clonar el repositorio, crear la rama sobre `origin/main` y aplicar
   `C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\powerbi-canonical-naming.patch` con
   `git am`. **Vía recomendada.**
2. Hacer push de la rama sin ancestro común, lo que produce un PR ilegible.

El PR debe relacionarse con las incidencias **#1** y **#2** y, dado que ninguna
puede cerrarse aún, enlazarlas sin usar palabras clave de cierre automático
(escribir `refs #1`, no `closes #1`).

Contenido mínimo del PR:

- resumen del renombrado y de la corrección de `RutaCSV`;
- los tres hallazgos del apartado 2;
- resultados de regresión (151 / 5 / 77);
- hashes del [`POWERBI_RELEASE_MANIFEST.md`](POWERBI_RELEASE_MANIFEST.md);
- declaración de que G2–G7 **no** están validados y el PBIX **no** existe;
- capturas **auténticas** de Desktop, una vez ejecutada la Fase 7;
- riesgos residuales y procedimiento de reversión.

## 7. Riesgos residuales

| # | Riesgo | Mitigación |
|---|---|---|
| 1 | Desktop autodetecta una relación hacia `ML_Holdout` al actualizar, mezclando los 389 con los 1 941 | Paso 10 de [`POWERBI_PBIP_PBIX_INTEGRITY.md`](POWERBI_PBIP_PBIX_INTEGRITY.md) §3.2. Las tres relaciones existentes se llaman `AutoDetected_…`: la autodetección **está activa**. Registrar antes de eliminar |
| 2 | Desktop reescribe archivos cubiertos por `pre_ml_powerbi_hashes.json` y `test_previous_powerbi_preserved` falla | Es el diseño de la prueba. Clasificar cada diff; **no** debilitar la prueba ni borrar la línea base |
| 3 | Se valida la distribución equivocada | Apartado 2.3; comprobar la ruta en el título de Desktop |
| 4 | La tolerancia `1e-12` se "verifica" leyendo una tarjeta redondeada a `0.8147` | Exportar los datos del visual; §3.4 pasos 21–22 |
| 5 | Reejecutar `tools/prepare_ml_powerbi.py` sobre una página ya refinada en Desktop la sobrescribe | No ejecutarlo tras la validación de Desktop |
| 6 | Un `git checkout` reescribe los CSV congelados por `text eol=crlf` | `core.autocrlf=false` fijado; toda reversión termina en verificación SHA256 |
| 7 | Sin `--basetemp`, `pytest` vuelve a dar 27 errores | Reparar la ACL de `Temp\pytest-of-<USUARIO>` o usar siempre `--basetemp` |
| 8 | El puntero LFS apunta a un objeto inexistente: todo clon con LFS activo falla al hacer checkout | Apartado 2.1; decisión de OWNER |

## 8. Próximos pasos

1. **OWNER** revisa esta entrega y decide sobre los tres hallazgos del apartado 2.
2. Cerrar la distribución `Steel_Plates_PowerBI_Lista_Para_Desktop_Local` en Desktop.
3. Ejecutar la Fase 7 siguiendo
   [`POWERBI_PBIP_PBIX_INTEGRITY.md`](POWERBI_PBIP_PBIX_INTEGRITY.md) §3, paso a
   paso, rellenando la plantilla del §4 con resultados reales y capturas
   auténticas. Registrar los fallos explícitamente.
4. Volver a ejecutar `pytest` y la validación estática tras el guardado;
   clasificar el diff originado por Desktop.
5. Calcular el SHA256 del PBIX y completar el manifiesto.
6. Decidir la opción A o B del apartado 5.
7. Preparar el PR según el apartado 6, relacionado con #1 y #2.
8. **OWNER** acepta o rechaza formalmente.

## 9. Declaración final

PRODUCCIÓN ha completado todo el trabajo que no exige la interfaz nativa de
Power BI Desktop, y **no declara** ninguna validación que no haya ejecutado.

El criterio final de la orden —«el trabajo termina cuando el PBIP abre,
actualiza, compila, presenta las métricas esperadas, conserva las páginas
originales y permite generar un PBIX que se puede cerrar y reabrir sin
errores»— **no está cumplido**. Los archivos tienen el nombre correcto y las
rutas resuelven, lo cual, en palabras de la propia orden, no es el final del
trabajo.

Las incidencias **#1** y **#2** permanecen **OPEN**. PRODUCCIÓN no las cerrará.

No se declara el cierre. Se solicita la revisión de OWNER.

Estado: **`READY_FOR_DESKTOP_VALIDATION`**.
