param([Parameter(Mandatory=$true)][string]$Script, [string[]]$ScriptArgs=@(), [string]$Log='blender_pass2.log')
$ErrorActionPreference='Stop'
$progress=Join-Path $PSScriptRoot 'PROGRESS.md'
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
