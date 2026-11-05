# Hole 18: Sunset Arch (Par 4)

Zone: **Sugarloaf Crown**. Gimmick: **Finale: bank round a hoodoo, ramp up under the arch, then a geode-shortcut teleport or the rim route to a cliff-edge green**.
Layout: `h18-layout.png`. Geometry: `holes.json` -> holes[17]. World placement (from `world/world.json`): origin [-420.0, 190.0, 236.0], yaw 0.0.
Tee [0, 0, 0], cup [8.0, 0.8, -64.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A natural candy-striped **arch** spans the ramp, framing the sunset; a twin **geode** shortcut glows on the plateau; the cliff-edge green looks over the whole canyon.

## Gimmick
Finale: bank round a hoodoo, ramp up under the arch, then a geode-shortcut teleport or the rim route to a cliff-edge green.

## Intended shots
1. Play round the hoodoo at the end of the tee lane into the banked NE corner, west past the junction into the banked NW corner and up the ramp under the arch.
2. From the plateau: into the geode (it pops out by the cup) for a birdie try, or up the rim lane.
3-4. Putt on the cliff-edge green.
Ace: a full tee shot that rides both banks and the ramp straight into the geode.

## Hole-in-one line
Brute-force search from the tee found ace lines (5 grid shots). The most robust: aim **254.5°** (atan2(dz,dx): direction (-0.27, -0.96) in x/z, i.e. 15.5° left of straight -Z), speed **18.7 studs/s** (94% power). The red dashed line on the layout PNG traces it.

## Challenge
The finale strings the course together: bank, climb, shortcut or safe route. The geode exit uses 0.7 times entry speed, clamped to 1.5–7 studs/s: only a ball arriving fast holes out, a gentle plateau putt leaves a tap-in.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- **teleport geode**: entry [-9.5, 0.8, -32.0] r 0.55 -> exit [13.0, 0.8, -59.0] dir [-0.7071, -0.7071], exit speed = clamp(in x 0.7, 1.5, 7.0) studs/s. Cracked-open amethyst-and-rock-candy geode set in the plateau felt straight up the ramp line (entry) -> twin geode on the cliff-edge green (exit), aimed at the cup


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [8.0, 8.3, -64.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +3.26 studs).

## Playtest stats (p7; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 3.45 | 0.9% | 83% | 0.0% | 0 / 0 | [17, 633, 270, 746, 214, 97, 20, 3] |
| average | 4.25 | 0.0% | 57% | 0.3% | 0 / 0 | [0, 286, 421, 441, 400, 295, 131, 26] |

## Props for the 3D modeler (decoration only, sizes in studs)
Natural arch over the ramp (P1, landmark); hoodoo with gumdrop cap (P1); geode entry + exit (P1); cliff-edge rope railing (P1); rim sign (P1); felt arrow (P1); flag 7.5 (P1). The big Sunset Arch backdrop is world dressing.

Decoration anchors (position in hole-local studs):
- `cup_flag` at [8.0, 0.8, -64.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `arch_gate` at [-9, 0, -26] (LANDMARK) size [10, 13, 4]: Natural candy-striped sandstone arch spanning the ramp (feet outside the rails at x -13.25 and -4.75, opening 7.5 wide x 10 high), framing the sunset to the west
- `hoodoo_deco` at [0.0, 0, -11.0] size [2.2, 10, 2.2]: Striped hoodoo with a gumdrop cap on the 1.6 bumper (turned 45) at the end of the tee lane: play round it into the banked corner
- `geode_entry` at [-9.5, 0.8, -32.0] size [1.6, 0.3, 1.6]: Cracked geode bowl flush in the plateau felt, glowing violet (trigger radius 0.55)
- `geode_exit` at [13.0, 0.8, -59.0] size [1.6, 0.6, 1.6]: Twin geode on the green's east side (teleport exit)
- `cliff_edge` at [0, 0.8, -70] size [26, 2, 1]: Cliff-edge rope railing on carved posts along the green's north and east rails; the Crown drops away to the canyon beyond (the sunset view)
- `sign_rim` at [-12.6, 0.8, -42] size [1.8, 3.2, 0.25]: Sign 'Rim Trail' pointing north along the rim
- `felt_arrow_bank` at [1.0, 0.0, -10.0] size [2.0, 0.01, 2.6]: Glowing felt arrow decal curving right-then-left: 'bank it round the hoodoo'

## Concept prompt
First-person VR view at eye height on the highest mesa at sunset: a felt lane with a striped hoodoo ahead, banked corners leading to a ramp under a natural candy-striped stone arch, a glowing violet geode on the plateau beyond, a cliff-edge green with a red flag and the whole canyon below. Style: candy-striped sunset desert canyon, pink and cream banded sandstone, rock-candy crystals, lollipop saguaros, warm golden low sun from the west, lilac haze, chunky whimsical Roblox-friendly shapes, no text.
