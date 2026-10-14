# Stage sc9 (Claude Code): Sugarloaf Canyon look7 dressing edgefix4 -> v49fix_thin60 + LODs

Status: **PASS. Sugarloaf Canyon published v63** (Creator Hub Version History, "Show published only": 63, 57, 49, 42, ...; v63 = Oct 14 2026 3:48 PM). Evidence: `sc9-v63.png`, `sc9-final-histories.png`. Dressing (visual) only. Every gameplay collider is identical to v57.

## Preflight
- One Studio, on Sugarloaf Canyon (EditPlace 124440050576723), signed in as MetavrseBuilder (StudioService 1818120139). MCP: PlaceRole `sugarloaf_canyon`, PlaceVersion 57 at open.
- **Matches published v57:** all 707 gameplay parts identical to sc8's `inventory-final.json` (= `collider-verification-final.json`), 7980/7980 parts, placeholders 175 / 36 visible, same paths (`preflight-vs-sc8.json`).
- No other stage job (only this `claude -p` sc9 job; the cursor-agent workers and the ChatGPT codex exec-server are not stage jobs).
- Creator Hub published-only baselines: lobby 251, LG 19, SC 57, AU 13 (`sc9-preflight-sc-published.png`, `sc9-preflight-histories.png`, `playtests/stage-sc9/preflight.json`).
- The macOS "com.apple.sshd-session ... bypass the system private window picker" prompt was up the whole stage. I never answered it and sent no Return key. No permissions were granted.

## A. Baseline (untouched v57)
- **Smoke:** flow PASS (arrival, menu > lobby, finish > lobby, real putt 7.38). 0 server entries. **5 client warnings, all from Roblox's own CorePackages:** `[UIBlox - Warning] FoundationProvider not found`. A second run on the same untouched place gave the same 5 (`sc9-smoke-before.log`, `sc9-smoke-before2.log`). sc8 had none, so this is new engine noise (Studio 0.743.0.7431133), not a game script and not this stage.
- **18-hole sweep, seed 20261014:** 54/54 cups, 36 shots, 0 stuck, 0 escapes, 2 timeouts (H15), console empty (`sweep-before/`). This is identical to sc8's after sweep.
- **z-scan before:** 8068 total, 0 exposed planar (`zscan-before.json`). This equals sc8's after scan.

## B. Changes (`tools/sc9_place.py`, `tools/sc9_plan.py`, `tools/sc9_mesh_geom.py`)
### 1. Remove the old dressing and place v49fix_thin60
- **Removed:** `Workspace.CourseSugarloaf.Look7Dressing`, 20 piece folders, **1,423 models / 3,516 MeshParts** (all edgefix4 pieces that sc8 left). Nothing was backed up.
- **SC7Kit:** 54 → 51 templates. I removed the 3 templates the new layout doesn't use: `red_dirt_patch_v2b__RedDirtLight`, `tunnel_lanterns_post2__Iron` and `__NeonAmber`. The H2 lanterns are clones and don't reference the templates.
- **Final set:** `instances` in `layout_look7_dressing_v49fix_thin60.json` has **1,281 entries**, and this is the final set.
  - The other keys are logs of how it was derived. `generated` = "v49fix_thin60". `thin60.input` = v49fix and `thin60.kept` = 1281 (v49fix kept 1393, then thin60 deleted 112 far pieces). `v49fix.input` = edgefix4: 1832 − 409 buried fillers − 30 felt/rail = 1393, with 162 floaters already lowered.
  - So nothing from the edgefix* sections is added back.
- **Kit meshes:** all 21 source FBX in `piece_files` are **byte-identical (SHA256) to the files sc7 imported** into SC7Kit (`/tmp/sc7/sources.json`).
  - 13 also match their manifest SHA256. The 4 main-kit pieces and the 4 cliffT pieces have no SHA in their manifests, as in sc7.
  - So every source mesh is still imported exactly once (the SC7Kit templates). Only the LODs were new.
- **Placement:** as `models/manifest.json` / sc7. `CFrame.new(pos + (0,0,-5000)) * Angles(0, rad(yaw), 0)`, per-axis `scale` on every MeshPart Size and on its offset from the pivot. Each MeshPart is at `root * CFrame.new(center * scale) * RY(pi)`, using the merge-report bounds.
  - **1281/1281 placed, 3,031 MeshParts.** Every pivot was checked against the layout: max position deviation 0.0003, yaw 2e-5°.

### 2. LOD (`look7_dressing_lod/manifest.json`)
- **Import:** all 9 `*_lod.fbx` match their manifest SHA256. They were merged with `sc5_merge_fbx.py --split-materials` into `sc9_LOD.fbx`: 39 meshes, 5,315 tris, max 676, round-trip PASS (`merge/`).
  - Per stem, the tris equal the manifest `tris_lod`. The material slots equal the source's slots, and the bounds match the source within the art bot's re-fit.
  - One 3D Importer pass, same settings as sc6-sc8: Import Only as a Model off, Upload on, Add to Workspace, Insert Using Scene Position, Set Pivot to Scene Origin, Anchored, cages off, No Rig, Stud, scale 1, polygon count 5315 (`sc9-import-settings.png`, `sc9-import-geometry.png`). The importer scaled by about x100. The templates were rebuilt from the merge bounds with the Y half-turn undone, into `ServerStorage.SC9LODKit` (39 templates). The `sc9_LOD` bundle was removed.
- **Same pivot / appearance:** each LOD part uses the same report frame as the source (FBX origin). It copies the source template's material, colour, variant, transparency, reflectance, CastShadow and attributes for the same slot.
  - Texture rule as sc7: the LOD importer's own texture when it has one (it matches the LOD UVs), otherwise the source template's (`lod-templates.json`).
- **Rule:** nearest hole = the hole whose felt is nearest in plan to the instance pivot. **LOD when the plan distance to that hole's tee is > 60** (tees = hole origins, checked against the `HoleN.Tee` parts) and a LOD mesh exists.
  - Each instance also records its min distance to any tee and its distance to the H1 tee (`dressing-check.json` `perInstance`, `lod.json`).
- **222 LOD placed, 221 kept** (one LOD cactus failed the float rule). Their distance to their own tee is 60.1-128.7, and to the H1 tee at least 62.2 (median 569).
- 41 kept pieces are within 60 of the H1 tee.

### 3. Part settings
- Every dressing MeshPart is set to RenderFidelity Automatic, Anchored, CanCollide/CanQuery/CanTouch off, `VisualQueryDisabled`, Massless and CollisionFidelity Box.
- CastShadow comes from the template, which is sc7's setting.
- All 3,012 final parts were checked; 0 violations.

### 4. Verify and enforce (`playtests/stage-sc9/dressing-check.json`)
- **Footprints are true mesh footprints, not bounding boxes.** Per mesh slot, the XZ convex hull of the FBX vertices (`sc9_mesh_geom.py`), with the instance frame and scale applied. All 90 slot hulls match the merge-report bounds within 0.01.
- **(a) Felt:** checked against the plan polygons of all 205 GolfSurface parts (Felt, CupPlate, the H7 island stone collider, mover decks at their edit pose). **0 overlaps**; the nearest pivot is 2.6 from felt.
- **(b) Rails:** checked against all 322 `Geometry.Wall` parts, plan distance. **0 under 1 stud**; the closest is 1.125.
- **(c) Float:** each piece's contact ring is the stem's lowest vertices (within 0.05 of the lowest point, up to 16 points).
  - Ground is Terrain plus every visible non-dressing part. The 3,153 visual parts with CanQuery off were query-enabled for the check and then restored; the inventories confirm all flags are unchanged.
  - A ray goes down from lowest + 5. A piece floats when every ring point is more than 0.1 above its ground.
  - **4 float.** `boulder_scatter_v2_265` (H7, gap 1.51), `lollipop_cactus_a_v2_432` (H11, 0.32), `lollipop_cactus_a_v2_444` (H11, LOD, 0.23) and `lollipop_cactus_a_v2_433` (H11, 0.18), all over Terrain.
  - Of the rest, 30 sit within 0-0.1 and 1,247 are sunk.
- **Deleted: DEL_FELT 0, DEL_RAIL 0, DEL_FLOAT 4** (ids 265, 432, 433, 444; 19 MeshParts). Nothing was moved. **Final: 1,277 pieces / 3,012 MeshParts.**

### 5. Triangles (`tools/sc9_tris.py`, `tris-before.json`, `tris-after.json`, `mesh-tris.json`)
- **Method:** exact, not estimated. Every MeshId in the place (1,543, plus the 39 LOD ids) was counted with `AssetService:CreateEditableMeshAsync` and `#GetFaces()`. The Studio Look7 total before (910,790) equals the modelled edgefix4 non-filler tris exactly, and the LOD ids equal the manifest `tris_lod`.
- Visible = a Workspace MeshPart with Transparency < 1. The camera is at the H1 tee + 5 up (60, 22.98, -4530), and distance is measured to each part's bounding box.
- **View distance:** StreamingEnabled is off and FogEnd is 100000 (Atmosphere density 0.38). So nothing is culled by distance, and the whole place (farthest part 3,508) is within view distance. RenderFidelity Automatic engine LOD is not counted.

| Visible mesh tris from the H1 tee | Before (v57) | After |
|---|---:|---:|
| within 60 | 85,984 | 85,626 |
| within 120 | 170,152 | 144,249 |
| within 250 | 416,788 | 341,278 |
| within 500 (whole course) | 761,291 | 662,143 |
| **all = view distance (= whole place)** | **1,906,158** | **1,627,586** |
| of which Look7 dressing | 910,790 | 632,218 |
| of which other meshes | 995,368 | 995,368 |
| + primitive parts (approx.) | ~63k (1,142 parts) | ~63k |

- **TRIS_H1 = 1.628M against the 1.08M target: not met** (−279k, −15%).
- The art bot's 1.077M model assumed 0.778M non-Look7 and counted Look7 at 0.656× its modelled tris. Studio counts Look7 at 1.0× its modelled tris, and the non-Look7 meshes alone are already 0.995M.
- Within 500 studs (the course) it is 0.66M.
- **Parts:** 7980 → **7476** (−3,516 old dressing, +3,012 new).

## C. VisualSeparation and verification
- `CourseBuilder.ApplyVisualSeparation(CourseSugarloaf)`: gap 0.08, min 0.2. **1204 fixes, the same set as sc8** (882 targets, by name and change), 0 unresolved, 0 thin, 705 collider invariants, 0 failures, 171 joints.
- **Colliders: same.** All 707 gameplay parts are identical to v57, after separation and again after all Play sessions (`collider-verification.json`, `collider-verification-final.json`). Rails are included.
  - All 4,464 non-dressing parts are present with unchanged collide/query/touch flags.
  - Placeholders 175/175, 36 visible, same paths.

| z-scan (zf1_zscan.luau) | Before (v57) | After |
|---|---:|---:|
| Coplanar faces | 7293 | 7138 |
| Decorated coincident | 61 | 61 |
| Placeholder coplanar | 16 | 16 |
| Transparency candidates | 698 | 632 |
| **Total** | **8068** | **7847** |
| **Exposed planar candidates** | **0** | **0** |
| Imported mesh hits | 7355 | 7134 |
| Terrain candidates | 131 | 131 |

- Screenshots:
  - `sc9-after-h1tee.png`: the H1 tee looking down the hole.
  - `sc9-after-trench.png`: the H3 canyon corridor (river trench with cliffT stacks and edging). No "trench" is defined in the docs; this is my reading.
  - `sc9-after-h13.png`: H13.

## D. Playtests
- **Smoke:** flow PASS, real putt 7.57, **0 errors, 0 server entries**. The client shows the same 5 engine UIBlox `FoundationProvider` warnings as the untouched baseline (`sc9-smoke.log`).
- **18-hole sweep, same seed:** **54/54 cups, 36 shots, 0 escapes, 1 timeout (H15)**, console empty (`sweep-after/`, `sweep-comparison.json`).
  - The summary counts **1 stuck on H11**: the mover-sweep `offsurface` flag on `h11-sweep-lock_gate-1` (the ball brushes `Geometry.Wall`). The fuzz shots had 0 stuck. sc8 recorded the same H11 flag on untouched v49.
  - **H11 rerun alone: 3/3 cups, 0 stuck, no offsurface flag** (`sweep-after-h11rerun/`). Colliders are byte-identical and all dressing is non-colliding and non-query, so this is run-to-run variance.
  - H15 timeouts were 2 before and 1 after; they predate this stage.
- **H16 edge test** (`tools/sc8_h16_edge.py`, `h16-edge.json`): **identical to sc8.**
  - Opening ±0.95 in all 8 directions (0.955 on one diagonal).
  - The sc5 set is 12/12 the same.
  - Rest thresholds: drop at ≤0.925, stay at ≥0.95 (axis and corners).
  - 72 slow putts: 24 drop, **0 outside the frame**, max fall 0.869 from centre.
  - Rim flags all off.

## E. Publication
- File > Publish to Roblox (⌥P), one publish, to the open place. Creator Hub published-only shows **v63** at 3:48 PM; v58-v62 are Studio autosaves from this session.
- File > Download a Copy: `playtest/playtest-sugarloaf_canyon-v63.rbxl`, 5,418,017 bytes, SHA256 `0878d83627145acf056859f7a5afd6b4ca18e2c21b1eaf679e43d47e9942724f`.
- Studio quit normally (⌘Q, no prompts). No RobloxStudio process remains (only StudioMCP helpers).
- Final Creator Hub published-only: **lobby 251, LG 19, AU 13 unchanged**; SC 63. Lobby, LG, AU, 135374506016678 and the Windows PC were never opened or used.

## Open items
- **Triangle target not met:** 1.63M visible mesh tris at the H1 tee (no distance culling) against 1.08M. The art bot's 0.656 Look7 factor doesn't match Studio, which counts 1.0×.
  - The non-dressing meshes are 0.995M by themselves, so the dressing alone can't reach 1.08M.
  - Options: more LOD (cliffT, edging and rock pieces have no LOD; 390 kept pieces beyond 60 use their source mesh), thinning far dressing, LODs for the big non-dressing meshes, or a different target definition (for example a radius, or only what is on screen).
- **LOD rule:** with "nearest hole's tee", 29 LOD pieces are within 60 of *another* hole's tee. Switching to "min over all tees" would keep those at full detail.
- **Engine warnings:** 5 `UIBlox FoundationProvider not found` client warnings from Roblox CorePackages in every Play session, already present on untouched v57. They are not from our scripts; the smoke runner flags them as FAIL.
- **Persistence:** the dressing, SC7Kit (51) and SC9LODKit (39) live in the place, not in `src`/CourseData. The importer uploaded the `sc9_LOD` model asset; it is unused.
- Not done: the `.rbxl` copy to the Linux box and a headset check.

RESULT=PASS SC_NEW=63 PLACED=1277/1281 LOD=221 DEL_FELT=0 DEL_RAIL=0 DEL_FLOAT=4 PARTS=7980->7476 TRIS_H1=1627586 (target 1.08M) SC_SCAN=8068/7847/0 CUPS=54/54 SWEEP=36/1/0/1 SMOKE_ERRORS=0 COLLIDERS=same
