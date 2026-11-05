# Hole 13: Hoodoo Maze (Par 3)

Zone: **Hoodoo Garden**. Gimmick: **Pillar maze: hoodoo pillars and striped rock make three corridors of different length and risk**.
Layout: `h13-layout.png`. Geometry: `holes.json` -> holes[12]. World placement (from `world/world.json`): origin [-300.0, 150.0, -290.0], yaw 180.0.
Tee [0, 0, 0], cup [0.5, 0.0, -51.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A cluster of striped **hoodoo spires** with balanced gumdrop caps; low banded rock walls split the maze into three corridors.

## Gimmick
Pillar maze: hoodoo pillars and striped rock make three corridors of different length and risk.

## Intended shots
**Centre (birdie/ace):** straight through the 4-wide centre corridor past two staggered hoodoos onto the green.
**West (safe):** into the west corridor, up it past one hoodoo onto the green, then putt across.
**East:** the scenic route, ending far from the cup.

## Hole-in-one line
Brute-force search from the tee found ace lines (9 grid shots). The most robust: aim **270.5°** (atan2(dz,dx): direction (0.01, -1.00) in x/z, i.e. 0.5° right of straight -Z), speed **17.6 studs/s** (89% power). The red dashed line on the layout PNG traces it.

## Challenge
Line through the hoodoos. A gumdrop-glass lantern hangs over the cup as the cue where hoodoos hide the flag.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- none


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [0.5, 7.5, -51.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +5.50 studs).

## Playtest stats (p7; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.35 | 2.7% | 92% | 0.1% | 0 / 0 | [54, 1400, 388, 129, 17, 6, 4, 2] |
| average | 4.27 | 0.0% | 21% | 0.5% | 0 / 0 | [0, 0, 422, 889, 511, 104, 55, 19] |

## Props for the 3D modeler (decoration only, sizes in studs)
Hoodoo spires x5 over the bumper bases (P1); banded maze rock walls (P1, landmark); lantern cue, no collision (P1); signs x3 (P1); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [0.5, 0.0, -51.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `hoodoo_1` at [-1.1, 0, -24.0] size [1.6, 12, 1.6]: Striped hoodoo spire (1 base collider, yaw 45) 8-14 studs tall with a balanced gumdrop cap
- `hoodoo_2` at [1.1, 0, -32.0] size [1.6, 12, 1.6]: Striped hoodoo spire (1 base collider, yaw 45) 8-14 studs tall with a balanced gumdrop cap
- `hoodoo_3` at [-13.0, 0, -30.0] size [2.0, 12, 2.0]: Striped hoodoo spire (1.4 base collider, yaw 45) 8-14 studs tall with a balanced gumdrop cap
- `hoodoo_4` at [11.5, 0, -24.0] size [2.0, 12, 2.0]: Striped hoodoo spire (1.4 base collider, yaw 45) 8-14 studs tall with a balanced gumdrop cap
- `hoodoo_5` at [10.2, 0, -33.0] size [1.7999999999999998, 12, 1.7999999999999998]: Striped hoodoo spire (1.2 base collider, yaw 0) 8-14 studs tall with a balanced gumdrop cap
- `maze_rock` at [-5.5, 0, -28] (LANDMARK) size [7, 4, 24]: Striped hoodoo-rock walls between the corridors (colliders 1 tall on the rails; dressed as 3-5 tall banded rock and hoodoo clusters, kept below the tee->flag sightline over the centre corridor)
- `lantern_cue` at [0.5, 9.0, -51.0] size [1.0, 1.5, 1.0]: Gumdrop-glass lantern hanging 9 studs over the cup from a rope between two hoodoos: the visual cue when the hoodoos hide the flag
- `sign_west` at [-14.6, 0, -10] size [1.8, 3.2, 0.25]: Sign 'Long & easy' pointing into the west corridor
- `sign_centre` at [-2.6, 0, -15.5] size [1.8, 3.2, 0.25]: Sign 'Straight through (mind the hoodoos!)' at the centre corridor
- `sign_east` at [14.6, 0, -10] size [1.8, 3.2, 0.25]: Sign 'Scenic route' pointing into the east corridor
- `route_arrow_west` at [-11.5, 0, -13] size [1.4, 0.01, 2.0]: SAFE WEST: north from foyer into the marked corridor
- `route_arrow_centre` at [0, 0, -13] size [1.4, 0.01, 2.0]: SHORT CENTRE: north from foyer into the marked corridor
- `route_arrow_east` at [11.5, 0, -13] size [1.4, 0.01, 2.0]: SCENIC EAST: north from foyer into the marked corridor

## Concept prompt
First-person VR view at eye height on a high bench among striped hoodoo spires topped with giant gumdrops: three felt corridors between low banded rock walls, the middle one dotted with hoodoos, a gumdrop lantern hanging over a hidden cup ahead. Style: candy-striped sunset desert canyon, pink and cream banded sandstone, rock-candy crystals, lollipop saguaros, warm golden low sun from the west, lilac haze, chunky whimsical Roblox-friendly shapes, no text.
