# PRODUCTION BASELINE

> **Documento histórico — SUPERADO.** Describe el estado del 14 nov 2026, previo a la validación en Power BI Desktop. Sus valores `NOT_EXECUTED`, `UNVERIFIED` o `READY_FOR_DESKTOP_VALIDATION` ya no son vigentes. Estado vigente: [POWERBI_PRODUCTION_CLOSEOUT.md](POWERBI_PRODUCTION_CLOSEOUT.md) e [índice](README.md). Se conserva como antecedente.

Fecha de preparación: 2026-11-14. Fuente: ZIP adjunto `steel-plates-quality-mlops-main.zip`. Rama de GitHub consultada: `main`; último commit consultado: `e19cd1af045ea22e4518f3795f9c5070979a924f (remote main; snapshot ZIP commit UNVERIFIED)`. La equivalencia byte a byte entre ZIP y este commit no está demostrada. Autor original: Jesús R. L. González.

## Comprobaciones efectuadas
- Archivo ZIP íntegro (`ZipFile.testzip() = None`); entradas: 383.
- Datos originales: 1941 filas y 35 columnas.
- Exportación ML: 389 filas y 16 columnas.
- Páginas PBIR (definiciones, no render): [{"id": "f50491653678cb19a699", "name": "Control y capacidad", "visuals": 8}, {"id": "5ee9939d0101076d3381", "name": "Resumen ejecutivo ", "visuals": 10}, {"id": "ml_performance_review", "name": "MODEL PERFORMANCE & REVIEW", "visuals": 12}, {"id": "cb973d91eb46886907c2", "name": "Tooltip Pareto", "visuals": 3}, {"id": "1f75dde540a696f2b18f", "name": "Exploracion", "visuals": 13}].
- PBIX en ZIP: Git LFS pointer, no PBIX funcional disponible en este paquete. `git lfs pull` será necesario en un clon autorizado.
- Consultas: `RutaCSV` sustituida **solo en esta copia Windows**; `RutaMLCSV` se deriva de `RutaCSV`.
- Revisión estática: `ML_Holdout` no aparece en `relationships.tmdl`: True.
- Issues GitHub #1 y #2: abiertas al consultarlas el 2026-11-14.
- No se inspeccionó el informe Auditor 2: no adjuntado.

## Limitaciones
Sin Power BI Desktop/Service ni acceso a la ruta Windows. Sin repositorio `.git` en el ZIP: no se puede demostrar el commit de origen ni generar un diff Git real de esa extracción. Este ZIP no constituye una release ni un informe validado de Desktop.
