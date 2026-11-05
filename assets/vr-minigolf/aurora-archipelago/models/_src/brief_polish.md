# Aurora POLISH pass (two parts). Course dir = this folder's ../../.. (aurora-archipelago). holes.json MD5 fb913741b5dd4812b6d2318e258bcc46 (assert).
Follow the skill roblox-minigolf-3d-modeling. HARD RULES: do NOT launch Blender (I run it); plain python only. Every prop < 3000 tris; collision/query/touch off;
>= 0.15 from felt (plan, below felt+8) and rails/walls; 8-stud head room over all felt; red and cream only on moving parts; SAME anchors/pivots/yaw as now;
stay inside the same clearances/envelopes as the current version. Budget per hole: <= 2 assets over 900 tris (props.md).
Back up every script/json you change to *_prepolish.* first. Unchanged FBX must stay byte-identical: builds export ONLY the changed ids (--only list).

## Part A: corals, models/_src/props_batch1 (18 ids: h07_coral_w1..w5, h07_coral_e6..e10, h08_giant_coral, h08_coral_1..7)
Current state = rev6 (17 corals) and rev7 (giant), see summary.md and rev6.py/rev7.py/build_rev7.py. Write polish_corals.py (plain python: new geometry into
parts.json for these 18 ids only, using the rev6/rev7 crown shapes as the base) and build_polish_corals.py (Blender: export/preview/re-import only those 18,
like build_rev7.py; write triangles.json for all batch-1 parts, fbx_validation for the 18).
- Trunks THIN: about 0.1 x height thick, slight lean (3-8 deg, varied), forking 2-3 times under the dome into branches that meet the lumps.
- Keep the lumpy domes (giant: its 3 stacked domes, 4-stud occluder cap). Add soft mint glow cores (AuroraMint Neon) pushed about 0.2 studs proud
  through the gaps between lumps (6-10 per coral, small rounded blobs), not big spikes.
- Each coral <= 900 tris except the giant (< 3000). Exact bases/pivots/colours unchanged. Fitcheck against the CURRENT holes.json with fitcheck_batch1.py
  (update its MD5 assert); add a finalize step updating props_batch1_manifest.json records for the 18 and fitcheck_props_batch1.txt, and a summary.md
  "Polish" section.
## Part B: batch 3, models/_src/props_batch3 (do NOT touch h18_halo_arch or h06_kettle_pool or any other asset not listed)
Changed ids: h04_ice_channel_edge, h18_ramp_lanterns, h14_buoy_float, h04_frosted_palm_a, h04_frosted_palm_b, h06_frosted_palms, h04_snowpuffs, h06_snowpuffs,
h14_snowpuffs, h18_snowpuffs. Edit gen_batch3.py for these only; build_batch3.py already supports --only.
- h04_ice_channel_edge (<= 900): real ice-bank VOLUME along both sides of the ice felt outside the rails: chunky faceted ice blocks/bank (0.8-1.2 tall,
  0.6-1.0 wide) with an IceCore glow strip along the top inner edge; not thin strips.
- h18_ramp_lanterns (<= 900): about 1.5x bigger lantern heads and posts (still on the divider, foot caps kept, never over felt), warm amber panes
  (Glow #FFB861 Neon panes in a Brass frame, brass cap/finial).
- h14_buoy_float (<= 900): ROUND barrel-shaped harbour buoys (12-16 sided, bulged barrel body), banded AuroraMint / AuroraViolet / Snow (no red/cream),
  small cage top with brass lamp, sitting in a snow mound, plus the frosted rope coil.
- Palms (h04 a/b <= 900 each, h06_frosted_palms < 3000): DROOPING fronds (8-12, arched up from the crown then curving down, tapered, with width), Snow on the
  frond tops (a thin snow strip/top layer), fronds >= 8 above felt.
- Snowpuffs (all four, keep each < its current tris + 20% and < 3000): ROUNDER and LUMPIER, NO flat faces: subdivided spheroid/ellipsoid bodies
  (>= 12 segments, smooth lumps), round head, Snow belly patch (not cream), Beak, scarf. Same positions.
Then: python fitcheck_batch3.py --preflight until ALL PASS; finalize_batch3.py summary must derive Blender facts from build_report/fbx_validation
(it already does). Add a "Polish" section to summary.md.
## Before/after sheet
make_polish_sheet.py (PIL): for every changed asset: BEFORE 3/4 preview (from the backup previews dir I give: models/_src/_prepolish_previews/<batch>/<id>_34.png)
| AFTER 3/4 preview | AFTER front silhouette from triangles. Save to silhouettes/sheet06-polish-before-after.png. It runs after the Blender builds.
Print a table: id, old tris, new tris, nearest rail, nearest felt, heavy count per hole.
