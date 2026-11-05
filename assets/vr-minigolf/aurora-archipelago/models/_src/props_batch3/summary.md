# Batch 3 revision 2 handoff

23 assets; none skipped. ALL PASS: YES (Blender actual triangles).

Existing build_report.json records Blender 5.2.2 LTS and 23 asset records. It matches the current parts source.

Build report mtime: 1791932317.3062625; triangles mtime: 1791932317.2822626. Source hashes are checked for new builds.

Current revision FBX re-import validation: PASS. Current fitcheck uses Blender actual triangles.

Historical revision notes are preserved in summary_prepolish.md. Current Blender facts above derive from build_report.json and fbx_validation.json and require matching source hashes.

| Hole | Assets | Triangles | Result |
|---|---:|---:|---|
| H04 | 6 | 4998 | PASS |
| H06 | 5 | 4276 | PASS |
| H14 | 6 | 4640 | PASS |
| H18 | 6 | 5574 | PASS |

## Source conflicts and shape overrides

- h04_frosted_palm_a: Crown/segmented trunk override: source occluder describes only one straight trunk; two curved crowns required by brief.
- h04_frosted_palm_a: Polish: rounded organic geometry; original pivot/yaw and clearance envelope retained.
- h04_frosted_palm_b: Crown/segmented trunk override: source occluder describes only one straight trunk; two curved crowns required by brief.
- h04_frosted_palm_b: Polish: rounded organic geometry; original pivot/yaw and clearance envelope retained.
- h04_snowpuffs: Polish: rounded organic geometry; original pivot/yaw and clearance envelope retained.
- h06_snowpuffs: Polish: rounded organic geometry; original pivot/yaw and clearance envelope retained.
- h14_snowpuffs: Polish: rounded organic geometry; original pivot/yaw and clearance envelope retained.
- h18_snowpuffs: Polish: rounded organic geometry; original pivot/yaw and clearance envelope retained.
- h06_kettle_pool: Chunky boulder rim stays .20 inside east rail without touching it, rising .85 above water; rev2 Steam mesh removed for runtime particles; west/north/south rim conflicts with shelf felt so chunky rim concentrated east.
- h06_frosted_palms: Three curved trunks and crowns override the single straight-trunk occluder.
- h06_frosted_palms: Polish: rounded organic geometry; original pivot/yaw and clearance envelope retained.
- h06_respawn_stone: Flush sloped stone follows exact shelf_e top, extending below anchor by .029 studs; thickness is below felt.
- h14_bell_gantry: Approved legs moved to x +/-5.45, .8 square; 1x1 beam, knees and X braces entirely above y8.3, lumpy snow caps, beam-only icicles above y8.65. Existing pivot unchanged.
- h14_icicle_bell: Hollow 20-sided flared brass bell inside yaw30 cube envelope below y2.35; clapper visible in open mouth. Nine exact skid strips unchanged; crown ice above y2.35. Hanger/yoke ends .15 below beam.
- h14_buoy_float: Polish: rounded organic geometry; original pivot/yaw and clearance envelope retained.
- h14_safe_side_sign: Sign board extends beyond post-only occluder, within approx envelope and rail clearance.
- h18_halo_arch: Rev2 Game Art Bot update: every rev1 segment (12-sided after exact facet splits) doubled in radial thickness outward/upward only (2.4 to 4.8 studs). Entire inward half and inner facets fixed exactly; foot centres/base height unchanged, added foot thickness outside only. Light IceCore inner facets; original neon core retained. Pivot unchanged.
- h18_crystal_bank_ne_deco: Ten overlapping fat leaning hex crystals, .52-.66 radius, 3.3-4.58 high, neon cores. Approved rev0 bank centres retained outside outer rails; pivot unchanged. Wall widened along outside rail.
- h18_crystal_bank_sw_deco: Ten overlapping fat leaning hex crystals, .52-.66 radius, 3.3-4.58 high, neon cores. Approved rev0 bank centres retained outside outer rails; pivot unchanged. Wall widened along outside rail.
- h18_crystal_chute: Exact rail9/divider meet rail8/rail10 at zero-clearance structural joins. Extend ice skin asset to the complete connected H18 source rail/backing network so every joined collider is an explicitly owned exact skin; no blanket adjacent-rail exception. Full source network overrides chute-only approximate envelope; 1.6 chute opening unchanged.
- h18_ramp_lanterns: Separate 1.9-wide foot caps inset .15 from both felt edges, plate bottom .22 above divider top; downward lips terminate .15 above divider top to respect rail gap. North/south downward lips shield gap from tee eye; 5.5-tall timber posts, Glow heads, brass caps. Pivot unchanged.
- h18_ramp_lanterns: Polish: rounded organic geometry; original pivot/yaw and clearance envelope retained.
- h04_ice_channel_edge: Ice edges .175 outside slide rails; north termination avoids green cross rail. Pivot = ice_sheen.
- h04_ice_channel_edge: Polish: rounded organic geometry; original pivot/yaw and clearance envelope retained.
- h04_crystal_spire: NEW base-centre pivot [-12,0,-18], west of slide per concept spires; >5 studs from rail. Source frosted_palms region used only as contextual reference.
- h14_rail_bollards: NEW six bollards outside lane rails, >=.35 gap; documented hole-origin tee pivot [0,0,0].
- h06_tee_lantern: NEW base-centre pivot [8.2,0,-4], east of tee; >=3 studs from tee rail, chunky 7.4 post and warm lantern.

Chute skin extends to the connected H18 rail network; every exempt collider is explicitly listed and filled exactly. No exemption for unowned adjacent rails. Rail zero for skins is reported as exempt. Snow replaces cream bellies; buoy stripes use mint/violet/snow/brass. Every static pivot remains the source anchor.

## Run sequence

`python gen_batch3.py`, `python fitcheck_batch3.py --preflight`, `python finalize_batch3.py`, `python make_sheet05.py`. User then runs Blender 5.2 headless with `--background --python build_batch3.py`; CPU Cycles12 at1024x768. Afterwards run `python fitcheck_batch3.py`, `python finalize_batch3.py`, `python make_sheet05.py`. No script starts Blender.

Sheet fourth column labels current Blender context, current per-asset previews, earlier build context, or PIL geometry according to preview freshness. The build script re-imports every FBX in a fresh scene and compares meshes, materials, triangle counts and bounds; fbx_validation.json is required for exported handoff.

## Triangle and clearance table

| ID | Tris | Heavy (>900) | Nearest rail (studs) | Nearest felt (studs) |
|---|---:|:---:|---|---|
| h04_crystal_spire | 352 | no | rail2 5.9000 | ice 6.4000 |
| h04_frosted_palm_a | 804 | no | rail2 3.2462 | ice 2.4707 |
| h04_frosted_palm_b | 804 | no | rail2 3.2293 | ice 1.8846 |
| h04_ice_channel_edge | 768 | no | rail2 0.1500 | ice 0.6500 |
| h04_snowpuffs | 1178 | yes | rail3 3.3000 | green 3.8000 |
| h04_steam_vents | 1092 | yes | rail7 4.0750 | ice 4.5750 |
| h06_frosted_palms | 2412 | yes | rail5 1.3939 | shelf_e 4.9025 |
| h06_kettle_pool | 572 | no | rail5 0.1750 | shelf_se 0.3422 |
| h06_respawn_stone | 12 | no | rail5 8.6000 | flush cue |
| h06_snowpuffs | 1044 | yes | rail3 0.2500 | shelf 0.7500 |
| h06_tee_lantern | 236 | no | rail7 3.2500 | lane 3.7000 |
| h14_bell_gantry | 900 | no | rail1 0.5500 | lane 0.5577 |
| h14_buoy_float | 680 | no | rail6 0.5000 | green 1.0000 |
| h14_icicle_bell | 1444 | yes | rail1 2.9500 | contact/flush/source skin 0.0610 |
| h14_rail_bollards | 480 | no | rail1 0.4000 | lane 0.8500 |
| h14_safe_side_sign | 248 | no | rail1 0.4000 | lane 0.6750 |
| h14_snowpuffs | 888 | no | rail4 0.3000 | green 0.8000 |
| h18_crystal_bank_ne_deco | 880 | no | rail10 1.3700 | plaza 1.8700 |
| h18_crystal_bank_sw_deco | 880 | no | rail3 0.4460 | plaza_w 0.9460 |
| h18_crystal_chute | 384 | no | exempt exact skin | exempt exact skin |
| h18_halo_arch | 1664 | yes | rail5 3.8000 | green 4.3000 |
| h18_ramp_lanterns | 528 | no | chute_divider 0.1500 | chute 0.1510 |
| h18_snowpuffs | 1238 | yes | rail7 1.7000 | green 2.2000 |

| Hole | Total tris | Heavy count |
|---|---:|---:|
| H04 | 4998 | 2 |
| H06 | 4276 | 2 |
| H14 | 4640 | 1 |
| H18 | 5574 | 2 |

## Revision 2 baseline (before Polish)

Revision 2 changed h18_halo_arch and h06_kettle_pool; the Polish pass preserves both assets exactly. Rev1 scripts backed up as gen_batch3_rev1.py and build_batch3_rev1.py. Foot centres/base heights and complete inward half preserved exactly; added foot width extends outside only. Every leg/crown segment is doubled outward/upward, with twelve-sided chamfers and light IceCore inner facets. All kettle Steam mesh removed. All 23 current preflight asset checks pass.

Measured tube thickness (rev1 -> rev2): crown [2.399999999999995, 4.79999999999999]; legs [[2.3999999999999986, 4.799999999999997], [2.3999999999999986, 4.799999999999997]] studs. Inner-edge maximum deviation: 0.000000000000 studs; 156 complete inward facets unchanged. All segment thickness ratios pass 2x. Foot centres: [[-23, 0.5, -52], [23, 0.5, -52]].

Arch: 1664 triangles; headroom over each crossed felt: {'green': 26.223505307992195} studs; minimum 26.223505 studs. Ball-path clearance: none over ball path; the waypoint tee-to-cup path ends before the arch footprint. Sightline hits: 0.

Kettle pool: 572 triangles; headroom: none over felt.

Current-source Blender 5.2.2 LTS build confirmed by Blender bpy and matching parts_sha256. Started 2026-10-13 22:58:36 UTC; exported 2026-10-13 22:58:37 UTC; fresh-scene FBX re-import validation PASS at 2026-10-13 22:59:09 UTC.

Selective build exported/reimported 10 assets: h04_frosted_palm_a, h04_frosted_palm_b, h04_ice_channel_edge, h04_snowpuffs, h06_frosted_palms, h06_snowpuffs, h14_buoy_float, h14_snowpuffs, h18_ramp_lanterns, h18_snowpuffs. Build report covers 23 assets.
Selective build arguments: `-- --only h04_frosted_palm_a,h04_frosted_palm_b,h04_ice_channel_edge,h04_snowpuffs,h06_frosted_palms,h06_snowpuffs,h14_buoy_float,h14_snowpuffs,h18_ramp_lanterns,h18_snowpuffs`. Other FBXs stay unchanged.
Sheet05 selects previews by timestamp and labels per-asset previews separately from hole context.

## Polish

Only the ten requested assets changed. Original anchors, pivots, yaw, foot caps and authorized clearance envelopes retained; all other source assets and manifest records remain identical to prepolish backups. Rounded snowpuff bodies and heads have at least twelve segments, Snow bellies, Beak and scarves. Eleven broad, arched drooping palm fronds have thin Snow top strips. Twelve-sided mint/violet/Snow bulged harbour barrels have brass lamp cages and a frosted rope coil. Ramp lantern heads and posts are about 1.5x wider, with Glow #FFB861 Neon panes and Brass caps/finials.

Ice banks: chunky faceted volumes 0.82-1.09 studs tall with IceCore strips along the upper inner edge. Width is 0.40 studs: the original outer envelope x=+/-5.05 and the required 0.15 rail gap leave only 0.40, so the requested 0.6-1.0 width cannot fit without extending the envelope. Existing envelope retained.

Current-source Blender actual triangles: ALL PASS. Current-source Blender/FBX validation: PASS.

| ID | Old tris | New tris | Nearest rail | Nearest felt | Heavy count per hole |
|---|---:|---:|---|---|---:|
| h04_frosted_palm_a | 760 | 804 | rail2 3.2462 | ice 2.4707 | 2 |
| h04_frosted_palm_b | 760 | 804 | rail2 3.2293 | ice 1.8846 | 2 |
| h04_snowpuffs | 1538 | 1178 | rail3 3.3000 | green 3.8000 | 2 |
| h06_snowpuffs | 1284 | 1044 | rail3 0.2500 | shelf 0.7500 | 2 |
| h14_snowpuffs | 1176 | 888 | rail4 0.3000 | green 0.8000 | 1 |
| h18_snowpuffs | 1598 | 1238 | rail7 1.7000 | green 2.2000 | 2 |
| h06_frosted_palms | 2280 | 2412 | rail5 1.3939 | shelf_e 4.9025 | 2 |
| h14_buoy_float | 864 | 680 | rail6 0.5000 | green 1.0000 | 1 |
| h18_ramp_lanterns | 816 | 528 | chute_divider 0.1500 | chute 0.1510 | 2 |
| h04_ice_channel_edge | 48 | 768 | rail2 0.1500 | ice 0.6500 | 2 |

Selective user build arguments: `-- --only h04_frosted_palm_a,h04_frosted_palm_b,h04_ice_channel_edge,h04_snowpuffs,h06_frosted_palms,h06_snowpuffs,h14_buoy_float,h14_snowpuffs,h18_ramp_lanterns,h18_snowpuffs`. After build: `python fitcheck_batch3.py`, `python finalize_batch3.py`; after both batches: `python ../make_polish_sheet.py`. No Python script launches Blender.
