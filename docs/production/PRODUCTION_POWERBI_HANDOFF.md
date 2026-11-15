# PRODUCTION POWERBI HANDOFF

> **SUPERSEDED — no seguir las rutas de este documento.**
> OWNER-PBI-REN-001 (Fase 2) renombró el componente Power BI al nombre canónico
> `steel-plates-quality-mlops-powerbi`. Las rutas con `steel-plates-quality-bi`
> que aparecen más abajo **ya no existen**. Este documento se conserva como acta
> histórica de la preparación del 2026-11-14.
>
> Procedimiento vigente: [`POWERBI_PRODUCTION_HANDOFF_TO_OWNER.md`](POWERBI_PRODUCTION_HANDOFF_TO_OWNER.md)
> y [`POWERBI_PBIP_PBIX_INTEGRITY.md`](POWERBI_PBIP_PBIX_INTEGRITY.md).
>
> Corrección sobre el apartado siguiente: la equivalencia ZIP ↔ commit
> `e19cd1af`, aquí marcada como `UNVERIFIED`, **quedó demostrada** en
> [`POWERBI_RENAME_BASELINE.md`](POWERBI_RENAME_BASELINE.md) §3.

Fecha de preparación: 2026-11-14. Fuente: ZIP adjunto `steel-plates-quality-mlops-main.zip`. Rama de GitHub consultada: `main`; último commit consultado: `e19cd1af045ea22e4518f3795f9c5070979a924f (remote main; snapshot ZIP commit UNVERIFIED)`. La equivalencia byte a byte entre ZIP y este commit no está demostrada. Autor original: Jesús R. L. González.

## Ruta de esta distribución
Extraer el contenido del ZIP en `C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>` manteniendo la carpeta `steel-plates-quality-mlops`.

Abrir: `C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\steel-plates-quality-mlops\powerbi\project\steel-plates-quality-bi.pbip`.

Power Query > Transformar datos > Editor avanzado (en la consulta/expresión `RutaCSV`): usar la ruta literal:

`C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\steel-plates-quality-mlops\data\raw\steel_plates_faults.csv`

La copia PBIP ya tiene `RutaCSV` configurada para esa ruta. `RutaMLCSV` se calcula derivando la raíz del repositorio. Si la carpeta se extrajo en otra ubicación, actualizar `RutaCSV` manualmente.

## Validaciones obligatorias en Windows
1. Abrir PBIP en Power BI Desktop compatible y registrar versión. NO abrir el PBIX puntero LFS.
2. Verificar consulta `RutaCSV`, actualización de Power Query, 1.941 filas originales y 389 ML_Holdout.
3. Verificar relaciones estrella y que ML_Holdout no esté relacionada; DAX sin errores.
4. Comprobar 5 páginas y en `MODEL PERFORMANCE & REVIEW` 4 tarjetas, 3 filtros, 4 tablas y 1 nota.
5. Reconciliar contra `docs/evidence/powerbi_ml_reconciliation.md` y `docs/production/PRODUCTION_RECONCILIATION.md`.
6. Guardar PBIP; `Guardar como` PBIX mediante Desktop y reabrir ambos; generar capturas auténticas.
7. Calcular `Get-FileHash -Algorithm SHA256` para PBIX real y registrar versión Desktop.
8. Si utiliza Git clone completo, ejecutar `git lfs install`, `git lfs pull` antes de comparar PBIX anterior; nunca reescribir bytes PBIX manualmente.

Estado actual: `READY_FOR_DESKTOP_VALIDATION` significa proyecto preparado para pruebas nativas, NO `DESKTOP_VALIDATED`.
