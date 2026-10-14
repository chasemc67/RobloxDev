# Stage au6 — Aurora Archipelago H18 crystal banks and H6 respawn stone

Status: **PASS — Aurora published v8**.

## Preflight
No competing stage job and no Studio application at start. Launched exactly one Studio; Welcome, MetavrseBuilder visually verified. Opened only `playtest/playtest-aurora_archipelago-v6.rbxl` through File > Open from File. Input SHA256 `4bafc4a07182b732fa9df2ff14c3231ec6a7aa85e2e56ed03711128c077aa4af`. MCP verified PlaceId 0, role aurora_archipelago, and Workspace.CourseAurora with Hole1–Hole18. Creator Hub published-only baselines: lobby 251, Sugarloaf 23, Lantern Grove 12, Aurora 6. Aurora unfiltered latest was saved/unpublished **v7**, October 14 at 2:14 AM; screenshot `au6-history-all-before.png`. No protected place opened in Studio; no Windows use.

## H18 import
Both supplied fix_overlap2 FBX SHA256 values match the manifest. Blender merge round-trip PASS: 2 props, 4 meshes, 5552 triangles, maximum mesh 2322 triangles; bounds/materials unchanged by merge. Imported `/tmp/stage_au6_props.fbx` with au5 settings: inventory Model upload unchecked, add to Workspace, scene position, scene-origin pivot and anchored enabled; zero-influence bones and cages disabled; Stud, scale 1. Child mesh assets were created by Studio.

Normalized each mesh to actual source FBX bounds with importer Y half-turn correction, then manifest pivot_world/world_yaw and materials. Each replacement is noncolliding/nonqueryable/nontouchable. Exactly one original verified and replaced; no duplicates or staging model remain. Recorded old paths:
- `Workspace.CourseAurora.Hole18.Decor.h18_crystal_bank_ne_deco`
- `Workspace.CourseAurora.Hole18.Decor.h18_crystal_bank_sw_deco`

Updated AuroraBatch3 kit and source bounds for future imports while preserving au5 corrections. Supplied fitcheck reports 0 intersecting pairs, 0 coplanar triangle pairs, minimum component gap 0.0856, minimum component thickness NE 0.27 / SW 0.269. Evidence is retained with the supplied assets and import-specs/merge-report/props-imported JSONs.

## H6 visible layers
Numerical inspection of untouched v6 showed Lime's bottom already 0.080989 studs above the sloped felt, but Lime overlapped the visible Hazards.RespawnStone layer by 0.019260 studs. That cylindrical visual intersected the felt by 0.099732 studs. Both are noncolliding/nonqueryable/nontouchable presentation parts; RespawnStone references in source are visual creation/cleanup, not the ball respawn position.

AuroraVisualCleanup now stacks both existing visual layers above the unchanged shelf/felt. RespawnStone center Y 84.056442; Lime center Y 84.337440. Marker-to-support minimum normal gap **0.0809892193**, Lime-to-marker gap **0.0809982095**, Lime-to-felt/support minimum normal gap **0.3619580056**. Both minimum dimensions remain 0.2. Every cached ZF1BaseCF/BaseSize and existing ZF1MeshTerrainBaseCF/BaseSize is rebased. A second CourseBuilder.ApplyVisualSeparation run preserves the final numerical layer results exactly (`idempotence.json`). No gameplay collider or roll height changed.

## Finalizer, inventory and scan
Reran VisualSeparation through CourseBuilder.ApplyVisualSeparation. Default separation 0.08, minimum thickness 0.2; zero unresolved, zero thin visible parts, zero invariant failures, 99 joints reconnected. 545 reported operations (206 minimum-thickness, 183 parallel exterior-face separations, 156 protected felt skins) include idempotent reapplications, not 545 net new changes.

| Category | Before | After |
|---|---:|---:|
| Coplanar faces | 983 | 978 |
| Decorated coincident faces | 0 | 0 |
| Placeholder coplanar faces | 0 | 0 |
| Transparency candidates | 110 | 109 |
| Total | 1093 | 1087 |
| Exposed planar candidates | 0 | 0 |
| Imported mesh hits | 463 | 457 |
| Terrain candidates | 0 | 0 |

After geometric classifications: 518 non-planar/mesh-bounds candidates, 460 opposing/internal-interface reviews. All raw hits retained in zscan-before/after and model-bot-mesh-hits JSONs. Whole Workspace BaseParts 1851/1851, visible parts 929/929, placeholders 0/0. All **615** gameplay/collider parts match untouched v6 exactly for path, CFrame, size, collision/query/touch, collision group, anchored state, current physical properties, custom physical properties. Before/after composite images show both H18 banks and H6 stone (`au6-before.png`, `au6-after.png`).

## Tests
Untouched v6 seeded 18-hole baseline PASS: 54 cup drops, 36 completed random shots, zero stuck/escapes/timeouts; server/client warnings and errors empty. Final desktop smoke PASS: Aurora arrival, real putt, menu and finish return-to-lobby requests, zero errors/warnings. Studio records teleport requests without opening the lobby.

Final seeded 18-hole sweep PASS: **54 cups / 36 completed random shots / 0 stuck / 0 escapes / 0 timeouts**, server/client warnings and errors empty. Every hole matches the untouched v6 baseline on cups, completed-shot count, stuck, escapes and timeouts (`sweep-comparison.json`). All 615 collider/gameplay parts were checked again after Play stopped and remain exact. Import metadata triangle counts were synchronized to the actual four FBX meshes; this changes no geometry or gameplay.

## Publication
Performed exactly one File > Publish to Roblox As > VR Mini Golf > row named exactly Aurora Archipelago > Overwrite. Selected-row evidence: `au6-publish-target.png`. Creator Hub Show published only confirms **v8**, October 14, 2026 at 4:06 AM; `au6-v8.png`. MCP independently confirms PlaceId **79649062523043**, PlaceVersion **8**, role aurora_archipelago. The preexisting unpublished v7 explains the skip from live v6; no restore or second publish.

Saved through File > Download a Copy: `playtest/playtest-aurora_archipelago-v8.rbxl`, **1,419,081 bytes**, SHA256 `cce8088dd9e05039f86233c4e3fdd57b7a79edbfa533c57bc8aefceadc610b8a`. Untouched v6 input SHA256 remains unchanged.

Normal quit stalled on Applying script changes. No Escape; TERM then KILL to the sole Studio process. Confirmed no Studio application process and empty MCP Studio inventory. Final Creator Hub published-only versions: **lobby 251, Sugarloaf 23, Lantern Grove 12**, unchanged; screenshots retained. No protected Studio place opened, no Windows use, no git push, no RBXL commit, no unrelated asset modifications or commits.

## Open items
Live headset rendering and actual cross-place teleport checks remain external. Conservative mesh-bounds, internal-interface and transparency candidates remain in the evidence for review.

RESULT=PASS AU_NEW=8 AU_SCAN=1093/1087/0 PLACEHOLDERS=0/0 SWEEP=54/36/0/0/0 STONE_GAP=0.0809892193
