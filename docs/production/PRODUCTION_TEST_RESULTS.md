# PRODUCTION TEST RESULTS

> **Documento histórico — SUPERADO.** Describe el estado del 14 nov 2026, previo a la validación en Power BI Desktop. Sus valores `NOT_EXECUTED`, `UNVERIFIED` o `READY_FOR_DESKTOP_VALIDATION` ya no son vigentes. Estado vigente: [POWERBI_PRODUCTION_CLOSEOUT.md](POWERBI_PRODUCTION_CLOSEOUT.md) e [índice](README.md). Se conserva como antecedente.

Fecha de preparación: 2026-11-14. Fuente: ZIP adjunto `steel-plates-quality-mlops-main.zip`. Rama de GitHub consultada: `main`; último commit consultado: `e19cd1af045ea22e4518f3795f9c5070979a924f (remote main; snapshot ZIP commit UNVERIFIED)`. La equivalencia byte a byte entre ZIP y este commit no está demostrada. Autor original: Jesús R. L. González.

Entorno: Linux, Python 3.13.5; dependencias de `requirements-dev.txt` no instaladas integralmente. Comandos ejecutados desde la raíz del ZIP extraído antes de añadir la configuración local:

| Comando | Resultado | Evidencia/causa |
|---|---|---|
| `python -B -m tools.project_checks lint` | PASS | Python AST syntax; 60 archivos (no Ruff) |
| `python -B -m tools.project_checks validate-data` | PASS | 1.941 filas; 27 features |
| `python -B -m tools.project_checks validate-artifact` | BLOCKED/FAIL | `ValueError: Unsupported serialized-model runtime: scikit-learn` |
| `python -B -m tools.project_checks batch-smoke` | BLOCKED/FAIL | Mismo error de runtime |
| `python -B -m tools.project_checks validate-evidence` | BLOCKED/FAIL | Mismo error de runtime |
| `python -B -m pytest -q` | COLLECTION ERROR | faltan `streamlit` y `duckdb`; 2 errores, 2 skipped |

No se reejecutó evaluación final ni se alteraron hashes científicos. Repetir en Python compatible con las versiones fijadas en requirements después de instalar las dependencias. No se validaron Docker, dbt ni ONNX por completo.
