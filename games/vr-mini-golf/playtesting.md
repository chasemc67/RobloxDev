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
| `bank` | Hole 2's 45° bank wall at 4 and 6 m/s: speed and angle in/out |
| `walls` | Hole 1's end wall head-on (3 and 6 m/s), hole 1's side wall at 45°, hole 2's bumper post head-on and with a 45° contact normal. Normal restitution, tangential retention, speed kept right after the hit and 0.3 s later (skid) |
| `windmill` | Hole 4 at 4 m/s, timed to two blade phases |
| `hill` | Hole 3: 5 m/s makes the green, 2 m/s rolls back down |
| `cup` | Hole 1 from 60 cm at 1.3–4 m/s: holed or not, speed at the rim, holed on the first pass. Contacts inside the cup (the ball dropping against the rim/liner) don't count against "first pass" |
| `ledge` | (SimulateVR) Ball against a wall or rail. The (fake) club is held over the ledge and the player stance is on or over the wall. Logs ball-plane Y vs VR rig floor, character feet and putter head bottom. Pass = all within 0.05 studs (character 0.1) |
| `clubviz` | (SimulateVR) Holds the club hand in a putting grip next to a ball (hand 0.91 m up, handle aimed at the ball), with the legacy mount and then the grip mount. Pass: the shaft is within 2° of the handle axis, starts at the handle bottom, and puts the head on the ball's plane right behind the ball. Then presses A (refit): shaft vertical from the handle bottom, head on the plane |
| `ghost` | (SimulateVR) Sweeps the putter head through a wall and a bumper post at ball-plane height. Checks it follows the hand exactly (no pushback, no climbing), the club parts can't collide/touch, and the ball doesn't move. Then makes a real simulated VR swing through the ball (face speed 1.2 m/s → ball speed = face speed × `VRHitMultiplier`) |

**Adding a scenario:** add a `scenario({ name, desc, seconds, vr?, run = function() ... end })` block in `src/StarterPlayer/StarterPlayerScripts/GolfClient/GolfTest.luau`. `seconds` is the recording length.

These helpers are available:
- `place(hole, x, z, surfaceY)`: hole 0 is the test lane.
- `shoot(label, dir, speedMps, {cup=, timeout=})`: returns distance, times, contacts, rim speed and outcome.
- `setFrame(focus, size, viewDir)`
- `measureLedge(...)`, `sweep(...)`
- `poseFn`: drives the simulated club hand.

Return a table. Then add a section to `summary_md()` and `key_metrics()` in the runner if you want it in the summary and compare.

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
