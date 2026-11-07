# run_detached.ps1 - run a .cmd file as a detached one-shot scheduled task (survives session drops). The .cmd writes its own done marker.
# Usage: powershell -ExecutionPolicy Bypass -File run_detached.ps1 -Name <task> -Bat <path.cmd>
param([string]$Name, [string]$Bat)
schtasks /create /f /tn $Name /sc once /st 23:59 /tr "cmd /c `"$Bat`"" | Out-Null
schtasks /run /tn $Name | Out-Null
