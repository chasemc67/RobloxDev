# Pirate Shipwreck v20 PREP report

**Result: prep done. Place UNSAVED, NOT PUBLISHED, version still 19.**
- No Save to Roblox, no File > Publish, no version bump. Every v20 edit exists only in the open place in memory (pid 65929). Studio is left open on that modified, unsaved place, HttpEnabled false.
- The place stays private. Nothing was spent, Team Create stays off, no Scripts were written through MCP, and no assets or Blockout parts were deleted.
- Pid 18508 was not touched. Every GUI input went to pid 65929, and the frontmost pid was checked before each one (`/tmp/v20/act.sh`).
- No Screen Recording prompt appeared.

**Headline findings:**
1. **Lanterns:** brightness alone can't reach the thatch target. The best brightness is **1.2** (thatch R on target, G/B low). The light *colour* (255,170,90) is the real lever: at **colour (255,235,200) + brightness 1.2** the thatch reads (207,167,66).
2. **Hut posts:** the orange is lighting, not the mesh or texture. The posts sample wood (110,70,40) and, with the lights off, render neutral-dark. The pad 5 rim torch light (range 14) reaches the right post.
3. **Pad 1 torch:** still buried in the wreck deck plate at any u from 21 to 24. The fix is **Y = FeltTopY + 5.9**, not u.
4. **Pad 17 felt:** the cause is two extra **SoftPadLight** PointLights on pads 15, 16 and 17 (brightness 1.4, range 30). Disabling them makes pad 17 render exactly like pads 5/18.
5. **Paths:** they read well at walking level but are hard to see from overhead under the canopy. Rendered Sand is about (168,147,118) in sun and (89,83,76) in shade.

## 1. Preflight and baseline
**Studio and MCP:**
- The MCP lists one named studio, "Pirate Shipwreck (placeId 131316561222931)". Marker `V20_MARKER_4417` is in `~/Library/Logs/Roblox/0.745.0.7451137_20261101T132308Z_Studio_c0bae_last.log`. That is pid 65929's log, which loaded `...&version=19`.
- The log has no earlier LT20D/MATPATCH lines, so this was a clean start.
- No other Studio job was running. `v20_claude.log` / `run_v20.sh` are this run.

**Docks and viewport:**
- The reopen had brought back Terrain Editor, Toolbox, Explorer, Properties, Autopilot, Rojo and Asset Manager. I closed them one at a time with a screen check after each.
- The viewport is full width again, so vp14.env (280,166,1360,877) is unchanged.
- The Rojo dock showed "connected, synced 18 minutes ago". BuildInfo sha in the place is **c2339cd** (the v19 post-publish re-stamp), dirty false.

**Helpers:**
- `/tmp/v19/*` were hard-wired to pid 61461. I copied them to `/tmp/v20/` with pid 65929.
- I stopped the v19 :8767 shot server (pid 91202) and started `/tmp/v20/shotsrv.py` (pid 96516, still up). :8765 (pid 9525) is still up.

**Baseline (chk16 + hut16 + sig16b + terr16b on the open v19 place) matched v19 exactly:**
- torches 14, all bad counts 0
- meshparts 3330, instances 3955, pointlights 74
- bright 1.60, exp -0.30, haze 0, Bloom 1.1/0.35, ColorCorrection sat 0 / contrast 0.05
- felt 18 at (87,147,79): chk16 flags 18 against the old (120,190,110) target, as expected
- footprints 5/0, huts 4/0 on the kit_v2_4 ids, cliff tex 104642093288682, ruin_wall 99217150386445 / 125403212114636
- **sig16b fb63b14e (3619 / 3704)**, terr16b green
- The 2 v19-hidden canopy_walls were present and hidden.
- Baseline chk20 was RED only on `torch core bad 0` (v19 cores are (255,220,150)).

**BEFORE samples** (px.py 9x9 median):
- hut (cam_hut): thatch (251,201,53) / (238,171,40); posts (213,92,21) / (233,137,35); deck (111,54,31)
- felt at (680,650): pad 5 (105,186,103), pad 17 (151,218,128), pad 18 (105,186,103)

## 2. ltdr20 rebuild
**Placer log:**
- `DR torches 14`, `DR hut lanterns lowered 8 (brightness 1.5)`, `DR kit_v2 point lights 28`
- `DR placed 3222` (v19 3253, so **-31**), `DR DONE instances 3673`, `LT20D run ok=true nil http=false`

**chk20 after ltdr20: ALL EXPECTED GREEN** (no deviations):
- core (255,200,130) bad 0
- meshparts **3299** (v19 3330: -31 = 29 path vegetation + 2 canopy_walls), instances 3924, pointlights 74
- lantern_hanging lights: 1.50/18 x8 (near huts), 4.00/18 x3
- The two v19-hidden canopy_walls are no longer generated: no hidden canopy_wall remains, and nothing was deleted by hand.

**Determinism:**
- **sig16b 99d54b7b (rows 3588, desc 3673)** after run 1, **and 99d54b7b again after a second ltdr20 run**.
- terr16b green before matpatch: hump voxels Air / LeafyGrass 0.26 / Air; Rock region 286 Rock / 0 LeafyGrass; cliff (115,100,92).

## 3. Hut lantern tuning
**Lights:**
- The 8 in-range lights are `Set2.lantern_hanging.kit_lantern_hanging_Glow.LightAttach.PointLight`, 17.8 studs (xz) from each of the 4 huts, Range 18, Color (255,170,90).
- Iterations (cam_hut; the brief's thatch point (600,200) plus the others):

| Lantern light | Thatch (600,200) | Thatch (750,280) | Post (960,560) | Post (330,500) | Deck (640,700) | Thatch error vs (200,165,90) |
|---|---|---|---|---|---|---|
| 4.0 (v19 / BEFORE) | (251,201,53) | (238,171,40) | (213,92,21) | (233,137,35) | (111,54,31) | +51/+36/-37 |
| 1.5 (generator v20) | (218,144,35) | (192,116,28) | (164,56,16) | (183,87,27) | (95,50,30) | +18/-21/-55 |
| **1.2 (final, applied)** | **(207,132,32)** | (179,105,25) | (153,51,15) | (169,79,25) | (92,49,30) | **+7/-33/-58** |
| 1.0 | (197,122,31) | (169,99,25) | (145,48,15) | (159,75,25) | (91,49,30) | -3/-43/-59 |
| 0.8 | (186,114,29) | (158,92,24) | (138,45,15) | (147,68,24) | (89,49,30) | -14/-51/-61 |
| off (floor) | (89,62,23) | (78,57,19) | (94,30,13) | (70,43,21) | (84,47,30) | |
| 1.2 + Color (255,220,170) *test* | (207,160,56) | (179,130,41) | (153,65,21) | (169,99,36) | (92,51,31) | +7/-5/-34 |
| **1.2 + Color (255,235,200) *test*** | **(207,167,66)** | (179,138,49) | (153,69,25) | (169,105,41) | (92,51,31) | **+7/+2/-24** |

**FINAL in Studio: Brightness 1.2, Range 18, Color (255,170,90) unchanged, on the 8 in-range lights.**
- **Report for the generator: `HUT_LANTERN_BRIGHT = 1.2`** (distance 26 is fine; Range unchanged at 18).
- Brightness only moves R/G along the orange light colour: B gains about 8 per unit of brightness, so G and B can't reach target with brightness alone.
- **Proposal (not applied):** set the in-range lantern PointLight `Color` to **(255,235,200)** at brightness 1.2. That lands the thatch within 7 / 2 / 24 of target (`hut_b120_c255235200_v20.png`).
- The colour was restored to (255,170,90) after each test, so the place matches what the generator writes with only the brightness constant changed.

**Glass:** stays Neon and still glows clearly.
- Glass median: (247,193,87) at 1.5; **(242,185,83) at 1.2**; (242,211,123) with the whiter colour.
- Shots: `lantern_v20.png` (final), `lantern_b150_v20.png`, `lantern_b120_c255235200_v20.png`.

**Texture cells:** EditableMesh raycast of the cam_hut pixels on the pad 5 hut mesh (UV top-origin, 8x8 palette):
- thatch (600,200)/(750,280) sample **cell r5c1 = (166,134,74)**, the darker straw, not (200,165,90) (r5c0)
- posts (960,560)/(960,640) sample **r4c1 = (110,70,40)**; (960,480)/(330,500) sample **r4c2 = (140,95,55)**
- deck (640,700) samples r4c1
- the dark wood **(80,50,30) is r7c6**, used by 96 faces elsewhere on the mesh

## 3b. Hut posts: lights-off
`hut_posts_lightsoff_v20.png` (8 lantern lights Enabled=false, then restored 8/8; verified):

| Post point | Lights off | Restored (1.2) |
|---|---|---|
| (960,560) | (94,30,13), G/R 0.32 | (153,51,15), G/R 0.33 |
| (330,500) | (70,43,21), G/R 0.61 | (169,79,25), G/R 0.47 |

The posts still read orange/red with the lanterns off, so I ran the one-hut experiment.

**One-hut experiment** (pad 5 hut only). This was an in-memory EditableImage copy of 108289367129276 with cells r4c1 + r4c2 recoloured, applied through `TextureContent`. No upload was made.
- Afterwards TextureID was restored to rbxassetid://108289367129276 and verified on all 4 huts (bad 0).

| Variant | Right post (960,560) | Left post (330,500) |
|---|---|---|
| Dark wood (80,50,30), lights on | (104,28,9) | (84,25,9) |
| Dark wood, lanterns off | (56,15,7) | (25,12,8) |
| Dark wood, lanterns + Torch_Pad05 off | (26,13,7) | (25,12,8) |
| Grey (128,128,128) diagnostic, lights on | (177,127,102) | (155,119,100) |
| Grey, lanterns off | **(116,82,88)** | (60,70,86) |
| Grey, lanterns + Torch_Pad05 off | **(61,71,87)** | (60,70,86) |
| Original texture, lanterns + Torch_Pad05 off (`hut_alloff_v20.png`) | **(47,24,13)** | (70,43,21) |

**Verdict: not a mesh or texture issue. Do not send this to 3D Model Bot.**
- With all warm lights off, a neutral grey texel renders neutral-cool (61,71,87), and the original wood renders dark brown (47,24,13). That is the same as v19's (47,23,12).
- The orange comes from:
  1. the lantern 6.4 studs from the right post
  2. the **pad 5 rim torch light** (Torch_Pad05, (240,110,30), brightness 1.5, range 14, about 16 studs from the post). It adds about +47 R to the right post even with the lanterns off.
- Swapping the posts to dark wood (80,50,30) only makes them a darker red under the same lights (104,28,9).
- **What would fix it:** the whiter lantern colour above, plus keeping Torch_Pad05's light off the hut (move the torch, or range ≤ 12).
- Asset ids for reference: hut mesh 131857226019693, texture 108289367129276. The posts use palette cells r4c1/r4c2.
- Experiment shots: `hutexp_*_v20.png`, `hut_alloff_v20.png`, `hut_off_v20.png`.

## 4. Torch snap (torch20.luau = torch19 retitled; read-only)

| Pad | Base (x,y,z) | u | v | Terrain Y | Gap | Nearest pad part |
|---|---|---|---|---|---|---|
| 1 | (-507.9,27.5,225.1) | **21.0** | -2 | none (sea, 0.00) | n/a (on wreck) | RimE 2.0 |
| 4 | (173.4,8.4,373.0) | -24.0 | -2 | 8.47 | **-0.10** | Base 5.0 |
| 5 | (446.7,10.4,406.1) | -24.0 | -2 | 10.46 | **-0.10** | Base 5.0 |
| 6 | (735.4,8.4,391.8) | 24.0 | -2 | 8.47 | **-0.10** | Base 5.0 |
| 8 | (893.5,10.4,156.2) | 24.0 | -10 | 10.47 | **-0.10** | Base 5.0 |
| 10 | (398.8,12.8,184.2) | 24.0 | -2 | 12.95 | **-0.10** | Base 5.0 |
| 12 | (-132.4,19.9,-70.9) | 24.0 | -2 | 19.96 | **-0.10** | Base 5.0 |
| 15 | (-355.7,43.8,-526.6) | -24.0 | -2 | 43.94 | **-0.10** | Base 5.0 |
| 17 | (394.2,75.9,-373.6) | 24.0 | -2 | 75.96 | **-0.10** | Base 5.0 |
| 18 | (567.6,98.3,-499.6) | 24.0 | -2 | 98.39 | **-0.10** | RimE 6.3 |

- **Pads 4-18 all meet |gap| < 0.3.** Pad 18 is no longer buried (it was 3.9 in v19); it now stands upright on the slope in `pad_18_v20.png`.

**Pad 1 vs the wreck hull** (`World.Meshes.WreckV2.wreck_hull`, CanQuery false, so tested with an EditableMesh raycast, read-only):
- Vertical hull crossings at the torch xz:

  | u | Deck plate top / bottom |
  |---|---|
  | 16 | 31.85 / 30.33 |
  | 21 | **33.02 / 31.50** |
  | 22 | 33.29 / 31.77 |
  | 23 | 33.55 / 32.03 |
  | 24 | 33.82 / 32.30 |
  | 26 | 41.81 (bulwark) |

- The torch base is at y 27.5 (FeltTopY 27 + 0.5), so **the lower about 5.5 studs of the post are inside the deck plate at every u from 21 to 24.** The horizontal clearance from the post to the hull is 0.0 at u 21.
- Shots `torch_pad1_u21/u22/u23_v20.png`: only the bowl and flame show above the deck at all three.
- **u is not the fix.** A test lift of u 21 onto the deck (base y 32.92, i.e. +5.42) stands the whole post on the deck: `torch_pad1_u21_decksnap_v20.png`, `pad_1_decksnap_test_v20.png`. Reverted afterwards; pivot back at (-507.90,33.07,225.05).
- **Report for the generator:**
  - keep **pad 1 u = 21**
  - set **base Y = FeltTopY + 5.9** (deck top 33.02 - 0.1)
  - **do not** ground-ray the hull: with Default collision fidelity a physics ray returns y 44.7-45.2 (about 11.7 too high)

## 5. Paths (matpatch20)
**Run:**
- terr16b was green on heights first. `MATPATCH20 chunks 35 cellsPainted 4016 cellsSkipped 17` (4033 cells: 1108 Sand, 2925 LeafyGrass).
- terr16b after: identical (hump Air/0.26/Air, Rock 286 / LeafyGrass 0, cliff unchanged).

**Material histogram** over the patch area (x -616..616, z -572..244, solid 4-stud voxels; `terrhist20.luau`):

| Material | Before | After |
|---|---|---|
| Ground | 11,955 | **0** |
| LeafyGrass | 143,983 | 152,744 (+8,761) |
| Sand | 9,504 | 12,773 (+3,269) |
| Grass | 7,899 | 7,824 (-75) |
| Rock / Slate / Water | 880,950 / 2,513 / 1,345 | unchanged |

Totals are identical (1,058,149), so there is no occupancy change.

**Hub:** used as given, (28.7, -58.1), between pads 11 and 12. The patch has 42 Sand cells within r 17 (about 44 expected for r 15). Ground there is y 13.5.

**Coverage:** the Sand network joins 10→11→hub→12→13→14→15→16→17→18, plus a short strip by pads 1/2 (z 216-240).
- **Pads 3-9 have no new path** (the patch stops at x 616). Their back views already show the existing beach sand trails.

**Rendered Sand** (automatic Sand-pixel classification, medians):
- **sunlit (166,144,115) on leg 13→14, (170,149,120) at the hub**
- **shaded (88,81,74) / (90,84,77)**
- So it renders darker and less saturated than the (226,184,128) base. Under the canopy it reads grey-tan.
- Before the patch the same leg 13→14 points were dark dirt (32-36,31-35,25-27).

**Edges:** they blend. The x-scan across the leg 2 path edge at y 700 goes (89,82,77) → (67,70,60) → (57,60,50) → (30,51,28) over about 120 px, with no hard line.

**Vegetation on the path:** exported all 1635 visible Dressing MeshParts in the area and tested their base x,z against the 1108 Sand cells.
- **No leafclump, fern, palm or rock base stands on a Sand cell.**
- The only items on Sand are 30 `vine_arch` (the arches straddle the trail by design; their legs stand at the sides).
- Within 4 studs of the path edge: 10 rock_s, 7 fernclump, 5 vine_arch, 1 canopy_wall, 1 boulder_pile.
- The boardwalk planks and stepping stones (Parts) sit on the path by design.
- No floating items were seen in the walking views.

**Problems:**
1. **The trail is not obvious from overhead.**
   - `overview_paths_v20.png` (full course, straight down from y 830, FOV 70, north up) and `overview_paths_9_13_v20.png` (y 560) show the 4-10 stud strips only faintly: about 3-6 px wide at that scale, and mostly under palms, vine-arch rows and leafclumps.
   - The old brown Ground lanes are now green, so from above the corridor reads *less* than in v19.
   - A Walkabout-style overhead read would need wider paths (≥ 12 studs) and/or a canopy gap along the trail.
2. **The hub sits under dense canopy.** Every overhead or high pose ended inside foliage (`hub_before_v20.png`, `hub12/11_before_v20.png`). `hub_v20.png` uses an eye-level pose from the north (28.7,23.9,-88.1), picked by an occlusion search: it shows the Sand clearing with the boardwalk plank between vine arches.
3. **Pad 14 back:** the trail start reads as a dark Rock/Slate patch with tall grass over the boardwalk end (`pad_14_back_v20.png`). REPAINT skips Rock/Slate voxels, so the path can't paint there.
4. **Jungle floor greener:** yes, Ground → LeafyGrass makes the floor around the paths greener than v19, and LeafyGrass carries terrain grass blades up to the path edges (`jungle_v20.png`, `pad_12_back_v20.png` vs v19). At walking level that reads fine and the Sand strip stands out against it. It doesn't look wrong.
5. **Path width:** narrow in places (leg 11→hub, `path_leg_v20.png`), wider on leg 13→14 (`path_leg2_v20.png`).

## 6. Pad 17 felt vs pads 5 and 18
**Measurements:**

| | Pad 5 | Pad 17 | Pad 18 |
|---|---|---|---|
| Tee view (cam_tf, 680,650) | (105,186,103) | **(151,218,128)** | (105,186,103) |
| Same felt-relative pose (felt-local (0,6,24) → centre; 680,600) | (82,162,84) | **(152,219,126)** | (105,185,101) |

Relative pose for the other soft-light pads: pad 15 (152,218,126), pad 16 (152,218,126).

**Causes checked:**
- **(a) Orientation:** Felt UpVector = (0,1,0) on all 18 pads. Nothing is tilted.
- **(b) Sun:** sun dir (0,0.552,0.834); sun·up = 0.552 on 5, 17 and 18 (identical).
- **(c) Shadows:** with only the soft lights toggled, pad 17 drops exactly to the pad 5/18 value, so shadowing is not the difference. Pad 5's relative view is a bit darker (82,162,84), from local shade at that spot; its tee view equals pad 18.
- **(d) Lights within 60 studs of each felt:**
  - **Pad 5:** LightAnchor1/2 PointLight 1.0 / r16 / (255,245,225) at 8.0; 2 lantern lights 1.2 / r18 at 19.3 and 24.3; Torch_Pad05 1.5 / r14 at 12.4.
  - **Pad 17:** LightAnchor1/2 1.0 / r16 at 8.0; **SoftLightAnchor1/2 `SoftPadLight` PointLight 1.4 / r30 / (255,225,190) at 14.0** (at (379.5,90.5,-350.5) and (409.5,90.5,-348.5), 14 above the felt); Torch_Pad17 1.5 / r14 at 11.6.
  - **Pad 18:** LightAnchor1/2 1.0 / r16 at 8.0; Torch_CaveMouth 1.5 / r14 at 16.4; Torch_Pad18 1.5 / r14 at 16.2.
  - SoftPadLights exist on **pads 15, 16 and 17 only** (Blockout parts, attribute Blockout=true; not generated by the Dressing placer).
- **(e) Material:** all SmoothPlastic, Reflectance 0, Color (87,147,79), Transparency 0, plain Part with no children. No difference.

**Proof by toggle** (restored 6/6 enabled):

| Pad 17 | Tee view | Relative view |
|---|---|---|
| SoftPadLights off | **(105,186,103)**, identical to pads 5/18 | (104,185,100) vs pad 18 (105,185,101) |

| Pad | Tee view, soft on | Tee view, soft off |
|---|---|---|
| 15 | (151,218,128) | **(105,186,103)** |
| 16 | (138,208,116) | (84,163,88) |

Shots: `felt_*_v20.png`, `felt_rel_*_v20.png`, `*_softoff_v20.png`, `pad_17_softoff_test_v20.png`.

**PROPOSED FIX (not baked):**
- Remove or disable the `SoftPadLight` PointLights on Pads 15-17 in the course builder (Blockout). Then all pads render the one felt Color equally.
  - Pads 15 and 17 then match 5/18 exactly.
  - Pad 16 lands about 20 darker, (84,163,88); a pad 16-only SoftPadLight at about 0.5 brightness would even it out.
- Alternative if the soft lights must stay: drop SoftPadLight brightness to about 0.3, or give pads 15-17 a felt Color factor of about 0.70/0.85/0.81. Not tested.

`pad_17_softoff_test_v20.png` shows pad 17 with the soft lights off: it looks natural.

## 7. Screens (`~/stage/shots14/`, 1360x877 viewport only)
Every image was looked at (contact sheets plus close views). Hover-outline (halo.py) is 0 on every shot. The cursor was swept and parked by shoot.sh. The camera was restored to Custom FOV 70 after every batch. LocalTransparencyModifier nonzero 0.
- **Fronts and backs:** `pad_1_v20.png` … `pad_18_v20.png` and `pad_1_back_v20.png` … `pad_18_back_v20.png` (same cam_tf / cam_bf cameras as v19)
- **v19 set:** `overview_v20.png` (cam_ov12), `jungle_v20.png` (cam_j12), `torch_closeup_v20.png` (cam_tcu), `torch_check_pad5_v20.png` (cam_tgt5d), `hut_closeup_v20.png`, `hut_posts_lightsoff_v20.png`, `lantern_v20.png` (new cam_lantern), `panel_pad6/13/18_v20.png`, `cliff_pad18_v20.png`, `hump_pad17_v20.png`, `ruinwall_v20.png`
- **New:**
  - `overview_paths_v20.png` (cam_ovp, straight down), `overview_paths_9_13_v20.png` (cam_ovp913)
  - `path_leg_v20.png` (cam_leg1, 11→hub) and `path_leg2_v20.png` (cam_leg2, 13→14)
  - `hub_v20.png` (cam_hubA), `hubB_v20.png` (cam_hubB, high, mostly canopy)
- **Before/evidence:**
  - `hut_before_v20`, `felt_pad5/17/18_before_v20`, `overview_paths(_9_13)_before_v20`, `path_leg(2)_before_v20`, `hub*_before_v20`
  - `hut_b150/b120/b100/b080/b120_c*_v20`, `hut_off_v20`, `hut_alloff_v20`, `hut_posts_lightson_v20`, `hutexp_*_v20`, `lantern_b*_v20`
  - `torch_pad1_*_v20`, `pad_1_decksnap_test_v20`
- **Contact sheets** (tools16/sheet.py): `shots14/sheets_v20/fronts_1_9_v20.png`, `fronts_10_18_v20.png`, `backs_1_9_v20.png`, `backs_10_18_v20.png`, `misc_v20.png`, `misc2_v20.png` (paths/hub are on misc2)

## 8. Final checks (unsaved place)
**chk20: CHK20 ALL EXPECTED GREEN.** Every EXPECT line is ok; no deviations.
- torches 14, flame / core / light / emitter bad 0
- flame (240,110,30), light 1.5, other Neon 0, grey 0
- meshparts 3299, instances 3924, pointlights 74, templates 34, no stray kit_
- clock 12, lat 80, bright 1.60, exp -0.30
- Atmosphere: dens 0.040, offset 0.05, haze 0, glare 0.40; Color (255,235,210), Decay (190,150,110)
- ColorCorrection sat 0 / contrast 0.05 / tint white; Bloom 1.1 / 0.35
- felt 18 / 0 bad at (87,147,79); footprints 5 / 0
- wreck_glow and cave_glow SmoothPlastic; backfill 3; huts 4 / 0
- lantern_hanging lights **1.20/18 x8 | 4.00/18 x3**
- sha c2339cd, dirty false; streaming true; sun elevation 33.5; http false

**terr16b:** green and unchanged.

**sig16b: fa9577e3** (rows 3588, desc 3673).
- This differs from the ltdr20 hash only by the 8 tuned lantern brightnesses: sig16b hashes PointLight brightness.
- Proof: setting those 8 back to 1.5 gives **99d54b7b** (the twice-stable ltdr20 hash); back at 1.2 it gives fa9577e3 again.
- **Once the generator writes `HUT_LANTERN_BRIGHT = 1.2`, a fresh ltdr should hash fa9577e3.**

**Restore audit:**
- LocalTransparencyModifier nonzero 0
- hut textures all 108289367129276
- all 14 torch lights and all 6 SoftPadLights enabled, 0 disabled lights in workspace
- Torch_Pad01 at the generator position
- wreck_hull CanQuery false (restored)
- cliff tex 104642093288682
- no V19_/V20_ test objects
- camera Custom FOV 70, HttpEnabled false
- (The Studio MCP assistant itself resets the camera type to Fixed after every execute_luau call; that is why a fresh read shows `Fixed`, as noted since v17b.)

**Not done, per the brief:** no Save, no Publish, no version bump, no Version History check, no deploys row, no `tools/stamp`.

## 9. What is in the open place vs v19 (all unsaved)
1. ltdr20 Dressing:
   - generator lantern 1.5, then **tuned to 1.2 by hand** on the 8 in-range lights
   - torch core (255,200,130)
   - snapped rim torches
   - 2 canopy_walls and 29 path items no longer generated
2. matpatch20 terrain materials (paths, hub, Ground lane → LeafyGrass).

Everything else (lighting, felt, haze, hut, ruin_wall, cliff) is unchanged from v19. All experiments were reverted.

## Values for the generator
- **`HUT_LANTERN_BRIGHT = 1.2`** (range 18, distance 26 unchanged). Proposed extra: lantern light Color **(255,235,200)** near huts.
- **Pad 1 rim torch: u = 21, base Y = FeltTopY + 5.9** (stand on the wreck deck plate). No hull raycast (collision fidelity is too coarse).
- **Felt:** remove/disable the Pads 15-17 `SoftPadLight` lights (Blockout/course builder).
- **Hut posts:** keep the pad 5 rim torch light off the hut (move it, or range ≤ 12). No mesh change needed.
- **Paths:**
  - widen them for an overhead read and/or open the canopy along the trail
  - allow the path to paint over Rock/Slate at the pad 14 → 15 start
  - add front-nine paths if wanted (the patch stops at x 616)

## Problems / follow-ups
1. The thatch target can't be met with brightness alone (G/B low by about 33/58 at 1.2). It needs the colour change above.
2. The pad 1 torch is still buried in the deck in the open place (generator position kept); it needs the Y offset.
3. The paths are weak from overhead and the hub is canopy-covered (see §5).
4. The pad 16 felt is a bit dark if the soft lights are removed (84,163,88).
5. **Studio state:**
   - pid 65929 is open on the **unsaved** v20-prep place: MCP on it, docks closed, Rojo still connected in the background.
   - Pids 61461, 34084, 93578, 30033, 62563 and 78191 are as before. 18508 untouched.
   - :8765 (pid 9525) and the :8767 v20 shot helper (/tmp/v20/shotsrv.py, pid 96516) are still up.
6. **New files in ~/stage:**
   - `torch20.luau`, `terrhist20.luau`
   - `cam_lantern`, `cam_t1side`, `cam_ovp`, `cam_ovp913`, `cam_leg1`, `cam_leg2`, `cam_hub`, `cam_hub11`, `cam_hub12`, `cam_hubA`, `cam_hubB`, `cam_rel5/15/16/17/18`
   - batch files in `~/stage/v20s/`
   - helpers in `/tmp/v20/`

**Place UNSAVED, NOT PUBLISHED, version still 19.**

DONE_V20
