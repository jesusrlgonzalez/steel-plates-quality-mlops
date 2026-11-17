# Expediente de producción Power BI — índice y estado vigente

Estado vigente al 16 nov 2026: **Power BI validado en Desktop 2.156.951.0 y publicado** (PR #9, merge `3a240ad`). PBIX vigente SHA-256 `a48291e59dfdc4d6b57da11b9c0280c60bfb48fcbab4f4533cacf0ddfc9435f4` (17 nov, con la página P02 validada en Desktop, ver [POWERBI_P02_REVIEW_PAGE.md](POWERBI_P02_REVIEW_PAGE.md); anteriores `a37f3743…` y `91f89ff2…`). Power BI Service: **no usado**.

## Documentos vigentes

| Documento | Contenido |
|---|---|
| [POWERBI_PRODUCTION_CLOSEOUT.md](POWERBI_PRODUCTION_CLOSEOUT.md) | Cierre de la producción y puertas G1 a G8 |
| [POWERBI_DESKTOP_RUNTIME_EVIDENCE.md](POWERBI_DESKTOP_RUNTIME_EVIDENCE.md) | Evidencia del motor de Desktop (XMLA, solo lectura) |
| [POWERBI_RECONCILIATION_RESULTS.md](POWERBI_RECONCILIATION_RESULTS.md) | Reconciliación Python ↔ Power BI con diferencia 0 |
| [POWERBI_PBIX_CERTIFICATION.md](POWERBI_PBIX_CERTIFICATION.md) | Certificación original del PBIX (15 nov, `91f89ff2…`) |
| [POWERBI_PBIX_RESAVE_PORTABLE.md](POWERBI_PBIX_RESAVE_PORTABLE.md) | Re-guardado con `RutaCSV` portátil (16 nov, `a37f3743…`), incidencia #2 |
| [POWERBI_P02_REVIEW_PAGE.md](POWERBI_P02_REVIEW_PAGE.md) | Página P02 de revisión humana validada en Desktop (17 nov, `a48291e5…`), reserva R3 |
| [POWERBI_SECURITY_PORTABILITY.md](POWERBI_SECURITY_PORTABILITY.md) | Rutas, parámetro portátil y privacidad |
| Resto de `POWERBI_*.md` y `evidence/` | Fases del renombrado, validaciones y scripts de verificación |

## Documentos históricos (superados)

Los `PRODUCTION_*.md` y `PRODUCTION_RELEASE_MANIFEST.json` son la entrega del 14 nov 2026, **anterior** a la validación en Desktop. Llevan un aviso de «superado» y se conservan sin otros cambios como antecedente. Sus estados (`NOT_EXECUTED`, `UNVERIFIED`, `READY_FOR_DESKTOP_VALIDATION`) no describen el estado actual.

`reports/ml/integration/phase10_validation.json` es evidencia congelada de la fase 10; su campo de runtime refleja el estado de esa fecha.
