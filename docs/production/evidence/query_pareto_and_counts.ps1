# Verify the Pareto cumulative line reaches 100% and re-check the row counts.
# Read-only. COPQ Acumulado % returns BLANK without category context, so it must
# be evaluated inside a category grouping, which is what the chart does.
param([Parameter(Mandatory)][int]$Port,
      [string]$Bin = 'C:\Program Files\Microsoft Power BI Desktop\bin')

$ErrorActionPreference = 'Stop'
[void][System.Reflection.Assembly]::LoadFrom((Join-Path $Bin 'Microsoft.PowerBI.AdomdClient.dll'))
$connection = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$Port")
$connection.Open()
Write-Output "CONECTADO. Base de datos: $($connection.Database)"
Write-Output ""

function Invoke-Query {
    param([string]$Label, [string]$Text)
    Write-Output "### $Label"
    $cmd = $connection.CreateCommand()
    $cmd.CommandText = $Text
    $reader = $cmd.ExecuteReader()
    $cols = @(0..($reader.FieldCount - 1) | ForEach-Object { $reader.GetName($_) })
    $rows = @()
    while ($reader.Read()) {
        $row = [ordered]@{}
        for ($i = 0; $i -lt $reader.FieldCount; $i++) {
            $v = $reader.GetValue($i)
            if ($v -is [double]) { $v = $v.ToString('R', [cultureinfo]::InvariantCulture) }
            $row[$cols[$i]] = $v
        }
        $rows += [pscustomobject]$row
    }
    $reader.Close()
    $rows | Format-Table -AutoSize | Out-String -Width 220 | Write-Output
    Write-Output ""
}

Invoke-Query 'Recuentos tras el guardado' @'
EVALUATE
UNION (
    ROW ( "Tabla", "Fact_Defecto", "Filas", COUNTROWS ( Fact_Defecto ) ),
    ROW ( "Tabla", "ML_Holdout",   "Filas", COUNTROWS ( ML_Holdout ) )
)
'@

Invoke-Query 'Pareto por tipo de defecto, en contexto de categoria (como el grafico)' @'
EVALUATE
SUMMARIZECOLUMNS (
    Dim_TipoDefecto[tipo_defecto],
    "Defectos",  [Defectos],
    "COPQ",      [COPQ MXN],
    "Acumulado", [COPQ Acumulado %]
)
ORDER BY [COPQ] DESC
'@

Invoke-Query 'Cierre del Pareto: maximo del acumulado y su distancia a 1' @'
EVALUATE
VAR Tabla =
    SUMMARIZECOLUMNS ( Dim_TipoDefecto[tipo_defecto], "Acum", [COPQ Acumulado %] )
VAR Maximo = MAXX ( Tabla, [Acum] )
RETURN
    ROW ( "MaximoAcumulado", Maximo, "DistanciaA1", ABS ( Maximo - 1 ),
          "LlegaA100", IF ( ABS ( Maximo - 1 ) <= 0.000000000001, "SI", "NO" ) )
'@

Invoke-Query 'Las dos metricas finales siguen congeladas' @'
EVALUATE
ROW (
    "MacroF1",      [Final Macro-F1 (389)],
    "Balanced",     [Final Balanced Accuracy (389)],
    "difMacroF1",   ABS ( [Final Macro-F1 (389)] - 0.8146728101764369 ),
    "difBalanced",  ABS ( [Final Balanced Accuracy (389)] - 0.8048726799979933 )
)
'@

Invoke-Query 'Relaciones tras el guardado (ML_Holdout debe seguir ausente)' @'
SELECT [FromTableID], [ToTableID], [FromCardinality], [ToCardinality], [CrossFilteringBehavior]
FROM $SYSTEM.TMSCHEMA_RELATIONSHIPS
'@

Invoke-Query 'Tablas y su ID (para localizar ML_Holdout)' @'
SELECT [ID], [Name] FROM $SYSTEM.TMSCHEMA_TABLES ORDER BY [ID]
'@

$connection.Close()
Write-Output "CONEXION CERRADA. No se escribio nada en el modelo."
