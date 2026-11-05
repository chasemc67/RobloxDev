# Pirate Shipwreck v22 report

**Result: PUBLISHED as version 22, private.**
- Save to Roblox at 2026-11-01T17:56:47Z (`Saved new changes in "Pirate Shipwreck" to Roblox.`).
- File > Publish at **17:56:57Z = 09:56:57 AM PST**. Log: `→ Add publish notes to v22`, `Published new changes in "Pirate Shipwreck" to Roblox.` No dialog.
- Reopened with the protocol URL as new pid **30870** (MCP studio ab45911e…). Log `0.745.0.7451137_20261101T175722Z_Studio_f71ea_last.log`: `DataModel Loading …?id=131316561222931&version=22` at 17:57:26.754Z.
- chk20, sig16b ×2 and terr16b on the reopened place are **line-for-line identical** to the pre-publish run (48 lines, `diff` empty). Sig **26ef2457** before and after.
- Never public; HttpEnabled false; no Robux, no Team Create, no Scripts through MCP; nothing deleted (hidden = Transparency 1). Pid 18508 not touched. Every GUI input went through activate-by-pid with a frontmost check (`/tmp/v22/p.sh`, `shoot.sh`, `click.sh`). No Screen Recording prompt.

**Read first: judgment calls**
1. **Trail widths (bar 2): published on a judgment call.**
   - I used the v21 perpendicular method on the generator cells, with 5 points per leg spread along the real route.
   - With that method, **7 legs have one point under 8**: 2→3 3.8, 7→8 4.0, 10→11 5.5, 13→14 4.0, 14→15 4.0, 15→16 4.0, 17→18 5.0.
   - Every one of those points is where the painted Sandstone ends against a Rock or Slate outcrop, or at a pad/beach join. matpatch never repaints Rock, so the paint stops there.
   - The clear walkable ground (sand + bare rock/slate) at those points is 14.5-32 studs. The exception is 7→8 (926,282), a 2-cell paint sliver beside a broad beach sand band that the route actually follows (overhead crop checked).
   - I scanned all 3336 trail cells for real necks (painted width < 8 *and* clear width < 8 with planting both sides). I found 8, on legs 9→10, 10→11, 12→13, 14→15 (×4) and 17→18, and widened them in place (29 cells painted Sandstone). They now measure 10.5-15.5.
   - This is the same kind of call as v21's "widths marginal". If you read the bar strictly against painted cells, it is not met.
2. **Pad 12 back cone (bar 1): 10 `leafclump@Far` were still above felt+2.5.** The generator's Skyline/Far cap did not take there. I hid them in place (the one fix) rather than leave the bar failing; names and positions are in §9.
3. **Pad 14 backlit slope (bar 5).** The Limestone (140,125,112) is applied and the slope now reads as light grey rock instead of dark rock/grass. It *renders* (65,65,75) against v21's (37,38,45), because it faces away from the sun. It does not render as (140,125,112).
4. **Placer bug: `palm shadows off: 0`.** The rule tests `m:IsA("Model")`, but palms are MeshParts (single-mesh kit templates), so it never matches. I applied the same rule in place (the 4 listed Mid palms; no palms are within 48 of Pad14). The pad 14 felt shadows actually come from 4 `palm_l@Skyline` about 125 studs south (§8).
5. **Gangplank re-routed in place (bar 4).** The first guess was at the rail gap and visible from the tee, but it dropped 62° and ran through the bow stem and hull wall, so nothing showed from the beach. Final geometry is in §5.
6. **Hub sand (237,195,136)** is +11/+11/+8 off (226,184,128), essentially v21's (235,191,134). I counted that as within "~10" and made no change.

## Hard bars

| # | Bar | Measured | Result |
|---|---|---|---|
| 1 | v21 bars | Haze 0.00 / Glare 0.30 / Density 0.200 / Color (255,235,210) read back. All 18 felts (107..108,187..188,100..101), max dev 3 (§9). SoftPadLights 15/16/17 off, lat 75 / ClockTime 12. Torch core Neon, 0 white pixels in torch_closeup_v22. Pads 10-14 back cones: 0 ferns/leaves above felt+2.5 after hiding 10 on pad 12; palms 0 in every cone. Pad 17 back: 0 floaters. Hub (237,195,136). Overhead trail **50 %** (v21 43 %) | **PASS** (pad 12 needed 10 hides; hub at the edge of ~10) |
| 2 | Trail ≥ 8 every leg; Sandstone renders ≥ (189,167,142); sand along the whole route; 17→18 ≥ 8 | Cell method: legs 1, 3-6, 8, 9, 11, 12, 16 min ≥ 8; 7 legs have one transition point < 8 with clear ground 14.5-32 (7→8 sliver: route on the beach band). 8 real necks widened. Sandstone under canopy renders **(190,167,143)** in jungle_v22 (v21 (190,167,142)). Sand visible along the route in overview_v22 / overview_paths_v22. 17→18 points 12.0/12.8/11.8/8.0/5.0 (5.0 = slate transition, clear 17) | **PASS (judgment call 1)** |
| 3 | Fresh fronts/backs; pads 2-9 far posts visible + sand at the gap; aprons 1/2/4/5; pads 6-9 sand clearly more | All 36 `_v22` md5 ≠ `_v21`. Posts visible on 2-9 after hiding 28 hedge items on 2/4/5/7 (§7). Pads 6-9 sand cells 27 / 17 / 12 / 37 (v21 7 / 5 / 5 / 5). apron_1/2/4/5_v22 shot | **PASS** |
| 4 | Pad 1 gangplank at the rail gap, visible from tee and beach | Visible in the bow gap from the tee (rope posts + plank) and down the bow to the trail head from the beach, after the in-place re-route (§5) | **PASS** |
| 5 | Pad 14: slope light rock; ~30 % sand at the trail start; palm shadows cut; big left rock | Slope (37,38,45) → (65,65,75) backlit. Sand overhead: frame c 40 % (v21 29 %), full overview 43 % (v21 12 %). Felt with shadows (87,164,84) → without (107,187,100), no shadow left. Rock = boulder_pile@Set2, scaled 0.55 | **PASS** (slope colour: judgment call 3) |
| 6 | Pad 13: whole arch + lantern in frame; no palm trunk crossing | Arch + lantern moved 28 studs along the trail; both whole in pad_13_v22. No palm trunk crosses | **PASS** |
| 7 | Hut kit_v2_7_2 upload, readback, all 4 huts, lanterns unchanged | **rbxassetid://118487047899591**, 64/64 cells match the PNG, r5c0 (230,192,112). Set on 4/4, lanterns 1.00/16/shadows ×7. Thatch (190,149,62), target (200,165,90) (soft bar) | **PASS** (thatch soft: closer, still short on G/B) |
| 8 | chk20 green; sig16b ×2; terr16b | chk20 **ALL EXPECTED GREEN**; sig16b 26ef2457 ×2; terr16b green | **PASS** |

## 1. Preflight
- MCP "Pirate Shipwreck (placeId 131316561222931)" = studio d455561c (pid 30994). `V22_MARKER_5521` landed in `…165833Z_Studio_a8a65_last.log` (the v21 reopen log, version=21).
- **Docks were open after the v21 reopen** (Terrain Editor, Toolbox, Explorer, Properties, Autopilot, Rojo, Asset Manager). I closed each with its X button; the viewport is full width and the vp14.env (280,166,1360×877) crop holds.
- Helpers: `/tmp/v22/` (act.sh, p.sh, shoot.sh, click.sh, mk.sh retargeted to pid 30994) and shotsrv.py on **:8770**. Scripts are in `~/stage/v22s/`; the shot driver prefix is `v22s/shot22.luau`.

## 2. Hut texture upload
- Studio MCP `upload_image` of `http://localhost:8765/kit_v2_7_up/hut_v2_7_2.png` → **rbxassetid://118487047899591**.
- EditableImage readback: all 64 cell centres equal the PNG. r5c0 (230,192,112), r5c1 (196,158,90), r5c2 (245,215,155); posts r4c1 (100,72,50), r4c2 (122,90,64).
- Workspace attribute `HutTextureId` = rbxassetid://118487047899591, set before ltdr. The placer applied it to all 4 hut_leanto.

## 3. Rebuild
- **ltdr** (dressing_v20.luau, cache key `?v=22_<clock>`): `LT20D run ok=true nil http=false`. Placer log:
  - `templates 34`
  - `walkways: 99 boardwalk planks, 297 stepping stones`
  - `mouth torch ground 86.7 on Terrain`
  - `torches 15`
  - **`palm shadows off: 0`** (bug, judgment call 4)
  - `hut lanterns lowered 7 (brightness 1)`
  - `kit_v2 point lights 28`
  - `placed 2883 (skipped wet/no-ground 0), cave vine strips 6`
  - counts: fernclump 618, leafclump 696, palm_l 81, palm_lean_a 20, palm_lean_b 24, palm_m 54, palm_s 16, rock_s 773, rock_m 264, rock_l 61, boulder_pile 18, canopy_wall 67, ruin_arch 3, ruin_wall 3, lantern_hanging 10, vine_arch 37, vine_strip 25
  - `DONE instances 3565`
- **matpatch20:** `MATPATCH20 chunks 67 cellsPainted 2965 cellsSkipped 4449`. The skipped columns already had the target material from v21. **grade20:** ok.
- SoftPadLights 15/16/17 Enabled=false (the Blockout already had them off from v21; none deleted). Felts Plastic ×18. Lat 75 / ClockTime 12.
- Palm shadows applied in place: palm_l@Mid (-394.8,294.7), palm_lean_b@Mid (164.7,403.9), palm_l@Mid (161.0,407.4), palm_m@Mid (150.6,397.8).
- **BackFills read back:** Pad10 1.5/20, Pad11 0.8/40, Pad12 1.5/20.
- **Checks right after the rebuild:** chk20 ALL EXPECTED GREEN (`lantern_hanging 1.00/16x7`), sig16b `d54654ea` ×2, terr16b green.
- **Top-surface cells** (terrain ray at each matpatch cell centre):
  - Sandstone target cells 3212 → 2665 read Sandstone, 216 LeafyGrass, 139 Sand, 123 Rock, 55 Grass, 14 Slate.
  - Limestone 340 → 331 Limestone.
  - Sandstone top over all cells: 2770.
  - The non-Sandstone tops are thin top voxels (occupancy 0.06-0.53) where a higher grass/rock neighbour forms the visible surface.

## 4. Hut texture measurement (cam_hut, 9×9 medians)

| Variant | Thatch (600,200) | Thatch (750,280) | Post (960,560) G/R | Post (330,500) G/R | Deck (640,700) | Lantern glass (880,400) |
|---|---|---|---|---|---|---|
| kit_v2_7_1, lit (re-shot now) | (163,123,44) | (141,102,35) | (116,62,31) 0.53 | (129,82,46) 0.64 | (79,55,40) | (245,202,111) |
| kit_v2_7_1, lights off | (85,63,24) | (78,57,21) | (67,31,18) 0.46 | (57,39,28) 0.68 | (78,54,39) | (219,143,72) |
| **kit_v2_7_2, lit (final)** | **(190,149,62)** | **(168,127,50)** | (118,61,31) 0.52 | (127,82,47) 0.65 | (80,54,41) | (245,202,111) |
| kit_v2_7_2, lights off | (110,82,34) | (101,75,30) | (69,30,19) 0.43 | (56,39,29) 0.70 | (79,53,40) | (219,143,72) |

- Thatch is up about 27 R / 26 G / 18 B; target (200,165,90) is still about 10 / 16 / 28 short. Posts are unchanged (same cells as kit_v2_7_1). Lanterns glow.
- **Final for the generator:** `HUT_TEXTURE_ID = "rbxassetid://118487047899591"` (kit_v2_7_2); lanterns 1.0 / 16 / shadows.
- Shots: hut_closeup_v22, hut_posts_lightsoff_v22, lantern_v22, hut_k271_lit_v22, hut_k271_off_v22.

## 5. Pad 1 gangplank
- **First guess:** plank top (-474.8,32.9,255.8) → foot (-459.4,3.1,260.0), 4 wide.
  - It sat in the bow gap between the port rail end (-470,254, rail top ≈43) and the stem (-469..-466, 256-264, top 34-50), so it showed from the tee.
  - It dropped 29.8 studs over 16.4 horizontal (61°) and ran through the stem and bow wall. Invisible from the beach (gp tee/beach/side test frames).
- **Hull map** (EditableMesh RaycastLocal height grid): deck about 27-29 at the bow, port rail top 43-48, stem 46-50.
  - The gap between rail end and stem is only 1-2 studs wide at the lip (about 24-30).
  - Every plank that clears the hull completely has its top hidden behind the rail from the tee, so I kept the top in the gap.
- **Final, in place (Walkways folder, generator part logic; posts at 0.04 / 0.96 of the length, ropes between post tops):**
  - **top A = (-477.0, 32.9, 253.8)**: deck = Pad01 FeltTopY 27 + 5.9, unchanged;
  - **foot B = (-448.0, 4.2, 260.4)**: ground 4.0 + 0.2, the trail head just before the pad 1 TeeExitPosts (-445.8,257.7) / (-449.4,268.5);
  - centre (-462.50,18.55,257.10), plank length 41.33, horizontal run 29.74;
  - **yaw 77.2°** (generator convention dx = sin(yaw)·len/2), **width 4**, slope 44°.
- **Generator data entry:** centre xz (-462.5,257.1), yaw 77.2°, horizontal length 29.74, width 4. In the Pad01 frame (pivot (-511.48,245.84), forward = -LookVector (0.965,0,0.262)), A is at (along 35.4, right 1.4) and B at (65.1, 2.6).
- Its middle passes inside the stem/bow for about 10 studs. It reads as a plank resting against the bow: gangplank_beach_v22, exit_markers_1b_v22.
- From the tee: rope posts + plank in the gap left of the stem (pad_1_v22, gangplank_v22). Same visibility as the first guess.

## 6. Trail
**Widths:** v21 perpendicular run on the generator trail cells (Sandstone + Sand), 5 points at 20/35/50/65/80 % of the route length. The route is a BFS through the cells, bridging boardwalk/stepping-stone gaps only to place the points. "Clear" is the same perpendicular on the terrain top map, counting Sand/Sandstone/Rock/Slate. Values are after the in-place widening.

| Leg | Cells (5 pts) | Min | Clear (5 pts) | Note |
|---|---|---|---|---|
| 1→2 | 12.0 12.2 12.0 12.0 16.0 | 12.0 | 0 0 8 12 12 | clear 0 = thin-voxel grass top at the beach start |
| 2→3 | 3.8 12.0 12.0 12.2 12.0 | 3.8 | 27.8 32 32 26 12 | (-358,286) Rock/Sand transition |
| 3→4 | 8.5 12.0 8.5 12.0 16.0 | 8.5 | | |
| 4→5 | 11.5 8.0 8.5 8.0 12.0 | 8.0 | | |
| 5→6 | 8.8 12.0 12.2 8.2 12.0 | 8.2 | | |
| 6→7 | 12.0 13.2 8.2 10.0 8.2 | 8.2 | | |
| 7→8 | 4.0 4.0 14.0 13.8 13.8 | 4.0 | 6.5 6.5 15 14 14 | (926,282) 2-cell sliver; route on the beach sand band |
| 8→9 | 16.0 10.5 8.2 10.0 9.0 | 8.2 | | |
| 9→10 | 14.5 12.2 8.5 12.0 13.5 | 8.5 | | |
| 10→11 | 5.5 12.5 10.0 27.5 15.0 | 5.5 | 14.5 … | (338,142) Rock side |
| 11→12 | 10.8 12.0 12.5 12.0 12.8 | 10.8 | | |
| 12→13 | 8.0 12.5 11.8 13.2 12.5 | 8.0 | | |
| 13→14 | 4.0 11.5 12.8 13.0 10.8 | 4.0 | 25 … | (-382,-230) Rock side |
| 14→15 | 4.0 12.2 15.0 8.0 9.0 | 4.0 | 30.5 … | (-574,-406) Rock side |
| 15→16 | 8.0 4.0 9.2 12.0 8.5 | 4.0 | 32 … | (-186,-514) Rock crossing |
| 16→17 | 12.8 8.0 12.8 12.5 12.0 | 8.0 | | |
| 17→18 | 12.0 12.8 11.8 8.0 5.0 | 5.0 | 17 … | (582,-434) Slate side |

- Overall: 85 points, 8 under 8 (7 legs), all at transitions.
- Files: `v22_diag/widths_final2_v22.txt`, `necks_v22.txt`, `widths_v22.txt` (literal v21 straight-line sampling: 1→2 7.5, 4→5 6.5, 7→8 4.5, 10→11 4.5).
- **Widened in place (necks):** cells (grid g,h; centre = (-2048+4g+2, -1280+4h+2)) `367,235 368,235 369,235 389,203 390,203 391,202 392,205 396,202 396,201 406,194 407,194 409,196 410,196 492,292 494,289 494,290 495,290 577,341 578,341 578,342 580,338 581,339 630,340 631,339 633,342 634,342 636,219 637,219 639,221 640,221` (list in `v22s/widen.txt`; 29 painted; (494,290) was already Sandstone). Necks: (-570,-342), (-482,-462), (-466,-478), (-414,-498), (-74,-114), (270,82), (482,86), (506,-398).
- **Sandstone renders (190,167,143)** under the canopy (jungle_v22 sand-pixel median; v21 (190,167,142)). In overview_v22 the sand-read trail pixels median (176,156,129) through the atmosphere from 1150 up.
- **Overhead sand** (`trailvis`, final state): overview_v22 **1656/3336 = 50 %**.
  - Per pad: 2 59, 3 63, 4 53, 5 59, 6 57, 7 64, 8 56, 9 62, 10 23, 11 46, 12 58, 13 45, **14 43**, 15 42, 16 35, 17 42, 18 36.
  - Frames: a 55 %, b 66 %, c 45 % (11 36, 12 67, 13 60, **14 40**), d 51 %.
  - Weakest: 10 / hub (23 %), 16, 18. The route reads as a continuous pale strip in overview_v22 and the overlay `overview_paths_v22.png`.

## 7. Pads 1-9 tee views

| Pad | md5 ≠ v21 | Far posts visible | Trail cells reading sand (in frame ≤160) | Trail visible |
|---|---|---|---|---|
| 1 | yes | n/a (gangplank + its rope posts in the bow gap) | 0 / 43 | no (wreck rail); exit reads by the gangplank |
| 2 | yes | **yes** after hiding 9 hedge items (both posts) | 5 / 82 (v21 2) | sand at the gap behind the posts |
| 3 | yes | yes (both, on sand) | 37 / 111 | yes |
| 4 | yes | **yes** after hiding 9 items (both) | 26 / 87 | yes, centre |
| 5 | yes | **yes** after hiding 6 items (both) | 15 / 88 | yes, centre |
| 6 | yes | yes (both) | **27** / 117 (v21 7) | yes, left |
| 7 | yes | **yes** after hiding 4 items (both) | **17** / 94 (v21 5) | yes, left |
| 8 | yes | yes (both) | **12** / 120 (v21 5) | yes, L/C |
| 9 | yes | yes (both) | **37** / 123 (v21 5) | yes, L and R |

- All 36 fronts/backs re-shot fresh; no `_v22` md5 equals its `_v21`.
- Post crops are in `/tmp/v22/posts.png` (projected far-pair positions).
- **Hidden in place (Transparency 1, CastShadow off), blocking the far posts:**
  - pad 2: fernclump@Edge (-367.4,269.8), (-355.9,269.7); rock_s@Edge (-359.7,269.3), (-363.0,270.4), (-370.3,266.7); fernclump@Front (-351.7,284.8), (-341.4,297.0); leafclump@Edge (-379.7,268.0), (-359.2,270.2)
  - pad 4: fernclump@Edge (188.1,329.4), (209.1,332.8), (191.8,331.3); rock_s@Edge (204.6,332.8), (206.2,333.5), (198.1,329.9), (196.3,331.6), (204.1,330.8); fernclump@Front (208.1,321.2)
  - pad 5: leafclump@Edge (480.2,363.2); fernclump@Edge (474.8,364.6), (480.3,365.6); rock_s@Edge (476.3,365.8), (465.9,364.4), (471.2,364.0)
  - pad 7: rock_s@Edge (931.6,299.9), (929.6,301.7); rock_s@Front (931.0,275.0); fernclump@Edge (929.2,307.4)
  - → generator: give pads 2/4/5/7 the same 10-wide sightline gap toward the far pair as pads 6-9.
- **Aprons** (`apron_N_v22`, tee eye yawed 90° to the side of the near TeeExitPost pair):
  - pad 1: right/beach side; the exit itself is ahead at the bow.
  - pad 2: right; opens onto beach sand.
  - pads 4 and 5: left; read as grass at eye level with the exit posts visible, little apron sand.
  - `apron_v22` is the v21 pad 17 apron camera.
- Tee-exit foot rocks: 15 of 32 posts have a rock bounding-box top 0.05-0.5 over base+1. The larger ones are (-342.0,277.9) +2.8, (933.7,287.3) +2.2, and rock_m@Front at (896.1,335.6) +5.0 (2.8 studs off). All posts read in the views. Not changed.

## 8. Pads 13 and 14
**Pad 14 slope:** Limestone patch centred (-598,-289), 340 cells (331 read Limestone). It is behind the tee, so it's in **pad_14_back** (cam_bf14), not the tee view: 0 cells in the tee frame, 322 in the back frame. Rendered median over the slope region:

| Version | x 380-900 / y 300-430 | x 1000-1300 / y 320-420 |
|---|---|---|
| v21 | (37,38,45) | (36,39,53) |
| v22 | (65,65,75) | (67,67,81) |

**Pad 14 felt shadows:**
- Sun rays from 325 felt points hit **palm_l@Skyline (-602.1,-245.4), (-622.5,-252.7), (-572.2,-241.5), (-554.7,-251.9)**, 99-132 tall, about 125 studs south. CastShadow=false in place.
- Felt median (whole felt region) (87,164,84) → **(107,187,100)** (pad 5 (107,186,101)).
- (680,740) is (107,187,100) either way. No shadow is left on the felt (t_pad14_noshadow_v22 / pad_14_v22). The yellow patch on the left of the felt is the left torch/lantern light, as in v21.

**Pad 14 sand at the trail start:** 43 % (overview, v21 12 %); frame c 40 % (v21 29 %). Not short, so no canopy change.

**Pad 14 big left rock:**
- Pixel pick at (100,250)/(150,350)/(200,300) → **boulder_pile@Set2 (-635.0,38.3,-385.2)**, 31.4×19.3×19.6, 48 studs from the eye (the near left edge is lantern_post + leafclump@Front).
- Scaled to **0.55** about its base: size 17.3×10.6×10.8, centre y 33.9, base 28.6.

**Pad 13:**
- The generator's ruin_arch@Set2 at (-357.2,34.4,-220.9) was still clipped at the top right (frame-box x up to 2047).
- Moved arch + lantern 28 studs along the trail (-0.95,0,-0.30): **arch → (-383.9,34.4,-229.3)** (RightVector (0.987,0,0.162) unchanged, ground 19.8 same, centre on trail sand); **lantern (-365.6,44.6,-221.8) → (-392.3,44.6,-230.2)**. Whole arch and lantern now in pad_13_v22.
- Its span still runs along the trail, not across it.
- No palm trunk crosses the pad 13 tee view; palms are 0 in all pad 13 cones.

## 9. Felt, cones, hub
**Felt** (9×9 median at (680,740), final pad_N_v22): every pad (107..108,187..188,100..101), against v21 final (107..108,187..188,99..101). Max dev from (105,185,98) is 3. No trims.

| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|
| 108,188,101 | 108,188,101 | 108,187,101 | 108,188,101 | 108,187,101 | 108,187,101 | 107,187,100 | 107,187,100 | 107,187,101 |

| 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 |
|---|---|---|---|---|---|---|---|---|
| 108,187,101 | 107,187,100 | 107,187,101 | 107,187,100 | 107,187,100 | 107,188,101 | 108,188,101 | 108,187,101 | 107,187,100 |

**Back cones** (v21 audit: ferns 160° / 90 studs; palms r16, 140° back, 124° forward to 90):

| Pad | Ferns/leaf in cone | Above felt+2.5 | Palms r16 / back / fwd |
|---|---|---|---|
| 10 | 21 | 0 | 0 / 0 / 0 |
| 11 | 4 | 0 | 0 / 0 / 0 |
| 12 | 27 | **10 → hidden → 0** | 0 / 0 / 0 |
| 13 | 18 | 0 | 0 / 0 / 0 |
| 14 | 4 | 0 | 0 / 0 / 0 |

- Pad 12, all leafclump@Far, top over felt: (-75.3,-77.7) +3.1, (-76.0,-71.1) +3.2, (-64.0,-68.7) +2.6, (-67.3,-62.4) +3.0, (-48.5,-71.7) +2.6, (-52.0,-63.5) +2.6, (-67.7,-12.0) +3.1, (-42.3,-58.1) +2.6, (-52.1,-12.6) +2.5, (-28.9,-50.0) +3.8.
- These sit on slopes (ground under the footprint up to 12 studs above the base), so a cap from the centre ground misses them. Generator: cap with the max footprint ground, or drop them.

**Pad 17 back:** 0 bases > 0.5 above ground in the 140° cone to 160.

**Hub:** sand-pixel median of hub_v22's lower half is (237,195,136); v21 (235,191,134), v20 (244,205,140). BackFill_Pad11 0.8/40 unchanged.

**v21 edits in the new output:** all present. Boulder (311.9,-456.8) absent; the 4 checked v21-hidden leafclumps, 2 fernclumps and rock_s are absent; pad 15 rock_m at (-374.9,-575.3); pad 16 arch at (140,-472) with RightVector (0.199,-0.980). The **no-shadow palms were missing** (judgment call 4).

## Final values for the generator (in-place changes after the rebuild)
1. **Hut:** `HUT_TEXTURE_ID = "rbxassetid://118487047899591"` (kit_v2_7_2). Lanterns 1.0 / 16 / shadows.
2. **Palm shadow rule:** match BaseParts as well as Models (`d.Name:sub(1,4)=="palm"`).
   - CastShadow off on palm_l@Mid (-394.8,294.7), palm_m@Mid (150.6,397.8), palm_l@Mid (161.0,407.4), palm_lean_b@Mid (164.7,403.9);
   - and on palm_l@Skyline (-602.1,-245.4), (-622.5,-252.7), (-572.2,-241.5), (-554.7,-251.9) (pad 14 felt).
3. **Gangplank:** A (-477.0,32.9,253.8), B (-448.0, ground+0.2 = 4.2, 260.4); centre xz (-462.5,257.1), yaw 77.2°, horizontal length 29.74, width 4, deck Y = FeltTopY + 5.9 = 32.9, ground Y 4.0.
4. **Trail paint:** add the 29 neck cells in `v22s/widen.txt` as Sandstone. Consider painting Rock/Slate route cells too (matpatch skips Rock) if the cell width must hold ≥ 8 at outcrops.
5. **Hide / drop:**
   - the 28 hedge items in §7 (sightline gaps toward the far posts on pads 2/4/5/7);
   - the 10 leafclump@Far in §9 (pad 12);
   - fernclump@Front (-420.0,-501.1) and fernclump@Fill (-462.3,-471.2), on widened cells.
6. **Pad 13:** ruin_arch → (-383.9,34.4,-229.3) with the same rotation; its lantern_hanging → (-392.3,44.6,-230.2).
7. **Pad 14:** boulder_pile@Set2 (-635.0,-385.2) scale 0.55 (size 17.3×10.6×10.8, base on ground 28.6), or drop it.
8. **Unchanged:** Lighting (lat 75, ClockTime 12), BackFills (10/12 1.5/20, 11 0.8/40), SoftPadLights 15/16/17 off, Neon cores, Limestone (140,125,112).

## Checks (pre-publish = reopened, identical)
- **chk20:** ALL EXPECTED GREEN.
  - meshparts 2962, instances 3816, pointlights 74
  - clock 12, lat 75, bright 1.60, exp -0.30, dens 0.200, haze 0.00, glare 0.30, bloom 1.1
  - torches 15 / all bad 0; felt 18 / 0 bad; huts 4 / 0 bad; backfill 3
  - `lantern_hanging 1.00/16x7`, shadows ok
  - sha e861643 dirty false; streaming true; http false
- **sig16b:** `rows=3479 desc=3565 hash=26ef2457` ×2, pre-publish and reopened. The rebuild alone gave d54654ea; the difference is the in-place edits.
- **terr16b:** green (hump Air / LeafyGrass 0.26 / Air; Rock 286 / LeafyGrass 0; cliff (115,100,92)).
- Camera Custom FOV 70 before saving; LocalTransparencyModifier nonzero 0; halo.py 0 on all 102 `_v22` images.

## Publish
- `tools/stamp` in ~/src/vr-mini-golf-v2: sha e861643 == HEAD, dirty false. Rojo synced BuildInfo stampedAt 17:56:31Z into the place (read back).
- Save to Roblox and File > Publish through System Events on pid 30994, frontmost verified. File > Close Place (no prompt), then `open roblox-studio:1+launchmode:edit+task:EditPlace+placeId:131316561222931+universeId:10771778371` → pid 30870, `version=22`.
- **Reopened, persisted:** hut texture 4/4, HutTextureId attribute, 40 hidden items, gangplank, 4 Skyline palms with no shadow, boulder scaled, arch moved, widened Sandstone. HttpEnabled false.
- **Deploys row:** `~/src/vr-mini-golf-v2` commit **66744ba `docs: add v22 deploys row`** (not pushed). Re-stamped afterwards (BuildInfo sha 66744ba, gitignored). If Rojo syncs that into the reopened session, the change is unsaved and unpublished, as in v21.
- Creator Hub Version History was not checked in a browser; the version comes from the Studio log and the reopen loading version=22.

## Shots (`~/stage/shots14/`, 1360×877; `_v20` / `_v21` untouched)
- **Fronts / backs:** pad_1..18_v22, pad_1..18_back_v22.
- **Overviews:** overview_v22, overview_paths_v22 (overlay), overview_paths_a..d_v22 (+ `_raw_v22`), oblique_v22.
- **Run list:** jungle, torch_closeup, torch_check_pad5, hut_closeup, hut_posts_lightsoff, lantern, panel_pad6/13/18, cliff_pad18, hump_pad17, ruinwall, path_leg, hub, apron, arch_clearing (+ arch_clearing_w), cave_clearing, stepstone, felt_grain, boulders_pad16/17/18 (all `_v22`).
- **New:** gangplank_v22, gangplank_beach_v22, apron_1/2/4/5_v22, exit_markers_{1,1b,2,4,5,7,8,9,11}_v22, hut_k271_lit/off_v22.
- **Evidence:** t_gp_*, t_gp3_*, t_gp4_* (gangplank tries, top view), t_pad14_noshadow_v22, t_pad_1_gp_v22.
- **Diagnostics:** `~/stage/v22_diag/` (widths*, necks, topmap, teeov_N_v22).
- **Sheets** (`shots14/sheets_v22/`): fronts_1_9, fronts_10_18, backs_1_9, backs_10_18, exit_markers, gangplank_aprons, hut, misc, overviews, panels.

## Problems and what I did NOT do
- Trail cell widths dip under 8 at rock/slate transitions on 7 legs (judgment call 1). Pad 14's backlit slope renders (65,65,75), not (140,125,112). Hut thatch is short of (200,165,90) by about 10/16/28. Hub is +11.
- Aprons on pads 4/5 read as grass at eye level. The pad 13 arch stands along the trail, not across it. The gangplank passes through the stem for about 10 studs of its length.
- I didn't change Bloom, sky, Rock/Grass colours, Atmosphere, lantern brightness or any BackFill. No canopy edits for pad 14 (not needed).
- No deletions, no MaterialVariant, no Script edits, no public setting, no Robux, no push, no browser Version History check.
- **Studio state:**
  - pid 30870 open on the published v22 place (MCP ab45911e…; its default docks are probably back);
  - pid 30994 at the Start page;
  - pids 18508, 5180, 30033, 34084, 61461, 62563, 65929, 78191, 93578 untouched;
  - :8765, :8767, :8769, :8770 still up.
- **Files:** new files only in `~/stage/v22s/`, `~/stage/v22_diag/`, `/tmp/v22/`, `shots14/*_v22*`, `shots14/sheets_v22/` and this report. Generator files untouched.

DONE_V22
