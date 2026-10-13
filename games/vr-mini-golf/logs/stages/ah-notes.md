# Stage ah — local Aurora H6/H18 collider check

Result: **PASS (inspection complete; no generator mismatch found in the requested joints or hazard)**. No geometry/source changes, rebuild, or save. `playtest/playtest-aurora-v3.rbxl` is unchanged; no v3b was created. The authored H6 pad lip and H18 bank/rollback layout remain design/data issues for Game Art Bot, not fixes made by this stage.

## Preflight and scope

Read game AGENTS.md, ag-notes.md and ah-inputs/cap_oob_h6_h14_h18.md first. Process check found no other stage job; the only matching shell was this run's own check. Launched Studio and visually confirmed **Welcome, MetavrseBuilder** in a CUA screenshot. Used **File > Open from File** for `games/vr-mini-golf/playtest/playtest-aurora-v3.rbxl`. Exactly one MCP Studio: `playtest-aurora-v3.rbxl`, id `31c9f91c-8e5c-49b2-bdae-ba7e2c54acec`. Edit mode, PlaceId=0, GameId=0, no NetworkClient, PlaceRole=`aurora_archipelago`, gravity=32.7.

Live CourseBuilder, AuroraArchipelago, Config and BallController sources exactly equal their repo files. Regenerating Aurora data **in memory** from current holes.json exactly equals the current generated source. The source spec SHA256 is recorded in preflight.json. All work used this one local place. No cloud place opened/saved, new place, publish, asset upload, or git push. Sugarloaf, including H8, was not opened or changed.

## Measurement

Read-only native downward `Workspace:Raycast` with only collidable `GolfSurface` parts included and `RespectCanCollide=true`. Heights and normals are hole-local. 9,778 grid positions at 0.1 stud spacing, plus 773 joint positions sampled on all felt and on each adjoining piece separately; joint offsets include +/-0.001 and +/-0.01 studs. Supplemental pool boundary probes use +/-0.001 studs. Loops yield every 500 grid positions.

- H18 collection/foot: x -17.4..-9.6, z -30..-22, 6,399 positions. This covers the entire reported x -13..-10, z -26.3..-22.6 patch.
- H18 ramp profile: x -13.6..-13.4, z -38.5..-27.5, 333 positions.
- H6 pad/shelf: x -2..2, z -56..-52, 1,681 positions.
- H6 north pool edge: x 8.3..14.7, z -47.5..-45.5, 1,365 positions.

The analyzer independently intersects boxes derived from the spec's top-center, horizontal dimensions, yaw and rise, using CourseBuilder's documented normal-direction slab thickness. It also checks the authored top planes. This distinction matters for the exposed sides of the steep crystal bank. Native CSG ray hits inside the circular cup can report the shelf collision decomposition; cup-interior samples are retained in raw evidence but excluded from seam-height error metrics. This pass is not a new physical cup-entry test.

## H18 — ramp foot continuous; raised bank present in collection area

`plaza_w`: x -17.5..-9.5, z -28..-16, y=0. `ramp`: same x footprint, z -38..-28, y = -0.08*(z+28), rising from 0 to 0.8. Expected ramp grade 8%, angle 4.573921 degrees.

At all 79 cross-sections across the ramp width, the plaza at z=-27.999 and z=-28 reads y=0; ramp at z=-28.001 reads y=0.000076294, versus expected 0.000080000. Extrapolated seam intercept error is **0.000003706 studs**. At z=-28.01 it reads 0.000793457; at -28.1, 0.007995605. These are the continuous authored slope, not a lip. **No ramp-foot step >0.02, no missing support/gap in the joint probes.** Ramp height error across the full profile is at most 0.000008912 studs.

The collection region is **not all flat plaza**: `crystal_bank_sw` crosses it. The data explicitly defines a 45-degree overlay, top center [-10.3243,0.6,-21.5757], horizontal size [1.2,17.5706], yaw=45, x rise=-1.2. Its top runs from y=0 to 1.2. The reported patch has measured surface heights 0..1.197998; most points are plaza or bank top.

The broad grid contains **2,414 adjacent 0.1-stud height changes >0.02**, all involving this bank (including ordinary changes along the 45-degree plane). Largest adjacent change is **1.131317 studs** at its end near [-16.9,-27.4], from plaza y=0 at z=-27.5. This is an authored raised-bank edge, not the ramp-foot joint. The bank's 0.4-stud solid thickness also exposes a sloped side outside its top rectangle: **214 samples** hit that side. Its horizontal projection extends 0.282843 studs past the high top edge, as expected for normal extrusion at 45 degrees. Comparing only infinitely thin top rectangles would incorrectly label these as 1.198-stud height errors. The complete spec-derived solid matches all 6,399 native grid hits within **0.000030210 studs**; there are no missing grid hits.

Stop rules: BallController computes gravity*sqrt(1-normal.Y^2), yielding **2.607669 studs/s²** on the ramp and **23.122392** on the bank, versus RollDecel=0.5 (decel_scale=1). Neither qualifies for ordinary gentle-slope rest. Flat plaza acceleration is 0 and does qualify. Thus uphill stall/rollback onto the plaza is consistent with the authored geometry and stop rules. This static measurement supports, but does not dynamically reproduce, Playtest Bot's under-powered rollback diagnosis. Game Art Bot owns any bank margin/ramp/layout change.

## H6 — authored east lip, below 0.02 studs

Shelf top equation: **y=0.0434 - (0.3331/23)*(x+3)**, grade -1.448261%, angle 0.829734 degrees toward +x. `cup_pad` is flat y=0, x +/-0.6, z -54 +/-0.6, directly overlapping the shelf. The exposed surface is the higher of these two.

At east edge x=+0.6,z=-54: native pad y=0, native shelf y=-0.008735657. **Lip=0.008735657 studs**, authored difference=**0.008737391**, error=0.000001735. At x=0.599 the surface is pad y=0; at x=0.601 it is shelf y=-0.008743286. Therefore a small uphill lip exists for a putt approaching from the east, but it is exactly the authored flat-pad/tilted-shelf overlap, not a generator error.

At west edge x=-0.6 the shelf is y=+0.008644104 and remains the upper surface across the pad boundary: no downward exposed step there. North/south pad-edge changes on the east half are bounded by the same ~0.00874 height. No pad/shelf step >0.02 or missing support was measured. Outside the cup interior, maximum height error in the 0.1 grid is **0.000130299 studs**, including native CSG boundary precision.

Shelf slope acceleration is **0.473532**, just below the 0.5 gentle-slope threshold. Ordinary rest requires speed<0.2 for 0.5 seconds; the flat pad also qualifies. Ready-state static hold applies on these gentle slopes for speed<1.5. RollDrag=0.25 and EngineRollLoss=0.2 are unchanged. These rules permit weak putts to settle near the authored lip; widening/blending the pad or reducing tilt is **Game Art Bot's design/data work**.

## H6 pool — footprint matches

| Item | holes.json / builder expectation | Native measurement |
|---|---|---|
| Horizontal center | x=11.5,z=-35 | exact |
| Footprint size | 6 by 22 | exact |
| X edges | 8.5,14.5 | exact |
| Z edges | -46,-24 | exact |
| Water surface y | -0.81 | -0.809997559 |
| Detector center y | water surface minus 1 = -1.81 | -1.809997559 |
| Detector dimensions | [6,6,22] | exact |
| Respawn | [5.5,-0.0797,-35] + ball lift 0.11 | [5.5,0.030303955,-35] |

HazardId=kettle_pool, penalty=1. Detector CanCollide/CanQuery=false is intentional; gameplay checks its volume rather than raycasting it. No horizontal position, size, yaw or edge difference found. Vertical differences are <0.000004 studs.

At the reported endpoint [10.27,-47.47], the ray hits `shelf_ne` at y=-0.148788452. This is **1.47 studs north of the authored pool boundary**, and is inside the authored shelf, not an omitted portion of the specified pool. This endpoint alone does not establish where the earlier moving ball entered water; trajectory/hazard handling and any desired footprint expansion belong to a subsequent investigation/design change.

Sixteen dense-grid misses occur exactly at the outer mathematical shelf edge x=14.5. Supplemental rays at 14.499 hit, and 14.501 miss. These are floating-point boundary ownership at the outside edge, not an interior seam/gap. At z=-46.001 the shelf is present; at -45.999, x>8.5, the felt correctly ends over the pool. The shelf/shelf_ne join at x=8.5 differs by only the authored rounding (~0.00002 stud), with continuous sampled support.

## Disposition and artifacts

No real mismatch requiring a source fix was found in the requested scope. **No geometry, holes.json, Config, generator or CourseBuilder edits.** Consequently the conditional rebuild, cupdrop 3 + random 8, H6 short-putt 10 and H18 slow-roller 10 checks were not triggered and were not run. No new runtime success is claimed.

Studio was closed without saving. `final-state.json` verifies no Studio process and identical input SHA256 before/after (`7338048959d2b566a812be21e36fe1e14d48c483e9ef27e6eca262a2953c0827`); no v3b exists. Native H18/H6 views were inspected through MCP screenshots. Existing unrelated asset changes remain unstaged.

Evidence: `playtests/stage-ah/{preflight,authored-h6-h18,h6-profile,h18-profile,summary,supplemental,final-state}.json`. Tools: `tools/stage_ah_profile.py`, `tools/stage_ah_profile.luau`, `tools/stage_ah_analyze.py`. Profile transport uses 50k-character chunks to avoid Studio MCP's 100k text truncation; the temporary `_G` string is cleared afterward. Notes and tools/evidence committed locally under the requested message; no rbxl or screenshots committed.
