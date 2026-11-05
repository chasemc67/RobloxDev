# Pirate Shipwreck v17b report

**Result: published, version 18 (v18 = v17 + kit_v2_5 rock cliff palette).** The place stays private. Nothing was spent, Team Create stays off, no Scripts were written through MCP, and no assets or Blockout parts were deleted or hidden. Pid 18508 was not touched: every input went to pid 34084, and the frontmost pid was checked before each one.

**The cliff still reads tan on pad 18.** The new palette is in and verified, but it only changes the small Sandy ledge tops. The big tan faces use rock cells that were already (115,100,92)-ish; the warm lighting renders them tan. See CLIFF.

## Preflight
- The MCP was on pid 34084. My marker `V17B_MARKER_4417` is in `..._20261101T120542Z_Studio_82146_last.log`.
- PlaceId 131316561222931; :8765 returned 200 (a python http.server serving ~/stage).
- The docks were back: Terrain Editor, Toolbox, Explorer, Properties, Autopilot, Rojo, Asset Manager. I closed them all. The viewport is full width again, so the vp14.env crop is unchanged (offset 277/2 still valid for ident15_ray).
- No Screen Recording prompt appeared.
- The baseline matched the v17 publish:
  - all chk16 bad counts 0; hash **288e6bfc**; terr16b as in v16b
  - sha c810f8d (Rojo had synced the v17 deploys commit into the session)

## 1. Hut re-check (no hut work)
| Hut | Mesh / TextureID | Color | Material | SA | children |
|---|---|---|---|---|---|
| Template `ServerStorage.KitV1.hut_leanto` | 131857226019693 / **108289367129276** | (255,255,255) | Plastic | none | 0 |
| Placed (-92.1,19.5,357.4) | same | (255,255,255) | Plastic | none | 0 |
| Placed (460.1,23.2,428.9) (pad 5) | same | (255,255,255) | Plastic | none | 0 |
| Placed (863.9,23.1,144.2) | same | (255,255,255) | Plastic | none | 0 |
| Placed (-153.7,32.7,-55.2) | same | (255,255,255) | Plastic | none | 0 |

`hut_closeup_v16.png` was retaken with cam_hut.luau. Readings are px.py 9x9 medians:

| Point | v17 (`hut_closeup_v17old.png`) | **v18 (`hut_closeup_v16.png`)** |
|---|---|---|
| Thatch (600,200) | (251,201,48) | **(251,201,48)** |
| Thatch (750,280) | (239,171,34) | **(238,171,34)** |
| Wood post (960,560) | (207,89,17) | **(207,89,18)** |
| Wood post (330,500) | (233,135,31) | **(233,137,31)** |
| Deck plank (640,700) | (135,58,22) | **(135,58,23)** |

The hut is unchanged, as decided. The grade was not touched.

## 2. Cliff palette (kit_v2_5, rock)
**Upload**
- `~/sc17imp25png/cave_cliff_rock.png` (sha1 bf3f6fe5…, 256x256) was uploaded from Studio with the Studio MCP `upload_image` tool. That uploads through the signed-in Studio session, so the asset is private to this account. The file was served from a copy at `~/stage/kit_v2_5_up/`.
- Returned **rbxassetid://104642093288682**.

**It is the Image id.** I read it back with `AssetService:CreateEditableImageAsync` + `ReadPixelsBuffer`:
- Size 256x256.
- Row 0 cells 0..7: (115,100,92) (94,82,76) (135,119,110) (106,94,88) (68,60,56) **(115,100,92) (115,100,92)** (150,130,120).
  - **Cell 0 at (16,16) = (115,100,92); cell 5 at (176,16) = (115,100,92); cell 6 = (115,100,92).**
- r1c0 (120,102,96), r2c1 (140,90,55), r3c0 (120,84,56).
- Every row-0 cell matches the PNG exactly.
- Id 104642093288681 gives AssetNotFound, so no Decal/Image pair needed resolving.

**Old textures for comparison** (same readback):
- 99336401497933 (lower) and 103734712397151 (upper) have the same row 0 except **cell 5 = (190,150,110) and cell 6 = (171,133,98)** (Sandy / SandyDk).

**Not verified:** I could not check the brief's "byte-identical to kit_v2_5/cave_cliff_upper_rock/cave_cliff_upper.png": no kit_v2_5 folder is mirrored on the Mini. Only the cave_v1/v2/v2_2 PNGs exist under ~/src/RobloxDev, and they differ, as expected.

**Change** (`~/stage/cliff17b.luau`, one ChangeHistory recording):

| Part | TextureID before | TextureID after | Color before | Color after |
|---|---|---|---|---|
| `Workspace.World.Meshes.CaveV2.cave_cliff_lower` (mesh 78593172579470) | 99336401497933 | **104642093288682** | (115,100,92) | (115,100,92) |
| `Workspace.World.Meshes.CaveV2.cave_cliff_upper` (mesh 105613407352521) | 103734712397151 | **104642093288682** | (163,162,165) | **(115,100,92)** |

Both are Plastic, with no SurfaceAppearance and no children. The terrain Slate mound and the grade were not touched.

**Rendered (cam_tf18, px.py 9x9 medians):**

| Point | v17 before (`cliff_pad18_before_v17b.png`, = `cliff_pad18_v17old.png`) | **v18 after (`cliff_pad18_v16.png`)** |
|---|---|---|
| Lit face (60,150) | (141,102,70) | **(143,102,68)** |
| Lit face (480,280) | (144,105,71) | **(146,105,70)** |
| Mid face (230,200) | (124,87,60) | **(125,87,58)** |
| Shaded face (380,250) | (99,68,49) | **(100,68,47)** |
| Shaded face (340,200) | (92,62,45) | **(93,62,44)** |
| Sandy ledge top (145,304), 5x5 | **(201,140,70)** (max pixel) | **(126,81,51)** |

- **New lit about (143,102,68), shaded about (100,68,47).** Only about 870 pixels changed by more than 20: the light-tan ledge tops left of the torch, now rock brown (`cliff18_beforeafter_v17b.png`, left = before, right = after).
- **Why the big faces stay tan:**
  1. I read the mesh UVs with EditableMesh, face-centre cell weighted by area:

     | Mesh | cell 4 (68,60,56) | cell 1 (94,82,76) | cell 2 (135,119,110) | cell 0 (115,100,92) | **cells 5+6** |
     |---|---|---|---|---|---|
     | cave_cliff_lower | 36% | 26% | 16% | 13% | **2.6%** |
     | cave_cliff_upper | 18% | 35% | 20% | 15% | **4.0%** |

  2. As a diagnostic I blanked lower's TextureID for one frame (Color (115,100,92), untextured), then restored it straight away and verified it. The faces rendered **(169,126,87) / (131,92,65)** (`cliff18_diag_notex_v17b.png`).
     - Textured is about 0.82x that on every channel, which matches cell 1 (94,82,76).
     - So neutral rock (115,100,92) itself renders tan under Brightness 2, the warm Outdoor/Ambient, the warm Atmosphere and contrast 0.05.
     - This is the same mechanism as the hut in v16b.
  3. **Making the pad 18 cliff read grey needs either a lighting/grade change or a cooler/darker rock palette across cells 0-4** (Game Art Bot / 3D Model Bot call). The swap of cells 5/6 alone is nearly invisible.

## 3. Pad 17 boulder and rock stacks
**a. Pad 17 boulder `Workspace.World.Dressing.Set2.boulder_pile` at (531.1,109.0,-356.3)** (ray-probed from cam_tf17 at (620,300) and (580,240)):
- MeshPart, size 72.3 x 44.4 x 45.0, Plastic, **Color (163,162,165)**, no SA.
- MeshId **rbxassetid://125422249289317**, TextureID **rbxassetid://99398462771678**. These are the same as the template `ServerStorage.KitV1.boulder_pile`; 18 placed copies in Set2 share them.
- **Palette = kit_boulder_pile.png.** Readback row 0:
  - (120,84,56) (92,62,40) (146,106,70) (140,90,55) (118,74,45) (168,118,74) (84,52,34) (176,140,86)
  - This is identical to `~/sc13imp/kit_boulder_pile.fbm/kit_boulder_pile.png` (the kit_v2_1 set imported at v13; v14 notes kit_v2_2 kept those 10 meshes identical).
  - Rows 1-2 are greens; row 3 is (115,100,92) (94,82,76) (135,119,110) (190,150,110) (206,168,124) (226,184,128) (200,160,106) (70,66,64).
- **UV use:** the brown row-0 cells are not used at all.
  - r3c0 (115,100,92) 36%, r3c1 (94,82,76) 19%, r3c2 (135,119,110) 12%: the rock cells.
  - r2c1 16%, r2c3 11%, r2c0 3%, r1c6/r1c7 4%: the moss greens.
  - The boulder therefore renders warm grey-brown, about (107,77,58) lit, from the same warm-light effect. Nothing was changed or uploaded.
- **Other pad 17 rocks**, all kit MeshParts, Color (163,162,165), Plastic:
  - Top-left tan rocks (208,162,99): `Dressing.Set.rock_l` at (420.1,101.1,-405.7) and (411.8,105.0,-430.4). Mesh 90962011535037, tex 89594025674791. UV: r3c0/c1/c2 rock cells 82%, greens 10%.
  - Left foreground: terrain Rock plus `Dressing.Front.rock_m` (393.5,81.0,-385.5). Mesh 97725724467287, tex 112793249103157; rock cells 82%.
  - Centre boulders: `Set2.boulder_pile` at (531,109,-356), (526,97,-313), (548,90,-289), (595,98,-319), (526,84,-251).
  - Also near the felt: `Front.rock_s` (mesh 89769197134592, tex 93472473571412), several `Front.rock_m` (e.g. (425,74,-301)), and `Walkways.StepStone` Parts (Slate, (132,128,106)).

**b. "Checkerboard rock stacks":**
- I looked through all pad_N_v16 / pad_N_back_v16 shots plus overview and jungle. The blocky checkerboard stacks are on the **pad 17 front (right edge)** and the **pad 9 front (right edge)**.
- ident15_ray probes:
  - pad 17: (1250,400), (1300,350), (1110,430), (1200,480), (1340,300), (1050,340)
  - pad 9: (1200,400), (1300,320), (1250,200)
- Both resolve to **`Workspace.World.Dressing.Set2.ruin_wall`**:
  - MeshPart, mesh **127133709792681**, tex **74097284487246**, 23.1 x 16.6 x 11.1, Color (163,162,165), Plastic.
  - The pad 17 copy is at (406.0,80.7,-313.1); the pad 9 copy is at (723.5,17.2,-93.5).
  - **Kit mesh `ruin_wall` = `kit_ruin_wall.fbx`** (`~/sc13imp/kit_ruin_wall.fbx`, kit_v2_1 set, imported at v13; not in models/kit_v1_import, which has only kit_stack_a/b/c).
  - Its palette is the shared kit palette (row 0 identical to the boulder's). Its blocks alternate between rock cells r3c1 (94,82,76) 33%, r3c2 (135,119,110) 29% and r3c0 (115,100,92) 23%, which is what reads as a checkerboard.
- **It is a kit mesh, so nothing was changed:** no Part hidden, no boulder clone. The Dressing hash stays **288e6bfc**.
  - Evidence shot: `ruinwall_pad17_v17b.png` (= `pad_17_v16.png`). Before/after are identical apart from cloud and foliage sway, because nothing changed.
  - The pad 10/11 front blocky arches are presumably `ruin_arch` (kit_ruin_arch.fbx, same set). I did not probe them.

## 4. Shots (`~/stage/shots14/`, 1360x877, viewport only, cursor swept out and parked at 1000,1075, halo.py = 0 on every shot)
I kept the previous files as `*_v17old.png` and then retook:
- `hut_closeup_v16.png` (cam_hut): unchanged.
- `pad_17_v16.png` (cam_tf17): 3511 px differ from v17, all clouds and foliage; rocks identical.
- `pad_18_v16.png`, `cliff_pad18_v16.png`, `panel_pad18_v16.png` (cam_tf18): Sandy ledge now rock.
- `pad_18_back_v16.png` (cam_bf18): sky and foliage shift only.
- `overview_v16.png` (cam_ov12): 1373 px differ, foliage only.

Evidence:
- `cliff_pad18_before_v17b.png`
- `cliff18_beforeafter_v17b.png`
- `cliff18_diag_notex_v17b.png` (texture blanked, restored)
- `ruinwall_pad17_v17b.png`

The camera is back to Custom, FOV 70, and LocalTransparencyModifier is nonzero on 0 parts.

## 5. Final checks, publish, reopen
**Pre-publish chk16 + hut16 + sig16b + terr16b, all green:**
- torches 14; flame, core, light and emitter bad all 0
- grey 0, other Neon 0
- meshparts 3333, instances 3958, pointlights 74, templates 34, no stray kit_
- clock 12, lat 80, bright 2.00, exp -0.30
- Atmosphere: density 0.040, offset 0.05, haze 0.15, glare 0.40; Color (255,235,210), Decay (190,150,110)
- ColorCorrection: sat 0, contrast 0.05, tint white. Bloom: threshold 1.1, intensity 0.35
- felt 18 / 0 bad; footprints 5 / 0; wreck_glow and cave_glow SmoothPlastic; backfill 3; huts 4 / 0 bad
- **sig16b rows 3622, desc 3707, hash 288e6bfc (unchanged)**
- terr16b: hump voxels Air / LeafyGrass 0.26 (edge) / Air; Rock region 286 Rock, 0 LeafyGrass
- both cliffs on 104642093288682, (115,100,92)
- http false, StreamingEnabled true

**BuildInfo:** `tools/stamp` was re-run and Rojo synced it (stampedAt 2026-11-01T12:20:12Z read back). **sha c810f8d4b37a820ec1d75994a8dc1a6a62912223 (HEAD at publish), dirty false.**

**Save and Publish** (File menu via System Events on pid 34084; frontmost verified):
- Save: `Saved new changes in "Pirate Shipwreck" to Roblox.` at 12:21:02.593Z.
- **Publish** (existing place, not Publish As):
  - `→ Add publish notes to v18`
  - `Published new changes in "Pirate Shipwreck" to Roblox.` at **2026-11-01T12:21:22.682Z = 04:21:22 AM PST**
  - Log: `~/Library/Logs/Roblox/0.745.0.7451137_20261101T120542Z_Studio_82146_last.log`

**Reopen:**
- File > Close Place closed with no prompt (Start page). Then I ran `open roblox-studio:1+launchmode:edit+task:EditPlace+placeId:131316561222931+universeId:10771778371`.
- New **pid 61461**, log `..._20261101T122155Z_Studio_343b7_last.log`. The line `DataModel Loading https://assetdelivery.roblox.com/v1/asset/?id=131316561222931&version=18` came at 12:21:59Z. **Reopen version = 18.**
- The MCP is on it (marker `V17B_MARKER_REOPEN_8823` is in that log).
- chk16, hut16, sig16b, terr16b and the cliff state on the reopened place are **identical** to the pre-publish results (hash 288e6bfc, sha c810f8d, stampedAt 12:20:12Z).

**Deploys row:** `~/src/vr-mini-golf-v2` commit **2c88454 `docs: add v18 deploys row`** (not pushed). It is inserted after the v17 row: "v18 = v17 + kit_v2_5 rock cliff palette". I re-stamped afterwards (BuildInfo sha 2c88454, gitignored). If Rojo connects to the reopened session, it may sync sha 2c88454 into it. That change would be unsaved and unpublished, as in earlier rounds.

## Problems / follow-ups
1. **The pad 18 cliff still renders tan** (about (143,102,68) lit / (100,68,47) shaded). The kit_v2_5 swap of cells 5/6 only affects about 3-4% of the cliff surface. The rest uses rock cells that the warm lighting renders tan; the same holds for the boulders, rock_l/m and ruin_wall. The fix is lighting/grade, or cooler and darker rock cells 0-4 across the kit palettes. Not touched here.
2. **Upload path:** I used the Studio MCP `upload_image` tool, not the Asset Manager / File > Import Image GUI. It is still a Studio-session upload, private to this account, and the readback confirms an Image asset.
3. **kit_v2_5 byte-identity not checked:** no kit_v2_5 copy is mirrored on the Mini.
4. Once, after a cursor sweep, the edit camera read `Fixed` instead of `Custom`. I re-set it to Custom / FOV 70 and it held before the publish.
5. **Studio state:**
   - The v18 place is open in **pid 61461** (MCP on it; its default docks are probably back).
   - Pid 34084 is on the Start page after Close Place. Pids 30033, 62563, 78191 and 93578 are as before.
   - 18508 untouched.
   - :8765 is still up. `~/stage/kit_v2_5_up/cave_cliff_rock.png` is a copy of the uploaded PNG.
6. **Creator Hub Version History was not checked in a browser.** The version comes from the Studio log ("v18" quick link) and the reopen loading `version=18`.

DONE_V17B
