# Hole 4: Spore Spinner (Par 3)

Zone: **Mushroom Village**. Gimmick: **Rotating 2-arm spinner bar in a plaza (time it for a birdie, or take a side gap for a safe par), then ramp up to a raised green**.
Layout: `h04-layout.png`. Geometry: `holes.json` -> holes[3]. World offset [52, 1, -60], yaw 0.0.
Tee [0, 0, 0], cup [2.5, 0.6, -42.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
The **Puffball Carousel**: a toadstool hub in the middle of a widened plaza, turning a padded 2-arm bar of puffball stalks (6 studs across) at a lazy 30°/s. Lantern posts on the plaza rails mark the two side gaps. Mushroom houses flank the plaza, and a raised green sits beyond a short ramp.

## Gimmick
Rotating 2-arm spinner bar in a plaza (time it for a birdie, or take a side gap for a safe par), then ramp up to a raised green.

## Intended shots
**Birdie line (timing):** time the tee shot straight through the plaza past the turning bar and run it up the 0.6-stud ramp onto the green; 2) putt. A ball clipped by the bar caroms off the padded arm (bumper restitution 0.65) at the bar's surface speed.
**Safe line (side gap, ~1 stroke longer):** 1) a firm, accurate putt down the right side of the plaza, between the arm tips and the rail (gap 3.9 studs wide), stopping just past the carousel; 2) straight up the ramp onto the green; 3) putt out.

## Hole-in-one line
Brute-force search from the tee found ace lines (94 grid shots). The most robust: aim **252.5°** (atan2(dz,dx): direction (-0.30, -0.95) in x/z, i.e. 17.5° left of straight -Z), speed **19.0 studs/s** (96% power), start phase t=1.5s of the moving parts. The red dashed line on the layout PNG traces it.

## Challenge
First timing obstacle. The bar is slow enough to read in VR (a full turn every 12 s, an arm passes every 6 s). Skilled players take the side gap for a near-certain par or time the bar for birdie; players who fire at the flag through the carousel get knocked back about half the time. Diagonal shots up the ramp curl back, so come in straight.

## Moving parts / teleports (exact specs, also in holes.json)
- **spinner** (rotate): pivot [0, 0, -21], axis [0, 1, 0], speed 30.0 deg/s, continuous, phase 0.0, cycle 12.0 s. Blockers (relative to pivot at angle/offset 0): box [2.3, 1.0, 0.7] at [1.85, 0.5, 0.0]; box [2.3, 1.0, 0.7] at [-1.85, 0.5, -0.0] yaw 180.0. Visual: 2 padded puffball-stalk arms (one 6-stud bar) on a toadstool hub; arms are soft bumpers (restitution 0.65)

## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) standing in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [2.5, 8.1, -42.0]; visual only, no collision. Line of sight from the tee eye (5.5 studs above the tee) to the flag top: **visible** (min clearance over rails/felt/props +5.50 studs).

## Playtest stats (final, r5b, 2000 plays per skill)
| Skill | Avg strokes | HIO | Capped (8) | Strokes 1..8 |
|---|---|---|---|---|
| good | 3.15 | 2.8% | 0.0% | [55, 252, 1195, 371, 89, 32, 6, 0] |
| average | 3.73 | 1.3% | 0.7% | [26, 311, 660, 509, 286, 127, 47, 34] |

## Props for 3D Model Bot (decoration only, sizes in studs)
Puffball carousel bar (moving, pivot hub centre, axis +Y, 30°/s) 6x1x0.7 padded arms + puffballs (P1, **rebuild: shorter**); toadstool hub 1.4x2x1.4 (P1); mushroom houses x2 7–8x9–10x7–8 (P1); green lantern posts 0.5x3.5x0.5 (P1); side-gap lantern posts 0.4x2.5x0.4 on the plaza rail tops at x ±7.25, z -17 (P2, new); paper lanterns (P2); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [2.5, 0.6, -42.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `puffball_carousel` at [0, 0, -21] (LANDMARK) size [6.0, 4, 6.0]: Toadstool hub with a 2-arm padded puffball bar (moving mesh, pivot at hub centre)
- `mushroom_house_L` at [-12, 0, -21] size [8, 10, 8]: Mushroom house beside plaza
- `mushroom_house_R` at [12, 0, -24] size [7, 9, 7]: Mushroom house beside plaza
- `green_lanterns` at [-7, 0.6, -41] size [0.5, 3.5, 0.5]: Lantern posts flanking raised green
- `side_gap_lanterns` at [7.25, 0, -17] size [0.4, 2.5, 0.4]: Pair of small lantern posts on the plaza rails marking the east and west side gaps (x = +-7.25, on the rail tops)

## Concept prompt
First-person VR view from a mini golf tee at eye height looking into a cobbled mushroom-village plaza. A small carousel of giant white puffballs on two short padded stalks slowly turns on a red toadstool hub in the middle of the green felt, with clear gaps on both sides marked by little lantern posts on the rails. Behind it a short ramp climbs to a raised round green with a tall red flag, flanked by lantern posts. Red-capped mushroom houses with glowing round windows on both sides, strings of paper lanterns, falling maple leaves, golden afternoon light, playful cozy fairy-forest style.
