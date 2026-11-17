# Página P02 «SEGUIMIENTO DE REVISIÓN HUMANA» — validación en Power BI Desktop

**Autor:** Jesús R. L. González · **Fecha:** 2026-11-17 · **Autorización:** OWNER, 2026-11-17 (orden A5, A5-D10) · **Cierra:** reserva R3 de P02

Datos **SINTÉTICOS**, Nivel A. Las cifras no son beneficios observados.

## 1. Resultado

La página se construyó en una copia versionada, se abrió, actualizó, revisó y guardó en Power BI Desktop. El PBIX resultante sustituye al certificado anterior.

| Identidad | Valor |
|---|---|
| PBIX vigente | `powerbi/artifacts/steel-plates-quality-mlops-powerbi.pbix` · 274,350 bytes · SHA-256 `a48291e59dfdc4d6b57da11b9c0280c60bfb48fcbab4f4533cacf0ddfc9435f4` |
| PBIX anterior | `a37f3743…5bec1` (supersedido; sigue en el historial y en el release `v1.6.0`) |
| Generador | `tools/prepare_review_powerbi.py` (borrador; tras el guardado en Desktop conserva los archivos guardados) |
| Pruebas | `tests/test_review_powerbi.py`, `tests/test_bi_integration.py` (SHA fijado), `tests/test_pilot_p02.py::test_c10…` |

## 2. Qué se añadió y qué no cambió

- **Añadido:** la tabla `Seguimiento_Revision` (612 filas, 14 columnas, 13 medidas de `powerbi/dax/revision_humana.dax`), la expresión `RutaRevisionCSV` (derivada de `RutaCSV`) y la página `review_tracking` con 15 visuales.
- **Sin cambios:** las páginas certificadas, `ML_Holdout` (389 filas), `Fact_Defecto` (1,941 filas), las 34 medidas previas y las 3 relaciones. El modelo guardado no tiene tablas de fechas automáticas ni relaciones nuevas (`fecha_corte` es texto ISO por esa razón).
- **Fuera del commit:** el nodo nuevo que Desktop añade a `diagramLayout.json` (solo posición en la vista de modelo). Se conserva el archivo certificado y Desktop lo vuelve a colocar al abrir.

## 3. Conciliación en Desktop (motor en vivo)

| Comprobación | Desktop | Exportación Python |
|---|---|---|
| Totales (todos los escenarios) | 5,463 piezas · 1,860 a revisión · 34.0% · 699 errores en aceptadas · 194.0 escapes/1000 · costo 3.74 M MXN | Idénticos |
| S1 · priorizada | 608 · 250 · 41.1% · 33 · 92.2 · costo 203,500 (revisión 10,000 + escapes 193,500) | Idénticos |
| S3 · priorizada | costo 278,500; cortes suspendidos los días 7, 8 y 10 | Idénticos (`test_c7`, `test_c10`) |
| Semáforo de escapes | rojo el 03-26 y el 03-28 | — |
| Páginas previas | ML 0.8147 / 0.8049 / 67.10% / 389; Resumen 1,941 defectos, COPQ 2,242,600.00 | Sin cambios |

## 4. Incidencias halladas al validar en Desktop

1. Una medida `Piezas` con el mismo nombre que la columna `piezas`: Desktop la rechaza. Se renombró a `Piezas Totales`, con guarda en el generador y prueba.
2. La exportación agrupaba por fecha de inspección y un registro tardío heredaba la suspensión del día siguiente. Ahora agrupa por día de decisión; la prueba `test_c10` lo verifica.
3. Una columna de fecha hizo que Desktop añadiera tablas de fechas automáticas y una relación. `fecha_corte` pasó a texto ISO; el guardado final no las tiene.

## 5. Naturaleza

Autoevaluación del autor. La validación en Desktop se hizo en el equipo del OWNER; Power BI Service no se usó.
