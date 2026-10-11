# Hole 9: Heart of the Grove (Par 4)

Zone: **Inside the Hollow Tree**. Gimmick: **Ramp + banked corner, rising root gate, rolling dip through the trunk tunnel, deflector, swinging lantern pendulum at the heart well, drop to a sloped heart green**.
Layout: `h09-layout.png`. Geometry: `holes.json` -> holes[8]. World offset [214, 2, -70], yaw 0.0.
Tee [0, 0, 0], cup [26.0, -0.8, -52.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
The **heart of the giant hollow tree**: you putt up a ramp, round a banked corner and through a **root portcullis** into a tunnel in the trunk, where the felt **dips and rises** (the course's only rolling dip). Inside, a lantern-lit chamber ends at the **heart well**, where a **great lantern swings on a chain** across the mouth of the drop to the heart green below. Three big amber lanterns hang high above the heart green and light it.

## Gimmick
Ramp + banked corner, rising root gate, rolling dip through the trunk tunnel, deflector, swinging lantern pendulum at the heart well, drop to a sloped heart green.

## Intended shots
1. A strong putt up the 1-stud ramp rides the banked corner east and, if the root gate is up, rolls through the tunnel's dip into the chamber.
2. The root deflector turns the ball north. Time the swinging lantern (it swings slowly, once every 4 s), or play to the edge of the 8-stud well mouth, and drop 1.5 studs into the heart.
3. The heart green slopes gently away from the drop; the cup sits in its north-east part (26, -0.8, -52). Putt out.
**Secret:** a tiny glowing **Lantern Knot** in the corridor floor at (6.5, 1.0, -23.0), half a stud past the root gate and one stud in from the corridor's south rail, teleports the ball to the heart green's north-west corner and rolls it east along the back of the green toward the cup. It is the hole's ace route.

## Hole-in-one line
Brute-force search from the tee found ace lines (55 grid shots). The most robust: aim **293.0°** (atan2(dz,dx): direction (0.39, -0.92) in x/z, i.e. 23.0° right of straight -Z), speed **19.4 studs/s** (98% power), start phase t=0.0s of the moving parts. The red dashed line on the layout PNG traces it.

## Challenge
Finale combining everything: ramp pace, a bank, a vertical gate (open ~70% of its 4 s cycle), a rolling dip (a weak shot settles in the tunnel), a deflector, a swinging lantern and a drop. Round 8 (after RobloxDevBot measured it in Studio): the hinge sits right over the chamber shot line (x 21.2), the lantern swings a short, readable ±13° every 4 s, and a collider foot hangs below the ball's centre, so a ball that meets the lantern is stopped instead of rolling under it. Round 9: the foot is 0.9x0.4x1.6, square to the swing (yaw 0), 0.034 above the felt, with a matching base plinth on the lantern mesh. At the ends of its swing the lantern hangs beside the line (centre 1.6 studs east or west of it) and the ball rolls past. Fired at 24 evenly spaced timings, the intended chamber shot is blocked 46% of the time (1 more is deflected, 12 pass), with no traps; on RobloxDevBot's in-engine test line it is blocked 42-50% at 7-9 studs/s (45% at 7.75 over 80 timings; Studio measured 33% with the Round 8 foot). The 1.6x1.6 square lantern is turned 30°, so a hit knocks the ball out of the swing plane and it can never be batted back and forth along it. The three amber lanterns over the green are decoration only, 8 studs above the felt. The secret knot rewards players who explore.

## Moving parts / teleports (exact specs, also in holes.json)
- **root_gate** (slide): pivot [6, 1.0, -25.5], axis [0, 1, 0], speed 0.9 studs/s, ping-pong 0.0..1.8 studs, phase 0.0, cycle 4.00 s. Blockers (relative to pivot at angle/offset 0): box [0.8, 1.4, 7.4] at [0, 0.4, 0]. Visual: Root portcullis rising/falling 0..1.8 in the tunnel mouth (open ~70% of its 4 s cycle)
- **lantern_pendulum** (swing = pendulum): pivot (hinge) [21.2, 8.996, -38.5], axis [0, 0, 1] (swings in the plane perpendicular to it), angle(t) = 13.0° x sin(360°·t/4.0 s + 0.0°), peak angular speed 20°/s at the bottom. Blocker: bob box [1.6, 1.8, 1.6] centred [0, -7.0, 0] from the pivot when hanging straight down; blocker 2: box [0.9, 0.4, 1.6] centred [0, -7.762, 0]. Visual: Great lantern on a 7-stud chain from a root beam, swinging east-west across the heart-well mouth (1.5 studs before the drop edge); the bob (1.6x1.8x1.6 box turned 30 deg about the vertical, 2.19 across the swing) skims the felt at the bottom of its swing and swings clear of the shot line (x 21.2) near the ends; blocker 2 = invisible collider foot 0.9x0.4x1.6 (yaw 0: square to the swing) under the lantern body, bottom 0.034 above the felt at rest (body bottom 0.096); its corners poke out past the lantern's faces, so the lantern mesh gets a matching base plinth
- **teleport lantern_knot**: entry [6.5, 1.0, -23.0] r 0.3 -> exit [15.0, -0.8, -52.0] dir [1.0, 0.0], exit speed = clamp(in x 1.0, 4.0, 10.0) studs/s

## Flag and sightline
Flag: 8.0-stud pole (0.15 diameter) standing in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [26.0, 7.2, -52.0]; visual only, no collision. Line of sight from the tee eye (5.5 studs above the tee) to the flag top: **visible** (min clearance over rails/felt/props +0.20 studs).

## Playtest stats (final, latest, 2000 plays per skill)
| Skill | Avg strokes | HIO | Capped (8) | Strokes 1..8 |
|---|---|---|---|---|
| good | 3.81 | 3.0% | 0.1% | [60, 52, 559, 1025, 191, 83, 20, 10] |
| average | 4.21 | 0.2% | 0.4% | [5, 32, 505, 784, 458, 131, 53, 32] |

## Props for 3D Model Bot (decoration only, sizes in studs)
Giant hollow tree trunk with chamber and heart 34x60x34 (P1); root portcullis gate (moving, slides along Y 0..1.8 at 0.9 studs/s) 0.8x1.4x7.4 (P1); **great lantern pendulum** (moving, Round 8: hinge at **(21.2, 8.996, -38.5)**, axis +Z, **±13°, period 4 s**; chain 7 long; lantern bob **1.6x1.8x1.6 square lantern turned 30° about the vertical** whose bottom hangs 0.096 above the felt at rest, plus a **collider foot 0.9x0.4x1.6, yaw 0** (Round 9, square to the swing; centred 7.762 below the hinge, bottom 0.034 above the felt at rest), covered by a **new base plinth on the lantern mesh** of the same size and yaw (its corners stick out up to 0.12 past the lantern's faces)) (P1, **rebuild**); root beam over the chamber 16x1.2x1.2 (P1, still centred at x 22; the hinge is on it at x 21.2); trunk tunnel arch 7x5x8 with root-and-moss trim following the 0.4 dip (P2); root deflector cladding 15x1x0.5 (P1); heart-well root rim 8x0.6x1 (P2); Lantern Knot 1.2x1.2x0.6 + exit knot 1.0x0.3x1.0 (P2); **3 hanging amber lanterns** 1.2x1.8x1.2 (NEW, replace the old 'dozens of lanterns' cluster) at (18.5, -47.5), (28.5, -46.5), (20, -51.5), bottoms at y 7.2 = 8 studs above the green felt, chains up into the canopy, warm PointLights; decoration only, no collision (P1); glowing mushrooms (P2); flag 8 (P1). The old lantern bar + lantern post are removed.

Decoration anchors (position in hole-local studs):
- `cup_flag` at [26.0, -0.8, -52.0] size [2.0, 8.0, 0.15]: Flag: 8.0-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `hollow_tree` at [22, -0.5, -36] (LANDMARK) size [34, 60, 34]: Giant hollow tree: trunk ~34 across, chamber is inside it, opening above the heart
- `trunk_tunnel` at [11, 1.0, -25.5] size [7, 5, 8]: Arched tunnel through a root buttress (opening 7 wide x 3 high above the corridor level, solid above y 4 up to y 6); the felt inside dips 0.4 (rolling dip)
- `amber_lantern_1` at [18.5, 7.2, -47.5] size [1.2, 1.8, 1.2]: Hanging amber paper lantern 1/3 lighting the heart green (warm PointLight); bottom at y 7.2 = 8 studs above the green felt, chain up into the trunk canopy (y ~16). Decoration only, no collision
- `amber_lantern_2` at [28.5, 7.2, -46.5] size [1.2, 1.8, 1.2]: Hanging amber paper lantern 2/3 lighting the heart green (warm PointLight); bottom at y 7.2 = 8 studs above the green felt, chain up into the trunk canopy (y ~16). Decoration only, no collision
- `amber_lantern_3` at [20.0, 7.2, -51.5] size [1.2, 1.8, 1.2]: Hanging amber paper lantern 3/3 lighting the heart green (warm PointLight); bottom at y 7.2 = 8 studs above the green felt, chain up into the trunk canopy (y ~16). Decoration only, no collision
- `lantern_knot` at [6.5, 1.0, -23.0] size [1.2, 1.2, 0.6]: Secret glowing knot-hole in the corridor floor at (6.5, 1.0, -23.0): 0.5 stud past (east of) the root gate at x=6 and 1 stud in from the corridor's south rail (z=-22). Teleport entry r 0.3; the exit knot is in the heart green's north-west corner (15, -0.8, -52)
- `lantern_knot_exit` at [15.0, -0.8, -52.0] size [1.0, 0.3, 1.0]: Matching small glowing knot on the heart green's north-west corner (teleport exit)
- `well_rim` at [22.0, 1.0, -40] size [8.0, 0.6, 1]: Carved root rim along the heart-well drop edge
- `pendulum_beam` at [22.0, 8.996, -38.5] size [16, 1.2, 1.2]: Root beam spanning the chamber high above the heart-well mouth (x 14..30), hinge of the lantern pendulum on it at x 21.2
- `dip_cladding` at [11.0, 0.6, -25.5] size [6.0, 0.4, 7]: Root-and-moss trim on the tunnel rails following the rolling dip (felt dips 0.4 studs: down x 8..11, back up 11..14)
- `glow_mushrooms` at [30, -0.5, -52] size [3, 2, 3]: Bioluminescent mushrooms ring

## Concept prompt
First-person VR view at eye height from a mini golf tee at the base of a colossal hollow golden tree. A green felt lane climbs a ramp to a banked stone corner, then turns into an arched tunnel in the trunk where the felt dips and rises, behind a portcullis of twisted roots that rises and falls. Through the opening, a warm glow: inside the hollow tree three big amber paper lanterns hang high above the heart green, and a great square brass-and-paper lantern swings slowly on a long chain across the mouth of a round sunken heart green with a tall red flag. Fireflies, glowing mushrooms, golden autumn canopy, magical evening light, grand finale feel, cozy fairy-forest storybook style.
