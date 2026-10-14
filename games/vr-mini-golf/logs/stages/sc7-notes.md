# Stage sc7 (Claude Code): Sugarloaf Canyon tunnel lanterns (post2), look7 dressing edgefix4, cliff filler rocks

Status: **PASS. Sugarloaf Canyon published v49** (Creator Hub Version History, "Show published only": 49, 42, 34, 23, ...; v49 = Oct 14 2026 1:47 PM). Evidence: `sc7-v49.png`, `sc7-history-all.png`, `sc7-final-histories.png`.

## Preflight
- One Studio, opened from the cloud on Sugarloaf Canyon (EditPlace 124440050576723), signed in as MetavrseBuilder (StudioService 1818120139). MCP: PlaceRole `sugarloaf_canyon`, PlaceVersion 42 at open. `Workspace.CourseSugarloaf` has Hole1-Hole18.
- **Matches published v42:** all 707 gameplay parts identical to sc6's final inventory (= v42), 4462/4462 parts, placeholders 175 / 36 visible, same paths (`preflight-vs-sc6.json`). The z-scan total is 6298, equal to sc6's after scan.
- No other stage job. Creator Hub published-only baselines: lobby 251, LG 19, SC 42, AU 13 (`sc7-preflight-sc-published.png`, `sc7-preflight-others.png`, `playtests/stage-sc7/preflight.json`).
- The macOS "com.apple.sshd-session ... bypass the system private window picker" prompt was up the whole stage. I never answered it and sent no Return key. No permissions were granted (one `osascript` reload of Chrome was refused by macOS. I did not grant it and reloaded by reopening the URL).

## 1. Baseline (untouched v42)
- Smoke PASS: real putt 7.58 studs, 0 server/client errors or warnings (`sc7-smoke-before.log`).
- 18-hole sweep, seed 20261014: **53/54 cups, 36 shots, 0 stuck, 0 escapes, 1 timeout (H15)**, console empty (`sweep-before/`). The miss is **H17 cup drop 2/3**: the 112.5° approach rolled to rest (sc6 logged that approach as "refused" and took the next angle). A rerun of H17 alone on the same untouched place gave **3/3** (`sweep-before-h17rerun/`), so this is run-to-run variance in v42, not a stage change.
- z-scan before: `zscan-before.json` (6298, 0 exposed planar). Screenshot: `sc7-before.png`.

## 2. Imports (`tools/sc7_place.py`, `imported.json`)
- **One 3D Importer pass.** All 24 kit sources were merged with `sc5_merge_fbx.py --split-materials` into `sc7_K.fbx`: 56 meshes, 12,592 tris, max 1,436, round-trip PASS. The sources are the 21 layout `piece_files` (17 look7 / main-kit pieces + 4 cliffT_w24_h6), `cliff_filler_rock_a/b` and `tunnel_lanterns_post2`. Every manifest SHA256 matches (the main-kit pieces have no SHA in their manifest; their actual hashes are recorded). Settings as sc6: Import Only as a Model off, Upload on, Add to Workspace, Insert Using Scene Position, Set Pivot to Scene Origin, Anchored, cages off, No Rig, Stud, scale 1 (`sc7-import-settings.png`, `sc7-import-geometry.png`). The importer scaled uniformly by x85.33. Every template was rebuilt from the merge bounds with the Y half-turn undone.
- **Templates:** each kit mesh was imported once, into `ServerStorage.SC7Kit` (56 MeshParts). The `sc7_K` staging bundle was removed from Workspace.
  - Appearance: when the place already has the same mesh (old-kit pieces), I copied it fully, texture included. Otherwise I copied material and colour from a part with the same material slot and kept the importer's own texture, because only that texture matches the mesh UVs.
- **Strata:** the place has **no MaterialVariants** (MaterialService is empty). Its cliff kit's Strata slot is **Enum.Material.Sandstone** plus the shared strata texture (rbxassetid://100807267874640, grey tint). All Strata pieces use Enum Sandstone.
  - The cliff filler rocks have no UVs: with the strata texture they sampled one rose texel and looked like flat pink lumps. They are untextured Enum Sandstone in the manifest Strata colour (0.74, 0.42, 0.31), recorded as an `SC7Appearance` attribute.
- **A. tunnel_lanterns_post2:** 4 copies, every 6 studs along the H2 right tunnel (felt spans hole-local z -16..-42). Positions are the manifest placement (109, 26, 378) and z +12/+6/0/-6, with offset (0,0,-5000) and yaw 0. They live in `Hole2.Decor.tunnel_lanterns.SC7Lanterns`.
  - The post was **not lowered** (pivot y 26 as authored). NeonAmber is Material=Neon in the ph1 / sc5 lantern colour (1, 0.70, 0.25), CastShadow off.
  - The sc5 `SC5Mesh` lanterns (8 parts) went to `ServerStorage.SC7Backup`. The placeholder `Glow` stays and stays hidden.
  - **Float check** (`lanterns.json`): every post base is at 18.27. The ground below (`h02_ground_s12/s11__RedDirtLight`, top 18.29) puts each base **0.02 into the ground** (within 0.15; the art bot's intended pierce was 0.1 against the pre-drop 18.37).
  - **Clearance:** post column to `Hole2.Geometry.Wall` (rail9 line) is **0.32**, the same as the art bot's fitcheck. The arm and lantern are 5.6 above all H2 gameplay parts. The ball path is untouched.
- **B. look7 dressing edgefix4:** `layout_look7_dressing_edgefix4.json` has **1,832 entries** (1,423 look7 / edgefix3 + 409 edgefix4 filler rocks), not the ~1,460 in the prompt. **All 1,832 placed** (3,925 MeshParts) in `Workspace.CourseSugarloaf.Look7Dressing/<piece>/<piece>_<layout index>`.
  - Placement follows the `models/manifest.json` rule: `CFrame.new(pos + offset) * Angles(0, rad(yaw), 0)`, with `scale` applied per local axis to Size and to the offset from the pivot.
  - No earlier look7 dressing existed, so nothing was replaced. 409 fillers: 205 rock_a + 204 rock_b.
- All new parts are anchored, CanCollide/CanQuery/CanTouch off, with `VisualQueryDisabled`, so CameraOcclusion does not turn CanQuery on at runtime. I checked all 3,933 new parts; none is thinner than 0.2.

## 3. Cliff base check (`cliff-check.json`, `sc7-cliff-site01.png`)
- Sites 0-39 = the 40 cliff steps dropped in edgefix2 (edgefix3 `fills` order = edgefix4 `sites`).
  - Per site, top-down rays over the dropped panel's footprint count where ground shows at or below the cliff base.
  - For every cliffT and filler piece within 3 studs of the footprint, the perimeter of its base is sampled against the first ground surface (Terrain or a non-dressing part).
- **No gaps at any site.** Open fraction is 0 at every site (0.001 at sites 13 and 30), and no base sample is above the ground.
- **Reason, flagged for 3D Model Bot / Game Art Bot:** the Studio **terrain stands 2.7 to 3.7 studs above the cliff stack bases** along the west wall, and up to about 50-70 where the canyon wall rises. So every base is buried, and **all 409 filler rocks are fully under the terrain** at their centres (terrain minus base: min 2.77, median 40.7). They are placed exactly as the layout says but are not visible. The layout's ground model evidently does not include this terrain. I invented no fix.
- CLIFF_GAPS: none.

## 4. VisualSeparation and verification
- `CourseBuilder.ApplyVisualSeparation(CourseSugarloaf)`: gap 0.08, min 0.2, **1204 fixes (the same set as sc5/sc6, idempotent), 0 unresolved, 0 thin, 705 collider invariants, 0 failures**, 171 joints reconnected. The new MeshParts fall in the non-box "audited by zscan" class.
- **Colliders: same.** All 707 gameplay parts are identical to untouched v42, after separation and again after all Play sessions (`collider-verification.json`, `collider-verification-final.json`, `collider-vs-sc6-final.json`). Rails are unchanged. Placeholders 175/175, 36 visible, same paths.
- **Parts: 4462 → 8387** (+3925 dressing, +8 lantern parts, -8 old SC5Mesh lantern parts moved to the backup).

| z-scan (zf1_zscan.luau) | Before (v42) | After |
|---|---:|---:|
| Coplanar faces | 5918 | 7467 |
| Decorated coincident | 61 | 61 |
| Placeholder coplanar | 15 | 15 |
| Transparency candidates | 304 | 699 |
| **Total** | **6298** | **8242** |
| **Exposed planar candidates** | **0** | **0** |
| Imported mesh hits | 5585 | 7529 |
| Terrain candidates | 131 | 131 |

The increase is all mesh-bbox / review classes from the 3,925 new MeshParts. The extra transparency candidates are the crystal pieces, which use the place's Glass candy look. Screenshot: `sc7-after.png` (lit tunnel lanterns from two angles, H1 dressing, the cliff site).

## 5. Playtests
- Smoke PASS: real putt 7.38 studs, **0 server/client errors or warnings** (`sc7-smoke.log`).
- 18-hole sweep, same seed. **After: 54/54 cups, 36 shots, 0 stuck, 0 escapes, 1 timeout (H15)**, console empty. The only differing hole versus the baseline is H17's cup drop (baseline 2/3, explained above; after 3/3) (`sweep-comparison.json`). The H15 slope timeouts predate this stage.
- **H16 sinkhole edge** (`h16-edge.json`): the 4 axis rolls and 4 diagonal rolls drop, balls at rest 0.9 from centre drop, and balls at rest 1.3 stay. All 12 outcomes are the same as sc5/sc6. The rim keeps all flags off.

## 6. Publication
- File > Publish to Roblox (⌥P), one publish, to the open place. Creator Hub published-only shows **v49** at 1:47 PM; v43-v48 are Studio autosaves from this session.
- File > Download a Copy: `playtest/playtest-sugarloaf_canyon-v49.rbxl`, 5,287,374 bytes, SHA256 `2b580545506db27280140cd13a3131a5e276a551878b92e61326b38091ae6836`.
- Studio quit normally (⌘Q, no prompts). No RobloxStudio process remains.
- Final Creator Hub published-only: **lobby 251, LG 19, AU 13 unchanged**; SC 49. Lobby, LG, AU, 135374506016678 and the Windows PC were never opened or used.

## Open items
- **Filler rocks hidden:** all 409 edgefix4 fillers (and the cliff stack bases) are under the Studio terrain. If the fillers are meant to be seen, 3D Model Bot / Game Art Bot need to fit the cliff stacks to the place's terrain, or the terrain needs lowering there.
- **Prompt count:** the layout has 1,832 entries, not ~1,460. All were placed.
- **Baseline H17 flake:** the cup-drop approach at 112.5° on H17 sometimes rolls to rest instead of being refused (untouched v42). Worth a Playtest Bot look.
- **Persistence:** the lanterns, dressing and SC7Kit templates live in the place, not in `src`/CourseData. `ServerStorage.SC7Backup` holds the old sc5 lantern meshes.
- The importer uploaded the `sc7_K` model asset; it is unused (the parts live in the place).
- Not done: the `.rbxl` copy to the Linux box and a headset check.

RESULT=PASS SC_NEW=49 LANTERNS=4 DRESSING=1832/1832 FILLERS=409 CLIFF_GAPS=none SC_SCAN=6298/8242/0 CUPS=54/54 SWEEP=36/0/0/1 SMOKE_ERRORS=0 COLLIDERS=same
