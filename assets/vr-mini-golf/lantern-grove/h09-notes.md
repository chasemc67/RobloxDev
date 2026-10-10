# Hole 9: Heart of the Grove (Par 4)

Zone: **Inside the Hollow Tree**. Gimmick: **Ramp + banked corner, rising root gate in a trunk tunnel, deflector, rotating lantern bar over the heart well, drop to a sloped heart green**.
Layout: `h09-layout.png`. Geometry: `holes.json` -> holes[8]. World offset [214, 2, -70], yaw 0.0.
Tee [0, 0, 0], cup [22.0, -0.8, -50.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
The **heart of the giant hollow tree**: you putt up a ramp, round a banked corner and through a **root portcullis** into a tunnel in the trunk. Inside, a lantern-lit chamber ends at the **heart well**, where a slowly turning lantern bar guards the drop to the heart green below. Dozens of lanterns hang in the hollow above.

## Gimmick
Ramp + banked corner, rising root gate in a trunk tunnel, deflector, rotating lantern bar over the heart well, drop to a sloped heart green.

## Intended shots
1. A strong putt up the 1-stud ramp rides the banked corner east and, if the root gate is up, runs through the tunnel into the chamber.
2. The root deflector turns the ball north. Time the lantern bar and drop 1.5 studs into the heart.
3. The heart green slopes gently toward the cup. Putt out.
**Secret:** a tiny glowing **Lantern Knot** in the corridor floor just past the gate teleports the ball to the heart green's south-west corner, rolling toward the cup. It is the hole's ace route.

## Hole-in-one line
Brute-force search from the tee found ace lines (459 grid shots). The most robust: aim **292.0°** (atan2(dz,dx): direction (0.37, -0.93) in x/z, i.e. 22.0° right of straight -Z), speed **18.3 studs/s** (93% power), start phase t=1.5s of the moving parts. The red dashed line on the layout PNG traces it.

## Challenge
Finale combining everything: ramp pace, a bank, a vertical gate (open ~62% of its 4 s cycle), a deflector, a rotating bar and a drop. The secret knot rewards players who explore.

## Moving parts / teleports (exact specs, also in holes.json)
- **root_gate** (slide): pivot [6, 1.0, -25.5], axis [0, 1, 0], speed 0.6 studs/s, ping-pong 0.0..1.2 studs, phase 0.0, cycle 4.0 s. Blockers (relative to pivot at angle/offset 0): box [0.8, 1.4, 7.4] at [0, 0.4, 0]. Visual: Root portcullis rising/falling in the tunnel mouth (open ~62% of the cycle)
- **lantern_bar** (rotate): pivot [25.0, 1.0, -36.5], axis [0, 1, 0], speed 40.0 deg/s, continuous, phase 0.0, cycle 9.0 s. Blockers (relative to pivot at angle/offset 0): box [6.0, 1.0, 0.6] at [0, 0.5, 0]. Visual: Rotating bar on the lantern post guarding the heart well, lanterns at both ends
- **teleport lantern_knot**: entry [6.5, 1.0, -23.0] r 0.3 -> exit [15.0, -0.8, -52.0] dir [0.9615, 0.2747], exit speed = clamp(in x 1.0, 4.0, 10.0) studs/s

## Playtest stats (final, p4, 2000 plays per skill)
| Skill | Avg strokes | HIO | Capped (8) | Strokes 1..8 |
|---|---|---|---|---|
| good | 3.50 | 3.2% | 0.9% | [64, 533, 516, 432, 263, 109, 45, 38] |
| average | 4.02 | 1.4% | 1.6% | [28, 273, 552, 489, 336, 167, 76, 79] |

## Props for 3D Model Bot (decoration only, sizes in studs)
Giant hollow tree trunk with chamber and heart 34x60x34 (P1); root portcullis gate (moving, slides along Y) 0.8x1.4x7.4 (P1); lantern bar + post (moving, axis +Y, 40°/s) 6x1x0.6 (P1); trunk tunnel arch 7x5x8 (P2); root deflector cladding 15x1x0.5 (P1); heart-well root rim 8x0.6x1 (P2); Lantern Knot 1.2x1.2x0.6 (P2); hanging lanterns cluster 16x6x12 (P1); glowing mushrooms (P2).

Decoration anchors (position in hole-local studs):
- `hollow_tree` at [22, -0.5, -36] (LANDMARK) size [34, 60, 34]: Giant hollow tree: trunk ~34 across, chamber is inside it, opening above the heart
- `trunk_tunnel` at [11, 1.0, -25.5] size [7, 5, 8]: Arched tunnel through a root buttress
- `heart_lanterns` at [23, 4, -47] size [16, 6, 12]: Dozens of hanging lanterns inside the heart
- `lantern_knot` at [6.5, 1.0, -23.0] size [1.2, 1.2, 0.6]: Secret glowing knot-hole in the corridor floor just past the root gate (teleport entry); exit is a knot in the heart's south-west corner
- `well_rim` at [22, 1.0, -40] size [8, 0.6, 1]: Carved root rim along the heart-well drop edge
- `glow_mushrooms` at [30, -0.5, -52] size [3, 2, 3]: Bioluminescent mushrooms ring

## Concept prompt
First-person VR view at eye height from a mini golf tee at the base of a colossal hollow golden tree. A green felt lane climbs a ramp to a banked stone corner, then turns into an arched tunnel in the trunk, where a portcullis of twisted roots rises and falls. Through the opening, a warm glow: inside the hollow tree hundreds of paper lanterns hang above a lantern-lit chamber and a slowly turning lantern bar over a round heart green with a red flag. Fireflies, glowing mushrooms, golden autumn canopy, magical evening light, grand finale feel, cozy fairy-forest storybook style.
