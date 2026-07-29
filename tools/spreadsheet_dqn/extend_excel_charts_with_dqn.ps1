param(
    [Parameter(Mandatory = $true)]
    [string]$WorkbookPath
)

$resolved = (Resolve-Path -LiteralPath $WorkbookPath).Path
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

try {
    $workbook = $excel.Workbooks.Open($resolved)
    foreach ($sheetName in @('Sheet1', 'Sheet1 (2)')) {
        $sheet = $workbook.Worksheets.Item($sheetName)
        $ranges = @('$B$9:$F$10', '$V$9:$Z$10', '$B$26:$F$27', '$V$26:$Z$27')
        if ($sheet.ChartObjects().Count -ne 4) {
            throw "Expected four charts on $sheetName, found $($sheet.ChartObjects().Count)."
        }
        for ($index = 1; $index -le 4; $index++) {
            $sheet.ChartObjects().Item($index).Chart.SetSourceData($sheet.Range($ranges[$index - 1]))
        }
    }
    $workbook.SaveAs($resolved, 51)
    $workbook.Close($true)
}
finally {
    if ($workbook) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($workbook) }
    $excel.Quit()
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($excel)
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

Write-Output "Updated native chart sources in $resolved"
