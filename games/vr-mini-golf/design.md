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

- The putter shaft follows the controller's pointing direction (`VRClubAngle` tilts it).
- Club length fits itself to your height, and the head stretches up to 15 cm to stay on the ground.
- The putter head slides along the ground. Face speed and angle at contact set the ball's velocity, with haptics on hit.
- The putter turns see-through while the ball is rolling.
- A wrist panel shows the hole, par and strokes. Messages and the scorecard are world-space panels.

## Tuning
All tuning values are in `ReplicatedStorage.Golf.Config` (see `src/ReplicatedStorage/Golf/Config.luau`):
- `RollDecel` 3.6 sets felt friction. A ~2 m/s stroke rolls about 4.7 m.
- `VRHitMultiplier` 1.7
- `TouchMaxSpeed` 26
- `VRMoveSpeed` 6.5

## Test hooks (Studio only)
- Workspace attribute `DebugStartHole` starts the round on a later hole.
- Workspace attribute `SimulateVR` = true fakes head and hand tracking, so the VR swing code can be tested without a headset.

## Not done yet
- No real-headset test yet. VR was only checked in simulation.
- The mobile/2D pass needs work (Chase: "could use some work too, but for now lets just focus on VR").
- No persistence, monetization or badges.
