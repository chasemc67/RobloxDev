# Script drift: exported places vs `games/vr-mini-golf/src` (exp1, Oct 15, 2026)

`places.json` says every place runs the same scripts and `src/` is the source of truth. Only Sugarloaf Canyon v103 could be exported (the lobby, Lantern Grove and Aurora opened at saved versions newer than their published ones and were skipped; see README.md), so there is no place-to-place comparison this time.

## sugarloaf_canyon-v103 vs src
Both have the same 59 files. **Two files differ (DRIFT):**

| File | Difference |
|---|---|
| `ServerStorage/CourseData/AuroraBatch3.luau` | `src` has the stage-au7 `h18_ramp_lanterns` (props_fix_overlap4) update: header comment, cage `tris` 348 → 492, collider `center` y 6.184 → 6.185, `size` {0.366,0.397,7.366} → {0.206,0.206,7.206}, prop total `tris` 648 → 792. SC v103 still has the au6 version. |
| `ServerStorage/CourseData/PropPlacements.luau` | SC v103 has 8 extra Lantern Grove rail entries near line 1308 (5 `rail_lantern_crook` + 3 `rail_lantern_stake`, role "rail") that aren't in `src`. Given lg14 ("H7 crook duplicates"), these are probably the duplicates that were removed from `src` and Lantern Grove v25 but never pushed to Sugarloaf. |

Both are course data modules for other courses (Aurora, Lantern Grove), so they probably don't change Sugarloaf gameplay, but SC v103 isn't byte-identical to `src`. The next SC push and publish of `src` would clear it.

Reproduce: `diff -r src exports/sugarloaf_canyon-v103/src`.
