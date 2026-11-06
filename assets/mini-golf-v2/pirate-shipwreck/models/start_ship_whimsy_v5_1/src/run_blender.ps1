# Run ONE headless Blender job as a detached scheduled task and wait for it.
# usage: powershell -File run_blender.ps1 -Tag <tag> -BArgs "<blender args after -b --factory-startup>"
# Writes out/logs/<tag>.log (stdout+stderr) and out/logs/<tag>.exit (exit code).
param([string]$Tag, [string]$BArgs, [int]$TimeoutMin = 90)
$ErrorActionPreference = 'Stop'
$W = 'C:\Users\chase\sc_jobs\ship_v5_1_n1'
$BL = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$log = "$W\out\logs\$Tag.log"; $ex = "$W\out\logs\$Tag.exit"; $cmdf = "$W\out\logs\_task_$Tag.cmd"
if (Get-Process blender -ErrorAction SilentlyContinue) { throw 'another blender.exe is running; one job at a time' }
Remove-Item $ex -ErrorAction SilentlyContinue
"@echo off`r`ncd /d $W`r`n`"$BL`" -b --factory-startup $BArgs > `"$log`" 2>&1`r`necho %ERRORLEVEL% > `"$ex`"`r`n" | Set-Content -Encoding ascii $cmdf
$tn = "ship_v51_$Tag"
schtasks /Create /F /TN $tn /SC ONCE /ST 23:59 /TR "cmd /c `"$cmdf`"" | Out-Null
schtasks /Run /TN $tn | Out-Null
$t0 = Get-Date
while (-not (Test-Path $ex)) {
  Start-Sleep -Seconds 5
  if (((Get-Date) - $t0).TotalMinutes -gt $TimeoutMin) { schtasks /End /TN $tn | Out-Null; schtasks /Delete /F /TN $tn | Out-Null; throw "timeout $Tag" }
}
Start-Sleep -Seconds 2
schtasks /Delete /F /TN $tn | Out-Null
Remove-Item $cmdf -ErrorAction SilentlyContinue
$code = (Get-Content $ex -Raw).Trim()
"$Tag exit=$code elapsed_s=$([int]((Get-Date) - $t0).TotalSeconds)" | Tee-Object -Append "$W\out\logs\run_history.txt"
