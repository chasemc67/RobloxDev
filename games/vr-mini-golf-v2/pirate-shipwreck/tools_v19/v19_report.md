# Pirate Shipwreck v19 report

**Result: published, version 19.**
- The place stays private. Nothing was spent, Team Create stays off, no Scripts were written through MCP, and nothing was deleted (the two canopy_walls were hidden, not deleted).
- Pid 18508 was not touched. Every GUI input went to pid 61461, and the frontmost pid was checked before each one.
- **v19 = v18 + lighting (Brightness 1.6 / neutral ambient) + eye cap on Skyline and ground plants + torches off the rail + smoothed ruin_wall (kit_v2_6_1) + felt (87,147,79) + Atmosphere Haze 0.**

**Main findings:**
1. **The hut is hot because of its own lanterns.** With the two hanging-lantern PointLights off for one frame, the thatch renders (87,63,23), not (251,201,48).
2. **The plain (115,100,92) calibration renders brighter and bluer than the (125,108,98) target.** Lighting was not tuned further.
3. **The new torch positions have ground-fit problems** on pads 1 and 18 (see 2b).

## 0. Starting state (an earlier attempt had run)
An earlier v19 attempt ran from 12:30 to 12:35Z, and its transcript is lost. The Studio log shows what it did:
- It ran ltdr19 twice (hash 0b65b81d) and applied light19 at 12:33:46Z.
- It left `cave_cliff_lower.TextureID` **blank**. A 12:37Z restart restored it (104642093288682).
- No test Part was left behind.
- `dressing_v19.luau` was regenerated at 04:36 PST, after that ltdr19 run. So that rebuild did **not** have the new torch positions; my ltdr19 runs below did.

For clean before/after numbers, I temporarily put back the exact v18 lighting and took every BEFORE sample myself, then re-applied light19:
- The v18 values come from the `LIGHT19 before` log line: Brightness 2.00, Top (255,190,110), Bottom (120,112,72), Ambient (100,92,66), Outdoor (150,142,104).
- The earlier attempt's shots are kept as `*_prior.png`.

## 1. Preflight and baseline
- **MCP and servers:** MCP was on pid 61461 (marker `V19C_MARKER_6611` is in `..._20261101T122155Z_Studio_343b7_last.log`). PlaceId 131316561222931. :8765 returned 200, and the :8767 shot helper was up.
- **Viewport:** docks were closed and the viewport was full width, so the vp14.env crop held. After the import I closed the Import Queue dock again and checked the screen.
- **Baseline:** the BEFORE images under v18 lighting match the v18 shots:
  - hut: identical to `hut_closeup_v18old`
  - cliff: within 2 of `cliff_pad18_v18old`

## 2. Dressing rebuild and 2b torches
**Rebuilds:**
- ltdr19 (after the 04:36 generator) gave: `DR torches 14`, `placed 3253`, `DONE instances 3704`, hash **65896dc8**.
- After the ruin_wall import, two more runs:
  - run 1: `DR converted templates: ruin_wall`
  - **both runs: hash fb63b14e, identical (deterministic)**
- sig16b: 3619 rows (was 3622) and 3704 descendants (was 3707).

**Counts vs v18:**
- meshparts 3330 (was 3333), instances 3955 (was 3958): **3 fewer**.
- Unchanged: huts, cliffs, terrain edits, back lights (Pad10 40/1.5, Pads 11/12 55/3), footprints (5 / 0), wreck/cave glow SmoothPlastic, torches 14 (all bad counts 0).

**2b. Rim torch read-back** (base = bounding-box bottom; u/v in the felt frame; rim outer edge at |u| 19):

| Pad | Base (x,y,z) | u | v | Clearance to rim | Base vs ray-hit terrain | Result |
|---|---|---|---|---|---|---|
| 1 | (-507.1,27.5,222.2) | 24.0 | -2 | 5.0 | no terrain (sea level) | **post sunk into the wreck hull side**; only bowl + flame show above the bulwark (`torchside_pad1c_v19.png`) |
| 4 | (173.4,9.5,373.0) | -24.0 | -2 | 5.0 | +1.03 | ~1 stud above terrain (Y = FeltTop+0.5, no terrain snap); base hidden in plants |
| 5 | (446.7,11.5,406.1) | -24.0 | -2 | 5.0 | +1.03 | same; now stands at the hut's front corner |
| 6 | (735.4,9.5,391.8) | 24.0 | -2 | 5.0 | +1.03 | same |
| 8 | (893.5,11.5,156.2) | 24.0 | -10 | 5.0 | +1.03 | same |
| 10 | (398.8,14.0,184.2) | 24.0 | -2 | 5.0 | +1.05 | same |
| 12 | (-132.4,21.0,-70.9) | 24.0 | -2 | 5.0 | +1.04 | same |
| 15 | (-355.7,45.0,-526.6) | -24.0 | -2 | 5.0 | +1.06 | same |
| 17 | (394.2,77.0,-373.6) | 24.0 | -2 | 5.0 | +1.04 | same |
| 18 | (567.6,94.5,-499.6) | 24.0 | -2 | 5.0 | **-3.89 (buried)** | base sunk 3.9 studs into the slope; only bowl + short post show (`torchside_pad18_v19.png`) |

- In v18 every torch stood at |u| 15.8 (RimE/RimW distance 0.0, i.e. on the rail). All 10 now stand at |u| 24, 5 studs clear of the rim.
- **Ground fit, more than 0.5 stud off, reported and not moved:**
  1. **All of pads 4-17:** about 1.0 above the ray-hit terrain. The placer sets rim torches at FeltTopY+0.5 with no terrain snap. Plants hide the gap in every view.
  2. **Pad 18:** buried 3.9.
  3. **Pad 1:** clips into the wreck hull.
- **Tee views:**
  - Pads 17 and 18 (`torchtee_pad17_v19.png`, `torchtee_pad18_v19.png`): the torch no longer touches the rail. It sits at the left edge of the frame, off the rim. On pad 18 it stands on the dirt slope and is partly cut off at the frame edge.
  - Pad 5 (`torchtee_pad5_v19.png`): clear of the rail, among the plants beside the hut.
- **Other contact** (bounding-box check, approximate):
  - The moved torches now stand among Edge-layer ferns, leafclumps and small rocks. pad 4 `Edge.rock_s` and pad 5 `Edge.rock_s` overlap the torch box by up to 1.8, so they may clip.
  - The pad 5 torch stands in front of the hut and now appears in the foreground of `hut_closeup_v19.png` and `torch_check_pad5_v19.png`.

## 3. Lighting
**light19 read-back (and chk16 on the reopened place):** Brightness 1.60, Top (255,245,230), Bottom (0,0,0), Ambient (110,110,115), OutdoorAmbient (135,135,140), ExposureCompensation -0.30.

Unchanged: ColorCorrection (sat 0, contrast 0.05, tint white), Bloom (threshold 1.1, intensity 0.35), Atmosphere Color/Decay, clock 12, lat 80.

**Rendered colours** (px.py 9x9 medians; same cameras; camera back to Custom FOV 70 after every batch; cursor swept; halo 0):

| Point | Before (v18 lighting) | **After (v19)** | Target |
|---|---|---|---|
| Hut thatch (600,200) | (251,201,48) | **(251,201,54)** | (200,165,90) |
| Hut thatch (750,280) | (238,171,34) | **(238,171,41)** | |
| Hut wood post (960,560) | (207,89,18) | **(206,88,20)** | (110-140,70-95,40-55) |
| Hut wood post (330,500) | (233,137,31) | **(233,136,34)** | |
| Hut deck (640,700) | (135,58,23) | **(111,53,30)** | |
| Pad 18 cliff lit (60,150) | (141,102,70) | **(106,94,92)** | |
| Cliff lit (480,280) | (144,105,71) | **(108,96,94)** | |
| Cliff mid (230,200) | (124,87,60) | **(92,80,79)** | |
| Cliff shaded (380,250) | (99,68,49) | **(72,62,63)** | |
| Cliff shaded (340,200) | (92,62,45) | **(67,58,59)** | |
| Sandy ledge top (145,304) 5x5 | (126,81,51) | **(94,77,73)** | |
| **Plain (115,100,92) test Part, sun-facing face** | (190,151,117) | **(169,145,134)** | **(125,108,98)** |
| Plain test Part, vertical face toward camera | (167,133,103) | **(150,127,115)** | |
| **cave_cliff_lower untextured (115,100,92), lit face** (60,150)/(480,280) | (169,126,87)/(171,128,88) | **(133,117,112)/(135,119,114)** | **(125,108,98)** |
| Untextured, shaded (380,250) | (131,92,65) | (101,86,84) | |
| Torch flame (median of flame pixels, torch_closeup) | (246,175,37) | (245,178,43) | |

- **Cliff:** the warm tan cast is gone. It now reads neutral grey-brown.
- **Calibration is not at target:**
  - The untextured lit cliff face renders (134,118,113): +9/+10/+15 vs (125,108,98), bluer than the target.
  - A fully sun-facing plain Part renders (169,145,134).
  - Per the brief, I did not tune the lighting beyond the specified values.
- **Calibration method:**
  - Test Part `V19_CalibPart`: 12x12x0.5, Plastic, (115,100,92), at (597.9,97.5,-492.2) in the cam_tf18 view. It was destroyed after each shot. No Part remains (checked before publish).
  - `cave_cliff_lower.TextureID` was blanked for one frame and restored. It was verified as 104642093288682 on every run and on the reopened place.
- **Hut (why it didn't move):**
  - With the two `Set2.lantern_hanging` PointLights 18 studs from the pad 5 hut disabled for one frame, the hut renders thatch **(87,63,23)** / (79,58,20) and wood (47,23,12) / (70,42,20) (`hut_diag_nolantern_v19.png`; lights re-enabled 2/2). The lights are range 18, brightness 4, colour (255,170,90).
  - **The hut's hot orange comes from its own lantern lights on the roof underside**, not from the sun or ambient. The kit_v2 lantern PointLight (brightness 4) needs to drop in the generator.
  - The hut and its grade were not touched.

### 3b. Felt
Measured at mid-felt (680,650), 9x9 median, using the pad tee cameras (cam_tf5/17/18):

| | Felt Color | Pad 5 | Pad 17 | Pad 18 |
|---|---|---|---|---|
| Before (v18 light) | (120,190,110) | (171,222,136) | (208,242,168) | (171,221,136) |
| v19 light, Color unchanged | (120,190,110) | (154,219,148) | (200,241,176) | (154,218,148) |
| Iteration 1 (3-pad mean factors .709/.841/.699) | (85,160,77) | (102,198,99) | (147,227,124) | (101,197,99) |
| **Iteration 2, final** (factors 1.028/.917/1.025) | **(87,147,79)** | **(105,186,103)** | **(151,218,127)** | **(105,185,103)** |

- **Final felt Color for the Studio-side grade script: (87,147,79)**, SmoothPlastic (Material unchanged, non-neon), on all 18 `Blockout.Pads.PadNN.Felt`.
- The 3-pad mean is now (120,196,111), essentially the target. A third iteration would not change anything.
- Pads 5 and 18 are within 12 except R (-15).
- **Pad 17 stays brighter** (151,218,127). Its felt catches more light, and one shared Color can't satisfy both. A per-pad value or a pad 17 check is needed if this matters.
- chk16's felt check now reports `notExpectedColour 18`, because its expected value is the old (120,190,110). That is the intended change.

## 4. Pads 10-12 back views
**(a0) The flat yellow fronds:**
- In v18 they were the big Skyline leafclumps (`pad_11_back_v18old.png` top left, `pad_12_back_v18old.png` top right and a yellow triangle at left).
- **In v19 they are gone.** The new cap removed or shrank them.
- **Nothing is still above eye after the cap, so nothing was hidden for this.**

**(a) Audit:** every visible Dressing MeshPart within 160 studs and the 160-degree cone of each back camera, with top above the camera eye:
- **Pad 10:**
  - only Skyline palm_l (4) and a far Skyline rock_l
  - no leaf or fern clumps
- **Pad 11:**
  - Skyline palm_l (4)
  - 3 Front.fernclump shrunk to 0.9x0.2 studs, 0.5-3.4 over eye on raised ground at 60-78 studs (invisible)
  - 1 Moss leafclump 1.5x0.5 (2.0 over)
  - Far leafclumps at 135 and 157 studs (4.9 and 10 over)
  - `Skyline.leafclump` (266.1,16.4,126.9), 69.9x24.2x64.2, 8 over eye at **139 studs** (outside the 120-stud Skyline cap)
- **Pad 12:** only Skyline palm_l (4)
- **Near the cameras:** all ground plants within 22 studs top out 1.8-3.7 below eye on all three pads.

**Remaining large mass above eye in pad 11:**
- `Workspace.World.Dressing.BackdropPersistent.canopy_wall` (185.7,52.9,120.7), 293.5x87.7x22.7, first ray hit about 44 studs out. It's the olive block behind the vine arch.
- Confirmed with a one-frame LocalTransparencyModifier test (`pad_11_back_hidecw_v19.png`).
- It is a backdrop canopy_wall, not a frond, so it was not hidden. The generator could thin or push back this one wall if the pad 11 back view should open up.

**(b) Pad 10 dark far canopy:**
- **It did not lift.** The shaded patches read:

  | Point | v18 lighting | v19 lighting |
  |---|---|---|
  | (820,300) | (7,26,9) | (6,24,11) |
  | (600,330) | (12,36,13) | (10,34,16) |
  | (900,360) | (11,32,10) | (9,31,13) |
  | (1000,330) | (10,30,10) | (8,30,12) |

  The threshold is (30,55,20).
- Ray probes show the mass is two first-layer BackdropPersistent canopy_walls. Hiding one alone left the second dark.
- **Hidden (Transparency 1, CanCollide/CanQuery/CastShadow false; not deleted):**
  - `Workspace.World.Dressing.BackdropPersistent.canopy_wall` at x 521.6, z 159.1 (y 52.5), size 293.5x87.7x22.7, scale 1.0, mesh 89183111808394
  - `Workspace.World.Dressing.BackdropPersistent.canopy_wall` at x 557.3, z 45.7 (y 49.1), same size and mesh, scale 1.0
  - Script: `~/stage/thin19.luau`.
- **ltdr19 would bring them back; the generator needs the same rule.**
- **After:**
  - That area of pad_10_back now shows sky (116,178,210) and lighter distant jungle (51,87,45).
  - The only remaining darks are palm-trunk bands (about 15,4,0).
  - Side effects: pad 9 front loses its dark canopy band (distant palms show instead); pad 9 back, pad 10 front and pad 11 back are unchanged (0 to 6.6k px). See `*_prethin.png`.

## 5. Pad 17 hump
Still flat in `pad_17_v19.png` / `hump_pad17_v19.png`: flat green ground up to the rock base. terr16b is green: hump voxels Air / LeafyGrass 0.26 (edge) / Air; Rock region 286 Rock, 0 LeafyGrass. Terrain was not touched.

## 6. Ruin_wall swap (kit_v2_6_1)
**Import:**
- `~/sc19imp261fbx/kit_ruin_wall.fbx` (sha1 8e888392…, byte-identical to `~/stage/ruin_wall_new/kit_ruin_wall.fbx`; READY present).
- Method: File > Import, Cmd-Shift-G, Studio Default preset, Import. The Import Queue showed a green check.
- The preview showed the bevelled stones with moss caps and vines.

**Imported part:**

| | MeshId | TextureID | Size |
|---|---|---|---|
| New | **rbxassetid://99217150386445** | **rbxassetid://125403212114636** | 23.09x16.56x11.09, same as the old |
| Old | 127133709792681 | 74097284487246 | 23.09x16.56x11.09 |

- I set the part to Color white, then ran ltdr19: `DR converted templates: ruin_wall`. Workspace kit_ruin_wall is gone (converted).
- **Texture readback** (EditableImage): 256x256. All 14 sampled cells equal `~/stage/ruin_wall_new/kit_ruin_wall.png`, e.g. r0c0 (120,84,56), r3c0 (115,100,92), r3c1 (94,82,76), r3c2 (135,119,110). The texture is present.

**Audit:**
- Template `ServerStorage.KitV1.ruin_wall` and all 3 placed `Dressing.Set2.ruin_wall` use the new ids: Color (255,255,255), Plastic, no SurfaceAppearance.
- Placed walls:
  - pad 17: (406.0,80.7,-313.1)
  - pad 9: (723.5,17.2,-93.5)
  - pad 11: (184.8,24.2,-48.6)

**Rendered stone** (it's the lighter, neutral rock):
- `ruinwall_lit_v19.png` (sunlit side):
  - light stones (147,132,121) / (155,141,131)
  - mid stones (110-123, 93-105, 87-109)
- `ruinwall_v19.png` (the side facing the pad 17 tee, which is in shade):
  - light (71-77, 67-72, 72-74)
  - mid (52-58, 47-51, 53-55)
  - dark (32-35, 29-31, 34)
- For comparison, the old wall in the pad 17 front view was warm (84,72,62); the new one reads neutral (58,50,54) in the same area.
- The bevels and moss caps are clearly visible. From the pad 17 and pad 9 tee views (shaded side, far) it still reads as stacked stones.

**Sig hash:** fb63b14e, stable over two runs, and the same on the reopened place.

## 7. Screens and 7b haze
**7b. Horizon band** (`overview_v19.png` at x 680):
- **Before:** a uniform grey band (126,137,155) from y 95 to about 265, between the sky (153,187,202) and the sea.

| Haze | Band (y 100 / 150 / 250) | Distant terrain (900,330) / (1200,300) |
|---|---|---|
| 0.15 (v18) | (126,137,155) / (125,137,155) / (122,136,153) | (17,103,35) / (97,86,85) |
| 0.10, 0.05, 0.02, 0.01 | **unchanged** | unchanged |
| 0.05 + Color (200,220,235) | band turns blue (93,127,173): still a band | unchanged |
| **0 (applied)** | **(169,200,211) / (194,208,211) / (199,201,200): band gone**, sky gradient down to the sea horizon | **unchanged** (not flat, not blown out) |

- Eye-level check at Haze 0 (`haze0_bf16/bf15/jungle/tf3.png`):
  - The grey strip above the sea in pad 16 back is gone.
  - Jungle and pad 15 are unchanged.
- **Applied: Atmosphere Haze 0.15 -> 0.** Color (255,235,210), Decay (190,150,110), Density 0.04, Offset 0.05 and Glare 0.40 are unchanged. Script: `~/stage/haze19.luau`.
- Then the whole set was retaken.

**Notes from the set:**
- Torch flame looks the same as v18 (rendered median (245,178,43)). No glare, no blown areas.
- The far side of the sea horizon is now a pale whitish gradient (about 199,201,200) instead of the grey band.
- Shaded canopy in the pad 12 back view stays near-black (about 0,8,0 in the darkest gaps).

**Screens** (`~/stage/shots14/`, 1360x877, viewport only, every image looked at, halo.py = 0 on every shot; camera restored to Custom FOV 70 after each batch, LocalTransparencyModifier nonzero 0):
- `pad_1_v19.png` … `pad_18_v19.png`
- `pad_1_back_v19.png` … `pad_18_back_v19.png`
- `overview_v19.png`, `jungle_v19.png`
- `torch_closeup_v19.png`, `torch_check_pad5_v19.png`, `hut_closeup_v19.png`
- `panel_pad6_v19.png`, `panel_pad13_v19.png`, `panel_pad18_v19.png`
- `cliff_pad18_v19.png`, `hump_pad17_v19.png`
- `ruinwall_v19.png`, `ruinwall_lit_v19.png`
- Contact sheets (tools16/sheet.py): `shots14/sheets_v19/fronts_1_9_v19.png`, `fronts_10_18_v19.png`, `backs_1_9_v19.png`, `backs_10_18_v19.png`, `misc_v19.png`, `misc2_v19.png`

**Evidence files:**
- BEFORE (v18 lighting): `hut_before_v19`, `cliff_before_v19`, `felt_pad5_before_v19`, `felt_pad17_before_v19`, `calib_sun_before_v19`, `calib_vert_before_v19`, `cliff_notex_before_v19`, `pad_10/11/12_back_before_v19`, `torch_closeup_before_v19`, `overview_before_v19`
- After lighting: `calib_sun_v19`, `calib_vert_v19`, `cliff_notex_v19`, `felt_pad5/17_after_v19`, `felt_pad5/17/18_it1/it2_v19`
- `hut_diag_nolantern_v19`
- Torches: `torchtee_pad1/5/17/18_v19`, `torchside_pad1/1b/1c/1d/18_v19`
- Canopy: `pad_11_back_hidecw_v19`, `pad_10_back_thintest/thinL1/thinL12_v19`, `t1_*.png`, `*_prethin.png`
- Haze: `haze_ov_010/005/002/001/000/005blue.png`, `haze0_*.png`
- The earlier attempt's: `*_prior.png`

## 8. Final checks, publish, reopen
**Pre-publish chk16 + hut16 + sig16b + terr16b** (identical on the reopened place):
- **Torches:** 14; flame, core, light and emitter bad all 0; flame (240,110,30), light 1.5.
- **Parts:** grey 0, other Neon 0. Meshparts 3330, instances 3955, pointlights 74, templates 34, no stray kit_.
- **Lighting:** clock 12, lat 80, **bright 1.60**, exp -0.30.
- **Atmosphere:** density 0.040, offset 0.05, **haze 0.00**, glare 0.40; Color (255,235,210), Decay (190,150,110).
- **Grade:** ColorCorrection sat 0, contrast 0.05, tint white. Bloom 1.1 / 0.35.
- **LIGHTRB:** top (255,245,230), bottom (0,0,0), ambient (110,110,115), outdoor (135,135,140).
- **Felt and decor:**
  - felt 18 at **(87,147,79)** (chk16 flags 18 against the old target, as expected)
  - footprints 5 / 0
  - wreck_glow and cave_glow SmoothPlastic
  - backfill 3 (40/1.5, 55/3, 55/3)
  - huts 4 / 0 bad, kit_v2_4 ids unchanged
- **Hashes and terrain:** sig16b hash **fb63b14e** (rows 3619, desc 3704). terr16b green. Both cliffs on 104642093288682 at (115,100,92).
- **Other:** two canopy_walls hidden; ruin_wall template and 3 placed walls on the new ids. No test Part.
- **Settings:** HttpEnabled false, StreamingEnabled true. Sun elevation 33.5. LocalTransparencyModifier nonzero 0.

**BuildInfo:**
- `tools/stamp` was run, and Rojo synced it (stampedAt 2026-11-01T13:21:46Z read back in the place).
- **sha 2c8845407fdcfa52bef46192a6c8b0c8a8e552b0 (HEAD at publish), dirty false.**

**Save and Publish** (File menu via System Events on pid 61461; frontmost verified):
- Save: `Saved new changes in "Pirate Shipwreck" to Roblox.` at 2026-11-01T13:22:11.950Z.
- **Publish** (existing place, not Publish As):
  - `→ Add publish notes to v19`
  - `Published new changes in "Pirate Shipwreck" to Roblox.` at **2026-11-01T13:22:33.196Z = 05:22:33 AM PST**
  - Log: `~/Library/Logs/Roblox/0.745.0.7451137_20261101T122155Z_Studio_343b7_last.log`

**Reopen:**
- File > Close Place closed with no prompt (Start page). Then I ran `open roblox-studio:1+launchmode:edit+task:EditPlace+placeId:131316561222931+universeId:10771778371`.
- New **pid 65929**, log `..._20261101T132308Z_Studio_c0bae_last.log`. The line `DataModel Loading https://assetdelivery.roblox.com/v1/asset/?id=131316561222931&version=19` came at 13:23:12Z. **Reopen version = 19.**
- MCP is on it (marker `V19C_MARKER_REOPEN_7140` is in that log). All checks above were rerun there and are identical, lighting values included.

**Deploys row:**
- `~/src/vr-mini-golf-v2` commit **c2339cd `docs: add v19 deploys row`** (not pushed), inserted after the v18 row.
- I re-stamped afterwards (BuildInfo sha c2339cd, gitignored). If Rojo connects to the reopened session, it may sync that into it. That change would be unsaved and unpublished, as in earlier rounds.

## Files
- **New:**
  - `light19.luau` was used as delivered.
  - `shot19.luau` (shot driver via :8767), `calib19.luau` (test Part / texture blank with guaranteed cleanup)
  - `felt19.luau`, `torch19.luau` (torch read-back), `eye19.luau` (eye-height audit + probes)
  - `thin19.luau` (canopy hide), `haze19.luau`
  - `cam_rw19.luau`, `cam_rw19b.luau`, batch files in `~/stage/v19s/`
- **In the place, outside the generator:**
  - felt Color
  - Atmosphere Haze
  - the 2 hidden canopy_walls
  - **ltdr19 reverts the canopy hide, not the felt or haze.**

## Problems / follow-ups (for the generator / art)
1. **Hut still hot**, and the cause is now pinned down: the two `lantern_hanging` PointLights (brightness 4, range 18, (255,170,90)) about 18 studs from each hut. Lowering kit_v2 lantern brightness (or range) in the generator should bring the thatch toward target. The hut and its texture are fine.
2. **Calibration miss:** plain (115,100,92) renders (134,118,113) on the untextured lit cliff face and (169,145,134) fully sun-facing, vs target (125,108,98). Not tuned, per the brief.
3. **Torch ground fit:**
   - Pads 4-17 float about 1.0 above terrain (Y = FeltTopY+0.5, no terrain snap at |u| 24).
   - **Pad 18 is buried 3.9.**
   - **Pad 1 is pushed into the wreck hull** (|u| 24 is outside the deck).
   - The placer should ground-snap rim torches, and pad 1 needs its own offset.
   - Pads 4/5 may clip small Edge rocks.
4. **Pad 10 canopy thinning is place-only:** hidden canopy_walls at (521.6,52.5,159.1) and (557.3,49.1,45.7). The generator should drop or hide these (or similar first-layer walls in the pad 10 back cone).
5. **Pad 11 back:** the large olive block is BackdropPersistent.canopy_wall (185.7,52.9,120.7), about 44 studs out. Left as is.
6. **Felt:** one Color can't hit target on all pads. Pad 17 renders (151,218,127) vs pads 5/18 (105,185,103).
7. **chk16 expectations to update:** felt (87,147,79), haze 0, brightness 1.6, sig fb63b14e.
8. **Studio state:**
   - The v19 place is open in **pid 65929** (MCP on it; its default docks are probably back).
   - Pid 61461 is on the Start page after Close Place. Pids 30033, 34084, 62563, 78191 and 93578 are as before.
   - 18508 untouched.
   - :8765 and the :8767 shot helper (/tmp/v19/shotsrv.py, pid 91202) are still up.
   - The v19chk camera line reads `Fixed` on a fresh check (as noted in v17b). The camera was set back to Custom FOV 70 after every batch and before publishing.
9. **Creator Hub Version History was not checked in a browser.** The version comes from the Studio log ("v19" quick link) and the reopen loading `version=19`.

DONE_V19
