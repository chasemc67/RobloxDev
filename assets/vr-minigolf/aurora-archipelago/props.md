# Aurora Archipelago: props for the 3D modeler (concise)

Build from `holes.json` (holes, movers, anchors: source of truth) and `world/world.json` (placement, backdrop). Full inventory with every anchor, rail box, blocker, backdrop piece and budget: **`props-full.md`**. 18 holes, par 53.

## Rules
- Studs (1 stud = 0.3 m), +Y up, +X east, -Z north. Sizes = bounding boxes [x,y,z]. Positions are **hole-local** (tee = origin, play toward -Z) unless marked world. world = R_y(yaw)·local + origin: `x'=lx·cos+lz·sin+ox`, `z'=-lx·sin+lz·cos+oz`.
- **All props are decoration only (no collision).** Ball collision = invisible holes.json parts. A mesh that skins a collider must match its faces exactly from felt to box top: no bigger bases, no lips into the lane.
- Felt `center` = TOP surface; wall/blocker `center` = box centre; anchor `position` = base centre.
- **P1** playable and readable · **P2** strong theming · **P3** polish.
- Blender 1 unit = 1 stud; FBX forward -Z, up Y. Origin at base centre (static) or **exact pivot** (movers). One mesh per material plus a flat-colour fallback. Glass ice: T 0.3, Refl 0.1 + Neon core `#BFF6FF`. Aurora: Neon, mint `#5CFFB0` -> violet `#B07CFF`.
- **Quest budgets:** dressing within 60 studs of a hole's felt ≤ 34k tris (estimates 17.5k-33.1k, max H7). Per-hole merged file < 20k. ≤ 2 heavy small props (> 900) per hole. Pines ≥ 40 from felt = 12-tri cards (33 of 60). Targets: rail 25 tris/stud, flag 150, lantern post 450, snowpuff 500, pine 800, palm 600, coral 450, crystal 400. Auto-LOD only.
- **Clash:** nothing from felt +1.25 to felt +8 over any felt (8 = course head clearance). Only exceptions: movers and felt cues. Plants ≥ 1.5 from rails; tall props ≥ 3. Nothing in pools, pits, gaps (H3 z -24..-50, H17 z -16..-42, x ±13), on walkways/stairs/pads, or in mover sweeps (+0.15). Keep tee-eye (5.5) -> flag-top clear; stay inside anchor `occluders`.

## P1: build first

### Flag and kits (reused)
- **Flag** ×18: pole 7.5 × Ø0.15, banner 2 × 1.2 × 0.05 `#E03C31`, separate banner mesh (it turns to face the tee). Base = `cup.position`.
- **Rail kit**: snow-capped timber (`#8A5A33` + white cap), brass bolts, 0.5 thick, 1.0 over felt. Pieces: straight 1/2/4/8, 45°, corner, end cap, slope-follower. 3,460 studs of rail boxes in total.
- **Tall-wall skins** (colliders taller than a rail): H2 snow drift 2.4; H9 coral reef walls 2.4 + bank backings 2.7; H10 snow walls 1.3 with an ice lip; H11 snowbank/berg 2.4 + floe pocket 3.2; H18 crystal walls top y 3.2 + chute divider 2.2 × 3.7 × 10. Fill each box face; no see-through gaps.
- **Decals** (flush 0.01, mint glow): arrows 1.4 × 2.0, chevrons 2.4 × 1.2, ripples. **Respawn stones** 0.8 × 0.8 aurora-lime `#D8FF6A` (H3 [0,0,-22.5], H6 [5.5,-0.08,-35], H17 [0,0,-14.5]). **Signs** ×12: plank 1.6 × 2.6 × 0.2 and lantern sign 1.8 × 3.2 × 0.25.
- **Brass lantern** on a chunky post (PointLight `#FFB861`, r 14, b 0.8): 89 world posts 1 × 7 × 1, plus hole posts 9 high.

### Moving meshes: origin = pivot, exactly as in holes.json
| Mesh | Hole | Pivot / axis (local) | Pivot (world) | Motion | Contact shape to match |
|---|---|---|---|---|---|
| **geyser_column** | H5 | [0,0,-26.5] / [0,1,0] | [241.5,84,420] | slide 2 studs/s, 0..4; dwell 8 s at 0, 1.5 s at 4; cycle 13.5 s | 3×4×3 box under the origin (y -4..0). **Square 3×3 faces**: hex look only on the top tiles and trim. Steam-vent dimple, gauge flush on the side |
| **ice_floe** | H11 | [0,0,-28] / [1,0,0] | [410,146,12] | slide 3 studs/s, -7..0; dwell 1.2 s at 0, 2.0 s at -7; cycle 7.8667 s | slab 6.4 × 1.0 × **0.636** + 45° pointed ends to x ±3.5 (blocks 0.4243² yaw 45 at ±3.2). Snow + mini snowpuff ≤ 1.2 high, inside the footprint |
| **paddle_wheel** | H12 | [0,4.16,-17.75] / [0,0,1] | [352.25,150.16,-60] (axis world +X) | rotate 30°/s continuous, phase 0 (12 s/rev) | 4 paddles (roll 0/90/180/270), each 2.4 wide × 0.4 thick, r 0.6 -> **arc r 4.1** (lowest edge 0.06 over felt). Rims/spokes only at r ≤ 3.9 within z ±0.2 |
| **carousel_arms** | H13 | [0,0,-36] / [0,1,0] | [120,182,-266] | rotate 15°/s continuous (24 s/rev) | 4 runners 3.3 (r 8.2..11.5) × 0.9 high × 3.6 wide at 0/90/180/270. Sleds + snowpuffs above 0.9 stay inside the footprint, < 4. Spokes ≥ 1.4 over felt at r < 8.2 |
| **icicle_bell** | H14 | hinge [0,10.35,-24] / [0,0,1] | [61,192.35,-300] (axis world +X) | swing ±9°, period 4 s, phase 0, peak 14.14°/s | bell = 2×2×2 cube 9.0 below the hinge, **yaw 30** (y 0.35..2.35 at rest). Flare/icicles above 2.35 only. Skid plate 2.1 × 0.4 × 0.15, top y 0.461 at rest, underside an arc r 10.289 about the hinge (9 collider strips; y 0.062 at the centre, 0.115 at the ends; ≥ 0.061 at every swing angle), yaw 0. Hanger 9 |
| **aurora_span** | H17 | [0,0,-29] (toggle, no motion) | [-165,222,-291] | 9 s: fade-in 0.6 / solid 6.0 / fade-out 0.6 / gone 1.8; collider only [0.6, 6.6) s | Neon deck 3 × 0.4 × 8 = felt `light_span`; ribbon above y 10 only (3 × 60 × 8) |

### Teleport / lift dressing
- H5 `geyser_lift`: the platform top is the trigger (±1.5; drop-ins from the upper green ±1.65 in x, covering the 0.15 rail-end slots). Boarding while flush (t 0-8 s); release at t 10.1 s from [0,4,-29.6] toward [-0.2514,-0.9679]. Separate signal lamp [-9.5,2,-27.6] (0.6×1×0.4, base y 2: on the cliff face just outside basin_rail7, below upper_rail8): green while flush, amber otherwise. Shaft lining 3.2 × 3.2 cut into the basin; cliff face in two skins on the upper tier's south face, under the felt slab: cliff_face_w [-7.075,0,-28.3] and cliff_face_e [7.075,0,-28.3], each 10.85 × 3.5 × 0.5 (x -12.5..-1.65 and 1.65..12.5, z -28.05..-28.55, y 0..3.5), shaft gap x ±1.65.
- H9 `conch`: lime ring decal r 0.3 at [0,0,-33] inside the entry conch mouth (shell 5 × 4.5 × 5, base [0,0,-34], body behind the ring, < 5 high). Exit conch 4 × 4 × 4 (same mesh × 0.8) at [11,0,-67]; mouth faces [-0.9487, 0.3162] (aimed at the cup).

### Hole landmarks (static heroes; base = local anchor)
| Hole / par | Origin, yaw | Cup | Landmark: base; size | Other P1 hole props |
|---|---|---|---|---|
| H1 Lantern Quay /2 | [-150,60,545], 0 | [6,0,-30.5] | **harbour_lantern** [-6,0,-24]; 0.9×9×0.9 | snow_boulder skin over the 3×3×3 bumper (yaw 45) at [-1.3,0,-35.8], ≤ 5 high, with a mint glow line on the SE bank face |
| H2 Snowpuff Burrows /3 | [-115,60,480], -90 | [-11,0,-46] | **rookery_drift** [0,0,-22]; 24×5×26 | open-top burrows. 3 ice lintels 5×1.2×1.2, underside y 8, at x -9.5/0/9: the lintels are **legless**; each end rests on a basalt rock pillar standing outside the rail / on the drift wall top, never inside the clear burrow width. Lantern cue (0.9×1.2×0.9, bottom y 9) hangs over the cup [-9.75,9,-46] from **lantern_crook** [-13.6,0,-46]: a shepherd's-crook post (timber + brass, 0.35 thick, 11 tall) outside the west rail (rail outer face x -12.5); its curved arm reaches east to x -9.75 with underside ≥ y 10.4, then a drop rod holds the lantern. Visual only, no collision; nothing below y 10.4 over the felt |
| H3 Glimmer Crossing /3 | [-40,60,470], -45 | [-1,0,-55.5] | **glimmer_islet** [24,-20,-36]; 20×30×20 (view cue) | rail-less glowing ice plank 2.4×0.8×26 at [0,0,-37]. Railed ice bridge 5×2×26 at [6,0,-37]. Walk-on deck x 8.5..12.5 |
| H4 Glissade /3 | [185,84,470], 0 | [9,0.6,-54] | **frosted_palms** [-8,0,-22]; 6×12×6 | glassy ice felt `#9FE3F2` 8×32 (T 0.15, Refl 0.15) with frost chevrons. Decal 'ICE' at z -7 |
| H5 Geyser Hop /3 | [215,84,420], -90 | [-4,4,-45] | **steamwhistle_geyser** [-16.75,4,-36]; 6×7×6 (base x -19.75..-13.75: outside upper_rail9, outer face x -13) | geyser column (above), cliff_face_w/e, signal lamp (see H5 note above). **geyser_steps** [15,0,-23]; 3×4×12: x 13.5..16.5, z -17..-29, 5 steps × 1.5 tread rising 4 to a y-4 landing east of upper_rail11 |
| H6 Palm Lagoon /3 | [305,84,478], 0 | [0,0,-54] | **kettle_pool** [11.5,-0.81,-35]; 6×1×22 | basalt rim under rail5. Slope ripples. Palms (P2) at [16.5,0,-35] |
| H7 Mogul Meadow /3 | [365,112,330], 0 | [6,0,-53] | **coral_fans** [-12,0,-24]; 3×6×30 | mogul_trim 9×0.4×28: rails follow 4 humps (+0.6/-0.4). **Coral clumps, both sides** (base [x,0,z], height): west coral_w1 [-6.5,-11] 4.5 bubblegum · w2 [-9,-18] 6 tangerine · w3 [-6,-24.5] 3.5 mint · w4 [-10,-30] 5.5 bubblegum · w5 [-7,-35] 4 tangerine; east (mirrored, varied) coral_e6 [7,-13.5] 4 mint · e7 [9.5,-20.5] 5.5 bubblegum · e8 [6,-26] 3 tangerine · e9 [8.5,-31.5] 6 mint · e10 [6.5,-35.5] 4.5 bubblegum. Footprint ≈ 0.5 × height wide, 0.4 × height deep. **Shape: BRANCHING coral, not sticks.** A short 0.5-thick trunk splits 2-3 times into 3-5 flattened, fan-like branches with rounded, slightly swollen tips, spreading wider than the trunk (crown ≈ 0.5 × height); neon core glow in the branch tips. No straight poles, no single spikes; vary branch count and lean per clump |
| H8 Coral Pinball /3 | [430,112,300], 0 | [-3.5,0,-48.5] | **giant_coral** [-10.5,0,-18]; 7×14×7 | 7 coral bumper skins (section below) |
| H9 Conch Shortcut /4 | [535,112,230], 0 | [2,0,-64] | **conch_entry** [0,0,-34]; 5×4.5×5 | conch_exit. Reef lagoon water 25×34 at y -1.2. Coral spit under the 3×13 felt |
| H10 Bobsled Bend /3 | [510,146,60], 90 | [-0.5,0,-42] | **bobsled_hut** [-7.5,0,-6]; 5×7×5 | snow walls (≤ 4) cover the plate felt outside `plate_visible`. Ice lip on the rails to y 1.3 |
| H11 Floe Drift /3 | [410,146,40], 0 | [-4,0,-45] | **fishing_hut** [-9,0,-30]; 3×6×3 | floe (above). Slot cut in rail5/berg18: x -10.68..3.68, y -0.15..1.27 (floe mesh top <= 1.12). Pocket walls |
| H12 Icebreaker Wheel /3 | [370,146,-60], 90 | [-1.5,0,-42] | **icebreaker** [-3,0,-21]; 16×8×6 | wheel (above). Hull faces = hull13-18 + rail2-5 (rail2/hull13 inner face z -18.01, 0.06 behind the paddles). 2.4-wide slot kept clear |
| H13 Snowpuff Carousel /3 | [120,182,-230], 0 | [10.1,0,-46] | **carousel_canopy** [0,0,-36]; 16×12×16 | canopy underside y 9. **Hub plinth** r 7.5 × 1.2 (48 box strips, 48-sided) |
| H14 Bell Buoy /3 | [85,182,-300], 90 | [1,0.8,-44] | **bell_gantry** [0,0,-24]; 10×11.35×1.5 | legs x ±5, beam y 10.35. Bell (above) |
| H15 Frozen Falls /2 | [12,182,-334], 0 | [3.5,-4,-31] | **great_frozen_falls** (world mesh; anchor [13.5,-4,-30] is a view cue) | lip_ice 7×4×1 down the 4-stud drop at z -20. Clear ice parapet 8×3.5. Steps x -6..-9.5 |
| H16 Moonwell /2 | [-110,222,-300], 0 | [3.2,-0.8,-35.5] | **moonwell** [0,-0.8,-21]; 20×2×18 | moonstone coping skins rails y -1.3..1.0. Crescent spout at z -30 |
| H17 Aurora Bridge /3 | [-165,222,-262], 0 | [2.2,0,-56] | **aurora_ribbon** [0,0,-29]; 3×60×8 | crystal piers 3×9 (z -20.5/-37.5). Ice bridge 5×2×26 at x 6. Timing lamp [-2.4,0,-15]. Walk-on deck |
| H18 Halo Arch /4 | [-235,222,-232], 0 | [-4,0.8,-46] | **halo_arch** [0,0.8,-52]; 46×34×4 | legs x ±23, opening ≥ 18 over the felt. Crystal banks + chute (1.6 wide) |

### Plinths: where invisible colliders poke out of meshes
- **Bumpers**: flat-faced bases exactly the box footprint, from felt to box top. Widen only above that. H1 boulder 3×3×3 yaw 45 (top y 2.5). H8 corals, top y 1.6: coral1 [-2,-10] 1.8×1.8 y45 · coral2 [3,-15.5] 2.4×1 y-35 · coral3 [-3.2,-20.5] 2.4×1 y35 · coral4 [1.5,-25] 1.8×1.8 y45 · coral5 [-1.5,-30.5] 2.2×1 y60 · coral6 [3.5,-34.5] 2×1 y-30 · coral7 [2,-45] 1.6×1.6 y45.
- **H13 hub**: round base r 7.5, 1.2 high. Not felt-textured.
- **Floating decks**: rail boxes go down to felt -0.5. On H3/H17 bridges, piers, the plank and the H9 spit, model decks ≥ 0.6 thick or skirts to y -0.6 so nothing shows under them.
- **Drops/tiers**: H5 cliff 4 under upper_rail8/12 (rail ends stop 0.15 short of the column, at x ±1.65). H15 lip face 4 high. H14 green skirt 0.8. H16 coping down into the 0.8-deep well.

## P2: theming
- **Snowpuffs**: one rig (ink `#222233`, cream `#FFF4E2`, beak `#FF9A3C`, knitted scarves), separate head on a neck pivot (it follows the ball). Poses: wave, slide, binoculars, towel, snorkel, sailor hat, telescope, bells, grandstand. 14 hole groups + 12 world groups.
- World kits: snowy pine (60: 27 full, 33 cards), ice-crystal cluster (30), frosted palm (16), coral-ice branch (22), island undersides (25, slate-violet roots with crystal veins).
- Frozen falls kit, widths 10/14/26 (Glimmer, Great, Twin W, Summit, Reef) + Steamwhistle Falls (Beam + steam). **Starfrost Spire** 64×240×64 at world [0,100,-40] (P1 skyline: visible from all tees, ~8k tris, orbiting shards r 50-90).
- Lifts: one 10×10 open cage ×4 (Steam, Coral, Icefall, Crystal). Gondola cabin 6×6 + 2 stations 12×12×12. Bridges: Glimmer 52, Coral 50, Aurora Skybridge 134.5 (Neon deck). Lantern Stair 3 × 10 steps. 8 teleport pads 4×4.
- H2 burrow lanterns, H13 music lanterns, H18 ramp lanterns, H7 fans, H4/H6 palms, H11 floe posts.

## P3: polish
- Far islands ×16 (r 760-960, ~300 tris), far silhouettes ×12 and cloud rings ×3 (cards), sister landmark Ice-Arch Isle, lantern huts ×6, sky lanterns ×12, moon disc, star field.
- H1 bollards, H4 steam vents, H14 buoys, snow/boulder blobs.

## Source mismatches (details in props-full §13)
- **Halo Arch**: holes.json anchor = world [-235,222.8,-284], depth 4; world.json says [-235,222,-292], depth 8. **Use holes.json** (the flag line of sight was validated with it).
- **Geyser**: H5 cone (world [251,88,403.25], 6×7×6) vs world.json cone [262,84,380] 14×10×14. Use one mesh, two instances; designer to confirm which one puffs.
- course.md mover "starting specs" are superseded by holes.json (the table above).
