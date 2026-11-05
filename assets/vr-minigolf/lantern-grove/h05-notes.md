# Hole 5: Rootbridge Crossing (Par 3)

Zone: **Stream Crossing**. Gimmick: **Split path: narrow rail-less root bridge straight from the tee (risk) vs covered plank bridge (safe); a fall respawns at the bridge entry**.
Layout: `h05-layout.png`. Geometry: `holes.json` -> holes[4]. World offset [96, -1, -10], yaw 0.0.
Tee [0, 0, 0], cup [1.5, 0.0, -37.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
The **Rootbridge**: a gnarled, arched root bridge only 1.8 studs (0.54 m) wide and with no rails, spanning a clear babbling stream straight in line with the tee. To the left is a roofed **covered plank bridge** with lanterns. A glowing marker stone at the root-bridge entry shows where a ball that falls in comes back.

## Gimmick
Split path: narrow rail-less root bridge straight from the tee (risk) vs covered plank bridge (safe); a fall respawns at the bridge entry.

## Intended shots
**Risk line (good players):** one firm, dead-straight putt across the arched root bridge, finishing near the cup. Then a short putt (birdie or par). If it falls in the stream: +1 stroke and the ball respawns at the bridge entry (0, 0, -13.5), so the retry is a 13-stud bridge putt, not a full replay.
**Safe line:** 1) line up with the covered bridge on the shore; 2) putt through it; 3) approach; 4) putt out.

## Hole-in-one line
Brute-force search from the tee found ace lines (8 grid shots). The most robust: aim **271.5°** (atan2(dz,dx): direction (0.03, -1.00) in x/z, i.e. 1.5° right of straight -Z), speed **17.6 studs/s** (89% power). The red dashed line on the layout PNG traces it.

## Challenge
Nerve: a small aim error over 28 studs drops the ball in the stream. Since Round 5 a miss costs a stroke plus a short, easier retry from the bridge entry, so the bridge stays tempting after a splash. The covered bridge costs about a stroke but is almost risk-free.

## Moving parts / teleports (exact specs, also in holes.json)
- **hazard stream** (water): a ball that falls in gets +1 stroke and is placed at rest on the respawn point [0.0, 0.0, -13.5] (not back at the stroke start)

## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) standing in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [1.5, 7.5, -37.0]; visual only, no collision. Line of sight from the tee eye (5.5 studs above the tee) to the flag top: **visible** (min clearance over rails/felt/props +5.50 studs).

## Playtest stats (final, r5b, 2000 plays per skill)
| Skill | Avg strokes | HIO | Capped (8) | Strokes 1..8 |
|---|---|---|---|---|
| good | 2.46 | 2.2% | 0.0% | [44, 1405, 166, 361, 21, 3, 0, 0] |
| average | 3.79 | 0.0% | 0.0% | [0, 0, 684, 1068, 225, 23, 0, 0] |

## Props for 3D Model Bot (decoration only, sizes in studs)
Arched root bridge 3.5x3x14 (P1); covered plank bridge with shingle roof 7x6x14 (P1); stream water surface + banks (P1); bridge respawn marker stone 0.8x0.02x0.8 flush in the felt at (0, 0, -13.5) (P2, new); mossy stepping stones 2x1x2 (P3); small upstream waterfall 6x8x3 (P2); lanterns on the covered bridge (P1); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [1.5, 0.0, -37.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `root_bridge` at [0, 0.2, -21.5] (LANDMARK) size [3.5, 3, 14]: Gnarled arched root bridge (no rails), felt on top, 1.8 wide
- `covered_bridge` at [-10.5, 0, -21.5] size [7, 6, 14]: Plank covered bridge with shingle roof and lanterns
- `stream_rocks` at [4, -1, -21] size [2, 1, 2]: Mossy stepping stones in the stream
- `waterfall_bg` at [10, -1, -21] size [6, 8, 3]: Small waterfall feeding the stream (upstream, right side)
- `bridge_respawn_stone` at [0, 0, -13.5] size [0.8, 0.02, 0.8]: Glowing mossy marker stone set flush in the felt at the root-bridge entry: where a ball that falls in the stream reappears

## Concept prompt
First-person VR view at eye height from a mini golf tee on a grassy stream bank. Straight ahead, a narrow arched bridge made of twisted tree roots, topped with a thin strip of green felt and no railings, crosses a sparkling clear stream to a wide green with a tall red flag. A softly glowing mossy stone marks the foot of the root bridge. To the left, a cozy roofed wooden covered bridge with hanging lanterns offers the safe way across. Mossy stepping stones, a small waterfall upstream, autumn trees in red and gold, warm afternoon light and mist over the water, storybook fairy-forest style.
