# Piloto P02 · Revisión humana de la clasificación de defectos con inspectores limitados

**Versión `P02-v1.0.0` (release del repositorio `v1.6.0`) · Nivel A (demostración operativa reproducible) · empresa ficticia · flujo operativo sintético · sin piloto real.**

Capa operativa sobre activos ya validados del proyecto:
- el clasificador congelado de 7 tipos de defecto;
- la política de revisión humana del MVP (`review_policy`).

Ninguno de los dos se modifica ni se reevalúa. El alcance es clasificar defectos ya detectados; no hay detección temprana ni prevención.

## Recorrido para reclutadores (5 minutos)

1. [Ficha ejecutiva](00_ficha_ejecutiva.md).
2. [Resultados](03_resultados.md): tres políticas, tres escenarios y sensibilidad.
3. Código: [`src/quality_ml/pilot_p02.py`](../../../src/quality_ml/pilot_p02.py). Pruebas: [`tests/test_pilot_p02.py`](../../../tests/test_pilot_p02.py).
4. [Dictamen y constancia](04_dictamen.md).

Competencias: separación entre evidencia científica y simulación, gobierno de datos imperfectos, decisión por costo con restricción de capacidad, monitoreo con umbrales calibrados sin datos futuros, sensibilidad con incertidumbre, trazabilidad y regeneración determinista en CI.

## Recorrido empresarial

1. [Caso empresarial](01_caso_empresarial.md): encargo, decisiones, preguntas de descubrimiento y criterios previos.
2. [Datos y escenarios](02_datos_y_escenarios.md): qué datos se necesitan, qué errores llegan y cómo se decide cada día.
3. [Resultados](03_resultados.md): cuándo conviene y cuándo no.
4. [Condiciones para un piloto real](04_dictamen.md#5-condiciones-para-un-piloto-real-nivel-b).

## Reproducir

```bash
pip install -r requirements-dev.txt
python -B -m quality_ml.pilot_p02
python -B -m pytest -q tests/test_pilot_p02.py
```

Salidas en [`reports/pilots/P02/`](../../../reports/pilots/P02/):
- `manifest.json`: reglas de imperfección y conteos;
- `raw_export_history.csv`: exportación con errores;
- `decisions.csv`: bitácora de decisiones;
- `results.json`: resultados por escenario;
- `sensitivity.csv`: sensibilidad;
- `seguimiento_revision.csv`: exportación para Power BI;
- `evidence.json`: SHA-256 de salidas, código y fuente.
