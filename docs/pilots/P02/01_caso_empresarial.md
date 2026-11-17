# P02 · Caso empresarial: revisión humana de la clasificación de defectos con inspectores limitados

**Nivel de validación:** A, demostración operativa reproducible. **Empresa:** ficticia. **Datos operativos:** sintéticos. **Piloto real (Nivel B):** no existe.

## 1. Encargo

**Aceros Laminados del Golfo, S.A.** es una empresa ficticia. Su sistema automático de inspección ya separa las placas defectuosas, y un clasificador asigna a cada una uno de 7 tipos de defecto: `Pastry`, `Z_Scratch`, `K_Scatch`, `Stains`, `Dirtiness`, `Bumps` y `Other_Faults`. Según el tipo, la placa va a una disposición distinta: retrabajo superficial, esmerilado, limpieza, recorte o inspección especial.

La responsable de calidad escribe:

> Clasificamos unas 60 placas defectuosas por día. Tenemos inspectores para revisar 25 y el resto sale con el tipo que dio el sistema. Cuando el tipo está mal, la placa va al proceso equivocado: unas veces es retrabajo perdido; otras, una placa con golpes o una falla especial sale como si fuera una mancha y la reclama el cliente. Necesito saber cuáles mandar a inspección cada día sin pasarme del personal, cuánto me cuesta cada opción y cuándo no debo confiar en la clasificación automática.

## 2. Alcance científico (no cambia)

| Sí | No |
|---|---|
| Clasificar placas **ya identificadas como defectuosas** en 7 tipos existentes | Detectar defectos antes de que ocurran |
| Decidir qué clasificación revisa una persona | Prevenir defectos o identificar sus causas |
| Estimar el costo de las clasificaciones equivocadas con supuestos declarados | Reportar beneficios observados en una planta real |

El modelo, su selección y su evaluación final congelada no se tocan. Esa evaluación se hizo sobre 389 placas, con macro-F1 0.8147 y exactitud balanceada 0.8049 ([`MODEL_CARD.md`](../../../MODEL_CARD.md), [docs/ml/07](../../ml/07_final_holdout_evaluation.md)).

## 3. Información disponible y supuestos

| Concepto | Valor del caso | Origen |
|---|---|---|
| Predicciones del clasificador | Predicciones **fuera de muestra** de validación cruzada sobre las 1,552 placas de entrenamiento de UCI, con clase, confianza y clase real | `examples/review_triage/inspeccion_placas.csv`, filas `validación cruzada`. Las 389 del holdout **no** se usan |
| Flujo diario | Placas **simuladas** por remuestreo de esas predicciones: ~60 por día, 20 días de historial y 10 de operación | Supuesto del caso; cada fila se marca como simulada |
| Muestra revisada del historial | 30 % al azar dentro de cada banda de confianza | Protocolo de [`docs/MVP_PILOTO.md`](../../MVP_PILOTO.md) |
| Capacidad de inspección | 25 placas por día | Supuesto del caso |
| Costo de revisar una placa | MXN 40 | `review_policy.Costos` |
| Costo de una clasificación equivocada que sale sin revisar | Matriz por clase real y clase asignada: MXN 150 si las dos clases van a la misma disposición; 1,500 si van a disposiciones distintas; 6,000 si la placa es `Bumps` u `Other_Faults` y sale como otro tipo | Supuesto del caso, solo para **evaluar** |
| Costo de escape con el que se ajusta la política | MXN 1,500 (único) | `review_policy.Costos`; el algoritmo no se modifica |

## 4. Decisiones de la responsable de calidad

1. Cada día: qué placas revisa una persona y cuáles salen con el tipo del sistema.
2. Cuándo suspender la aceptación automática porque la clasificación dejó de ser confiable.
3. Qué hacer con lo que el sistema no reconoce o con registros incompletos.

## 5. Preguntas de descubrimiento

| Pregunta | Por qué importa | Respuesta en este caso |
|---|---|---|
| ¿La revisión humana se hace sin ver la confianza del sistema? | Evita sesgo en la clase confirmada | Sí |
| ¿La muestra revisada es al azar dentro de cada banda? | Sin eso los pesos no corrigen el sesgo | Sí, 30 % |
| ¿Hay más de una línea o software de inspección? | Escalas y nombres distintos | Dos líneas; la B reporta la confianza de 0 a 100 desde el día 8 |
| ¿Cuánto tarda en cerrarse una revisión? | Define qué revisiones ya se pueden usar | Las de los 3 últimos días del historial siguen abiertas |
| ¿Los registros llegan a tiempo? | Retrasos de captura | Algunos llegan con un día de retraso |
| ¿Qué pasa con lo que no cabe en el cupo? | Restricción dura | Sale con el tipo del sistema y queda marcado para el supervisor |

## 6. Políticas que se comparan

1. **Revisar todas:** se revisa por orden de llegada hasta llenar el cupo; el resto sale con el tipo del sistema.
2. **Umbral único:** un solo corte de confianza para todas las clases (`review_policy`, `by_class=False`). Lo que queda bajo el corte va a revisión por orden de llegada hasta llenar el cupo.
3. **Priorizada con capacidad:** cortes por clase (`review_policy`). Lo que queda bajo su corte se ordena por distancia al corte, de mayor a menor, y se revisa hasta llenar el cupo. Las clases desconocidas y los registros sin confianza van siempre a revisión humana.

## 7. Criterios de aceptación (fijados antes de la implementación y la evaluación)

| Id | Criterio | Cómo se comprueba |
|---|---|---|
| C1 | Cada regla de imperfección del manifiesto se detecta, corrige o excluye como indica el manifiesto | Prueba automática contra la verdad sintética |
| C2 | Los cortes se ajustan solo con revisiones cerradas antes del primer día de operación | Prueba automática |
| C3 | En ningún día, escenario ni política las revisiones humanas superan la capacidad | Prueba automática |
| C4 | El flujo sintético sale solo de predicciones de validación cruzada, cada fila marcada como simulada. El holdout, sus métricas, `ml_holdout_evaluation.csv` y el PBIX certificado no cambian | Prueba automática |
| C5 | Referencia (S1): costo de la política priorizada menor que el de «revisar todas», con límite inferior del intervalo bootstrap 90 % por días mayor que cero. Si no se cumple, el dictamen es «no desplegar» | Reporte de resultados |
| C6 | Inspectores reducidos (S2): costo de la priorizada no mayor que el del umbral único (estimación puntual) | Reporte de resultados |
| C7 | Límites (S3): ninguna clase desconocida se acepta automáticamente; los días con datos inválidos > 10 % o con cambio de confianza detectado suspenden la aceptación automática. La tasa de detección se reporta | Prueba automática y reporte |
| C8 | Cada decisión registra día, placa, clase, confianza, política, decisión, motivo, escenario e identificador de cortes; las salidas se regeneran idénticas | Prueba automática y CI |
| C9 | Los costos reportados coinciden con un recálculo independiente desde la bitácora: revisiones × costo + suma de la matriz sobre lo que salió mal clasificado | Prueba automática |
| C10 | La exportación para Power BI cumple su esquema y concilia con la bitácora. La página de Power BI se declara validada **solo** si se comprobó en Power BI Desktop | Prueba automática; registro de Desktop |
| C11 | Ningún documento presenta resultados sintéticos como beneficios observados ni atribuye a P02 detección temprana, prevención o causas | Revisión manual |

Un incumplimiento de C1–C4 o C7–C9 es incidencia crítica y bloquea la publicación. C5 y C6 deciden entre «conviene probar» y «no desplegar». Sin Desktop, C10 queda como «no ejecutado» en lo que corresponde a la página; nunca como PASS.
