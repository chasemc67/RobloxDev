# Sugarloaf Canyon HERO LOOK pass 4 (render-only). Ignore any movers / SRV-132 / sc_movers* work and any other brief files.
Workdir: C:\Users\chase\sc\sugarloaf-canyon\models. Render script: _src\render_hero.py (Cycles OptiX). Run headless, one at a time:
  & 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b --factory-startup -P _src\render_hero.py -- [--preview] [--shots a,b]
Before each launch confirm no blender.exe is running (another job may use the PC; wait if so). Never leave Blender running.
Do NOT change fbx\, layout.json, manifest.json or textures used by the FBX. Back up _src\render_hero.py to _src\render_hero_pass3.py, then edit only render_hero.py (render-only objects, lights, world nodes, cameras). Log notes to _src\PROGRESS.md.
References: ..\world\vistas\V1-hub-tee1.png, V2-slot-canyon.png, V3-rope-bridge-mesa.png, V4-sunset-arch.png, V4b-dam-reservoir.png. Current renders: previews\hero\*.png. Open the PNGs as images to judge.
Coordinates: game Y-up (x,y,z); rb() converts to Blender. Sun is west (bearing 270).

Targets:
1. Exposure +~1 stop (view_settings.exposure .35 -> ~1.35; tune so nothing clips badly). Golden hour, not dusk.
2. Sky (camera rays): gradient peach (~#FFB98A at horizon) to turquoise (~#4FC8D8 high up), plus a few lit cumulus clouds (render-only, e.g. noise-masked world clouds or a few cloud puffs/billboards lit warm from the west). Keep lavender ambient for lighting.
3. Warm rim on sun-facing rock: stronger warm key and/or a second low warm sun from the west so west faces glow orange-gold.
4. Lift shadows to lavender, never black: raise lavender ambient/fill until shadow sides read lavender/rose, clearly above black.
5. Arch shot (sunset_arch_from_crown): stop hiding the terrain and placed pieces. Use the REAL near arch `sunset_arch` at (-478,190.4,205) seen from the Crown green (cacti_crown (-379.5,189.6,171), scatter_crown (-336.6,149.2,144.9)). Pull camera back east and drop it a little (a few studs above the Crown ground) looking west. Set the arch-shot sun bearing/elevation so the sun disc sits fully INSIDE the arch opening with a clear sky gap below the lintel; Crown green/ground fills the bottom third. Measure the opening from imported geometry bounds; verify in --preview renders.
6. Dam (dam_crest_walk): peppermint_dam at (0,17,-305); reservoir north (z -425, level 108); downstream is SOUTH (+z). Camera low (y ~25-40) and downstream (z ~ -230..-200) looking up at the dam face so the spillway (top y108 z-309 -> bottom y16.8 z-298, width 20, x=0) reads as a tall white cascade. Render-only effects: bright white foam material with vertical streaks on the spillway sheet; spray/mist at the base (low-density volume or white billboards) and a foam ring on the plunge pool.
7. Junction (junction_town): town row at (150,17.8,455) yaw 90. Rotate the camera ~30 deg so the town row lines the LEFT side of the frame, receding; keep plaza/river readable.
Keep old_sugarloaf_skyline, narrows_crystal_walls, world_vista framing; new lighting only.

Process: edit, --preview render all shots, inspect, iterate (max ~4 rounds), then one final full render (no --preview) writing six PNGs, the .blend and render_report.json. Then make previews\hero\contact_sheet.png (2x3 labelled grid of six finals) and previews\hero\compare_vs_vistas.png (rows render|vista: skyline-V1, narrows-V2, junction-V3, arch-V4, dam-V4b) with Python+PIL.
Finally write _src\pass4_summary.md (exposure, sky, rim, shadow lift, each camera eye/target/fov, sun dirs, render-only objects, file paths, FBX untouched, honest remaining gaps vs V1-V4) and create _src\pass4_done.flag.
