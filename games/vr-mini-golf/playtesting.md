# VR Mini Golf: playtesting

How to measure and record the game's feel without a headset, and what still needs one.

## Test mode (Studio only)

The harness is **off in normal play**. It only starts when both are true at the moment you press Play:
- `RunService:IsStudio()`
- workspace attribute `GolfTestMode == true`

| Workspace attribute | Effect |
|---|---|
| `GolfTestMode` (bool) | Starts `GolfServer.GolfTestServer` (builds the flat `GolfTestLane` off to the side at x = -40, adds `ReplicatedStorage.Golf.GolfTestRemote`) and `GolfClient.GolfTest` (scenarios, logging, cameras, `ReplicatedStorage.GolfTestAPI`) |
| `SimulateVR` (bool) | Fakes head and hand tracking from the CFrameValues in `ReplicatedStorage.VRDebug`, so `VRControls` runs without a headset. The `ledge` and `ghost` scenarios need this |
| `GolfTestCamera` | `""` (normal), `"fixed"` (3/4 view of the scenario area), `"topdown"`, or `"follow"` (chase cam behind the ball) |
| `GolfTestFocus` / `GolfTestFrameSize` / `GolfTestViewDir` | Framing for the cameras. Each scenario sets these itself |
| `GolfTestClubDebug` (bool) | Draws the club debug overlay: a part-built Quest Touch proxy at the club hand plus axis gizmos (see below) |
| `GolfTestCamPos` / `GolfTestCamUp` / `GolfTestFOV` | Framing for the `"look"` camera (from `GolfTestCamPos` at `GolfTestFocus`) |
| `DebugStartHole` | (Not test mode) Start the round on a later hole |

The runner sets and clears all of these for you.

Every scripted shot goes through `Ball.hit()` in `GolfClient.BallController`, the same function the VR putter (`Ball.clubImpulse` → `Ball.hit`) and the phone pull-back use. The `ghost` scenario also makes a real simulated VR swing through the ball, so it exercises the putter contact code end to end.

## Runner

`tools/run_playtests.py` uses only the Python stdlib plus `tools/studio_mcp.py`. It only ever talks to the Studio whose name contains placeId 87725688219952.

```bash
cd ~/src/RobloxDev/games/vr-mini-golf
python3 tools/run_playtests.py list
python3 tools/run_playtests.py run                          # all scenarios -> playtests/<today>/
python3 tools/run_playtests.py run walls cup --out /tmp/x   # a subset
python3 tools/run_playtests.py run --cams fixed,topdown,follow --record --out playtests/<date>/after
python3 tools/run_playtests.py compare playtests/2026-10-03/baseline playtests/2026-10-03/after
python3 tools/run_playtests.py smoke     # normal solo playtest: errors/warnings + HUD texts, test mode off
python3 tools/run_playtests.py push src/<path>.luau ...    # copy edited src/ files into Studio (Edit)
python3 tools/run_playtests.py export    # mirror every Studio script into src/ (run before committing)
python3 tools/run_playtests.py clubviz --out playtests/<date>-clubfix   # VR club mount screenshots, before/after
```

- `clubviz` captures the Studio window (`screencapture -l<window id>`) for each view and crops it to the game viewport (the 2 px blue play border, minus the CoreGui strip).
  - Mounts: legacy aim ray, then the grip mount.
  - Views: `side`, `front`, `top`, `side_close`, `front_close`.
  - It writes `before_<view>.png`, `after_<view>.png` and `clubpose.json`.

- `run` does the following:
  1. Stops play and sets `GolfTestMode` + `SimulateVR` (unless `--no-vr`).
  2. Starts play and runs each scenario once per camera.
  3. Pulls the logs and writes `<scenario>[-<cam>].jsonl`, `results.json` and `summary.md`.
  4. Stops play and clears the attributes.
- With `--record`, it brings the "VR Mini Golf" Studio window to the front (via `tools/studio_window.py`, which uses pyobjc through `uv`). It then records that window rect with `screencapture -v` for each scenario/camera into `<scenario>-<cam>.mov`. Use `--rect x,y,w,h` to override the rect. The `.mov` files are gitignored.
- Logs:
  - Each scenario's JSONL has a header (config and physics properties), ~30 Hz samples `{p, v, s}`, and events: `placed`, `hit`, `contact`, `rest`, `cup`, `oob`, `shot`, `ledge`, `sweep`, `swing`.
  - The final line is `result`.
  - Compact event lines are also printed to the client output prefixed `GOLFTEST|`.
- `compare` prints a before/after table of the key numbers from two `results.json` files.

**Workflow for changes:**
1. Edit `src/`.
2. Run `push`.
3. Run `run <scenarios>`.
4. Repeat.
5. When you're done, run `export`, so `src/` mirrors Studio exactly.

`push` refuses to run while Studio is in play mode.

**Course physics:** wall/bumper physics come from `Config`. After changing them, re-apply them to the live course in Edit. The command bar caches modules, so pass fresh clones:
```lua
require(game.ServerStorage.CourseBuilder:Clone()).ApplyPhysics(nil, require(game.ReplicatedStorage.Golf.Config:Clone()))
```

## Scenarios

| Name | What it measures |
|---|---|
| `rollout` | 2/4/6 m/s straight putts on the flat test lane: distance and time vs the rolling model (`RollDecel + RollDrag·v`) |
| `bank` | Hole 1 Lantern Gate's 45° timber deflector at 4 and 6 m/s: speed and angle in/out |
| `walls` | Hole 1's green rail head-on (3 and 6 m/s), hole 1's lane rail at 45°, hole 3's toadstool stool bumper head-on and at 45°. Normal restitution, tangential retention, speed kept right after the hit and 0.3 s later (skid) |
| `hill` | Hole 9's 1-stud ramp: 5 m/s makes the landing, 2 m/s rolls back down |
| `cup` | Hole 1 (cup radius 0.5 stud) from 60 cm at 1.3–4 m/s: holed or not, speed at the rim, holed on the first pass. Contacts inside the cup (the ball dropping against the rim/liner) don't count against "first pass" |
| `movers` | Every moving part: server constraint value vs the spec at server time, each blocker's pose vs the spec formula, server network ownership, and how far behind the client sees it (replication lag) |
| `h1` … `h9` | The per-hole suites (Lantern Grove), see below |
| `h7pin` | Hole 7's sliding log: 30 balls parked in / beside the log's path at both ends of its travel and 12 slow putts into it at 4 phases. Logs contact time at ~0 speed and the unstick nudges |
| `h8door` | Hole 8's sliding root door: balls parked against the alcove rails at the door's ends of travel (the crush case) |
| `progress` | (best with SimulateVR) Sinks holes 1 → 9 in turn: the server moves the ball to the next tee, the VR rig warps beside it, the HUD title changes, and the final 9-hole scorecard (par 27) opens |
| `ledge` | (SimulateVR) Ball against a wall or rail. The (fake) club is held over the ledge and the player stance is on or over the wall. Logs ball-plane Y vs VR rig floor, character feet and putter head bottom. Pass = all within 0.05 studs (character 0.1) |
| `clubviz` | (SimulateVR) Holds the club hand in a putting grip next to a ball (hand 0.91 m up, handle aimed at the ball), with the legacy mount and then the grip mount. Pass: the shaft is within 2° of the handle axis, starts at the handle bottom, and puts the head on the ball's plane right behind the ball. Then presses A (refit): shaft vertical from the handle bottom, head on the plane |
| `ghost` | (SimulateVR) Sweeps the putter head through a wall and a bumper post at ball-plane height. Checks it follows the hand exactly (no pushback, no climbing), the club parts can't collide/touch, and the ball doesn't move. Then makes a real simulated VR swing through the ball (face speed 1.2 m/s → ball speed = face speed × `VRHitMultiplier`) |

**Adding a scenario:** add a `scenario({ name, desc, seconds, vr?, run = function() ... end })` block in `src/StarterPlayer/StarterPlayerScripts/GolfClient/GolfTest.luau`. `seconds` is the recording length.

These helpers are available:
- `place(hole, x, z, surfaceY)`: world coordinates; hole 0 is the test lane.
- `placeL(hole, x, z, y?)`: spec-local coordinates (straight from `holes.json` / `hNN-notes.md`), on the felt under that point.
- `W(hole, x, y, z)` / `WD(hole, dx, dz)` / `aimDir(hole, deg)`: spec-local point / direction / notes-style aim angle (atan2(dz, dx)) to world.
- `shootS(label, dir, studsPerSec, opts)`: `shoot` in studs/s that also classifies out-of-bounds as `hazard` (water / rabbit hole) or `escape`, collects flags, and waits for the re-placement after an OOB.
- `waitPhase(hole, t)`: waits until the hole's moving parts, as this client sees them, are at spec time `t` (mod the hole's `MoverPeriod`).
- `playHole(hole, skill)`: plays the hole from the tee like the designer's sim golfer (cup if allowed and in sight, else the furthest `ai_waypoints` target), with the flat-felt speed model plus √(2gΔh) for climbs.
- `shoot(label, dir, speedMps, {cup=, timeout=})`: returns distance, times, contacts, rim speed and outcome.
- `setFrame(focus, size, viewDir)`
- `measureLedge(...)`, `sweep(...)`
- `poseFn`: drives the simulated club hand.

Return a table. Then add a section to `summary_md()` and `key_metrics()` in the runner if you want it in the summary and compare.

## Lantern Grove per-hole scenarios (`h1` … `h9`)

Each `hN` suite runs on hole N, in this order (`GolfTestOpts.parts` picks a subset):

| Part | What it does | Pass / flag |
|---|---|---|
| `routes` | Two full plays from the tee with the spec's `ai_waypoints`: `good` = the aggressive/risk line from `hNN-notes.md` (H2 left chute, H5 root bridge, H8 firefly ring), `average` = the safe line (H2 right chute, H5 covered bridge, H8 long route) | Strokes vs par, holed, every stroke's target, outcome and finishing zone |
| `hio` | The notes' ace line (aim, speed, mover phase), then candidate lines from `tools/engine_sim.py` (if `--engine-sim`), a ±8° scan at 100% / 88% power, and a Newton/Broyden refinement on the miss vector. Stops at the first ace | `ace`, best miss (studs) |
| `banks` | Two rail/bank shots per hole (e.g. H1 deflector, H3 both banked corners, H6 both boards, H9 bank + root deflector) | First contact: part, normal restitution, angles in/out |
| `sweep` | For each moving part: the ace line (or first intended shot) at N evenly spaced phases of that part's cycle | Blocked or clear, finishing zone, flags |
| `fuzz` | Random shots (any direction, 20–100% power) from the tee and from random spots on the felt | Hazards, **escapes**, **stuck**, nudges |

**Automatic stuck / escape detection** (every scripted shot, all scenarios):
- **escape**: the server's out-of-bounds (below the hole's `KillY` or outside its `Bounds`) while the ball was **not** over a hazard footprint (`Hazards/Hazard`). The server writes it to the ball's `LastOOB` attribute (`escape` or `hazard:<id>`); water and the rabbit hole count as hazards.
- **fell**: the client saw the ball more than 3 studs below the hole's lowest felt (`FeltMinY`).
- **stuck**: a shot that never finished (timeout), a rest that isn't on felt (`Ball.OffSurface`, also gives a free reset to the stroke start), a "wedged" rest (below `StopSpeed` for 2 s on a slope) or the 25 s `MaxRollTime` cap (`Ball.ForcedRest`).
- **unstuck**: the pin/unstick nudge fired (`Ball.Unstuck`: touching a moving part at ~0 speed, or riding on one, for > 0.5 s, moving or at rest). It hops the ball to the nearest clear felt spot sideways of the part's motion.
- Teleports (`Ball.Teleported`) are logged as flags but aren't issues.

Options (JSON in workspace attribute `GolfTestOpts`, set with `--opts`): `parts` (default `"routes,hio,banks,sweep,fuzz"`), `fuzz` (shots, default 12), `sweep` (phases per moving part, default 6), `hioTries` (default 30), `seed`, `hioLines` (`{"<hole>": [[aim, speed, phase], ...]}`, filled by `--engine-sim`).

**Engine-calibrated sim** (`tools/engine_sim.py`): a patched copy of the designer's `tools/sim.py` with the game's measured rail response (normal restitution 0.60, tangential 0.93, then BallController's post-impact skid, net `v = v_out + 0.5·(v_in − v_out)/3.5`). It brute-forces aim × speed (× phase) from each tee in ~25 s for all 9 holes and prints candidate ace lines; only an in-engine ace counts.

### Playtest Bot: how to run the per-hole scenarios

Studio must be open on place 87725688219952 (VR Mini Golf), in Edit mode, with the Studio MCP enabled. Then, from the repo:
```bash
cd ~/src/RobloxDev/games/vr-mini-golf
# 1. all 9 hole suites (~75 min), HIO seeded by the engine sim; then the H7 log pin hunt, H8 door test, mover check:
python3 tools/run_playtests.py holes --engine-sim --opts '{"fuzz":12,"sweep":6,"hioTries":24}' --out playtests/<date>-lantern
python3 tools/run_playtests.py run h7pin h8door movers --no-vr --out playtests/<date>-lantern/movers
# 2. one or a few holes, a subset of parts (fast):
python3 tools/run_playtests.py holes 7 --opts '{"parts":"routes,sweep","sweep":8}' --out /tmp/h7
# 3. progression (fade to black + next tee + VR warp) and VR checks (SimulateVR on):
python3 tools/run_playtests.py run progress ledge ghost --out playtests/<date>-lantern/vr
# 4. screenshots: holeNN.png (3/4 view, HUD on), topdown_hNN.png, follow_hNN_a/b.png (ace-line chase cam, ball height):
python3 tools/run_playtests.py shots --out playtests/<date>-lantern/shots
#    world stills from Edit mode (the play client doesn't draw terrain/parts from ~1000 studs up):
python3 tools/run_playtests.py overview --out playtests/<date>-lantern/shots     # overview.png + overview_aerial.png
# 5. normal play check (test mode off), desktop then phone emulation: errors/warnings, HUD, ball on the tee, perf counts:
python3 tools/run_playtests.py smoke
python3 tools/run_playtests.py smoke --device iphone_17_pro
```
Read `<out>/summary.md` (per-hole table: lines, ace, banks, sweep, fuzz, escapes/stuck/nudges) and **look at the PNGs**. Anything in the "Escapes / stuck / nudges" column or the `hN issues` lines is a bug to fix (positions are world coordinates; each `HoleN` model's `HoleOrigin`/`HoleYaw` attributes give its frame, and every scenario works in those hole-local frames, so it doesn't matter where a hole sits in the world).

### Rebuilding the world (after a spec, world map or prop update)
All steps run against Studio in Edit mode and are idempotent:
```bash
python3 tools/holes_to_lua.py --push            # holes.json -> CourseData.LanternGrove
python3 tools/world_to_lua.py --push --build    # world.json -> CourseData.WorldLayout, rebuild workspace.Course in the world
python3 tools/world_terrain.py                  # terrain-4stud.json -> Terrain, carve every felt piece, clearance check (expect 0 intrusions)
python3 tools/props_to_lua.py --push            # models/manifest.json -> CourseData.PropPlacements
# in Studio (command bar / MCP execute_luau, Edit):
#   require(game.ServerStorage.WorldBuilder:Clone()).BuildScenery()   -- workspace.World: walkways, water, tree, backdrop, lanterns
#   require(game.ServerStorage.PropsBuilder:Clone()).Place()          -- HoleN/Decor/Props + mover visuals
```
- Moving a hole: edit its `placement` (origin, yaw) in world.json and rerun the last four steps. Hole geometry, harness, tees, cups, teleports, movers and the VR next-tee warp all follow the hole frame. Set `enabled = false` in `CourseData.WorldLayout` to get the flat greybox back.
- New props from 3D Model Bot: `blender -b --factory-startup -P models/library/make_library.py -- <models> <models>/library`, import `lg_lib_a/b.fbx` with File > Import 3D (unit Stud; `tools/codex_ui.sh codex-import logs/prompts/import_props.md`), then `PropsBuilder.PrepareLibrary()` (detects and undoes the importer's 180-degree turn, applies the manifest materials, makes every part decoration-only) and `Place()`.

## VR club: grip axis (needs a headset to confirm)

How `VRService:GetUserCFrame(Enum.UserCFrame.RightHand/LeftHand)` is read, for Quest Touch (Roblox reports the OpenXR **aim** pose, as far as we can tell):
- **-Z (LookVector)** is the aim/laser ray out of the front of the controller.
- **+Y** is the top of the controller (face buttons).
- **+X** is the controller's right.
- **The handle** runs from the top down along -Y, raked back toward +Z (pistol-grip style: the bottom of the grip sits down and back toward the wrist). It is ~90° + rake from the aim ray.

Up to v9 the shaft ran along -Z, so on a real Quest it came out ~perpendicular to the handle (fixed 2026-10-09, see `playtests/2026-10-09-clubfix/NOTES.md`). Now `VRControls.defaultClubMount` builds the club like this:
```
gripRot  = Angles(rad(-90 - VRClubGripPitch), 0, 0) * Angles(0, rad(±VRClubGripYaw), 0) * Angles(0, 0, rad(±VRClubGripRoll))
clubButt = gripRot.LookVector * VRClubButtOffset      -- bottom of the handle, hand space
clubCF   = handCF * CFrame.new(clubButt) * clubOffset -- clubOffset = gripRot, or the A-button fit
shaft    = from clubCF.Position along clubCF.LookVector, length auto-fit from eye height (+ up to 15 cm stretch)
```
- **Defaults:** pitch 35°, yaw 0, roll 0, butt 0.25 studs (7.5 cm).
- **Left hand:** pitch is a rotation about hand X, which the left/right mirror (across the hand YZ plane) leaves alone, so it is the same for both hands. Yaw and roll are negated for the left hand.
- **Legacy mount:** `VRClubLegacyAim = true` brings back the old tip/aim-ray mount (`VRClubTipOffset`, `VRClubAngle`).

**What Chase should check on the Quest (both hands; X swaps hands):**
1. Does the shaft continue the line of the handle?
   - Tilted toward the front or back of the controller: adjust `VRClubGripPitch` (+ rakes the shaft back toward your wrist).
   - Tilted sideways: adjust `VRClubGripYaw`.
2. Does it start at the bottom of the handle? Adjust `VRClubButtOffset`.
3. Is the putter face square when the controller is held naturally? Adjust `VRClubGripRoll`.
4. If the shaft points along the controller's front/back instead (Roblox reporting the OpenXR grip pose, where the handle bottom is +Z): `VRClubGripPitch` ≈ 90.
5. A (hold the club straight down, press A) still refits the angle and length per player, from the bottom of the handle.

**Visual check without a headset:** `run_playtests.py clubviz`, or `GolfTestAPI` `clubpose` (legacy, view). The overlay shows:
- **The controller proxy:**
  - Handle: the dark cylinder along the physical grip axis.
  - Orange ring: the handle bottom.
  - Grey disk: the tracking ring.
  - Red block: the trigger.
- **Gizmos** (X red, Y green, Z blue): thick = hand, thin = club mount at the shaft start.
- **Yellow:** the aim ray.
- **Skin sphere:** the player's head.

## Plane snap and ghosting (how it works now)

**Hole plane:**
- `CourseBuilder.ApplyPhysics()` tags the playable felt (`Felt`, `CupPlate`, `Ramp`) with CollectionService `GolfSurface`.
- `VRControls` raycasts **only** against `GolfSurface` under the ball to get the ball's plane (point and normal, so The Hill's ramp works too).
- Within `Config.VRPlaneRange` (12 studs) of the ball:
  - The putter head is clamped to that plane.
  - The VR rig floor and character stand at the ball's contact height.
- Walls, rails and posts never count as ground.

**Walls are not standable:** walls, bumpers, the windmill house, roof and blades are in collision group `GolfWall`:

| `GolfWall` vs | Collides? |
|---|---|
| `GolfBall` | yes |
| `Default` | yes |
| `GolfPlayer` | no |
| `GolfClub` | no |

On top of that, the VR character's Humanoid is `PlatformStand`, with a local anti-gravity `VectorForce`, and it's pivoted onto the rig every frame.

**Club ghosting:**
- All putter parts are `Anchored`, `CanCollide`/`CanTouch`/`CanQuery = false`.
- The club's ground raycasts ignore `GolfWall`.
- The ball is only moved by `Ball.hit()` from the swing-contact logic, never by physical contact.

## What needs a real headset

- Club grip axis (above): `VRClubGripPitch`/`Yaw`/`Roll`, `VRClubButtOffset`.
- How the swing feels and `VRHitMultiplier` with real tracking noise and haptics.
- Comfort of the rig height snapping to the ball's plane when you walk across a wall or up The Hill (it eases at 10/s).
- Real Quest floor calibration (`UserCFrame.Floor`). SimulateVR always uses floor 0.
- Whether others see the PlatformStand VR avatar sensibly. The local player is hidden; the avatar just follows your head.
