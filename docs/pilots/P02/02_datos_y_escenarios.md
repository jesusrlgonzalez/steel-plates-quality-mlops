# P02 · Manifiesto de datos, reglas de imperfección y escenarios

## 1. Fuentes y separación de la evidencia científica

| Fuente | Contenido | Uso |
|---|---|---|
| Predicciones del clasificador real | `examples/review_triage/inspeccion_placas.csv`, filas `validación cruzada`: 1,552 predicciones fuera de muestra, con clase, confianza y clase real | Base del remuestreo |
| Holdout congelado | Las 389 filas `evaluación final` del mismo archivo | **No se lee.** Una prueba comprueba que ninguna placa simulada proviene de ellas |
| Verdad sintética del historial | 20 días desde el 2026-03-02, ~60 placas por día remuestreadas de la base; 30 % revisado al azar dentro de cada decil de confianza | Fuente original conservada; solo sirve para comprobar la conciliación |
| Exportación recibida | La verdad con las reglas D1–D7: [`raw_export_history.csv`](../../../reports/pilots/P02/raw_export_history.csv) (1,218 filas) | Entrada del flujo |
| Días operados | 10 días; cada placa con su clase real oculta, que solo se usa después para calcular costos | Operación simulada |

Cada placa operada lleva `origen = "simulada: remuestreo de predicción fuera de muestra (validación cruzada)"` y `fila_base`, su fila de origen. Así las predicciones simuladas se distinguen de las salidas del clasificador real.

Semillas: historial 3, imperfecciones del historial 21, operación 4, imperfecciones de operación 31. Conteos por escenario: [`manifest.json`](../../../reports/pilots/P02/manifest.json).

## 2. Reglas de imperfección

| Regla | Qué simula | Cómo se genera | Filas (historial) | Tratamiento | Cómo se evalúa |
|---|---|---|---|---|---|
| D1 | Placa leída dos veces | Copia exacta del 3 % | 35 | Se conserva una lectura por `id_placa` | Ids únicos y tantas placas como la verdad |
| D2 | Confianza ausente | Vacía en el 5 % | 59 | Información insuficiente: la placa nunca se acepta sola; va a revisión humana o queda retenida | Marcadas exactamente las afectadas |
| D3 | Escala mezclada | La línea B reporta de 0 a 100 desde el día 8 | 343 | Se divide entre 100 cuando la mayoría de una línea en un día es > 1 | Confianza conciliada = verdad (±0.00005) |
| D4 | Nomenclatura inconsistente | 10 % con variantes (`Z-Scratch`, `K_Scratch`, `Rayón K`, `OTRAS_FALLAS`, `Golpes`…) | 118 | Catálogo de las 7 clases; lo desconocido va a revisión humana | Clase conciliada = verdad |
| D5 | Revisiones abiertas | Clase real vacía en las revisiones de los 3 últimos días del historial | 54 | No se usan para fijar los cortes | Ninguna en el ajuste |
| D6 | Retraso de captura | 4 % llega un día después | 47 | Se decide el día en que se captura y cuenta contra el cupo de ese día | Retraso de un día exacto, fecha de inspección intacta |
| D7 | Errores de integración | Confianza 1.7 o ilegible, clase vacía | 6 | Fila excluida con motivo | Ninguna afectada queda válida |

Resultado del historial: 1,218 filas recibidas, 35 duplicados fuera y 1,183 placas. De ellas, 118 nombres corregidos, 343 confianzas reescaladas, 59 sin confianza y 6 inválidas. Las filas no afectadas quedan idénticas a la verdad. Pruebas: `check_reconciliation` y `tests/test_pilot_p02.py`.

## 3. Información futura

Los cortes se fijan con revisiones cerradas de los días 1 a 17 del historial. Los días con revisión abierta y los días operados no entran. Los umbrales del monitor (PSI de confianza y de mezcla de clases) se calibran solo con esos mismos días: 1.5 × el mayor PSI diario observado, nunca menos de 0.25.

## 4. Escenarios

| Id | Situación | Capacidad diaria | Perturbaciones en los días operados |
|---|---|---|---|
| S1 | Operación normal | 25 | D1 3 %, D2 5 %, D3, D4 10 %, D6 4 %, D7 2 filas |
| S2 | Inspectores reducidos a la mitad y registros más incompletos | 12 | D1 6 %, D2 10 %, D3, D4 15 %, D6 8 %, D7 2 filas |
| S3 | Límites | 25 | Las de S1, y además: el triple de placas `Bumps` (días 3–5); una clase nueva `Inclusion` (días 2 y 9); confianza inflada c^0.25 (días 7–8); 15 % de filas ilegibles (día 10) |

## 5. Reglas de decisión de cada día

1. Conciliar las placas capturadas ese día.
2. Suspender la aceptación automática si más del 10 % de las filas son inválidas o si el PSI de confianza o de mezcla supera su umbral calibrado. En un día suspendido se revisa por orden de llegada.
3. Primero, siempre a revisión humana: clases desconocidas y placas sin confianza. Si no hay cupo, quedan **retenidas**.
4. Después, según la política:
   - **Revisar todas:** por orden de llegada.
   - **Umbral único:** lo que queda bajo el corte único, por orden de llegada.
   - **Priorizada:** lo que queda bajo el corte de su clase, de mayor a menor distancia al corte.
5. Lo que debía revisarse y no cupo sale con su clase como **liberada_sin_cupo** y genera un aviso al supervisor. El resto se acepta.

Cada decisión queda en [`decisions.csv`](../../../reports/pilots/P02/decisions.csv) con escenario, política, día, placa, línea, fecha, clase, confianza, decisión, motivo, identificador de cortes, origen y costo del error.

## 6. Costos

| Concepto | Valor | Uso |
|---|---|---|
| Revisión | MXN 40 | Ajuste y evaluación |
| Escape único | MXN 1,500 | Solo para ajustar los cortes; `review_policy` no se modifica |
| Matriz de error | 150 si la clase asignada lleva a la misma disposición; 1,500 si lleva a otra; 6,000 si la real es `Bumps` u `Other_Faults` | Solo para evaluar. No cambia la optimización |
