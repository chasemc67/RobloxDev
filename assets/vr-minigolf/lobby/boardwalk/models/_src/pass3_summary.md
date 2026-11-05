# Lobby portal pass 3

Completed with Blender 5.2.2 LTS. Export-based fitcheck and reimport check: ALL PASS. Original pass 2 assets, manifest, previews and arch generator preserved once in `../_backup_pass2/`.

| Course | Static + separate moving + portal tris | Cap | Use |
|---|---:|---:|---:|
| lantern_grove | 14,142 | 15,000 | 94.3% |
| sugarloaf_canyon | 7,374 | 8,000 | 92.2% |
| aurora_archipelago | 8,974 | 10,000 | 89.7% |

## Triangle table per file

| FBX | Tris | Pivot |
|---|---:|---|
| fbx/bw_arch_aurora_archipelago.fbx | 8170 | local origin (0,0,0), shared arch base centre |
| fbx/bw_arch_aurora_archipelago_lantern_01.fbx | 144 | cord anchor / swing hinge at local origin |
| fbx/bw_arch_aurora_archipelago_lantern_02.fbx | 144 | cord anchor / swing hinge at local origin |
| fbx/bw_arch_aurora_archipelago_snowpuff.fbx | 514 | local origin (0,0,0), shared arch base centre |
| fbx/bw_arch_lantern_grove.fbx | 13252 | local origin (0,0,0), shared arch base centre |
| fbx/bw_arch_lantern_grove_lantern_01.fbx | 148 | cord anchor / swing hinge at local origin |
| fbx/bw_arch_lantern_grove_lantern_02.fbx | 148 | cord anchor / swing hinge at local origin |
| fbx/bw_arch_lantern_grove_lantern_03.fbx | 148 | cord anchor / swing hinge at local origin |
| fbx/bw_arch_lantern_grove_lantern_04.fbx | 148 | cord anchor / swing hinge at local origin |
| fbx/bw_arch_lantern_grove_lantern_05.fbx | 148 | cord anchor / swing hinge at local origin |
| fbx/bw_arch_lantern_grove_lantern_06.fbx | 148 | cord anchor / swing hinge at local origin |
| fbx/bw_arch_nameplate.fbx | 176 | base centre: bbox centre X/Z, min Y = 0 |
| fbx/bw_arch_sugarloaf_canyon.fbx | 7084 | local origin (0,0,0), shared arch base centre |
| fbx/bw_arch_sugarloaf_canyon_lantern_01.fbx | 144 | cord anchor / swing hinge at local origin |
| fbx/bw_arch_sugarloaf_canyon_lantern_02.fbx | 144 | cord anchor / swing hinge at local origin |
| fbx/bw_portal_apron.fbx | 12 | local origin (0,0,0), shared arch base centre |
| fbx/bw_portal_surface_aurora_archipelago.fbx | 2 | local origin (0,0,0), shared arch base centre |
| fbx/bw_portal_surface_lantern_grove.fbx | 2 | local origin (0,0,0), shared arch base centre |
| fbx/bw_portal_surface_sugarloaf_canyon.fbx | 2 | local origin (0,0,0), shared arch base centre |

## Lantern anchors

Coordinates below use arch-local Roblox X/Y/Z. Every lantern FBX has its origin at the cord anchor, not at the arch base. Place it at the recorded anchor; rotate about its own local Z axis +/-3 degrees with different phases. Glow pulse +/-15% at 0.5 Hz. Collision disabled.

| Lantern | Anchor X/Y/Z | Swing axis |
|---|---|---|
| bw_arch_aurora_archipelago_lantern_01 | [-6.8, 6.2, 1.25] | [0, 0, 1] |
| bw_arch_aurora_archipelago_lantern_02 | [6.8, 6.2, 1.25] | [0, 0, 1] |
| bw_arch_lantern_grove_lantern_01 | [-6.5, 11.5, 1.3] | [0, 0, 1] |
| bw_arch_lantern_grove_lantern_02 | [6.5, 11.5, 1.3] | [0, 0, 1] |
| bw_arch_lantern_grove_lantern_03 | [-6.5, 7.5, 1.3] | [0, 0, 1] |
| bw_arch_lantern_grove_lantern_04 | [6.5, 7.5, 1.3] | [0, 0, 1] |
| bw_arch_lantern_grove_lantern_05 | [-3.5, 14.5, 1.3] | [0, 0, 1] |
| bw_arch_lantern_grove_lantern_06 | [3.5, 14.5, 1.3] | [0, 0, 1] |
| bw_arch_sugarloaf_canyon_lantern_01 | [-6.5, 12.6, 1.6] | [0, 0, 1] |
| bw_arch_sugarloaf_canyon_lantern_02 | [6.5, 12.6, 1.6] | [0, 0, 1] |

## Changes and visual review

Lantern Grove: twisting twin trunks, front branch forks, knot rings, root rocks/moss/flowers and forty additional layered autumn leaf masses with foliage spilling down both sides. Six paper lanterns exported independently.

Sugarloaf Canyon: independently offset and rotated bevelled sandstone courses, contrasting cream strata, flat lintel with chipped rock cap, pink/gold crystal clusters at feet, middle ledges and crowns, lollipop saguaro and two independent brass lanterns.

Aurora Archipelago: larger layered dark boulders and snow caps around both legs, additional stacked faceted purple/cyan crystals, snow-covered crown rocks and crystal cluster, lintel icicles, felt mats, two wooden posts and separate brass lanterns. Separate snowpuff remains 514 tris (limit 1,500).

Reviewed the eye and 3/4 renders alongside all three supplied concepts. Iterated twice after initial visual review: enlarged and moved foliage forward, made sandstone courses angular, moved candy crystals in front of the towers and onto crowns, and enlarged/moved snowy base rocks forward. These now show distinct layered silhouettes and themed base dressing. The fixed 16x18x4 envelope and toy-scale budget require a narrower silhouette and much coarser foliage than the painted concepts.

## Preserved integration

Base-centre arch origin, front +Z, 16x18x4 envelope; 10x12 opening from Y=0 and trigger 10x10x3 at (0,5,0) verified by polygon clipping against volumes, including face interiors. Exact collision boxes: legs (-6.5,9,0)/(6.5,9,0), sizes 3x18x4; lintel (0,14,0), 10x4x4. Portal surfaces remain 10x12 quads, 2 tris, UV 0-1, Z=1.5. Apron and shared nameplate/sign are unchanged. Nameplate/sign attachment locations remain unchanged and are forward of the decorative envelope.

Shared 1024 atlas plus vertex colours; separate Neon material; zero additional textures or model lights; opaque materials. Two-segment bevels on chunky block edges. Collision on invisible boxes only. Reused thin apron/portal planes and painted atlas details are prescribed exceptions to solid detail size. Lanterns animate independently; snowpuff retains its arch-base pivot. Suggested swing is runtime metadata, not baked FBX animation.

Preview portal shader is illustrative colour noise; animated swirls/ribbons, particles, lettering, teleport and glow behaviour remain runtime responsibilities. Preserve the exported Col attribute for vertex colours and use manifest Neon colours when importing. Preview camera is five studs high, about twenty studs in front, with a 2x5 reference capsule; reference figure is omitted from 3/4 views.

## Rebuild and validation

Run Blender directly with `-b --factory-startup -P _src/build_all.py -- --group arches`, then Python `_src/metadata_pass3.py` and `_src/build_all.py --assemble`. Run Blender `_src/fitcheck.py -- --pass3`, `_src/reimport_check.py`, and `_src/render_pass3.py`, followed by Python `_src/compose_pass3.py`. Never use run_blender.ps1. One owned Blender instance at a time.

Checks: `fitcheck_pass3_validated.txt`, `reimport_check_pass3.txt`, `artifact_audit_pass3.txt`. Final lobby manifest total: 66828 triangles, no missing assets. Old combined lantern files and manifest fragments removed; preserved in backup. Every direct Blender invocation has returned and no owned instance remains running.
