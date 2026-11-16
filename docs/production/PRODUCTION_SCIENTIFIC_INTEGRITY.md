# PRODUCTION SCIENTIFIC INTEGRITY

> **Documento histórico — SUPERADO.** Describe el estado del 14 nov 2026, previo a la validación en Power BI Desktop. Sus valores `NOT_EXECUTED`, `UNVERIFIED` o `READY_FOR_DESKTOP_VALIDATION` ya no son vigentes. Estado vigente: [POWERBI_PRODUCTION_CLOSEOUT.md](POWERBI_PRODUCTION_CLOSEOUT.md) e [índice](README.md). Se conserva como antecedente.

Fecha de preparación: 2026-11-14. Fuente: ZIP adjunto `steel-plates-quality-mlops-main.zip`. Rama de GitHub consultada: `main`; último commit consultado: `e19cd1af045ea22e4518f3795f9c5070979a924f (remote main; snapshot ZIP commit UNVERIFIED)`. La equivalencia byte a byte entre ZIP y este commit no está demostrada. Autor original: Jesús R. L. González.

Criterio de alcance: el modelo clasifica el defecto de placas ya defectuosas; no detecta placas sanas ni anticipa fallas. Valores congelados: entrenamiento 1.552; holdout 389; aciertos 307; errores 82; accuracy 0.7892030848; Macro-F1 0.8146728101764369; balanced accuracy 0.8048726799979933; candidatos a revisión 261; aceptación 128; errores capturados 81; errores no capturados 1. Estas cifras son referencias del proyecto, no resultados calculados de Power BI en esta sesión.

Protección: el manifiesto de hashes documenta que todos los archivos científicos recibidos se mantienen idénticos. No se ajustaron umbrales ni se reentrenó. Los fallos de compatibilidad en esta sesión no justifican modificar el artefacto congelado.
