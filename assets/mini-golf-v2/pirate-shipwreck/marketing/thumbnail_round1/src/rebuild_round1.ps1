# rebuild_round1.ps1 - full reproducible rebuild of the round-1 thumbnail scenes + proofs (Windows PC).
# Usage (from anywhere):  powershell -ExecutionPolicy Bypass -File out\src\rebuild_round1.ps1 [-Blender <blender.exe>] [-Python <python.exe>] [-Source <ship.blend>]
# Paths are relative to this script: out\src\ -> out\ -> job root (expects inputs\start_ship_whimsy_v5_1.blend unless -Source).
# One Blender process at a time; CPU Cycles (Roblox Studio may be open on the PC - never touch it).
param(
  [string]$Blender = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
  [string]$Python = "python",
  [string]$Source = ""
)
$ErrorActionPreference = "Continue"   # native stderr (Blender warnings) must not abort under PS 5.1; exit codes are checked instead
$Src = $PSScriptRoot
$Out = Split-Path $Src -Parent
$Root = Split-Path $Out -Parent
if (-not $Source) { $Source = Join-Path $Root "inputs\start_ship_whimsy_v5_1.blend" }
$Logs = Join-Path $Out "logs"; New-Item -ItemType Directory -Force $Logs | Out-Null
$before = (Get-FileHash $Source -Algorithm SHA256).Hash.ToLower()

# 1) regenerate ORIGINAL kit geometry (unmodified kit_v1 / kit_v22 generators; numpy + Pillow; local trimesh shim)
$env:PYTHONPATH = Join-Path $Src "trimesh_shim"
& $Python (Join-Path $Src "kit_v1_src\gen_kit.py") (Join-Path $Out "build\kit_v1_geom") *> (Join-Path $Logs "gen_kit_v1.log")
if ($LASTEXITCODE -ne 0) { throw "gen_kit v1 failed" }
& $Python (Join-Path $Src "kit_v22_src\gen_kit22.py") (Join-Path $Out "build\kit_v22_geom") *> (Join-Path $Logs "gen_kit_v22.log")
if ($LASTEXITCODE -ne 0) { throw "gen_kit22 failed" }
Remove-Item Env:PYTHONPATH

# 2) build the packed 3-scene file (source opened read-only, saved as a copy)
& $Blender -b $Source --python-exit-code 1 --python (Join-Path $Src "build_thumbnail_round1.py") -- `
  --kit1 (Join-Path $Out "build\kit_v1_geom") --kit22 (Join-Path $Out "build\kit_v22_geom") --output (Join-Path $Out "pirate_thumbnail_round1.blend") *> (Join-Path $Logs "build_r1.log")
if ($LASTEXITCODE -ne 0) { throw "build failed (see logs\build_r1.log)" }

# 3) render the three proofs one at a time
foreach ($s in "A", "B", "C") {
  & $Blender -b (Join-Path $Out "pirate_thumbnail_round1.blend") --python-exit-code 1 --python (Join-Path $Src "render_round1.py") -- --scene $s *> (Join-Path $Logs "render_$s.log")
  if ($LASTEXITCODE -ne 0) { throw "render $s failed" }
}

# 4) validate + write manifest.json
& $Blender -b --factory-startup --python-exit-code 1 --python (Join-Path $Src "validate_round1.py") -- --source $Source --output (Join-Path $Out "pirate_thumbnail_round1.blend") --hash-before $before *> (Join-Path $Logs "validate.log")
if ($LASTEXITCODE -ne 0) { throw "validation failed (see logs\validate.log)" }
Write-Output "REBUILD_ROUND1_OK"

