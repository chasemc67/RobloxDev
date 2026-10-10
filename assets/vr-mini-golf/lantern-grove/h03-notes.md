# Hole 3: Toadstool Row (Par 3)

Zone: **Mushroom Village**. Gimmick: **S-bend with two steep banked-plane corners and a stem tunnel**.
Layout: `h03-layout.png`. Geometry: `holes.json` -> holes[2]. World offset [4, 1, -66], yaw 0.0.
Tee [0, 0, 0], cup [15.5, 0.0, -30.5] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A **red-cap mushroom house** whose thick cream stem has an arched tunnel straight through it (opening 7 wide x 3 high). The felt runs inside. A fat spotted **toadstool stool** guards the cup on the green.

## Gimmick
S-bend with two steep banked-plane corners and a stem tunnel.

## Intended shots
1. Hit up the lane into the **steep banked corner** (a 45° pitched bank backed by a rail). It swings the ball right, through the stem tunnel.
2. The second bank swings it left up the leg onto the green. A strong first putt can ride both banks and reach the green.
3. Putt around the toadstool stool to the cup.

## Hole-in-one line
Brute-force search from the tee found ace lines (3 grid shots). The most robust: aim **243.5°** (atan2(dz,dx): direction (-0.45, -0.89) in x/z, i.e. 26.5° left of straight -Z), speed **19.8 studs/s** (100% power). The red dashed line on the layout PNG traces it.

## Challenge
Pace through two banks. Too soft and the ball stalls in the tunnel. Too hard and it climbs the bank, clatters off the backing rail and loses its line. The stool forces the last putt to curl in from the left.

## Moving parts / teleports (exact specs, also in holes.json)
- none

## Playtest stats (final, p4, 2000 plays per skill)
| Skill | Avg strokes | HIO | Capped (8) | Strokes 1..8 |
|---|---|---|---|---|
| good | 2.79 | 2.6% | 0.4% | [52, 890, 733, 184, 72, 39, 18, 12] |
| average | 3.81 | 0.0% | 0.4% | [0, 217, 648, 660, 322, 105, 32, 16] |

## Props for 3D Model Bot (decoration only, sizes in studs)
Mushroom house large with stem tunnel 10x12x10 (P1); mushroom house medium 7x9x7 (P1); toadstool stool cladding for `toadstool_stool` 2x1.8x2 (P1); bank cladding (rounded stone banks on bank1/bank2, 1.2-stud plane, 9 long) (P1); small toadstool cluster 3x2.5x3 (P2); lantern string 12x1x0.3 (P2).

Decoration anchors (position in hole-local studs):
- `stem_house` at [8.5, 0, -12] (LANDMARK) size [10, 12, 10]: Red-cap mushroom house; felt tunnel runs through its stem (5 long, 3 high opening)
- `small_toadstools` at [-6, 0, -6] size [3, 2.5, 3]: Cluster of 3 small toadstools
- `house_2` at [26, 0, -14] size [7, 9, 7]: Second mushroom house with round window
- `toadstool_stool_deco` at [17.0, 0, -28.8] size [2, 1.8, 2]: Fat spotted toadstool stool guarding the cup (bumper block 1.6x1.5x1.6)
- `lantern_string` at [17.5, 4, -22] size [12, 1, 0.3]: Lantern string across green entrance

## Concept prompt
First-person VR view at eye height from a mini golf tee in a mushroom village. A green felt lane runs ahead to a steeply banked stone corner that curves right, straight into an arched tunnel bored through the thick cream stem of a giant red-capped mushroom house with round glowing windows. Beyond, the path banks left again toward a lantern-strung green with a fat spotted toadstool beside the red flag. Little wooden porches, tiny doors, paper lanterns, orange and red autumn foliage, warm late-afternoon light, cozy whimsical fairy-tale style.
