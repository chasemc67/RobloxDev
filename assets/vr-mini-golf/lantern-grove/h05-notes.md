# Hole 5: Rootbridge Crossing (Par 3)

Zone: **Stream Crossing**. Gimmick: **Split path: narrow rail-less root bridge straight from the tee (risk) vs covered plank bridge (safe), water hazard**.
Layout: `h05-layout.png`. Geometry: `holes.json` -> holes[4]. World offset [96, -1, -10], yaw 0.0.
Tee [0, 0, 0], cup [1.5, 0.0, -37.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
The **Rootbridge**: a gnarled, arched root bridge only 1.8 studs (0.54 m) wide and with no rails, spanning a clear babbling stream straight in line with the tee. To the left is a roofed **covered plank bridge** with lanterns.

## Gimmick
Split path: narrow rail-less root bridge straight from the tee (risk) vs covered plank bridge (safe), water hazard.

## Intended shots
**Risk line (good players):** one firm, dead-straight putt across the arched root bridge, finishing near the cup. Then a short putt (birdie or par).
**Safe line:** 1) line up with the covered bridge on the shore; 2) putt through it; 3) approach; 4) putt out.

## Hole-in-one line
Brute-force search from the tee found ace lines (8 grid shots). The most robust: aim **271.5°** (atan2(dz,dx): direction (0.03, -1.00) in x/z, i.e. 1.5° right of straight -Z), speed **17.6 studs/s** (89% power). The red dashed line on the layout PNG traces it.

## Challenge
Pure nerve: a small aim error over 28 studs drops the ball in the stream (+1, replay from the tee). The covered bridge costs about a stroke but is almost risk-free.

## Moving parts / teleports (exact specs, also in holes.json)
- none

## Playtest stats (final, p4, 2000 plays per skill)
| Skill | Avg strokes | HIO | Capped (8) | Strokes 1..8 |
|---|---|---|---|---|
| good | 2.49 | 2.2% | 0.0% | [44, 1406, 163, 320, 44, 20, 1, 2] |
| average | 3.79 | 0.0% | 0.0% | [0, 0, 684, 1068, 225, 23, 0, 0] |

## Props for 3D Model Bot (decoration only, sizes in studs)
Arched root bridge 3.5x3x14 (P1); covered plank bridge with shingle roof 7x6x14 (P1); stream water surface + banks (P1); mossy stepping stones 2x1x2 (P3); small upstream waterfall 6x8x3 (P2); lanterns on the covered bridge (P1).

Decoration anchors (position in hole-local studs):
- `root_bridge` at [0, 0.2, -21.5] (LANDMARK) size [3.5, 3, 14]: Gnarled arched root bridge (no rails), felt on top, 1.8 wide
- `covered_bridge` at [-10.5, 0, -21.5] size [7, 6, 14]: Plank covered bridge with shingle roof and lanterns
- `stream_rocks` at [4, -1, -21] size [2, 1, 2]: Mossy stepping stones in the stream
- `waterfall_bg` at [10, -1, -21] size [6, 8, 3]: Small waterfall feeding the stream (upstream, right side)

## Concept prompt
First-person VR view at eye height from a mini golf tee on a grassy stream bank. Straight ahead, a narrow arched bridge made of twisted tree roots, topped with a thin strip of green felt and no railings, crosses a sparkling clear stream to a wide green with a red flag. To the left, a cozy roofed wooden covered bridge with hanging lanterns offers the safe way across. Mossy stepping stones, a small waterfall upstream, autumn trees in red and gold, warm afternoon light and mist over the water, storybook fairy-forest style.
