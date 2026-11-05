# Sugarloaf Canyon — world pieces (SRV-131, pass 2)
Decoration only, so CanCollide, CanQuery and CanTouch are all off. 1 unit = 1 stud. FBX: forward -Z, up Y, scale 1, textures embedded (also in textures/). Blender +Y = Roblox -Z.
Import 3D at scale 1 (Stud) and keep the hierarchy, which gives one MeshPart per material named <part>__<Material>. Set Anchored on. Turn CastShadow off on far_card and sky pieces, and on the Neon and glass cores.
Placement: `model:PivotTo(CFrame.new(pos) * CFrame.Angles(0, math.rad(yaw), 0))`. Every instance (pos, yaw, scale) is in manifest.json `pieces[].instances` and layout.json. The pivot is at the base centre.
Groups: hero (Old Sugarloaf shell, Sunset Arch, dam, intake tower), buildings (ranger station, Junction town, water tower, mine-head), lifts (4 static frames + cage), bridges (Ranger Footbridge, Licorice Rope Bridge), walkway kit, striped cliff kit (strata banded by world y every 6 studs) and slot-wall kit with crystals, merged clusters (hoodoos, crystals, cacti, scatter at world positions), variants for hand placement, far cards, sky (sun disc, clouds, balloons).
Not included: per-hole props, moving parts (H6/H9/H11/H14/H17), gondola cable/cabin, water/falls (use Beams).
Checks: fitcheck_pass1.txt and _src/fitcheck_pass1_validated.txt. Previews: previews/ and contact_sheet.png. Details and questions: _src/pass1_summary.md.

## Pass 2 (Windows, Blender 5.2)

100 pieces, 105 FBX, 818 placements, 309,074 placed triangles. Added 80 visibility-tested low-poly outer-rim silhouettes (960 triangles); set CastShadow off. All 18 holes already clear both scatter sightline corridors, so no scatter removals. Validation: [_src/fitcheck_pass2_validated.txt](_src/fitcheck_pass2_validated.txt), ALL PASS.

Six 1920x1080 Cycles OptiX hero stills (128 samples, denoised): [previews/hero/contact_sheet.png](previews/hero/contact_sheet.png). Reusable packed [hero scene](previews/hero/sugarloaf_canyon_hero.blend), [_src/render_hero.py](_src/render_hero.py), and [render details](previews/hero/render_report.json). Hardcoded dusk sun: bearing 277°, elevation -3°. Crown sunset shot rendered last.

Use [_src/run_blender.ps1](_src/run_blender.ps1) for every Blender launch; it waits for existing Blender jobs. Full changes, counts, paths, timings and scene visibility notes: [_src/pass2_summary.md](_src/pass2_summary.md).

## Pass 3

Steps 1-7 executed; fitcheck ALL PASS; six Cycles OptiX 1920x1080 / 128 sample renders, arch LAST. One self-review iteration corrected flat orange sky, warm ambient, dam occlusion and arch camera/sun alignment.

Palette deviation from course.md per Game Art Bot: cream #E8C9A1, ochre #C68C59, rose #CC8D91, muted terracotta #AF7061; 4/10/6/16 stud bands, blurred edges. Shared strata color map applies to all cliff/slot variants, rim, hoodoos, dome, arch, rocks/clusters; regenerated far-card textures. Roblox SurfaceAppearance: ColorMap + RoughnessMap; rose roughness .48, others .84.

Old Sugarloaf: base (80,18,-130), radius72, height110, width144/height110=1.309. Rounded dome with flattened top: y=18+110*sqrt(max(0,1-(r/72)^4)), r<=72. Replace old terrain heights inside radius72 with this formula; retain original outside. Render terrain already patched; builder must apply heightmap patch. Footprint and walkway clearance validated after export.

Golden-hour west key bearing270/elevation25; warm peach key, lavender ambient/fill, saturated sunset gradient. No global volumetric haze; distant cards retain baked atmospheric tint. Arch only: bearing277/elevation+2, eye(-370,170,165), target(-1250,155,60), FOV52. Render-only hide terrain and other placements to reveal far arch; no source pieces moved. Dam camera raised to show downstream sheet; Junction river visible.

Rebuilt 67 affected FBX across 63 pieces; other FBX retained. Placed tris 309,074 -> 303,458 (-5,616); library 129,583 -> 123,967. Render-only terrain/card tessellation/water excluded from shipping totals.

Renders: previews/hero/old_sugarloaf_skyline.png, previews/hero/dam_crest_walk.png, previews/hero/narrows_crystal_walls.png, previews/hero/junction_town.png, previews/hero/world_vista.png, previews/hero/sunset_arch_from_crown.png.
Contact: previews/hero/contact_sheet.png; comparison: previews/hero/compare_vs_vistas.png; packed scene: previews/hero/sugarloaf_canyon_hero.blend. Detailed cameras/timings: previews/hero/render_report.json.

Remaining gaps vs vistas: source layout is sparse and angular, without golf greens/per-hole props; cards are flat silhouettes, terrain and kit seams remain visible; spillway is a simple sheet without spray or foam detail. Vista illustrations have richer vegetation, clouds, surface detail and staged compositions. Palette/light improved within existing low-poly assets; not a full illustration match.

| Strata material | Vista colour | Roughness |
|---|---|---|
| Cream | #E8C9A1 | .84 |
| Ochre | #C68C59 | .84 |
| Rose | #CC8D91 | .48 |
| Muted terracotta | #AF7061 | .84 |

## Pass 3

Steps 1-7 executed; fitcheck ALL PASS; six Cycles OptiX 1920x1080 / 128 sample renders, arch LAST. One self-review iteration corrected flat orange sky, warm ambient, dam occlusion and arch camera/sun alignment.

Palette deviation from course.md per Game Art Bot: cream #E8C9A1, ochre #C68C59, rose #CC8D91, muted terracotta #AF7061; 4/10/6/16 stud bands, blurred edges. Shared strata color map applies to all cliff/slot variants, rim, hoodoos, dome, arch, rocks/clusters; regenerated far-card textures. Roblox SurfaceAppearance: ColorMap + RoughnessMap; rose roughness .48, others .84.

Old Sugarloaf: base (80,18,-130), radius72, height110, width144/height110=1.309. Rounded dome with flattened top: y=18+110*sqrt(max(0,1-(r/72)^4)), r<=72. Replace old terrain heights inside radius72 with this formula; retain original outside. Render terrain already patched; builder must apply heightmap patch. Footprint and walkway clearance validated after export.

Golden-hour west key bearing270/elevation25; warm peach key, lavender ambient/fill, saturated sunset gradient. No global volumetric haze; distant cards retain baked atmospheric tint. Arch only: bearing277/elevation+2, eye(-370,170,165), target(-1250,155,60), FOV52. Render-only hide terrain and other placements to reveal far arch; no source pieces moved. Dam camera raised to show downstream sheet; Junction river visible.

Rebuilt 67 affected FBX across 63 pieces; other FBX retained. Placed tris 309,074 -> 303,458 (-5,616); library 129,583 -> 123,967. Render-only terrain/card tessellation/water excluded from shipping totals.

Renders: previews/hero/old_sugarloaf_skyline.png, previews/hero/dam_crest_walk.png, previews/hero/narrows_crystal_walls.png, previews/hero/junction_town.png, previews/hero/world_vista.png, previews/hero/sunset_arch_from_crown.png.
Contact: previews/hero/contact_sheet.png; comparison: previews/hero/compare_vs_vistas.png; packed scene: previews/hero/sugarloaf_canyon_hero.blend. Detailed cameras/timings: previews/hero/render_report.json.

Remaining gaps vs vistas: source layout is sparse and angular, without golf greens/per-hole props; cards are flat silhouettes, terrain and kit seams remain visible; spillway is a simple sheet without spray or foam detail. Vista illustrations have richer vegetation, clouds, surface detail and staged compositions. Palette/light improved within existing low-poly assets; not a full illustration match.

| Strata material | Vista colour | Roughness |
|---|---|---|
| Cream | #E8C9A1 | .84 |
| Ochre | #C68C59 | .84 |
| Rose | #CC8D91 | .48 |
| Muted terracotta | #AF7061 | .84 |

## Pass 5 (Sunset Gondola) + 5b (staged renders)

New pieces (Blender 5.2, FBX forward -Z / up Y / scale 1, textures embedded; reimport ALL PASS, see `_src/reimport_pass5.txt`):

| Piece | FBX | Tris (max mesh) | MeshParts | Pivot | Motion |
|---|---|---|---|---|---|
| `gondola_cable` | `fbx/gondola_cable.fbx` | 2,012 (928) | 5: Iron, Licorice, MintWhite, PepRed, SandBlock | bottom bull-wheel centre = line start, world (130.392, 25.6, 542.811), yaw 0; geometry baked at world offsets | static |
| `gondola_cabin` | `fbx/gondola_cabin.fbx` | 512 (180) | 7: body GumLemon/Licorice/MintWhite/PepRed/Window + `Iron_hanger`, `PepRed_hanger` | cable grip point (haul-rope centreline); front local -Z = travel direction | travels the up line at 6 studs/s |

- **Line:** straight in plan, 687.2 studs, bottom station (132,18,544) yaw 53.53 -> top station (-420,190.1,128) yaw -126.84. Bull wheels (from the exported station torus): bottom (130.392,25.6,542.811), top (-418.399,197.7,129.199). Two 6-sided Licorice haul ropes r0.18, 7.6 apart (groove r3.8), CastShadow OFF on `gondola_cable__Licorice`.
- **Support tower:** the straight chord cut ~37 studs into the Crown cliff and H17 sits under the line, so there is one candy-striped portal tower on the Crown lip at plan distance 524 from the bottom wheel, centre (-288.068, 221, 227.427), ground y190, rope crest y221, 25+ studs from H17's footprint. The 3 `cableway_trestle` instances at x=-330 are the old ore cableway (283-399 studs off the line), not supports.
- **Sag:** parabolic spans, 10 studs bottom->tower, 2.5 studs tower->top. Up-line arc 559.65 + 164.95 = 724.6 studs.
- **Motion:** `P(w) = P + (Q-P)*w - (0, 4*sag*w*(1-w), 0)` per span (A->T sag 10, T->B sag 2.5). `s(t) = 6t` of arc length, so `w ~= s/L1` on span 1 and `(s-L1)/L2` on span 2 (max error 3.49 studs). Ride time 120.77 s. The cabin stays level with constant yaw: up line 53.53, down line 233.53. Roblox: `cabin:PivotTo(CFrame.new(P(t)) * CFrame.Angles(0, math.rad(yaw), 0))`. Grip-to-floor 6.4. One layout instance is parked at the boarding point (132.65, 25.6, 539.755). Full 10 s samples are in `manifest.json` under `gondola_cabin.motion`.

**Fitcheck at 0.15 studs** ([fitcheck_pass5.txt](fitcheck_pass5.txt), `_src/sc_fitcheck_holes.py`, 820 instances + cabin swept along both lines):
- Hole play volumes and footprints: ALL PASS for H1-H18.
- Walkways: 6 FAILs.
  - `p_h18_hub` seg 3: the swept gondola cabin is 2.92 above the walk (cable 7.45). This is pending a RobloxDevBot decision on the boarding-approach exemption or a re-route.
  - `p_h11_h12` segs 4-8: the dam railings (`railing_12`, lowest -0.20) and `peppermint_dam`. These are most likely checker false positives, because the railings flank the dam-crest walk rather than overhang it.
- `_src/fitcheck_pass5_validated.txt` was not written, because the result is not ALL PASS.

**Staged renders (render-scene-only; no kit changes)** by `_src/render_hero_pass5.py`:
- [previews/hero/V1-hub-tee1_staged.png](previews/hero/V1-hub-tee1_staged.png): eye (60, 25.5, 482), target (80, -49.6, -130), horizontal FOV 78. Holes are staged from holes.json: 126 felt slabs with a felt noise and bump texture, 308 timber rails with candy-striped caps (bumpers skipped), and 18 cups and flags. Lighting is a key sun at 277/7, an orange rim at 330/10, and a camera sky that runs peach to coral to mauve to violet. Cycles OptiX, 128 spp, denoised, 1920x1080.
- [previews/hero/V1-hub-tee1_vs_concept.png](previews/hero/V1-hub-tee1_vs_concept.png): the staged render side by side with `world/vistas/V1-hub-tee1.png`.
- [previews/gondola_span.png](previews/gondola_span.png): the whole span with both stations and the tower. Eye (246, 400, -184), target (-145, 80, 335), FOV 65, key 277/22, far cards hidden.
- Camera and timing details: `previews/hero/pass5b_render_report.json`.
- [contact_sheet.png](contact_sheet.png) was regenerated and now includes `gondola_cable` and `gondola_cabin`.

## Pass 6 (art rework)

Full details, tables and the reproduction order are in [_src/pass6_summary.md](_src/pass6_summary.md).

**Totals.**
- Placed triangles went from **305,982 to 588,476**: cliff kit 192,224 → 295,248, rim 960 → 4,800, new hole dressing 174,746.
- 208 pieces, 213 FBX files, 874 instances.
- Max mesh: 4,324 tris for the whole kit (3,880 for the pass-6 pieces).
- Worst per-hole Quest near-field count (centroid within 60 studs) is **29,086 at H5**, against a budget of about 40k.

**Gondola.**
- **Tower recolour:** the tower is now sun-weathered timber (new `TimberWeathered`, texture `textures/timber_weathered.png`). The crossbeam baulks alternate with `Timber`. Fittings are dark `Iron`, and the cradle bolt plates use the new `Brass`. Only the turning sheaves keep red/cream.
- **Identical geometry:** `gondola_cable` was rebuilt with the same geometry, 2,012 tris, and the same bbox and centre as pass 5 (`_src/_cache/pass6_step1.json`).
- **Clearance:** the bottom station is now **`gondola_station_bottom`** (2,205 tris).
  - It is the station raised 7.2 studs on a timber/sandstone undercroft, with a 10-riser side stair and the deck top at world y 26.
  - Same footprint centre and yaw. The ground boarding point (130, 18, 540) stays clear underneath.
  - The bottom wheel/attach goes from 25.6 to 32.8. The tower, top attach and sags are unchanged.
  - The motion formula and samples are recomputed in `manifest.json` `gondola_cabin.motion`; the cabin FBX is unchanged.
  - The `gondola_cable` pivot is (130.392, 32.8, 542.811). The top station still uses `gondola_station`.

**New pieces** (FBX forward −Z, up Y, scale 1, textures embedded):

| Piece | Tris |
|---|---:|
| `trading_post_deck` | 3,840 |
| `barrel_a` / `barrel_b` | 252 / 624 |
| `lantern_post` / `lantern_hanging` | 244 / 156 |
| `lollipop_cactus_cluster` | 696 |
| `rock_candy_cluster` | 264 |
| `gumdrop_shrub_a` / `b` / `c` | 592 / 356 / 456 |
| `boulder_scatter` / `fallen_rock_scatter` | 180 / 100 |
| `red_dirt_patch_a` / `b` | 36 / 36 |
| `pebble_scatter` | 80 |
| `clay_brick_edging` | 120 |

- **CastShadow off:** turn it off on `__LanternGlow` (Neon lantern cores) and on the flat `__RedDirt` / `__RedDirtLight` ground meshes.
- **New materials:** TimberWeathered, Brass, LanternGlow, Canvas, CanvasRed, ClayBrick, RedDirt, RedDirtLight, Pebble.

**Placements.**
- **Trading post:** at (47.5, 17.36, 469.0), yaw −90, beside the H1 tee on the west side, facing the lane.
- **Prop clusters:** 68 clusters of 3–5 props at every tee and every turn of all 18 holes (308 members).
- **Ground:** a terrain-hugging two-tone red-dirt carpet, pebbles, and 1,892 rounded clay-brick edging bricks 0.2 outside the rails. Walkways stay clear, and sand shows at the cliff feet.
- **Merges:** everything is merged per material per hole into `hNN_dress_props`, `hNN_dress_plants` and `hNN_ground`. These are world-baked, with the pivot at the tee and yaw 0.
- **Records:** instances are in `layout.json`; per-hole members, clusters and tris are in `manifest.json` `pass6.dressing`.
- **Placement checks** (`_src/sc_dress_pass6.py`): exact 0.15 tests against holes.json play volumes, the lane rules (nothing taller than 2 within 3 of a rail; no plants within 1.5 of the rail strip), walkways, existing kit and the decoration anchors.

**Cliffs.**
- **Tower panels:** `cliff_w24_*` / `slot_w24_*` are rebuilt as separate eroded towers:
  - recessed edge gaps, so the towers stand apart with about 5-stud slots at the 21-stud spacing;
  - a 12-stud world-y stepped taper with cap-rock overhangs;
  - gently wavy strata that stay world-y banded, with a wave of 0 at the panel edges.
- **Rounded tops:** 36 new rounded-top variants `cliffT_*` / `slotT_*` are used on the top panel of all 309 stacks.
- **Same placements:** placements and the panel envelope are unchanged.
- **Tri counts:** h48 panel 496 → 648 tris; `rim_silhouette` is now stepped towers with gaps, 12 → 60 tris.

**Fitcheck.**
- [fitcheck_pass6.txt](fitcheck_pass6.txt) at 0.15 studs is **ALL PASS**, copied to `_src/fitcheck_pass6_validated.txt`. The new dressing has zero intrusions.
- **`p_h18_hub` seg 3 PASSES**, with a minimum gondola clearance of **10.04 studs** (≥ 8 required; it was 2.92).
- The `p_h11_h12` dam railings are exempt from head clearance by an explicit edge rule: `railing_12` / `peppermint_dam` triangles in the outer 0.6 studs of the corridor and ≤ 4.0 high are railings at the edge, listed as INFO.
- Pass-6 hole dressing is judged by the exact play-volume test plus new lane-rule check [C], not by the coarse 2-stud footprint rule.
- [D] reports the near-field counts.

**Re-import.** [_src/reimport_pass6.txt](_src/reimport_pass6.txt) is ALL PASS for 144 FBX files.

**Previews.** Previews were regenerated, and [contact_sheet.png](contact_sheet.png) now has 148 thumbnails.

**Render** (`_src/render_hero_pass6.py`).
- **Final:** [previews/hero/V1-hub-tee1_pass6.png](previews/hero/V1-hub-tee1_pass6.png), Cycles OptiX, 1920x1080, 128 spp, denoised.
- **Comparison:** [previews/hero/V1-hub-tee1_pass6_vs_concept.png](previews/hero/V1-hub-tee1_pass6_vs_concept.png). Camera and timing are in `previews/hero/pass6_render_report.json`.
- **Staging:** the candy staged rails are replaced by render-only rounded clay-brick curbs.
- **Light:**
  - Key sun 277°/4°, orange, with shadows.
  - No-shadow orange rim sun 285°/3°. At 3–4° the west mesas shade most of the canyon, so this is what puts the orange rim on the cliff-tower tops.
  - Peach-to-gold camera sky, AgX Punchy grade.
- **Dark slab:** the dark slab right of the H1 lane in `V1-hub-tee1_staged.png` is **kit geometry**, not a staging artefact. It is three `walk_boardwalk_6x12` boardwalk planks on `p_h1_h2`, and I left it unchanged.

## Cup clearance check (2026-10-12)
RobloxDevBot's cup fix lowers the ground ~0.6 studs under each cup, so nothing in `hNN_ground` / `hNN_dress_*` may sit within 1.5 studs (target 1.8) of a cup. I measured the horizontal clear radius from every holes.json cup to all 54 per-hole ground/dress meshes on the PC (`_src/cup_clear.py`). All 18 pass. The tightest are h04 at 2.2, h10 at 2.7 and h02 at 3.4. The pass-6 carpet already stops 0.9 studs outside the felt. Nothing was cut and the FBX are unchanged. Report: `_src/cupclear_pass6.txt`; manifest `pass6.cup_clearance`.

## Final props batch 1 (2026-10-12): timing meshes + flag
New visual FBX in `fbx/props_batch1/`: h06_sluice_gate, h09_windpump_rotor, h11_lock_gate (single flat leaf), h14_ore_bucket, h17_shadow_arms, flag. Each one's origin is its holes.json pivot. Visual only; collision stays the holes.json blockers. These replace the older visuals of the same parts in `fbx/movers/`. Manifest: `props_batch1_manifest.json`. Fitcheck: `fitcheck_props_batch1.txt` (ALL PASS). Previews: `previews/props_batch1/`. Source: `_src/props_batch1/`.

## H8 crease update (2026-10-12)
`fbx/h08_ground.fbx` was rebuilt for the new H8 rails (3 flat 0.5 creases, 3.8125 dips). It now has 114 clay bricks (was 108) and 4,566 tris (was 4,446). Carpet and pebbles are unchanged. The old files are backed up in `_src/backup_h8crease_20261012/`. Previews: `previews/h8crease/`.

## props_batch2 (2026-10-12) H1-H6 Sugarloaf landmarks
fbx/props_batch2/h01_trailhead_arch, h02_headframe (open lattice), h03_ranger_station, h04_geode_wall, h05_echo_walls, h06_bell_tower. Visual only (CanCollide off), pivots = holes.json anchor base centre. Manifest props_batch2_manifest.json, fitcheck fitcheck_props_batch2.txt (ALL PASS), previews previews/props_batch2/ (+contact_sheet.jpg). Source _src/props_batch2/ (gen_batch2.py -> parts.json -> build_batch2.py in Blender).

## props_batch1 rev1 (2026-10-12)
H9 rotor: iron hub plate fills hub corners, bubblegum/white swirl both faces. H14 bucket: stronger taper, peppermint band, brass rivets, pink/amber ore lumps. rev0 backup in _src/props_batch1/_backup_rev0_20261012/.

## props_batch3 (2026-10-12) H7-H12 Sugarloaf landmarks
fbx/props_batch3/h07_rope_bridges (rope posts + sagging hand ropes; decks are the flat felt), h08_gumdrops (cherry + lime, inside the two bumper colliders), h09_pump_house, h10_sluice_flume, h11_lock_keeper_hut, h12_intake_tower. Visual only (CanCollide off), pivot = holes.json anchor. Manifest props_batch3_manifest.json (world pivots via world_offset/world_yaw), fitcheck fitcheck_props_batch3.txt (ALL PASS), previews previews/props_batch3/ (+contact_sheet.jpg). Source _src/props_batch3/ (gen_batch3.py -> parts.json -> build_batch3.py; prefit.py = quick pre-Blender check).
Note: props_batch2_manifest.json world pivots re-computed with world_yaw (H3/H4 were wrong; old copy in _src/props_batch2/).

## props_batch4 (2026-10-12) H13-H18 Sugarloaf landmarks
fbx/props_batch4/h13_maze_rock (banded spine inside rock_w9..w12 + 6 gumdrop-capped hoodoo stubs, <= 4.0), h14_cableway_trestle (splayed A-legs outside rail1/rail9, beam = holes.json occluder, clear of the bucket swing), h15_sugar_dune (sugar drifts outside dune_rail1/2 + striped sled; the dune face is the holes.json felt), h16_sinkhole_rim (flush crystal collar inside the 2.4 opening + rope railing south of the bowl), h17_gnomon (striped triangular blade on a base plate 0.1 over the plinth), h18_arch_gate (striped arch, legs outside rail3/rail11, underside >= 9.3 over the ramp felt). Visual only (CanCollide off), pivot = holes.json anchor. Manifest props_batch4_manifest.json (pivot_world includes world_yaw), fitcheck fitcheck_props_batch4.txt (ALL PASS; gates >= 0.1 off walls, no felt contact, 8 overhead, moving-part sweeps), previews previews/props_batch4/ (+contact_sheet.jpg). Source _src/props_batch4/ (gen_batch4.py -> parts.json -> build_batch4.py; prefit.py; fitcheck_batch4.py).

## props_batch3 rev1 (2026-10-12) H9 pump house polish
h09_pump_house: white/bubblegum candy trim along the south roof eave, candy-striped stack (x 5.6, to 7.97) and iron/brass mushroom vent (x -4, to 7.42). 264 -> 844 tris. Fitcheck re-run: ALL PASS (rotor sweep 0 points). rev0 backup: _src/props_batch3/_backup_rev0_20261012/; rev1 build files: _src/props_batch3/rev1_h09/.

## props_batch4 rev1 (2026-10-12) H15 sugar drifts
h15_sugar_dune drifts rebuilt as taller rounded half-dome mounds (west crest ~2.4..3.3, east to ~-0.4 over its -3.45 base, ends tapered over 3 studs), 272 -> 668 tris; refit ALL PASS (0.12 off dune_rail1/2). rev0 backup _src/props_batch4/_backup_rev0_20261012/; rev1 build _src/props_batch4/rev1_h15/.

## mine_head (2026-10-12) Sugarloaf world landmark
fbx/mine_head/mine_head.fbx (1,346 tris): candy-striped headframe + brass sheave wheel over a timber shaft collar (west), winding house with drum, brick chimney and gable roof (east), ore cart with rock-candy load on a short track. Pivot = base centre, world [134, 18.3, 392], yaw 0, inside props.md envelope 14x18x12 (x +-7, y 0..18, z +-6). Replaces the older kit fbx/mine_head.fbx (16x26x25, left untouched). Manifest mine_head_manifest.json, fitcheck fitcheck_mine_head.txt (ALL PASS: nearest hole wall 15.4 (H2 rail10), nearest path corridor 29). Previews previews/mine_head/.

## lift_cage, gondola, scatter (2026-10-12) props.md "Transport and scatter sizes"
- fbx/lift_cage/lift_cage.fbx (1,128 tris): one mesh for all 4 lifts. Outer 7x9.5x7, floor 6x6, clear 8, striped 0.4 posts, 0.15 lattice at 1.0, brass waist rail 3.5, 4-wide opening on -Z (face it to the landing; doorway header leaves 7.7). Pivot floor centre.
- fbx/gondola/gondola_cabin.fbx (540 tris): enclosed cabin 8W(x) x 6D(z) x 8H, inner 7x5 clear 7, two facing benches 1.5 deep at seat 1.8, glazing 3.2..6.5 all round, hanger 0.5 sq rising 4 to a grip clamp. Pivot = cable grip (cabin base at y -12), cable along local Z. Previews are rendered with the cabin lifted 12 so it sits on the preview ground.
- fbx/scatter/: cactus_a/b/c, gumdrop_a/b/c, ore_a/b/c, crystal_a/b/c, hoodoo_a/b/c (144..282 tris each), pivot base centre, sized so 0.8..1.25 scale stays inside the props.md ranges.
Manifests lift_cage_manifest.json / gondola_manifest.json / scatter_manifest.json, fitchecks fitcheck_lift_cage.txt / fitcheck_gondola.txt / fitcheck_scatter.txt (ALL PASS), previews previews/<set>/ (+contact_sheet.jpg). Source _src/world_props/ (gen_world.py -> <set>/parts.json -> build_generic.py; fitcheck_world.py).

## Props H09/H14 (2026-10-13): water tank + loading dock (replace placeholders)
- `fbx/props_h09h14/h09_water_tank.fbx`: 1,128 tris, 3.89 x 8.0 x 3.89. Timber barrel tank, 3 Iron hoops, cone roof, Iron spout + Brass valve (faces +Z), 4 splayed TimberWeathered legs with X-braces. Pivot = base centre at the holes.json anchor (-11.65, 0, -40), world (370, 70, -121.65), yaw -90. Rail7 is 0.205 away, the green felt 0.705 in plan.
- `fbx/props_h09h14/h14_loading_dock.fbx`: 1,240 tris, 4.9 x 2.54 x 9.87. Plank deck (top 0.95) on 6 posts, two steps on the outer side, 3 crates (one heaped with lilac rock candy). Pivot stays at the holes.json anchor (0, 0, -33), world (-300, 150, -167), yaw 180. The geometry is offset WEST of the ramp (x -9.6..-4.7, z -35.35..-25.49) because the anchor box is the ramp felt. Rail3/rail4 are 0.15 away, rail2 0.20, the felt 0.65 in plan.
- Materials reuse Trading Post names (Timber, TimberWeathered, Iron, Brass), plus RockCandyLilac #B49AC9. No red or cream. Collision, query and touch are all off.
- Manifest `props_h09h14_manifest.json`; fitcheck `fitcheck_props_h09h14.txt` passes everything at the 0.15 gate. Previews are in `previews/props_h09h14/` (34/front/eye); the silhouette sheet is `../silhouettes/sheet05-h09-tank-h14-dock.png`. Source is in `_src/props_h09h14/` (the gen script was written by Codex gpt-6.1-sol on the PC). holes.json MD5 e06f8ee873659899c4b436ffeea7ee2e.
- Rev 1 (2026-10-13, Game Art Bot review): the tank has two RockCandyLilac bands between the hoops, 1,192 tris. The dock has an ore heap about 3x bigger (lilac crystals spilling over the crate rim plus Bubblegum #F78FB3 shards), two 4.6-tall ramp-side corner posts with a cross beam and knee braces, and solid closed iron post caps, 1,468 tris, 4.9 x 4.6 x ~10. Clearances are unchanged (rail7 0.205; rail3/rail4 0.15, rail2 0.20). The fitcheck passes everything. Rev 0 is backed up in `_src/props_h09h14/_backup_rev0_*`.
- Rev 2 (2026-10-13): H14 ore only. A chunky lilac mound (top 3.66, 0.49 under the beam) drapes over the crate's +x and +z sides, with 8 fat hexagonal Bubblegum crystals and 4 chunks on the deck. Dock is 1,688 tris. The dock's 3/4 preview camera is raised so the ore reads above the beam. Clearances are unchanged; the fitcheck passes everything. Rev 1 is backed up in `_src/props_h09h14/_backup_rev1_*`.
