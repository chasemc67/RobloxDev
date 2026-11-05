# Pirate Shipwreck v20 FINAL RUN report (v20c)

**Result: PUBLISHED as version 20, private.**
- Save to Roblox at 2026-11-01T15:43:36Z.
- File > Publish (existing place) at **2026-11-01T15:43:57Z = 07:43:57 AM PST**. Log: `→ Add publish notes to v20`, then `Published new changes in "Pirate Shipwreck" to Roblox.`
- Reopened with the protocol URL as new pid **5180**. Log `0.745.0.7451137_20261101T154432Z_Studio_032dc_last.log`: `DataModel Loading https://assetdelivery.roblox.com/v1/asset/?id=131316561222931&version=20` at 15:44:37Z.
- chk20, the scoped lantern check, sig16b ×2 and terr16b on the reopened place are **line-for-line identical** to the pre-publish run. Sig **13e15e2d** before and after.
- Private, HttpEnabled false, no Robux, no Team Create, no Scripts through MCP, nothing deleted. Pid 18508 not touched; every GUI input went through activate-by-pid with a frontmost-pid check. No Screen Recording prompt.

**One acceptable deviation, read this first.** `chk20` ends `ALL EXPECTED RED`. The only two FAIL lines are the lantern rules:
- `hut lantern lights 0.4 / range 6` FAIL
- `hut lantern shadows on` FAIL

Cause: chk20 matches every `lantern_hanging`. dressing_v20 now restores the 3 `ruin_arch`, and each has a hanging lantern at the generator's default 4.00/18, shadows off. In the data they are anchored to the arch centres (359.2,127.2), (-361.2,-214.1), (101.8,-478.8) at offset 27, not to a hut. Run 2 had no arches, so this never showed.
- The 7 hut lanterns are all 0.40 / 6 / Shadows on / Enabled. Scoped check `v20cs/chk20c_lant.luau`: `hut lanterns 7 all 0.40/6/shadows/enabled=true | non-hut lanterns 3` (each about 8.5 studs from an arch centre).
- Every other chk20 EXPECT line is ok.
- I judged this a check-scope bug from a listed change (the arch restore), not a scene defect, and published. **chk20 needs its lantern rule scoped to hut lanterns** (or the generator should decide what the arch lanterns get).

**Look at these:**
1. **Haze 0.5 brings the grey band back.** Measured (131,138,155) against sky (125,180,208) just above it. It is plainly visible above the sea in elevated views (`arch_clearing_v20`, `boulders_pad16_v20`, oblique overview), and faintly in `pad_16_back`. It is the band v19 removed with Haze 0. Not changed, per the brief.
2. **Hut thatch now reads like the lights-off state**, (87,64,24) against the (200,165,90) bar. Posts still fail G/R. The dark-wood texel test makes the posts darker and redder, not browner (§4).
3. **Tee-view trail still fails on pads 1, 2, 4 and 5**, and is weak on 7-11 (§6).

---

## 1. Preflight
- MCP studio "Pirate Shipwreck (placeId 131316561222931)". Marker `V20C_MARKER_5182` landed in pid 65929's log (`..._20261101T132308Z_Studio_c0bae_last.log`). PlaceVersion 0 (the unsaved run-2 place).
- Docks closed, viewport full width (full-screen check), vp14.env (280,166,1360,877) still valid.
- Helpers up and reused: :8765 (pid 9525), :8767 `/tmp/v20/shotsrv.py` (pid 96516), `/tmp/v20/shoot.sh`, `/tmp/v20/act.sh`. New `/tmp/v20c/mk.sh` writes batches to `~/stage/v20cs/`.
- HttpEnabled false throughout. Every batch ends `http false`.
- Run 2's `_v20` shots were copied to `~/stage/shots14_v20b_run2/` before being overwritten.

## 2. Rebuild
**ltdr20:** loaded with a fresh cache key. `LT20D run ok=true nil http=false`.

Placer log:
- `DR templates 34`
- `walkways: 99 boardwalk planks, 264 stepping stones`
- `mouth torch ground 86.7 on Terrain`
- **`torches 15`**
- **`hut lanterns lowered 7 (brightness 0.4)`**
- `kit_v2 point lights 28`
- **`placed 2957 (skipped wet/no-ground 0)`**, cave vine strips 6
- `DONE instances 3504`

Counts:

| barrel | boulder_pile | canopy_wall | cliff_ridge | crate | crate_stack | fernclump | hull_rib | hut_leanto | lantern_hanging |
|---|---|---|---|---|---|---|---|---|---|
| 27 | 20 | **67** (run 2: 76) | 16 | 9 | 2 | 657 | 12 | 4 | **10** (7 hut + 3 arch) |

| lantern_post | leafclump | palm_l | palm_lean_a | palm_lean_b | palm_m | palm_s | planks | reef_ring | rock_l |
|---|---|---|---|---|---|---|---|---|---|
| 3 | 728 | 94 | 24 | 28 | 66 | 20 | 18 | 1 | 61 |

| rock_m | rock_s | rope_coil | rowboat_broken | **ruin_arch** | ruin_wall | spar_snapped | vine_arch | vine_strip |
|---|---|---|---|---|---|---|---|---|
| 263 | 737 | 10 | 1 | **3** | 3 | 10 | 37 | 26 |

**matpatch20, grade20:** both `ok=true`. matpatch20 holds 6264 cells: 2504 Sand, 3706 LeafyGrass, 35 Grass, 19 Slate.

**In the open place, set by hand:**
- SoftPadLights: Pad15 ×2 and Pad17 ×2 Enabled=false; Pad16 ×2 Brightness 0.15 (Range 30). All 6 still exist.
- All 18 Felt: Material Plastic, Color (87,147,79).

**chk20:** every EXPECT ok except the two lantern lines above.
- torches 15, all bad counts 0
- meshparts 3036, instances 3755, pointlights 74
- clock 12, lat 80, bright 1.60, exp -0.30
- Atmosphere dens 0.200 / offset 0.05 / haze 0.50 / glare 0.40, Color (255,235,210), Decay (190,150,110)
- CC sat 0 / contrast 0.05; Bloom 1.1 / 0.35
- felt 18 / 0 bad; footprints 5 / 0
- glows SmoothPlastic; backfill 3; huts 4 / 0 bad
- sha c2339cd, dirty false; streaming true; http false

**sig16b:** `rows=3418 desc=3504 hash=13e15e2d`, twice. It was still the same at the end of the run and on the reopened place.

**terr16b:** green. Hump voxels Air / LeafyGrass 0.26 / Air; rock region 286 Rock / 0 LeafyGrass; cave_cliff_lower (115,100,92).

**Terrain materials** (`terrhist20b`, wide area). Rock and Water are unchanged, so no terrain damage:

| | Grass | LeafyGrass | Rock | Sand | Slate | Water |
|---|---|---|---|---|---|---|
| run 2 | 13,956 | 246,183 | 1,530,248 | 79,280 | 2,921 | 6,869 |
| **v20** | 13,866 | 245,790 | **1,530,248** | 79,781 | 2,903 | **6,869** |

## 3. Atmosphere (Density 0.2 / Haze 0.5 / Color (255,235,210))
- Read-back: `dens=0.200 haze=0.50 col=(255,235,210) decay=(190,150,110) glare=0.40 off=0.05`.
- Same-scene A/B: Density 0.04 / Haze 0 (run 2) against the new values, then restored to the new values. Shots `atm_*_before/after_v20c.png`.

| Point | Before (0.04 / 0) | After (0.2 / 0.5) |
|---|---|---|
| Felt pad 5 tee (680,650) | (106,186,100) | (106,185,99) |
| Felt pad 17 | (106,186,100) | (106,185,99) |
| Felt pad 18 | (105,185,99) | (105,185,99) |
| Pad 18 cliff-view sand (680,410) | (189,165,124) | (188,165,124) |
| Pad 5 distant dark foliage (300,300) | (8,23,7) | (17,32,25) |
| Overview from y 1150, centre jungle | (51,103,40) | (70,109,62) |
| Overview, shaded jungle | (29,53,20) | (58,73,53) |
| **Oblique overview, horizon band** | (195,208,211) pale sky | **(125,137,155) grey band** |
| Oblique, beach sand (1100,700) | (142,94,56) | (140,99,72) |

- **Tee views:** felt, sand and near colours are unchanged (Δ ≤ 1); distant darks lift a little. Fine.
- **Overview from altitude:** a strong grey-green wash. Darks lift about 30 and saturation drops; the course looks flat from above.
- **Horizon band:** a flat grey-mauve band (131,138,155) above the sea. It shows in the oblique overview and in elevated in-course views (`arch_clearing_v20`, `boulders_pad16_v20`, `pad_16_back_v20`). It looks wrong to me; v19 fixed exactly this with Haze 0. Not changed (brief: don't touch).
- The trail overhead classifier is unaffected: 41 % at both settings.
- Bloom Threshold 1.1, untouched.

## 4. Hut lanterns at 0.4 / Range 6 / Shadows on
cam_hut sample points; 9×9 medians.

| Setting | Thatch (600,200) | Thatch (750,280) | Post (960,560) G/R | Post (330,500) G/R | Deck (640,700) |
|---|---|---|---|---|---|
| run 2: 1.2 / 18 | (207,167,66) | (179,138,49) | (153,69,25) 0.45 | (169,105,41) 0.62 | (92,51,31) |
| **v20: 0.4 / 6 / shadows, (255,235,200)** | **(87,64,24)** | (79,58,21) | (86,31,14) **0.36** | (84,49,24) **0.58** | (84,47,31) |
| lights off (`hut_posts_lightsoff_v20`) | (87,64,24) | (79,58,21) | (79,28,13) 0.35 | (70,43,21) 0.61 | (84,47,30) |
| Color (255,245,225) | (87,64,24) | (79,58,21) | (86,31,14) 0.36 | (84,50,24) 0.60 | (84,47,31) |
| Color (255,250,240) | (87,64,24) | (79,58,21) | (86,31,14) 0.36 | (84,50,24) 0.60 | (84,47,31) |
| Color (255,215,160) | (87,64,24) | (79,58,21) | (86,30,13) 0.35 | (84,49,23) 0.58 | (84,47,31) |

- **Thatch fails the bar** (200,165,90): at range 6 the lantern no longer reaches the roof underside, so the thatch reads exactly as with the lights off. Colour has no effect. `torch_check_pad5` shows the same: the thatch went from (227,194,87) to (129,98,40).
- **Posts:** dark brown, not saturated orange, but G/R 0.36 / 0.58 fails the > 0.65 bar. The right post (0.36) is lit by Torch_Pad05, so it stays at 0.35 with the lanterns off.
- **Lantern glow is still visible:** glass (166,130,71) and (229,152,75), Neon (`lantern_v20`, `hut_closeup_v20`).
- **Generator value:** keep the user's 0.4 / 6 / shadows. Colour (255,235,200) restored; no colour reaches the bar, so there is no colour to hand to the generator.

**Dark-wood experiment** (one hut, pad 5 hut `hut_leanto` at (460.1,23.2,428.9); in-memory EditableImage, cells r4c1 / r4c2 painted (80,50,30); reverted):

| | Post (960,560) | Post (330,500) | Deck (640,700) |
|---|---|---|---|
| original texture, lit | (86,31,14) G/R 0.36 | (84,49,24) 0.58 | (84,47,31) |
| dark wood (80,50,30), lit (`hutexp_darkwood_on_v20c`) | (51,16,8) 0.31 | (31,14,9) 0.45 | (54,31,24) |
| dark wood, lanterns off | (47,14,7) 0.30 | (25,12,8) 0.48 | (54,31,24) |
| restored (`hutexp_restored_v20c`) | (86,31,14) | (84,49,24) | (84,47,31) |

Restore verified: TextureID back to `rbxassetid://108289367129276` on all 4 huts (`HUT tex check n 4 bad 0`).

**For 3D Model Bot:**
- Asset: `hut_leanto` MeshPart, MeshId `rbxassetid://131857226019693`, TextureID `rbxassetid://108289367129276`, Color white, Plastic.
- Posts sample palette cells r4c1 / r4c2; texels (110,70,40) G/R 0.64 and (140,95,55) G/R 0.68.
- (80,50,30) renders **darker and redder** (G/R 0.31-0.48), so a darker red-brown texel cannot reach the bar. The warm grade, the shade and the pad 5 torch together drop rendered G/R by about 0.05-0.3 from the texel's.
- **What dark wood needs to be (estimate):** a lighter, less red texel, G/R ≈ 0.80-0.85 at value ~120-140, e.g. (130,108,85). Keep torches away from the post faces too.
- This is a texture change, so it needs a texture re-upload. Not done.

## 5. Trail (overhead)
**Shots:** `overview_v20` (cam_ov20, (167,1150,-68), straight down, FOV 50), `overview_paths_v20` (annotated: cyan = projected trail cell reads as Sand, magenta = hidden), `overview_paths_a..d_v20` (raw `overview_paths_*_raw_v20c`).
- Heights were re-read for the new 2504 Sand cells (terrain-only rays; the top surface ray-hit material is Sand on 2141).

| Frame | Trail cells reading Sand | Run 2 |
|---|---|---|
| **overview_v20** | **1019 / 2504 = 41 %** | 32 % (B-test 46 %) |
| run 2 image scored against the new cells | 31 % | |
| same scene, Haze 0 | 41 % | |
| a (pads 1-5) | 47 % | 41 % |
| b (6-10) | 57 % | 42 % |
| c (10-14) | 33 % | 22 % |
| d (14-18) | 41 % | 34 % |

Per nearest pad (overview):
- 2-9: 48-69 %
- 10: 40 %, 11: 34 %, 12: 42 %, 13: 34 %
- **14: 6 %**
- 15: 29 %, 16: 26 %, 17: 38 %, 18: 41 %

**What still hides it** (oriented footprint at 80 %, height > 3): **458 / 2504 cells = 18.3 %** (run 2: 35 %).

| Class@folder | Cells | Parts |
|---|---|---|
| vine_arch@Arches | 95 | 17 (by design) |
| fernclump@Front / @Fill / @Edge | 79 / 41 / 4 | 27 / 8 / 2 |
| rock_s@Front / @Edge | 35 / 7 | 18 / 8 |
| leafclump@Front / @Fill / @Set / @Skyline / @Far / @Edge | 32 / 17 / 15 / 12 / 4 / 2 | |
| rock_m@Front | 23 | 7 |
| palm_lean_a@Mid / palm_m@Mid / palm_lean_b@Mid | 22 / 14 / 6 | |
| rock_l@Skyline | 22 | 1 |
| palm_l@Skyline | 15 | 6 |
| ruin_arch@Set2 | 15 | 3 (by design) |
| hull_rib, planks, boulder_pile, torches, etc. | ≤ 8 each | |
| **canopy_wall@BackdropPersistent** | **1** | 1 (run 2: 53) |

The long dark canopy_wall slabs still lie across the jungle interior and read as dark bands, but they now sit beside the trail, not on it. Visually the jungle legs 10→14 read as a faint dashed strip between the vine-arch rows, and pad 14's leg is under rock / dark ground.

**Pass bar ("visible end to end from overhead"): partial.** Beach 1→9, 9→10, the hub and 15→18 read clearly. 11→14 is faint, and pad 14's start is not visible.

**Widths** (perpendicular Sand run on the generator cells, 4-stud quantised):

| Leg | 10→hub | 11→12 | 12→13 | 13→14 | 14→15 | 15→16 | 16→17 | 17→18 | 18→beach |
|---|---|---|---|---|---|---|---|---|---|
| Width | 13.0 | 12.5 | 9.0 | 8.5 | 12.5 | 13.5 | 8.5 | 7.0 | 12.5 |

17→18 at 7.0 is below the 7.6 minimum; quantisation adds about ±2.

**Hub** (229.9,62.9):
- Sand 100 % within r 10, 92 % within r 15, 60 % within r 20.
- Items inside r 15: lantern_post, Torch_BackPad11, BackFill_Pad11, Torch_Hub02 only.
- BackFill_Pad11 reads back 1.5 / 40 (also Pad10 1.5/40; Pad12 3/55).
- **Hub sand rendered (242,203,136)** (`hub_v20`). Run 2 at 3/55: (252,223,152); target (226,184,128). No longer blown out, still about +16 bright.

**Aprons:** `apron_v20` (pad 17) shows a sand apron to the rim.

**Arch clearings, with arches** (Sand share around the arch centre):

| Arch | r 7.5 | r 12 | Shot | Notes |
|---|---|---|---|---|
| (359.2,127.2) 10→hub | 43 % | 18 % | `arch_clearing_a_v20c` | straddles the trail with stepping stones; lantern hangs |
| (-361.2,-214.1) by pad 13 | 36 % | 15 % | `arch_clearing_b_v20c` | straddles the trail |
| (101.8,-478.8) pad 16 | 28 % | 38 % | `arch_clearing_v20` | **edge-on to the trail**: the trail runs beside it, not through it; one pillar stands by the felt |

The r 7.5 shares are low because the arch footprint is 34 × 13 and only the trail strip is Sand, so these are not round clearings.

**Cave clearing:** Torch_CaveMouth (600.5,-527.5), Sand 42 % r 7.5 / 45 % r 12 (`cave_clearing_v20`).

**StepStones:** 264 (`stepstone_v20`).

**Longest all-Sand straight:** jungle 128 studs, (-70,-502)→(58,-498), on the 15→16 leg; beach 109 studs.

**1.5-stud plant margin:** Dressing items (not Skyline / Persistent / Walkways) with centres within 1.5 studs of trail Sand: **69** (run 2: 92).
- rock_s 28, fernclump 19
- vine_arch 6 and ruin_arch 3 (by design)
- torches / hub props 9
- lantern_hanging 2 (on arch / hut)
- **leafclump@Edge 2: (883.3,131.0) and (878.8,127.5) by pad 8.** These are the only non-fern/rock plants left (run 2: 13 leafclumps).

## 6. Tee eye-height trail views
- `pad_N_v20` (cam_tf): trail cells within 160 studs projected and classified. Overlays in `~/stage/v20c_diag/teeov_*`.
- Pads that failed or read weak got a yawed view `pad_N_trail_v20` (`v20cs/cam_trcN`: tee eye, aimed at the centroid of trail cells ~55 studs out toward the next leg).
- Visible = ≥ 10 cells read as Sand; weak = 3-9; no = < 3.

| Pad | Tee: sand % / cells read | Yawed: cells read | Visible | Next leg | Cause when failing |
|---|---|---|---|---|---|
| 1 | 0.0 / 0 of 38 | 0 | **no** | ahead-left, off the stern | hull rail / deck |
| 2 | 0.5 / 2 | 1 | **no** | ahead-left | rim hedge (fernclump/rock_s), grazing angle |
| 3 | 2.7 / 25 | - | yes | ahead | |
| 4 | 0.4 / 3 | 3 | **no / weak** | ahead-right | Edge hedge |
| 5 | 0.6 / 2 | 2 | **no** | ahead-right | Edge hedge; hut on the right |
| 6 | 0.5 / 5 | **11** | yes (yawed) | ahead-right | |
| 7 | 0.6 / 5 | 9 | weak | ahead-right | hedge / grazing angle |
| 8 | 1.0 / 5 | 7 | weak | ahead-right | hedge |
| 9 | 2.2 / 7 | 5 | weak | ahead / right | fernclump Front |
| 10 | 1.2 / 9 | 10 | weak→yes | ahead to the hub | vine arch row / rim |
| 11 | 1.6 / 9 | 8 | weak | ahead | grazing angle behind the rim |
| 12 | 1.2 / 15 | - | yes | ahead | |
| 13 | 1.1 / 10 | - | yes | ahead-right | |
| 14 | 0.6 / 9 | **23** | yes (yawed) | ahead-right | |
| 15 | 2.0 / 11 | - | yes | ahead-right | |
| 16 | 1.7 / 23 | - | yes | ahead-right | |
| 17 | 1.8 / 59 | - | yes | left, clearest | |
| 18 | 0.9 / 11 | - | yes | left / up | |

- **Still failing: 1, 2, 4, 5. Weak: 7, 8, 9, 11.** (Run 2: 9 failed, 5 weak.)
- Cause: the 6-stud eye at a grazing angle over the rim plus the low Edge hedge. On pad 1 it is the wreck's rail and deck. The beach back views (`pad_1..9_back`) show the trail clearly.

## 7. Torch gap table
Base = model bbox bottom; terrain = ray at the base xz; ring = 4 rays 0.8 studs out.

| Torch | Kind | u | v | Base Y | Terrain Y | Gap | Ring | Status |
|---|---|---|---|---|---|---|---|---|
| Torch_Pad01 | rim | 21.0 | -2.0 | 32.90 | deck top 33.02 (hull mesh) | -0.12 | sea below | ok, on the deck plate |
| Torch_Pad04 | rim (short) | -24.0 | -2.0 | 8.37 | 8.47 | -0.10 | 8.47..8.47 | ok |
| Torch_Pad05 | rim | -24.0 | -2.0 | 10.36 | 10.46 | -0.10 | 10.46..10.47 | ok |
| Torch_Pad06 | rim | 24.0 | -2.0 | 8.37 | 8.47 | -0.10 | 8.46..8.47 | ok |
| Torch_Pad08 | rim | 24.0 | -10.0 | 10.37 | 10.47 | -0.10 | 10.47 | ok |
| Torch_Pad10 | rim | 24.0 | -2.0 | 12.85 | 12.95 | -0.10 | 12.93..12.95 | ok |
| Torch_Pad12 | rim | 24.0 | -2.0 | 19.86 | 19.96 | -0.10 | 19.95..19.96 | ok |
| Torch_Pad15 | rim | -24.0 | -2.0 | 43.84 | 43.94 | -0.10 | 43.93..43.95 | ok |
| Torch_Pad17 | rim (short) | 24.0 | -2.0 | 75.86 | 75.96 | -0.10 | 75.96..75.97 | ok |
| Torch_Pad18 | rim | 24.0 | -2.0 | 98.29 | 98.39 | -0.10 | 98.12..98.69 | ok |
| Torch_Hub02 | hub | - | - | 8.72 | 8.82 | -0.10 | 8.79..8.85 | ok |
| Torch_BackPad11 | hub | 34.9 | -80.0 | 11.54 | 11.64 | -0.10 | 11.62..11.65 | ok |
| Torch_BackPad10 | back | 15.0 | -48.0 | 12.13 | 12.23 | -0.10 | 12.07..12.35 | ok |
| Torch_BackPad12 | back | 15.0 | -48.0 | 19.06 | 19.16 | -0.10 | 19.01..19.31 | ok |
| **Torch_CaveMouth** | cave mouth | - | - | 85.67 | 86.67 | **-1.00** | 85.39..87.60 | sunk 1 stud by design: centre buried 1.0, downhill edge 0.28 above the base, so no visible float; fails the literal \|gap\| < 0.3 by design |

**Pad 1 hull** (EditableMesh, `WreckV2.wreck_hull` `rbxassetid://76701491754201`, read-only):
- vertical crossings 33.02 / 31.50 / …; gap -0.12
- nearest hull surface horizontally from the post axis: 3.29 studs (at +1, 285°); torch bbox 4.78 wide, so about 0.9 clearance at the bowl
- Unchanged from run 2.

## 8. Palms and back views
Tee = felt centre + 27·LookVector; eye = felt top + 5. Cones: r < 16; back cone 140° to 80 studs; forward cone 110° to 80 studs.

| Pad | Palms in the tee cone | Fern/leaf above eye-0.5 in the back cone |
|---|---|---|
| 10 | 0 | 0 |
| 11 | **palm_lean_b@Mid (135.7,30.2), 75.6 studs, forward cone** | 0 |
| 12 | 0 | 0 |
| 13 (extra) | palm_lean_a@Front 48.9 fwd, palm_lean_b@Mid 61.1 fwd, palm_m@Mid 73.2 fwd, palm_l@Skyline 70.2 back | leafclump@Fill 71.1 (+0.2) |
| 14 | 0 | 10 fernclump@Front at 42-76 studs, 0.2-1.3 tall: ground ferns on the slope behind pad 14, bases 0-11 studs **above** the eye; nothing hangs over the eye |

**Pad 11 back** (`pad_11_back_v20`):
- no canopy_wall at ~44 studs (open vine-arch tunnel to the hub)
- no high leafclump over the eye
- darkest 5 % mean 19.8, L < 20 1.7 %

**Pad 12 back** (`pad_12_back_v20`): **darkest 5 % mean luminance 22.4** (run 2: 10.8; target > 17), P5 27.5, **L < 20: 1.2 %** (run 2: 11.4 %). Pass. Part of the lift may be the atmosphere change.

**Pad 14 forward ground** (terrain rays, 110° cone, r 4-60):
- rise/run from the felt top: max 0.065, mean -0.03
- local gradient: max 0.75 at the cone edge, mean 0.033
- ground ahead is flat (centreline 28.0 at r 34-58)
- nothing above the eye (max ground -1.2 below eye)

**Pad 10 back:** darkest 5 % mean 23.1.

**Pad 14 back:** 19.0; it faces the grassy rise and rock.

## 9. Boulders, pads 16-18
`boulders_pad16/17/18_v20`.
- 32 Set2 boulder items: 20 boulder_pile, 6 rock_m, 6 rock_l, varied yaws.
- **No doubles** (no pair within 3 studs; run 2's (584.1/584.6) and (595.4/596.0) pairs are now single).
- **None on the trail** (0 trail cells under the 80 % footprint of any).
- rock_m all 43.5 wide, consistent with the scale ≤ 2.4 cap (run 2's scale-4.0 one was 72 wide); rock_l 66-75 wide.
- The shots read varied: green-capped piles next to bare rocks.

## 10. Felt
- Material Plastic on all 18 (chk20 ok).
- `felt_grain_v20` (close-up, pad 5): median (91,172,88), std 1.40 / 1.31 / 1.01. Same subtle grain as run 2.

| Pad (tee, 680,650) | v20 | Run 2 |
|---|---|---|
| 5 | (106,185,99) | (106,186,100) |
| 15 | (105,185,99) | (106,185,100) |
| **16** (Soft 0.15) | **(90,169,86)** | (125,200,110) at 0.5 |
| 17 | (106,185,99) | (106,186,100) |
| 18 | (105,185,99) | (105,185,99) |
| 12 | (178,224,119) | (178,225,120): BackFill_Pad12 3/55 warm pool, unchanged |
| 10 | (113,190,101) | (114,190,101) |

- Pads 5/15/17/18 match. Pad 16 now reads about 15 **darker**, everywhere in the frame (far end (77,152,79)). Run 2's 0.15 test gave (112,191,107), so the difference is new shade on the felt (the restored pad 16 ruin_arch and boulders stand right beside it), not the light. Left at 0.15 (generator value). The generator may want about 0.3 for pad 16 now.

## 11. Sun
No change: ClockTime 12, latitude 80 (chk20).

## 12. Screens (`~/stage/shots14/`, 1360×877, `_v20` overwritten)
- **Fronts / backs:** `pad_1..18_v20`, `pad_1..18_back_v20`
- **Overviews:** `overview_v20`, `overview_paths_v20` (annotated), `overview_paths_a/b/c/d_v20` (annotated) and `_raw_v20c`
- **Trail views:** `pad_{1,2,4,5,6,7,8,9,10,11,14}_trail_v20`. Run 2's stale `pad_{12,13,15,18}_trail_v20` were moved to `shots14_v20b_run2/*_stale.png`, not retaken (those pads pass).
- **Run-1 list:** `jungle_v20` (new camera on the 12→13 trail, outside any arch), `torch_closeup_v20`, `torch_check_pad5_v20`, `hut_closeup_v20`, `hut_posts_lightsoff_v20`, `lantern_v20`, `panel_pad6/13/18_v20`, `cliff_pad18_v20`, `hump_pad17_v20`, `ruinwall_v20`
- **Trail / clearings:** `path_leg_v20`, `hub_v20`, `apron_v20`, `arch_clearing_v20` (pad 16 arch) + `arch_clearing_a_v20c`, `arch_clearing_b_v20c`, `arch_clearing_c_alt_v20c`, `cave_clearing_v20`, `stepstone_v20`
- **Felt / boulders:** `felt_grain_v20`, `boulders_pad16/17/18_v20`
- **Evidence:** `atm_{overview,oblique,pad5,pad17,cliff18}_{before,after}_v20c`, `hut_c*_v20c`, `hutexp_*_v20c`, `pre_v20c`

**Shot hygiene:**
- Every image was looked at, individually or on a sheet.
- **halo.py = 0 on every shot.**
- Cursor swept and parked by shoot.sh for each shot.
- Camera back to Custom FOV 70 after every batch.
- **LocalTransparencyModifier nonzero 0.**

**Sheets** (`tools16/sheet.py`, `shots14/sheets_v20/`): `fronts_1_9`, `fronts_10_18`, `backs_1_9`, `backs_10_18`, `trail`, `misc` (boulders, torches, panels, cliff, hump, ruin wall, jungle), `misc2` (overviews, paths, hub, apron, arches, cave, stones, grain), `misc3` (hut, lantern, dark wood, atmosphere A/B).

## 13. Final checks and publish
**Pre-publish:**
- chk20 as in §2 (lantern scope deviation only)
- `chk20c_lant` hut lanterns 7/7 ok
- sig16b `13e15e2d` ×2
- terr16b green
- HttpEnabled false

**BuildInfo:**
- `tools/stamp`: sha c2339cd85aaef0bc7036f905cf09a68bd5c67785 == HEAD, dirty false
- Rojo synced it: stampedAt 2026-11-01T15:43:12Z read back in `ReplicatedStorage.Shared.BuildInfo`

**Save / Publish:** File menu items clicked via System Events on pid 65929, frontmost verified before each.
- Save: `Saved new changes in "Pirate Shipwreck" to Roblox.` at 15:43:36.736Z
- **Publish:** `→ Add publish notes to v20`, `Published new changes in "Pirate Shipwreck" to Roblox.` at **15:43:57.175Z (07:43:57 AM PST)**
- `→ View error reports` also prints on every publish (v19's log has it too).

**Reopen:**
- File > Close Place, no prompt (Start page). Then `open roblox-studio:1+launchmode:edit+task:EditPlace+placeId:131316561222931+universeId:10771778371`.
- New pid 5180, log `0.745.0.7451137_20261101T154432Z_Studio_032dc_last.log`: **`...id=131316561222931&version=20`**. Marker `V20C_REOPEN_MARKER_9034` in that log.

**Reopened checks:** chk20 / chk20c_lant / sig16b ×2 / terr16b output diffed against pre-publish: **IDENTICAL** (sig 13e15e2d).
- SoftPadLights read back: 15 / 17 off, 16 at 0.15.
- BuildInfo sha c2339cd, dirty false.
- HttpEnabled false; camera Custom FOV 70.

**Deploys row:**
- `~/src/vr-mini-golf-v2` commit **235dfad `docs: add v20 deploys row`** (not pushed), after the v19 row.
- Re-stamped afterwards (BuildInfo sha 235dfad, gitignored). If Rojo syncs it into the reopened session, that change is unsaved and unpublished, as in v19.

Creator Hub Version History was not checked in a browser; the version comes from the Studio log ("v20") and the reopen loading `version=20`.

## Values / notes for the generator
1. **chk20 lantern rule:** scope it to hut lanterns (within HUT_LANTERN_DIST of a hut_leanto), or decide the ruin_arch lantern values (now 4/18, no shadows).
2. **Haze 0.5:** re-creates the grey band (131,138,155) over the sea. Haze 0 removed it in v19.
3. **Hut lanterns 0.4 / 6:** the thatch reads lights-off (87,64,24). The posts need a lighter, less red texel (G/R ~0.8, e.g. (130,108,85)); (80,50,30) makes it worse.
4. **Pad 16 felt:** about 15 darker than the others at Soft 0.15 now that the arch shades it. Try ~0.3.
5. **Pad 16 ruin_arch** (101.8,-478.8) is edge-on to the trail. Rotate it 90° to straddle the trail like the other two.
6. **Tee views still failing: 1, 2, 4, 5** (weak 7, 8, 9, 11). Widen or lower the Edge hedge further on the trail side, or add a visible marker (torch / post) at each outgoing leg.
7. **Leg 17→18 width 7.0** is below spec; widen it. Overhead, 11→14 and pad 14's start stay weak (pad 14 at 6 %).
8. 2 leafclump@Edge on the trail by pad 8: (883.3,131.0), (878.8,127.5).
9. Hub sand (242,203,136) with BackFill_Pad11 1.5/40 is still about +16 over target; ~1.0 would be closer.

## Problems / not done
- chk20 RED on its lantern rule only (explained above). Published on that judgment.
- Pass bars not met: hut thatch / posts; tee-view trail on pads 1, 2, 4, 5; overhead trail fully end to end (11→14 faint).
- Haze band visible (not changed, per brief).
- **Not done:**
  - no Brightness / Range change on the lanterns
  - no texture upload; dark-wood test reverted
  - no atmosphere / Bloom / sun changes
  - no deletions, no MaterialVariant, no Script edits, no public setting, no Robux, no push
- **Studio state:**
  - pid 5180 open on the published v20 place, MCP connected
  - pid 65929 left at the Start page (place closed)
  - pids 18508, 30033, 34084, 61461, 62563, 78191, 93578 untouched
  - :8765 and :8767 still up
- New files only in `~/stage/v20cs/`, `~/stage/v20c_diag/`, `/tmp/v20c/` and `shots14_v20b_run2/` (backup); nothing in the generator files changed.

DONE_V20C
