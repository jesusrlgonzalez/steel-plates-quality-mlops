# P02 · Ficha ejecutiva: qué placas defectuosas revisa una persona cada día

**Nivel A, demostración operativa reproducible.** Empresa ficticia, flujo operativo sintético, 10 días simulados. **No existe piloto real (Nivel B).** La clasificación es de defectos ya detectados; no hay detección temprana, prevención ni identificación de causas.

**Problema.** Una planta ficticia clasifica unas 60 placas defectuosas por día en 7 tipos, pero solo tiene inspectores para revisar 25. Si una placa sale con el tipo equivocado, va al proceso equivocado. Cuando la placa real tiene golpes o una falla especial, eso le cuesta mucho al cliente.

**Qué se hizo.**
- El flujo diario remuestrea predicciones fuera de muestra del clasificador real, sin tocar el holdout.
- Los registros llegan con 7 tipos de error documentados: duplicados, confianza ausente, escala mezclada, nombres inconsistentes, revisiones abiertas, retrasos de captura y filas inválidas.
- Cada día se decide qué revisa una persona **sin pasarse del cupo**. Lo desconocido o sin confianza nunca sale solo, y la aceptación automática se suspende cuando los datos o la confianza cambian.

**Resultado de escenario** (MXN de escenario; no es un beneficio real). Ahorro de la política priorizada frente a revisar por orden de llegada, en 10 días, con intervalo del 90 %:

| Escenario | Ahorro | Placas mal clasificadas que salieron: priorizada / orden de llegada |
|---|---|---|
| Normal, 25 inspecciones al día | 228,150 (172,650 a 287,295) | 33 / 84 |
| Inspectores a la mitad | 74,850 (26,850 a 128,850) | 93 / 109 |
| Clase nueva, confianza descalibrada, datos inválidos | 148,500 (87,000 a 210,000) | 50 / 80 |

**Cuándo conviene y cuándo no.**
- Conviene cuando los inspectores no alcanzan y un error cuesta bastante más que una revisión.
- Si alcanza para revisarlo todo, o si la confianza deja de estar calibrada, no aporta nada frente a revisar todo.

**Límites visibles.**
- El monitor **no detectó** un cambio de mezcla (triple de `Bumps`).
- Los costos son supuestos.
- La página de Power BI se añadió en `v1.7.0`, validada en Power BI Desktop ([evidencia](../../production/POWERBI_P02_REVIEW_PAGE.md)). En `v1.6.0` solo existía la exportación `seguimiento_revision.csv`.

**Dictamen:** demostración aprobada con reservas, exclusivamente en Nivel A (autoevaluación). Detalle en [04_dictamen.md](04_dictamen.md).

**Evidencia científica, aparte.** El modelo congelado se evaluó una sola vez en 389 placas: macro-F1 0.8147, exactitud balanceada 0.8049 ([`MODEL_CARD.md`](../../../MODEL_CARD.md)). Ese resultado no cambia ni se atribuye a este escenario.
