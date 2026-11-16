# Expediente de producción Power BI — índice y estado vigente

Estado vigente al 16 nov 2026: **Power BI validado en Desktop 2.156.951.0 y publicado** (PR #9, merge `3a240ad`). PBIX certificado SHA-256 `91f89ff2d8ce7605e9b54d9c2c45a6d5cf2511649498e9c70ed82abfe7d86260`. Power BI Service: **no usado**. Incidencia abierta: #2, porque el binario del PBIX aún guarda internamente la ruta de la máquina de validación.

## Documentos vigentes

| Documento | Contenido |
|---|---|
| [POWERBI_PRODUCTION_CLOSEOUT.md](POWERBI_PRODUCTION_CLOSEOUT.md) | Cierre de la producción y puertas G1 a G8 |
| [POWERBI_DESKTOP_RUNTIME_EVIDENCE.md](POWERBI_DESKTOP_RUNTIME_EVIDENCE.md) | Evidencia del motor de Desktop (XMLA, solo lectura) |
| [POWERBI_RECONCILIATION_RESULTS.md](POWERBI_RECONCILIATION_RESULTS.md) | Reconciliación Python ↔ Power BI con diferencia 0 |
| [POWERBI_PBIX_CERTIFICATION.md](POWERBI_PBIX_CERTIFICATION.md) | Guardado, reapertura y hash del PBIX |
| [POWERBI_SECURITY_PORTABILITY.md](POWERBI_SECURITY_PORTABILITY.md) | Rutas, parámetro portátil y privacidad |
| Resto de `POWERBI_*.md` y `evidence/` | Fases del renombrado, validaciones y scripts de verificación |

## Documentos históricos (superados)

Los `PRODUCTION_*.md` y `PRODUCTION_RELEASE_MANIFEST.json` son la entrega del 14 nov 2026, **anterior** a la validación en Desktop. Llevan un aviso de «superado» y se conservan sin otros cambios como antecedente. Sus estados (`NOT_EXECUTED`, `UNVERIFIED`, `READY_FOR_DESKTOP_VALIDATION`) no describen el estado actual.

`reports/ml/integration/phase10_validation.json` es evidencia congelada de la fase 10; su campo de runtime refleja el estado de esa fecha.
