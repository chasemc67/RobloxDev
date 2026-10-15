# Stage bd1 (Claude Code): SC H1 cactus + H10 chevrons v2, LG H5 disc texture + fx1 src push

Status: **PASS.** Sugarloaf Canyon published **v113** (from v109), Lantern Grove published **v36** (from v32). Lobby still **251**, Aurora still **17** (published only).
- **Gameplay colliders:** identical to the published base on both places. SC 736/736, LG 396/396 (path, CFrame, size, collide/query/touch, physics, group), after Apply and again after all Play sessions.
- **Cups:** SC 54/54, LG 27/27. 0 stuck, 0 escapes, 0 timeouts. Every hole matches the fx1 sweep.
- **Seams:** SC 0 visible (the same 19 raw mitre-corner samples as fx1), LG 0 (0 interior samples).
- **z-scan exposed planar:** 0 on both places.

## Preflight
- One Studio, one place at a time: SC first, then LG. Both opened via EditPlace and signed in as MetavrseBuilder (1818120139).
- **SC:** the first EditPlace hit "We could not join the Team Create session ... Server did not start [0]"; **Retry** opened it. There was also a BulkPluginAssetDetailsFetcher HTTP 500 popup (OK).
  - PlaceVersion 109, all 7502 parts identical to fx1's final inventory (`sugarloaf_canyon-open-vs-v109.json`).
  - Scripts = src except the known v103 drift (AuroraBatch3, PropPlacements byte-equal to `exports/sugarloaf_canyon-v103`).
- **LG:** PlaceVersion 32, all 3788 parts identical to fx1's final (`lantern_grove-open-vs-v32.json`).
  - Scripts: fx1 first-revision VisualSeparation/CourseBuilder plus the v25 data drift (AuroraBatch3, SugarloafCanyon, GolfTest byte-equal to `exports/lantern_grove-v25`), as fx1 recorded.
- Nothing needed reverting.
- **Viewport:** Studio's viewport was left in "iPhone 17 Pro" device emulation, which gave tiny captures. `StudioDeviceSimulatorService:StopSimulationAsync()` reset it; that's a Studio setting, not place content.

## (1) Sugarloaf Canyon v109 -> v113
One 3D Importer pass (Blender-merged `bd1_SC.fbx` = both FBX; `tools/merge_fbx_for_import.py`, PASS, SHA256 of both sources = manifests).
- Settings as sc12: not "Import Only as a Model", Upload, scene position, anchored, Stud/1 (`bd1-sc-import-settings.png`).
- **Placement:** sc10/sc12 frame, `root * CFrame.new(fbx_bounds centre) * RY(pi)`, Size = `tools/fbx_bounds.py` size.
- Importer bundle `bd1_SC` removed after placing.
- **Backups:** `ServerStorage.BD1Backup` holds the pre-change models. Library copies are in `ServerStorage.StageAFProps`.

### a. H1 lollipop cactus (placeholders_ph3)
- `Hole1.Decor.lollipop_cactus_1.lollipop_cactus_1` (Model, 4 MeshParts: Bubblegum F78FB3, Cactus 3E8E41, Cream F6E3C8, MintWhite F2F7F0).
  - SmoothPlastic, like the SC lollipop kit.
  - Root `CFrame.new(66, 18.2, -4548)`, yaw 0.
- **Collision:** the old placeholder (Arm/Cactus/Lollipop Parts) was CanCollide/Query/Touch false, so the new parts are false/false/false too, anchored, `VisualQueryDisabled`.
- **Old placeholder:** the 3 Placeholder parts are hidden (Transparency 1, `BD1ReplacedBy`), not deleted. The Placeholder model and Anchor are kept, so placeholders are still 175, now 24 visible.
- **Grounded:** the true render ground (`h01_ground_s11/s12__RedDirt` mesh, EditableMesh raycasts) is exactly y 18.200 under the base. The mesh bottom is 18.1, so it's sunk 0.1 as the manifest says.
  - The Terrain under it is 17.98, but it's covered by the ground mesh.
- Mesh ids: Bubblegum 71969986277447, Cactus 83792482017139, Cream 112914556974367, MintWhite 88663272065213.
- Shots: `bd1-sc-h1-cactus-before.png` / `-after.png` (player view | top-down), `bd1-sc-h1-cactus-after-close.png`.

### b. H10 chevrons v2
- `Hole10.Decor.h10_chevrons.h10_chevrons__ChevronGlow` at `CFrame.new(290, 114.2, -5278) * CFrame.Angles(0, pi, 0)`.
  - MeshId 116509854449908, CanCollide/CanQuery/CanTouch false, CastShadow off, SmoothPlastic FFB830.
  - The importer's SurfaceAppearance (emissive) was dropped.
- **Texture:** `h10_chevrons.png` uploaded via `upload_image` (localhost HTTP). It is byte-identical to the sc12 `h15_lip_chevrons.png`/`h10_chevrons.png` upload, so it deduplicated to image **91089251317155**. MeshPart.TextureID = rbxassetid://91089251317155.
- **Fit (EditableMesh vertices vs the chute felt plane):** tops +0.080/+0.081, bottoms -0.126 over the whole chute, which matches the manifest exactly. The chevrons point down the chute, the same way as the ONE WAY arrow.
- **Old H10 chevrons:** `chevron_1..4` placeholder arrows hidden (Transparency 1, `BD1ReplacedBy`), not deleted.
- **Separation:**
  - A MeshPart without Decal children was never moved by `Apply`.
  - To make that explicit, src `VisualSeparation` now skips any noncolliding part with attribute **`ZF1KeepPose`**, set on the chevron mesh.
  - After `ApplyVisualSeparation(CourseSugarloaf)` (1192 fixes, 0 unresolved/thin/invariant failures), the CFrame is bit-exact (max component diff 0, lift 0), so **lifted=no**.
  - Placed and after inventories are identical, so separation moved nothing.
- Shots: `bd1-sc-h10-chevrons-before.png` / `-after.png` (player view | top-down).

### SC checks
| | before (v109) | after |
|---|---|---|
| z-scan total / exposed | 8070 / 0 | 8066 / **0** |
| seams interior raw / visible | 19 / 0 | 19 / **0** (identical segments: fx1's mitre corners) |
| colliders | 736 | **736 same** (`sugarloaf_canyon-collider-verification-final.json`) |
| parts | 7502 | 7507 (+4 cactus, +1 chevron) |

- **Smoke:** flow PASS, putt 6.32, 0 server entries, client only the 5 known UIBlox `FoundationProvider` warnings (`bd1-sugarloaf_canyon-smoke.log`).
- **Sweep (seed 20261014):** 54/54 cups, 36 shots, 0/0/0, console empty. Differing holes vs fx1: none (`sugarloaf_canyon-sweep-comparison.json`).
- **H16 edge** (`tools/sc12_h16_edge.py`): **unchanged**. Lip stops 0/80, outside drops 0, slow putts 58/72 (sc12 54/57/58, fx1 56), puttsParked 2 (sc12 2/1/2), max fall Chebyshev 0.966, every rest-scan distance drops (`bd1-sc-h16-edge.log`).

## (2) Lantern Grove v32 -> v36
### a. H5 respawn disc (fix_zfight5_uv)
- **Import:** `h5_respawn_stone.fbx` (SHA256 = manifest), one importer pass, same settings (`bd1-lg-import-settings.png`).
  - The geometry is identical to the old disc (1033 vertices, max nearest distance 0.0000). The new mesh has UVs (1033).
- **Replacement:** a new `h5_respawn_stone__Slate` MeshPart at the old part's exact CFrame and Size (same parent, name, material, attributes and flags).
  - MeshId **75962065905773**.
  - TextureID = **103297586023250**, the `upload_image` of `h05_disc_color.png`. It didn't dedupe to lg14's Asset-Manager id 127293087692817.
  - The importer's own texture upload 134750749915251 isn't used.
- **Two-decal workaround removed:** the old part, with `LG14DiscColor` and `LG14DiscGlow`, is gone. 0 `LG14DiscColor` decals remain in the place, and no carrier parts existed.
- **Glow: KEPT.** With the texture only (`bd1-lg-h5-disc-try-noglow.png`), the amber ring reads dim. Re-adding the lg14 overbright ring decal (image 70908422415368, ZIndex 2, Color3 2.5) lines up exactly with the texture's ring and dots, and reads as the lit waypoint (`bd1-lg-h5-disc-try-glow.png`). It's kept as `LG14DiscGlow` on the new part.
- **Z-fighting / separation:**
  - The disc bottom is 0.156 above the felt (manifest, unchanged), so nothing is coplanar; z-scan exposed is 0.
  - After the final Apply the disc pose is exact (position diff 0, rotation same). The top-decal carrier above the felt isn't lifted.
  - The texture also fixes lg14's smeared side band: the rim now shows the slate/moss UV band.
- Shots: `bd1-lg-h5-disc-before.png` / `-after.png` (close | top-down).

### b. fx1 seam-fix source pushed to LG, with a bd1 source fix
- **Pushed** `src/ServerStorage/VisualSeparation.luau` and `src/ServerStorage/CourseBuilder.luau` (now byte-identical to src: `lg-scripts-final-vs-src.txt`), then `ApplyVisualSeparation(workspace.Course)`.
- **Problem found:** with fx1's final src, LG got **137 interior seam samples, two visible 0.16 dark lines** (H8 along x=3.01, z 12.3-18.8; H9 along the bank strip edge; `bd1-lg-seamcheck-h8.png` / `-h9.png`). v32's first revision had 0.
- **Cause:** fx1's side-face rule (#3). On H8 the flat felt (x 3-10) meets the H8 ramp felt (also x 3-10) end to end. Their side planes coincide only in a ~0.1-stud corner band at the joint. The rule pulled the flat felt's side in 0.08 on **both** sides, which opened its flush joint to the neighbouring felt at x=3. H9's 3.03-wide bank strips do the same.
- **Fix (`VisualSeparation.luau`, `feltJointCorner`):**
  - A felt-felt same-normal side-face coincidence is kept (exclusion `felt-joint-corner`) only when the overlap along the horizontal is a band of 0.25 or less **and** that side of the skin is a flush joint (inset 0.001). Pulling such a side would open the top joint.
  - Outer (inset 0.08) sides keep the normal pull, which only widens their hidden outer inset.
  - The first try exempted outer sides too. That gave 7 exposed coplanar side faces in the z-scan, which this version removed.
  - In LG it applies to 2 corners (H8, H9).
- **Result:** LG seams **0 interior** (`lantern_grove-seams-after.json`), z-scan 3078/0 -> **3074/0 exposed**, and `bd1-lg-seamcheck-h8-fixed.png` / `-h9-fixed.png` show no dark line.
- Separation: 1149 fixes, 0 unresolved/thin/invariant failures.
- **Skin changes vs v32 (`lantern_grove-skin-deltas.json`):** 0.001 setbacks at flush joints, plus about 10 outer-edge skins with a further ~0.08 inset (H1, H5 ridge pair, H8, H9). No collider changed.

### LG checks
- **Colliders:** 396/396 same (after Apply and after Play).
- **Parts:** 3788 = 3788 (disc part replaced in place).
- **Smoke:** flow PASS, putt OK, 0 server entries, client only the 5 UIBlox warnings (`bd1-lantern_grove-smoke.log`).
- **Sweep (seed 20261014):** 27/27 cups, 18 shots, 0/0/0. Client console = the 5 UIBlox warnings. Differing holes vs fx1: none.

## Publication
- **SC:** File > Publish to Roblox (System Events menu click), once.
  - Creator Hub published-only: **113, 109, 103, ...** (`bd1-sugarloaf_canyon-v113.png`, 12:56 PM; v110-112 are autosaves).
  - File > Download a Copy: `playtest/playtest-sugarloaf_canyon-v113.rbxl`, 5,454,609 B, SHA256 `7be3110f1df7a7dd2c1f1c586215912a5d02f9f7976df7e02a05ba0787ceb3e8`.
- **LG:** published once.
  - Creator Hub published-only: **36, 32, 25, ...** (`bd1-lantern_grove-v36.png`, 1:18 PM; v33-35 autosaves).
  - Copy: `playtest/playtest-lantern_grove-v36.rbxl`, 3,477,656 B, SHA256 `07bd65576997f102b2652acdcc113d3222285f7b614da697d5a80e99515ffd27`.
- **Studio:** quit normally with ⌘Q after each place. `pgrep -x RobloxStudio` was empty before LG opened and at the end. "Applying script changes" never appeared.
- **Final published-only:** lobby **251** (`bd1-lobby-published.png`), AU **17** (`bd1-aurora_archipelago-published.png`). Lobby, AU, 135374506016678 and the Windows PC were never opened.
- **macOS prompt:** the "Screen Recording" (`universalAccessAuthWarn`) prompt was on screen behind Chrome during the Creator Hub checks. It was never clicked and no Return was sent; all clicks were outside its rectangle. No permission was granted.
- **New uploads (none deleted or archived):**
  - **SC import:** model `bd1_SC` 108948606937895; MeshParts listed above, plus Asset Manager MeshPart assets 125610169210594 and 98758392936677. The importer also uploaded SurfaceAppearance images 133764822575391 and 92857755248005, which are unused.
  - **Chevron image:** 91089251317155 (deduplicated, existing).
  - **LG:** mesh 75962065905773, image 103297586023250 (`h05_disc_color.png`), and the importer's texture 134750749915251 (unused).
- **Temporary files removed:** `~/a_bd1imp`, `~/a_bd1save`, `/tmp/bd1srv` and its localhost HTTP server.

## Tools
- `tools/bd1_stage.py`: fx1_stage commands with SC v109 / LG v32 bases, writing to `playtests/stage-bd1`.
- `tools/bd1_shots.py`: paired player-view | top-down captures.
- `src/ServerStorage/VisualSeparation.luau`: `ZF1KeepPose` opt-out; `feltJointCorner` (flush-side end-to-end felt corners).
- Skill `roblox-studio-mcp`: bd1 lessons (localhost `upload_image`, importer frame, `ZF1KeepPose`, Team Create retry).

## Open items
- **SC script drift:** SC v113 has `ZF1KeepPose` but not `feltJointCorner`, which was found on LG after SC was published (one publish per place). AU v17 has neither.
  - The next SC/AU publish should push `VisualSeparation.luau`, re-apply, and re-run seams + z-scan.
  - The new rule only exempts flush-side corner pulls, and may also remove SC's 19 raw mitre-corner samples.
- **H10 chevron glow:** TextureID only (no emissive). The importer's emissive SurfaceAppearance was dropped per the brief.
- Not done: `.rbxl` copies to the Linux box, a headset check.

RESULT=PASS SC=v113 LG=v36 CACTUS=ok CHEVRONS=ok(textureId=91089251317155,lifted=no) DISC=ok(textureId=103297586023250,glow=kept) SEAMS=0/0 COLLIDERS=same CUPS=54/27 SMOKE_ERRORS=0 (+5 UIBlox) H16=unchanged STUDIO_CLOSED=yes COMMIT=(this commit, see git log)

BUILD DONE, STUDIO CLOSED
