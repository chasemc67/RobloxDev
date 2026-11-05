# Pirate Shipwreck v14 report

**Result: published, version 14.** The place stays private. Nothing was spent and Team Create stays off. No Scripts were written through MCP and no assets were deleted.

## Publish and verify
- Save to Roblox: log line `Saved new changes in "Pirate Shipwreck" to Roblox.` at 2026-11-01T10:31:27Z.
- File > Publish (the existing place, not Publish As): log line `Published new changes in "Pirate Shipwreck" to Roblox.` at **2026-11-01T10:31:43.708Z**. That is **02:31:43 AM PST**. DST ended at 02:00 local today, so the PDT-equivalent clock time is 03:31:43 AM. The log quick link says "Add publish notes to **v14**".
  - Log file: `~/Library/Logs/Roblox/0.745.0.7451137_20261101T082106Z_Studio_8dbdb_last.log`
- Reopen (File > Close Place, then `open roblox-studio:1+launchmode:edit+task:EditPlace+placeId:131316561222931+universeId:10771778371`): `DataModel Loading https://assetdelivery.roblox.com/v1/asset/?id=131316561222931&version=14` at 10:32:15Z. **Reopen version = 14.** The reopened place is Studio pid 78191.
- MCP read-back (chk14.luau) on the reopened place:
  - torches 10 (Torch_CaveMouth, Pad01, 04, 05, 08, 10, 12, 15, 17, 18)
  - flameBad 0, coreBad 0, lightBad 0, emitterBad 0
  - grey parts 0
  - other Neon parts 2: `WreckV2.wreck_glow` and `CaveV2.cave_glow`. Both are pre-existing v13 set-piece meshes, not changed here; see Problems.
  - meshparts 3325, instances 3928, pointlights 67, KitV1 templates 34
  - no stray kit_ models in Workspace
  - clock 12.00, lat 80, bright 2.60, exp 0.20
  - Atmosphere dens 0.040, offset 0.05, haze 0.15, glare 0.40, Decay (200,215,235), Color (255,225,190)
  - Bloom threshold 1.1, intensity 0.35
  - terrain Rock (115,100,92)
  - http false, StreamingEnabled true
- **BuildInfo sha 25751470ab1fce546d2b5b9bc1b556f705d7196d, dirty false.** This was git HEAD at publish time; `tools/stamp` was run and Rojo 7.7.1 on :34872 synced it. HttpEnabled false.
  - After publishing I committed the deploys row as `09ea0af docs: add v14 deploys row` (not pushed) and re-stamped. The published place therefore carries 2575147, which is the commit before the docs-only row. v13 was handled the same way.

## Steps
1. **Preflight OK.** MCP was connected, placeId 131316561222931, http.server :8765 returned 200, and the place was signed in as MetavrseBuilder. The stale pid 18508 has no windows and was left alone.
2. **Before state (chk14):** 10 torches using the old v2_1 template, all 10 flame/core/light/emitter bad (expected); the earlier interrupted run had already rebuilt with the old torch. Atmosphere was already at 0.04 / 0.35 / 0.2.
2b. **Import OK.**
   - Method: File > Import, Cmd-Shift-G to the folder, then the Import Queue's "Start Import" with the Studio Default preset; both items got a green check.
   - The file dialog selected the palette PNGs too, so I copied only the two FBX files into `/Users/chase-mini/sc14imp22fbx/` and imported from there.
   - Workspace then had Models `kit_torch_tiki` and `kit_torch_tiki_short`, each with 3 MeshParts (body, _Flame, _Core).
   - No Screen Recording prompt appeared.
3. **terrain14, light14, ltdr14:**
   - The placer printed `DR converted templates: torch_tiki,torch_tiki_short`, `DR torches 10`, `DR placed 3260`, and `LT14D run ok=true nil http=false`.
   - chk14 was all green. The stray kit_ models were consumed by the placer, leaving none in Workspace. Selection cleared.
4. **Viewport capture:**
   - I closed every dock (Terrain Editor, Toolbox, Autopilot, Rojo, Import Queue) and turned off the Command Bar (Window > Script) and View > Show View Selector.
   - The viewport is x 3-1916, y 164-1044. `vp14.env` is `VX=280 VY=166 VW=1360 VH=877`, a centred 1.55:1 crop with the same aspect as v12's 1000x645, so the vertical FOV and framing match.
   - shoot14.sh fix: `screencapture` refused to write the hidden `shots14/.full.png`, so the temp capture now goes to `/tmp/shoot14_full.png`.
   - Every shot was checked by eye and contains no Studio UI.
5-10. Shots were taken through a small localhost-only helper on :8767 (stopped afterwards). It let the camera Luau set the camera, wait 3 s, then trigger shoot14.sh synchronously. Afterwards the camera was restored to Custom with FOV 70.

## Torch daylight check (step 6): PARTIAL
- **Before** (Range 10, Brightness 1.2): the flame renders pure lemon yellow (255,232,0) with a cream-white centre stripe. The bowl is dark (151,59,8).
- **Change:** the torch PointLight went to **Range 14, Brightness 2.0** (the allowed maximum) in `dressing_v14.luau`. `chk14.luau`'s expected light values were updated to match. ltdr14 and chk14 were rerun with lightBad 0.
- **After:** the bowl and pole pick up a visible warm pool (bowl 194,71,7; pole 237,154,37). The flame itself can't change, because its colour comes from the Neon material and the light doesn't affect it.
- **Honest verdict:**
  - It reads as a self-lit, stylised yellow flame with a hot core.
  - It is clearly different from the palm leaves.
  - It is lemon yellow, not orange, and close in hue to the gold hut thatch behind it (254,191,27). It does not read as a strongly glowing orange flame in daylight.
  - Scale, colours and textures were not touched, per the rules.
- `cam_tcu.luau` fix: it looked for a `_Glow` part, which v2_2 torches don't have, so it framed the pole and cut off the flame. It now also matches `_Flame`, and the close-up frames the whole flame.

## Hut colour (step 7): FAILED, no fix possible within the rules
- Rendered pixels at the pad 5 hut:
  - thatch about (251-255, 174-200, 19-31)
  - wood posts about (238,105,11) to (255,154,24)
  - Targets are wood 110-140 / 70-95 / 40-55 and thatch 200,165,90. The huts render clearly brighter and more saturated: blown gold and orange.
- Iteration 1: I set Color (205,190,165) live on the pad 5 hut. The rendered pixels were **identical**. The hut is a MeshPart with a TextureID (palette texture), and Color doesn't tint it, so the HUT_MUL path (part Color) has no effect.
- **Final HUT_MUL = nil** (unchanged). The test hut was rebuilt by the ltdr14 rerun.
- What actually blows it out is the scene grade: Brightness 2.6, ExposureCompensation 0.2, and ColorCorrection Saturation 0.1 / Contrast 0.08 / Tint (255,240,225). Those were off-limits here.

## Atmosphere (step 8)
- At the start (0.04 / 0.35 / 0.2, Decay 255,220,180) the overview had a strong salmon-pink band from the horizon down to the water edge.
- Haze 0.15 / Offset 0.05 alone was still pink.
- Changing Decay to (200,215,235) made the band neutral grey, with a clean horizon and a crisp island.
- **Final: Density 0.04, Haze 0.15, Offset 0.05, Decay (200,215,235), Color (255,225,190) unchanged, Glare 0.40.** Saved into `light14.luau`.

## Sun (step 9)
- Lighting:GetSunDirection() = (0, 0.552, 0.834): elevation 33.5 deg, azimuth +Z.
- Tee cameras are pitched -3.4 deg; the top of the 70-degree frame is at 31.6 deg, and the half horizontal FOV is about 47 deg.

| Pad | Forward azimuth | Sun angle off forward line |
|---|---|---|
| 9 | -86.8 | 86.8 |
| 10 | -84.6 | 84.6 |
| 11 | -116.5 | 116.5 |
| 12 | -106.5 | 106.5 |
| 13 | -120.3 | 120.3 |

- The sun is outside the view on all five pads, so **ClockTime stays 12.00** (before and after) with latitude 80 and elevation 33.5 deg.
- The sun disc does show in some back views (pads 7, 8, 14 back) and in torch_check_pad5. That is allowed.

## Visual review (step 11)

**(a) No eye-height ferns in back views of 3, 4, 5, 10, 11, 15, 16:**
- 3 PASS, 4 PASS, 15 PASS, 16 PASS: fern tops sit below the horizon.
- 5 PASS (marginal): one near-left fern blade reaches almost to the horizon.
- **10 FAIL**: a large leaf plant on the right rises well above eye height.
- **11 FAIL**: big broad leaves in the upper-left foreground are above eye height.
- Pad 2 and 9 back views have tall yellow grass in the lower half, but they are not on the list.

**(b) No yellow/orange rim-lantern blocks on 1, 4, 5, 8, 10, 12, 15, 17, 18; torches instead:**
- PASS. Tiki torches are visible in the front views of 1, 4, 5, 8, 10, 12, 15, 17 and 18, with no rim lantern blocks.
- Note: pad 1's back view (the wreck deck) shows two round yellow glowing balls, which are the ship's lanterns, not rim lanterns.

**(c) Pad 17 mound gone or far back, boulder piles in rock tint: PARTIAL.**
- The boulder piles are in rock tint with mossy tops.
- A low grassy hump is still visible mid-distance in the pad 17 front view, though no large mound faces the tee.

**(d) No big tan rock faces behind 16-18; pad 2 tan rock gone: PARTIAL.**
- Pad 2: PASS, the tan rock is gone and boulder piles are mid-distance.
- 16 and 17 show boulder piles (rock tint) plus a craggy grey-brown rock spire on the left of 16.
- 18 front still shows big tan-brown cliff faces on the left: the cave-mouth cliff set piece around Torch_CaveMouth.
- 17 front has a tan boulder overhanging the top-left.

**(e) No rock spikes on 7 and 9:** PASS.

**(f) Sun not behind the play line on 9-13:** PASS (geometry above; not in any front shot).

**(g) Low edge dressing along beach rails 2-8:** PASS. Fern and leaf clumps run along both rails on pads 2-8.

**(h) Jungle on 10-14 still dense, arches on 10 and 14, canopy walls, stepped backdrop, ridge green:**
- PASS for density, the ruin arch on 10 and the vine arches on 10-14.
- The canopy walls and layered backdrop show in the 10-13 front views and the overview.
- The ridge reads green in the overview, with brown cliff faces under the green.

**(i) Terrain rocks not dark-smudged:** PASS. Terrain rock reads mid brown-grey (pad 14 and 18 back views).

## Screens (~/stage/shots14/, 40 files, 1360x877, viewport only)
- `pad_1_v14.png` … `pad_18_v14.png`
- `pad_1_back_v14.png` … `pad_18_back_v14.png`
- `overview_v14.png`
- `jungle_v14.png`
- `torch_check_pad5_v14.png` (retaken after the final light change)
- `torch_closeup_v14.png` (about 10 studs; the flame fills a large part of the frame, so I didn't move the camera closer)

## Files changed
- `~/stage/dressing_v14.luau`: torch PointLight Range 10 → 14 and Brightness 1.2 → 2.0. HUT_MUL is still nil.
- `~/stage/chk14.luau`: expected torch light changed to 14 / 2.0.
- `~/stage/light14.luau`: Haze 0.15, Offset 0.05, Decay (200,215,235).
- `~/stage/cam_tcu.luau`: targets the `_Flame` part.
- `~/stage/shoot14.sh`: temp capture path moved to /tmp.
- `~/stage/vp14.env`: new.
- New copy folder: `/Users/chase-mini/sc14imp22fbx/` (FBX copies only).
- `~/src/vr-mini-golf-v2`: commit `09ea0af docs: add v14 deploys row` (not pushed).

## Problems / follow-ups
1. **Hut colours are blown** (thatch about 254,191,27, wood about 238,105,11). HUT_MUL can't fix this because Color does not tint textured MeshParts. It needs a grade change (Brightness, Exposure, ColorCorrection) or a darker palette texture. Both were out of scope for this job.
2. **The torch flame is lemon yellow, not orange, in daylight.** Neon 255,140,50 under this grade comes out as (255,232,0). It is close to the thatch hue. The fix is a flame colour or grade change, which was not allowed here.
3. **Two non-torch Neon parts:** `Workspace.World.Meshes.WreckV2.wreck_glow` (grey, 86x29x190) and `CaveV2.cave_glow` (190,80,25, transparency 0.3). Both are pre-existing from v13 and outside the dressing rebuild, so they were not changed. They break the "nothing Neon except torches and lantern glass" rule.
4. Back views 10 and 11 still have above-eye leaf plants. The jungle shrink cap missed some large leaf meshes there; they are probably not fernclump/leafclump.
5. **White halo outlines** show around tree silhouettes against the sky (pad 3, 4, 6 front; pad 12 back, most obvious). They look like a post-effect edge artifact, probably DepthOfField.
6. Near-camera translucent panels appear at the left edge of the pad 13 front and pad 18 front views, and at the top-left of pad 6 front. They are probably camera-fade or canopy geometry close to the tee cameras.
7. Pad 18 still has big tan-brown cave cliff faces in its front view.
8. Studio state:
   - The reopened place runs as a new process, pid 78191.
   - The previous Studio process (pid 62563) sits on the Start page with no place open.
   - The stale pid 18508 is untouched; MacBot owns that cleanup.
   - If Rojo is connected in the reopened session, it may sync the post-commit stamp (sha 09ea0af) into that edit session. That change would be unsaved and is not published.
9. Creator Hub Version History was not checked in a browser. The version number comes from the Studio log ("v14" quick link) and from the reopen loading `version=14`.
