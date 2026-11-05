# Batch 3 revision 1 handoff

23 assets; none skipped. ALL PASS: YES (Blender actual triangles).

Existing build_report.json records Blender 5.2.2 LTS and 23 exports. It matches the current parts source.

Build report mtime: 1791925777.500819; triangles mtime: 1791925777.4767482. Source hashes are checked for new builds.

Current revision FBX re-import validation: PASS. Current fitcheck uses Blender actual triangles.

## Batch 3 rev0 provenance

Blender 5.2 headless ran on the PC 13:29:29-13:30:37 PT (exit 0), 19 FBX exported, 61 preview renders saved; the exported fitcheck used Blender actual triangles; summary.md text claiming otherwise was stale boilerplate from the preflight; no FBX re-import check was run for rev0.

| Hole | Assets | Triangles | Result |
|---|---:|---:|---|
| H04 | 6 | 4550 | PASS |
| H06 | 5 | 4420 | PASS |
| H14 | 6 | 5112 | PASS |
| H18 | 6 | 6014 | PASS |

## Source conflicts and shape overrides

- h04_frosted_palm_a: Crown/segmented trunk override: source occluder describes only one straight trunk; two curved crowns required by brief.
- h04_frosted_palm_b: Crown/segmented trunk override: source occluder describes only one straight trunk; two curved crowns required by brief.
- h06_kettle_pool: Chunky boulder rim stays .20 inside east rail without touching it, rising .85 above water; steam curls above pool; west/north/south rim conflicts with shelf felt so chunky rim concentrated east.
- h06_frosted_palms: Three curved trunks and crowns override the single straight-trunk occluder.
- h06_respawn_stone: Flush sloped stone follows exact shelf_e top, extending below anchor by .029 studs; thickness is below felt.
- h14_bell_gantry: Approved legs moved to x +/-5.45, .8 square; 1x1 beam, knees and X braces entirely above y8.3, lumpy snow caps, beam-only icicles above y8.65. Existing pivot unchanged.
- h14_icicle_bell: Hollow 20-sided flared brass bell inside yaw30 cube envelope below y2.35; clapper visible in open mouth. Nine exact skid strips unchanged; crown ice above y2.35. Hanger/yoke ends .15 below beam.
- h14_safe_side_sign: Sign board extends beyond post-only occluder, within approx envelope and rail clearance.
- h18_halo_arch: Source feet x +/-23 with thickness conflict with nominal 46 width; 48-wide outer envelope follows feet occluders. Core crown follows supplied upper occluder; source y0.5 overrides older y0.8 notes.
- h18_crystal_bank_ne_deco: Ten overlapping fat leaning hex crystals, .52-.66 radius, 3.3-4.58 high, neon cores. Approved rev0 bank centres retained outside outer rails; pivot unchanged. Wall widened along outside rail.
- h18_crystal_bank_sw_deco: Ten overlapping fat leaning hex crystals, .52-.66 radius, 3.3-4.58 high, neon cores. Approved rev0 bank centres retained outside outer rails; pivot unchanged. Wall widened along outside rail.
- h18_crystal_chute: Exact rail9/divider meet rail8/rail10 at zero-clearance structural joins. Extend ice skin asset to the complete connected H18 source rail/backing network so every joined collider is an explicitly owned exact skin; no blanket adjacent-rail exception. Full source network overrides chute-only approximate envelope; 1.6 chute opening unchanged.
- h18_ramp_lanterns: Separate 1.9-wide foot caps inset .15 from both felt edges, plate bottom .22 above divider top; downward lips terminate .15 above divider top to respect rail gap. North/south downward lips shield gap from tee eye; 5.5-tall timber posts, Glow heads, brass caps. Pivot unchanged.
- h04_ice_channel_edge: Ice edges .175 outside slide rails; north termination avoids green cross rail. Pivot = ice_sheen.
- h04_crystal_spire: NEW base-centre pivot [-12,0,-18], west of slide per concept spires; >5 studs from rail. Source frosted_palms region used only as contextual reference.
- h14_rail_bollards: NEW six bollards outside lane rails, >=.35 gap; documented hole-origin tee pivot [0,0,0].
- h06_tee_lantern: NEW base-centre pivot [8.2,0,-4], east of tee; >=3 studs from tee rail, chunky 7.4 post and warm lantern.

Chute skin extends to the connected H18 rail network; every exempt collider is explicitly listed and filled exactly. No exemption for unowned adjacent rails. Rail zero for skins is reported as exempt. Snow replaces cream bellies; buoy stripes use mint/violet/snow/brass. Every static pivot remains the source anchor.

## Run sequence

`python gen_batch3.py`, `python fitcheck_batch3.py --preflight`, `python finalize_batch3.py`, `python make_sheet05.py`. User then runs Blender 5.2 headless with `--background --python build_batch3.py`; CPU Cycles12 at1024x768. Afterwards run `python fitcheck_batch3.py`, `python finalize_batch3.py`, `python make_sheet05.py`. No script starts Blender.

Sheet fourth column is labelled PIL preflight geometry until Blender context previews exist. The build script re-imports every FBX in a fresh scene and compares meshes, materials, triangle counts and bounds; fbx_validation.json is required for exported handoff.

## Triangle and clearance table

| ID | Tris | Heavy (>900) | Nearest rail (studs) | Nearest felt (studs) |
|---|---:|:---:|---|---|
| h04_crystal_spire | 352 | no | rail2 5.9000 | ice 6.4000 |
| h04_frosted_palm_a | 760 | no | rail2 3.2462 | ice 2.5207 |
| h04_frosted_palm_b | 760 | no | rail2 3.2293 | ice 1.9346 |
| h04_ice_channel_edge | 48 | no | rail2 0.1750 | ice 0.6750 |
| h04_snowpuffs | 1538 | yes | rail3 3.3000 | green 3.8000 |
| h04_steam_vents | 1092 | yes | rail7 4.0750 | ice 4.5750 |
| h06_frosted_palms | 2280 | yes | rail5 1.3939 | shelf_e 4.9024 |
| h06_kettle_pool | 608 | no | rail5 0.1750 | shelf_se 0.3422 |
| h06_respawn_stone | 12 | no | rail5 8.6000 | flush cue |
| h06_snowpuffs | 1284 | yes | rail3 0.2500 | shelf 0.7500 |
| h06_tee_lantern | 236 | no | rail7 3.2500 | lane 3.7000 |
| h14_bell_gantry | 900 | no | rail1 0.5500 | lane 0.5577 |
| h14_buoy_float | 864 | no | rail6 0.4500 | green 0.9500 |
| h14_icicle_bell | 1444 | yes | rail1 2.9500 | contact/flush/source skin 0.0610 |
| h14_rail_bollards | 480 | no | rail1 0.4000 | lane 0.8500 |
| h14_safe_side_sign | 248 | no | rail1 0.4000 | lane 0.6750 |
| h14_snowpuffs | 1176 | yes | rail4 0.3000 | green 0.8000 |
| h18_crystal_bank_ne_deco | 880 | no | rail10 1.3700 | plaza 1.8700 |
| h18_crystal_bank_sw_deco | 880 | no | rail3 0.4460 | plaza_w 0.9460 |
| h18_crystal_chute | 384 | no | exempt exact skin | exempt exact skin |
| h18_halo_arch | 1456 | yes | rail5 3.8000 | green 4.3000 |
| h18_ramp_lanterns | 816 | no | chute_divider 0.1500 | chute 0.1510 |
| h18_snowpuffs | 1598 | yes | rail7 1.7000 | green 2.2000 |

| Hole | Total tris | Heavy count |
|---|---:|---:|
| H04 | 4550 | 2 |
| H06 | 4420 | 2 |
| H14 | 5112 | 2 |
| H18 | 6014 | 2 |
