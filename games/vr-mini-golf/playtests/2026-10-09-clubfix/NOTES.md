# VR club mount fix: shaft parallel to the controller handle (2026-10-09)

## Problem and root cause
- On a real Quest, the putter came out roughly **perpendicular** to the controller handle.
- `VRControls.updatePutter` built the shaft as `handCF * CFrame.new(0, 0, -VRClubTipOffset) * Angles(VRClubAngle, 0, 0)`, i.e. along the hand CFrame **LookVector (-Z)**.
- -Z is the aim/laser ray: it comes out of the front of the controller.
- On Quest Touch the handle runs along -Y raked back toward +Z (like a pistol grip). So the handle is 90° + rake ≈ **125°** away from the aim ray.
- Holding the controller like a putter grip (handle down at the ball) points the aim ray forward-up, so the old shaft went forward-up into the air. In this pose the old head floated **4.98 studs (1.5 m)** above the felt.

## Fix
- **Shaft direction:** in hand space, `CFrame.Angles(rad(-90 - VRClubGripPitch), 0, 0) * Angles(0, rad(yaw), 0) * Angles(0, 0, rad(roll))`, applied to LookVector.
  - The -90° turns -Z (aim) into -Y (down the handle).
  - `-VRClubGripPitch` rakes it toward +Z.
  - Default pitch is **35°**; yaw and roll are 0.
- **Start point:** the shaft starts at the bottom of the handle, `VRClubButtOffset` = **0.25 studs (7.5 cm)** along that axis from the hand origin.
- **Club axes:** RightVector = controller X, which becomes the putter face normal. UpVector ≈ the controller front (aim side), so the toe points away from the golfer.
- **Left hand:** the pitch is a rotation about hand X. The left/right controller mirror is across the hand YZ plane, which leaves X rotations unchanged, so the same pitch is correct for both hands. Yaw (about the club Y) and roll (about the shaft) flip sign under that mirror, and the code negates them for the left hand.
- **Legacy mount:** `Config.VRClubLegacyAim = true` restores the old tip/aim-ray mount (`VRClubAngle`, `VRClubTipOffset`). It's only used for the BEFORE images.
- **A-button refit:** keeps the butt point and re-aims the shaft straight down from it.

## Test pose
- Built by `GolfTest` `clubpose`, from the `side` view.
- Ball on hole 1 at (0, 10); stance from `VR.warpToBall`; simulated head at eye height 5.4 studs (1.62 m), looking down 60°.
- Club hand 0.914 m (3 ft) above the floor, ~0.9 studs in front of the eyes, above a point 0.6 studs inside the ball line.
- The physical handle (35° rake model) is aimed at the spot right behind the ball. The handle leans 11.4° from vertical toward the ball.
- Controller X points to the golfer's right, so the aim ray points forward-up, 46° above horizontal, away from the body.

## Results (`clubpose.json`, `harness/summary.md`)
| | Before (legacy aim ray) | After (grip axis) |
|---|---|---|
| Shaft vs handle axis | 125° | **0°** (drawn shaft-to-hosel 3.4°) |
| Shaft start vs handle bottom | 0.40 studs away | **0** |
| Shaft lean from vertical | 136° (pointing up) | 11.4° |
| Head bottom above ball plane | 4.98 studs | **0.011** (3 mm clearance) |
| Head to intended spot behind the ball | 5.13 studs | **0.001** |
| Club length (auto-fit, eye x 0.47) | 2.54 | 2.54 (+0.25 stretch) |

- A-button refit from the same pose: shaft vertical (0°), starts at the handle bottom, head on the plane (0.011), length 2.54 → 2.75 studs.
- Ledge (3 cases), ghost (wall + post sweeps) and the real simulated VR swing (1.2 m/s face → 6.80 studs/s ball, expected 6.80) all pass.
- 0 console warnings or errors. Smoke playtest: 0 errors, HUD up.

## Images (Studio window captures, cropped to the viewport, 1280 px)
- Views:
  - `side`: down the line, from the target side.
  - `front`: face-on, from beyond the ball.
  - `top`
  - `side_close` and `front_close`: centered on the controller.
- Overlay:
  - Dark cylinder: the handle, along the physical grip axis.
  - Orange ring: the handle bottom.
  - Grey disk: the tracking ring.
  - Red block: the trigger.
  - Thick gizmos: hand X/Y/Z (red/green/blue).
  - Thin gizmos: the club mount at the shaft start.
  - Yellow: the aim ray (-Z).
  - Skin sphere: the player's head.
- Files: `before_*.png` (VRClubLegacyAim) and `after_*.png`.

## Iteration notes
1. **First pass** (`/tmp`, not kept):
   - The crop failed: I looked for the wrong border blue, and the real one is (51,95,255).
   - The camera was 8 studs from the hand-to-ball midpoint, so the 3.6 cm proxy handle was unreadable.
   - The head sphere was out of frame, the hole-1 sign sat behind the shaft in the side view, and the course wall clipped the front view.
   - The geometry itself was already right: the after shaft ran down the handle to the ball; the before shaft pointed up and away.
2. **Second pass** (`iter2_contact_sheet.png`):
   - The side view now looks from the target side, which removed the sign. Close-ups were added at 2.6 studs, and the front camera was raised.
   - Close-ups confirmed the shaft leaves through the orange handle-bottom ring and continues the handle axis; before, it leaves the controller front along the yellow aim ray.
   - Still wrong: the crop locked onto the blue "Client" tab icon (CoreGui buttons leaked in), and the head sphere was still clipped at the top of the full views.
3. **Third pass** (final images, `iter3_contact_sheet.png`):
   - The border is now detected as long blue rows and columns, and the CoreGui strip is dropped.
   - The full views sit 11 studs out, centered between the head and the ball.
   - Everything reads:
     - The head sits above and behind the hands.
     - The hands are at the waist.
     - The handle points at the ball, and the shaft runs out of its bottom to a head resting right behind the ball.
     - The before club sticks up and out at about head height.
   - The putter's dark 9 cm grip ferrule overlaps the shaft just below the handle, so it reads as a continuous grip.

## Needs a real headset
- The 35° rake and the 0.25-stud butt offset are a model of Quest Touch (OpenXR aim pose), not a measurement. On the headset:
  1. Check the shaft continues the handle line. If it's tilted forward or back, change `VRClubGripPitch`; if it's tilted sideways, change `VRClubGripYaw`.
  2. Check the shaft starts at the bottom of the handle; if not, change `VRClubButtOffset`.
  3. Check the face is square; if not, change `VRClubGripRoll`.
  4. Check with the left hand too (X swaps hands).
- If Roblox turns out to report the OpenXR grip pose rather than the aim pose, -Z runs up the handle (pinky to thumb), so the handle bottom is +Z. In that case `VRClubGripPitch` ≈ 90 brings it back.
