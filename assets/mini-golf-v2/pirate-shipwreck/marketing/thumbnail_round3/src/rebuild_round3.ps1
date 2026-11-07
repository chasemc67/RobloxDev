# rebuild_round3.ps1 - full reproducible rebuild of the round-3 lead thumbnail (sketch follow-up, round-2 A frame) (Windows PC, one Blender process at a time, CPU Cycles).
# Usage: powershell -ExecutionPolicy Bypass -File out\src\rebuild_round3.ps1 [-Blender <blender.exe>] [-Python <python.exe>]
#        [-Source <round2.blend>] [-Approved <approved ship.blend>] [-Output <round3.blend>] [-Samples 64]
# Defaults are relative to this script: out\src -> out -> job root (inputs\pirate_thumbnail_round2.blend, inputs\start_ship_whimsy_v5_1.blend).
# Inputs are opened read-only and never written. Roblox Studio may be open on the PC: never touch it (CPU render only).
param(
  [string]$Blender = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
  [string]$Python = "python",
  [string]$Source = "",
  [string]$Approved = "",
  [string]$Output = "",
  [int]$Samples = 64
)
$ErrorActionPreference = "Continue"   # Blender writes warnings to stderr; exit codes are checked instead
$Src = $PSScriptRoot; $Out = Split-Path $Src -Parent; $Root = Split-Path $Out -Parent
if (-not $Source)   { $Source   = Join-Path $Root "inputs\pirate_thumbnail_round2.blend" }
if (-not $Approved) { $Approved = Join-Path $Root "inputs\start_ship_whimsy_v5_1.blend" }
if (-not $Output)   { $Output   = Join-Path $Out "pirate_thumbnail_round3.blend" }
$Logs = Join-Path $Out "logs"; New-Item -ItemType Directory -Force $Logs | Out-Null
$Prev = Join-Path $Out "previews"; New-Item -ItemType Directory -Force $Prev | Out-Null
$Report = Join-Path $Logs "build_report_r3.json"
$Ref2 = Join-Path $Logs "round2_A_reference.png"

# 1) build the packed single-thumbnail-scene file
& $Blender -b --factory-startup --python-exit-code 1 --python (Join-Path $Src "build_thumbnail_round3.py") -- `
  --source $Source --approved $Approved --output $Output --report $Report --samples $Samples *> (Join-Path $Logs "build_r3.log")
if ($LASTEXITCODE -ne 0) { throw "build failed (see logs\build_r3.log)" }
if (Test-Path "$Output`1") { Remove-Item "$Output`1" }   # Blender's automatic .blend1 backup

# 2) render round 3, then the round-2 scene A reference (sketch frame) from the unmodified round-2 input (for the comparison sheet only)
& $Blender -b $Output --python-exit-code 1 --python (Join-Path $Src "render_round3.py") -- --output (Join-Path $Prev "B_round3.png") *> (Join-Path $Logs "render_r3.log")
if ($LASTEXITCODE -ne 0) { throw "render failed (see logs\render_r3.log)" }
& $Blender -b $Source --python-exit-code 1 --python (Join-Path $Src "render_round3.py") -- --scene Thumbnail_A_Hero_R2 --output $Ref2 *> (Join-Path $Logs "render_r2A_reference.log")
if ($LASTEXITCODE -ne 0) { throw "round-2 reference render failed" }

# 3) downsamples, grayscale copies, round2-vs-round3 comparison (Pillow)
& $Python (Join-Path $Src "make_downsamples_r3.py") --previews $Prev --round2 $Ref2 *> (Join-Path $Logs "downsamples_r3.log")
if ($LASTEXITCODE -ne 0) { throw "downsamples failed" }

# 4) validate + manifest.json
& $Blender -b --factory-startup --python-exit-code 1 --python (Join-Path $Src "validate_round3.py") -- `
  --source $Source --approved $Approved --output $Output --previews $Prev --report $Report --manifest (Join-Path $Out "manifest.json") *> (Join-Path $Logs "validate_r3.log")
if ($LASTEXITCODE -ne 0) { throw "validation failed (see logs\validate_r3.log)" }
Write-Output "REBUILD_ROUND3_OK"
