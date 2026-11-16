# Evaluate every measure in the live model individually, so one failure cannot mask
# the others. A measure that does not compile raises on evaluation.
param([Parameter(Mandatory)][int]$Port,
      [string]$Bin = 'C:\Program Files\Microsoft Power BI Desktop\bin')

$ErrorActionPreference = 'Stop'
[void][System.Reflection.Assembly]::LoadFrom((Join-Path $Bin 'Microsoft.PowerBI.AdomdClient.dll'))
$connection = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$Port")
$connection.Open()

function Get-Rows {
    param([string]$Text)
    $cmd = $connection.CreateCommand()
    $cmd.CommandText = $Text
    $reader = $cmd.ExecuteReader()
    $rows = @()
    while ($reader.Read()) {
        $row = @{}
        for ($i = 0; $i -lt $reader.FieldCount; $i++) { $row[$reader.GetName($i)] = $reader.GetValue($i) }
        $rows += [pscustomobject]$row
    }
    $reader.Close()
    return $rows
}

$tables = @{}
Get-Rows 'SELECT [ID], [Name] FROM $SYSTEM.TMSCHEMA_TABLES' | ForEach-Object { $tables[[string]$_.ID] = $_.Name }
$measures = Get-Rows 'SELECT [TableID], [Name] FROM $SYSTEM.TMSCHEMA_MEASURES'

Write-Output ("Medidas declaradas en el modelo: {0}" -f $measures.Count)
Write-Output ""

$ok = 0; $bad = @()
foreach ($m in ($measures | Sort-Object { $tables[[string]$_.TableID] }, Name)) {
    $table = $tables[[string]$m.TableID]
    $name = $m.Name
    # Brackets inside a measure name would break the reference; none are expected.
    $query = "EVALUATE ROW ( ""v"", [$name] )"
    try {
        $value = (Get-Rows $query)[0].'[v]'
        if ($value -is [double]) { $value = $value.ToString('R', [cultureinfo]::InvariantCulture) }
        if ($null -eq $value) { $value = '(BLANK)' }
        Write-Output ("  OK    {0,-22} {1,-32} = {2}" -f $table, $name, $value)
        $ok++
    } catch {
        $first = ($_.Exception.Message -split "`n")[0]
        Write-Output ("  FALLO {0,-22} {1,-32} -> {2}" -f $table, $name, $first)
        $bad += "$table/$name"
    }
}

Write-Output ""
Write-Output ("RESULTADO: {0} de {1} medidas evaluadas sin error" -f $ok, $measures.Count)
if ($bad.Count -gt 0) { Write-Output ("NO COMPILAN: " + ($bad -join ', ')) }
$connection.Close()
