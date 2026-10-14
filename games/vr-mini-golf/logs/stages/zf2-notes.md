# Stage zf2 — Aurora and Lantern Grove visual separation

Status: PARTIAL — Aurora PASS, published v4. Lantern Grove FAIL at cloud-launch/preflight; not modified or published.

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
