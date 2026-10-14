# Stage au7 (Claude Code): Aurora Archipelago H7 mogul trim, H18 ramp lantern cage, separation

Status: **PASS. Aurora Archipelago published v13** (Creator Hub Version History, "Show published only": 13, 8, 6, 4, 3, 2; v13 = Oct 14 2026 11:35 AM). Evidence: `au7-v13.png`, `au7-history-all.png`.

## Preflight
- One Studio, opened from the cloud on Aurora Archipelago (EditPlace 79649062523043, universe 10769274294), signed in as MetavrseBuilder (StudioService 1818120139). MCP: PlaceRole `aurora_archipelago`, PlaceVersion 9 at open.
- **Course root:** `Workspace.CourseAurora` (Folder, Hole1-Hole18). Workspace children: CourseAurora, Terrain, SpawnLocation, Camera.
- **Matches published v8:** the whole-Workspace inventory is identical to au6's final inventory (= v8), 1851/1851 BaseParts field for field, 615 gameplay parts, 0 placeholders. The z-scan total is 1087, the same as au6 after. AU v9 (4:07 AM) is an unpublished save made just after the v8 publish.
- No other stage job (`pgrep -fl "claude -p"` empty).
- Creator Hub published-only baselines: lobby 251, LG 19, SC 34, AU 8 (`au7-preflight-au-published.png`, `playtests/stage-au7/preflight.json`).
- The macOS "com.apple.sshd-session ... bypass the system private window picker" prompt was up the whole stage and was never answered. One focus click landed on the prompt's text, which made Allow the default button. I sent no keys, clicked an empty Studio panel to move focus back, and checked the screenshot before any keystroke.

## Imports (3D Importer, one pass)
- Both FBX SHA256 values match their manifests (overlap3 `74a70da8...`, overlap4 `1c7b27ca...`). The fitchecks report 0 intersecting pairs, 0 coplanar triangle pairs and 0 thin parts. Rail clearance: trim 0.30, cage 0.157.
- Blender merge `/tmp/au7/stage_au7_props.fbx` (`merge_fbx_for_import.py`) PASSED: 2 props, 6 meshes, 3336 tris, max 2240 (`playtests/stage-au7/merge-report.json`).
- Importer settings (au5/au6/lg13): Import Only as a Model off, Upload on, Add to Workspace, Insert Using Scene Position, Set Pivot to Scene Origin, Anchored, cages and zero-influence bones off, Stud, scale 1 (`au7-import-settings.png`, `au7-import-geometry.png`). The importer auto-scaled the scene (about x73.7). `tools/au7_props.py` rebuilds each mesh from the true FBX bounds (`fbx_bounds.py`) with the Y half-turn undone.
- Placement: the manifests carry no CFrames, so the placement comes from the props' approved pivot records: h07 `props_batch1_manifest.json` pivot_world (365, 112, 308), yaw 0; h18 `props_batch3_manifest.json` pivot_world (-243.9, 224.9, -265), yaw 0. Before replacing, the script asserted that each live model pivot equals that record. Colour, material, transparency and cast shadow come from the live part with the same name. CanCollide, CanQuery and CanTouch are off, plus `VisualQueryDisabled`.
- Replaced exactly once each, with no duplicates and the staging model deleted (`playtests/stage-au7/imported.json`):
  - `Workspace.CourseAurora.Hole7.Decor.h07_mogul_trim`: Snow 7.4 x 0.206 x 27.8 at y 113.497, Timber 7.4 x 1.158 x 27.8 at y 112.729. Before: 9.0 wide over the rails.
  - `Workspace.CourseAurora.Hole18.Decor.h18_ramp_lanterns`: the Glow cube is now 0.206 x 0.206 (was 0.366 x 0.397) inside the new Brass corner-bar cage. Brass, Snow and Timber bounds are unchanged.
  - Kit: `ServerStorage.AuroraBatch3Kit.h18_ramp_lanterns` was replaced too. No kit copy of h07 exists.
- `src/ServerStorage/CourseData/AuroraBatch3.luau`: the h18_ramp_lanterns Glow bounds and tri counts now match props_fix_overlap4 (Brass 492, total 792).

## VisualSeparation and verification
- First I pushed all of `src` (Studio lacked lg13's committed EntryRing change in CourseBuilder and the optional `scenery` argument in VisualSeparation, which does nothing when nil). Then `CourseBuilder.ApplyVisualSeparation(CourseAurora)`: gap 0.08, min 0.2, 544 operations (idempotent reapplications; au6 had 545 because the old trim Snow needed thickening), **0 unresolved, 0 thin, 0 invariant failures**, 99 joints reconnected (`fixes.json`). None of the operations touched the new trim or cage parts.
- ZF1 poses: ZF1BaseCF stores each part's pose from before separation. The new parts were never offset, so they have no cached pose, and nothing else moved. No rebase was needed.
- **Colliders: same.** All 615 gameplay parts are identical to untouched v8 (path, CFrame, size, collide/query/touch, physics, group, anchored, custom physics), and still identical after the Play sessions (`inventory-final.json`). Rails are unchanged. Placeholders 0/0. Workspace BaseParts 1851 -> 1851. Only 3 parts differ: trim Snow, trim Timber and lantern Glow.

| z-scan (zf1_zscan.luau) | Before (v8) | After |
|---|---:|---:|
| Coplanar faces | 978 | 908 |
| Decorated coincident | 0 | 0 |
| Placeholder coplanar | 0 | 0 |
| Transparency candidates | 109 | 109 |
| **Total** | **1087** | **1017** |
| **Exposed planar candidates** | **0** | **0** |
| Imported mesh hits | 457 | 387 |
| Terrain candidates | 0 | 0 |

Scan hits involving the trim or cage went from 70 to 0. After classes: 448 non-planar or mesh-bbox candidates and 460 opposing-interface reviews (the same 460 as before).

## Playtests
- Smoke on untouched v8 PASS (`smoke-before.log`). Final smoke PASS: real putt 7.3 studs, 0 server/client errors or warnings (`au7-smoke.log`).
- 18-hole sweep, same seed (20261014). **Baseline v8: 54/54 cups, 36 shots, 0 stuck, 0 escapes, 0 timeouts. After: 54/54, 36, 0, 0, 0**, console empty both times. Every hole matches (`sweep-comparison.json`).

## Publication
- File > Publish to Roblox (⌥P), one publish, to the open place. Creator Hub published-only shows **v13** at 11:35 AM. v10-v12 are Studio cloud saves from this session (11:09-11:25 AM), and v9 predates the stage.
- File > Download a Copy: `playtest/playtest-aurora_archipelago-v13.rbxl`, 1,422,186 bytes, SHA256 `c662d2674959315f00c329129e8b33c0b979e0673933424fd1c5cb33a8041352`.
- Studio quit normally (⌘Q, no prompts). No RobloxStudio process remains.
- Final Creator Hub published-only: **lobby 251, LG 19, SC 34 unchanged** (`au7-final-histories.png`); AU 13. Lobby, LG, SC, 135374506016678 and the Windows PC were never opened or used.

## Open items
- **Persistence:** the H7 trim lives only in the place. It is a props_batch1 asset with no `src` spec, so a fresh batch-one build would bring back the old 9-wide trim. H18 is covered by AuroraBatch3.luau and the kit.
- The importer also uploaded a `stage_au7_props` Model asset (103673756315476), as in earlier stages. It is unused.
- Not done: the `.rbxl` copy to the Linux box and a headset check (the H7 trim now sits 0.30 inside the rails; the H18 cage bars are visible around the glow).

RESULT=PASS AU_NEW=13 ROOT=Workspace.CourseAurora AU_SCAN=1087/1017/0 CUPS=54/54 SWEEP=36/0/0/0 SMOKE_ERRORS=0 COLLIDERS=same
