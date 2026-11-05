# Hole 7: Cascade Steps (Par 3)

Zone: **Waterfall Terraces**. Gimmick: **Two drops down terraces, sliding log on the middle tier, waterfall-pool hazard, side-sloped bottom green**.
Layout: `h07-layout.png`. Geometry: `holes.json` -> holes[6]. World offset [144, -3, -40], yaw 0.0.
Tee [0, 0, 0], cup [-2.5, -2.4, -36.5] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A **three-step waterfall** cascading into a pool on the left. The hole steps down beside it over two felt terraces, with a **floating log** with whittled, pointed ends sliding back and forth across the middle tier and pausing at each end.

## Gimmick
Two drops down terraces, sliding log on the middle tier, waterfall-pool hazard, side-sloped bottom green.

## Intended shots
1. Drop off the top tier (full width), cross the middle tier past the sliding log (shoot while it rests at the west end), and thread the **2.5-stud gap** (x 4 to 6.5) that drops to the bottom tier. The bottom tier's east half slopes down toward the west and carries the ball across toward the flag side.
2–3. The cup sits deep in the north-west part of the bottom green (-2.5, -36.5), beyond where the slope drops tee shots, so the second putt is a real one.

## Hole-in-one line
Brute-force search from the tee found ace lines (137 grid shots). The most robust: aim **236.5°** (atan2(dz,dx): direction (-0.55, -0.83) in x/z, i.e. 33.5° left of straight -Z), speed **19.0 studs/s** (96% power), start phase t=0.0s of the moving parts. The red dashed line on the layout PNG traces it.

## Challenge
Two drops plus a timing obstacle (Round 7): the 6-stud log slides ±6 studs at 3.5 studs/s, its ends stopping 1 stud short of each rail. It **pauses 1.0 s at the west end** (the gap line is open) and **1.5 s at the east end**, where it lies right across the line to the gap. Cycle 9.36 s. Fired at 24 evenly spaced timings, the intended tee shot is blocked or deflected 46% of the time and passes 54% of the time, with no traps. The pointed ends knock a ball sideways out of the log's track, so it can no longer be batted back and forth along the track (the old soft-lock). A deflected ball can still be shoved toward the waterfall pool (gap in the middle tier's left rail = hazard). The narrower lower gap and the deeper cup reward an accurate tee shot and a well-paced putt.

## Moving parts / teleports (exact specs, also in holes.json)
- **log** (slide): pivot [0, -1.2, -20.5], axis [1, 0, 0], speed 3.5 studs/s, ping-pong -6.0..6.0 studs with pauses 1 s at -6, 1.5 s at 6, phase 0.0, cycle 9.36 s. Blockers (relative to pivot at angle/offset 0): box [5.2, 0.8, 0.8] at [0, 0.4, 0]; box [0.5657, 0.8, 0.5657] at [-2.6, 0.4, 0] yaw 45.0; box [0.5657, 0.8, 0.5657] at [2.6, 0.4, 0] yaw 45.0. Visual: Floating log on a hidden rail; log ends stop 1 studs short of each rail line (x=+-10): travel +-6

## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) standing in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [-2.5, 5.1, -36.5]; visual only, no collision. Line of sight from the tee eye (5.5 studs above the tee) to the flag top: **visible** (min clearance over rails/felt/props +5.35 studs).

## Playtest stats (final, r7-final, 2000 plays per skill)
| Skill | Avg strokes | HIO | Capped (8) | Strokes 1..8 |
|---|---|---|---|---|
| good | 2.95 | 2.2% | 0.1% | [45, 550, 1063, 222, 71, 31, 10, 8] |
| average | 3.40 | 0.1% | 0.2% | [2, 266, 1057, 439, 143, 49, 31, 13] |

## Props for 3D Model Bot (decoration only, sizes in studs)
Three-step waterfall cascade 8x14x10 (P1); floating log (moving, slides along X ±6 at 3.5 studs/s, pauses 1.0 s west / 1.5 s east; ends 1.0 short of the rails) **6x0.8x0.8 with pointed (45°, whittled/root-knot) ends**: collision = 5.2x0.8x0.8 box + two 0.566x0.8x0.566 boxes turned 45° at the ends (P1, **rebuild**); pool water (P1); lantern posts at the lower gap 0.5x3x0.5 at x 3.75 and 6.75 (P1, **move**: gap is now x 4..6.5); ferns & red leaf bushes (P3); stone terrace faces (P1); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [-2.5, -2.4, -36.5] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `cascade` at [-16, -3, -18] (LANDMARK) size [8, 14, 10]: Three-step waterfall dropping into the pool on the left
- `log_rail` at [0, -1.2, -20.5] size [6.0, 0.8, 0.8]: Floating log (moving mesh) on a hidden rail across the middle tier; stops 1 short of each rail
- `ferns` at [12, -2.4, -34] size [3, 2, 3]: Fern clumps and red leaves
- `step_lanterns` at [5.0, -1.2, -27] size [0.5, 3, 0.5]: Lanterns flanking the lower gap

## Concept prompt
First-person VR view at eye height from a mini golf tee at the top of a series of green felt terraces stepping down beside a beautiful three-tiered waterfall that pours into a misty pool on the left. On the middle terrace a mossy log with whittled pointed ends floats sideways across the path, pausing at each rail. Two lanterns mark a narrow gap down to the bottom green, where a tall red flag waits in the far corner. Rocks covered in moss and ferns, red and golden autumn trees, rainbow in the spray, warm sunlight, cozy fairy-forest style.
