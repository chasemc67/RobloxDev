# rebuild_round2.ps1 - full reproducible rebuild of the round-2 thumbnail scenes A/B + proofs (Windows PC).
# Usage: powershell -ExecutionPolicy Bypass -File out\src\rebuild_round2.ps1 [-Blender <blender.exe>] [-Python <python.exe>]
#        [-Source <round1.blend>] [-Approved <approved ship.blend>] [-Output <round2.blend>] [-Samples 64]
# Paths default relative to this script: out\src\ -> out\ -> job root (inputs\pirate_thumbnail_round1.blend, inputs\start_ship_whimsy_v5_1.blend).
# One Blender process at a time; CPU Cycles (Roblox Studio may be open on the PC - never touch it). Inputs are never written.
param(
  [string]$Blender = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
  [string]$Python = "python",
  [string]$Source = "",
  [string]$Approved = "",
  [string]$Output = "",
  [int]$Samples = 64
)
$ErrorActionPreference = "Continue"   # native stderr (Blender warnings) must not abort under PS 5.1; exit codes are checked instead
$Src = $PSScriptRoot
$Out = Split-Path $Src -Parent
$Root = Split-Path $Out -Parent
if (-not $Source)   { $Source   = Join-Path $Root "inputs\pirate_thumbnail_round1.blend" }
if (-not $Approved) { $Approved = Join-Path $Root "inputs\start_ship_whimsy_v5_1.blend" }
if (-not $Output)   { $Output   = Join-Path $Out "pirate_thumbnail_round2.blend" }
$Logs = Join-Path $Out "logs"; New-Item -ItemType Directory -Force $Logs | Out-Null
$Prev = Join-Path $Out "previews"; New-Item -ItemType Directory -Force $Prev | Out-Null
$Report = Join-Path $Out "build\build_report_r2.json"

# 1) build the packed 2-scene file (round-1 file opened read-only, saved as a copy to -Output)
& $Blender -b --factory-startup --python-exit-code 1 --python (Join-Path $Src "build_thumbnail_round2.py") -- `
  --source $Source --approved $Approved --output $Output --report $Report --samples $Samples *> (Join-Path $Logs "build_r2.log")
if ($LASTEXITCODE -ne 0) { throw "build failed (see logs\build_r2.log)" }

# 2) render A then B (one at a time)
foreach ($s in "A", "B") {
  & $Blender -b $Output --python-exit-code 1 --python (Join-Path $Src "render_round2.py") -- --scene $s --out (Join-Path $Prev "$($s)_round2.png") *> (Join-Path $Logs "render_r2_$s.log")
  if ($LASTEXITCODE -ne 0) { throw "render $s failed (see logs\render_r2_$s.log)" }
}

# 3) downsamples + grayscale review copies (Pillow)
& $Python (Join-Path $Src "make_downsamples.py") --previews $Prev *> (Join-Path $Logs "downsamples.log")
if ($LASTEXITCODE -ne 0) { throw "downsamples failed" }

# 4) validate + measurements + manifest.json
& $Blender -b --factory-startup --python-exit-code 1 --python (Join-Path $Src "validate_round2.py") -- `
  --source $Source --approved $Approved --output $Output --report $Report --previews $Prev --manifest (Join-Path $Out "manifest.json") *> (Join-Path $Logs "validate_r2.log")
if ($LASTEXITCODE -ne 0) { throw "validation failed (see logs\validate_r2.log)" }
Write-Output "REBUILD_ROUND2_OK"
