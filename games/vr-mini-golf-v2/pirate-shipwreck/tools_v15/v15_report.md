# Pirate Shipwreck v15 report

**Result: published, version 15.** The place stays private. Nothing was spent, Team Create stays off, no Scripts were written through MCP and no assets were deleted. The stale pid 18508 was not touched.

## Publish and verify
- **Save to Roblox:** log line `Saved new changes in "Pirate Shipwreck" to Roblox.` at 2026-11-01T11:01:36Z.
- **File > Publish** (the existing place, not Publish As): log line `Published new changes in "Pirate Shipwreck" to Roblox.` at **2026-11-01T11:02:45.302Z**, which is **03:02:45 AM PST**. DST ended at 02:00 local on Nov 1, so the Mini's local zone is now PST (UTC-8). The quick link reads "Add publish notes to **v15**".
  - Log: `~/Library/Logs/Roblox/0.745.0.7451137_20261101T103212Z_Studio_1d791_last.log`
- **Reopen:** File > Close Place, then `open roblox-studio:1+launchmode:edit+task:EditPlace+placeId:131316561222931+universeId:10771778371`.
  - Log line: `DataModel Loading https://assetdelivery.roblox.com/v1/asset/?id=131316561222931&version=15` at 11:03:09Z.
  - **Reopen version = 15.** The new Studio process is pid 30033 (log `..._20261101T110304Z_Studio_94e80_last.log`).
- **chk15 on the reopened place:**
  - torches 10 (Torch_CaveMouth, Pad01, 04, 05, 08, 10, 12, 15, 17, 18)
  - flameBad 0, coreBad 0, lightBad 0, emitterBad 0
  - flame colour (240,110,30), light brightness 1.5
  - grey parts 0
  - other Neon 2 (wreck_glow and cave_glow, pre-existing and unchanged)
  - meshparts 3325, instances 3928, pointlights 67, KitV1 templates 34
  - no stray kit_ models
  - clock 12.00, lat 80, bright 2.00, exp -0.30
  - Atmosphere dens 0.040, offset 0.05, haze 0.15, glare 0.40
  - ColorCorrection sat 0.00, contrast 0.05, tint white
  - Bloom threshold 1.1, intensity 0.35
  - http false, StreamingEnabled true
  - sun dir (0, 0.552, 0.834), elevation 33.5 deg
  - Torch distances on the reopened place: Pad05 29.6, Pad17 29.5, Pad18 29.6 studs from the tee.
- **BuildInfo sha 09ea0afdee590573b965c59e798497c6a9203696, dirty false.** That equals git HEAD at publish (the v14 deploys commit).
  - I ran `tools/stamp`; Rojo 7.7.1 on :34872 synced it, and the place's stampedAt matched the file (11:01:15Z).
  - HttpEnabled false. No game code was changed.
  - After publishing I committed the deploys row as **3c861cf** `docs: add v15 deploys row` (not pushed) and re-stamped as `tools/stamp` requires. If Rojo is still connected to the reopened session, it may sync sha 3c861cf into that edit session; that change is unsaved and unpublished. v13 and v14 were handled the same way.

## Steps
1. **Preflight OK.**
   - MCP was connected, PlaceId 131316561222931, universe 10771778371.
   - It was the reopened v14 place (pid 78191). chk read-back matched the v14 report: torches 10, all bad counts 0, bright 2.6, exp 0.2.
   - BuildInfo was already 09ea0af, synced by Rojo after v14.
   - :8765 returned 200.
   - After the reopen, the docks were back (Terrain Editor, Toolbox, Explorer, Properties, Autopilot, Rojo, Asset Manager). I closed them with cliclick. The viewport is again x 3-1916, y 164-1044, so `vp14.env` is unchanged, and shoot14.sh shots were verified viewport-only.
   - No Screen Recording prompt appeared.
2. **grade15:** `GRADE15 bright=2.00 exp=-0.30 sat=0.00 contrast=0.05 tint=1,1,1 bloomThr=1.1`.
   - ltdr15: `LT15D run ok=true nil http=false`.
   - chk15: torches 10, every bad count 0, grey 0, Bloom 1.1, no stray kit_.
3. **Torch retake: the flame was still lemon, so the fallback was applied.** Details in the next section.
4. **Hut pixels:** recorded below. No change was made.
5. **Atmosphere and sun:** unchanged. Details below.
6. **Identification:** see the IDENTIFICATION section.
7. **Visual review:** see below.
8. **All screens retaken:** 46 files plus extra test shots, listed below. The camera was restored to Custom, FOV 70.
9. **Final chk15:** green (same numbers as the reopen read-back above, before publish).
10. **Publish and reopen:** OK, version 15.
11. **Deploys row committed:** 3c861cf.

## Torch flame (step 3)
Pixels are sampled from shoot14.sh viewport crops (1360x877).

| State | Flame (body) | Bowl | Verdict |
|---|---|---|---|
| v14 grade, before anything (`pre_torch_closeup_v14grade.png`) | (255,232,0) | (193,71,10) | lemon |
| v15 grade, Neon (255,140,50), light 14 / 2.0 (`torch_closeup_v15_a.png`, `torch_check_pad5_v15_a.png`) | **(255,227,7)** | (152,53,12) | still lemon (G 227 > 190) |
| v15 grade + fallback: Neon **(240,110,30)**, light **14 / 1.5** (`torch_closeup_v15_b.png`, `torch_check_pad5_v15_b.png`, final `torch_closeup_v15.png`, `torch_check_pad5_v15.png`) | **(255,162,0)** | (133,45,11) | **orange** |

- **Change made:** in `~/stage/dressing_v15.luau`, `TFLAME = Color3.fromRGB(240, 110, 30)` (TCORE (255,220,150) unchanged) and `TLIGHT_BRIGHT = 1.5` (range stays 14).
- After the change I reran ltdr15 (ok=true, http=false) and chk15 (all 0).
- Nothing else changed: no scale, textures or Bloom.
- The core stripe stays cream-white (255,248,222).
- **Final flame:** Neon (240,110,30) renders as (255,162,0), PointLight (240,110,30) at range 14, brightness 1.5.

## Hut colour (step 4): record only
In the pad 5 views under the new grade:
- **Thatch:** about **(235-246, 165-189, 31-39)**. Target is about (200,165,90). v14 was about (254,191,27).
- **Wood posts and rafters:** about **(193-217, 89-98, 15-19)**. Target is (110-140, 70-95, 40-55). v14 was about (238,105,11).
- The grade brought both down a little, but the hut is **still warmer and more saturated than the targets**, with very little blue.
- No change was made, per the brief. It still needs a darker or less saturated palette texture for the hut cells.

## Atmosphere and sun (step 5)
- **Overview:** the horizon band at the top centre measures (138,152,161), against v14's (171,175,173). It is neutral grey-blue, not pink.
- The haze looks the same as in v14 (accepted then). The island is crisp and the ridge is green. **No change:**
  - Density 0.04, Haze 0.15, Offset 0.05, Glare 0.40
  - Decay (200,215,235), Color (255,225,190)
- **Sun:** ClockTime 12.00 and GeographicLatitude 80 are unchanged. The sun direction is the same as in v14 (0, 0.552, 0.834; elevation 33.5 deg; azimuth +Z), and the pad 9-13 tee cameras are unchanged.
  - So the v14 geometry still holds: the sun is 85-120 deg off every front line and outside the view.
  - No sun disc appears in the pad 9-13 front shots. It is visible only in some back views (8, 14), which is allowed.

## IDENTIFICATION (for 3D Model Bot)

### 6a. Near-camera see-through panels
`ident15.luau` (60-stud OBB list) printed only pad felt, rims, boardwalks and fern/rock clumps near the tees. None of the listed parts was translucent.

The decor parts are CanQuery=false, so workspace:Raycast misses them. I used a manual ray-vs-bounding-box test through the panel pixels (`~/stage/ident15_ray.luau`, read-only). For each panel I confirmed the part by setting LocalTransparencyModifier = 1 on it alone, taking a shot (`hide_padN.png`), then resetting it to 0. The panel was gone in each shot.

**Pad 13 front: large translucent olive panel at the left edge (x < 0.1)**
- This is a **Blockout part, not a kit mesh.**
- Path: `Workspace.World.Blockout.HeroPropFootprints.gag10_flytrap_burp`
- Name `gag10_flytrap_burp`, class **Part** (no MeshId, no TextureID).
- Size 20 x 30 x 20, at (-389.2, 39.7, -138.4).
- Transparency 0.50, Material SmoothPlastic, Color (190,215,90), CanCollide false, CanQuery false, CastShadow true.
- **Why it looks see-through:** it has Transparency 0.5 (the footprint placeholder style per deploys.md). It is a box about 47 studs from the tee at the left edge of the frame. The real `Workspace.World.Meshes.Props.prop_flytrap` mesh sits inside it.
- Rendered panel colour is about (65,96,27). Seen from the pad 13 front camera (cam_tf13: (-344.2,28.5,-161.9) looking at (-430.5,22.5,-212.4), FOV 70).
- Proof: `hide_pad13.png`, panel gone.

**Pad 18 front: translucent yellow-olive panel top-left, behind the tall torch**
- This is a **Blockout part, not a kit mesh.**
- Path: `Workspace.World.Blockout.HeroPropFootprints.gag13_captains_last_nap`
- Class **Part**, size 24 x 30 x 24, at (557.8, 121.4, -516.0).
- Transparency 0.50, SmoothPlastic, Color (190,215,90), CanCollide false.
- **Why it looks see-through:** Transparency 0.5. The `Meshes.Props.prop_captain` mesh sits inside it, about 47 studs from the tee.
- Rendered colour is about (187,169,68): yellow-olive over the tan cliff.
- Seen from the pad 18 front camera (cam_tf18: (561.8,99,-465.4) looking at (642.1,93,-525)).
- Proof: `hide_pad18.png`, panel gone.

**Pad 6 front: olive panel at the far left edge, top-left**
- This is a **kit mesh, not a Blockout part.**
- Path: `Workspace.World.Dressing.BackdropPersistent.canopy_wall` (the instance at (765.3, 48.7, 243.4), rotY -102.6 deg).
- Class MeshPart, MeshId `rbxassetid://89183111808394`, which matches the **ServerStorage.KitV1 template `canopy_wall`**. TextureID `rbxassetid://87472779474813`.
- Size 293.5 x 87.7 x 22.7, Transparency 0, Material Plastic, Color (163,162,165) (untinted), DoubleSided false.
- **Why it shows:** it is **not translucent** in v15; it renders as solid dark olive (85,99,37).
  - The pad 6 tee is just past the wall's +X end (tee in wall-local space: X 181.8 against a half-length of 146.7; Z 13.4 against a half-thickness of 11.35).
  - So the tee camera sees the wall's end cap and back edge from about 41 studs, as a flat olive slab at the frame edge.
  - In v14 it only looked like a "panel" because the Studio hover outline traced its edge (see 6b). It is not see-through, and backface culling does not apply here: there is no sky showing through it.
- Seen from the pad 6 front camera (cam_tf6: (712.6,14,417.9) looking at (812.2,8,409)).
- Proof: `hide_pad6.png`, the slab is gone and only sky remains.

**Extra: pad 10 front, translucent vertical olive strip top-right**
- Path: `Workspace.World.Blockout.HeroPropFootprints.gag07_coconut_casualty`
- Class Part, 16 x 55 x 16, at (390.7, 33.7, 119.7), Transparency 0.5, Color (190,215,90).
- Confirmed by a hide shot (`hide_pad10.png`).

**Footprint summary:** `HeroPropFootprints` has 5 parts, all Transparency 0.5, Color (190,215,90), SmoothPlastic, CanCollide false, CastShadow true: gag02_backward_cannon, gag07_coconut_casualty, gag10_flytrap_burp, gag11_croc_nap, gag13_captains_last_nap. They are placeholders that now overlap the real prop meshes. **They are published in the live place and are visible in play.** I did not change them, as the brief allows no permanent scene change. A fix such as Transparency 1 or removal is for the build owner to decide.

### 6b. White / pale-blue halos around tree and canopy silhouettes
**Verdict: no mesh is responsible.** The halo is **Roblox Studio's edit-mode hover outline**. It is drawn only while the mouse cursor is over the 3D viewport and is not part of the game render.

Evidence:
1. **Parked vs hovering.**
   - With the cursor parked on the status bar, the pad 6 front shot has **0** halo pixels (`hover_none_pad6.png`, `ab_pad6_none.png`).
   - Moving the cursor into the viewport, over a tree or the canopy slab, brings it back: **15,308** halo pixels (`hover_tree_pad6.png`, `hover_canopy_pad6.png`).
   - That is pixel-identical in count to v14's `pad_6_v14.png` (15,308), so the v14 shots were taken with the cursor in the viewport.
2. **Same on the other pads.**
   - Pad 3 front: 0 parked, 9,412 hovered (`ab_pad3_parked.png`, `ab_pad3_hover.png`). v14 had 16,183.
   - Pad 12 back: 0 parked, 17,349 hovered (`ab_pad12back_parked.png`, `ab_pad12back_hover.png`). v14 had 17,367.
3. **Class A/B from the pad 6 front camera, cursor parked** (LocalTransparencyModifier = 1 on every MeshPart of one class at a time; files `ab_pad6_<class>.png`):

   | Class hidden | MeshParts | Halo pixels |
   |---|---|---|
   | canopy_wall | 79 | 0 |
   | cliff_ridge | 16 | 0 |
   | palm_* (palm_s, palm_m, palm_l, palm_lean_a, palm_lean_b) | 257 | 0 |
   | vine_arch | 37 | 0 |
   | rock_l / rock_m / rock_s | 1154 | 0 |
   | stack_* | 0 (no such MeshParts exist now) | 0 |
4. **Hiding meshes doesn't remove it.** With all 79 canopy_wall MeshParts hidden and the cursor in the viewport, the outline is **still drawn at the hidden canopy walls' silhouettes in empty sky**, with the same 15,308 pixels (`ab_pad6_hover_nocanopy.png`). It is an editor overlay that ignores LocalTransparencyModifier, not mesh pixels.
5. **Colour.**
   - Every halo pixel is a flat **(178,229,255)**, the same in v14 and in the reproduction.
   - It does **not** match PaintLt (118,166,174) or Paint (90,140,150), so it is not palette bleed or mip filtering from the cells above CanopyA/B/C.
   - It is not a sky-coloured alpha fringe either: the sky behind it is (107,174,209).
   - No meshes need changes for this. Future shots must park the cursor outside the viewport; shoot15 runs did this (cursor at 1000,1075).
6. **Cleanup:** every BasePart's LocalTransparencyModifier was reset to 0 and verified (3757 parts, 0 nonzero) before the final shots and publish. LocalTransparencyModifier is not saved anyway. chk15 was rerun afterwards: all green.

## Visual review (step 7)
- **Torches on pads 5, 17, 18:** now about 6.4 studs further back (29.5-29.6 studs from the tee) and no longer looming.
  - Pad 5: the torch stands small beside the hut.
  - Pad 17: mid-left, well back.
  - Pad 18: mid-left with the cave torch behind.
  - The flame reads orange everywhere.
- **Tiered canopy backdrop on pads 10-14:** still there; layered dark canopy walls in the 10-13 front views and the overview.
- **No regressions vs v14:**
  - Ruin arch and vine arches on 10, vine arch on 14.
  - Ridge green in the overview.
  - Water, sand and the felt look the same, slightly darker and less saturated under the new grade, as intended.
  - All 46 shots are viewport-only, with no Studio UI and no halos.
- **Panels still visible in the final scene** (unchanged, by rule):
  - pad 6 canopy_wall end (top-left)
  - pad 13 gag10 footprint (left edge)
  - pad 18 gag13 footprint (top-left)
  - pad 10 gag07 footprint strip (top-right)

## Screens (`~/stage/shots14/`, 1360x877, viewport only, all looked at)
- `pad_1_v15.png` … `pad_18_v15.png`
- `pad_1_back_v15.png` … `pad_18_back_v15.png`
- `overview_v15.png`, `jungle_v15.png`
- `torch_closeup_v15.png`, `torch_check_pad5_v15.png` (final settings)
- `panel_pad6_v15.png`, `panel_pad13_v15.png`, `panel_pad18_v15.png`
- `halo_pad6_v15.png`, `halo_pad3_v15.png`, `halo_pad12_back_v15.png` (final scene, cursor parked: no halo)
- Evidence and intermediate files:
  - `pre_torch_closeup_v14grade.png`
  - `torch_closeup_v15_a/_b.png`, `torch_check_pad5_v15_a/_b.png`
  - `hut_pad5_v15.png`, `overview_v15_a.png`
  - `idA_pad6/13/18.png`, `hide_pad6/10/13/18.png`
  - `hover_tree_pad6.png`, `hover_canopy_pad6.png`, `hover_none_pad6.png`
  - `ab_pad6_{none,canopy_wall,cliff_ridge,palm,vine_arch,rock,stack}.png`, `ab_pad6_hover_nocanopy.png`
  - `ab_pad3_{parked,hover}.png`, `ab_pad12back_{parked,hover}.png`

## Files changed or added
- `~/stage/dressing_v15.luau`: TFLAME (255,140,50) → (240,110,30), TLIGHT_BRIGHT 2.0 → 1.5. TCORE and range are unchanged.
- New `~/stage/run15.luau`: runner that loads a stage file from :8765 with print capture, plus a shot via :8767.
- New `~/stage/ident15_ray.luau`: read-only ray-vs-bounding-box probe.
- New `~/stage/helper15/shot_helper.py`: localhost-only :8767 helper that runs shoot14.sh. It is stopped now.
- `~/src/vr-mini-golf-v2`: commit `3c861cf docs: add v15 deploys row` (not pushed). BuildInfo was re-stamped afterwards (gitignored).

## Problems / follow-ups
1. **Hut colours are still warm and saturated** under the new grade (thatch about 240,180,35; wood about 205,92,18). It needs a palette or texture change for the hut cells.
2. **The Blockout `HeroPropFootprints`** (5 parts, Transparency 0.5) are live in the published place and show as translucent olive boxes over the real props on pads 10, 13 and 18 (and probably at the cannon on 2, the croc on 11 and the cave set). They should be hidden (Transparency 1) or removed in a future build. That was out of scope here.
3. **The pad 6 tee looks at the end cap of a BackdropPersistent canopy_wall** about 41 studs away (top-left slab). The wall could be shortened or moved, or given a closed, double-sided end.
4. **The halos were never in the game.** Any shot taken with the cursor over the Studio viewport will show the (178,229,255) hover outline; the shooting setup must park the cursor.
5. **Two non-torch Neon parts** (wreck_glow, cave_glow) are unchanged from v13.
6. **Studio state:**
   - The v15 place is open in pid 30033.
   - Pid 78191 and pid 62563 sit on the Start page.
   - Pid 18508 was untouched (MacBot owns it).
   - The reopened session has its default docks open again.
7. **Creator Hub Version History was not checked in a browser.** The version number comes from the Studio log ("v15" quick link) and from the reopen loading `version=15`.

DONE_V15
