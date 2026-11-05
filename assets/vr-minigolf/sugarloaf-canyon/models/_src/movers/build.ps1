$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location -LiteralPath $taskRoot
while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 10 }
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b -t 4 -P out\src\build_movers.py *> out\src\build.log
python out\src\fitcheck_movers.py *> out\src\fitcheck.log
python out\src\handoff.py
# Final Cycles only after a true passing fitcheck, never a draft certificate.
if (Test-Path out\src\fitcheck_movers_pass1_validated.txt) {
    foreach ($name in 'h06_sluice_gate','h11_lock_gate','h11_lock_lift') {
        while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 10 }
        & 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b -t 4 -P out\src\render_pc.py -- --input "out/src/$name.blend" --id $name --output out/previews/cycles *> "out/src/cycles_$name.log"
    }
}
