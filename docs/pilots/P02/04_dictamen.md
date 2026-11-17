# P02 · Dictamen y constancia interna

**Dictamen: DEMOSTRACIÓN APROBADA CON RESERVAS, exclusivamente en Nivel A.** La revisión la hizo el propio autor: es una **autoevaluación**, no una auditoría independiente.

> **Alcance.** Es una demostración operativa reproducible con un flujo sintético. **No** equivale a:
> - certificación independiente;
> - validación en una planta real;
> - autorización de uso industrial.
>
> No se atribuye a P02 detección temprana, prevención ni identificación de causas. La aceptación formal del OWNER es un acto posterior a la publicación y se registra fuera de este expediente.

## 1. Puertas

| Puerta | Estado | Evidencia |
|---|---|---|
| G0 Definición del problema | PASS | [01_caso_empresarial.md](01_caso_empresarial.md), criterios C1–C11 en el commit `86130681b78bad0cef27c53d839225fd06e7e6f4`, publicado antes del código |
| G1 Datos y contratos | PASS | D1–D7 comprobadas contra la verdad sintética (C1); revisiones abiertas fuera del ajuste (C2) |
| G2 Validación científica | PASS | El holdout no se lee (C4). Modelo, métricas, `ml_holdout_evaluation.csv` y el PBIX certificado sin cambios; las pruebas existentes lo verifican |
| G3 Integración operativa | PASS con reserva | Cupo estricto (C3), revisión humana obligatoria para lo desconocido o incompleto, suspensión, bitácora (C8) y costos recalculables (C9). Power BI: exportación y pruebas; página **no ejecutada** (R3) |
| G4 Escenarios y robustez | PASS con reservas | S1–S3 y 21 combinaciones de sensibilidad. Reservas R1 y R2 |
| G5 Auditoría y expediente | PASS (autoevaluación) | Este expediente |
| G6 Publicación verificable | PASS | Versión del repositorio `v1.6.0` (`P02-v1.0.0`). Integración por PR con los 4 checks obligatorios; las salidas se regeneran idénticas en CI; el release incluye `p02-evidence-v1.6.0.zip`, verificado por `tests/test_release_p02.py` |

## 2. Criterios

| Id | Resultado | Fuente |
|---|---|---|
| C1 Imperfecciones | PASS: 7 de 7 reglas; las filas no afectadas quedan idénticas | `test_c1_*` |
| C2 Sin información futura | PASS: cortes con días 1–17; monitor calibrado con los mismos días | `test_c2_*` |
| C3 Cupo | PASS: máximo 25, 12 y 25 revisiones por día | `test_c3_*` |
| C4 Separación científica | PASS: 0 placas simuladas del holdout; todas marcadas como simuladas | `test_c4_*` |
| C5 Referencia: ahorro frente a revisar todas, límite inferior > 0 | PASS: 172,650 | [03_resultados.md](03_resultados.md) |
| C6 Adversa: priorizada ≤ umbral único | PASS: 498,450 frente a 549,300 | [03_resultados.md](03_resultados.md) |
| C7 Límites | PASS: 0 placas de clase nueva liberadas; suspendidos los días con confianza descalibrada (2 de 2) y con datos inválidos (1 de 1). El cambio de mezcla se detectó 0 de 3 veces (R1) | `test_c7_*` |
| C8 Trazabilidad y regeneración | PASS | `test_c8_*`, `evidence.json`, paso de CI |
| C9 Consistencia económica | PASS: los costos se recalculan desde la bitácora | `test_c9_*` |
| C10 Power BI | Exportación y conciliación: PASS. Página en Desktop: **NO EJECUTADO** | `test_c10_*` |
| C11 Sin atribución indebida | PASS (revisión manual) | Ficha y resultados |

Sin incidencias críticas.

## 3. Reservas

- **R1 El cambio de mezcla no se detecta.** El triple de `Bumps` en los días 3–5 de S3 no superó el umbral del PSI de mezcla (0.38), calibrado con el historial. Con ~60 placas por día el PSI diario es ruidoso. Antes de un piloto real: ventanas de varios días o pruebas por clase.
- **R2 Costos y flujo del mismo autor.** La matriz de costos, el remuestreo y las políticas son supuestos. Las cifras no anticipan el efecto en una planta.
- **R3 Página de Power BI no construida.** La exportación cumple el esquema de `revision_humana.dax` y concilia con la bitácora. La página **MODEL PERFORMANCE & REVIEW** requiere:
  - construirla en una copia versionada;
  - validarla en Power BI Desktop;
  - un nuevo SHA-256 del PBIX y la actualización controlada de `test_bi_integration.py`.
- **R4 Un solo costo de escape en el ajuste.** Los cortes se optimizan con MXN 1,500 y se evalúan con la matriz. Optimizar con la matriz sería una extensión del algoritmo con versión y pruebas propias.
- **R5 Decisiones humanas simuladas.** El inspector corrige siempre la clase de lo que revisa; lo liberado sin cupo no se recupera.

## 4. Constancia Interna de Demostración Verificada

| Campo | Valor |
|---|---|
| Proyecto | `steel-plates-quality-mlops` · Piloto P02, revisión humana de la clasificación de defectos con inspectores limitados |
| Versión | `P02-v1.0.0`, en el release del repositorio `v1.6.0` |
| Código evaluado | `src/quality_ml/pilot_p02.py` y `review_policy.py`, con SHA-256 en `reports/pilots/P02/evidence.json` |
| Fecha | 2026-11-17 |
| Pruebas | Piloto: 11 de 11; suite completa en CI |
| Resultado | Demostración aprobada con reservas R1–R5 |
| Naturaleza | **Autoevaluación del autor.** No es certificación externa, validación empresarial independiente ni acreditación de producción |

## 5. Condiciones para un piloto real (Nivel B)

1. Una planta con autorización, un responsable identificado y criterios aprobados por escrito.
2. Exportación real del sistema de inspección con confianza por placa, y una muestra revisada al azar por banda (protocolo de [`docs/MVP_PILOTO.md`](../../MVP_PILOTO.md)).
3. Una matriz de costos validada por el cliente. Resolver R1 antes de empezar.
4. Operación vigilada de 4 semanas con auditoría de lo aceptado.
