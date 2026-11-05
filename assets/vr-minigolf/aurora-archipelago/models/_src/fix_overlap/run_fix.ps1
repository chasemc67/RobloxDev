param([string]$Blender='C:\Program Files\Blender Foundation\Blender 5.2\blender.exe',[string]$Python='python')
$ErrorActionPreference='Stop'
$root=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../../..')).Path
$log=Join-Path $PSScriptRoot 'build_fix.log'
$flag=Join-Path $PSScriptRoot 'done_fix.flag'
$code=1
Set-Content -LiteralPath $log -Value 'Starting overlap fix job'
Remove-Item -LiteralPath $flag -ErrorAction SilentlyContinue
Push-Location $root
try {
    & $Python (Join-Path $PSScriptRoot 'common.py') init 2>&1 | Out-File -LiteralPath $log -Append
    if ($LASTEXITCODE -ne 0) { throw 'Source SHA256 guard failed' }
    while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 30 }
    $script=Join-Path $PSScriptRoot 'fix_blender.py'
    $stdout=Join-Path $PSScriptRoot 'blender.stdout.log'
    $stderr=Join-Path $PSScriptRoot 'blender.stderr.log'
    $proc=Start-Process -FilePath $Blender -ArgumentList @('-b','--factory-startup','--python-exit-code','1','-P',('"'+$script+'"')) -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    Get-Content -LiteralPath $stdout | Out-File -LiteralPath $log -Append
    Get-Content -LiteralPath $stderr | Out-File -LiteralPath $log -Append
    if ($proc.ExitCode -ne 0) { throw "Blender exit $($proc.ExitCode)" }
    & $Python (Join-Path $PSScriptRoot 'finalize.py') 2>&1 | Out-File -LiteralPath $log -Append
    if ($LASTEXITCODE -ne 0) { throw 'Python finalization failed' }
    $code=0
} catch {
    $_ | Out-File -LiteralPath $log -Append
} finally {
    & $Python (Join-Path $PSScriptRoot 'common.py') check 2>&1 | Out-File -LiteralPath $log -Append
    if ($LASTEXITCODE -ne 0) { $code=1 }
    Set-Content -LiteralPath $flag -Value "exit $code"
    Pop-Location
}
exit $code
