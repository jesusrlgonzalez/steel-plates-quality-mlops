# P02 · Resultados de escenario

**Todo lo de esta página es resultado de escenario sintético**: una empresa ficticia, 10 días operados, cifras en MXN de escenario. No son beneficios observados en una planta. Tampoco es el desempeño del modelo: ese se midió una sola vez en el holdout de 389 placas (macro-F1 0.8147, exactitud balanceada 0.8049; [`MODEL_CARD.md`](../../../MODEL_CARD.md)) y no se toca aquí.

Las cifras salen de [`results.json`](../../../reports/pilots/P02/results.json). Una prueba automática comprueba que las de costo coincidan con ese archivo.

## Cortes elegidos

`review_policy` fija los cortes con 956 placas de los días 1 a 17 del historial, todas con revisión cerrada. Su identificador, `f0ee8d6c140f`, aparece en cada fila de la bitácora.

| Clase | Pastry | Z_Scratch | K_Scatch | Stains | Dirtiness | Bumps | Other_Faults | Corte único |
|---|---|---|---|---|---|---|---|---|
| Confianza mínima para aceptar | 0.802 | 0.892 | 0.798 | 0.837 | 0.874 | 0.905 | 0.860 | 0.882 |

## Comparación de las tres políticas (10 días)

El costo suma MXN 40 por placa revisada y la matriz de costo por cada placa que sale mal clasificada: 150, 1,500 o 6,000. El ahorro de la política priorizada se da con su intervalo bootstrap del 90 % por días.

| | S1 Referencia (cupo 25) | S2 Inspectores a la mitad (cupo 12) | S3 Límites (cupo 25) |
|---|---|---|---|
| Placas válidas | 608 | 608 | 605 |
| Costo: revisar todas (por orden de llegada) | 431,650 | 573,300 | 427,000 |
| Costo: umbral único | 364,150 | 549,300 | 412,000 |
| Costo: priorizada con capacidad | 203,500 | 498,450 | 278,500 |
| **Ahorro de la priorizada frente a revisar todas** | **228,150** (172,650 a 287,295) | **74,850** (26,850 a 128,850) | **148,500** (87,000 a 210,000) |
| Ahorro de la priorizada frente al umbral único | 160,650 (102,000 a 220,500) | 50,850 (5,700 a 101,857.5) | 133,500 (79,500 a 190,500) |
| Placas mal clasificadas que salieron (todas / único / priorizada) | 84 / 69 / 33 | 109 / 105 / 93 | 80 / 76 / 50 |
| De ellas, severas (`Bumps` u `Other_Faults` reales) | 66 / 56 / 32 | 90 / 86 / 79 | 66 / 64 / 43 |
| Revisiones por política | 250 | 120 | 250 |
| Días con aceptación automática suspendida | 0 | 0 | 3 |
| Máximo de revisiones en un día | 25 | 12 | 25 |

Lectura:

- **Las tres políticas usan todo el cupo.** La diferencia está en *qué* placas revisan. La priorizada manda primero las de confianza más baja respecto al corte de su clase, y así deja salir menos clasificaciones equivocadas con el mismo número de inspectores.
- **S2:** con 12 inspectores las tres dejan salir muchas placas sin revisar. La ventaja frente al umbral único se reduce: su límite inferior es 5,700.
- **S3:**
  - Las placas de la clase nueva `Inclusion` siempre fueron a revisión humana.
  - Los días 7 y 8, con la confianza inflada, se suspendieron por cambio en su distribución (PSI 3.88 y 5.26). El día 10 se suspendió por 15 % de filas inválidas.
  - **El cambio de mezcla (el triple de placas `Bumps` en los días 3 a 5) no se detectó**: su PSI de mezcla (0.07, 0.16 y 0.09) quedó bajo el umbral calibrado de 0.38.

## Sensibilidad

[`sensitivity.csv`](../../../reports/pilots/P02/sensitivity.csv) cubre 21 combinaciones:
- capacidad de 8 a 35 por día, y sin límite;
- costo de los errores × 0.25, × 1 y × 4;
- confianza descalibrada en todos los días.

| Condición | Frente a revisar todas | Frente al umbral único |
|---|---|---|
| Capacidad 8 a 35, costo de errores × 1 o × 4 | Conviene | Conviene |
| Capacidad 8 a 25, costo × 0.25 | Conviene | Conviene |
| Capacidad 35, costo × 0.25 | Conviene | **Indiferente**: hay inspectores para casi todo lo dudoso |
| Sin límite de inspectores | Costo × 0.25 o × 1: **indiferente** (−4,180 y −920), porque revisar todo cuesta lo mismo o menos. Costo × 4: conviene por solo 3,760 | Indiferente (× 0.25); conviene por solo 440 (× 1) y 200 (× 4) |
| Confianza descalibrada todos los días | **Indiferente** (0): se suspenden los 10 días y el sistema no aporta nada; tampoco empeora | Indiferente |

Conclusión económica: la priorización conviene **cuando el cupo de inspectores es escaso** y los errores cuestan bastante más que una revisión. Si alcanza para revisarlo todo, o si la confianza deja de estar calibrada, no aporta nada frente a revisar todo.

## Reproducir

```bash
pip install -r requirements-dev.txt
python -B -m quality_ml.pilot_p02        # regenera reports/pilots/P02/
python -B -m pytest -q tests/test_pilot_p02.py
```

CI regenera las salidas en cada cambio y falla si difieren de las publicadas. [`evidence.json`](../../../reports/pilots/P02/evidence.json) guarda el SHA-256 de cada salida, del código y del archivo fuente de predicciones.
