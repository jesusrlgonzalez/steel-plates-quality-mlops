# Expediente de producción Power BI — índice y estado vigente

Estado vigente al 16 nov 2026: **Power BI validado en Desktop 2.156.951.0 y publicado** (PR #9, merge `3a240ad`). PBIX vigente SHA-256 `a37f3743e6107b41eb11c31886cfa6120ebc468e480d361f000104e55bf5bec1` (re-guardado el 16 nov con `RutaCSV` portátil; certificado anterior `91f89ff2…`, ver [POWERBI_PBIX_RESAVE_PORTABLE.md](POWERBI_PBIX_RESAVE_PORTABLE.md)). Power BI Service: **no usado**.

## Documentos vigentes

| Documento | Contenido |
|---|---|
| [POWERBI_PRODUCTION_CLOSEOUT.md](POWERBI_PRODUCTION_CLOSEOUT.md) | Cierre de la producción y puertas G1 a G8 |
| [POWERBI_DESKTOP_RUNTIME_EVIDENCE.md](POWERBI_DESKTOP_RUNTIME_EVIDENCE.md) | Evidencia del motor de Desktop (XMLA, solo lectura) |
| [POWERBI_RECONCILIATION_RESULTS.md](POWERBI_RECONCILIATION_RESULTS.md) | Reconciliación Python ↔ Power BI con diferencia 0 |
| [POWERBI_PBIX_CERTIFICATION.md](POWERBI_PBIX_CERTIFICATION.md) | Certificación original del PBIX (15 nov, `91f89ff2…`) |
| [POWERBI_PBIX_RESAVE_PORTABLE.md](POWERBI_PBIX_RESAVE_PORTABLE.md) | Re-guardado con `RutaCSV` portátil (16 nov, `a37f3743…`), incidencia #2 |
| [POWERBI_SECURITY_PORTABILITY.md](POWERBI_SECURITY_PORTABILITY.md) | Rutas, parámetro portátil y privacidad |
| Resto de `POWERBI_*.md` y `evidence/` | Fases del renombrado, validaciones y scripts de verificación |

## Documentos históricos (superados)

Los `PRODUCTION_*.md` y `PRODUCTION_RELEASE_MANIFEST.json` son la entrega del 14 nov 2026, **anterior** a la validación en Desktop. Llevan un aviso de «superado» y se conservan sin otros cambios como antecedente. Sus estados (`NOT_EXECUTED`, `UNVERIFIED`, `READY_FOR_DESKTOP_VALIDATION`) no describen el estado actual.

`reports/ml/integration/phase10_validation.json` es evidencia congelada de la fase 10; su campo de runtime refleja el estado de esa fecha.
