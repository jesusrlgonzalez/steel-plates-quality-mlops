# Re-guardado del PBIX con `RutaCSV` portátil (incidencia #2)

Autor: Jesús R. L. González · 16 nov 2026 · Power BI Desktop 2.156.951.0 (26.07), en la máquina del OWNER.

## Qué se hizo

1. Se abrió el PBIX certificado (`91f89ff2…`). En el Editor avanzado, `RutaCSV` contenía la ruta de la máquina de validación (`C:\Users\<USUARIO>\<CARPETA_DE_TRABAJO>\…\steel_plates_faults.csv`), sin `meta`.
2. `RutaCSV` se sustituyó por el mismo parámetro portátil que publica el PBIP: `"C:\path\to\steel-plates-quality-mlops\data\raw\steel_plates_faults.csv" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]`. Sintaxis validada por el editor.
3. Para que la actualización sea real y no queden cambios pendientes, esa ruta neutra existe en la máquina con copias byte a byte de los CSV públicos del repositorio (`data/raw/steel_plates_faults.csv`, SHA-256 `ca0e2cbc…`, y `powerbi/data/ml_holdout_evaluation.csv`, `5f5fb946…`).
4. «Cerrar y aplicar» sin errores y sin cambios pendientes; después, actualización completa (esquema y datos) sin errores.
5. Comprobación en pantalla: Final Macro-F1 0,8147, Final Balanced Accuracy 0,8049, Candidate Review Rate 67,10 %, ML Rows 389. Resumen ejecutivo: 1,941 defectos y COPQ 2.242.600,00 MXN.
6. Guardado desde Desktop («Guardar como», sin edición de bytes).

## Artefacto

| Campo | Valor |
|---|---|
| Archivo | `powerbi/artifacts/steel-plates-quality-mlops-powerbi.pbix` |
| Tamaño | 257,711 bytes |
| SHA-256 | `a37f3743e6107b41eb11c31886cfa6120ebc468e480d361f000104e55bf5bec1` |
| Paquete ZIP | 64 entradas, `testzip` sin errores |
| Modelo (descomprimido con pbixray) | 7 tablas, 34 medidas, 3 relaciones; `Fact_Defecto` 1,941 filas y `ML_Holdout` 389 |
| Expresión activa `RutaCSV` (tabla `Expression` de los metadatos) | Solo el valor portátil |

## Residuos conocidos dentro del binario

El modelo descomprimido aún contiene dos tipos de bytes con el usuario de Windows de la máquina de validación:

- **Registro de archivos de Analysis Services** (296 apariciones de `C:\Users\<USUARIO>\AppData\Local\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces\…`). Power BI Desktop lo escribe en todo PBIX que guarda; el certificado anterior tenía el mismo registro. No es una fuente de datos ni una ruta del proyecto, y no se puede eliminar desde Desktop.
- **Una copia obsoleta del valor anterior de `RutaCSV`**, en una página libre del almacenamiento interno. No pertenece a ninguna expresión activa: la tabla `Expression` solo contiene el valor portátil. Persistió en un segundo guardado de control (`9e4828b5…`), así que es estructural del formato.

Ninguno es visible al abrir el informe ni influye en la actualización; solo se detectan descomprimiendo el modelo. Para eliminarlos haría falta guardar desde una cuenta de Windows con nombre neutro. Queda como decisión del OWNER.

## Pruebas

- `tests/test_bi_integration.py`: el PBIX vigente es el único aceptado además de la línea base pre-ML congelada.
- El certificado anterior (`91f89ff2…`) queda como antecedente en `POWERBI_PBIX_CERTIFICATION.md`.
