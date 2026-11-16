# Does the model carry the local path? The engine is the authority: DataModel is a
# compressed stream, so a plaintext search of the PBIX proves nothing. Read-only.
param([Parameter(Mandatory)][int]$Port,
      [string]$Bin = 'C:\Program Files\Microsoft Power BI Desktop\bin')

$ErrorActionPreference = 'Stop'
[void][System.Reflection.Assembly]::LoadFrom((Join-Path $Bin 'Microsoft.PowerBI.AdomdClient.dll'))
$connection = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$Port")
$connection.Open()
Write-Output "Base de datos: $($connection.Database)"

$cmd = $connection.CreateCommand()
$cmd.CommandText = 'SELECT [Name], [Expression] FROM $SYSTEM.TMSCHEMA_EXPRESSIONS'
$reader = $cmd.ExecuteReader()
while ($reader.Read()) {
    $name = $reader.GetValue(0)
    $expr = [string]$reader.GetValue(1)
    Write-Output ""
    Write-Output "--- expression $name"
    foreach ($line in ($expr -split "`r?`n")) { Write-Output "    $line" }
    if ($expr -match '<USUARIO>' -or $expr -match 'C:\\Users') {
        Write-Output "    >>> CONTIENE RUTA PERSONAL <<<"
    }
}
$reader.Close()

# Partition sources carry M too.
$cmd2 = $connection.CreateCommand()
$cmd2.CommandText = 'SELECT [TableID], [Name], [QueryDefinition] FROM $SYSTEM.TMSCHEMA_PARTITIONS'
$reader2 = $cmd2.ExecuteReader()
Write-Output ""
Write-Output "=== particiones que mencionan una ruta personal ==="
$found = $false
while ($reader2.Read()) {
    $q = [string]$reader2.GetValue(2)
    if ($q -match '<USUARIO>' -or $q -match 'C:\\Users') {
        $found = $true
        Write-Output "  $($reader2.GetValue(1)): CONTIENE RUTA PERSONAL"
    }
}
if (-not $found) { Write-Output "  ninguna" }
$reader2.Close()
$connection.Close()
