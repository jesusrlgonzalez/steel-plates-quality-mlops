# Read-only interrogation of the live Power BI Desktop model (OWNER-PBI-REN-001).
# Queries the engine Desktop itself loaded. Never writes to the model.
#
# Run under Windows PowerShell 5.1: LoadFrom probes the assembly's own directory
# for dependencies there, which .NET 8 (pwsh) does not do. No AssemblyResolve
# handler is installed, because one that calls cmdlets recurses into itself.
param(
    [Parameter(Mandatory)][int]$Port,
    [string]$Bin = 'C:\Program Files\Microsoft Power BI Desktop\bin'
)

$ErrorActionPreference = 'Stop'

# The assembly is Microsoft.PowerBI.AdomdClient.dll but its namespace is
# Microsoft.AnalysisServices.AdomdClient; the two names do not match.
[void][System.Reflection.Assembly]::LoadFrom((Join-Path $Bin 'Microsoft.PowerBI.AdomdClient.dll'))

$connection = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$Port")
$connection.Open()
Write-Output "CONECTADO. Base de datos: $($connection.Database)"
Write-Output ""

function Invoke-Query {
    param([string]$Label, [string]$Text)
    Write-Output "### $Label"
    try {
        $cmd = $connection.CreateCommand()
        $cmd.CommandText = $Text
        $reader = $cmd.ExecuteReader()
        $cols = @(0..($reader.FieldCount - 1) | ForEach-Object { $reader.GetName($_) })
        $rows = @()
        while ($reader.Read()) {
            $row = [ordered]@{}
            for ($i = 0; $i -lt $reader.FieldCount; $i++) { $row[$cols[$i]] = $reader.GetValue($i) }
            $rows += [pscustomobject]$row
        }
        $reader.Close()
        if ($rows.Count -eq 0) { Write-Output "  (sin filas)" }
        else { $rows | Format-Table -AutoSize | Out-String -Width 200 | Write-Output }
    } catch {
        Write-Output "  ERROR: $($_.Exception.Message)"
    }
    Write-Output ""
}

Invoke-Query 'Tablas del modelo' 'SELECT [Name] FROM $SYSTEM.TMSCHEMA_TABLES ORDER BY [Name]'

Invoke-Query 'Relaciones' ('SELECT [FromTableID], [ToTableID], [FromCardinality], [ToCardinality], ' +
    '[CrossFilteringBehavior], [IsActive] FROM $SYSTEM.TMSCHEMA_RELATIONSHIPS')

Invoke-Query 'Particiones: estado y modo' ('SELECT [TableID], [Name], [State], [Mode] ' +
    'FROM $SYSTEM.TMSCHEMA_PARTITIONS ORDER BY [TableID]')

Invoke-Query 'Recuento de filas por tabla' @'
EVALUATE
UNION (
    ROW ( "Tabla", "Fact_Defecto",         "Filas", COUNTROWS ( Fact_Defecto ) ),
    ROW ( "Tabla", "ML_Holdout",           "Filas", COUNTROWS ( ML_Holdout ) ),
    ROW ( "Tabla", "Dim_TipoDefecto",      "Filas", COUNTROWS ( Dim_TipoDefecto ) ),
    ROW ( "Tabla", "Dim_Acero",            "Filas", COUNTROWS ( Dim_Acero ) ),
    ROW ( "Tabla", "Dim_BandaTamano",      "Filas", COUNTROWS ( Dim_BandaTamano ) ),
    ROW ( "Tabla", "Param_Especificacion", "Filas", COUNTROWS ( Param_Especificacion ) )
)
'@

Invoke-Query 'Medidas ML sin filtro (reconciliacion G6)' @'
EVALUATE
ROW (
    "ML Rows",           [ML Rows],
    "ML Correct",        [ML Correct],
    "ML Errors",         [ML Errors],
    "ML Review Rows",    [ML Review Rows],
    "MacroF1",           [Final Macro-F1 (389)],
    "BalancedAccuracy",  [Final Balanced Accuracy (389)],
    "ObservedAccuracy",  [Observed Accuracy],
    "CandidateReview",   [Candidate Review Rate]
)
'@

Invoke-Query 'Por tipo de acero' @'
EVALUATE
SUMMARIZECOLUMNS (
    ML_Holdout[steel_type],
    "Registros", [ML Rows], "Aciertos", [ML Correct], "Revisiones", [ML Review Rows]
)
ORDER BY ML_Holdout[steel_type]
'@

Invoke-Query 'Por clase real' @'
EVALUATE
SUMMARIZECOLUMNS (
    ML_Holdout[actual_defect],
    "Registros", [ML Rows], "Aciertos", [ML Correct],
    "Errores", [ML Errors], "Revisiones", [ML Review Rows]
)
ORDER BY ML_Holdout[actual_defect]
'@

Invoke-Query 'Confusion Bumps -> Other_Faults' @'
EVALUATE
CALCULATETABLE (
    ROW ( "Casos", [ML Rows] ),
    ML_Holdout[actual_defect] = "Bumps", ML_Holdout[predicted_defect] = "Other_Faults"
)
'@

Invoke-Query 'row_id 1277' @'
EVALUATE
CALCULATETABLE (
    SELECTCOLUMNS ( ML_Holdout,
        "row_id", ML_Holdout[row_id], "actual", ML_Holdout[actual_defect],
        "predicho", ML_Holdout[predicted_defect], "confianza", ML_Holdout[confidence],
        "estado", ML_Holdout[review_status], "acierto", ML_Holdout[correct_prediction],
        "revision", ML_Holdout[review_required] ),
    ML_Holdout[row_id] = 1277
)
'@

Invoke-Query 'Estados de revision' @'
EVALUATE
SUMMARIZECOLUMNS ( ML_Holdout[review_status], "Registros", [ML Rows] )
ORDER BY ML_Holdout[review_status]
'@

Invoke-Query 'Inmunidad al filtro: A300 seleccionado' @'
EVALUATE
CALCULATETABLE (
    ROW ( "MacroF1filtrado", [Final Macro-F1 (389)], "MLRowsfiltrado", [ML Rows] ),
    ML_Holdout[steel_type] = "A300"
)
'@

Invoke-Query 'Medidas originales compilan (muestra de _Medidas)' @'
EVALUATE
ROW (
    "Defectos",     [Defectos],
    "COPQ MXN",     [COPQ MXN],
    "Cpk",          [Cpk],
    "Linea Central",[Linea Central],
    "Sigma Global", [Sigma Global],
    "USL px2",      [USL px2]
)
'@

$connection.Close()
Write-Output "CONEXION CERRADA. No se escribio nada en el modelo."
