# Hole 3: Ranger's Riverbend (Par 3)

Zone: **Sugarloaf Junction**. Gimmick: **River crossing: a rail-less log plank straight over the river (risky) or the railed ranger footbridge (safe); a ball in the river respawns at the plank entry**.
Layout: `h03-layout.png`. Geometry: `holes.json` -> holes[2]. World placement (from `world/world.json`): origin [-95.0, 18.0, 330.0], yaw -90.0.
Tee [0, 0, 0], cup [1.0, 0.0, -55.5] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
The **ranger station** on stilts with a fire-lookout cupola watches over the turquoise Sugarloaf River. Two crossings: a rail-less peeled **log plank** straight from the tee, and the railed **ranger footbridge** off to the west.

## Gimmick
River crossing: a rail-less log plank straight over the river (risky) or the railed ranger footbridge (safe); a ball in the river respawns at the plank entry.

## Intended shots
**Risky line:** straight down the 2-wide rail-less plank, 22 studs over the river, to the north bank and the cup (a 55-stud max-power putt can ace it).
**Safe line:** to the footbridge mouth, across the railed bridge, then two putts on the north bank.

## Hole-in-one line
Brute-force search from the tee found ace lines (4 grid shots). The most robust: aim **271.0°** (atan2(dz,dx): direction (0.02, -1.00) in x/z, i.e. 1.0° right of straight -Z), speed **19.0 studs/s** (96% power). The red dashed line on the layout PNG traces it.

## Challenge
Nerve and line. A ball that falls off the plank costs a stroke and **reappears at rest on the glowing marker stone at the plank entry** (not back at the tee). The footbridge is a sure par.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- **hazard river** (water): +1 stroke, ball placed at rest on the respawn point [0.0, 0.0, -28.5]


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [1.0, 7.5, -55.5]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +5.50 studs).

## Playtest stats (p7; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.74 | 9.2% | 68% | 0.0% | 0 / 0 | [183, 932, 239, 560, 39, 46, 1, 0] |
| average | 3.70 | 0.0% | 42% | 0.0% | 0 / 0 | [0, 0, 836, 937, 212, 15, 0, 0] |

## Props for the 3D modeler (decoration only, sizes in studs)
Ranger station + lookout cupola 10x18x10 (P1, world dressing); peeled-log plank 2.6x1.2x22 (P1); railed footbridge with rope railings 6x3x22 (P1); respawn marker stone flush in the felt (P1); signs x2 (P1); river rocks, canoe (P3); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [1.0, 0.0, -55.5] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `ranger_station` at [-19, 0, -20] (LANDMARK) size [10, 18, 10]: Ranger station on stilts with a fire-lookout cupola, west of the shore (outside the footprint, in the world dressing)
- `log_plank` at [0, 0, -41.0] size [2.6, 1.2, 22]: Rail-less peeled-log plank, felt on top, 2 wide, straight over the river
- `ranger_footbridge` at [-8.5, 0, -41.0] size [6, 3, 22]: Railed timber footbridge with rope railings and lantern posts at both ends
- `plank_respawn_stone` at [0, 0, -28.5] size [0.8, 0.02, 0.8]: Glowing turquoise marker stone set flush in the felt at the plank entry: where a ball that falls in the river reappears
- `sign_plank` at [2.2, 0, -27.5] size [1.6, 2.6, 0.2]: Sign 'Log Plank - no rails!' with a splash icon beside the plank entry
- `sign_bridge` at [-13.1, 0, -24] size [1.8, 3.2, 0.25]: Ranger sign 'Footbridge - the safe way' pointing to the footbridge
- `route_arrow_plank` at [0, 0, -25] size [1.4, 0.01, 2.0]: RISKY PLANK: straight north toward the narrow crossing
- `route_arrow_bridge` at [-8.5, 0, -25] size [1.4, 0.01, 2.0]: SAFE FOOTBRIDGE: north along the railed crossing
- `river_rocks` at [5, -1.5, -41] size [6, 1, 8]: Turquoise river with foam, stepping stones and a sunken canoe downstream

## Concept prompt
First-person VR view at eye height from a mini golf tee on a riverbank in a candy-striped canyon at sunset: a narrow rail-less log bridge runs straight across a clear turquoise river to a green with a red flag; to the left a railed timber footbridge with rope railings; a ranger station on stilts with a lookout cupola; Old Sugarloaf beyond. Style: candy-striped sunset desert canyon, pink and cream banded sandstone, rock-candy crystals, lollipop saguaros, warm golden low sun from the west, lilac haze, chunky whimsical Roblox-friendly shapes, no text.
