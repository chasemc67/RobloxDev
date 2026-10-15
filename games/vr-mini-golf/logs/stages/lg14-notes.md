# Stage lg14 (Claude Code): Lantern Grove H5 respawn-disc texture + H7 crook duplicates

Status: **PASS. Lantern Grove published v25** (Creator Hub Version History, "Show published only": 25, 19, 12, 9, ...; v25 = Oct 14 2026 11:40 PM). Evidence: `lg14-v25.png`, `lg14-history-all.png` (v20-v24 are Studio autosaves from this stage), `lg14-final-histories.png`.

Gameplay colliders: **all 396 gameplay parts (270 colliders) are identical to v19.** That covers path, CFrame, size, collide/query/touch, physics, group, anchored and custom physics, and it held before and after Play. Ball roll heights are unchanged. The only part change is −20 BaseParts: the four deleted crook models, 5 parts each.

## Preflight
- One Studio, on Lantern Grove (EditPlace 91438142503824), signed in as MetavrseBuilder (StudioService 1818120139). PlaceRole `lantern_grove`, PlaceVersion 19.
- The course root is **`Workspace.Course`, Hole1-Hole9.** Lantern Grove has 9 holes, so the sweep is 9 holes / 27 cups. The prompt's "Hole1-Hole18" and "54/54" figures are Sugarloaf's.
- **Matches published v19:** all 3805 parts are identical to lg13's final inventory (`playtests/stage-lg13-claude/inventory-after.json`), and so are the 396 gameplay colliders. Placeholders 0.
- No other stage job was running; only the ChatGPT/Codex desktop app was up, and it isn't a stage job.
- Published-only baselines: lobby 251, LG 19, SC 103, AU 13 (`lg14-preflight-histories.png`, `playtests/stage-lg14/preflight.json`).
- The macOS "sshd-session ... bypass the system private window picker" prompt never appeared. No permission prompt appeared and none was granted.

## A. Baseline (untouched v19)
- **Smoke:** flow PASS, putt 7.08. 0 server entries; only the 5 known UIBlox `FoundationProvider` warnings (`lg14-smoke-before.log`).
- **9-hole sweep, seed 20261014** (`tools/zf2_sweep.py`): **27/27 cups, 18 shots, 0 stuck, 0 escapes, 0 timeouts**. The client console has only the 5 UIBlox warnings (`sweep-before/`).
- **z-scan before:** 3097 total, **0 exposed**, the same as lg13's after scan.

## B. Changes
### 1. H5 respawn disc texture: **texture (top-face Decals)**, no fallback ring
- **Checked the UVs first.** `fix_zfight4/h5_respawn_stone.fbx` (Blender import) has **no UV layer**, so a SurfaceAppearance ColorMap can't map. Instead I used a **Top-face Decal** on the MeshPart `Hole5.Decor.Props.h5_respawn_stone.h5_respawn_stone__Slate` (0.79 × 0.206 × 0.79).
  - A MeshPart decal projects straight down over the bounding-box top. The texture is a square image with a disc and transparent corners, so the disc lines up exactly with no stretching (`lg14-after-h5.png`, top-down).
  - The 0.206 side band shows the edge pixels smeared vertically: a dark slate/moss band, visible at eye height.
- **Uploads** (Asset Manager > Import, as MetavrseBuilder):
  - `h05_disc_color.png` → image **127293087692817**, `Decal LG14DiscColor`, ZIndex 1.
  - `h05_disc_glow_mask.png` → image **126024788707354** (uploaded as given; not used directly, because a black/white mask has no alpha).
  - `h05_disc_glow_ring.png` → image **70908422415368**. Built from the mask: RGB = the colour map's average under the mask (255, 198, 100), alpha = mask. It is `Decal LG14DiscGlow`, ZIndex 2, `Color3` (2.5, 2.5, 2.5) overbright, so the ring and its 8 dots read brighter and warmer.
  - This is a **neon-ish look, not true emissive.** Decals have no emissive channel, and SurfaceAppearance emissive would need UVs.
- **VisualSeparation:** the disc is now a Top-decal carrier, but no felt top lies above it (its bottom sits 0.156 above the felt). So Apply gave it **no fix (lift 0)**.
  - Its CFrame and Size are bit-identical before Apply, after Apply, after Play and after the reopen (`h5-pose-*.json`).
  - The old stand-ins `Hazards.RespawnStone` and `Decor.bridge_respawn_stone` were left untouched.

### 2. H7 crook duplicates: **4 deleted**, src fixed
- `Hole7.Decor.Props.Dressing` held 4 `rail_lantern_crook` models. Each was an exact copy of its `Light_H7_rail_left_03/left_04/right_03/right_04` crook: the same rotation, **0.05 lower**, 5 parts, noncolliding, and **each with its own duplicate PointLight** (`h7-crooks-before.json`).
  - Nothing referenced them: no ObjectValues, joints or constraints, and scripts reach them only through PropsBuilder's generic Dressing build.
  - All 4 were deleted (`h7-crooks-deleted.json`). Hole7 now has 5 crooks, all under `Lights.Light_H7_*` with their lights.
  - The 5th source entry (right_02) was already skipped at build time (path/hole filter), so the place had no duplicate for it.
- **Source:**
  - Removed the 8 H7 `dressing` entries that duplicate pointLights posts: the 5 crooks, plus the 3 stakes lg13 deleted in-place. This is in `src/ServerStorage/CourseData/PropPlacements.luau`, pushed to Studio.
  - The cause is in `tools/props_to_lua.py`: a dressing instance with a `light_id` was emitted both as dressing and as the pointLight's post. The generator now drops rail_lantern light posts from dressing for `DEDUP_RAIL_LIGHT_HOLES = {7}`.
  - A regeneration reproduces the edited H7 block exactly. I compared only that block: the rest of the manifest has moved on since the last generation, through other bots' in-progress work, so a full regen wasn't committed.
- Screenshot: `lg14-after-h7.png`.

## C. VisualSeparation and verification
- `CourseBuilder.ApplyVisualSeparation(workspace.Course)` with gap 0.08 and min 0.2: 1144 fixes (idempotent reapplications; lg13 had 1148, and the 4 fewer are the deleted crooks), **0 unresolved, 0 thin, 0 invariant failures**, 93 joints reconnected.
- **Colliders same** (`collider-verification.json` after Apply; `collider-verification-final.json` after Play): 396/396 gameplay parts, 270 colliders, placeholders 0/0 with the same paths.
  - Apart from the 20 deleted crook parts, every other part is identical in path, cf, size, transparency and material, so separation moved nothing.
- Parts 3805 → 3785.

| z-scan (zf1_zscan.luau) | Before (v19) | After |
|---|---:|---:|
| Coplanar faces | 2719 | 2599 |
| Decorated coincident | 0 | 0 |
| Placeholder coplanar | 0 | 0 |
| Transparency candidates | 378 | 374 |
| **Total** | **3097** | **2973** |
| **Exposed planar candidates** | **0** | **0** |
| Imported mesh hits | 2683 | 2559 |
| Terrain candidates | 117 | 117 |

The drop is the deleted duplicate crooks, which were coincident with their twins' bounding boxes.

## D. Playtests
- **Smoke:** flow PASS, putt 7.36, **0 errors**, 0 server entries; only the 5 UIBlox `FoundationProvider` warnings (`lg14-smoke.log`). The runner prints FAIL only because of those 5, exactly as in the baseline.
- **9-hole sweep, seed 20261014:** **27/27 cups, 18 shots, 0 stuck, 0 escapes, 0 timeouts**. No hole differs from the baseline (`sweep-after/`, `sweep-comparison.json`). Client console: the 5 UIBlox warnings only.

## E. Publication
- File > Publish to Roblox (⌥P), one publish. Studio showed "Published. Playtesters can play now."
- **Creator Hub published-only shows v25** at 11:40 PM (`lg14-v25.png`). The unfiltered history (`lg14-history-all.png`) shows that v20-v24 are autosaves from 11:19-11:35 PM.
- **Incident:** after the publish I clicked the tab title to focus Studio. The title had shortened to "Lantern Grove ×", so the click hit **×** and closed the place.
  - Nothing was lost. The place had just been published, and there were no edits after it.
  - I reopened it (EditPlace). It was PlaceVersion 25, and its full inventory is identical to the post-Play final (`inventory-reopened.json`), decals included.
  - Nothing was edited or published after the reopen.
- **File > Download a Copy:** `playtest/playtest-lantern_grove-v25.rbxl`, 3,474,151 bytes, SHA256 `5f6abe225eb021a2fbd991e867af40991c2b99574134bde2bdb744ec86374ab0`. It was saved through `~/a_lg14save` and moved into place; the temporary folders `~/a_lg14imp` and `~/a_lg14save` were removed.
- **Studio quit normally:** ⌘Q closed the place, then ⌘Q on the start page. No prompts, and "Applying script changes" never appeared. No RobloxStudio process remains, only the StudioMCP helpers.
- **Final published-only:** LG 25; lobby 251, SC 103 and AU 13 are unchanged (`lg14-final-histories.png`). Lobby, SC, AU, 135374506016678 and the Windows PC were never opened or used.
- **New uploads** (none deleted or archived): images 127293087692817 (`h05_disc_color`), 126024788707354 (`h05_disc_glow_mask`, unused) and 70908422415368 (`h05_disc_glow_ring`).
- Other UI slips, none of which changed the place:
  - I clicked **Clear All** on the Asset Manager's Recent > Uploads list. That clears only the list; the assets are intact and their ids were read back via Copy AssetId.
  - One `cliclick` typing burst into the Asset Manager search lost focus and opened System Settings > Keyboard. I closed it without any change. A full inventory diff right afterwards (`inventory-check1.json`) was identical to the baseline.

## Tools (new/changed)
- `tools/lg14_stage.py`: the sc5/sc12 stage commands for `workspace.Course`: preflight, inventory, scan, verify, apply, run, shot, and a 9-hole sweep summary.
- `tools/props_to_lua.py`: `DEDUP_RAIL_LIGHT_HOLES` (H7) drops the duplicated rail-lantern posts from dressing.
- `tools/run_playtests.py`: `Studio()` tolerates a start-page entry with a null name.
- `src/ServerStorage/CourseData/PropPlacements.luau`: H7 dressing without the 8 duplicated rail-lantern posts.
- Skill `roblox-studio-mcp`: lg14 lessons (Asset Manager uploads, Copy AssetId, swallowed typing, the tab-close hazard, the start-page null entry, UV-less disc decals).

## Open items
- **H8 has the same duplication:** all 15 `Hole8.Decor.Props.Dressing.rail_lantern_crook` models duplicate their `Light_H8_rail_*` crooks (0.05 lower, each with a PointLight), so there are 15 extra lights.
  - They're out of scope here. To fix them: delete the 15, and add 8 to `DEDUP_RAIL_LIGHT_HOLES` (plus remove the H8 crook dressing entries).
- **Glow:** the ring is an overbright decal, not real emissive or bloom. True emissive needs a UV-mapped disc (art bot) with SurfaceAppearance emissive. The color decal also smears onto the disc's 0.206 side band.
- Not done: the `.rbxl` copy to the Linux box and a headset check.

RESULT=PASS LG_NEW=25 H5=texture H7_CROOKS_DELETED=4 SRC_FIXED=yes LG_SCAN=3097/2973/0 CUPS=27/27 SWEEP=18/0/0/0 SMOKE_ERRORS=0 (+5 UIBlox) COLLIDERS=same STUDIO_CLOSED=yes COMMIT=(this commit, see git log)

BUILD DONE, STUDIO CLOSED
