# Hole 4: Spore Spinner (Par 3)

Zone: **Mushroom Village**. Gimmick: **Rotating 2-arm spinner bar in a plaza, then ramp up to a raised green**.
Layout: `h04-layout.png`. Geometry: `holes.json` -> holes[3]. World offset [52, 1, -60], yaw 0.0.
Tee [0, 0, 0], cup [2.5, 0.6, -42.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
The **Puffball Carousel**: a toadstool hub in the middle of a widened plaza, turning a 2-arm bar of puffball stalks (9 studs across) at a lazy 36°/s. Mushroom houses flank the plaza, and a raised green sits beyond a short ramp.

## Gimmick
Rotating 2-arm spinner bar in a plaza, then ramp up to a raised green.

## Intended shots
1. Time the shot through the plaza past the turning bar (or slip down a side gap). Run it up the 0.6-stud ramp onto the raised green.
2–3. Putt out. A ball clipped by the bar caroms off at the bar's surface speed.

## Hole-in-one line
Brute-force search from the tee found ace lines (98 grid shots). The most robust: aim **272.5°** (atan2(dz,dx): direction (0.04, -1.00) in x/z, i.e. 2.5° right of straight -Z), speed **17.9 studs/s** (91% power), start phase t=1.5s of the moving parts. The red dashed line on the layout PNG traces it.

## Challenge
First timing obstacle. The bar is slow enough to read in VR (a full turn every 10 s, an arm passes every 5 s). Getting knocked back costs a stroke or two. Diagonal shots up the ramp curl back, so come in straight.

## Moving parts / teleports (exact specs, also in holes.json)
- **spinner** (rotate): pivot [0, 0, -21], axis [0, 1, 0], speed 36.0 deg/s, continuous, phase 0.0, cycle 10.0 s. Blockers (relative to pivot at angle/offset 0): box [3.8, 1.0, 0.7] at [2.6, 0.5, 0.0]; box [3.8, 1.0, 0.7] at [-2.6, 0.5, -0.0] yaw 180.0. Visual: 2 puffball-stalk arms (one long bar) on a toadstool hub

## Playtest stats (final, p4, 2000 plays per skill)
| Skill | Avg strokes | HIO | Capped (8) | Strokes 1..8 |
|---|---|---|---|---|
| good | 3.84 | 1.8% | 1.7% | [36, 258, 698, 472, 275, 130, 61, 70] |
| average | 4.09 | 0.8% | 2.5% | [15, 285, 562, 475, 281, 176, 98, 108] |

## Props for 3D Model Bot (decoration only, sizes in studs)
Puffball carousel bar (moving, pivot hub centre, axis +Y) 9x1x0.7 arms + puffballs (P1); toadstool hub 1.4x2x1.4 (P1); mushroom houses x2 7–8x9–10x7–8 (P1); green lantern posts 0.5x3.5x0.5 (P1); paper lanterns (P2).

Decoration anchors (position in hole-local studs):
- `puffball_carousel` at [0, 0, -21] (LANDMARK) size [9, 4, 9]: Toadstool hub with a 2-arm puffball bar (moving mesh, pivot at hub centre)
- `mushroom_house_L` at [-12, 0, -21] size [8, 10, 8]: Mushroom house beside plaza
- `mushroom_house_R` at [12, 0, -24] size [7, 9, 7]: Mushroom house beside plaza
- `green_lanterns` at [-7, 0.6, -41] size [0.5, 3.5, 0.5]: Lantern posts flanking raised green

## Concept prompt
First-person VR view from a mini golf tee at eye height looking into a cobbled mushroom-village plaza. A big carousel of giant white puffballs on curved stalks slowly turns on a red toadstool hub in the middle of the green felt. Behind it a short ramp climbs to a raised round green with a red flag, flanked by lantern posts. Red-capped mushroom houses with glowing round windows on both sides, strings of paper lanterns, falling maple leaves, golden afternoon light, playful cozy fairy-forest style.
