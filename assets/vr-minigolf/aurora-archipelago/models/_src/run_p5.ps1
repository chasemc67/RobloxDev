$ErrorActionPreference = 'Stop'
$code = 1
try {
    & (Join-Path $PSScriptRoot 'run_blender.ps1') -Script (Join-Path $PSScriptRoot 'props_batch3\p5_blender.py') -Log 'build_p5.log'
    $code = $LASTEXITCODE
    if ($null -eq $code) { $code = 1 }
    if ($code -eq 0) {
        & python (Join-Path $PSScriptRoot 'finish_polish2.py')
        $code = $LASTEXITCODE
    }
} catch {
    Write-Error $_ -ErrorAction Continue
    $code = 1
} finally {
    Set-Content -LiteralPath (Join-Path $PSScriptRoot 'done_p5.flag') -Value "exit $code"
}
exit $code
