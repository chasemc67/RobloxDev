# Aurora batch 3 REVISION 1. Same HARD RULES as brief_batch3.md (read it again): do NOT launch Blender; plain python only; holes.json MD5
fb913741b5dd4812b6d2318e258bcc46; static props no red/cream; each asset < 3000 tris; >= 0.15 from rails/walls and from felt in plan below felt+8;
8-stud head room; collision off; pivots unchanged for existing assets. Back up gen_batch3.py -> gen_batch3_rev0.py first (other rev0 backups exist in _backup_rev0).
Look at the rev0 previews in ../../previews/props_batch3/ and the concepts (open PNGs) to see what is wrong: shapes are too thin/boxy.

## Budget (props.md): per hole merged < 20k; at most 2 heavy assets (> 900 tris) per hole. Plan:
H4 heavy = h04_snowpuffs, h04_steam_vents (everything else <= 900); H6 heavy = h06_frosted_palms, h06_snowpuffs (kettle pool & lantern <= 900);
H14 heavy = h14_icicle_bell, h14_snowpuffs (gantry, buoys, bollards, sign <= 900); H18 heavy = h18_halo_arch, h18_snowpuffs (banks, lanterns, chute <= 900 each).

## Changes, in priority order
1. h14_icicle_bell (MOVER, pivot = hinge, KEEP the 2x2x2 yaw-30 collision cube envelope and the exact skid plate unchanged): real flared BRASS bell:
   lathe profile (16-24 sides) with waist, shoulder, crown and a flared lip, all inside the cube region below y 2.35 (relative to rest) and the flare/crown/
   icicles above 2.35 as allowed; a visible clapper (Brass/Iron ball on a rod) hanging inside the mouth, visible from eye height; Ice icicles on the crown
   and lip; hanger rod + yoke. Re-run the full +-9 deg sweep, report min clearance + angle.
2. h18_halo_arch: thick translucent faceted ICE ring (cross-section 8-10 sided, ~2.0-2.5 thick, faceted inner edge with chamfers), IceCore neon inner core
   strip; same feet/occluders, nothing within 8 over felt, sightline clear.
3. h18_crystal_bank_ne_deco / sw_deco: chunky glowing crystal WALLS: 8-12 fat hex crystals per bank (radius 0.5-1.0, heights 3-5, leaning), merged into a
   continuous wall, IceCore glow cores; keep the approved placement outside the outer rails.
4. h14_bell_gantry: heavy beams (legs 0.8 square, beam 1x1 as occluder), diagonal knee braces and X bracing above y 8 over the lane / outside rails below,
   thick lumpy Snow caps on beam and leg tops, brass bolts, icicles along the beam (>= 8 above felt). Approved: legs at x +-5.45.
5. Palms h04_frosted_palm_a/_b (<= 900 each) and h06_frosted_palms (3 palms, < 3000): fuller crowns: 9-12 drooping arched fronds with width, layered,
   snow dusting on top; fronds >= 8 above felt.
6. h06_kettle_pool (<= 900): chunky boulder rim (8-12 lumpy Basalt/Rock boulders around the pool edge OUTSIDE the felt and rails per clearance rules,
   plus the east rim), curling Steam wisps (twisted rising loft ribbons/puffs) over the pool.
7. h18_ramp_lanterns: taller (posts ~5-6 tall, lantern head with Glow core, brass cap); each lantern gets a separate, wider non-colliding FOOT CAP plate
   (wider than the post, sitting 0.15 above the divider top, as wide as the divider top allows while staying >= 0.15 from felt in plan) with a
   short downward lip on faces that do not face felt, so the 0.15 gap is not visible from eye height 5.5 at the tee. Never over ramp/chute felt.
8. If room: rounder snowpuffs (smooth 10-12 sided bodies, belly Snow, scarves) in all four snowpuff assets (keep each <= its current tris if possible);
   h14_buoy_float as real harbour buoys (spar/can buoys: float body with mint/violet bands, cage top, brass lamp, sitting in a snow mound) + frosted rope coil.

## NEW assets (Game Art Bot)
- h04_ice_channel_edge (<= 900): a glowing ice edge (Ice with IceCore glow strip) running along both sides of the frozen-river ice felt, OUTSIDE the rails
  (>= 0.15), low (<= 1.2 tall) so it does not violate lane rules, pivot = ice_sheen anchor.
- h04_crystal_spire (<= 900): one tall crystal spire cluster (3-5 hex spires, tallest 8-12) far enough from rails (>= 3 for tall props) and felt, placed
  where the concept shows crystal spires (pick a clear spot west or east of the slide, document it; pivot = its base centre).
- h14_rail_bollards (<= 900): 4-6 snow-capped timber bollards with brass bands, standing just outside the rails (>= 0.15) along the lane, pivot = hole
  origin (tee) or a documented point.
- h06_tee_lantern (<= 900): a brass lantern on a chunky timber post (~7-9 tall, Glow core) beside the tee outside the rails (>= 0.15, tall props >= 3 from
  rails if possible, otherwise document), like props.md's lantern post.
H6 steam on the pool: covered by item 6.

## Pipeline fixes
- finalize_batch3.py must write summary.md from facts: whether triangles.json/build_report.json came from Blender (check build_report.json fields / mtimes),
  never boilerplate "Blender was not launched". Add a "Batch 3 rev0 provenance" note: Blender 5.2 headless ran on the PC 13:29:29-13:30:37 PT (exit 0),
  19 FBX exported, 61 preview renders saved; the exported fitcheck used Blender's actual triangles; summary.md text claiming otherwise was stale boilerplate
  from the preflight; no FBX re-import check was run for rev0.
- build_batch3.py: at the end, re-import every exported FBX in a fresh scene (bpy.ops.import_scene.fbx), compare mesh/material count, triangle count
  and bounds with build_report.json, and write fbx_validation.json (this pass must include it). Keep CPU Cycles <= 16 samples.
- make_sheet05.py: label the 4th column honestly from build_report presence; add rows/columns so the new assets appear (per-hole rows are fine).
Run gen + fitcheck --preflight until ALL PASS; print a table: id, tris, heavy?, nearest rail, nearest felt, per-hole totals and heavy count.
