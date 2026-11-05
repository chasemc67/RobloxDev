## World pieces

Pass 3 adds world-scale background meshes for the continuous world in `../world/` (world.json, terrain, placements). They live in `models/world/`:

| Path | What |
|---|---|
| `world/fbx/<id>.fbx`, `world/fbx/<id>_partN.fbx` | One FBX per piece, or several parts that share one origin (every file < 20k tris) |
| `world/manifest.json` | Every piece: files, parts (role, tris, bbox, meshes/materials), origin, notes, **instances** (world pos / yaw / scale) |
| `world/layout.json` | Just the instances (written by `_src/world_layout.py`) |
| `world/previews/<id>_34.png` (+ `hollow_tree_world_shell_door/cutaway/top_fit.png`) | Piece previews |
| `world/previews/vista_*.png` | World vistas over a preview-only terrain mesh (holes as felt boxes) |
| `world/contact_sheet_world.png` | All previews + vistas |
| `world/fitcheck_world.txt` | Hero tree vs H8/H9/walkways fit check (`_src/world_fitcheck.py`) |

**Import (RobloxDevBot):**

1. File > Import 3D each FBX with the **scale unit Stud** (same as the props), keep the hierarchy: one Model per file, one MeshPart per material `<part>__<Material>`. Set Color/Material/Transparency from the material table above (new world materials are listed below). Anchored, `CanCollide = CanQuery = CanTouch = false` (all decoration).
2. **Positions are world studs** (+X east, +Y up, -Z north, the same frame as world.json and the placed holes), and they are the **base centre** of the piece (exceptions are in the `origin` column). Every part of a multi-part piece has the same origin, so put the parts in one Model and pivot the Model.
3. Place each instance with `Model:PivotTo(CFrame.new(pos[1], pos[2], pos[3]) * CFrame.Angles(0, math.rad(yaw), 0))`. If the pivot did not survive import, set `Model.WorldPivot` to the FBX origin first (see Pivot above: `bbox_center_from_origin` per part is in world/manifest.json). `scale` [sx, sy, sz]: equal values -> `Model:ScaleTo(s)`; otherwise scale each MeshPart's Size and its offset from the pivot per axis (rock kits, tree line, hills and mountains are fine with this).
4. Far pieces (mountains, far hills, clouds, tree line): `CastShadow = false`, `RenderFidelity = Performance`. Neon parts (Glow) get PointLights only on the hero tree and near pieces.
5. Hero tree extras: SurfaceLight / Beam light shaft from the oculus (r 14, top of the hollow at y 117.6) down onto H9; PointLights in the lanterns of `hollow_tree_world_shell_part6/7` and `hollow_tree_crown_part1`.

**Hero tree origin**: `hollow_tree_world_shell` origin = trunk base centre **[-74, 39.6, 6]** (yaw 0): local y 0 = the H9 floor (terrain 39.6). The skirt goes 4.6 below it so the shell meets uneven terrain. Door at map angle 53.1 deg (atan2(dz, dx)). `hollow_tree_crown` origin = crown base centre **[-74, 139.6, 6]**; its limbs dip 3 below it into the trunk top. H9 needs no change: place the holes as in world/README.md.

New materials (world pieces only):

| Material | Colour | Roblox Material | Transparency | Texture |
|---|---|---|---|---|
| `Heartwood` | `#B9783F` | Wood | 0 | textures/heartwood.png (tile 12 on the shell) |
| `MountainFoot` | `#EDC6A8` | SmoothPlastic | 0 | (flat) = horizon sky haze |
| `MountainPeach` | `#D8A38E` | SmoothPlastic | 0 | (flat) |
| `MountainMauve` | `#AE8890` | SmoothPlastic | 0 | (flat) |
| `MountainSnow` | `#F8EDE6` | SmoothPlastic | 0 | (flat) |
| `SkyPaper` | `#F6A04A` | SmoothPlastic | 0 | textures/paper_glow.png, self-lit (SurfaceAppearance ColorMap; Neon-like glow via PointLight) |
| `Cloud` | `#FFE6BE` | SmoothPlastic | 0 | (flat) |
| `CloudShade` | `#E9B7A4` | SmoothPlastic | 0 | (flat) |
| `Mist` | `#F3F7F8` | SmoothPlastic | 0.45 | (flat) |

Textures: world pieces reuse `textures/*.png` with bigger tiles (`texture_tile_scale` per part: x3 for the trunk shell, x4 for the crown, x2-8 for the rest), so bark and leaves keep a sensible size at world scale.

| Piece | Kind | Files | Tris (max part) | Size [x,y,z] | Instances | Origin |
|---|---|---|---|---|---|---|
| **hollow_tree_world_shell** | hero_tree | `hollow_tree_world_shell_part1.fbx` .. `hollow_tree_world_shell_part8.fbx` (8) | 76952 (16660) | [127.85, 107.22, 124.56] | 1 | trunk base centre [-74, 39.6, 6] (world.json hollow_tree.center); yaw 0 |
| **hollow_tree_crown** | hero_tree | `hollow_tree_crown_part1.fbx` .. `hollow_tree_crown_part6.fbx` (6) | 61956 (16640) | [176, 81, 176] | 1 | crown base centre [-74, 139.6, 6] (= trunk base + 100); limbs dip ~4 below it into the trunk top |
| **sister_tree_nw** | background | `sister_tree_nw.fbx` | 19202 (19202) | [60, 90, 60] | 1 | base centre (pos = world base centre) |
| **sister_tree_sw** | background | `sister_tree_sw.fbx` | 16294 (16294) | [55, 80, 55] | 1 | base centre (pos = world base centre) |
| **sister_tree_ne** | background | `sister_tree_ne.fbx` | 16542 (16542) | [50, 75, 50] | 1 | base centre (pos = world base centre) |
| **grand_falls_curtain** | waterfall | `grand_falls_curtain.fbx` | 3102 (3102) | [22.13, 46.79, 15.34] | 1 | plunge-pool centre at the bottom water level (world.json pos); local +Z = flow direction |
| **twin_falls_curtain** | waterfall | `twin_falls_curtain.fbx` | 3592 (3592) | [22.7, 12.6, 8.55] | 1 | plunge-pool centre at the bottom water level (world.json pos); local +Z = flow direction |
| **lantern_falls_curtain** | waterfall | `lantern_falls_curtain.fbx` | 3918 (3918) | [21.49, 24.88, 12.94] | 1 | plunge-pool centre at the bottom water level (world.json pos); local +Z = flow direction |
| **highland_cliff_kit_a** | rock | `highland_cliff_kit_a.fbx` | 1780 (1780) | [43.31, 36.59, 18.22] | 3 | base centre of the face (foot of the scarp); front local +Z |
| **highland_cliff_kit_b** | rock | `highland_cliff_kit_b.fbx` | 1000 (1000) | [40.8, 32.9, 14.49] | 3 | base centre of the face (foot of the scarp); front local +Z |
| **highland_cliff_kit_c** | rock | `highland_cliff_kit_c.fbx` | 1756 (1756) | [43.55, 35.82, 17.13] | 3 | base centre of the face (foot of the scarp); front local +Z |
| **highland_cliff_kit_d** | rock | `highland_cliff_kit_d.fbx` | 1820 (1820) | [25.63, 35.19, 25.07] | 3 | base centre of the face (foot of the scarp); front local +Z |
| **terrace_rock_faces_a** | rock | `terrace_rock_faces_a.fbx` | 1780 (1780) | [25.88, 13.57, 7.15] | 7 | base centre (foot of the wall); front local +Z |
| **terrace_rock_faces_b** | rock | `terrace_rock_faces_b.fbx` | 1776 (1776) | [26.21, 13.9, 7.81] | 7 | base centre (foot of the wall); front local +Z |
| **terrace_rock_faces_c** | rock | `terrace_rock_faces_c.fbx` | 920 (920) | [24.77, 14, 6.12] | 6 | base centre (foot of the wall); front local +Z |
| **old_lantern_tower** | background | `old_lantern_tower.fbx` | 7860 (7860) | [16.39, 38.3, 16.22] | 1 | base centre (pos = world base centre) |
| **hill_mushroom_houses** | background | `hill_mushroom_houses.fbx` | 16448 (16448) | [27.28, 20.11, 28.71] | 1 | base centre (pos = world base centre) |
| **mere_dock** | decor | `mere_dock.fbx` | 1780 (1780) | [14.64, 6.3, 4.85] | 1 | water-line reference: deck top at local y 0.86 (world 9.36, water 8) |
| **mere_lantern_boat** | decor | `mere_lantern_boat.fbx` | 380 (380) | [2.9, 1.87, 6] | 8 | waterline centre |
| **sky_lantern** | sky | `sky_lantern.fbx` | 250 (250) | [1.1, 1.37, 1.1] | 24 | bottom centre |
| **cloud_card_a** | sky | `cloud_card_a.fbx` | 3388 (3388) | [600, 120, 200] | 4 | base centre (pos = world base centre) |
| **cloud_card_b** | sky | `cloud_card_b.fbx` | 3388 (3388) | [520, 140, 180] | 3 | base centre (pos = world base centre) |
| **treeline_clump_a_gold_orange** | tree_line | `treeline_clump_a_gold_orange.fbx` | 2812 (2812) | [40, 48, 40] | 6 | base centre; trunks reach 3 below |
| **treeline_clump_a_red_orange** | tree_line | `treeline_clump_a_red_orange.fbx` | 2812 (2812) | [40, 48, 40] | 6 | base centre; trunks reach 3 below |
| **treeline_clump_a_red_gold** | tree_line | `treeline_clump_a_red_gold.fbx` | 2812 (2812) | [40, 48, 40] | 5 | base centre; trunks reach 3 below |
| **treeline_clump_a_gold_green** | tree_line | `treeline_clump_a_gold_green.fbx` | 2812 (2812) | [40, 48, 40] | 2 | base centre; trunks reach 3 below |
| **treeline_clump_b_gold_orange** | tree_line | `treeline_clump_b_gold_orange.fbx` | 3848 (3848) | [40, 48, 40] | 6 | base centre; trunks reach 3 below |
| **treeline_clump_b_red_orange** | tree_line | `treeline_clump_b_red_orange.fbx` | 3848 (3848) | [40, 48, 40] | 4 | base centre; trunks reach 3 below |
| **treeline_clump_b_red_gold** | tree_line | `treeline_clump_b_red_gold.fbx` | 3848 (3848) | [40, 48, 40] | 6 | base centre; trunks reach 3 below |
| **treeline_clump_b_gold_green** | tree_line | `treeline_clump_b_gold_green.fbx` | 3848 (3848) | [40, 48, 40] | 3 | base centre; trunks reach 3 below |
| **treeline_clump_c_gold_orange** | tree_line | `treeline_clump_c_gold_orange.fbx` | 1890 (1890) | [40, 48, 40] | 2 | base centre; trunks reach 3 below |
| **treeline_clump_c_red_orange** | tree_line | `treeline_clump_c_red_orange.fbx` | 1890 (1890) | [40, 48, 40] | 10 | base centre; trunks reach 3 below |
| **treeline_clump_c_red_gold** | tree_line | `treeline_clump_c_red_gold.fbx` | 1890 (1890) | [40, 48, 40] | 3 | base centre; trunks reach 3 below |
| **treeline_clump_c_gold_green** | tree_line | `treeline_clump_c_gold_green.fbx` | 1890 (1890) | [40, 48, 40] | 3 | base centre; trunks reach 3 below |
| **far_hill_a** | far_hill | `far_hill_a.fbx` | 13008 (13008) | [280, 100, 160] | 9 | base centre (pos = world base centre) |
| **far_hill_b** | far_hill | `far_hill_b.fbx` | 12048 (12048) | [280, 100, 160] | 9 | base centre (pos = world base centre) |
| **mountain_a** | mountain | `mountain_a.fbx` | 440 (440) | [500, 320, 300] | 4 | base centre (pos = world base centre) |
| **mountain_b** | mountain | `mountain_b.fbx` | 440 (440) | [500, 320, 300] | 4 | base centre (pos = world base centre) |
| **mountain_c** | mountain | `mountain_c.fbx` | 440 (440) | [500, 320, 300] | 4 | base centre (pos = world base centre) |

- **hollow_tree_world_shell**: Giant hollow trunk shell around H9: outer r 45.84 (flared base), inner r 38.84, 100 tall, hollow up to y+78 under a dome with a 14-radius oculus shaft open through the top. Heartwood Door: 14 wide x 20 high arch at map angle 53.1 deg (splays to 17.5 wide inside). Parts 1-4 = trunk wall sectors (bark outside, warm Heartwood inside), 5 = buttress roots (to r 65.8, trimmed so they never touch H8/H9 felt, walls, walkways or lantern posts), 6 = outer details (door frame + lanterns, glowing windows, bracket fungi, moss), 7 = interior lantern strings / wall lanterns / glowing mushrooms (all far above or outside H9).
- **hollow_tree_crown**: Golden/orange crown: 7 lumpy leaf masses (6 in a ring leaving a ~16-radius light gap over the oculus, 1 high mass west of it), limbs rising from the trunk-top rim, 12 big hanging lanterns under the outer crown.
- **sister_tree_nw**: Golden cousin of the hero tree (hollow_tree look: furrowed bark, buttress roots, lumpy masses) with a glowing arched door and windows facing local +Z.
- **sister_tree_sw**: Red maple giant on the SW hills.
- **sister_tree_ne**: Squat golden oak giant on the NE shoulder above the village.
- **grand_falls_curtain**: Grand Falls curtain [114, 77.8, -205] -> [112, 39.0, -199]: translucent Water sheet (thin closed slab), Foam ribbons, plunge foam + Mist puffs, backing slate slab and lip/base rocks. Add a Beam/ParticleEmitter mist at the bottom in Studio.
- **twin_falls_curtain**: Twin Falls curtain [77.5, 37.0, -90] -> [76, 29.8, -86]: translucent Water sheet (thin closed slab), Foam ribbons, plunge foam + Mist puffs, backing slate slab and lip/base rocks, two strands split by a rock. Add a Beam/ParticleEmitter mist at the bottom in Studio.
- **lantern_falls_curtain**: Lantern Falls curtain [38, 22.2, 57] -> [36, 9.2, 62]: translucent Water sheet (thin closed slab), Foam ribbons, plunge foam + Mist puffs, backing slate slab and lip/base rocks, lantern posts at the lip and floating lanterns at the base. Add a Beam/ParticleEmitter mist at the bottom in Studio.
- **highland_cliff_kit_a**: Highland slate cliff face, style 'strata' (40 x 30 x 14 unscaled), mossy ledges, autumn shrubs on the lip. Front = local +Z. Scale per instance (sy = scarp height / 30, sx = sz = sqrt(sy)).
- **highland_cliff_kit_b**: Highland slate cliff face, style 'columns' (40 x 30 x 14 unscaled), mossy ledges, autumn shrubs on the lip. Front = local +Z. Scale per instance (sy = scarp height / 30, sx = sz = sqrt(sy)).
- **highland_cliff_kit_c**: Highland slate cliff face, style 'overhang' (40 x 30 x 14 unscaled), mossy ledges, autumn shrubs on the lip. Front = local +Z. Scale per instance (sy = scarp height / 30, sx = sz = sqrt(sy)).
- **highland_cliff_kit_d**: Highland slate cliff face, style 'corner' (40 x 30 x 14 unscaled), mossy ledges, autumn shrubs on the lip. Front = local +Z. Scale per instance (sy = scarp height / 30, sx = sz = sqrt(sy)).
- **terrace_rock_faces_a**: Terrace rock facing, style 'strata' (24 x 12 x 6 unscaled) for the village / mill / root terrace walls and the tree mound. Front = local +Z.
- **terrace_rock_faces_b**: Terrace rock facing, style 'overhang' (24 x 12 x 6 unscaled) for the village / mill / root terrace walls and the tree mound. Front = local +Z.
- **terrace_rock_faces_c**: Terrace rock facing, style 'columns' (24 x 12 x 6 unscaled) for the village / mill / root terrace walls and the tree mound. Front = local +Z.
- **old_lantern_tower**: Ruined octagonal stone tower (NE side broken away), timber loft with a shingle roof and a big amber lantern, glowing slit windows, ivy moss and rubble. Door faces local +Z.
- **hill_mushroom_houses**: 4 mushroom houses (scaled mushroom_house_medium, red / orange / gold caps) with lit windows, toadstools, a lantern string and path stones.
- **mere_dock**: Plank dock on pilings, two lantern posts at the water end (local -X), rope coil and crate. Pilings reach 2.7 below the deck reference.
- **mere_lantern_boat**: Tiny paper boat carrying a paper lantern (Glow core). 8 instances drifting on Lantern Mere.
- **sky_lantern**: Pass 4: small round paper sky lantern 1.1 x 1.35 x 1.1, glowing washi texture (SkyPaper = textures/paper_glow.png, self-lit) with a Glow flame at the open bottom. 24 instances around the crown (drift upward).
- **cloud_card_a**: Golden cumulus card (13 sunlit puffs + 7 peach underside puffs), 600 x 120 x 200. Faces the play area.
- **cloud_card_b**: Cumulus card variant.
- **treeline_clump_a_gold_orange**: Tree-line clump variant a (4 round crowns), colour mix gold+orange, 40 x 45 x 40 unscaled (scale y to the world.json size).
- **treeline_clump_b_gold_orange**: Tree-line clump variant b (6 mixed + a spire), colour mix gold+orange, 40 x 45 x 40 unscaled (scale y to the world.json size).
- **treeline_clump_c_gold_orange**: Tree-line clump variant c (5 tall layered), colour mix gold+orange, 40 x 45 x 40 unscaled (scale y to the world.json size).
- **far_hill_a**: Far forested hill impostor shell (single dome), 280 x 100 x 160 unscaled, open bottom, autumn patches + canopy bumps. Long axis local X.
- **far_hill_b**: Far forested hill impostor shell (double hump), 280 x 100 x 160 unscaled, open bottom, autumn patches + canopy bumps. Long axis local X.
- **mountain_a**: Low-poly distant mountain silhouette (pass 4 colours): foot = horizon haze #EDC6A8 (fades into the sky), hazy peach slopes, dusty mauve ridges, warm-white snowcaps; 500 x 320 x 300 unscaled. Long axis local X.
- **mountain_b**: Low-poly distant mountain silhouette (pass 4 colours): foot = horizon haze #EDC6A8 (fades into the sky), hazy peach slopes, dusty mauve ridges, warm-white snowcaps; 500 x 320 x 300 unscaled. Long axis local X.
- **mountain_c**: Low-poly distant mountain silhouette (pass 4 colours): foot = horizon haze #EDC6A8 (fades into the sky), hazy peach slopes, dusty mauve ridges, warm-white snowcaps; 500 x 320 x 300 unscaled. Long axis local X.

### Hero tree fit check (`_src/world_fitcheck.py`)

```
Hero tree fit vs H8/H9 (holes.json transformed with world.json placements) and walkways p_h7_h8/p_h8_h9
keep-out boxes: 194 hole elements, 19 walkway segments, 12 lantern posts

PASS  hollow_tree_world_shell_part1.fbx: 7734 tris, no triangle inside any H8/H9/walkway/post keep-out
PASS  hollow_tree_world_shell_part2.fbx: 7845 tris, no triangle inside any H8/H9/walkway/post keep-out
PASS  hollow_tree_world_shell_part3.fbx: 7848 tris, no triangle inside any H8/H9/walkway/post keep-out
PASS  hollow_tree_world_shell_part4.fbx: 7843 tris, no triangle inside any H8/H9/walkway/post keep-out
PASS  hollow_tree_world_shell_part5.fbx: 6848 tris, no triangle inside any H8/H9/walkway/post keep-out
PASS  hollow_tree_world_shell_part6.fbx: 8748 tris, no triangle inside any H8/H9/walkway/post keep-out
PASS  hollow_tree_world_shell_part7.fbx: 13426 tris, no triangle inside any H8/H9/walkway/post keep-out
PASS  hollow_tree_world_shell_part8.fbx: 16660 tris, no triangle inside any H8/H9/walkway/post keep-out
PASS  hollow_tree_crown_part1.fbx: 5796 tris, no triangle inside any H8/H9/walkway/post keep-out
PASS  hollow_tree_crown_part2.fbx: 16640 tris, no triangle inside any H8/H9/walkway/post keep-out
PASS  hollow_tree_crown_part3.fbx: 16640 tris, no triangle inside any H8/H9/walkway/post keep-out
PASS  hollow_tree_crown_part4.fbx: 16640 tris, no triangle inside any H8/H9/walkway/post keep-out
PASS  hollow_tree_crown_part5.fbx: 4160 tris, no triangle inside any H8/H9/walkway/post keep-out
PASS  hollow_tree_crown_part6.fbx: 2080 tris, no triangle inside any H8/H9/walkway/post keep-out
PASS  inner wall (lowest 8 studs, outside the door bore) r >= H9 footprint r + 4.5  (inner wall min r 39.15, H9 felt+walls max r 33.84, walking room 5.31)
PASS  Heartwood Door: 30 rays along p_h8_h9 (15.6 studs from [-44.7, 39.6, 45.1] through the arch to [-54.1, 39.6, 32.6], 7 wide, up to 11 high) are unobstructed
PASS  door opening at the outer face ~14 wide x ~20 high  (free width 14.00 at 1 above the floor, free height 20.00 at the centreline)
PASS  negative test flagged: triangle on H9 lane felt  (H9:felt:lane)
PASS  negative test flagged: triangle in the lantern-bar sweep  (H9:felt:chamber, sweep:lantern_bar)
PASS  negative test flagged: triangle in the door corridor at 9 studs  (path:p_h8_h9:6:walk)

PASS  grand_falls_curtain x1: clear of every hole, walkway and lantern post
PASS  highland_cliff_kit_a x3: clear of every hole, walkway and lantern post
PASS  highland_cliff_kit_b x3: clear of every hole, walkway and lantern post
PASS  highland_cliff_kit_c x3: clear of every hole, walkway and lantern post
PASS  highland_cliff_kit_d x3: clear of every hole, walkway and lantern post
PASS  hill_mushroom_houses x1: clear of every hole, walkway and lantern post
PASS  lantern_falls_curtain x1: clear of every hole, walkway and lantern post
PASS  mere_dock x1: clear of every hole, walkway and lantern post
PASS  old_lantern_tower x1: clear of every hole, walkway and lantern post
PASS  sister_tree_ne x1: clear of every hole, walkway and lantern post
PASS  sister_tree_nw x1: clear of every hole, walkway and lantern post
PASS  sister_tree_sw x1: clear of every hole, walkway and lantern post
PASS  terrace_rock_faces_a x7: clear of every hole, walkway and lantern post
PASS  terrace_rock_faces_b x7: clear of every hole, walkway and lantern post
PASS  terrace_rock_faces_c x6: clear of every hole, walkway and lantern post
PASS  twin_falls_curtain x1: clear of every hole, walkway and lantern post

PASS  all 51 world FBX files < 20k tris

ALL PASS
```

Rebuild: `python3 _src/world_layout.py && blender -b -P _src/world_build.py && blender -b -P _src/world_fitcheck.py && blender -b -P _src/world_vista.py && python3 _src/world_docs.py && python3 _src/make_docs.py` (or `_src/build_world.sh`).

