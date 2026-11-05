param([string]$Script,[string]$Log,[string[]]$ExtraArgs)
$ErrorActionPreference='Continue'
while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 30 }
Add-Content -LiteralPath (Join-Path $PSScriptRoot 'PROGRESS.md') "`n- $((Get-Date).ToString('o')) Blender process check clear; launch $Script"
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b --python-exit-code 1 -P (Join-Path $PSScriptRoot $Script) @ExtraArgs *> (Join-Path $PSScriptRoot $Log)
if ($LASTEXITCODE -ne 0) { throw "Blender failed: inspect $Log" }
while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 30 }

