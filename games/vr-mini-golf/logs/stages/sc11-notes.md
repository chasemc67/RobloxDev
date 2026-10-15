# Stage sc11 (Claude Code): Sugarloaf Canyon cliff caps, near-felt full detail, placeholder decals, H15 rail seam

Status: **PASS. Sugarloaf Canyon published v79** (Creator Hub Version History, "Show published only": 79, 69, 63, 57, ...). Evidence: `sc11-v79.png`, `sc11-history-all.png`, `sc11-final-histories.png`.

Every gameplay collider is identical to v69, except **one added part**: the H15 dune_rail2 seam shelf (item 4).

## Preflight
- One Studio, on Sugarloaf Canyon (EditPlace 124440050576723), signed in as MetavrseBuilder (StudioService 1818120139).
  - MCP: PlaceRole `sugarloaf_canyon`, PlaceVersion 69.
- **Matches published v69:** all 707 gameplay parts are identical to sc10's final inventory, the one behind `collider-verification-final.json` (`preflight-vs-sc10.json`).
  - Parts 7476, placeholders 175 / 36 visible, Look7Dressing 1277 models.
- No other stage job. Only this `claude` sc11 job was running; the cursor-agent workers and the ChatGPT codex exec-server are not stage jobs.
- Creator Hub published-only baselines: lobby 251, LG 19, SC 69, AU 13 (`sc11-preflight-histories.png`, `playtests/stage-sc11/preflight.json`).
- The macOS "com.apple.sshd-session ... bypass the system private window picker" prompt was up at the start.
  - I never answered it, sent no Return key and granted no permissions. It was gone by publish time.
  - Every file dialog was confirmed with clicks (Go-to suggestion double-click, Save button).

## A. Baseline (untouched v69)
- **Smoke:** the third run passed: flow PASS, putt 7.38, 0 server entries, 0 errors, only the 5 known UIBlox `FoundationProvider` warnings (`sc11-smoke-before3.log`).
  - The first two runs failed only at "menu > lobby" (`opened: false`, the gamepad-selected Return didn't reach the menu). Chrome was in front after the Creator Hub check.
  - Every other step and the putt passed. The after smoke passed first time.
- **18-hole sweep, seed 20261014:** 53/54 cups, 36 shots, 0 stuck, 0 escapes, 2 timeouts (H15), console empty (`sweep-before/`).
  - The miss was H17 cup-drop try 3. The server's `place` put the ball 1.2 off the requested spot (a mover at that moment), so it rolled past the cup without reaching the rim.
  - A rerun of H17 alone on the same untouched place also gave 2/3 (`sweep-before-h17rerun/`). This is mover-phase variance, not geometry. The after sweep got 3/3.
- **H16 edge** (`h16-edge-before.json`):
  - Opening ±0.95 (0.955 on one diagonal). Rest thresholds: drop ≤0.925, stay ≥0.95. 22/72 putts drop, 0 outside the frame.
  - The 4 sc5 diagonals stopped at the corner. This is the same run-to-run variance sc10 saw on untouched v63; the after run dropped all 4.
- **z-scan before:** 7845 total, 0 exposed (= sc10 after).

## B. Changes
### 1. Cliff caps: **snapped 6/6, then deleted 6/6** (`caps-*.json`, `tools/sc11_caps.py`, `tools/sc11_place.py caps`)
The pieces are cliffT_w24_h6_p4_832, p2_823, p2_821, p2_1247, p0_830 and p0_1279.

**Why sc10's float check found 0 floaters.**
- The sc9/sc10 float rule rays only the **contact ring**: the stem's lowest vertices, which lie within 0.05 of minY.
- The cliffT ring is a small strip at the very bottom of the mesh, and on all six pieces it is **buried 3.0-4.3 studs** in Terrain. On 832 and 830, part of the ring also hangs over a drop.
- The rule counts a piece as grounded when any ring point is within 0.1, so all six passed.
- Many ring rays also start *inside* Terrain (Terrain is 18 → 115 across a footprint), so they miss.
- The mesh steps up: its upper "cap" lid (underside 4-6 above the base) **overhangs the floor where the body isn't**. The lid is what floats.

**Whole-base measure (new).**
- Per column on a 1-stud XZ grid over each piece: the render-mesh underside (EditableMesh ray up) minus the true ground (`trueground` from top + 120: Terrain plus visible non-dressing render meshes).

| id | pivot | contact-ring gap (min..max) | whole-base max gap | float cols / cols | snap dy | after snap: max gap / visible cols | sc9 float rule after snap |
|---|---|---|---:|---|---:|---|---|
| 832 | (-597.6, 134.6, -4896.1) | -3.87..+12.13 | **12.66** | 45/178 | -12.707 | -0.05 / 0 | pass |
| 823 | (-31.8, 14.7, -5292.3) | -3.30..-3.00 | 2.26 | 35/150 | -2.310 | -0.05 / 0 | pass |
| 821 | (-34.4, 14.6, -5243.7) | -3.30..-2.99 | 2.34 | 51/152 | -2.390 | -0.05 / 0 | **fail** (ring buried, no hit) |
| 1247 | (-140.1, 14.8, -4930.9) | -3.26..-3.06 | 2.94 | 36/105 | -2.988 | -0.05 / 0 | **fail** |
| 830 | (569.7, 74.7, -5219.2) | -4.26..+1.06 | 4.31 | 40/145 | -4.362 | -0.05 / 0 | pass |
| 1279 | (-375.1, 146.8, -4948.4) | -3.20..-3.20 | 2.89 | 42/155 | -2.938 | -0.05 / 0 | **fail** |

- **Every column of these pieces that shows above ground today is a floating-lid column** (visible = floating, e.g. 45/45 on 832).
- Snapping the lid down to the ground (dy = −(max gap + 0.05), XZ/rotation kept) leaves **0 columns above ground on all six**. The only remains are 1-3 lid columns within ±0.1 of the Terrain surface, a coplanar z-fight risk.
- Felt 0 and rail: none near (no wall within the search band).
- **Deleted all six after the snap:**
  - 821, 1247 and 1279 fail the float rule.
  - 832, 823 and 830 pass the rules but are fully underground and only leave coplanar slivers.
  - Visually this is the same as "no floating caps", without the slivers. Backups: `ServerStorage.SC11Backup` (6 models, pre-snap).
- Screenshots: `sc11-before-caps.png` → `sc11-after-caps.png`, same cameras. The floating lobes (for example the beige lump at 1279 and the pink lobe at 821) are gone; the rest is neighbouring geometry.

### 2. Full detail near felt: **40 LOD pieces restored** (`lod-plan.json`, `lod-swap.json`, `lod-verify.json`)
- **Rule:**
  - Look7 piece on SC9LODKit meshes. 221 such pieces.
  - True XZ footprint: sc9 slot hulls at the live pivot, plan scale.
  - Plan distance ≤ 15 to any GolfSurface plan polygon (206 felt polys, as sc9).
- **40 pieces, not the expected ~26.** Other readings give 36 (pivot ≤15), 33 (<12) or 24 (≤10). I used the rule as written.
- Each piece was swapped to its SC7Kit source templates: same pivot (WorldPivot), plan scale, sc9 per-slot centre/size from the merge report with the RY half-turn, and template appearance.
  - Settings: RenderFidelity Automatic, Anchored, CanCollide/Query/Touch off, `VisualQueryDisabled`, CollisionFidelity Box. 149 → 149 MeshParts.
  - Verified: 40/40 pieces and 149/149 parts match their template mesh, texture, material, colour, variant, transparency and CastShadow, with flags off and no `_lod__` parts left.
- **Ids (felt distance order):** 126, 766 (gumdrop_shrub_c_v2_766 as expected), 111, 528, 769, 275, 527, 767, 606, 278, 280, 286, 604, 109, 437, 288, 287, 529, 107, 482, 106, 645, 611, 235, 281, 768, 236, 65, 289, 131, 771, 480, 290, 67, 531, 237, 291, 241, 293, 132.
  - Kinds: gumdrop shrubs a/c, rock candy, scrub, lollipop cactus, crystal cluster a, barrel a. Holes 2, 3, 6, 7, 8, 11, 12, 13, 15, 18.
- **Triangles** (`tools/sc11_tris.py` = sc9_tris.py method):
  - Exact per MeshId with `CreateEditableMeshAsync` → `#GetFaces()`. Visible = Workspace MeshPart with Transparency < 1.
  - Distance from the H1 tee camera (60, 22.98, -4530) to each part's bounding box. No distance culling (StreamingEnabled off, FogEnd 100000). Engine LOD not counted.

| visible mesh tris | sc9 after (v63) | sc11 after (v79) |
|---|---:|---:|
| within 60 of the H1 tee | 85,626 | 85,626 |
| within 120 | 144,249 | 145,672 |
| within 250 | 341,278 | 347,176 |
| **within 500** | 662,143 | **673,185** |
| **whole place** | 1,627,586 | **1,649,759** |
| of which Look7 | 632,218 | 654,391 |

### 3. Placeholders: **175 / 36 visible, 0 new decals** (`placeholders.json`, `placeholders-raw.json`, `decal-asset-match.json`, `sc11-after-decals.png`)
- **Inventory:** every BasePart under CourseSugarloaf with a `Placeholder` ancestor, or "placeholder" in its name, tags or attribute names. That's 175 parts, all found via a `Placeholder` model; no extras by tag or attribute.
  - Per part: name, path, hole, visible, size, material and what it represents (the Decor anchor's `Notes`).
- **Decal folder:** 37 PNGs. 29 are in `manifest.json` and 8 are not (H7 pads ×2, plank respawn stone, H9 bypass ×2, H14 safe bank ×2 and the timing arrow).
- **All 37 were already uploaded and applied:**
  - 29 by stage zf1 (`StageZf1Image`, on the same-named items).
  - The H7 pads and the plank stone by sc5.
  - The H9/H14 five by stage al2 (`HintVisual`).
- I read every applied asset back with `CreateEditableImageAsync` (12×12 pixel samples). **37/37 are pixel-identical to the current PNGs.** The slope arrows were stored at 1024×128, the same image as the 2048×256 file.
- So nothing was uploaded and nothing was re-applied. **DECALS_APPLIED=0 (all mapped decals already in place).**
- Visible placeholders by decal status:
  - **25 parts:** the decal is already on their item (14 boards/rock carry it; 11 are their posts).
  - **11 parts:** no decal in the folder: the H1 lollipop cactus (3) and the H10 chute chevrons (8). These are list-only.
  - No collider or placeholder property was changed.

| hole | item | visible parts (size) | represents | decal | status |
|---|---|---|---|---|---|
| 2 | sign_left | SignBoard 1.6x3.2x0.2, SignPost 0.2x3.2x0.2 | 'Short Cut - tight!' sign, left tunnel | h02_sign_short_cut.png | applied (zf1), identical |
| 2 | sign_mid | SignBoard 3x0.8x0.2, SignPost 0.2x1x0.2 | plank sign 'DEAD END - NO GOLD' | h02_sign_dead_end.png | applied (zf1), identical |
| 2 | sign_right | SignBoard 1.6x3.2x0.2, SignPost 0.2x3.2x0.2 | 'Long Haul - safe; firm putt' sign | h02_sign_long_haul.png | applied (zf1), identical |
| 3 | sign_plank | SignBoard 1.6x3.2x0.2, SignPost 0.2x2.6x0.2 | 'Log Plank - no rails!' sign | h03_sign_log_plank.png | applied (zf1), identical |
| 3 | sign_bridge | SignBoard 1.6x3.2x0.2, SignPost 0.2x3.2x0.2 | 'Footbridge - the safe way' sign | h03_sign_footbridge.png | applied (zf1), identical |
| 6 | flood_marks | Rock 1.5x3x0.2 | high-water marks + 'Flash Flood Zone' plaque | h06_flood_marks.png | applied (zf1), identical |
| 6 | sign_overflow | SignBoard 1.6x3.2x0.2, SignPost 0.2x3.2x0.2 | 'Overflow - the long way round' | h06_sign_overflow.png | applied (zf1), identical |
| 12 | sign_pier | SignBoard 1.6x3.2x0.2, SignPost 0.2x2.6x0.2 | 'Intake - shoot the pipe!' | h12_sign_intake.png | applied (zf1), identical |
| 12 | sign_shore | SignBoard 1.6x3.2x0.2, SignPost 0.2x3.2x0.2 | 'Shoreline Trail' | h12_sign_shoreline.png | applied (zf1), identical |
| 13 | sign_west | SignBoard 1.6x3.2x0.2, SignPost 0.2x3.2x0.2 | 'Long & easy' | h13_sign_west.png | applied (zf1), identical |
| 13 | sign_centre | SignBoard 1.6x3.2x0.2, SignPost 0.2x3.2x0.2 | 'Straight through (mind the hoodoos!)' | h13_sign_centre.png | applied (zf1), identical |
| 13 | sign_east | SignBoard 1.6x3.2x0.2, SignPost 0.2x3.2x0.2 | 'Scenic route' | h13_sign_east.png | applied (zf1), identical |
| 18 | sign_rim | SignBoard 1.6x3.2x0.2, SignPost 0.2x3.2x0.2 | 'Rim Trail' | h18_sign_rim_trail.png | applied (zf1), identical |
| 1 | lollipop_cactus_1 | Cactus 1.2x8.4x1.2, Arm 0.7x2.4x0.7, Lollipop 0.3x2.6x2.6 | saguaro with a swirl lollipop | none | list only (3D prop) |
| 10 | chevron_1..4 | 8 × Arrow 0.2x0.2x0.9 | glowing felt chevrons on the chute (one-way) | none | list only (felt_arrow_deck = h10_felt_arrow_one_way.png is on its own item) |

- **All 175 by hole (parts / visible):** H1 26/3, H2 15/6, H3 12/4, H4 7/0, H5 1/0, H6 7/3, H7 13/0, H8 1/0, H10 10/8, H11 7/0, H12 13/4, H13 13/6, H15 4/0, H16 14/0, H17 1/0, H18 31/2.
  - 58 parts belong to items whose decal is applied; 117 have no decal in the folder. Full rows are in `placeholders.json`.

### 4. H15 dune rail seam: **stuck 47/48 → 2/48** (`h15-colliders.json`, `h15-seam-fix.json`, `seam-manifest.json`, `seam-before.json`, `seam-after.json`, `sc11-after-h15seam.png`)
- **Location.** The point was given as "(-313.7, 146.7) XZ", but it is world **x, y**: x -313.7 at y 146.7 lies on `dune_rail2` (z ≈ -5091.5).
  - Stage al's 26 "wedge_seam" stops all sit at y 146.69, along the whole of rail2, z -5074..-5099.
- **The joint.** There is no lip, step or gap.
  - The dune felt (tilted 5.71°, falling straight toward rail2) ends **exactly** on the rail2 inner face (0.0001); its Base block is flush too.
  - Along the rail the joint is **level** (felt top 146.600 at every point).
  - So a ball rolling down the cross-slope parks in a level V-gutter.
  - In BallController, slope acceleration on 5.71° (3.25) is above RollDecel (0.5), so a ball against the rail can never rest normally. `valleyPoint` finds no crease (the rail is in the way). The ball gets 3 seam hops into the rail, then `forcedrest:wedged`, which counts as stuck.
- **Fix: one added collider.** `Hole15.Geometry.Felt` (PieceId `dune_rail2_shelf`, Zone dune, GolfSurface, felt physics 1/0.35/0/1/100, Transparency 1, like the other felt colliders).
  - A **flat 0.25 × 30 shelf** in the corner, top 146.625. That is the dune felt height 0.25 in from the rail, so the inner edge is flush (146.625 = 146.625). It sits +0.025 above the felt at the rail face, and its outer face is flush with the rail2 inner face (0.0002).
  - World CFrame (-310.7624, 146.4250, -5085.9814), yaw = dune/rail2 (R = [-0.9063 0 -0.4226; 0 1 0; 0.4226 0 -0.9063]), size (0.25, 0.4, 30).
  - Before: none. After: that part.
  - Rail heights and every other collider are unchanged (`collider-verification-final.json`: 707 identical + 1 added).
  - The roll height only changes inside that 0.25 strip (≤ +0.025).
- **src:** `CourseData/SugarloafCanyon.luau` H15 felt `dune_rail2_shelf`, center (10.7624, -3.375, -29.0186), size {0.25, 30}, yaw 25, overlay. Pushed to the place.
- **Test** (new `seamshots` scenario in GolfTest.luau, `tools/sc11_seam.py`, fixed seed 20261014):
  - 48 native shots through Ball.hit: 24 across the seam (±60°, 1-7 studs/s), 16 along it (0-15° in, 1-6), 8 gentle parks (0.4-1.2).
  - Half the shots are within 4 studs (along the rail) of the reported spot.
  - Stuck = timeout, stuck-3s, forcedrest, offsurface or timeout reset, or crawling (< 0.3 studs/s while moving) > 2 s within 0.6 of the seam.
  - **Before: 47/48 stuck** (all `unstuck:seam`×3 + `forcedrest:wedged`). **After: 2/48**: 46 rest normally at the rail (0 hops).
  - The 2 left are at the far north end, where rail2, dune_lean3 and the 0.6 dune→tier drop meet. #14 is the known lean3 crawl (timeout reset, ends 2.5 from the seam, identical before and after). #44 now takes one hop and rests (before, it crawled and rolled off the edge).
  - The targeted rate (47/48) is far above the general-play 1/40 because every shot is aimed at the joint.
- **H15 in the 18-hole sweep:** timeouts 2 → **1**.
  - The remaining one is the lean3 crawl at (-307.2, -5087.9), which history shows on every run (sc8-sc10 at the same spot).
  - The former fuzz-2 timeout at (-306.8, -5085.6) now takes one seam hop at the north corner and rests.

## C. VisualSeparation and verification
- `CourseBuilder.ApplyVisualSeparation(CourseSugarloaf)` with gap 0.08 and min 0.2: **1204 fixes** (same as sc10), 0 unresolved, 0 thin, **706 collider invariants** (705 + the shelf), 0 failures, 171 joints.
- **Colliders** (`collider-verification.json`, and `collider-verification-final.json` after all Play sessions):
  - All 707 v69 gameplay parts are identical. Exactly 1 was added (the H15 shelf). Nothing is missing.
  - `after-vs-final.json`: the post-separation and post-Play inventories are identical (708).
  - Placeholders 175/175, 36 visible, same paths.
- **Parts: 7476 → 7471** (−6 caps; +1 shelf; LOD swap 149 → 149).
- **Full dressing check** (sc10 rules, `dressing-check-after.json`, 1271 pieces): **felt 0 / rail<1 0 / float>0.1 0**. Closest rail 1.126. 206 felt polygons, including the shelf.

| z-scan (zf1_zscan.luau) | Before (v69) | After |
|---|---:|---:|
| Coplanar faces | 7136 | 7130 |
| Decorated coincident | 61 | 61 |
| Placeholder coplanar | 16 | 16 |
| Transparency candidates | 632 | 632 |
| **Total** | **7845** | **7839** |
| **Exposed planar candidates** | **0** | **0** |
| Imported mesh hits | 7132 | 7126 |
| Terrain candidates | 131 | 131 |

## D. Playtests
- **Smoke:** flow PASS (arrival, menu > lobby, finish > lobby). Real putt 7.36. **0 errors**, 0 server entries. The client showed only the 5 UIBlox `FoundationProvider` warnings (`sc11-smoke.log`).
- **18-hole sweep, seed 20261014:** **54/54 cups, 36 shots, 0 stuck, 0 escapes, 1 timeout (H15)**, console empty (`sweep-after/`, `sweep-comparison.json`).
  - It differs from the baseline only on H15 (timeouts 2 → 1) and H17 (cups 2 → 3, the baseline's mover variance).
- **H16 edge** (`h16-edge.json`):
  - Opening ±0.95 (0.955 on one diagonal). **sc5 set 12/12** (all 4 diagonals drop). Rest: drop ≤0.925 / stay ≥0.95.
  - 72 slow putts: 24 drop, **0 outside the frame**, max fall 0.866. Rim flags all off.
- **seamshots before/after:** see item 4.

## E. Publication
- File > Publish to Roblox (⌥P), one publish, to the open place (the tab lost its unsaved timestamp).
- **Creator Hub published-only shows v79** (`sc11-v79.png`).
  - "Last Updated" is 6:25 PM, the last autosave; I published at about 6:30.
  - After 6:25 there were only Play sessions and read-only checks. The H15 screenshot's temporary highlight part was created and deleted earlier.
  - v70-v78 are autosaves from this session (`sc11-history-all.png`).
- **File > Download a Copy:** `playtest/playtest-sugarloaf_canyon-v79.rbxl`, 5,426,563 bytes, SHA256 `193a04f8514083bd4c841017f45c1367ba26be6a9e44f700f44ac03a451b8efb`.
- Studio quit normally (⌘Q, no prompts). No RobloxStudio process remains, only the StudioMCP helpers.
- **Final Creator Hub published-only:** lobby 251, LG 19 and AU 13 unchanged; SC 79 (`sc11-final-histories.png`). Lobby, LG, AU, 135374506016678 and the Windows PC were never opened or used.
- **New uploads: none.** There were no imports, and no decal uploads were needed (item 3). No asset was deleted or archived.
- A misdirected click opened Chrome's Edit > Emoji picker once; I closed it.

## Tools (new/changed)
- `sc11_stage.py`: the sc10_stage commands writing to stage-sc11.
- `sc11_place.py`: caps ring/true-ground probe and snap, LOD plan/swap, placeholder inventory, dressing check.
- `sc11_caps.py`: whole-base column gaps (render-mesh underside/top vs true ground).
- `sc11_tris.py`: sc9_tris with stage-sc11 output.
- `sc11_placeholders.py`: builds `placeholders.json`.
- `sc11_seam.py`: seam manifest and run.
- `GolfTest.luau`: the `seamshots` scenario (test mode only).
- `CourseData/SugarloafCanyon.luau`: the H15 shelf.

## Open items
- **Caps:** the cliffT lid overhang is a mesh property. Other cliffT pieces sunk to their contact ring may show the same floating lid; sc10's contact-ring rule can't see it.
  - Running `sc11_caps.py` on all 95 remaining cliffT pieces would list them. Also consider a whole-base float rule for future dressing checks.
- **LOD count:** 40 by the stated rule against ~26 expected. If the art bot meant a 10-stud radius (24), 16 of these could go back to LOD.
- **Triangles:** 1.650M whole place / 0.673M within 500 (+22k from full detail, −6 cliffT).
- **H15:** the lean3 crawl (1 sweep timeout) and the north-end corner (rail2 / lean3 / drop) remain. They are separate from the rail2 gutter.
- **H17 cup-drop variance** on untouched v69: the server `place` shifted a cup-drop ball 1.2 studs (mover phase). The after sweep got 3/3.
- **Smoke "menu > lobby"** can fail when Studio isn't the front app (twice in the baseline here).
- **Persistence:** the cap deletion, LOD swap and shelf live in the place. The shelf is also in src CourseData. `ServerStorage.SC11Backup` holds the 6 caps.
- Not done: the `.rbxl` copy to the Linux box and a headset check.

RESULT=PASS SC_NEW=79 CAPS_SNAPPED=6/6 (then all 6 deleted: 0 visible above ground after the snap) CAPS_DELETED=6 LOD_RESTORED=40 TRIS_H1_500=673185 TRIS_ALL=1649759 PLACEHOLDERS=175/36 DECALS_APPLIED=0 (37/37 already applied, pixel-identical) H15_STUCK=47/48 -> 2/48 DRESSING_CHECK=0/0/0 PARTS=7476->7471 SC_SCAN=7845/7839/0 CUPS=54/54 SWEEP=36/0/0/1 SMOKE_ERRORS=0 (+5 UIBlox) COLLIDERS=same except H15 seam (+1 shelf) COMMIT=(this commit, see git log)
