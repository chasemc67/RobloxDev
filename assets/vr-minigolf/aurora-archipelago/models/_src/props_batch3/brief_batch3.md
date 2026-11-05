# Aurora Archipelago props batch 3: FINAL meshes for H4, H6, H14, H18
Follow the skill roblox-minigolf-3d-modeling (in your skills dir). Course dir = ../../.. (aurora-archipelago). holes.json there is the source of truth
(MD5 fb913741b5dd4812b6d2318e258bcc46, assert it in gen). Art direction: course.md, props.md, props-full.md, hNN-notes.md, hNN-concept.png
(open the PNGs as images and look at them), paintover/h14_paint.png. Reuse the batch-2 pipeline in ../props_batch2/ (geometry.py, palette.json,
gen_batch2.py, build_batch2.py, fitcheck_batch2.py, checks.py, render_batch2.py, finalize_batch2.py): copy what you need into this folder and adapt
(paths -> props_batch3, NS=[4,6,14,18]). Reuse the existing material names/colours in palette.json (Timber, Snow, SnowShadow, Rock, Basalt, Brass, Glow,
Ice, IceCore, AuroraMint, AuroraViolet, AuroraTeal, Lime, Lagoon, Steam, Ink, Beak ...).

## HARD RULES
- DO NOT run Blender. Write the scripts only; you may run plain python (gen + preflight fitcheck on fan-triangulated parts). I launch Blender myself.
- Red and cream are reserved for moving parts: static props must not use red (#E03C31-ish, PepRed/Cherry) or cream (#FFF4E2, MoveCream, CreamTaffy).
  Snowpuff bellies on static props -> Snow #F4F6FF, not cream. Buoy stripes -> AuroraMint/AuroraViolet/Brass/Snow, not red/white-cream.
  Only h14_icicle_bell (moving part) may use red/cream accents (optional).
- Every asset < 3000 triangles total. One mesh per material. Pivot = holes.json anchor position (base centre) for static props; movers = exact holes.json pivot.
- Collision off (visual only); colliders stay holes.json.
- Clearance: >= 0.15 studs from every holes.json wall/rail box (except wall skins that intentionally fill their own collider box exactly, and the mover
  contact shape that must match its holes.json collider, as in batch 2), and >= 0.15 in plan from the felt footprint for anything between felt top and felt+8
  (8 studs head room over all felt). Exempt only flush felt cues (decals, respawn stone, ice sheen) and skins. Movers: nothing static inside their sweep +0.15.
- Stay inside each anchor's approx_size envelope (documented override boxes allowed, like batch 2) and its occluders.

## ASSETS (ids)
H4 Glissade: h04_frosted_palm_a, h04_frosted_palm_b (two palms leaning over the slide from outside the west rail, region of anchor frosted_palms, teal fronds dusted
  white, curved segmented trunks, fronds >= 8 above felt); h04_steam_vents (small basalt vents with Steam puffs, outside east rail); h04_snowpuffs (2-3 round
  puffin figures on a snow bank by the green: Ink body, Snow belly, Beak orange, knitted scarf in AuroraTeal/AuroraViolet).
H6 Palm Lagoon: h06_kettle_pool (Lagoon water surface in the pool footprint + basalt rim on the far east side under the rail, steam wisps), h06_frosted_palms
  (3 palms on the east rim leaning over the pool, fronds >= 8 above felt), h06_snowpuffs (foot-bath with steam, snowpuffs), h06_respawn_stone (flush Lime stone).
H14 Bell Buoy: h14_bell_gantry (timber gantry, legs outside rails at x +-5, beam y 10.35..11.35, icicles hang from the beam only, >= 8 above felt, Brass fittings,
  Snow caps), h14_icicle_bell (MOVING: pivot = hinge [0,10.35,-24]; match props.md contact shape exactly: bell body inside 2x2x2 cube 9.0 below hinge yaw 30,
  flare/icicles only above y 2.35, skid plate per props.md, hanger; check the full +-9 deg sweep, report min felt/rail clearance and angle),
  h14_buoy_float (2 striped harbour buoys + frosted rope coil outside the green's east rail), h14_snowpuffs (puffs ringing hand-bells outside west of the green),
  h14_safe_side_sign (lantern sign).
H18 Halo Arch: h18_halo_arch (46 wide x 34 tall translucent Ice arch with IceCore neon core, feet outside the play area per anchor notes, nothing within 8 over felt,
  keep tee-eye(5.5)->flag-top sightline clear), h18_crystal_bank_ne_deco and h18_crystal_bank_sw_deco (faceted Ice crystal clusters 3-5 tall behind the
  backing rails, IceCore glow), h18_crystal_chute (glowing ice-crystal wall skins on the chute rails, filling their collider boxes exactly, no lips into the
  1.6-wide chute), h18_ramp_lanterns (brass lanterns on short posts on top of the chute divider, posts 0.6 wide, never over ramp/chute felt), h18_snowpuffs
  (grandstand of snow blocks with snowpuffs).
If an anchor note conflicts with these rules, follow holes.json and the rules, and write the conflict in the notes.

## DELIVERABLES (in this folder)
gen_batch3.py -> parts.json (+ palette.json); fitcheck_batch3.py (gates above; runs on triangles.json from Blender, or with --preflight on fan-triangulated parts.json,
writes fitcheck report text with per-asset tris, nearest rail and nearest felt clearance, head-room hits, sweep minima, ALL PASS line);
build_batch3.py (Blender 5.2 headless, CPU only: FBX per asset to ../../fbx/props_batch3/<id>.fbx forward -Z up Y scale 1, embed textures, root empty at pivot,
one mesh per material named <id>__<Material>; triangles.json; build_report.json; props_batch3.blend; CPU Cycles previews at most 16 samples 1024x768 to
../../previews/props_batch3/<id>_front.png, <id>_34.png, <id>_eye.png (eye height 5.5 from the tee side)); finalize_batch3.py (plain python: writes
../../../props_batch3_manifest.json in the batch-2 manifest format incl. world pivots, and ../../fitcheck_props_batch3.txt); make_sheet05.py (plain python+PIL:
silhouette sheet per hole: concept crop | front silhouette | side silhouette | 3/4 preview, saved to ../../../silhouettes/sheet05-batch3-h04-h06-h14-h18.png).
Run gen and the preflight fitcheck until ALL PASS. Print a summary table at the end.
