# Stage au5 — Aurora Archipelago props_fix_overlap

Status: **FAIL VERSION_GATE** — content and tests pass; Aurora was published v6, but the task required v5.

## Preflight
No competing stage job or preexisting Studio application. Opened only the exact local `playtest/playtest-aurora_archipelago-v4.rbxl` through File > Open from File. One Studio session; Welcome, MetavrseBuilder visually verified. MCP: PlaceId 0, PlaceVersion 0, PlaceRole aurora_archipelago, Workspace.CourseAurora with Hole1–Hole18. Input SHA256 `7503424e4a5a3b4d2982942c7c428a6ac8005a274e94099b1615ccc421242737`. Creator Hub Show published only baselines: lobby 251, Sugarloaf 23, Lantern Grove 12, Aurora 4. Protected places were never opened in Studio. No Windows use.

## Import
All 12 supplied FBXs passed Blender merge round-trip validation: 37 meshes, 10903 triangles, maximum mesh 1596 triangles. All ten replacement hashes provided by the manifest match; H6/H18 source_sha256 values describe earlier inputs, so replacement hashes are independently recorded in import-specs.json. Source FBXs and manifest unchanged.

Imported `/tmp/stage_au5_props.fbx` through Studio's File > Import. Inventory Model upload unchecked; add to Workspace, scene position, scene-origin pivot and anchored enabled; cages and zero-influence bones disabled; scale unit Stud, scale factor 1. Child MeshIds were created by Studio. Each mesh was normalized to its actual source FBX bounds with the importer Y half-turn correction, then placed at manifest pivot_world/world_yaw with manifest materials. CanCollide/CanQuery/CanTouch all false. Exactly one original per prop was verified before replacement; originals and the staging model were removed. Batch-three kit and source bounds updated for future imports.

Replaced instance paths:
- `Workspace.CourseAurora.Hole6.Decor.h06_respawn_stone`
- `Workspace.CourseAurora.Hole18.Decor.h18_crystal_chute`
- `Workspace.CourseAurora.Hole2.Decor.h02_lintel_left`
- `Workspace.CourseAurora.Hole2.Decor.h02_lintel_mid`
- `Workspace.CourseAurora.Hole2.Decor.h02_lintel_right`
- `Workspace.CourseAurora.Hole2.Decor.h02_rookery_drift`
- `Workspace.CourseAurora.Hole10.Decor.h10_bobsled_hut`
- `Workspace.CourseAurora.Hole15.Decor.h15_lip_ice`
- `Workspace.CourseAurora.Hole10.Decor.h10_snow_walls_e`
- `Workspace.CourseAurora.Hole10.Decor.h10_snow_walls_w`
- `Workspace.CourseAurora.Hole15.Decor.h15_great_frozen_falls`
- `Workspace.CourseAurora.Hole18.Decor.h18_ramp_lanterns`

## Blockout and small fixes
Blockout retained **hidden**, because AuroraPropsBuilder still performs two presentation-only folder lookups. Its 135 BaseParts have no collision/query/touch, tags, scripts, spawn instances, or ObjectValue/joint references from elsewhere. No CourseBuilder/gameplay script reference was found. Decorative cup/flag/tee meshes are not the gameplay cup/spawn objects. Evidence: blockout-dependencies.json plus full collider inventory. All 68 previously visible Blockout parts are now transparent; all 135 remain noncolliding/nonqueryable/nontouchable. This hides h10_bank and duplicate h05/h12/h15 rails without deleting a referenced folder.

H14 safe_side_sign moved 0.28 studs outward (+world Z). Its board now clears the post by about 0.081 studs, and brass/glow/snow layers have about 0.081 vertical gaps. Rebased cached VisualSeparation poses so the finalizer cannot restore v4 overlaps. H6 respawn_stone is now 0.2 studs thick and clears the shelf collider by at least 0.081001 studs across its corners (center Y 84.056442). H5 retains both original Base colliders, hidden, with six untagged noncolliding visual pieces cut around the full geyser-mesh footprint; measured minimum clearance at least 0.08098 studs. The entire vertical travel corridor is clear. The visual cutout does not alter the mover or its gameplay colliders.

Cleanup is reproducible in AuroraVisualCleanup, invoked from CourseBuilder.ApplyVisualSeparation and AuroraEffects after imported decoration. VisualSeparation reran through the course build finalizer. Its final application reports 546 operations (207 minimum-thickness, 183 parallel exterior-face separations, 156 protected felt skins). These include idempotent reapplications of existing v4 fixes, not 546 newly introduced net changes. Zero unresolved, zero thin visible parts, zero invariant failures, 99 joints reconnected. Felt visual tops remain at original collider planes.

## Scan and physics evidence
| Category | Before | After |
|---|---:|---:|
| Coplanar faces | 1341 | 983 |
| Decorated coincident faces | 0 | 0 |
| Placeholder coplanar faces | 0 | 0 |
| Transparency candidates | 110 | 110 |
| Total | 1451 | 1093 |
| Exposed planar candidates | 0 | 0 |
| Imported mesh hits | 834 | 463 |
| Terrain candidates | 0 | 0 |

After geometry classifications: 523 non-planar/mesh-bounds candidates and 460 opposing/internal-interface reviews. They remain in the raw report; conservative mesh bounds are not treated as actual exposed polygon intersections. Full mesh-hit and per-hole lists retained. BaseParts 1845/1851; visible Workspace parts 993/929; Blockout parts 135/135 and visible 68/0. Placeholders 0/0.

All 615 whole-Workspace colliders/gameplay parts match the untouched v4 inventory exactly for path, CFrame, size, collision/query/touch, collision group, anchored state, current physical properties and custom physical properties. No collider or roll height changes. Before/after H10 and H2 screenshots: au5-before.png and au5-after.png. Targeted small-fix images and numerical checks are in playtests/stage-au5.

## Tests
Untouched v4 seeded 18-hole baseline PASS: 54 cups, 36 completed random shots, 0 stuck/escapes/timeouts; server/client console empty. Desktop smoke after changes PASS: arrival on Aurora H1, menu and finish return-to-lobby requests, real putt, zero server/client errors or warnings. Studio records the teleport requests; it never opened the lobby.

Final seeded 18-hole sweep PASS: 54 cups, 36 completed random shots, zero stuck/escapes/timeouts and empty server/client warning/error lists. Every hole matches the untouched baseline on cup count, completed-shot count, stuck, escapes and timeouts. Evidence: sweep-comparison.json. All 615 colliders were checked again after Play stopped and remain exact.

## Publication and version-gate failure
Performed exactly one File > Publish to Roblox As > VR Mini Golf > row named exactly Aurora Archipelago > Overwrite. The selected-row screenshot is au5-publish-target.png. Creator Hub Show published only and MCP confirmed **Aurora v6**, PlaceId **79649062523043**, PlaceRole aurora_archipelago. Evidence: au5-v6.png. No other row was selected or published.

The requested N=5 gate failed. After discovering v6, the unfiltered history showed a pre-existing **saved/unpublished v5 dated October 13, 2026 at 10:29 PM**, between published v4 (10:28 PM) and today's published v6 (October 14, 2:12 AM). This explains the version jump; no second publish, restore, or rollback was attempted. Evidence: au5-version-history-all.png. Published-only preflight correctly showed v4 but did not reveal that saved revision.

Saved the actual published local copy through File > Download a Copy: `playtest/playtest-aurora_archipelago-v6.rbxl`, 1,413,890 bytes, SHA256 `4bafc4a07182b732fa9df2ff14c3231ec6a7aa85e2e56ed03711128c077aa4af`. No v5 output is claimed.

Normal quit stalled on Applying script changes. No Escape; sent TERM, then KILL to the one Studio application process. Verified empty MCP Studio inventory and no Studio application process. Final read-only Creator Hub Show published only checks: lobby **251**, Sugarloaf **23**, Lantern Grove **12**, all unchanged; screenshots retained. No protected Studio place opened, no git push, no RBXL commit, and no unrelated tracked/untracked asset changes.

## Open items
Live headset/cross-place teleport checks were not performed. Conservative mesh-bounds and transparency candidates remain available for art review; exposed planar candidates are zero.

RESULT=FAIL VERSION_GATE AU_NEW=6 AU_SCAN=1451/1093/0 PLACEHOLDERS=0/0 SWEEP=54/36/0/0/0 BLOCKOUT=hidden
