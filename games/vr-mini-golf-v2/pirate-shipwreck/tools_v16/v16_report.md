# Pirate Shipwreck v16 report

**Result: published, version 16.** The place stays private. Nothing was spent, Team Create stays off, no Scripts were written through MCP, and no assets or Blockout parts were deleted. The stale pid 18508 was not touched.

## Publish and verify
- **Save to Roblox** (File menu, driven through System Events on pid 30033 only): log line `Saved new changes in "Pirate Shipwreck" to Roblox.` at 2026-11-01T11:40:45Z.
- **File > Publish** (existing place, not Publish As):
  - Log line `Published new changes in "Pirate Shipwreck" to Roblox.` at **2026-11-01T11:40:59.556Z = 03:40:59 AM PST**.
  - The quick link reads "Add publish notes to **v16**".
  - Log: `~/Library/Logs/Roblox/0.745.0.7451137_20261101T110304Z_Studio_94e80_last.log`
- **Reopen:** File > Close Place closed with no unsaved-changes prompt. Then I ran `open roblox-studio:1+launchmode:edit+task:EditPlace+placeId:131316561222931+universeId:10771778371`.
  - Log line: `DataModel Loading https://assetdelivery.roblox.com/v1/asset/?id=131316561222931&version=16` at 11:41:32Z.
  - **Reopen version = 16.** The new Studio process is pid 93578 (log `..._20261101T114128Z_Studio_a11bb_last.log`).
- **chk16 on the reopened place:**
  - torches 14: BackPad10/11/12, CaveMouth, Pad01, 04, 05, 06, 08, 10, 12, 15, 17, 18
  - flameBad 0, coreBad 0, lightBad 0, emitterBad 0
  - flame (240,110,30), light brightness 1.5
  - grey parts 0, other Neon 0
  - meshparts 3333, instances 3958, pointlights 74, KitV1 templates 34, no stray kit_
  - clock 12.00, lat 80, bright 2.00, exp -0.30
  - Atmosphere dens 0.040, offset 0.05, haze 0.15, glare 0.40; **Color (255,235,210), Decay (190,150,110)**
  - ColorCorrection sat 0, contrast 0.05, tint white; Bloom threshold 1.1, intensity 0.35
  - felt parts 18, notExpectedColour 0 (120,190,110)
  - footprints 5, stillVisibleOrColliding 0
  - wreck_glow and cave_glow SmoothPlastic
  - backfill lights 3 (Pad10 40/1.5, Pad11 55/3, Pad12 55/3)
  - huts 4, notWhite/plastic/textured 0
  - cliff_lower Color (115,100,92); the carved hump voxel is Air
  - http false, StreamingEnabled true
  - sun dir (0, 0.552, 0.834), elevation 33.5 deg
- **BuildInfo sha 3c861cfd78d4eb2e2c8efdb17db838f5cf167dec, dirty false** (git HEAD at publish, the v15 deploys commit).
  - I ran `tools/stamp`; Rojo 7.7.1 on :34872 synced it (stampedAt 11:40:17Z matched in the place).
  - HttpEnabled false. No game code was changed.
- **Deploys row:** committed as **cfd970f** `docs: add v16 deploys row` (not pushed), then re-stamped as `tools/stamp` requires.
  - If Rojo connects to the reopened session, it may sync sha cfd970f into that session. That change would be unsaved and unpublished, same as v13 to v15.

## Steps
1. **Preflight OK.**
   - MCP was connected to pid 30033 (confirmed with a marker print in its log). PlaceId 131316561222931; :8765 returned 200.
   - The reopen had brought the docks back (Terrain Editor, Toolbox, Explorer, Properties, Autopilot, Rojo, Asset Manager). I closed them all, and the viewport is full width again (vp14.env unchanged). shoot14.sh crops were verified viewport-only.
   - No Screen Recording prompt appeared.
   - "Before" chk16 matched v15: torches 10, all bad counts 0, felt 18 parts at (100,230,135), footprints 5 visible, wreck/cave glow Neon, backfill 0, huts 4 "bad" (see HUTS).
2. **world16 and grade16 ran.**
   - Felt was **(100,230,135) on all 18** Felt parts; now (120,190,110).
   - The 5 footprints were Transparency 0.5. Now Transparency 1, CanCollide/CanQuery/CastShadow false, still in place.
   - wreck_glow: MeshPart, was Neon, (163,162,165), tex 71344437994910. cave_glow: MeshPart, was Neon, (190,80,25), tex 78701320522539. Both are now SmoothPlastic; colours and lights untouched.
   - Atmosphere is set as specified.
3. **ltdr16:** `LT16D run ok=true nil http=false`.
   - chk16: torches 14, all bad counts 0, backfill 3, footprints 0, felt 0, other Neon 0, Bloom 1.1.
   - The rebuild is deterministic: the Dressing position/size signature was identical across a second ltdr16 run.
4. **Huts:** see HUTS below. The template was fixed to Color white. The render is unchanged, and kit_v2_4 was not delivered.
5. **Pad 18 cliff:** identified as `cave_cliff_lower`. Its Color is set, but the render is unchanged (it's a textured MeshPart). See CLIFF.
6. **Pad 17 hump:** carved, then the remaining slope was retextured as Rock. Done; see HUMP.
7. **Visual review:** see below. BackFill tuned on pads 11 and 12.
8. **All shots retaken:** listed below. All are viewport-only with 0 hover-outline pixels, counted per image. The camera was restored to Custom, FOV 70.
9. **Final chk16 and hut16 green;** BuildInfo as above.
10. **Publish and reopen:** OK, version 16.
11. **Deploys row committed:** cfd970f.

## HUTS (step 4)
**Audit (hut16), before any fix.** All five hut MeshParts had the same values:
- Template `ServerStorage.KitV1.hut_leanto` and the 4 placed `Workspace.World.Dressing.Set2.hut_leanto`. The placed huts are at (-92.1,19.5,357.4), (460.1,23.2,428.9) (pad 5), (863.9,23.1,144.2) and (-153.7,32.7,-55.2).
- **Color (163,162,165)** (the importer default, not white). The placer does not tint huts (HUT_MUL nil).
- Material **Plastic**, Reflectance 0, **no SurfaceAppearance**, no children, Transparency 0.
- MeshId rbxassetid://138482272521568, **TextureID rbxassetid://109840655619516**.
  - That TextureID is the hut's own palette PNG: it is unique among the 34 KitV1 templates (canopy_wall is 87472779474813, for comparison).
  - All 34 kit templates sit at the same default (163,162,165) Plastic.
- No kit_assets json with these ids exists on this Mac to cross-check, and there is no record of a kit_v2_3 hut import. **This is the kit_v2_2 hut; nothing from v2_3 is in the place.**

**Fix:** the template Color was set to **(255,255,255)**, then ltdr16 was rerun. All 4 placed huts are now white, and chk16 shows huts bad 0.

**Rendered pixels** (`cam_hut.luau`: pad 5 hut, camera 30 studs from the hut centre, about 15 studs from its front, FOV 70, v15 grade):

| Attempt | Thatch | Wood post | Result |
|---|---|---|---|
| Before, Color (163,162,165) (`hut_closeup_v16_a_grey.png`) | (251,202,46) | (207,89,18) | hot |
| Color (255,255,255) (`hut_closeup_v16_b_white.png`) | (251,201,45) | (207,89,18) | **identical**: Color does not tint a textured MeshPart (same as found in v14). Kept, since the brief requires white. |
| + Material SmoothPlastic (`hut_closeup_v16_c_smooth.png`) | (251,201,44) | (207,90,19) | no change, reverted to Plastic |
| LightEmission / Reflectance | – | – | Reflectance already 0; MeshPart has no LightEmission property |
| Final (`hut_closeup_v16.png`) | (251,201,45) | (207,89,18) | still hot |

- Targets: thatch (200,165,90), wood (110-140, 70-95, 40-55).
- **Verdict:** nothing on the Studio side tints the hut. The hot colours are in the palette PNG (109840655619516). The fix has to be a darker, less saturated texture for the hut cells. The global grade was not touched.
- **kit_v2_4 gate:** `~/stage/kit_v2_4/READY` does **not** exist (the folder doesn't exist), so the current kit_v2_2 hut is kept.

## CLIFF (step 5, pad 18, cam_tf18)
**Identification:**
- `ident15_ray.luau` probe through the tan pixels (60,150), (230,200), (380,250), (480,280): the first solid hit is **`Workspace.World.Meshes.CaveV2.cave_cliff_lower`**. Its properties:
  - MeshPart, size 231.8 x 82.4 x 138.0, at (562.5, 106.8, -605.9)
  - MeshId rbxassetid://78593172579470, **TextureID rbxassetid://99336401497933** (palette PNG)
  - Plastic, Color (163,162,165), Reflectance 0, no SurfaceAppearance
  - Rendered about (141,102,70) lit and (99,68,49) shaded
- Hide tests (LocalTransparencyModifier, reset to 0 afterwards; 0 nonzero before publish):
  - Hiding `cave_cliff_lower` removes the tan faces (`hide18_cliff_lower.png`).
  - Hiding `cave_cliff_upper` (TextureID 103734712397151) barely changes the frame (`hide18_cliff_upper.png`).
- The tan mound at the lower left is **terrain Slate**. Slate's material colour is (105,95,88), already rock-toned, and the mound renders about (147,87,60) in the warm light. **Terrain was not changed.**

**Change:**
- `cave_cliff_lower.Color` (163,162,165) -> **(115,100,92)** (`~/stage/cliff16.luau`). **No rendered effect:** the pixels are identical (`cliff18_colortest.png`), because the textured MeshPart ignores Color.
- Tested and **not kept:** a SurfaceAppearance with ColorMap = the same TextureID and a tint. The tint is a multiply and can't add blue:
  - tint (205,200,215): lit (128,90,61)
  - tint (0.82,0.98,1.0): lit (130,104,70)
  - tint (200,215,255): lit (127,94,70)
  - Shadow faces dropped to near-black (about 60,40,35).
  - The test instances were removed; nothing remains on the part.
- **The tan cells in palette PNG 99336401497933 need recolouring to rock (115,100,92)** (3D Model Bot). Pad 15-17 and the overview were therefore not affected.

## HUMP (step 6, pad 17)
**Finding:** the green mound is LeafyGrass terrain about 105-150 studs ahead of the pad 17 tee (felt at y 76.3).
- Ray hits at (480.6,84.3,-339.9), (491.8,81.7,-358.4), (496.8,87.8,-348.5) and (498,79.6,-375).
- It is the leading edge of a raised shelf, about 78 -> 88-90, rising toward the Set2.boulder_pile at (531,109,-356), whose bottom is y 87.

**Change** (`~/stage/hump16.luau`; ChangeHistory waypoints set; TerrainRegion backups kept in `_G` for the session):
1. **Carve:** ReadVoxels/WriteVoxels at 4-stud resolution in (460..516, 60..104, -392..-320).
   - Columns are lowered to y 78 (the surrounding trail and ground height), ramping back to the original surface between x 492 and 512.
   - It only lowers, never raises: **97 columns, max drop 7.6 studs.**
   - The felt (x ≤ 425), dirt trail, torches and boulders are untouched.
2. The rest of the green swell is the slope under the boulder_pile. Lowering it would leave the boulders floating, so I used the brief's fallback there: **`Terrain:ReplaceMaterial` LeafyGrass -> Rock in (488..536, 80..104, -388..-320)**. That slope now reads as the boulders' rocky base.

**Result:** `hump_pad17_v16.png` (and `pad_17_v16.png`) show flat green ground up to a rock base, with no green hump. Pad 17 back and the overview look normal.

**Note:** this is terrain data in the place only. **A heightmap or terrain regeneration would bring the hump back.**

## Visual review (step 7)
- **Torches:**
  - The pad 1, 4, 6, 10, 12 and 15 rim torches stand beside the rails and are not on the felt.
  - None loom over the camera. Pad 1 sits small on the wreck deck; pad 6 is a new torch, mid-left.
  - The flame renders (255,162,0) and the bowl (139,49,16), the same as v15.
- **Pad 6 front:** the top-left end-cap slab is gone; that area is now sky (`pad_6_v16.png`, `panel_pad6_v16.png`).
- **Footprints:** none visible on pads 2, 10, 11, 13 or 18 (`panel_pad13_v16.png` and `panel_pad18_v16.png` are clean).
- **Overview:**
  - The jungle on pads 10-14 isn't thinned. The front views of 10-14 are as dense as v15.
  - Plant rows now look irregular. The remaining lines in the overview are the vine-arch rows along the trails, which are placed that way on purpose.
  - The atmosphere change is subtle. The horizon band went from (137,151,160) to (129,137,155): slightly more mauve and darker, not strongly warmer.
- **Back views 10-12** (pads 10-12, BackFill tuned):
  - At 40/1.5 the back torch and its warm light showed on the near plants, but the canopy patches stayed near-black. Samples: pad 10 (10,24,4) and (13,35,10); pad 11 (21,52,18); pad 12 (19,48,17).
  - At **range 55 / brightness 3**:
    - pad 11 centre canopy went from (21,52,18) to (99,128,33)
    - pad 12's right side went from (64,125,19) to (165,215,49)
    - pad 10 was unchanged: its dark mass is a Skyline leafclump about 32-70 studs out plus the canopy_wall about 85-160 studs out, beyond the light's reach
  - Moving BackFill_Pad10 14 studs toward the view axis, to (455,24,162), gave no gain, so it was put back.
  - **Final values, which the parent should copy into build_dressing_luau.py:**
    - **BackFill_Pad10: range 40, brightness 1.5, position (443.7, 23.2, 170.9), unchanged**
    - **BackFill_Pad11: range 55, brightness 3, position (231.1, 26.1, -2.5), unchanged**
    - **BackFill_Pad12: range 55, brightness 3, position (-85.7, 30.2, -66.5), unchanged**
    - Torch_BackPad10/11/12 were not moved: (443.7,17.7,170.9), (231.2,20.5,-2.5), (-85.7,24.6,-66.5).
    - Already applied in `~/stage/dressing_v16.luau` as `BACKFILL_PAD = { [11] = { 55, 3 }, [12] = { 55, 3 } }`, plus the matching line in the PointLight creation.
  - **Still dark:** the pad 10 back canopy (shaded leafclump undersides). Its edges read dark green, not black, but the far shaded parts measure about (10,24,4).
- **Pad 10 and 11 back views, big leaves:**
  - Pad 10's big leaf clump is now below the horizon.
  - **Pad 11 still has a large leaf plant reaching the top-left of the frame.** It is `Workspace.World.Dressing.Skyline.leafclump` (69.7 x 24.1 x 63.9, about 13 studs from the bf11 camera). It's in the **Skyline** layer, which the pads 10-12 back-view cap doesn't cover.
  - A similar Skyline.leafclump (85.4 x 29.6 x 78.3) sits about 20 studs from the bf12 camera.
  - That's a generator fix (cap or skip Skyline leafclumps near the 10-12 back cameras). I didn't edit it live because ltdr16 would revert it.
- **Felt:** the parts are (120,190,110). They render about (171,221,135) mid-felt (v15 was mint, (142,238,165)), so it now reads as a warmer, softer green.
- **Rails:** unchanged.
- **Huts:** still hot (see HUTS).
- **Pads 10, 12 and 14 front:** as in v15, a palm and fern clump stand just past the far end of the felt. On pad 10 the jitter made that palm look a little bigger and nearer.

## Screens (`~/stage/shots14/`, 1360x877, viewport only, every image looked at, hover-outline pixel count 0 on every final shot)
- `pad_1_v16.png` … `pad_18_v16.png`
- `pad_1_back_v16.png` … `pad_18_back_v16.png` (10-12 retaken with the final BackFill)
- `overview_v16.png`, `jungle_v16.png`
- `torch_closeup_v16.png`, `torch_check_pad5_v16.png`, `hut_closeup_v16.png`
- `panel_pad6_v16.png`, `panel_pad13_v16.png`, `panel_pad18_v16.png`
- `cliff_pad18_v16.png`, `hump_pad17_v16.png`
- Evidence and intermediate files:
  - `pre16_check.png` (docks open, before the cleanup)
  - `hut_closeup_v16_a_grey/_b_white/_c_smooth.png`
  - `cliff_pad18_before_v16.png` (has a stale hover outline), `cliff_pad18_before_v16b.png`
  - `hide18_cliff_lower.png`, `hide18_cliff_upper.png`
  - `cliff18_colortest.png`, `cliff18_satest.png`, `cliff18_satest1.png`, `cliff18_satest2.png`
  - `hump_pad17_before_v16.png`, `hump_pad17_after_a.png` (carve only), `hump_pad17_after_b.png` (carve + Rock)
  - `pad_10/11/12_back_v16_fill3.png`, `pad_10_back_v16_fill3b.png`

## Files changed or added
- `~/stage/dressing_v16.luau`: added per-pad BackFill override (pads 11 and 12: 55 / 3). Everything else is as delivered.
- New:
  - `~/stage/cam_hut.luau`
  - `~/stage/cliff16.luau`
  - `~/stage/hump16.luau`
  - `~/stage/tools16/px.py` (pixel sampler), `halo.py` (hover-outline counter), `sheet.py` (contact sheets)
- In the place, outside the generator:
  - KitV1.hut_leanto Color white
  - cave_cliff_lower Color (115,100,92)
  - pad 17 terrain carve + Rock
  - plus world16 and grade16 edits
- `~/src/vr-mini-golf-v2`: commit `cfd970f docs: add v16 deploys row` (not pushed). BuildInfo re-stamped (gitignored).

## Problems / follow-ups
1. **The hut is still hot** (thatch about 251,202,46; wood about 207,89,18). No Studio property affects it; the palette PNG 109840655619516 needs darker, less saturated hut cells. kit_v2_4 has not arrived.
2. **The pad 18 cliff is still tan as rendered.** `cave_cliff_lower`'s palette PNG 99336401497933 needs its tan cells recoloured to (115,100,92). Part Color can't tint it, and a SurfaceAppearance tint can't reach the hue without crushing the shadows.
3. **The pad 11 back view still has a big Skyline.leafclump above the horizon** (about 13 studs from the camera); pad 12 has one at about 20 studs. The back-view cap needs to cover the Skyline layer near the pad 10-12 back cameras.
4. **The pad 10 back canopy is still very dark** in its shaded far parts (about 10,24,4). A point light at the tee can't reach it; it needs a different fix (canopy placement or palette, or a light further out).
5. **The pad 17 hump fix is terrain data in the place only.** Regenerating terrain from the heightmap would bring it back. The heightmap needs the same flattening.
6. **The atmosphere change is subtle** in the overview (horizon (137,151,160) -> (129,137,155)).
7. **Hover outline:**
   - Parking the cursor by jumping it straight to 1000,1075 was not enough after the dock clicks: Studio kept a stale hover point and drew the (178,229,255) outline in `cliff_pad18_before_v16.png`.
   - Moving the mouse through the viewport and out in steps cleared it. Every final shot was checked to have 0 outline pixels.
8. **Studio state:**
   - The v16 place is open in pid 93578 (its default docks are probably back).
   - Pid 30033 is on the Start page after Close Place. Pids 78191 and 62563 are on the Start page.
   - Pid 18508 was untouched.
   - The shot helper on :8767 is stopped; :8765 is still up.
9. **Creator Hub Version History was not checked in a browser.** The version number comes from the Studio log ("v16" quick link) and the reopen loading `version=16`.

DONE_V16
