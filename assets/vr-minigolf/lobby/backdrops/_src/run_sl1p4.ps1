$ErrorActionPreference = 'Stop'
$w = 'C:\Users\chase\sl_spires'
$code = 1
try {
    Remove-Item -LiteralPath "$w\DONE_sl1p4.txt" -ErrorAction SilentlyContinue
    $p = Start-Process -FilePath 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -ArgumentList @('-b','--factory-startup','-P',"`"$w\_src\build_sl1_pass4.py`"",'--',"`"$w`"",'--render') -WindowStyle Hidden -PassThru -Wait -RedirectStandardOutput "$w\_src\build_sl1p4.log" -RedirectStandardError "$w\_src\build_sl1p4.log.stderr"
    $code = $p.ExitCode
    if ($code -ne 0) { throw "Blender failed: exit $code" }
    & python "$w\_src\fitcheck_sl1_pass4.py" $w
    $code = $LASTEXITCODE
    if ($code -ne 0) { throw "Fitcheck failed: exit $code" }
    & python "$w\_src\make_sheet_sl1_pass4.py" $w
    $code = $LASTEXITCODE
    if ($code -ne 0) { throw "Sheet failed: exit $code" }
} catch {
    if ($code -eq 0) { $code = 1 }
    Write-Output $_
} finally {
    Set-Content -LiteralPath "$w\DONE_sl1p4.txt" -Value "exit $code"
}
exit $code
