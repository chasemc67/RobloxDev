# Pirate Shipwreck v16b report

**Result: published, version 17 (v17 = v16 + kit_v2_4 hut).** The place stays private. Nothing was spent, Team Create stays off, no Scripts were written through MCP, and no assets or Blockout parts were deleted. Pid 18508 was not touched (see Problems 3: it was briefly raised to the front once, but it got no input).

**The hut still renders hot.** The new hut is in, but the render is unchanged from v16. The cause is the lighting, not the palette PNG (see HUT RENDER).

## New hut ids
- MeshId **rbxassetid://131857226019693** (was 138482272521568)
- TextureID **rbxassetid://108289367129276** (was 109840655619516)
- Asset Manager also lists the Model as 79701502666805.
- Size 32.35 x 27.02 x 30.18, identical to the old hut.

## Steps
1. **Preflight OK.**
   - The MCP was on pid 93578. My marker print `V16B_MARKER_7731` showed up in its log, `..._20261101T114128Z_Studio_a11bb_last.log`.
   - PlaceId 131316561222931, and :8765 returned 200.
   - The docks had reopened: Terrain Editor, Toolbox, Explorer, Properties, Autopilot, Rojo, Asset Manager and Import Queue. I closed them all.
   - The viewport is full width again (y 164-1044, x 3-1916), so the vp14.env crop is unchanged.
   - No Screen Recording prompt appeared.
   - The "before" chk16 matched the v16 publish: all bad counts 0, sha cfd970f, and the old hut ids on all 5 huts.
2. **Import OK.**
   - File > Import, then Cmd-Shift-G to `/Users/chase-mini/sc16imp24fbx`, then Import Preview > Import with the Studio Default preset. The Import Queue showed a green check.
   - It arrived as Model `Workspace.kit_hut_leanto` with one MeshPart `kit_hut_leanto`, Color (163,162,165), Plastic, no SurfaceAppearance, and the new ids above.
   - The FBX in the import folder is byte-identical to `~/stage/kit_v2_4/kit_hut_leanto.fbx`. Its embedded PNG is the kit_v2_4 palette.
3. **Template replaced.**
   - I set the imported part to Color white first, because the placer keeps the template's own Color. Then I ran ltdr16: `LT16D run ok=true nil http=false`.
   - Placer log: `DR converted templates: hut_leanto`, templates 34, torches 14, kit_v2 point lights 28, placed 3256, DONE instances 3707.
   - **Deterministic:** I wrote a new `~/stage/sig16b.luau` signature check. It covers 3622 Dressing part/light rows (name, position, size, colour, light range and brightness; the hut's own colour is left out).
     - The hash was **288e6bfc** before the rebuild, after it, and on the reopened v17 place.
     - Torches 14.
     - BackFill_Pad10 40/1.5, BackFill_Pad11 55/3, BackFill_Pad12 55/3.
     - Felt 18 parts at (120,190,110).
   - **Edits outside Dressing are still in place** (new `~/stage/terr16b.luau` check):
     - The pad 17 hump ray-hit voxels are Air: (481,84,-340) and (497,88,-348). The third point is at the edge of the ramp: LeafyGrass, occupancy 0.26.
     - The Rock retexture region has 286 Rock voxels and 0 LeafyGrass.
     - cave_cliff_lower is Color (115,100,92).
   - chk16 also confirms the world16 changes (footprints 5, stillVisibleOrColliding 0; wreck_glow and cave_glow SmoothPlastic; felt colour) and the grade16 atmosphere (Color 255,235,210, Decay 190,150,110).
4. **Hut audit (hut16):**

   | | Template | 4 placed (-92.1,19.5,357.4), (460.1,23.2,428.9), (863.9,23.1,144.2), (-153.7,32.7,-55.2) |
   |---|---|---|
   | Before | white, Plastic, no SA, no children, mesh 138482272521568 / tex 109840655619516 | same |
   | Imported part | (163,162,165) → set to (255,255,255) before ltdr16 | – |
   | After | **white, Plastic, no SA, no children, mesh 131857226019693 / tex 108289367129276** | **same, all 4** |

   Setting the colour before ltdr16 meant one rebuild was enough; no second ltdr16 run was needed.
5. **Shots:** see HUT RENDER and Screens. The camera is back to Custom, FOV 70.
6. **Final chk16 + hut16 all green.**
   - torches 14; flame, core, light and emitter bad all 0
   - flame (240,110,30), light 1.5
   - grey parts 0, other Neon 0
   - meshparts 3333, instances 3958, pointlights 74, templates 34, no stray kit_
   - clock 12, lat 80, bright 2.00, exp -0.30
   - Atmosphere: density 0.040, offset 0.05, haze 0.15, glare 0.40
   - ColorCorrection: sat 0, contrast 0.05, tint white. Bloom: threshold 1.1, intensity 0.35
   - felt 18 / 0 bad; footprints 5 / 0 visible; backfill 3; huts 4 / 0 bad
   - sun elevation 33.5 deg
   - LocalTransparencyModifier nonzero 0
   - **http false**, StreamingEnabled true
   - BuildInfo: I re-ran `tools/stamp` and Rojo synced it (stampedAt 12:04:41Z read back in the place). **sha cfd970fa75def005be42cabae40f3328d8734a6e (HEAD at publish), dirty false.**
7. **Save + Publish** (File menu, driven through System Events on pid 93578 only):
   - Save: `Saved new changes in "Pirate Shipwreck" to Roblox.` at 12:05:04Z.
   - **Publish** (existing place, not Publish As):
     - `→ Add publish notes to v17`
     - `Published new changes in "Pirate Shipwreck" to Roblox.` at **2026-11-01T12:05:17.080Z = 04:05:17 AM PST**
     - Log: `~/Library/Logs/Roblox/0.745.0.7451137_20261101T114128Z_Studio_a11bb_last.log`
   - **Reopen:**
     - File > Close Place closed with no prompt. Then I ran `open roblox-studio:1+launchmode:edit+task:EditPlace+placeId:131316561222931+universeId:10771778371`.
     - New pid 34084, log `..._20261101T120542Z_Studio_82146_last.log`. The log line `DataModel Loading https://assetdelivery.roblox.com/v1/asset/?id=131316561222931&version=17` came at 12:05:45Z. **Reopen version = 17.**
     - The MCP is on it (marker `V16B_MARKER_REOPEN_5512` is in that log).
     - chk16, hut16, sig16b and terr16b on the reopened place are identical to the pre-publish results: all green, new hut ids, hash 288e6bfc, sha cfd970f.
8. **Deploys row:** `~/src/vr-mini-golf-v2` commit **c810f8d `docs: add v17 deploys row`** (not pushed). The row is inserted after the v16 row and mentions "v17 = v16 + kit_v2_4 hut". I re-stamped afterwards (BuildInfo sha c810f8d, gitignored).
   - If Rojo connects to the reopened session, it may sync sha c810f8d into it. That change would be unsaved and unpublished, same as v13 to v16.

## HUT RENDER (cam_hut.luau: pad 5 hut, 30 studs from centre, FOV 70)
Final numbers are from `tools16/px.py`, 9x9 median.

| Point | v16 (`hut_closeup_v16_old.png`) | **v17 (`hut_closeup_v16.png`)** | Target |
|---|---|---|---|
| Thatch (600,200) | (251,201,45) | **(251,201,48)** | ~(200,165,90) |
| Thatch (750,280) | (238,171,31) | **(239,171,34)** | |
| Wood post (960,560) | (207,89,18) | **(207,89,17)** | (110-140, 70-95, 40-55) |
| Wood post (330,500) | (233,137,31) | **(233,135,31)** | |
| Deck plank (640,700) | (135,58,23) | **(135,58,22)** | |

- Only 32 of 1.19M pixels differ by more than 20 between the two frames. **The render is still off: thatch orange-yellow, wood hot orange.**
- In `pad_5_v16.png` the hut roof and post sample (213,92,12) and (201,97,21).

**Why (diagnosis, nothing kept):**
1. I read back both uploaded textures in Studio (EditableImage ReadPixelsBuffer). **The new texture 108289367129276 holds exactly the kit_v2_4 tones:** straw (200,165,90), (166,134,74), (222,190,130); dark wood (80,50,30); wood (110,70,40); and more.
   - **But the old texture 109840655619516 already held straw (200,165,90) and wood (110,70,40), plus (166,134,70) and (222,190,116).**
   - kit_v2_4 mostly tweaked tones and added cells. The old hut's palette cells were never far off target.
   - So the v16 conclusion ("the palette PNG was the problem") was wrong. I am correcting it here.
2. As a test, I blanked the pad 5 hut's TextureID for one frame (restored straight away; verified all 4 huts carry the new TextureID). Then the white hut rendered **clipped at about (255,250,220)** on roof and post, and (240,222,200) on the deck (`hut_diag_v16b_notex.png`, evidence only).
   - The light reaching the hut is well above 1x, and warm.
   - That is consistent with Brightness 2, warm OutdoorAmbient (150,142,104) and Ambient (100,92,66), the warm Atmosphere and contrast. Together they turn (200,165,90) into about (251,201,45), clipping red and pushing blue down.
   - **The fix has to come from lighting or the grade**, or from a much darker hut texture: roughly half the current values to land on target under this light. That is a Game Art Bot / 3D Model Bot call.
   - **The global grade was not touched.**

## Screens (`~/stage/shots14/`, 1360x877, viewport only, cursor swept through the viewport and parked at 1000,1075, hover-outline pixels 0 on every shot)
- `hut_closeup_v16.png` (new). The previous one is kept as `hut_closeup_v16_old.png`.
- `pad_5_v16.png`: the hut is at top right; the frame is otherwise as before (20 px differ).
- `pad_8_v16.png`: the hut is at the left edge.
- `overview_v16.png`, `jungle_v16.png`: the hut is visible in the jungle frame. They differ slightly from v16, by foliage and particles only.
- The previous pad_5, pad_8, overview and jungle shots are kept as `*_v16_old.png`.
- Evidence: `hut_diag_v16b_notex.png` (texture blanked).

## Files added
- `~/stage/sig16b.luau`: Dressing signature hash.
- `~/stage/terr16b.luau`: read-back of the v16 terrain and cliff edits.
- Session helpers in `/tmp/v16b/` (activate by pid, shot sweep). Not needed later.
- `dressing_v16.luau` and `ltdr16.luau` are unchanged.

## Problems / follow-ups
1. **The hut still renders hot** ((251,201,48) thatch, (207,89,17) wood). The palette is on target; the lighting/grade is the cause (see above). The same likely applies to the other warm palette props.
2. **New hut silhouette:** the kit_v2_4 mesh has leaf shingles on top (seen in the Import Preview). From the pad 5 camera you mostly see the flat underside and rafters, so it looks like the old one.
3. **AppleScript `set frontmost` on a process found by unix id raised pid 18508**, not 93578, once (several Studio processes share the bundle). Nothing was sent to it.
   - After that I activated by pid through NSRunningApplication and drove only pid 93578. I verified the frontmost pid before each input.
   - System Events `click at` and `click button "Open"` do not reach Studio's Qt dialogs: cliclick plus Return keystrokes worked.
4. **Studio state:**
   - The v17 place is open in **pid 34084** (MCP on it; its default docks are probably back).
   - Pid 93578 is on the Start page after Close Place. Pids 30033, 62563 and 78191 are as before.
   - 18508 untouched.
   - :8765 is still up; no :8767 helper was used.
5. **Creator Hub Version History was not checked in a browser.** The version comes from the Studio log ("v17" quick link) and the reopen loading `version=17`.

DONE_V16B
