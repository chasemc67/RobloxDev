# Hole 8: Firefly Hollow (Par 4)

Zone: **Hollow Tree Roots**. Gimmick: **Teleport ring shortcut in a dead-end alcove vs long route (banked corners, long ramp)**.
Layout: `h08-layout.png`. Geometry: `holes.json` -> holes[7]. World offset [190, 0, -10], yaw 0.0.
Tee [0, 0, 0], cup [8.0, 1.5, -43.5] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
The roots of the giant hollow tree arch over the course. In a dead-end alcove a **root knot holds a glowing firefly ring**, guarded by a sliding root door. Its twin ring stands on the upper green.

## Gimmick
Teleport ring shortcut in a dead-end alcove vs long route (banked corners, long ramp).

## Intended shots
**Shortcut:** 1) bank off the junction's back rail (or play to the junction); 2) thread the sliding root door into the firefly ring. It teleports you to the upper green's far corner and sends the ball rolling toward the cup; 3–4) putt out.
**Long route:** 1) to the junction; 2) along it into the banked corner; 3) up the long 1.5-stud climb; 4) the top bank turns you onto the connector; 5) putt out.

## Hole-in-one line
Brute-force search from the tee found ace lines (468 grid shots). The most robust: aim **225.5°** (atan2(dz,dx): direction (-0.70, -0.71) in x/z, i.e. 44.5° left of straight -Z), speed **19.4 studs/s** (98% power), start phase t=0.0s of the moving parts. The red dashed line on the layout PNG traces it.

## Challenge
The ring is small (radius 0.35) and the root door slides across the alcove mouth (±2.5 studs at 2 studs/s). A miss leaves the ball rattling in the alcove. The long route is safe but costs about a stroke.

## Moving parts / teleports (exact specs, also in holes.json)
- **root_door** (slide): pivot [4.75, 0.0, -11.5], axis [0, 0, 1], speed 2.0 studs/s, ping-pong -2.5..2.5 studs, phase 0.0, cycle 5.0 s. Blockers (relative to pivot at angle/offset 0): box [0.7, 1.0, 3.2] at [0, 0.5, 0]. Visual: Sliding root door across the alcove mouth
- **teleport ring**: entry [7.0, 0.0, -11.5] r 0.35 -> exit [-4.0, 1.5, -56.0] dir [0.6925, 0.7214], exit speed = clamp(in x 1.2, 4.0, 8.5) studs/s

## Playtest stats (final, p4, 2000 plays per skill)
| Skill | Avg strokes | HIO | Capped (8) | Strokes 1..8 |
|---|---|---|---|---|
| good | 3.30 | 5.7% | 4.0% | [114, 765, 500, 227, 126, 77, 76, 115] |
| average | 4.95 | 0.0% | 4.2% | [0, 0, 0, 621, 1066, 195, 22, 96] |

## Props for 3D Model Bot (decoration only, sizes in studs)
Root knot arch with firefly ring (entry) 3x4x4 (P1); exit firefly ring 2.5x3x1 (P1); sliding root door (moving, slides along Z) 0.7x1x3.2 (P1); hollow-tree base & arching roots 30x40x30 (P1); glowing mushrooms 2x1.5x2 (P2); bank cladding (P1).

Decoration anchors (position in hole-local studs):
- `root_knot_ring` at [8.5, 0, -11.5] (LANDMARK) size [3, 4, 4]: Root knot arch with a glowing firefly ring (teleport entry)
- `exit_ring` at [-4.0, 1.5, -56.0] size [2.5, 3, 1]: Matching firefly ring on the upper green (teleport exit)
- `hollow_tree_base` at [20, 0, -35] size [30, 40, 30]: Base of the giant hollow tree, roots arching over the course
- `glow_shrooms` at [-17, 0, -20] size [2, 1.5, 2]: Glowing mushrooms along the climb

## Concept prompt
First-person VR view at eye height from a mini golf tee at the foot of an enormous golden hollow tree whose roots arch overhead like a cathedral. The green felt lane opens into a junction. To the right, a dead-end nook inside a gnarled root knot holds a glowing ring of fireflies with a carved root door sliding across its mouth. To the left, a long banked path climbs away between the roots. Fireflies, glowing mushrooms, amber lanterns, dusky golden light filtering through the leaves, magical cozy fairy-forest style.
