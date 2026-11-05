# Pirate Shipwreck v20 PREP, RUN 2 report (v20b)

**Result: prep run done. Place UNSAVED, NOT PUBLISHED, version still 19.**
- No Save to Roblox, no File > Publish, no version bump. Every edit exists only in the open place in memory (pid 65929, `game.PlaceVersion` 0 in the open session; the live place is v19).
- Studio is left open on the modified, unsaved place:
  - HttpEnabled false
  - camera Custom, FOV 70
  - docks closed, cursor parked, no dialogs
- The place stays private:
  - no Robux spent, no uploads
  - Team Create off
  - no Scripts written through MCP
  - nothing deleted by hand (ltdr20 rebuilt only its own Dressing folder)
  - Blockout lights disabled, not deleted
  - test hides were Transparency-only and are all restored
- Pid 18508 was not touched. Every GUI input went through `/tmp/v20/act.sh` (activate pid 65929 through NSRunningApplication, verify the frontmost pid is 65929 first).
- No Screen Recording prompt appeared.

**Headline findings:**
1. **The new route is one continuous Sand trail in Studio** (Studio terrain top-surface map, `v20b_diag/topmap.png`):
   - 1→9 along the beach
   - 9→10→hub→11→12→13→14→15→16→17→18 through the jungle
   - 18 back down to the beach by pad 9
   - The 30-stud hub clearing is there.
2. **From overhead the trail is still weak.** Only **32 %** of trail cells read as Sand in the straight-down whole-course shot.
   - Main culprit: **Persistent `canopy_wall` slabs (179-293 studs long) lying across the jungle interior**. They read as long dark bands and also make the near-black mass in the pad 12 back view.
   - Next: Skyline palms and leafclumps inside the course, the pad 12 low leafclump gap-fill sitting *on* the trail, then vine_arch rows.
3. **From the tees at eye height the trail is mostly not visible** (9 pads fail, 5 weak). The low Edge hedge along the rims and the grazing angle hide it.
4. **Generator bugs found:**
   - **all 3 `ruin_arch` items are missing** from dressing_v20 (v19 had 3)
   - the **"hut-adjacent torch → Range 12" rule never fires**: the torch-to-hut-centre distance is 26.5-31.9, threshold 24
   - a 72-stud **rock_m boulder swap stands on the 16→17 trail**
5. **Felt grain:** `Plastic` keeps the colour (median (106,186,100)) with a subtle grain. Applied to all 18 felts. The std rise is below the 2-6 target, see §8. Fabric darkens about 20 and is rejected.
6. **Hut thatch** (207,167,66) at 1.2 / (255,235,200), the best reachable. **Posts can't reach G/R > 0.65 by lighting**: the texel itself is G/R 0.64, and they read 0.51 with every warm light off.
7. **Torch gaps:** every torch has |gap| < 0.3 at its centre. Pad 1 stands on the deck plate (gap -0.12) and clears the hull by 3.29 studs from the post axis. The cave mouth torch sits on a slope.
8. **Pad 17 felt** now equals pads 5/15/18 (105,186,103). Pad 16 at SoftPadLight 0.5 is (124,201,113).
9. **Sun:** no change worth making. ClockTime ±0.5 h moves the sun 0.3° at latitude 80. Kept ClockTime 12 / latitude 80.

---

## 1. Preflight
**Studio and MCP:**
- The MCP lists one named studio, "Pirate Shipwreck (placeId 131316561222931)". Marker `V20B_MARKER_7731` landed in `~/Library/Logs/Roblox/0.745.0.7451137_20261101T132308Z_Studio_c0bae_last.log`. That is pid 65929's log (loaded `&version=19`; it also holds run 1's `V20_MARKER_4417`).
- No other Studio job was running. Pid 18508 stayed untouched (only its process age was read).

**Docks and viewport:**
- Docks were already closed and the viewport is full width (screen check), so vp14.env (280,166,1360,877) still crops inside the 3D view.
- HttpEnabled false at start. Every helper toggles it on only for a GET and back off; each batch reports `http false` at the end.

**Helpers reused from run 1:**
- `/tmp/v20/shotsrv.py` on :8767 (pid 96516), `/tmp/v20/shoot.sh` (frontmost-pid check, cursor sweep and park, vp14 crop, halo.py), `/tmp/v20/act.sh`
- :8765 file server (pid 9525)

**New this run:**
- `/tmp/v20b/mk.sh` builds batches into `~/stage/v20bs/`
- new cameras `cam_ov20*`, `cam_hub20`, `cam_leg20`, `cam_st20`, `cam_apron20`, `cam_arch20`, `cam_cave20`, `cam_tr*`, `cam_bould16/17/18`, `cam_feltcu`
- `v20bs/autocam_core.luau`: occlusion-aware ring search for walking views
- analysis tools in `v20bs/`: `sandpx.py`, `sandcol.py`, `trailvis.py`, `teevis.py`, `stat.py`, `contrast.py`, `topmap.luau`, `cover.luau`, `torch20b.luau`, `terrhist20b.luau`

## 2. Revert / rebuild
**ltdr20:**
- **`LT20D run ok=true nil http=false`**
- Placer log:
  - `DR templates 34`
  - `walkways: 99 boardwalk planks, 264 stepping stones`
  - `mouth torch ground 86.7 on Terrain`
  - **`torches 15`**
  - **`hut lanterns lowered 7 (brightness 1.2)`**
  - `kit_v2 point lights 25`
  - **`placed 3046 (skipped 0)`**, cave vine strips 6
  - `DONE instances 3581`
- Counts:

  | barrel | boulder_pile | canopy_wall | cliff_ridge | crate | crate_stack | fernclump | hull_rib | hut_leanto | lantern_hanging |
  |---|---|---|---|---|---|---|---|---|---|
  | 27 | 21 | 76 | 16 | 9 | 2 | 686 | 12 | 4 | 7 |

  | lantern_post | leafclump | palm_l | palm_lean_a | palm_lean_b | palm_m | palm_s | planks | reef_ring | rock_l |
  |---|---|---|---|---|---|---|---|---|---|
  | 3 | 764 | 97 | 26 | 28 | 68 | 20 | 18 | 1 | 67 |

  | rock_m | rock_s | rope_coil | rowboat_broken | ruin_wall | spar_snapped | vine_arch | vine_strip | **ruin_arch** |
  |---|---|---|---|---|---|---|---|---|
  | 266 | 741 | 10 | 1 | 3 | 10 | 37 | 26 | **0 (v19: 3)** |

**matpatch20:** `MATPATCH20 chunks 63 cellsPainted 3193 cellsSkipped 2885`. Of the 6078 cells, 2336 are Sand, 3701 LeafyGrass, 25 Grass and 16 Slate. Skipped cells are ones already at the target material, or Rock/Water/Air columns.

**grade20:** `GRADE20 after bright=1.60 haze=0.00 felt parts=18` (nothing changed; the values were already in place).

**chk20 after the rebuild:**
- **ALL EXPECTED GREEN**
- torches 15, flame / core / light / emitter bad 0
- meshparts **3122**, instances 3832, pointlights 71
- lantern_hanging PointLights 1.20/18 x7

**SoftPadLights:**
- Pad15 SoftLightAnchor1/2 `SoftPadLight` Enabled=false
- Pad17 SoftLightAnchor1/2 Enabled=false
- Pad16 both Brightness 0.5 (Range 30)
- All 6 still exist (none deleted).

**Mesh count:** 3122 MeshParts in workspace (run 1: 3299).

**sig16b:** **`rows=3501 desc=3581 hash=0cfae99d`** read twice, stable. It was still 0cfae99d at the end of the run, twice: felt material, Blockout lights and lighting are not in the Dressing signature.

## 3. Sand trail verification
### Route, ground truth
I read the top-surface terrain material of x -700..1000, z -652..500 (4-stud cells) straight from Studio voxels into `v20b_diag/topmap.png` / `topmap_clean.txt`.
- The trail is **continuous** from the pad 1/2 beach through 9, then 9→10 (beach, StepStones at 696-752,-26..-35 and 346-419,126-142), hub, 11→18.
- From 18 a Sand + StepStone leg runs down (632..693, -470..-158) to the beach by pad 9.
- All 2336 matpatch Sand cells read back as Sand.

### Overview shots
Straight down, north up, FOV 50: `cam_ov20` at (167,1150,-68); a-d at y 640-960.
- `overview_v20.png`: whole course
- `overview_paths_v20.png`: the same frame **annotated**: every trail cell projected; cyan = the rendered pixel reads as Sand, magenta = hidden or not reading
- `overview_paths_a_v20.png` (pads 1-5), `_b_` (6-10), `_c_` (10-14), `_d_` (14-18)

**Trail cells that read as Sand from overhead** (3x3 classifier majority at each projected cell):

| Shot | All in-frame trail cells | Worst legs |
|---|---|---|
| overview_v20 (as is) | **756 / 2336 = 32 %** | pad 12 15 %, pad 13 18 %, **pad 14 8 %**, pad 11 22 %, pad 15 23 % |
| test A: canopy_wall (Persistent) + Skyline palms hidden | 837 = 36 % | 12: 19 %, 13: 33 %, 14: 26 % |
| test B: A + every item whose footprint covers a trail cell hidden | 1069 = 46 % | 12: 54 %, 13: 44 %, 14: 31 % |
| overview_paths_a (1-5) | 41 % | |
| overview_paths_b (6-10) | 42 % | |
| overview_paths_c (10-14) | 22 % (A 30 %, B 44 %) | |
| overview_paths_d (14-18) | 34 % | |

Overall Sand pixel share of the frame: overview 8.8 % → A 9.3 % → B 10.0 %; c-frame 3.1 % → 3.9 % → 4.3 %.

### What hides the trail
Measured in Studio with an oriented footprint test: item box at 80 %, height > 3, against every trail cell. 822 of 2336 cells (35 %) are under something.

| Class (folder) | Trail cells covered | Parts | Notes |
|---|---|---|---|
| leafclump | 193 | 49 | worst: **pad 12 gap-fill, 15 `leafclump` in `Far`, 21-24 wide, 7-8 tall, at (-66..2, -112..-59) on the 11→12 leg** (7 of them centred on trail sand); 3 **Skyline** leafclumps 53-70 wide at (-192,-177), (-221,-165), (266,127) |
| rock_l | 176 | 7 | mostly 4 **Skyline** rock_l 137-191 wide sunk along 15→16 (-168..-243, -474..-593); 2 at (501,37)/(604,59); `Set` rock_l (99,62,-456) at the pad 16 clearing |
| fernclump | 166 | 48 | allowed on the edge, but 39 sit over the strip |
| vine_arch | 93 | 17 | arch rows over 10→hub (328,137)/(299,109)/(274,79) and 11→12 (38,-56)/(19,-60)/(-1,-65) |
| rock_m | 58 | 9 | **Set2 rock_m (269.6,70,-404.9), scale 4.0, 72 studs wide: a pad 17 boulder swap standing on the 16→17 trail** (`path_leg_v20.png`) |
| palm_l | 55 | 8 | all **Skyline** palms: (-414..-443, -255..-285) ×5 on 12→13, (48,-13)/(65,-8) on hub→11→12, (-190,-164) |
| BackdropPersistent (canopy_wall) | 53 | 9 | the strongest *visual* hider overhead (long dark bands). See the hide test `ovtc_nocanopywall.png` against `ovtc_noskypalm.png`. |
| rock_s / palm_lean_a / palm_m / hull_rib / palm_lean_b / planks / vine_strip | 47 / 22 / 17 / 13 / 5 / 4 / 1 | | Mid palms at (-209,-163), (-250,-174), (-175,-149), (-252,-179) on 12→13 |

**Hide tests** (Transparency only, restored; `_G.HIDDEN` pending 0 at the end):
- `ovt_noskyline.png` / `ovtc_noskyline.png`: Skyline + BackdropPersistent, 190 parts
- `ovtc_noskypalm.png`: 49 Skyline palms
- `ovtc_nocanopywall.png`: 141 BackdropPersistent + non-palm Skyline
- `ovt_A_v20.png` / `ovtc_A_v20.png`: 125 parts
- `ovt_B_v20.png` / `ovtc_B_v20.png`: +183 covering parts

**Even with all of them hidden (test B) only 46 % reads:** at whole-course scale the trail is 6-9 px wide, and in shade it renders grey-tan (92,84,77), close to the dark LeafyGrass.

**For the generator, to drop or move:**
1. the Persistent `canopy_wall`s inside the course hull (23 within x -650..1000 / z -650..480), at minimum these four:
   - (3.8,52.9,-94.5) 293×88
   - (2.5,24.1,-99.7) 102×30
   - (64.3,25.8,-37.7) 102×30
   - (-39.4,54.6,16.2) 293×88
2. Skyline palm_l / leafclump / rock_l inside the course (the coordinates above)
3. the pad 12 `Far` leafclump gap-fill on the 11→12 trail
4. the rock_m swap at (269.6,-404.9)
5. thin the vine_arch rows over 10→hub and 11→12
6. widen the jungle trail toward 12+ studs for an overhead read

### Vegetation on the trail
Dressing item centres within 1.5 studs of trail sand (matpatch Sand cells, Studio positions): **92 items**.
- fernclump **34**: Front 16, Edge 14, Fill 2, Mid 1, Moss 1
- rock_s **30**: Front 15, Edge 15
- **leafclump 13:**
  - 7 pad 12 `Far` gap-fill: (-65.7,-111.9), (-54.8,-100.9), (-57.6,-90.5), (-43.8,-92.5), (-32.2,-92.3), (-12.9,-75.9), (-5.1,-59.1)
  - Front (890.9,184.6), Front (579.8,-433.1)
  - 4 Edge (883,131), (204,332), (480,363), (879,128)
- **vine_arch 6** (arches straddle the trail by design)
- by design in the hub / tee areas: lantern_post (229.0,50.3), Torch_BackPad11, BackFill_Pad11, Torch_Hub02, Torch_CaveMouth, Torch_Pad06/08/15/17

**Excluding fernclump / rock_s / vine_arch / torches: 13 leafclumps + 1 lantern_post. Not 0** (expected 0). The pad 12 gap-fill is the main offender.

### Widths
Perpendicular Sand run on the Studio top map at 0.5-stud steps. Voxel-quantised at 4 studs, so the dithered edge adds up to about 4.

| Point | Width (studs) |
|---|---|
| leg 10→hub (297,108) | 9.0 |
| leg 11→12 (18,-59) | 13.0 |
| leg 12→13 (-240,-159) | 9.5 |
| leg 13→14 (-488,-290) | 8.5 |
| leg 14→15 (-514,-453) | 12.5 |
| leg 15→16 (-136,-514) | 14.0 |
| leg 16→17 (257,-425) | 9.0 |
| leg 17→18 (510,-403) | 8.0 |
| leg 18→beach (671,-276) | 13.0 |
| 9→10 near pad 9 (633,12) | 31.5 (open beach) |

### Hub, aprons, clearings
**Hub** (229.9, 62.9): 100 % Sand within r 10, **91 % within r 15**, 59 % within r 20.
- Items inside r 15: only lantern_post (12.6 from centre), Torch_BackPad11, Torch_Hub02 (both 10.0), BackFill_Pad11. No vegetation.

**Tee aprons** (r 6 Sand share at the best point on |u| = 32):

| Pad | 1-9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 |
|---|---|---|---|---|---|---|---|---|---|---|
| Sand | beach, 69-100 % | 70 % | 70 % | 93 % | 81 % | **58 %** | 86 % | 100 % | 93 % | 96 % |

Pad 14's apron sits partly on Rock: Rock isn't repaintable, so the trail start still reads as dark rock in `pad_14_back_v20.png`.

**Arch / cave clearings:**
- **Not verifiable as designed, because the ruin arches are missing.** At the v19 arch positions:
  - (359,127): 44 % Sand within r 7.5
  - (-361,-214): 32 %
  - (102,-479): **93 %**, a clear round clearing next to pad 16 (`arch_clearing_v20.png`)
- Cave mouth torch (600.5,-527.5): 42 % within r 7.5. The mouth area is part Sand, part Rock with StepStones (`cave_clearing_v20.png`).
- A search for ≥ 90 % r 7.5 Sand blobs on the jungle trail found only the hub and the pad 16 clearing as round clearings.

### StepStones
- **264 `StepStone` Parts in Dressing = 171 carried over from v19 + exactly 93 new.** All new positions were compared against v19's walk data; the 93 are listed by cluster in this run's log.
- Colour read from `stepstone_v20.png`: (94,96,89) and (83,85,82) in light shade. Base (132,128,106) Slate reads as a cool grey-green stone on the dark Rock.

### Rendered Sand colour (classifier medians)
| Shot | Sunlit | Shade |
|---|---|---|
| apron (pad 17) | (173,151,120) | (106,93,87) |
| path leg 16→17 | (141,121,99) | (92,84,77) |
| arch clearing | (169,147,115) | (92,84,77) |

- Open sand reaches about (170,148,118), not (226,184,128).
- **Hub with BackFill_Pad11 at the generator's 3 / 55: (255,229,157), blown out.** At 1.5 / 40: (249,213,143). Light off: **(234,182,125), on target.** Restored to 3 / 55.

**Edge blend:** soft. Sand fades into LeafyGrass over the 2-stud dither with no hard line (`apron_v20.png`, `path_leg_v20.png`).

### Problems
1. ruin_arch ×3 missing
2. the pad 12 leafclumps and the rock_m swap on the trail
3. Persistent canopy_walls across the jungle
4. the overhead read is limited by width and contrast even with nothing covering the trail
5. the hub is over-lit by BackFill_Pad11
6. the pad 14 apron is on Rock

## 4. Tee eye-height trail views
Same cam_tf cameras as v19 (`pad_N_v20.png`, retaken after the felt change).
- Trail cells within 160 studs were projected into each frame and the rendered pixel classified. Overlays: `v20b_diag/teeov_N_v20.png`.
- Then a yawed view from the same eye toward the outgoing leg (`pad_N_trail_v20.png`; overlays `teeov_N_trail_v20.png`).

| Pad | Sand share of frame | Trail cells in frame / reading | Visible? | Where it goes | Blockers on the eye→trail line (yawed view) |
|---|---|---|---|---|---|
| 1 | 0.0 % | 43 / 0 | **no** | trail starts under the wreck deck / stern | hull_rib (Debris) and the deck plate |
| 2 | 0.6 % | 28 / 0 | **no** | left, behind the rim | rock_s / fernclump (Edge), leafclump (Front) |
| 3 | 2.1 % | 52 / 12 | yes | left / centre (beach) | - |
| 4 | 0.4 % | 46 / 3 | **no** | ahead-left | rock_s ×5 / leafclump / fernclump (Edge) |
| 5 | 0.2 % | 32 / 1 | **no** | ahead-left | fernclump ×2, rock_s ×3 (Edge) |
| 6 | 0.4 % | 22 / 1 | **no** (yawed: weak) | left | fernclump (Edge) |
| 7 | 1.1 % | 57 / 5 | weak | left | rock_s ×2 (Edge) |
| 8 | 1.2 % | 24 / 5 | yes | centre (distant path up) | - |
| 9 | 2.6 % | 20 / 3 | weak (yawed: **yes**, 10 % sand, 30 cells) | right (to pad 10) | fernclump (Front) |
| 10 | 0.6 % | 70 / 16 | **no** (only the vine arch row shows) | right | rock_m (Front), fernclump (Moss) |
| 11 | 2.3 % | 66 / 6 | **no** | left | none: grazing angle behind the rim hedge |
| 12 | 0.7 % | 58 / 13 | **no** | right | none: grazing angle / rim |
| 13 | 0.7 % | 70 / 6 | **no** | left | none: grazing angle / rim |
| 14 | 0.7 % | 72 / 10 | weak | right | rock_m (Front), fernclump (Moss) |
| 15 | 1.8 % | 72 / 11 | weak | right | - |
| 16 | 3.0 % | 95 / 31 | yes | right | - |
| 17 | 2.3 % | 86 / 61 | **yes** | left, the clearest of all | - |
| 18 | 1.3 % | 63 / 6 | weak | left, up the rock to the cave mouth (reads as rock) | leafclump ×2 (Front) |

**Failed (generator should open the canopy / hedge or widen there): 1, 2, 4, 5, 6, 10, 11, 12, 13.** Weak: 7, 9, 14, 15, 18.

Cause: the tees face along the felt and the trail leaves at |u| 32, at ground level behind a continuous Edge hedge of rock_s / fernclump / leafclump. At 6 studs eye height an 8-stud strip 40-90 studs out is a sliver.

Suggested fix: leave a 10-12 stud gap in the Edge layer where the apron meets the rim on the trail side, keep Edge items under 2 studs tall within 20 studs of the apron, and widen the first 30 studs of each outgoing leg.

**Shots:**
- `pad_{1,2,4,5,6,7,9,10,11,12,13,14,15,18}_trail_v20.png`
- `path_leg_v20.png` (16→17; the rock_m swap on the trail)
- `hub_v20.png` (hub: 2 tiki torches + lantern post on the Sand clearing)
- `apron_v20.png` (pad 17)
- `arch_clearing_v20.png` (pad 16 clearing, no arch)
- `cave_clearing_v20.png`
- `stepstone_v20.png` (pad 12 stones on Rock)
- hub light test: `hub_bf150_v20.png`, `hub_bfoff_v20.png`

## 5. Hut lanterns
7 in-range lantern_hanging lights at **1.2 / Range 18 / Color (255,235,200)** from the placer. Run 1 had 8; one lantern near a hut is no longer generated.

| Lantern brightness (colour 255,235,200) | Thatch (600,200) | Thatch (750,280) | Post (960,560) G/R | Post (330,500) G/R | Deck (640,700) |
|---|---|---|---|---|---|
| **1.2 (generator, kept)** | **(207,167,66)** | (179,138,49) | (153,69,25) 0.45 | (169,105,41) 0.62 | (92,51,31) |
| 1.0 | (197,157,60) | (169,128,44) | (145,63,23) 0.43 | (159,96,38) 0.60 | (91,51,31) |
| 1.5 | (218,181,75) | (192,151,56) | (164,77,28) 0.47 | (183,117,46) 0.64 | (95,52,31) |
| 1.2 + hut torches Range 12 (test) | (206,167,66) | (179,138,49) | (147,67,25) 0.46 | (169,105,41) 0.62 | (92,51,31) |
| 1.2 + hut torches Range 10 (test) | (206,167,66) | (179,138,49) | (138,66,25) 0.48 | (169,105,41) 0.62 | (92,51,31) |
| lanterns off (`hut_posts_lightsoff_v20.png`) | (89,62,23) | (78,57,19) | (94,30,13) 0.32 | (70,43,21) 0.61 | (84,47,30) |
| lanterns off + torches Range 12 | (85,62,23) | (78,57,19) | (80,28,13) 0.35 | (70,43,21) 0.61 | (84,47,30) |
| all warm lights off | (85,62,23) | (78,57,19) | (47,24,13) 0.51 | (70,43,21) 0.61 | (84,47,30) |

**Thatch:**
- Target (200,165,90) ±12: at 1.2 it is **+7 / +2 / -24**, so R and G pass and B is 24 low.
- No brightness fixes B: 1.5 gives +18/+16/-15, 1.0 gives -3/-8/-30.
- **Final: 1.2 kept** (3 brightness iterations, plus 2 torch-range tests).

**Posts:**
- The G/R > 0.65 bar is **not reachable with lighting**. The post texels are (110,70,40) = G/R 0.64 and (140,95,55) = 0.68, and with every warm light off the right post reads (47,24,13), G/R 0.51.
- The right post's orange is mostly the lantern 6.4 studs away (R 153 → 94 with lanterns off).
- The pad 5 torch at Range 12 takes off only about 6 R. **The generator's "torch near hut → Range 12" rule is not active:** every torch is Range 14, because the torch-to-hut-centre distances are Torch_Pad05 26.5, Torch_Pad12 26.5, Torch_Pad08 31.9 against the < 24 threshold. Use a 34-stud threshold, or measure to the hut's bounding box.
- Torch ranges restored to 14 (generator output).

**Glass:** `lantern_v20.png`, Neon glass still glows.

**Restore:** lantern lights back to 1.2 / Enabled 7/7 / (255,235,200); torch ranges back to 14.

## 6. Torch gap table
`v20bs/torch20b.luau`, read-only. The base is the model's bounding-box bottom, the terrain is a ray at the base xz, and the ring is 4 rays 0.8 studs out.

| Torch | Kind | u | v | Base Y | Terrain Y | Gap | Terrain ring | Status |
|---|---|---|---|---|---|---|---|---|
| Torch_Pad01 | rim | 21.0 | -2.0 | 32.90 | deck plate top 33.02 | **-0.12** | sea below | ok: stands on the deck |
| Torch_Pad04 | rim (short) | -24.0 | -2.0 | 8.37 | 8.47 | -0.10 | 8.47..8.47 | ok |
| Torch_Pad05 | rim | -24.0 | -2.0 | 10.36 | 10.46 | -0.10 | 10.46..10.47 | ok |
| Torch_Pad06 | rim | 24.0 | -2.0 | 8.37 | 8.47 | -0.10 | 8.46..8.47 | ok |
| Torch_Pad08 | rim | 24.0 | -10.0 | 10.37 | 10.47 | -0.10 | 10.47 | ok |
| Torch_Pad10 | rim | 24.0 | -2.0 | 12.85 | 12.95 | -0.10 | 12.93..12.95 | ok |
| Torch_Pad12 | rim | 24.0 | -2.0 | 19.86 | 19.96 | -0.10 | 19.95..19.96 | ok |
| Torch_Pad15 | rim | -24.0 | -2.0 | 43.84 | 43.94 | -0.10 | 43.93..43.95 | ok |
| Torch_Pad17 | rim (short) | 24.0 | -2.0 | 75.86 | 75.96 | -0.10 | 75.96..75.97 | ok |
| Torch_Pad18 | rim | 24.0 | -2.0 | 98.29 | 98.39 | -0.10 | 98.12..98.69 | ok |
| Torch_BackPad11 | hub (moved pad 11 back torch) | (34.9, -80 from pad 11) | | 11.54 | 11.64 | -0.10 | 11.62..11.65 | ok |
| Torch_Hub02 | hub | - | - | 8.72 | 8.82 | -0.10 | 8.79..8.85 | ok |
| Torch_CaveMouth | cave mouth | - | - | 86.67 | 86.67 | **0.00** | **85.39..87.60** | centre ok, but on a 2.2-stud slope across 1.6 studs: the downhill side floats up to about 1.3, the uphill side is buried about 0.9 |
| Torch_BackPad10 | back | 15.0 | -48.0 | 12.13 | 12.23 | -0.10 | 12.07..12.35 | ok |
| Torch_BackPad12 | back | 15.0 | -48.0 | 19.06 | 19.16 | -0.10 | 19.01..19.31 | ok |

**Pad 1 hull** (EditableMesh raycast on `WreckV2.wreck_hull`, read-only; the mesh is not resized):
- Vertical hull crossings at the torch xz: **33.02 (deck top) / 31.50**. Base 32.90, so it stands on the plate with a 0.12 sink (the generator's FeltTopY 27 + 5.9).
- **Nearest hull surface horizontally from the post axis (base +1..+10, 24 directions): 3.29 studs** (at +1, direction 165°). The torch bbox is 4.78 × 11.14 × 4.78, so the bowl edge clears the hull by about 0.9 and the thin post by more.
- `pad_1_v20.png` / `torch_closeup` show the whole torch on the deck.

## 7. Felt (9×9 median)
SoftPadLights set as briefed. Relative camera = felt-local (0,6,24) → centre.

| Pad | Tee view (680,650) | Relative view (680,600) |
|---|---|---|
| 5 | (105,186,103) | (82,162,84) (local shade at that spot, as in run 1) |
| 15 | (105,186,103) | (104,185,100) |
| 16 (SoftPadLight 0.5) | **(124,201,113)** | (123,200,110) |
| 17 | **(105,186,103)** | (104,185,100) |
| 18 | (105,186,103) | (105,185,101) |

- **Pad 17 is fixed** and identical to 5/15/18.
- Pad 16 at 0.5 is about +19/+15/+10 brighter. Tests (restored to 0.5): **0.25 → (115,194,108)**, **0.15 → (112,191,107)**. Off was (84,163,88) in run 1. So about 0.1-0.15 matches the others; 0.5 is acceptable as "slightly different".
- After the Plastic change (final fronts) the tee medians are (105-106,185-186,99-100) on pads 2, 3, 5-9, 11, 13-15, 17, 18. Pad 16 is (125,200,110). Pad 10 is (114,190,101) (torch warmth).
- **Pad 12 is (178,225,120):** a strong warm pool from BackFill_Pad12 (Range 55, Brightness 3, a v16 setting), not the felt.
- Pads 1 and 4 sample the deck / shade at that pixel.

## 8. Felt grain
Pad 5 only first. 40×40 patch, median and population std per channel.

| Material | Tee view median (680,650) | Tee std | Close-up median (680,700) | Close-up std | Verdict |
|---|---|---|---|---|---|
| SmoothPlastic (before) | (105,186,103) | 0.3 / 0.4 / 0.7 | (89,171,87) | 0.40 / 0.56 / 0.44 | baseline |
| **Plastic** | **(106,186,100)** ✓ | 0.5 / 0.5 / 0.6 | (91,172,89) | **1.38 / 1.31 / 1.00** | colour kept; fine grain visible up close; std rise below the 2-6 target |
| Fabric (option a) | (86,160,79) ✗ (-19/-26/-24) | 1.4 / 1.5 / 1.2 | (75,147,72) | 7.4 / 10.2 / 6.5 | nice weave but too dark; rejected |
| Carpet (extra) | (123,172,120) ✗ (G -14, desaturated) | 3.1 / 3.0 / 2.8 | (104,154,105) | 11.3 / 12.5 / 9.7 | speckled grey; rejected |

- Option (b): **no MaterialVariant or SurfaceAppearance exists in the place**, so not possible without an upload. Not done.
- Option (c): not used.
- **Decision: `Felt.Material = Enum.Material.Plastic` applied to all 18 felts** (Color unchanged (87,147,79), chk20 still green). It is the only option inside the ±6 colour bar. The grain is subtle: close-up std is about 1.0-1.4 (3× SmoothPlastic), not 2-6.
- If the brief's std target matters more than "built-in only", the next step would be a custom MaterialVariant (needs an upload, not done).
- Image: **`felt_grain_v20.png`**: SmoothPlastic | Plastic (applied) | Fabric, same close-up camera.

## 9. Sun angle (optional; done)
| Setting | Sun elevation | Pad 5 felt / felt contrast (P90-P10 lum) / lower-frame contrast | Pad 17 felt / felt contrast / lower-frame contrast |
|---|---|---|---|
| ClockTime 12.0 (generator) | 33.5° | (106,186,100) / 37 / 59 | (106,186,100) / 20 / 54 |
| ClockTime 11.5 | 33.2° | (106,185,100) / 40 / 60 | (106,185,100) / 20 / 54 |
| ClockTime 12.5 | 33.2° | (106,185,100) / 34 / 59 | (106,185,100) / 20 / 55 |
| GeographicLatitude 84 (clock 12) | 29.5° | (104,183,98) / 41 / 59 | (104,183,98) / 21 / 55 |

At latitude 80, ClockTime ±0.5 h only swings the sun azimuth (±0.07 in x). Latitude 84 lowers it 4° with felt Δ ≤ 3 and no visible gain (`sun_pad*_*.png`). **Not clearly better, so reverted: ClockTime 12, GeographicLatitude 80 (generator values unchanged).** Brightness, Ambient, Exposure, ColorShift, Bloom and Atmosphere were not touched.

## 10. Back views and boulders
Run 1 copies kept as `pad_11_back_v20_run1.png` and `pad_12_back_v20_run1.png`.

**Pad 11 back (`pad_11_back_v20.png`):**
- **The canopy_wall at about 44 studs is gone**: open sky and palms over the trail.
- **No high leafclump over the eye.**
- The back torch now stands at the hub, so the near view loses its warm accent.
- Darkest 5 % mean luminance 16.7 (run 1: 22.5): the darkest spots are now palm trunks against the sky (L 6-8), not a wall. Share of L < 20: 3.5 %.

**Pad 12 back (`pad_12_back_v20.png`): not improved.**
- **Darkest 5 % mean luminance 10.8 (run 1: 10.6)**, P5 14, **11.2 % of pixels below L 20** (run 1: 11.7 %). Darkest spots (0,7,0) / (13,1,0) at the top-left and centre.
- The 36 low `leafclump` gap-fills don't fill it. The near-black mass is **Persistent `canopy_wall`s** straight ahead:
  - **(3.8,52.9,-94.5) 293×88** and **(2.5,24.1,-99.7) 102×30**, both at 105 studs
  - plus (64.3,25.8,-37.7) and (-39.4,54.6,16.2) at the sides
- Hide test: BackdropPersistent hidden → darkest 5 % mean **21.0**, L < 20 only **1.6 %**, and the view opens to palms and sky (`p12back_nobackdrop_test.png`). Skyline hidden alone → 17.4 / 5.9 % (`p12back_noskyline_test.png`).
- **Generator: drop or relocate those canopy_walls** (they also cross the 11→12 trail from above).

**Boulders** (`boulders_pad16_v20.png`, `boulders_pad17_v20.png`, `boulders_pad18_v20.png`; view from behind each tee toward the Set2 boulder centroid):
- 29 Set2 boulder items around pads 16-18: 15 piles (scale 1.74-2.86, new random yaws) and **14 swaps (7 rock_m at scale 3.54-4.0, 7 rock_l at 1.93-2.18)**. In v19 all were piles at scale 2.30.
- Silhouettes read varied in the shots: green-capped piles next to bare angular rocks.
- One v19 pile at (295.5,-416.0) is no longer generated.
- **Issues:**
  1. rock_m (269.6,-404.9) at scale 4.0 sits on the 16→17 trail
  2. two overlapping pairs carried over from v19's data: (584.1,-276.6)/(584.6,-275.7) piles, and (595.4,-319.1) rock_l / (596.0,-318.2) rock_m. These are double placements; drop one of each.

## 11. Screen set
Everything is in `~/stage/shots14/`, 1360×877 viewport crop.
- Every image was looked at, individually or on a sheet.
- **halo.py = 0 on every shot.**
- shoot.sh swept and parked the cursor before each shot.
- The camera was restored to Custom FOV 70 after every batch.
- **LocalTransparencyModifier nonzero 0.**

**Shots:**
- **Fronts / backs:** `pad_1_v20` … `pad_18_v20` (retaken after the felt change), `pad_1_back_v20` … `pad_18_back_v20`
- **Run 1 list:**
  - `overview_v20` (now the straight-down whole course; the old oblique cam_ov12 view is `overview_oblique_v20`)
  - `jungle_v20`: cam_j12 now sits inside the new vine_arch at (-0.8,-64.5), so mostly arch foliage; a camera issue, not a scene defect
  - `torch_closeup_v20`, `torch_check_pad5_v20`, `hut_closeup_v20`, `hut_posts_lightsoff_v20`, `lantern_v20`
  - `panel_pad6/13/18_v20`, `cliff_pad18_v20`, `hump_pad17_v20`, `ruinwall_v20`
- **New:**
  - `overview_paths_v20` (annotated), `overview_paths_a..d_v20`
  - `pad_N_trail_v20` ×14, `path_leg_v20`, `hub_v20`, `apron_v20`, `arch_clearing_v20`, `cave_clearing_v20`, `stepstone_v20`
  - `felt_grain_v20`, `boulders_pad16/17/18_v20`, `pad_11/12_back_v20_run1`
- **Evidence:**
  - `ovt_*`, `ovtc_*`, `p12back_*_test`
  - `hub_bf150_v20`, `hub_bfoff_v20`
  - `hut_*_v20b`
  - `felt_tee_*_v20b`, `felt_cu_*_v20b`, `felt_rel_pad*_v20b`
  - `pad16_soft0*_v20b`, `sun_pad*`
- **Diagnostics:** `~/stage/v20b_diag/`: top map, overlays, tee overlays, item export.

**Contact sheets (`tools16/sheet.py`, overwritten) in `shots14/sheets_v20/`:**
- `fronts_1_9_v20.png`, `fronts_10_18_v20.png`, `backs_1_9_v20.png`, `backs_10_18_v20.png`
- `misc_v20.png` (run 1 list), `misc2_v20.png` (overviews, hub, legs, clearings, stones)
- new: `misc3_v20.png` (grain, back views, boulders), `trail_v20.png` (yawed trail views)

## 12. Final checks (unsaved place)
**chk20: ALL EXPECTED GREEN.**
- grey 0
- torches 15, flame / core / light / emitter bad 0
- other Neon 0
- meshparts 3122, instances 3832, pointlights 71
- clock 12, lat 80, bright 1.60, exp -0.30, haze 0
- CC sat 0 / contrast 0.05; Bloom 1.1 / 0.35
- felt 18 / 0 bad at (87,147,79)
- footprints 5 / 0
- glows SmoothPlastic; backfill 3; huts 4 / 0
- lanterns 1.20/18 x7
- sha c2339cd, dirty false; streaming true; http false

**terr16b:** unchanged and green: hump voxels Air / LeafyGrass 0.26 / Air, Rock region 286 Rock / 0 LeafyGrass, cave_cliff_lower (115,100,92).

**Terrain materials (`terrhist20`, run 1 area x -616..616, z -572..244; total 1,058,149, unchanged):**

| Material | v19 | Run 1 | **Now** |
|---|---|---|---|
| Ground | 11,955 | 0 | **0** |
| LeafyGrass | 143,983 | 152,744 | **152,355** |
| Sand | 9,504 | 12,773 | **13,966** |
| Grass | 7,899 | 7,824 | **7,173** |
| Slate | 2,513 | 2,513 | **2,360** |
| Rock | 880,950 | 880,950 | **880,950** |
| Water | 1,345 | 1,345 | **1,345** |

Wider area (x -704..1024, z -652..500, `v20bs/terrhist20b.luau`): Grass 13,956 / LeafyGrass 246,183 / Rock 1,530,248 / Sand 79,280 / Slate 2,921 / Water 6,869.

**sig16b: `0cfae99d` (rows 3501, desc 3581), twice.** Once the generator's own output is re-imported unchanged, a fresh ltdr20 should hash 0cfae99d.

**Restore audit:**
- Disabled lights in workspace: exactly the 4 pad 15 / 17 SoftPadLights (intended)
- Pad 16 SoftPadLights 0.5
- Dressing fully transparent parts 0 (besides the invisible BackFill anchors); `_G.HIDDEN` empty
- Lantern lights 1.2 / Enabled; torch ranges 14
- BackFill_Pad11 3 / 55
- Pad 5 felt Plastic like the other 17
- ClockTime 12 / latitude 80
- Camera Custom FOV 70, HttpEnabled false

## 13. In the open place vs v19 (all unsaved)
1. ltdr20 Dressing, the generator's run-2 output exactly as written (lantern 1.2 / (255,235,200), torches, hub props, StepStones, boulder swaps)
2. matpatch20 terrain materials
3. grade20 (no-op)
4. SoftPadLights: pads 15 and 17 Enabled=false, pad 16 Brightness 0.5
5. **all 18 Felt.Material = Plastic** (the only value tuned by hand this run)

All other tests were reverted.

## Values for the generator
- **Felt material: `Enum.Material.Plastic`** (Color stays (87,147,79)). Fabric is rejected (-20 darker).
- **Lantern: keep `HUT_LANTERN_BRIGHT = 1.2`, Color (255,235,200)**. Thatch (207,167,66) is the best reachable; B stays about 24 low.
- **Hut-torch Range rule: fix the threshold.** The torch-to-hut-centre distances are 26.5 / 26.5 / 31.9, so use < 34, or the hut bbox. Even at Range 12 the posts stay orange from the lantern. The post G/R bar isn't reachable by light.
- **Pad 1 torch: keep FeltTopY + 5.9.** It stands on the deck (gap -0.12, hull clearance 3.29 from the axis).
- **Cave mouth torch:** pick a flatter spot or sink it about 1 (terrain slope 85.4-87.6 under the base).
- **ruin_arch ×3 restore.** They're missing from dressing_v20 (v19 positions (359.2,127.2), (-361.2,-214.1), (101.8,-478.8)). The clearings then need to be centred on them; only the (102,-479) one exists as a round Sand clearing.
- **Remove from the trail:**
  - the pad 12 `Far` leafclump gap-fill at (-66..2, -112..-59), 15 items over the 11→12 leg
  - Set2 rock_m (269.6,-404.9)
  - Skyline palm_l / leafclump / rock_l inside the course (coordinates in §3)
- **Persistent canopy_walls inside the course: drop them.** At least (3.8,52.9,-94.5), (2.5,24.1,-99.7), (64.3,25.8,-37.7), (-39.4,54.6,16.2) for the pad 12 back view and the overhead read. All 23 within the course hull should be reviewed.
- **Tee visibility:** open a 10-12 stud gap in the Edge hedge at the apron/rim on the trail side for pads 1, 2, 4, 5, 6, 10, 11, 12, 13 (weak: 7, 9, 14, 15, 18), and widen the first 30 studs of each outgoing leg.
- **Overhead read:** widen the jungle trail toward 12+ studs. The trail is 8-14 now and reads 32 % from overhead.
- **Hub lighting:** BackFill_Pad11 at the hub blows the Sand out (255,229,157). Disable it, or set 1.5 / 40; with it off the hub reads (234,182,125).
- **Pad 16 SoftPadLight:** about 0.15 matches the other felts; 0.5 is +19 brighter.
- **Duplicate boulder placements:** (584.1,-276.6)/(584.6,-275.7) and (595.4,-319.1)/(596.0,-318.2). Drop one of each.
- **Pad 14 apron / trail start sits on Rock** (not repaintable): move the apron or allow Rock → Sand there.
- **Sun:** keep ClockTime 12 / latitude 80.

## Problems / not done
- The arch clearings couldn't be checked against arches (none exist). `arch_clearing_v20.png` shows the pad 16 clearing without one.
- The felt grain std target (2-6) is not met by any built-in option that keeps the colour. A custom MaterialVariant would need an upload, so it was not done.
- The hut post bar (G/R > 0.65) is unreachable by lighting; the thatch B channel is 24 low.
- `jungle_v20.png` (cam_j12) now frames the inside of a vine arch. The camera should be moved for future runs.
- The tee trail views (`pad_N_trail_v20.png`) and the walking views were shot before the felt material change; only the felt gloss differs.
- **Not done, per the brief:**
  - no Save, no Publish, no version bump, no Version History check
  - no deploys row, no `tools/stamp`, no asset uploads
  - no MaterialVariant creation, no Script edits
  - nothing generator-side changed in `~/stage/*.luau`; new files only in `v20bs/`, `v20b_diag/` and new `cam_*`
- **Studio state:**
  - pid 65929 is open on the **unsaved** v20-prep place, MCP connected
  - pids 18508, 30033, 34084, 61461, 62563, 78191, 93578 untouched
  - :8765 (pid 9525) and :8767 (/tmp/v20/shotsrv.py, pid 96516) still up

**Place UNSAVED, NOT PUBLISHED, version still 19.**

DONE_V20B
