# rebuild_round3_1.ps1 - reproducible R3.1 polish: polish -> one render (CPU, 1920x1080, 128 spp, denoise) -> downsamples -> validate.
# Usage: powershell -ExecutionPolicy Bypass -File out\src\rebuild_round3_1.ps1 [-Blender <blender.exe>] [-Python <python.exe>] [-Source <R3.blend>] [-Output <R3.1.blend>]
# One Blender process at a time; Roblox Studio may be open, so the render is CPU only. The source is opened read-only and never written.
param(
  [string]$Blender = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
  [string]$Python = "python",
  [string]$Source = "",
  [string]$Output = "",
  [double]$TurfDrop = 0.12,
  [double]$FlagYawDeg = 36
)
$ErrorActionPreference = "Continue"
$Src = $PSScriptRoot; $Out = Split-Path $Src -Parent; $Root = Split-Path $Out -Parent
if (-not $Source) { $Source = Join-Path $Root "inputs\pirate_thumbnail_round3.blend" }
if (-not $Output) { $Output = Join-Path $Out "pirate_thumbnail_round3_1.blend" }
$Logs = Join-Path $Out "logs"; New-Item -ItemType Directory -Force $Logs | Out-Null
$Prev = Join-Path $Out "previews"; New-Item -ItemType Directory -Force $Prev | Out-Null
$Report = Join-Path $Logs "polish_report.json"; $Full = Join-Path $Prev "B_round3_1_1920x1080.png"

& $Blender -b --factory-startup --python-exit-code 1 --python (Join-Path $Src "polish_round3_1.py") -- --source $Source --output $Output --report $Report --turf-drop $TurfDrop --flag-yaw-deg $FlagYawDeg *> (Join-Path $Logs "polish.log")
if ($LASTEXITCODE -ne 0) { throw "polish failed (logs\polish.log)" }
& $Blender -b --factory-startup $Output --python-exit-code 1 --python (Join-Path $Src "render_round3_1.py") -- --source $Output --output $Full --samples 128 *> (Join-Path $Logs "render.log")
if ($LASTEXITCODE -ne 0) { throw "render failed (logs\render.log)" }
& $Python (Join-Path $Src "make_downsamples_r3_1.py") --source $Full --output $Prev *> (Join-Path $Logs "downsamples.log")
if ($LASTEXITCODE -ne 0) { throw "downsamples failed" }
& $Blender -b --factory-startup --python-exit-code 1 --python (Join-Path $Src "validate_round3_1.py") -- --source $Source --output $Output --previews $Prev --polish-report $Report --manifest (Join-Path $Out "manifest.json") *> (Join-Path $Logs "validate.log")
if ($LASTEXITCODE -ne 0) { throw "validation failed (logs\validate.log)" }
Write-Output "REBUILD_ROUND3_1_OK"
