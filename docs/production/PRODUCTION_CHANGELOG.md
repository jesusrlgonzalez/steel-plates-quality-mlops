# PRODUCTION CHANGELOG

> **Documento histórico — SUPERADO.** Describe el estado del 14 nov 2026, previo a la validación en Power BI Desktop. Sus valores `NOT_EXECUTED`, `UNVERIFIED` o `READY_FOR_DESKTOP_VALIDATION` ya no son vigentes. Estado vigente: [POWERBI_PRODUCTION_CLOSEOUT.md](POWERBI_PRODUCTION_CLOSEOUT.md) e [índice](README.md). Se conserva como antecedente.

Fecha de preparación: 2026-11-14. Fuente: ZIP adjunto `steel-plates-quality-mlops-main.zip`. Rama de GitHub consultada: `main`; último commit consultado: `e19cd1af045ea22e4518f3795f9c5070979a924f (remote main; snapshot ZIP commit UNVERIFIED)`. La equivalencia byte a byte entre ZIP y este commit no está demostrada. Autor original: Jesús R. L. González.

Cambios aplicados únicamente en esta copia local:
1. `powerbi/project/steel-plates-quality-bi.SemanticModel/definition/expressions.tmdl`: sustituido el valor de `RutaCSV` de marcador neutro por la ruta de Windows indicada. El resto de la definición permanece igual.
2. `docs/production/`: añadidos informes de estado y guía de ejecución.
3. Raíz del paquete: scripts PowerShell locales para comprobación/apertura, sin acceso a credenciales.

La copia original descargada no ha sido alterada. No se ha modificado el modelo entrenado, la evidencia científica ni el PBIX. La ruta es específica de la máquina indicada; para GitHub conviene revertirla al placeholder antes de abrir un PR.
