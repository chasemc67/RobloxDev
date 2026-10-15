# Script drift: exported places vs `games/vr-mini-golf/src` (exp1 + exp2, Oct 15, 2026)

`places.json` says every place runs the same scripts and `src/` is the source of truth. All four published places are now exported: SC v103 from the live place (exp1), and lobby v251, LG v25 and AU v13 from the File-downloaded copies of those published versions (exp2; see README.md).

**None of the four is byte-identical to `src`, and no two places are identical to each other.** `src` has 59 scripts. 50 of them are identical in `src` and all four places. The other 9 drift:

| File | lobby v251 | LG v25 | SC v103 | AU v13 |
|---|---|---|---|---|
| `ServerStorage/AuroraVisualCleanup.luau` (au5, 151 lines) | **missing** | = src | = src | = src |
| `ServerStorage/AuroraEffects.luau` | **old**: no au5 cleanup / VisualSeparation calls (-2 lines) | = src | = src | = src |
| `ServerStorage/PropsBuilder.luau` | **old**: no `report.visualSeparation` call (-1) | = src | = src | = src |
| `ServerStorage/VisualSeparation.luau` | **old**: `Apply(course)` with no `scenery` argument (no course/world joins) | = src | = src | = src |
| `ServerStorage/CourseBuilder.luau` | **old**: missing the sc12 `pc.def.cframe` exact-pose piece, lg13 entry ring/glow (0.04 ring over a 0.01 disc), and `ApplyVisualSeparation` | missing sc12 `cframe` piece (-5) | = src | missing sc12 `cframe` piece (-5) |
| `ServerStorage/CourseData/SugarloafCanyon.luau` | pre-sc11: no `dune_rail2_shelf`, no 20 `dune_lean3_terrace_*`, no H16 `lip_*`/`lip2_*` sinkhole lip, old deck sizes (-100 +9) | same as lobby | = src | same as lobby |
| `StarterPlayer/.../GolfClient/GolfTest.luau` | no sc11/sc12 `seamShots` test (-108) | same as lobby | = src | same as lobby |
| `ServerStorage/CourseData/AuroraBatch3.luau` | **pre-au6**: stage_am header, old FBX bounds and tris (27 lines) | au6, no au7 `h18_ramp_lanterns` cage update | au6 (same as LG) | = src (au7) |
| `ServerStorage/CourseData/PropPlacements.luau` | +8 LG rail lanterns (5 `rail_lantern_crook` + 3 `rail_lantern_stake`, near line 1308) | = src (lg14 removed them) | +8 (same as lobby) | +8 (same as lobby) |

Drift from `src`, in diff lines: lobby 326 (8 files differ + 1 missing), LG 232 (4 files), AU 230 (4 files), SC 18 (2 files).

## What it means
- **The live places run their own course's code at its latest version**, and older copies of the other courses' data and shared builders. LG v25 has the lg14 PropPlacements, AU v13 has the au7 AuroraBatch3, and SC v103 has the sc11/sc12 SugarloafCanyon and GolfTest. Each place was last published from a `src` snapshot taken when that course's stage ran.
- **The lobby v251 is the oldest.** It predates au5 (AuroraVisualCleanup), lg13 (VisualSeparation scenery pass and entry ring), au6 and sc11. The lobby doesn't build courses, so this drift probably doesn't change what lobby players see. The shared client scripts (VRControls, HUD, FrontEnd, BallController, etc.) are identical in all four places and `src`.
- Most of the drift is course data or builders for *other* courses (and the GolfTest harness), so gameplay in each place probably isn't affected. A publish of the current `src` to all four places would make them identical.

Reproduce: `diff -r src exports/<role>-v<N>/src`, or `diff -rq exports/<a>/src exports/<b>/src` between places.
