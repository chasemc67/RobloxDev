# Hole 7: Cascade Steps (Par 3)

Zone: **Waterfall Terraces**. Gimmick: **Two drops down terraces, sliding log on the middle tier, waterfall-pool hazard, side-sloped bottom green**.
Layout: `h07-layout.png`. Geometry: `holes.json` -> holes[6]. World offset [144, -3, -40], yaw 0.0.
Tee [0, 0, 0], cup [-2.5, -2.4, -31.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A **three-step waterfall** cascading into a pool on the left. The hole steps down beside it over two felt terraces, with a **floating log** sliding back and forth across the middle tier.

## Gimmick
Two drops down terraces, sliding log on the middle tier, waterfall-pool hazard, side-sloped bottom green.

## Intended shots
1. Drop off the top tier (full width), cross the middle tier past the sliding log, and aim for the 3.5-stud gap that drops to the bottom tier. The bottom tier's east half slopes gently toward the cup side.
2–3. Putt out on the bottom green.

## Hole-in-one line
Brute-force search from the tee found ace lines (97 grid shots). The most robust: aim **283.0°** (atan2(dz,dx): direction (0.22, -0.97) in x/z, i.e. 13.0° right of straight -Z), speed **13.5 studs/s** (68% power), start phase t=0.0s of the moving parts. The red dashed line on the layout PNG traces it.

## Challenge
Two drops plus a moving blocker: the log slides ±6 studs at 5 studs/s and will happily shove the ball toward the waterfall pool (gap in the middle tier's left rail = hazard). The landing slope carries the ball left after the second drop.

## Moving parts / teleports (exact specs, also in holes.json)
- **log** (slide): pivot [0, -1.2, -20.5], axis [1, 0, 0], speed 5.0 studs/s, ping-pong -6.0..6.0 studs, phase 0.0, cycle 4.8 s. Blockers (relative to pivot at angle/offset 0): box [5.0, 0.8, 0.8] at [0, 0.4, 0]. Visual: Floating log on a hidden rail

## Playtest stats (final, p4, 2000 plays per skill)
| Skill | Avg strokes | HIO | Capped (8) | Strokes 1..8 |
|---|---|---|---|---|
| good | 2.74 | 2.1% | 0.1% | [41, 759, 963, 175, 45, 11, 3, 3] |
| average | 2.87 | 1.7% | 0.0% | [33, 605, 1043, 243, 60, 12, 4, 0] |

## Props for 3D Model Bot (decoration only, sizes in studs)
Three-step waterfall cascade 8x14x10 (P1); floating log (moving, slides along X) 5x0.8x0.8 (P1); pool water (P1); lantern posts at the lower gap 0.5x3x0.5 (P1); ferns & red leaf bushes (P3); stone terrace faces (P1).

Decoration anchors (position in hole-local studs):
- `cascade` at [-16, -3, -18] (LANDMARK) size [8, 14, 10]: Three-step waterfall dropping into the pool on the left
- `log_rail` at [0, -1.2, -20.5] size [5, 0.8, 0.8]: Floating log (moving mesh) on a hidden rail across the middle tier
- `ferns` at [12, -2.4, -34] size [3, 2, 3]: Fern clumps and red leaves
- `step_lanterns` at [4.5, -1.2, -27] size [0.5, 3, 0.5]: Lanterns flanking the lower gap

## Concept prompt
First-person VR view at eye height from a mini golf tee at the top of a series of green felt terraces stepping down beside a beautiful three-tiered waterfall that pours into a misty pool on the left. On the middle terrace a mossy log floats sideways across the path. Lanterns mark a narrow gap down to the bottom green, where a red flag waits. Rocks covered in moss and ferns, red and golden autumn trees, rainbow in the spray, warm sunlight, cozy fairy-forest style.
