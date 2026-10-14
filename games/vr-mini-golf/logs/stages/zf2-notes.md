# Stage zf2 — Aurora and Lantern Grove visual separation

Status: COMPLETE — Aurora PASS, published v4; corrected-gate Lantern Grove zf3 retry PASS, published v12. Earlier stopped attempts are retained below.

## Preflight
No competing stage job or preexisting Studio application. Launched one Studio and visually confirmed Welcome, MetavrseBuilder. MCP confirmed exactly one local Aurora session, Edit, PlaceId 0, role aurora_archipelago. No PC use.

Creator Hub histories verified published-only lobby 251, Sugarloaf 23, Lantern Grove 9, Aurora 3. Latest saved: lobby 251, Sugarloaf 24 (unpublished), Lantern Grove 11 (unpublished; 10 also unpublished), Aurora 3. Sugarloaf never opened in Studio; never accessed 135374506016678. The later unintended lobby launch is detailed below.

## Aurora
Input: `playtest/playtest-aurora_archipelago-v3.rbxl`, selected because latest cloud save is v3. Original hash is recorded in `playtests/stage-zf2/preflight.json`.

Before scan: coplanar 3175, decorated 0, placeholder 0, transparency 115; total 3290. Exposed planar candidates 818; imported mesh hits 1114; terrain 0.

Imported the two supplied props_fix_overlap FBXs through one merged FBX, using stage-am source bounds normalization and importer Y half-turn correction. Upload inventory Model unchecked, scene position/origin enabled, anchored enabled, cages disabled. Blender round-trip verified two props, three meshes, 1105 triangles, maximum 877 triangles, unchanged source inputs. Studio created child mesh assets as in earlier imports. Original model pivots retained: H6 [310.5,83.8696975708,441.75]; H18 [-241.5,222.25,-265]. No colliders or placeholders removed. Updated normalized kit and source bounds for future imports.

VisualSeparation applied: 276 thickness corrections, 183 parallel exterior-face separations, and 156 protected felt skins; 615 changes, 156 protected felt skins, 163 visual collider copies, 99 reconnected joints; zero unresolved, zero thin visible parts, zero invariant failures. All 614 course colliders and all 615 full-Workspace colliders retain exact baseline geometry and collision/query/touch/physical properties. Placeholder parts remain 0/0.

After scan: coplanar 1341, decorated 0, placeholder 0, transparency 110; total 1451. Exposed planar candidates 0. Remaining geometric candidates: 894 mesh/curved bounds, 447 opposing interfaces. Imported mesh hits 834; terrain 0. Per-hole audit and full before/after model-bot hit lists saved separately. Same-camera before/after evidence shows H7 exterior layers separated.

Desktop smoke PASS, zero server/client errors/warnings. 18-hole sweep PASS: 54 cup drops, 36 completed random shots, zero stuck/escapes/timeouts, zero server/client errors or warnings.

## Source persistence
CourseBuilder applies the rule after physics setup for Aurora/Lantern Grove. AuroraEffects applies it after final Aurora visuals/effects; AuroraPropsBuilder already invokes that path. PropsBuilder applies it after final Lantern Grove decoration. Existing Sugarloaf wiring retained. Source bounds updated for corrected H6/H18 props.

## Lantern Grove
Latest cloud history remains saved v11/published v9. Creator Hub Edit in Studio fell back to Download Studio. A direct documented Studio-protocol navigation was blocked by browser URL policy; that blocked link was not executed through another surface. Studio native Experiences was tried as a separate in-app route; clicking the experience opened its start place (lobby), not a place picker. Cancellation was too late. The wrong-place preflight stops this pass per AGENTS.md and roblox-minigolf-studio-build. No LG scan, apply, collider comparison, smoke, sweep, or publish was performed. No v11 versus v9 content comparison was possible. Source wiring is committed but not validated in LG. Scan/placeholder/prop-import categories for LG are NOT RUN, not zero.

## Publication
Aurora published to its exact existing row; Creator Hub published-only v4 and MCP PlaceId 79649062523043/PlaceVersion 4 verified. Saved `playtest/playtest-aurora_archipelago-v4.rbxl`, 1,376,246 bytes, SHA256 `7503424e4a5a3b4d2982942c7c428a6ac8005a274e94099b1615ccc421242737`. Normal quit stalled on Applying script changes; no Escape. TERM then KILL; no Studio process and empty MCP inventory verified before Lantern launch.

Final histories show lobby published v251 unchanged and Sugarloaf published v23 unchanged. Lobby now has saved-unpublished v252 at 10:33 PM after the unintended brief open/quit; no source push, geometry edit, Save or Publish command was issued in that session. The saved revision is an unexpected Studio side effect and has NOT been restored or published. The lobby window closed through normal quit; a remaining windowless Studio child was terminated with TERM, and no Studio application process remained.

No git push, RBXL commit, or asset-owner edits. Local Aurora v4 copy is on the Mini; no Linux transfer performed in this partial run. Live headset/cross-place teleport remain external checks.

RESULT=PARTIAL AU_NEW=4 LG_NEW=0 AU_SCAN=3290/1451/0 LG_SCAN=NA/NA/NA PROPS=2/2 LOBBY=251 SC=23

## Lantern Grove (zf3)

Status: **FAIL WRONG_PLACE** at the explicitly required identity gate. No build or publish performed.

No competing stage job or preexisting Studio application found. Launched one Studio, visually confirmed Welcome, MetavrseBuilder, then used File > Open from File to open the exact `games/vr-mini-golf/playtest-lg-v11.rbxl`. MCP reported one local session, PlaceId 0, PlaceVersion 0, and PlaceRole `lantern_grove`. However, `CourseLanternGrove` is absent both at Workspace root and in a full DataModel descendant-name search; the actual course root is `Workspace.Course`. The user's explicit gate required CourseLanternGrove to be present and instructed stopping on failure, so no alternative root was substituted or renamed. Evidence: `playtests/stage-zf2/lg/zf3-preflight.json`.

Creator Hub Show published only baselines, checked before and after: lobby **251**, Sugarloaf **23**, LG **9**, Aurora **4**, all unchanged. No protected place was opened in Studio. Studio quit normally without a save; MCP inventory is empty and no Studio application process remains. No PC use, git push, RBXL commit, or asset edits.

Counts per category before/after (coplanar, decorated, placeholder, transparency), exposed after, collider inventory, placeholder inventory, mesh-hit lists, screenshots, smoke, and hole sweep: **NOT RUN**, not zero. Top fixes: none applied. New published version/local output copy: none. LG remains published v9.

Open item: resolve the explicit CourseLanternGrove identity requirement against the supplied file's actual Workspace.Course root before a new build attempt. Source helper `tools/zf2_stage.py` also maps LG to Course, but that does not override this stage's explicit stop condition.

RESULT=FAIL WRONG_PLACE LG_NEW=0 LG_SCAN=NA/NA/NA PLACEHOLDERS=NA/NA


## Lantern Grove (zf3)

Corrected-gate retry, authorized fix-forward. Opened only `playtest-lg-v11.rbxl` through File > Open from File. One Studio, signed in as MetavrseBuilder; MCP verified Edit, PlaceId 0, PlaceRole `lantern_grove`, and `Workspace.Course` with Hole1–Hole9. No competing stage job. Creator Hub published-only baselines: lobby 251, Sugarloaf 23, LG 9, Aurora 4. Input hash and identity evidence: `playtests/stage-zf2/lg/zf3-retry-preflight.json`.

Before categories: coplanar 4738, decorated 0, placeholder 0, transparency 376; total **5114**. Exposed planar candidates **1050**: 873 within Course, 175 within World, and 2 at Course/World joins. Imported mesh hits 2916; terrain ray candidates 104.

Pushed current src. Exposed the existing visual finalizer through `CourseBuilder.ApplyVisualSeparation`, shared by CourseBuilder.Build and PropsBuilder.Place. The finalizer includes Lantern Grove’s `Workspace.World` in the same pairwise pass so scenery and course/scenery joins are fixed without rebuilding or replacing the existing colliders. VisualSeparation’s optional scenery root keeps this extension scoped; other course calls retain their existing single-root behavior.

Applied **1186 fixes**: 737 minimum-thickness corrections, 370 parallel exterior-face separations, and 79 protected felt skins. 79 visual collider copies, 93 joints reconnected, 267 scoped collider invariants, zero unresolved, zero thin visible parts, zero invariant failures. Independent whole-Workspace comparison verifies **all 270 colliders exactly unchanged**, including CFrame, size, collide/query/touch, collision group, anchored state, current and custom physical properties. Placeholder instances **0 before / 0 after**.

After categories: coplanar 2857, decorated 0, placeholder 0, transparency 351; total **3208**. Exposed planar candidates **0**, verified for every hole and World. Remaining geometry: 2598 mesh/curved bounding-box candidates and 259 opposing interfaces. Imported mesh hits 2803; terrain ray candidates 117. Raw terrain and transparency candidates remain reported, not treated as proven rendered z-fighting. Before/after mesh lists and per-hole audit are retained. Worst-overlap evidence is the welcome plaza/walkway junction, captured from the stored camera position before/after (`zf2-lg-before.png`, `zf2-lg-after.png`); viewport dimensions differ between captures.

Untouched-input nine-hole baseline: 27/27 cup drops, 18 completed random shots, zero stuck/escape/timeout findings, zero server/client warnings or errors. The older input harness’s completed shots are verified from shot-event telemetry rather than inferred from attempts. Updated desktop smoke PASS: real putt and menu/finish return-to-lobby requests, zero server/client warnings or errors.

Final nine-hole sweep **PASS**: 27/27 cup drops, 18 completed random shots, zero stuck/escape/timeout findings, zero server/client warnings or errors. Baseline/after comparison reports no new failures.

Published only via File > Publish to Roblox As > VR Mini Golf > exact existing Lantern Grove row > Overwrite. Creator Hub published-only **v12** and MCP PlaceId **91438142503824**, PlaceVersion **12**, PlaceRole `lantern_grove` confirmed. Evidence: `zf2-lg-v12.png`. Saved `playtest/playtest-lantern_grove-v12.rbxl`, 3,458,770 bytes, SHA256 `0b31865bbd722a1009e635fa5e647253e906334a375da063327f60730d683ce4`. Untouched input hash remains unchanged. Local copy is on the Mini; no Linux transfer performed in this stage.

Quit stalled on Applying script changes; no Escape. TERM then KILL closed the sole Studio application. Empty MCP inventory and no RobloxStudio process verified. Final Creator Hub published-only checks: **lobby 251, Sugarloaf 23, Aurora 4**, unchanged.

Open items: live headset rendering and actual cross-place teleports remain external checks; retained conservative mesh, terrain and transparency candidates remain review evidence. No PC use, git push, RBXL commit, or asset-owner file changes.

RESULT=PASS LG_NEW=12 LG_SCAN=5114/3208/0 PLACEHOLDERS=0/0
