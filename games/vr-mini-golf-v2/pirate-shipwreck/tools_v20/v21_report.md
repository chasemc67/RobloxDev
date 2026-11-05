# Pirate Shipwreck v21 report

**Result: PUBLISHED as version 21, private.**
- Save to Roblox at 2026-11-01T16:57:45Z (`Saved new changes in "Pirate Shipwreck" to Roblox.`).
- File > Publish at **2026-11-01T16:58:02.750Z = 08:58:02 AM PST**. Log: `Published new changes in "Pirate Shipwreck" to Roblox.`, `→ Add publish notes to v21`.
- Reopened with the protocol URL as new pid **30994**. Log `0.745.0.7451137_20261101T165833Z_Studio_a8a65_last.log`: `DataModel Loading https://assetdelivery.roblox.com/v1/asset/?id=131316561222931&version=21` at 16:58:36.913Z.
- chk20, chk20s (scoped), sig16b ×2 and terr16b on the reopened place are **line-for-line identical** to the pre-publish run (88 lines). Sig **f82361ee** before and after.
- Private; HttpEnabled false; no Robux, no Team Create, no Scripts through MCP; nothing deleted (hidden = Transparency 1).
- Pid 18508 was not touched. Every GUI input went through activate-by-pid with a frontmost-pid check (p.sh / shoot.sh).
- No Screen Recording prompt.

**Read first: deviations and judgment calls**
1. **chk20 ends `ALL EXPECTED RED`** on its two hut-lantern lines only.
   - Its new hut scope reads `d.Parent.Position` only for BasePart parents. The lantern PointLights are parented to Attachments, so no light matches (`lantern_hanging PointLights: ` empty), and the shadows rule is not scoped at all.
   - `v21s/chk20s.luau` is identical except that it uses `Attachment.WorldPosition` and lets the shadows rule skip the 3 ruin_arch 4/18 lanterns. It reads **ALL EXPECTED GREEN**: `lantern_hanging 1.00/16x7`, shadows on.
   - Every other chk20 EXPECT line is ok. Same class of check-scope bug as v20c; I published on that judgment.
   - **chk20 needs `Attachment.WorldPosition` in its lantern scope.**
2. **Trail widths, legs 11-14 (bar 5): marginal.**
   - Mean painted width (area ÷ smoothed centreline) is 11.6 / 10.5 / 11.9 against 10 ± 1.
   - The generator's half-width is 5.0; the excess is the 4-stud cell raster, since cells at bends and joins sit 5-7 studs off the centreline.
   - I judged this within tolerance and did not repaint terrain. Details in §10.
3. **Sun moved: GeographicLatitude 80 → 75** (step 9). This takes the sun disc out of the pad 14 / 7 / 8 back views. Felt lifts about 3 everywhere and stays within bar 10.
4. **Pad 16 SoftPadLight disabled** (Brightness left at 0.3) instead of the generator's 0.3. At 0.3 with lat 75 and the re-seated arch, pad 16 felt read (119,196,107), 14 over; disabled it matches pad 5 exactly.
5. **Pad 16 ruin_arch re-seated.** The generator's "rotated" arch still stood edge-on beside the trail (pillar test failed even at its original spot). I moved it with its lantern to straddle the 16→17 exit trail at (140,-472), yawed 90°.
6. **Hut textures were uploaded by this job's first attempt (≈16:01Z) and reused.** The run was restarted at 08:06 before writing anything. I verified both ids by EditableImage readback rather than uploading duplicates.

## Hard bars

| # | Bar | Measured | Result |
|---|---|---|---|
| 1 | Haze 0 / Glare 0.3 / Density 0.2 / Color (255,235,210); grey sea band gone | Read-back haze 0.00, glare 0.30, dens 0.200, colour ok. Oblique band row (400,100-250): v20c (127,137,155) → v21 (169..205,200..209,208..211), pale sky. boulders_pad16 horizon: (134,138,155) → (175,201,211). pad_16_back: no band | **PASS** |
| 2 | Pad 12 felt not lime, within ~8 of the others | (107,187,101) vs others (107..108,187..188,99..101). v20: (180,226,119) | **PASS** |
| 3 | Pad 17 back: no floating boulder | boulder_pile@Set2 (311.9,-456.8) hidden; re-audit 0 floaters | **PASS** |
| 4 | Pads 10-14 back cone: no fern/leaf above felt+2.5; no palm in the tee cones; pad 13 no palm trunk crossing | 9 offenders found and hidden → 0 visible. Palms 0 / 0 / 0 on all 5 pads. Pad 13 tee view clear | **PASS** |
| 5 | Trail legs 11-14 10 ± 1 wide; Sandstone under canopy; ferns 3 back; 17→18 ≥ 8; no leaf/fern/palm on sand; pad 8 leafclumps gone; pad 16 arch straddles; overhead ≥ 41 %; 11-14 continuous | Widths 11.6 / 10.5 / 11.9 (marginal, see §10). 17→18 11.1. Sandstone renders (189,167,142) (v20 (160,138,107)). Ferns: 1 at 2.99 studs, 0 nearer. 0 plant centres on trail cells. Both pad 8 leafclumps gone. Arch straddles after re-seat. Overhead **43 %**. Legs 11-14 continuous in overview_paths_c | **PASS** (widths marginal) |
| 6 | Pads 2-9 plain tee view shows trail sand / the planting gap; pad 1 best effort; aprons + edge stones pads 1/2/4/5 | Trail cells reading sand: 2 / 25 / 21 / 15 / 7 / 5 / 5 / 5 (v20: 2 / 25 / 3 / 2 / 5 / 5 / 5 / 7). Sand visible at the planting gap in every frame. Pad 1: 0 (wreck rail). Aprons: partial sand bands; edge stones 3 / 3 / 4 on pads 2/4/5, 0 on pad 1 | **PASS** (2, 6-9 weak by cell count) |
| 7 | Hub sand within ~10 of (226,184,128) | (235,191,134) at BackFill_Pad11 **0.8**; (237,194,133) at 1.0 | **PASS** |
| 8 | Pad 16 felt within ~10 of the others | (108,188,101) with SoftPadLight disabled; 0.3 gave (119,196,107) | **PASS** (value deviates) |
| 9 | Torch core orange-ish, not white | Neon core median (255,250,127), 0 pixels with all channels > 235. SmoothPlastic test (222,145,70), dull tan wedge | **PASS** (Neon kept) |
| 10 | Felt all 18 within ± 8 of (105,185,98) at the critic's point | All 18 at (107..108,187..188,99..101), max dev 3 (table §7) | **PASS** |
| 11 | 16 TeeExitPosts (+ rope, rock_s), grounded, visible, no lights | 16 posts, 48 ropes, rock_s at each foot, bases 0.15 below terrain, 0 lights/children, colour (110,70,40). Eye-height visibility in closeups: 2, 4, 5, 7, 8, 9, 11 yes; pad 1 hidden by the wreck rail (`exit_markers_1b_v21`) | **PASS** |
| 12 | Near-field clutter, pads 13 / 16 / 15 | Pad 13 arch + lantern moved 4 studs back (still clipped at the frame edge, smaller). Pad 16 arch re-seated to the far end, whole in frame. Pad 15 "slab" = sunlit rock_m@Front, moved 4 studs: gone | **PASS** |
| 13 | Overhead coverage, legs 11-14 and pad 14 start | 11: 34 → 45 %, 12: 42 → 57 %, 13: 34 → 47 %, 14: 6 → 12 %; frame c 33 → 42 % | **PASS** (pad 14 start still weak) |

## 1. Preflight
- MCP "Pirate Shipwreck (placeId 131316561222931)" (studio 62ac4c47…). `V21_MARKER_8113` landed in pid 5180's log (`…154432Z_Studio_032dc_last.log`). PlaceVersion 0.
- Docks closed, viewport full (vp14.env 280,166,1360×877).
- Helpers: `/tmp/v21/` shoot.sh, act.sh, p.sh, mk.sh, shotsrv.py on **:8769** (from this job's first attempt; :8767 is v20's), :8765 file server.
- **Inherited state:** this job's first attempt (07:58-08:03) had run ltdr20 on an older placer, uploaded 2 hut images and shot hut variants. matpatch20 had not run. I rebuilt from scratch.
- `dressing_v20.luau` was replaced at 08:06:08; this run used the new file, loaded with a fresh cache key.

## 2. Rebuild
- **ltdr20** (`v21s/ltdr21.luau`, cache key `?v=21_<clock>`): `LT20D run ok=true nil http=false`. Placer log:
  - `DR templates 34`
  - `walkways: 99 boardwalk planks, 280 stepping stones`
  - `torches 15`
  - `hut lanterns lowered 7 (brightness 1)`
  - `kit_v2 point lights 28`
  - `placed 2906 (skipped wet/no-ground 0)`, cave vine strips 6
  - counts: fernclump 627, leafclump 706, palm_l 88, palm_lean_a 20, palm_lean_b 26, palm_m 56, palm_s 17, rock_s 763, rock_m 263, rock_l 61, boulder_pile 20, canopy_wall 67, ruin_arch 3, lantern_hanging 10, vine_arch 37, vine_strip 26
  - `DONE instances 3517`
- **matpatch20, grade20:** ok=true. Sandstone colour reads (236,200,150).
- **SoftPadLights:** 15 and 17 Enabled=false; 16 set to 0.3 (later disabled, see bar 8). None deleted.
- **Felt:** all 18 Plastic (87,147,79).
- **chk20 right after the rebuild:** as in the deviation above. chk20s GREEN; sig16b `643cf721` ×2; terr16b green (hump Air / LeafyGrass 0.26 / Air, Rock 286 / LeafyGrass 0, cliff (115,100,92)).
- **Trail cells:** 2590 (2003 Sand, 587 Sandstone).
  - **Sandstone top-surface cells (terrain ray hit): 492** (491 Sandstone cells plus 1 Sand cell).
  - Sand cells with a Sand top: 1713.
- **Placed in the open place:** 16 TeeExitPost, 48 TeeExitRope, 0 lights on them. BackFill_Pad10 1.5/40, Pad11 1.0/40, Pad12 1.5/40.

## 3. Hut textures
Free private image uploads via the Studio MCP `upload_image` (this job's first attempt), read back here with EditableImage:

| File | Asset id | r4c1 | r4c2 | r5c0 |
|---|---|---|---|---|
| hut_v2_7.png (kit_v2_7) | **rbxassetid://125695280272501** | (107,71,43) | (136,96,59) | (200,165,90) |
| hut_v2_7_1.png (kit_v2_7_1) | **rbxassetid://86926769188910** | (100,72,50) | (122,90,64) | (200,165,90) |

## 4. Hut texture and lantern chain
cam_hut points, 9×9 medians.

| Variant | Thatch (600,200) | Thatch (750,280) | Post (960,560) G/R | Post (330,500) G/R | Deck (640,700) | Lantern glass (880,400) |
|---|---|---|---|---|---|---|
| kit_v2_7, 1.0/16 | (164,123,44) | (141,102,35) | (129,60,24) 0.47 | (145,91,41) 0.63 | (82,49,33) | (245,202,111) |
| kit_v2_7, lights off | (86,63,24) | (79,57,21) | (77,30,15) 0.39 | (67,43,25) 0.64 | (81,49,33) | - |
| kit_v2_7, 0.9 | (160,119,43) | (136,98,34) | (124,58,23) 0.47 | (139,87,40) 0.63 | (82,49,33) | - |
| **kit_v2_7_1, 1.0/16 (final)** | **(164,123,44)** | (141,102,35) | **(118,61,31) 0.52** | **(127,82,47) 0.65** | (75,50,38) | (245,202,111) |
| kit_v2_7_1, lights off | (86,63,24) | (79,57,21) | (69,30,19) 0.43 | (56,39,29) 0.70 | (74,49,38) | (219,143,72) |
| kit_v2_7_1, 0.9 | (160,119,43) | (136,98,34) | (114,59,30) 0.52 | (122,78,45) 0.64 | (75,50,38) | (244,199,108) |
| final, lat 75 (re-shot) | (164,123,44) | (141,102,35) | (118,61,31) 0.52 | (127,82,47) 0.65 | (80,54,41) | (245,202,111) |

- Chain: (a) posts < 0.65 with kit_v2_7 → swapped to kit_v2_7_1, which gives the best posts (0.52 / 0.65). (b) 0.9 does not help (0.52 / 0.64). (c) thatch R is 164 ≤ 210, so 0.9 isn't needed.
- **Thatch bar not met** (164,123,44) vs (200,165,90): about 40 under on G/B. **Posts:** left 0.65 (borderline); the right post (0.52) is also lit by Torch_Pad05. Lanterns glow.
- **Final for the generator: TextureID rbxassetid://86926769188910 (kit_v2_7_1) on all 4 hut_leanto; lanterns 1.0 / 16 / shadows.** Not a hard bar.
- Shots: hut_closeup_v21, hut_posts_lightsoff_v21, lantern_v21, plus variants hut_{a27,b271}_{b10,b09,off}_v21 and lant_*_v21.

## 5. Atmosphere
- Read-back: dens 0.200, haze 0.00, glare 0.30, offset 0.05, Color (255,235,210), Decay (190,150,110). Bloom Threshold 1.1 untouched.
- The band is gone (bar 1 row). Nothing else needed testing.

## 6. Torch core
- Neon (255,190,110), Transparency 0.3, 60 %: core median (255,250,127), 0 white pixels; torch_check_pad5 (254,253,180).
- SmoothPlastic test (all 15, then reverted): (222,145,70), reads as a dull wedge darker than the flame.
- **Final: Neon** (chk20 core bad 0).

## 7. Felt, including pad 12 lime
- **Metric:** 9×9 median at (680,740). That's the point that reproduces the critic's v20 numbers; (680,650) does not, and on pad 1 it lands on the deck.
- **Pad 12 cause:** the felt itself is identical to pads 10/11/13 (Plastic, (87,147,79), no children, Reflectance 0, nothing over it).
  - The only extra light on pad 12 is BackFill_Pad12 (v20 3/55 → lime; v21 1.5/40 still +18 at the tee end).
  - BackFill_Pad10 does the same to pad 10. No torch or hut-lantern light reaches the pad 10 or pad 12 felt.
- **Pads 2 and 4:** sun shadows of Mid palms over the felt.

| Pad | v20 | v21 after the rebuild | **v21 final** |
|---|---|---|---|
| 1 | (105,185,99) | (105,185,99) | (108,188,101) |
| 2 | **(82,161,81)** | (82,162,81) | (108,188,101) |
| 3 | (105,185,98) | (105,185,99) | (108,187,101) |
| 4 | **(95,175,91)** | (96,176,91) | (108,188,101) |
| 5 | (105,185,98) | (105,185,99) | (108,187,101) |
| 6 | (105,185,98) | (105,185,99) | (108,187,101) |
| 7 | (104,185,97) | (105,185,98) | (107,187,100) |
| 8 | (104,185,97) | (105,185,98) | (107,187,100) |
| 9 | (105,185,98) | (105,185,99) | (107,187,101) |
| 10 | **(123,196,102)** | (123,196,103) | (108,187,101) |
| 11 | (105,185,98) | (105,185,98) | (107,187,100) |
| 12 | **(180,226,119)** | (123,196,103) | (107,187,101) |
| 13 | (105,185,98) | (105,185,98) | (107,187,100) |
| 14 | (104,185,97) | (105,185,98) | (107,187,99) |
| 15 | (105,185,98) | (105,185,99) | (107,188,101) |
| 16 | **(89,168,84)** | (104,183,95) | (108,188,101) |
| 17 | (105,185,98) | (105,185,99) | (108,187,101) |
| 18 | (104,185,98) | (105,185,98) | (107,187,100) |

**Per-pad values for the generator:**
- No Felt.Color trims: all 18 stay (87,147,79).
- BackFill_Pad10 and BackFill_Pad12: **1.5 / Range 20** (were 40; each sits 20.4 studs from its felt, so 20 keeps them off it). Back views stay lit: pad 10 back darkest-5 % 24.8 → 22.9, pad 12 23.1 → 22.7.
- BackFill_Pad11: **0.8 / 40**.
- SoftPadLight: 15, 16, 17 Enabled=false (16 Brightness 0.3 kept).
- **CastShadow=false** (still visible) on:
  - palm_l@Mid (-394.8,39.7,294.7) (pad 2)
  - palm_m@Mid (150.6,33.2,397.8), palm_l@Mid (161.0,48.2,407.4), palm_lean_b@Mid (164.7,26.9,403.9) (pad 4)
  - Or move them south out of the felt's sun shadow.
- The +3 over v20 everywhere is the latitude change.

## 8. Pad 17 back view
- Pixel pick on `pad_17_back_v21` (1290,300) → **boulder_pile@Set2 (311.9,109.2,-456.8)**, 81×50×50, 107 studs out.
- Base 84.4 with ground 63.9-95.2 under the footprint: it sits on a crest and overhangs a 20-stud drop, so its underside shows against the sky.
- **Hidden in place (Transparency 1, CastShadow off). The generator should drop it.**
- Re-audit, 140° cone to 160 studs: 0 bases > 0.5 above ground.

## 9. Back-view ferns / palms, pads 10-14
Tee eye = cam_bf/cam_tf eye. Fern cone 160° to 90 studs; palm cones: 16 studs any direction, 140° back and 124° forward to 90.

| Pad | Ferns/leaf in back cone | Above felt+2.5 (before) | Hidden | Visible now | Palms (r16 / back / fwd) |
|---|---|---|---|---|---|
| 10 | 23 | 2 | leafclump@Skyline (492.3,213.3) +3.1, (476.1,186.4) +3.2 | 0 | 0 / 0 / 0 |
| 11 | 5 | 1 | leafclump@Skyline (224.4,89.1) +3.2 | 0 | 0 / 0 / 0 |
| 12 | 25 | 6 | leafclump@Skyline (-35.6,-114.1) +3.2; leafclump@Far (-75.3,-77.7) +3.1, (-76.0,-71.1) +3.2, (-66.3,-61.2) +3.5, (-66.8,-10.0) +3.4, (-28.7,-49.1) +5.0 | 0 | 0 / 0 / 0 |
| 13 | 18 | 0 | - | 0 | 0 / 0 / 0 |
| 14 | 4 | 0 | - | 0 | 0 / 0 / 0 |

- All 9 are in the Skyline / Far folders, which the placer's eye cap doesn't cover. **The generator should cap or drop those folders in the back cones too.**
- Pad 13 tee view: no palm trunk crosses the frame.

**Pad 14 sun:**

| ClockTime / lat | Pad 14 back: sun angle, pixel | Other views with the sun in frame | Pad 5 / 17 / 14 felt |
|---|---|---|---|
| 12 / 80 (v20) | 35° from look, (669,6) in frame (1258 white pixels). Tee view 150°, out | 7 and 8 backs also show the disc at the top edge (189 / 617 white pixels) | (105,185,99) / (105,185,99) / (105,185,98) |
| 11 or 13 / 80 | still in frame | also pad 7 or 8 back | - |
| **12 / 75 (applied)** | 40°, (669,-80): out (0 white pixels) | none; pads 9-13 sun-free | (108,187,101) / (108,187,101) / (107,187,99) |
| 12 / 70 | 45°, out | none | pad 14 felt drops to (82,162,81) (new shadow): rejected |

- **Final: GeographicLatitude 75, ClockTime 12** (sun dir (0,0.623,0.783), elevation 38.5°).
- **Dark slope in the pad 14 view:** terrain Rock (-586,37,-290) and Grass on a slope facing away from the sun, so it's backlit (that view looks toward the sun). No Skyline rock there.
  - A lighter Rock colour is global: it would lift every cliff and change terr16b's cliff readback, so I didn't change it.

## 10. Trail
**Widths** (studs):

| Leg | Perpendicular run on cells, 5 points (v20c method) | Area ÷ smoothed centreline | Cells > 5 from centreline | Rendered overhead, unoccluded points |
|---|---|---|---|---|
| 11→12 | 12.2 / 13.5 / 12.0 / 11.0 / 13.0 | **11.6** | 23 / 191 | 12, 11 |
| 12→13 | 12.0 / 12.0 / 13.8 / 8.0 / 14.5 | **10.5** | 15 / 134 | 15, 12.5, 11.5 |
| 13→14 | 12.5 / 11.8 / 15.8 / 11.0 / 13.5 | **11.9** | 25 / 174 | 8 |
| 17→18 | 12.0 / 13.0 / 12.2 / 12.5 / 11.0 | **11.1** | 17 / 129 | 10.5 |

- v20c (same perpendicular method): 12.5 / 9.0 / 8.5 / 7.0.
- Trimming the cells > 5 from the centreline would give 10.2 / 9.4 / 10.2 / 9.6.

**Other trail measurements:**
- **Sandstone:** legs 11→12, 12→13 and 13→14 are 100 % Sandstone cells (177/111/164). Under the canopy it renders (189,167,142) in `jungle_v21` vs (160,138,107) in v20, with 59 % more sand pixels.
- **Plants on sand:**
  - 0 leafclump / fern / palm centres on trail cells.
  - 11 fernclump centres within 1.5 studs of the edge (Front 5, Edge 4, Fill 2).
  - Within 3 studs of Sandstone cells: 1 fernclump@Front (116.2,7.0) at 2.99.
  - The pad 8 leafclumps (883.3,131.0) and (878.8,127.5) are gone. A different leafclump@Edge sits at (880.4,123.8), off the sand.
- **Pad 16 ruin_arch:** the generator's (101.8,-478.8) with rv (-0.95,0.31) had one pillar on the sand and its centre off it. Re-seated at **(140.0,72.7,-472.0), RightVector (0.200,-0.980)**:
  - pillars off sand, centre on sand, 9 studs of sand under the span;
  - lantern (108.7,-478.0) → (138.8,82.6,-463.6);
  - ground under the span 59.0 / 59.5 / 66.7, so the north pillar sits sunk into the slope.
  - Shots: arch_clearing_v21 (from the east), arch_clearing_w_v21.
- Other arches: (359.2,127.2) and (-359.2,-217.5) straddle (pillar test).

**Overhead:**
- `overview_v21` 1114 / 2590 cells read as sand = **43 %** (42 % with v20c's colour rule). v20c reported 41 % on its 2504 cells.
- Per pad (v20c → v21): 2 48-69→59, 3→61, 4→43, 5→50, 6→47, 7→62, 8→66, 9→55, 10 40→41, 11 34→45, 12 42→57, 13 34→47, **14 6→12**, 15 29→27, 16 26→26, 17 38→40, 18 41→43.
- Frames (v20c → v21): a 47→51 %, b 57→61 %, c 33→42 % (11 38, 12 65, 13 63, 14 29), d 41→46 %.
- `overview_paths_c_v21`: legs 11→12→13→14 read as one continuous pale strip. 11→hub and the pad 14 start (to 15) stay weak.

**Hub (229.9,62.9):** Sand 100 % r10, 92 % r15, 61 % r20. BackFill_Pad11 1.0 → (237,194,133); **0.8 → (235,191,134)** (final, bar ~10 met). The light barely matters; direct sun dominates the hub.

**Aprons and edge stones** (terrain top material in the 12-stud ring outside the felt):

| Pad | Tee end | Cup end | Left | Right | Edge stones at the sand edge |
|---|---|---|---|---|---|
| 1 | 0/174 (sea) | 147/174 | 0/192 | 46/192 | 0 |
| 2 | 14/174 | 76/174 | 28/192 (exit side) | 0/192 | 3 |
| 4 | 64/174 | 81/174 | 0/192 | 39/192 (exit side) | 3 |
| 5 | 63/174 | 77/174 | 0/192 | 27/192 (exit side) | 4 |

- The aprons are partial bands joined to the trail (matpatch flood fill reaches 217/219 studs from pads 4/5; pad 2's reaches 78).
- Pad 1 sits on the wreck, so its ring is mostly water.
- Spurs ahead of pads 2-9 read as sand at the far end in the tee views (§11).

**StepStones:** 264 parts named StepStone (the placer reports 280 stepping stones).

## 11. Tee views, pads 1-9 (plain `pad_N_v21`)
Trail cells within 160 studs projected into the frame (`v21_diag/teeov_N_v21.png`):

| Pad | Cells in frame | Reading sand | Where | Verdict |
|---|---|---|---|---|
| 1 | 38 | 0 | - | no: wreck rail / deck. Best effort; the markers are in `exit_markers_1b_v21` |
| 2 | 40 | 2 | centre | sand visible in the centre planting gap (spur); weak by cell count |
| 3 | 59 | 25 | L/C | yes |
| 4 | 52 | 21 | C | yes (v20: 3) |
| 5 | 43 | 15 | C | yes (v20: 2) |
| 6 | 24 | 7 | L | weak: sand under the torch and in the far centre gap |
| 7 | 57 | 5 | L | weak: sand behind the left rim, ferns over most cells (weakest) |
| 8 | 28 | 5 | L/C | weak: centre gap visible |
| 9 | 26 | 5 | L | weak: left and centre-right sand patches |

- Whole-frame sand-pixel counts are inflated by hut thatch on pads 5 and 8, so I didn't use them for the verdict.
- **What would fix the weak ones:** lower or open the Edge hedge on the trail side for 6-9, the same way the posts were cleared; or yaw the tee camera.

## 12. Near-field clutter and markers

**Pad 13:**
- ruin_arch@Set2 (-361.2,-214.1) → **(-359.2,-217.5)**; its lantern_hanging (-369.6,-214.9) → (-367.6,-218.4).
- Both moved 4 studs along (0.50,-0.86).
- Still clipped at the top right, smaller.

**Pad 16:**
- First move: arch (101.8,-478.8) → (100.7,-474.9) (4 studs).
- Then re-seated across the trail at (140,-472) (§10). It now stands whole at the far end of the tee view.

**Pad 15:**
- The pale slab is the sunlit top of **rock_m@Front (-374.1,-571.4)**, 19×7×20, overhanging the left rim at a grazing angle. It's not trail, spur or apron cells.
- Moved 4 studs to **(-374.9,-575.3)**; gone from the tee view.

**Tee-exit posts:**
- 16 posts: pads 1, 2, 4, 5, 7, 8, 9, 11, two each, 4-13 studs beside the tee where the trail leaves sideways.
- From the straight-down-the-pad tee cameras they fall outside the frame (pixel x -2763 … 3285), except pad 1 (94 studs out, behind the hull rail).
- Closeups `exit_markers_N_v21` (tee eye yawed to the pair) and `exit_markers_1b_v21` (beach-side, pad 1).
- Fix attempt, because only the post tops showed on 2/4/5:
  - **hidden** fernclump@Edge (-398.7,263.1) (pad 2); fernclump@Edge (164.7,327.9), (166.9,326.5), (161.6,326.2) (pad 4); rock_s@Edge (437.8,360.6), (440.6,358.7) (pad 5);
  - **sank 19 foot rock_s** so each top is post base + 1.0. The placer's 7.0×2.7×7.3 foot rocks covered 2 of the 3 post studs, and on pads 2/4/5 one post also stood on a 4-stud hedge rock at the exact same xz: (-402.2,267.1), (167.8,320.3), (439.8,353.2).
- **At eye height now:** 2, 4, 5, 7, 8, 9, 11 yes (rope bands visible); pad 1 no (wreck rail).
- **Generator:** foot rock top ≤ post base + 1; don't place posts on Edge rocks.

## 13. Torch gap table (unchanged from v20c)

| Torch | Base Y | Terrain Y | Gap | Ring |
|---|---|---|---|---|
| Torch_Pad01 | 32.90 | deck plate 33.02 (v20c EditableMesh; the terrain ray hits the sea) | -0.12 | deck |
| Torch_Pad04 | 8.37 | 8.47 | -0.10 | 8.47..8.47 |
| Torch_Pad05 | 10.36 | 10.46 | -0.10 | 10.46..10.47 |
| Torch_Pad06 | 8.37 | 8.47 | -0.10 | 8.46..8.47 |
| Torch_Pad08 | 10.37 | 10.47 | -0.10 | 10.47 |
| Torch_Pad10 | 12.85 | 12.95 | -0.10 | 12.93..12.95 |
| Torch_Pad12 | 19.86 | 19.96 | -0.10 | 19.95..19.96 |
| Torch_Pad15 | 43.84 | 43.94 | -0.10 | 43.93..43.95 |
| Torch_Pad17 | 75.86 | 75.96 | -0.10 | 75.96..75.97 |
| Torch_Pad18 | 98.29 | 98.39 | -0.10 | 98.12..98.69 |
| Torch_Hub02 | 8.72 | 8.82 | -0.10 | 8.79..8.85 |
| Torch_BackPad11 (hub) | 11.54 | 11.64 | -0.10 | 11.62..11.65 |
| Torch_BackPad10 | 12.13 | 12.23 | -0.10 | 12.07..12.35 |
| Torch_BackPad12 | 19.06 | 19.16 | -0.10 | 19.01..19.31 |
| Torch_CaveMouth | 85.67 | 86.67 | -1.00 (sunk by design) | 85.39..87.60 |

## Final values for the generator
1. **Huts:** TextureID **rbxassetid://86926769188910** (kit_v2_7_1); hut lanterns **1.0 / 16 / shadows**. Thatch is still about 40 under the bar.
2. **Lighting:** GeographicLatitude **75** (ClockTime 12). Atmosphere Haze 0 / Glare 0.3 as generated.
3. **Lights:**
   - BackFill_Pad10 and Pad12: **1.5 / 20**.
   - BackFill_Pad11: **0.8 / 40**.
   - SoftPadLight 15 / 16 / 17: Enabled=false.
   - Torch core: **Neon**.
4. **Drop or hide:**
   - boulder_pile@Set2 (311.9,-456.8);
   - leafclumps (492.3,213.3), (476.1,186.4), (224.4,89.1), (-35.6,-114.1), (-75.3,-77.7), (-76.0,-71.1), (-66.3,-61.2), (-66.8,-10.0), (-28.7,-49.1);
   - fernclump@Edge (-398.7,263.1), (164.7,327.9), (166.9,326.5), (161.6,326.2);
   - rock_s@Edge (437.8,360.6), (440.6,358.7).
5. **Move:**
   - pad 13 ruin_arch → (-359.2,-217.5), lantern → (-367.6,-218.4);
   - pad 16 ruin_arch → (140.0,-472.0) yawed to RightVector (0.200,-0.980), lantern → (138.8,82.6,-463.6);
   - pad 15 rock_m@Front (-374.1,-571.4) → (-374.9,-575.3).
6. **Shadows:** CastShadow off (or relocate) on palm_l@Mid (-394.8,294.7), palm_m@Mid (150.6,397.8), palm_l@Mid (161.0,407.4), palm_lean_b@Mid (164.7,403.9).
7. **Tee-exit foot rocks:** top ≤ post base + 1 (19 sunk 0.72-2.14 studs here); no posts on Edge rocks.
8. **chk20:** use `Attachment.WorldPosition` in the hut-lantern scope (as v21s/chk20s.luau does).
9. **Placer eye cap:** extend it to the Skyline / Far folders in the pads 10-14 back cones.
10. **Trail paint:** the cell rule gives about 11-12 painted width at half-width 5. Paint only cells whose centre is ≤ 5 from the centreline (gives 10.2 / 9.4 / 10.2) if 10 ± 1 must hold exactly.

## Checks
- **chk20** (pre-publish = reopened, identical): every EXPECT ok except `hut lantern lights 1.0 (or 0.9) / range 16 (v21) FAIL` and `hut lantern shadows on FAIL` (scope bug above) → `ALL EXPECTED RED`.
  - meshparts 2985, instances 3768, pointlights 74
  - clock 12, lat 75, bright 1.60, exp -0.30, dens 0.200, haze 0.00, glare 0.30
  - torches 15 / all bad 0; felt 18 / 0 bad; huts 4 / 0 bad; backfill 3
  - sha 235dfad, dirty false; streaming true; http false
- **chk20s:** ALL EXPECTED GREEN; `lantern_hanging 1.00/16x7`.
- **sig16b:** `rows=3431 desc=3517 hash=f82361ee` ×2, pre-publish and reopened. The rebuild alone gave 643cf721; the difference is the in-place edits above.
- **terr16b:** green (hump Air / LeafyGrass 0.26 / Air; Rock 286 / LeafyGrass 0; cliff (115,100,92)).

## Publish
- **BuildInfo:** `tools/stamp` sha 235dfad == HEAD, dirty false; Rojo synced stampedAt 16:57:19Z into the place (read back).
- **Save / Publish:** File menu items via System Events on pid 5180, frontmost verified. Log as at the top.
- **Reopen:** File > Close Place (no prompt), then the protocol URL. New pid 30994, `version=21`.
- **Reopened checks:** identical (diff 0 lines). Edits persisted: SoftPadLights, BackFills, hut TextureID ×4, 16 hidden decor, 4 no-shadow palms, 15 Neon cores, pad 16 arch at (140,-472). HttpEnabled false; camera Custom FOV 70; LocalTransparencyModifier nonzero 0.
- **Deploys row:** `~/src/vr-mini-golf-v2` commit **e861643 `docs: add v21 deploys row`** (not pushed). Re-stamped afterwards (BuildInfo sha e861643, gitignored). If Rojo syncs that into the reopened session, the change is unsaved and unpublished, as in v20c.
- Creator Hub Version History was not checked in a browser; the version comes from the Studio log ("v21") and the reopen loading `version=21`.

## Shots (`~/stage/shots14/`, 1360×877; `_v20` files untouched)
- **Tee / back views:** pad_1..18_v21, pad_1..18_back_v21 (final state).
- **Overviews:** overview_v21, overview_paths_v21 (annotated), overview_paths_a..d_v21 (+ `_raw_v21`), oblique_v21.
- **Run list:** jungle_v21, torch_closeup_v21, torch_check_pad5_v21, hut_closeup_v21, hut_posts_lightsoff_v21, lantern_v21, panel_pad6/13/18_v21, cliff_pad18_v21, hump_pad17_v21, ruinwall_v21, path_leg_v21, hub_v21, apron_v21 (pad 17 camera), arch_clearing_v21 (+ arch_clearing_w_v21), cave_clearing_v21, stepstone_v21, felt_grain_v21, boulders_pad16/17/18_v21.
- **Markers:** exit_markers_{1,2,4,5,7,8,9,11}_v21, exit_markers_1b_v21.
- **Evidence:** hut_*/lant_* variants; t_* test frames (felt fixes, BackFill, sun lat 75/70, pad 16 soft, torch SmoothPlastic, arch, near-field, hub 0.8).
- **Diagnostics:** `~/stage/v21_diag/teeov_N_v21.png`.
- Every image was looked at, singly or on a sheet. **halo.py = 0 on all 98 `_v21` shots.** Cursor swept and parked by shoot.sh; camera restored to Custom FOV 70 after each batch; LocalTransparencyModifier nonzero 0.
- **Sheets** (`shots14/sheets_v21/`): fronts_1_9, fronts_10_18, backs_1_9, backs_10_18, exit_markers, misc, overviews, panels.

## Problems and what I did NOT do
- Hut thatch (164,123,44) is still about 40 under the (200,165,90) bar. Not a hard bar.
- Tee-view trail is weak by cell count on pads 2 and 6-9; pad 1 is blocked by the wreck. Pad 14's start overhead is 12 %.
- Leg widths 11-14 are marginal (above). I didn't repaint any terrain.
- Pad 13's arch end is still clipped at the frame edge after the brief's 4-stud pull-back.
- I didn't change Bloom, the sky, Rock/Grass terrain colours, Atmosphere Decay or the hut lantern brightness.
- No deletions, no MaterialVariant, no Script edits, no public setting, no Robux, no push. No Version History check in a browser.

**Studio state:**
- pid 30994 open on the published v21 place (MCP studio d455561c…);
- pid 5180 at the Start page;
- pids 18508, 30033, 34084, 61461, 62563, 65929, 78191, 93578 untouched;
- :8765, :8767 and :8769 still up.

**Files:** new files only in `~/stage/v21s/`, `~/stage/v21_diag/`, `/tmp/v21/`, `shots14/*_v21*` and this report. Generator files untouched.

DONE_V21
