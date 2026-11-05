param([Parameter(Mandatory=$true)][string]$Script, [string[]]$ScriptArgs=@(), [string]$Log='blender_pass2.log')
$ErrorActionPreference='Stop'
$progress=Join-Path $PSScriptRoot 'PROGRESS.md'
# GATE (Chase priority): Sugarloaf movers pass 4 must finish first
while ((Get-CimInstance Win32_Process | ? {$_.CommandLine -match 'sc_movers4\\run4.ps1'}) -or -not ((Test-Path C:\Users\chase\sc_movers4\out\DONE4.txt) -or (Test-Path C:\Users\chase\sc_movers4\out\src\movers_pass4_summary.md))) {
    Add-Content $progress "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') PAUSED: waiting for Sugarloaf movers pass 4 (DONE4 / movers_pass4_summary.md); next check in 120 s. Keep doing non-Blender work."
    Start-Sleep -Seconds 120
}
while (Get-Process blender -ErrorAction SilentlyContinue) {
    Add-Content $progress "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') Waiting for existing Blender process; next check in 60 seconds."
    Start-Sleep -Seconds 60
}
Add-Content $progress "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') Launch Blender 5.2: $Script $ScriptArgs"
$stdout=Join-Path $PSScriptRoot $Log
$stderr=$stdout+'.stderr'
$scriptPath=(Resolve-Path -LiteralPath $Script).Path
$arguments=@('-b','--factory-startup','-P',('"'+$scriptPath+'"'),'--')+$ScriptArgs
$process=Start-Process -FilePath 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -ArgumentList $arguments -WindowStyle Hidden -PassThru -Wait -RedirectStandardOutput $stdout -RedirectStandardError $stderr
$code=$process.ExitCode
Add-Content $progress "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') Blender exited: $Script (exit $code)"
exit $code
