# Hole 8: Firefly Hollow (Par 4)

Zone: **Hollow Tree Roots**. Gimmick: **Teleport ring shortcut in a dead-end alcove (back-wall bank feeds misses out) vs long route (banked corners, climb)**.
Layout: `h08-layout.png`. Geometry: `holes.json` -> holes[7]. World offset [190, 0, -10], yaw 0.0.
Tee [0, 0, 0], cup [4.0, 1.5, -37.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
The roots of the giant hollow tree arch over the course. In a dead-end alcove a **root knot holds a glowing firefly ring** (1.1 studs across), guarded by a root door that slides in and out of pockets in the knot walls. The alcove's back wall is a banked root slope. Its twin ring stands in the far corner of the upper green.

## Gimmick
Teleport ring shortcut in a dead-end alcove (back-wall bank feeds misses out) vs long route (banked corners, climb).

## Intended shots
**Shortcut:** 1) bank off the junction's back rail (or play to the junction); 2) thread the root door into the firefly ring. It teleports the ball to the upper green's north-east corner (9, 1.5, -47) and rolls it toward the cup: a firm ring shot can drop straight in, a soft one leaves a short putt; 3) putt out. A miss climbs the back-wall bank and rolls back out of the alcove.
**Long route (par route, shortened in Round 5):** 1) up the lane to the junction; 2) along it softly into the banked corner; 3) one committed putt up the 1.5-stud climb, which the top bank turns onto the connector and the green; 4) putt out.

## Hole-in-one line
Brute-force search from the tee found ace lines (352 grid shots). The most robust: aim **288.5°** (atan2(dz,dx): direction (0.32, -0.95) in x/z, i.e. 18.5° right of straight -Z), speed **17.9 studs/s** (91% power), start phase t=0.0s of the moving parts. The red dashed line on the layout PNG traces it.

## Challenge
The ring is a fair target (radius 0.55) but the root door (3.2 long) slides ±3.5 studs at 2 studs/s across the 7-stud mouth and blocks the line about half the time. The long route is now about a stroke shorter (the flat run before the climb is gone) and is a genuine par.

## Moving parts / teleports (exact specs, also in holes.json)
- **root_door** (slide): pivot [4.75, 0.0, -11.5], axis [0, 0, 1], speed 2.0 studs/s, ping-pong -3.5..3.5 studs, phase 0.0, cycle 7.0 s. Blockers (relative to pivot at angle/offset 0): box [0.7, 1.0, 3.2] at [0, 0.5, 0]. Visual: Sliding root door across the alcove mouth
- **teleport ring**: entry [7.0, 0.0, -11.5] r 0.55 -> exit [9.0, 1.5, -47.0] dir [-0.4472, 0.8944], exit speed = clamp(in x 0.7, 4.0, 8.5) studs/s

## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) standing in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [4.0, 9.0, -37.0]; visual only, no collision. Line of sight from the tee eye (5.5 studs above the tee) to the flag top: **visible** (min clearance over rails/felt/props +3.02 studs).

## Playtest stats (final, r5b, 2000 plays per skill)
| Skill | Avg strokes | HIO | Capped (8) | Strokes 1..8 |
|---|---|---|---|---|
| good | 3.17 | 4.9% | 0.8% | [97, 521, 832, 269, 152, 71, 28, 30] |
| average | 4.50 | 0.0% | 0.1% | [0, 0, 19, 1108, 757, 90, 23, 3] |

## Props for 3D Model Bot (decoration only, sizes in studs)
Root knot arch with firefly ring (entry, ring glow 1.1 across) 3x4x4 (P1, **resize ring**); alcove back-wall bank cladding 1.3x0.5x7 root bark over the banked plane x 7.7..9 (P1, new); exit firefly ring 2.5x3x1 at (9, 1.5, -47) (P1, **move**); sliding root door (moving, slides along Z ±3.5) 0.7x1x3.2 with pockets in the root-knot walls at both ends of its travel (P1, **rebuild travel**); hollow-tree base & arching roots 30x40x30 (P1); glowing mushrooms 2x1.5x2 (P2); bank cladding (P1); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [4.0, 1.5, -37.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `root_knot_ring` at [8.5, 0, -11.5] (LANDMARK) size [3, 4, 4]: Root knot arch with a glowing firefly ring (teleport entry); the ring's glow disc is 1.1 studs across
- `alcove_bank_cladding` at [8.35, 0, -11.5] size [1.2999999999999998, 0.6, 7]: Root-bark cladding on the alcove back-wall bank (banked plane x 7.7..9, rising east), 7 long
- `exit_ring` at [9.0, 1.5, -47.0] size [2.5, 3, 1]: Matching firefly ring on the upper green (teleport exit)
- `hollow_tree_base` at [20, 0, -35] size [30, 40, 30]: Base of the giant hollow tree, roots arching over the course
- `glow_shrooms` at [-17, 0, -20] size [2, 1.5, 2]: Glowing mushrooms along the climb

## Concept prompt
First-person VR view at eye height from a mini golf tee at the foot of an enormous golden hollow tree whose roots arch overhead like a cathedral. The green felt lane opens into a junction. To the right, a dead-end nook inside a gnarled root knot holds a glowing ring of fireflies, a carved root door sliding in and out of the knot walls across its mouth. To the left, a short banked path climbs between the roots to an upper green with a tall red flag. Fireflies, glowing mushrooms, amber lanterns, dusky golden light filtering through the leaves, magical cozy fairy-forest style.
