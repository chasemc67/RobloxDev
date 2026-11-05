$ErrorActionPreference = 'Stop'
$code = 1
try {
    & (Join-Path $PSScriptRoot 'run_blender.ps1') -Script (Join-Path $PSScriptRoot 'props_batch3\polish2_blender.py') -ScriptArgs @('--only','h18_ramp_lanterns') -Log 'build_p4.log'
    $code = $LASTEXITCODE
    if ($null -eq $code) { $code = 1 }
} catch {
    Write-Error $_ -ErrorAction Continue
} finally {
    Set-Content -LiteralPath (Join-Path $PSScriptRoot 'done_p4.flag') -Value "exit $code"
}
exit $code
