# Lobby pass 2

Generated with Blender 5.2.2 LTS. All portal opening/envelope/trigger and aggregate budget checks pass, and portal/kit FBX reimport checks pass. Triangle clipping includes face interiors. See `fitcheck_pass2_validated.txt`, `reimport_check_pass2.txt`, and `../../../kit/_src/reimport_check_pass2.txt`.

Pass1 exports/manifest/previews preserved once in `../_backup_pass1/`. Source-only changes; every FBX was generated through PB/export_fbx. Shared 1024 atlas, no extra portal textures, separate Neon and vertex-colour materials, no real model lights.

## Portal files and tris

| Asset | Tris | Bbox W/H/D | Pivot |
|---|---:|---|---|
| bw_arch_aurora_archipelago | 2374 | 16.0/17.875/4.0 | local origin (0,0,0), shared arch base centre |
| bw_arch_aurora_archipelago_lanterns | 504 | 13.951/3.0/0.9 | local origin (0,0,0), shared arch base centre |
| bw_arch_aurora_archipelago_snowpuff | 514 | 1.617/3.0/1.45 | local origin (0,0,0), shared arch base centre |
| bw_arch_lantern_grove | 5968 | 16.0/17.899/3.859 | local origin (0,0,0), shared arch base centre |
| bw_arch_lantern_grove_lanterns | 888 | 13.9/9.03/0.9 | local origin (0,0,0), shared arch base centre |
| bw_arch_nameplate | 176 | 8.0/2.0/0.5 | base centre: bbox centre X/Z, min Y = 0 |
| bw_arch_sugarloaf_canyon | 1884 | 16.0/18.0/4.0 | local origin (0,0,0), shared arch base centre |
| bw_arch_sugarloaf_canyon_lanterns | 288 | 13.951/2.2/0.9 | local origin (0,0,0), shared arch base centre |
| bw_portal_apron | 12 | 12.0/0.1/4.0 | local origin (0,0,0), shared arch base centre |
| bw_portal_surface_aurora_archipelago | 2 | 10.0/12.0/0.0 | local origin (0,0,0), shared arch base centre |
| bw_portal_surface_lantern_grove | 2 | 10.0/12.0/0.0 | local origin (0,0,0), shared arch base centre |
| bw_portal_surface_sugarloaf_canyon | 2 | 10.0/12.0/0.0 | local origin (0,0,0), shared arch base centre |

Combined static + moving + surface: Lantern Grove 6,858; Sugarloaf Canyon 2,174; Aurora Archipelago 3,394 tris. Apron 12 tris per instance, reused nameplate/sign budgets unchanged. Manifest assembly includes 10 new attached instances; total lobby 48764 tris, 252 instances, well below 120k.

## Collision and attachment

Each arch: legs centre (-6.5,9,0)/(6.5,9,0), size 3x18x4; lintel centre (0,14,0), size 10x4x4. All decorative MeshParts CanCollide false; collision is invisible boxes only. No mesh geometry or modelled trigger in the opening.

Trigger metadata: PortalTrigger_<courseId>, centre (0,5,0), size 10x10x3, CanCollide/CanQuery false, Transparency 1. Portal quad is intentionally inside the trigger and excluded from decorative clearance. Quad at Z=1.5, 0.5 behind front envelope, 10x12, 2 tris, UV 0-1. Shared arch base origin preserved for all children.

Nameplate centre (0,14.5,2.25), sign centre (0,12.7,2.25); rope anchors (+/-2,13.5,2.25). Their reused meshes have base pivots: place nameplate base Y=13.5, sign base Y=11.7, plus the listed front Z. Sign is forward of arch/trigger depth. Lantern cord anchors listed per course in manifest. Separate apron origin (0,0,4), top Y=0, bottom -0.1, no step; intentionally outside arch envelope. Snowpuff keeps arch-local origin; optional bob <=0.1. Lantern sets share arch pivot; individually articulated lanterns require splitting at the documented anchors.

## Kit

| Asset | Tris | Bbox W/H/D | Pivot |
|---|---:|---|---|
| kit_stringlight_pole | 236 | 1.76/9.73/1.5 | base centre |
| kit_string_lights_span_10 | 584 | 10.447/2.447/0.425 | base centre |
| kit_string_lights_span_20 | 864 | 20.447/2.524/0.425 | base centre |
| kit_banner_pole | 288 | 4.0/10.0/1.5 | base centre |
| kit_banner_lantern_grove | 208 | 3.0/4.5/0.56 | top centre |
| kit_banner_sugarloaf_canyon | 452 | 3.0/4.5/0.5 | top centre |
| kit_banner_aurora_archipelago | 130 | 3.0/4.5/0.5 | top centre |
| kit_flag_pennant_string | 137 | 10.047/1.728/0.3 | base centre |
| kit_bench_a | 1188 | 6.0/3.3/2.25 | base centre |
| kit_bench_b | 304 | 6.0/3.2/2.0 | base centre |
| kit_planter_square | 648 | 3.0/2.1/3.0 | base centre |
| kit_planter_round | 224 | 3.0/2.1/3.0 | base centre |
| kit_plant_autumn | 348 | 2.673/3.305/2.693 | base centre |
| kit_plant_cactus_candy | 396 | 2.551/3.85/0.8 | base centre |
| kit_plant_crystal | 88 | 2.374/3.245/1.937 | base centre |
| kit_lamp_post | 288 | 1.5/8.8/1.5 | base centre |
| kit_lamp_post_double | 504 | 3.646/8.0/1.5 | base centre |
| kit_leaderboard_frame | 1728 | 14.0/9.85/1.75 | base centre |
| kit_leaderboard_panel_1 | 2 | 3.4/5.6/0.0 | shared local origin |
| kit_leaderboard_panel_2 | 2 | 3.4/5.6/0.0 | shared local origin |
| kit_leaderboard_panel_3 | 2 | 3.4/5.6/0.0 | shared local origin |

Kit manifest records hooks, cloth/soil attach origins and panel face rectangles. Leaderboard panels are separate two-triangle FBXs sharing frame origin, W3.4 H5.6 centred at X=-4.3/0/4.3, Y5, Z=-0.65, facing -Z. Span/bunting origins at base centre; use recorded hook heights to hang them. Banner cloth origin top centre for sway. No collision on any kit prop.

## Previews, rebuild and caveats

Portal eye/34 renders and concept comparison sheet: `../previews/portals/`. Kit eye/34 and contact sheet: `../../../kit/previews/`. Cycles OptiX used. Reference capsule is 2x5, in opening, moved forward of opaque portal display so visible. Eye camera Y=5 at ~20 studs in front. Preview nameplates reused; preview portal shader is illustrative noise colour only, runtime swirl/ribbons, particles, state controls and teleport remain RobloxDevBot's. FBX cannot preserve shader emission wiring: set Neon from manifest, preserve vertex colour attribute Col. Imported material count/geometry/pivot/orientation verified. Tiny texture marks are atlas paint, not modelled detail. Flat display planes and prescribed apron are exceptions to minimum solid detail thickness. Model shapes simplify painted concepts for VR/mobile budgets.

Run Blender directly, one instance at a time, never `_src/run_blender.ps1`:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b --factory-startup -P boardwalk/models/_src/build_all.py -- --group arches
python boardwalk/models/_src/metadata_pass2.py
python boardwalk/models/_src/build_all.py --assemble
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b --factory-startup -P boardwalk/models/_src/fitcheck.py -- --pass2
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b --factory-startup -P boardwalk/models/_src/reimport_check.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b --factory-startup -P kit/_src/build_kit.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b --factory-startup -P boardwalk/models/_src/reimport_check.py -- C:/Users/chase/bw_lobby2/lobby/kit --kit
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b --factory-startup -P boardwalk/models/_src/render_pass2.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b --factory-startup -P boardwalk/models/_src/render_pass2.py -- C:/Users/chase/bw_lobby2/lobby/kit --kit
python boardwalk/models/_src/finalize_pass2.py
```
