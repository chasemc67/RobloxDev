# SRV-132 H6 + H11 movers pass 2
Fitcheck FAILED. Source holes.json and library remain unchanged. CanCollide=false; FBX scale 1, forward -Z/up Y, textures embedded.
| FBX | Hole-local pivot | World pivot | Tris | MeshParts |
|---|---|---|---:|---:|
| fbx\h06_sluice_gate.fbx | [0, 0.0, -28.0] | [280.0, 26.0, 227.0] | 300 | 4 |
| fbx\h06_sluice_frame.fbx | [0, 0, -28] | [280.0, 26.0, 227.0] | 476 | 3 |
| fbx\h11_lock_gate.fbx | [0, 0.0, -21.25] | [150.0, 116.0, -273.25] | 180 | 4 |
| fbx\h11_lock_lift.fbx | [0.0, 0.0, -23.0] | [150.0, 116.0, -275.0] | 276 | 4 |
| fbx\h11_lock_chamber.fbx | [0, 0, -23] | [150.0, 116.0, -275.0] | 1684 | 6 |

H6 gate bottom raised .02 above felt, pivot unchanged; source blocker stays at y=0, so the visual bottom .02 strip differs from collision. Pointed board length 7.000051 (rounded .4243 end boxes), painted face skins project .018 beyond blockers. H11 blocker exact 3.6×1.2×.5 covered; nominal deck footprint 3.2x4 with .005 plank seams and a .58-deep full-width south gate slot; top flush at y=0.
H6 frame posts move west -3.6→-12, east 3.6→3.86; extended lintel; pocket trim raised above rails. H11 winch anchors x=±2.6→±3 and z=-21.25→-23; wheels likewise relocated. Chamber walls x=±2.15→±3, length 3.8→2.8; slot cheeks move south clear of deck.
H6 axis +X, offsets -7..0, speed 3, dwells 1.2 at 0/2.0 at -7, period 7.8666667. H11 gate +Y, offsets -1.3..0, speed 2, period 9.6: down 0–5.5, rise 5.5–6.15, up 6.15–8.95, sink 8.95–9.6.
Lift rise 5.50–7.50, tilt 0→4° and release 7.50–7.65, return 7.65–9.15 (untilt first .15 s), bottom until next rise. Gate not fully down 5.5–9.6 = 4.1 s. Bottom .45 s before gate fully down. North-edge hinge z=-25 around Roblox -X; south edge rises. See motion.lua, including CFrame transform and clamp(entrySpeed*.5,1.5,7).
Signal [0,5,-25.4], world [150,121,-277.4], separate Neon SignalRed/SignalGreen. Optional Studio PointLight range 6, brightness 1. Green while gate down; red otherwise.

## Explicit whitelist and Studio requirements
All cuts below are required collision/visual apertures for RobloxDevBot. Passing status applies to residual geometry after cuts; uncut source intersections remain reported in fitcheck. H6 pocket through rail5; west frame now entirely outside sweep. H11 gate slot requires relief at rail4/rail8 tips as well as felt. Remove/hide static lock felt and replace its collision with moving deck. Exit needs a real gap through quay_rail20; rail6 lower north edge and quay felt seam also need clearance relief.
- h06_sluice_gate / rail5: bounds [-10.56, -0.04, -28.38] to [3.56, 1.08, -27.62] (hole-local x,y,z).
- h11_lock_gate / rail4: bounds [-1.86, -1.36, -21.58] to [1.86, 1.26, -20.92] (hole-local x,y,z).
- h11_lock_gate / rail8: bounds [-1.86, -1.36, -21.58] to [1.86, 1.26, -20.92] (hole-local x,y,z).
- h11_lock_gate / felt_lock: bounds [-1.86, -1.36, -21.58] to [1.86, 1.26, -20.92] (hole-local x,y,z).
- h11_lock_lift / felt_lock: bounds [-1.66, -0.21, -25.06] to [1.66, 4.36, -20.94] (hole-local x,y,z).
- h11_lock_lift / rail6: bounds [-1.66, -0.21, -25.06] to [1.66, 4.36, -24.44] (hole-local x,y,z).
- h11_lock_lift / quay_rail20: bounds [-1.66, -0.21, -25.06] to [1.66, 4.36, -24.44] (hole-local x,y,z).
- h11_lock_lift / felt_quay: bounds [-1.66, 3.79, -25.06] to [1.66, 4.36, -24.94] (hole-local x,y,z).

## Clearance evidence
Full-cycle dt≤.005 s, translations≤.015 stud, angular increments≤.134° with additional top tilt sweep≤.25°. Triangle/OBB SAT conservative signed lower bounds; static detail primitives conservatively AABB-enclosed. Static felt overlap≤.001 accepted; H6 lifted felt .0195 accepted per lead. Every other pair and cut residual must clear .05.
Minimum non-exempt: {"prop": "h06_sluice_gate", "obstacle": "rock18", "clearance": -0.5000255107879639, "time": 0.0, "offset": 0, "tilt": 0, "location": [3.200000047683716, 0.019999980926513672, -28.100000003973644], "kind": "rail/wall", "residual_cut": false, "status": "FAIL"}
Exact exit raw reports:
- rail6: {"clearance": -8.326672684688674e-17, "time": 0.0, "offset": 0, "tilt": 0, "location": [-1.5499999523162842, -0.09166666368643443, -24.96666669845581]}
- quay_rail20: {"clearance": -0.4975060327932789, "time": 7.65, "offset": 4.0, "tilt": 4.0, "location": [1.5500000715255737, 3.9733158216944493, -24.664822148489833]}
- felt_quay: {"clearance": 0.002493967206721237, "time": 7.65, "offset": 4.0, "tilt": 4.0, "location": [-1.600000023841858, 3.9733158216944493, -24.664822148489833]}
The source rail6 is centered [0,.95,-25.25], spans y=-.5..2.4, z=-25.5..-25.0: lower edge contact only, no meaningful penetration. quay_rail20 is [0,4.25,-24.75], spans y=3.5..5,z=-25..-24.5: actual raised exit obstruction, not a mislabeled rail6. Quay felt starts z=-25 at y=4; the seam has only .002494 signed lower-bound clearance and needs the listed relief. All are designed exit gaps.

## Previews and handoff
20 REVIEW PNGs in out/previews/cycles/review, Cycles OptiX on RTX 4090, rest and maximum, eye (height 5) and 3/4. Static max duplicates rest for consistent review. Five-stud capsule included. FBX round-trip mesh counts passed.
Re-sync the five meshes in Studio; implement listed apertures, replace static lock floor, and use motion.lua. Existing teleported ball release stays at [0,4,-27] toward -Z. No manifest.json edited; H9/H14/H17 untouched.

Gate slot travels with the moving replacement felt/deck, local z=1.42..2 (hole z=-21.58..-21). Full-cycle gate/platform minimum .061999917 stud. Lift tilt transform corrected to preserve original y before computing z; no spurious height-dependent north translation.

## Conflicts outside supplied whitelist
No final passing certificate issued. Additional cuts proposed separately, pending the lead decision.
- h06_sluice_gate / rock18: {"clearance": -0.5000255107879639, "time": 0.0, "offset": 0, "tilt": 0, "location": [3.200000047683716, 0.019999980926513672, -28.100000003973644], "kind": "rail/wall", "residual_cut": false, "status": "FAIL"}
- h11_lock_gate / rail5: {"clearance": -0.19999995231628437, "time": 0.0, "offset": -1.3, "tilt": 0, "location": [-1.7999999523162842, -0.4999999682108562, -21.166666666666668], "kind": "rail/wall", "residual_cut": false, "status": "FAIL"}
- h11_lock_gate / rail7: {"clearance": -0.1999999523162841, "time": 0.0, "offset": -1.3, "tilt": 0, "location": [1.400000015894572, -0.519999929269155, -21.51800000667572], "kind": "rail/wall", "residual_cut": false, "status": "FAIL"}
- h11_lock_gate / felt_approach: {"clearance": -0.019999980926513672, "time": 5.59, "offset": -1.1200000000000003, "tilt": 0, "location": [-1.3599998950958252, -0.3399999292691552, -20.986666684349377], "kind": "felt", "residual_cut": false, "status": "FAIL"}
- h11_lock_lift / rail5: {"clearance": -2.3841858015627437e-08, "time": 0.0, "offset": 0, "tilt": 0, "location": [-1.600000023841858, -0.050000001986821495, -21.71999994913737], "kind": "rail/wall", "residual_cut": false, "status": "FAIL"}
- h11_lock_lift / rail7: {"clearance": -2.3841857821338408e-08, "time": 0.0, "offset": 0, "tilt": 0, "location": [1.5666667222976685, -0.050000001986821495, -24.49749994277954], "kind": "rail/wall", "residual_cut": false, "status": "FAIL"}
- PROPOSED CUT {"prop": "h06_sluice_gate", "obstacle": "rock18", "min": [-10.56, -0.04, -28.38], "max": [3.56, 1.08, -27.62]}
- PROPOSED CUT {"prop": "h11_lock_gate", "obstacle": "rail5", "min": [-1.86, -1.36, -21.58], "max": [1.86, 1.26, -20.92]}
- PROPOSED CUT {"prop": "h11_lock_gate", "obstacle": "rail7", "min": [-1.86, -1.36, -21.58], "max": [1.86, 1.26, -20.92]}
- PROPOSED CUT {"prop": "h11_lock_gate", "obstacle": "felt_approach", "min": [-1.86, -1.36, -21.58], "max": [1.86, 1.26, -20.92]}
- PROPOSED CUT {"prop": "h11_lock_lift", "obstacle": "rail4", "min": [-1.66, -0.21, -25.06], "max": [1.66, 4.36, -20.94]}
- PROPOSED CUT {"prop": "h11_lock_lift", "obstacle": "rail5", "min": [-1.66, -0.21, -25.06], "max": [1.66, 4.36, -20.94]}
- PROPOSED CUT {"prop": "h11_lock_lift", "obstacle": "rail7", "min": [-1.66, -0.21, -25.06], "max": [1.66, 4.36, -20.94]}
- PROPOSED CUT {"prop": "h11_lock_lift", "obstacle": "rail8", "min": [-1.66, -0.21, -25.06], "max": [1.66, 4.36, -20.94]}
- PROPOSED CUT {"prop": "h11_lock_lift", "obstacle": "felt_approach", "min": [-1.66, -0.21, -25.06], "max": [1.66, 4.36, -20.94]}

At height=4, tilt=0, the aggregate platform/quay_rail20 overlap envelope is x=[-1.6,1.6], y=[3.85,4.0], z=[-25,-24.5] (plank seams excluded from occupied material). At max tilt, worst triangle/OBB signed lower bound is -.497506 at t=7.65. This is the raised quay obstruction. rail6 instead contacts the north edge at z=-25 at rest; its clearance-relief cut is separate.
Proposed additional cuts sweep: minimum .059974432 at H6 gate/east frame post, t=0, offset=0, location [3.3000085,.6866666,-28.2000085]. This proposed result does not authorize extra cuts or replace the failed approved-whitelist result.