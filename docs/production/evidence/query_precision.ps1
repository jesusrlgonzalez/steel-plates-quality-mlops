# Prove the 1e-12 tolerance inside the engine itself: let DAX compute the absolute
# difference against the frozen literals, so no client-side formatting can hide it.
param([Parameter(Mandatory)][int]$Port,
      [string]$Bin = 'C:\Program Files\Microsoft Power BI Desktop\bin')

$ErrorActionPreference = 'Stop'
[void][System.Reflection.Assembly]::LoadFrom((Join-Path $Bin 'Microsoft.PowerBI.AdomdClient.dll'))
$connection = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$Port")
$connection.Open()

$cmd = $connection.CreateCommand()
$cmd.CommandText = @'
EVALUATE
ROW (
    "difMacroF1",   ABS ( [Final Macro-F1 (389)] - 0.8146728101764369 ),
    "difBalanced",  ABS ( [Final Balanced Accuracy (389)] - 0.8048726799979933 ),
    "difAccuracy",  ABS ( [Observed Accuracy] - 0.7892030848329049 ),
    "difReview",    ABS ( [Candidate Review Rate] - 0.6709511568123393 ),
    "igualMacroF1",  IF ( [Final Macro-F1 (389)] = 0.8146728101764369, "EXACTO", "DISTINTO" ),
    "igualBalanced", IF ( [Final Balanced Accuracy (389)] = 0.8048726799979933, "EXACTO", "DISTINTO" )
)
'@
$reader = $cmd.ExecuteReader()
while ($reader.Read()) {
    for ($i = 0; $i -lt $reader.FieldCount; $i++) {
        $name = $reader.GetName($i)
        $value = $reader.GetValue($i)
        # R round-trips a double to full precision; the default format truncates it.
        if ($value -is [double]) { $value = $value.ToString('R', [cultureinfo]::InvariantCulture) }
        Write-Output ("{0,-16} {1}" -f $name, $value)
    }
}
$reader.Close()

$cmd2 = $connection.CreateCommand()
$cmd2.CommandText = 'EVALUATE ROW ( "MacroF1", [Final Macro-F1 (389)], "Balanced", [Final Balanced Accuracy (389)] )'
$reader2 = $cmd2.ExecuteReader()
Write-Output ""
Write-Output "--- valores a precision completa (formato R) ---"
while ($reader2.Read()) {
    for ($i = 0; $i -lt $reader2.FieldCount; $i++) {
        $v = $reader2.GetValue($i)
        if ($v -is [double]) { $v = $v.ToString('R', [cultureinfo]::InvariantCulture) }
        Write-Output ("{0,-16} {1}" -f $reader2.GetName($i), $v)
    }
}
$reader2.Close()
$connection.Close()
