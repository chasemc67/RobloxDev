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
```

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
| `bank` | Hole 2's 45° bank wall at 4 and 6 m/s: speed and angle in/out |
| `walls` | Hole 1's end wall head-on (3 and 6 m/s), hole 1's side wall at 45°, hole 2's bumper post head-on and with a 45° contact normal. Normal restitution, tangential retention, speed kept right after the hit and 0.3 s later (skid) |
| `windmill` | Hole 4 at 4 m/s, timed to two blade phases |
| `hill` | Hole 3: 5 m/s makes the green, 2 m/s rolls back down |
| `cup` | Hole 1 from 60 cm at 1.3–4 m/s: holed or not, speed at the rim, holed on the first pass. Contacts inside the cup (the ball dropping against the rim/liner) don't count against "first pass" |
| `ledge` | (SimulateVR) Ball against a wall or rail. The (fake) club is held over the ledge and the player stance is on or over the wall. Logs ball-plane Y vs VR rig floor, character feet and putter head bottom. Pass = all within 0.05 studs (character 0.1) |
| `ghost` | (SimulateVR) Sweeps the putter head through a wall and a bumper post at ball-plane height. Checks it follows the hand exactly (no pushback, no climbing), the club parts can't collide/touch, and the ball doesn't move. Then makes a real simulated VR swing through the ball (face speed 1.2 m/s → ball speed = face speed × `VRHitMultiplier`) |

**Adding a scenario:** add a `scenario({ name, desc, seconds, vr?, run = function() ... end })` block in `src/StarterPlayer/StarterPlayerScripts/GolfClient/GolfTest.luau`. `seconds` is the recording length.

These helpers are available:
- `place(hole, x, z, surfaceY)`: hole 0 is the test lane.
- `shoot(label, dir, speedMps, {cup=, timeout=})`: returns distance, times, contacts, rim speed and outcome.
- `setFrame(focus, size, viewDir)`
- `measureLedge(...)`, `sweep(...)`
- `poseFn`: drives the simulated club hand.

Return a table. Then add a section to `summary_md()` and `key_metrics()` in the runner if you want it in the summary and compare.

## VR club: axis assumption (needs a headset to confirm)

`VRService:GetUserCFrame(Enum.UserCFrame.RightHand/LeftHand)` is used like this:
- **LookVector is the controller's pointing axis.** On Quest/OpenXR that's the direction the ray/laser comes out of the front of the controller. Roblox's own VR laser pointer uses the same axis.
- **The CFrame's origin is roughly in the middle of the controller.**
- I couldn't find documentation or DevForum posts that pin down whether Roblox reports the OpenXR *grip* pose or *aim* pose, so this is an assumption.

Based on that assumption, `VRControls.updatePutter` builds the club like this:
```
clubCF  = handCF * CFrame.new(0, 0, -Config.VRClubTipOffset) * clubOffset
clubOffset = CFrame.Angles(rad(Config.VRClubAngle), 0, 0)   -- or the A-button fit
shaft   = from clubCF.Position along clubCF.LookVector, length auto-fit from eye height
```
So the shaft starts `VRClubTipOffset` (0.2 studs = 6 cm) in front of the hand origin, at the controller tip. It runs along the pointing axis, tilted by `VRClubAngle` degrees (positive = toward the controller's top).

**What Chase should check on the Quest:**
1. Does the shaft come out of the front tip of the controller? If it starts inside the controller or in front of it, adjust `VRClubTipOffset`.
2. Does the shaft continue along the controller's pointing direction? If it's tilted up or down relative to the controller, adjust `VRClubAngle`. Roblox could be reporting the grip pose, which is tilted ~30–40° from the pointing ray on Quest Touch controllers; then `VRClubAngle` ≈ ±35 fixes it.
3. A (point the club straight down and press A) still re-fits the angle and length per player.

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

- Club origin/axis (above), `VRClubAngle`, `VRClubTipOffset`.
- How the swing feels and `VRHitMultiplier` with real tracking noise and haptics.
- Comfort of the rig height snapping to the ball's plane when you walk across a wall or up The Hill (it eases at 10/s).
- Real Quest floor calibration (`UserCFrame.Floor`). SimulateVR always uses floor 0.
- Whether others see the PlatformStand VR avatar sensibly. The local player is hidden; the avatar just follows your head.
