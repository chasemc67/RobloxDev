# Lantern Grove props: pass 1 summary (2026-10-09)

## Built (65 FBX, all P1 + P2 + P3)

**P1 moving parts** (origin = pivot, axis aligned, checked against the holes.json blockers):
- `h4_carousel_bar` (rotate +Y, 36°/s)
- `h6_mill_wheel` (rotate +Z, 30°/s)
- `h7_floating_log` (slide +X ±6)
- `h9_root_portcullis` (slide +Y 0..1.2)
- `h9_lantern_bar` (rotate +Y, 40°/s)
- `h8_root_door` (slide +Z ±2.5, from the H8 notes)

Static companions: `toadstool_hub_static`, `h6_wheel_trestle`, `h9_lantern_post_static`.

**P1 hero props:**
- `hollow_tree`
- `mushroom_house_large_tunnel`
- `mushroom_house_medium` (one model for H3/H4; recolour the cap)
- `lantern_torii_gate`
- `water_mill_house`
- `root_bridge_arched`
- `covered_bridge`
- `waterfall_cascade_3step`
- `waterfall_small`
- `firefly_ring_entry` and `firefly_ring_exit`
- `giant_acorn` and `stump_cladding`
- `toadstool_stool`
- `root_arch_large`
- `heart_lantern_cluster`

**P1 modules:**
- Lanterns: `lantern_small` / `lantern_medium` / `lantern_large`, `lantern_post`, `tee_sign_h01`..`h09`
- Rail kit: `rail_straight_4`, `rail_straight_2`, `rail_corner_45`, `rail_corner_90`, `rail_end_post`
- Walls and edges: `timber_deflector_board`, `bank_backing_stone`, `drop_face_stone`
- Water: `water_surface`, `stream_bank_rocks`

**P2:**
- `trunk_tunnel_arch`, `lantern_knot`, `heart_well_rim`, `rabbit_hole_rim`, `lantern_string`
- `red_maple_tree`, `golden_birch_tree`, `mossy_boulder`
- `toadstool_cluster`, `glowing_mushrooms`, `welcome_sign`

**P3:** `fern_clump`, `red_leaf_bush`, `leaf_pile`, `flour_sacks_crates`, `squirrel_hut`, `stepping_stones`.

**Triangles:** 84k in total. The heaviest prop is `heart_lantern_cluster` at 6.5k tris, and the heaviest hero is `covered_bridge` at 4.9k. Most small props are under 1k.

**Outputs:** every prop has an FBX, an eye preview and a 3/4 preview. Also produced:
- `contact_sheet.png`
- `manifest.json`, with placements in hole-local coordinates, per-part colour/material and pivot offsets
- `README.md`
- `lantern_grove_props.blend`
- `previews/assembly_hNN{,_tee,_top}.png` for all 9 holes

**Rebuild:** `models/_src/build.sh [--assembly]`.

## Review passes
- **Pass 1** (contact sheet, assemblies, bbox vs props.md). Fixes made:
  - The hollow tree trunk had been deleted by a boolean. The trunk is now its own mesh, and it was resized so it fits the H9 cavity.
  - The cascade and small waterfall rocks were spiky spires. They are now boxy terraces.
  - The tunnel house looked like a face. The windows were rearranged and a ground door added; its eye view now looks down the tunnel.
  - The lanterns were reduced from 592 to 336 tris, with a 100-tri version for clusters. That cut `heart_lantern_cluster` from 20.8k to 6.5k tris.
  - The H5 water was hidden under the ground plane in the assembly render. Fixed.
  - The mill was tightened and the squirrel hut widened.
- **Pass 2** (full rebuild, tee/top assemblies, numeric `fitcheck.py`): all 17 checks pass.
  - Tunnel opening clear at 7 wide x 3 high x 5 deep.
  - Torii posts outside the rails (min |x| 4.07).
  - Root bridge never rises above the felt; deck at least 2.2 wide.
  - Covered bridge interior clear.
  - Log, gate and door stay inside their blockers.
  - The carousel and lantern bar below ball height stay inside their blockers.
  - Only the 2 paddles of the mill wheel sweep the felt, and its axle reaches the mill wall.
  - H9 rails sit inside the tree cavity, and the tunnel is open.

## Missing / not done
- No textures (flat colours only, by design). No LODs. No collision meshes (by design).
- No animated water. The fall sheets are static meshes; use Beams/ParticleEmitters for motion.
- Not imported into Studio from here: the import scale (Stud) and pivot behaviour still need checking in Studio.

## Known issues
- **Size deviations** (justified in the README):
  - `hollow_tree` is about 49 x 57 x 59, against 34 x 60 x 34 in props.md. The H9 play area needs a 46-deep trunk.
  - The mill wheel's z is 12.2 because the axle runs to the wall.
  - `firefly_ring_entry` is 4 x 4 x 4.8.
  - `trunk_tunnel_arch` has z 9.2.
  - `root_bridge_arched` has y 3.4.
- **props.md vs holes.json conflict** on the mill wheel: props.md says pivot (12.5, 3.6, -12.5) with 3 paddles. I followed holes.json: pivot (7.5, 3.6, -8.5) with 2 paddles.
- **Mill house placement:** moved to [8.5, -1, 3], away from the anchor [7.5, 0, 0], to clear the millrace and rail2.
- **H6 rail notch:** the wheel passes through the visual north rail at x 5..10, so that rail needs a notch.
- **Lantern glow:** the glow needs PointLights (and paper transparency at night) to read in Roblox.
