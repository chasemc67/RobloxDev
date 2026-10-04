# VR Mini Golf: design

## Pitch
A Walkabout Mini Golf–style course on Roblox. In VR you hold a real putter with room-scale hand tracking. On a phone (or with a mouse) you pull back from the ball to putt.

Original ask (Chase, Claude Code session, 2026-10-03): "make me a mini golf game in Roblox Studio. It should work in VR... basically function just like Walkabout Mini Golf. If you play it on a phone, then it should just have normal 2D controls where you pull your finger back for the force and move the finger side to side for the angle. Build three or four test holes and iterate until it works good."

## Core loop
Tee off, putt until the ball drops, and the server moves everyone to the next hole. After hole 4 there's a shared scorecard and Play Again.

## Course (built procedurally by `ServerStorage.CourseBuilder`)
1. **Warm Up (par 2):** a straight hole with two angled bumpers.
2. **Dogleg (par 3):** a 45° bank wall at the corner and bumper posts guarding the cup.
3. **The Hill (par 3):** a short, gentle ramp to a raised green. A weak putt rolls back down.
4. **Windmill (par 3):** spinning blades in front of a tunnel. Spinners are synced so every player sees the same blade position. The hole is about 13 m long.

The cups are real holes cut into the felt with CSG (8 UnionOperations), so fast putts lip out and slow ones drop. Each player has their own coloured ball with a name tag, and balls don't collide with each other.

## Rules (server-authoritative, `ServerScriptService.GolfServer`)
- 8-stroke max per hole.
- +1 penalty stroke for going out of bounds.
- Automatic advance to the next hole (`HoleTransitionTime` 3.5 s).
- Shared scorecard.

## Scale
Roblox VR draws 1 stud as 0.3 m, so everything is life size:

| Item | Size |
|---|---|
| Ball | 4.8 cm (`BallRadius` 0.08) |
| Cup | 12.6 cm wide, 10.5 cm deep |
| Putter blade | 12.6 cm |
| Walls | 15 cm |

## Controls
**Phone / mouse (`GolfClient.TouchControls`)**
- Press near the ball and pull back. Distance sets power and sideways sets the angle. Release to putt.
- A dotted aim line and a power meter show while you pull. Dragging back to the ball cancels the shot.
- Drag elsewhere to orbit the camera; pinch or scroll to zoom.

**VR (`GolfClient.VRControls`), mapped to Walkabout**

| Input | Action |
|---|---|
| Trigger (either hand) | Warp to your ball in a putting stance |
| Right stick left/right | Snap turn (30°) |
| Right stick forward | Teleport arc; release to teleport |
| Right stick back | Rewind the ball to where the last shot started |
| Left stick | Walk |
| Grip | Grip-to-Putt (off by default; `VRGripToPutt`) |
| B / Y | Scorecard panel; Play Again at the end |
| A | Re-fit the club (point it straight down, then press A) |
| X | Swap hands |

- The putter shaft comes out of the controller's tip (`VRClubTipOffset`, 6 cm in front of the hand origin) along its pointing direction (`VRClubAngle` tilts it). The axis is an assumption until checked on a Quest: see `playtesting.md`.
- Club length fits itself to your height, and the head stretches up to 15 cm to stay on the ground.
- **Hole plane (Walkabout-style):** near the ball, the putter head and your floor sit on the plane of the felt the ball is on (parts tagged `GolfSurface`, ramp slopes included). Walls, rails and posts are never ground. The club ghosts through them, and you can't stand on them (collision group `GolfWall` doesn't collide with players).
- The putter head slides along that plane. Face speed and angle at contact set the ball's velocity, with haptics on hit. The ball is only moved by that hit logic, never by club physics.
- The putter turns see-through while the ball is rolling.
- A wrist panel shows the hole, par and strokes. Messages and the scorecard are world-space panels.

## Ball physics (tuned to Walkabout, see `walkabout-reference.md`)
- **Gravity:** `workspace.Gravity` is 32.7 studs/s² (9.81 m/s²).
- **Fast felt:** deceleration = `RollDecel` 0.5 + `RollDrag` 0.25·v (studs/s²), i.e. 0.15 m/s² + 0.25/s·v. Putts roll a long way and stop softly.
  - `EngineRollLoss` 0.2 compensates for Roblox's own contact losses.
  - A 2 m/s putt rolls about 4.5 m.
- **Walls/bumpers:** `WallElasticity` 0.63 (measures ~0.6 normal restitution), `BumperElasticity` 0.65, low `WallFriction` 0.05.
  - After a hit, the ball keeps half its old spin (`SpinKeep` 0.5) and skids at `SlideFriction` 0.3·g until it rolls again.
  - In practice: about 0.6× speed straight off a wall, and about ⅓–0.4× after 0.3 s.
  - Physics properties live in `Config`. `CourseBuilder.ApplyPhysics()` applies them to the course.
- **Cup:** a ball over the cup slower than `CupCaptureSpeed` (1.6 m/s) drops in. Faster ones skim across or lip out.

## Tuning
All tuning values are in `ReplicatedStorage.Golf.Config` (see `src/ReplicatedStorage/Golf/Config.luau`):
- `VRHitMultiplier` 1.7
- `TouchMaxSpeed` 26
- `VRMoveSpeed` 6.5

## Test hooks (Studio only)
- Workspace attribute `DebugStartHole` starts the round on a later hole.
- Workspace attribute `SimulateVR` = true fakes head and hand tracking, so the VR swing code can be tested without a headset.
- Workspace attribute `GolfTestMode` = true turns on the scripted playtest harness. See `playtesting.md`.

## Not done yet
- No real-headset test yet. VR was only checked in simulation.
- The mobile/2D pass needs work (Chase: "could use some work too, but for now lets just focus on VR").
- No persistence, monetization or badges.
