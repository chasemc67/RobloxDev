# Hole 5: Geyser Hop (Par 3)

Zone: **Steamwhistle Lagoons**. Gimmick: **Geyser lift: a basalt platform rides a steam column up 4 studs to the upper green, pauses, and sinks back; roll on while it is down**.
Layout: `h05-layout.png`. Geometry: `holes.json` -> holes[4]. World placement (from `world/world.json`): origin [215.0, 84.0, 420.0], yaw -90.0.
Tee [0, 0, 0], cup [-4.0, 4.0, -45.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
**Steamwhistle Geyser**, a basalt cone beside the upper green, puffs and whistles; at the foot of the 4-stud basalt cliff a hexagonal **geyser platform** rides a steam column between the basin and the upper green.

## Gimmick
Geyser lift: a basalt platform rides a steam column up 4 studs to the upper green, pauses, and sinks back; roll on while it is down.

## Intended shots
1. Roll onto the platform while it sits flush with the basin (the signal lamp is green): it holds the ball, rises 4 studs and puffs it out onto the upper green toward the cup (harder entry, stronger puff).
2. Putt out on the upper green. If the platform is up, the ball bounces off its basalt side: wait and go again.

## Hole-in-one line
Brute-force search from the tee found ace lines (2419 grid shots). The most robust: aim **244.5°** (atan2(dz,dx): direction (-0.43, -0.90) in x/z, i.e. 25.5° left of straight -Z), speed **16.8 studs/s** (85% power), start phase t=0.0s of the moving parts. The red dashed line on the layout PNG traces it.

## Challenge
First mover: platform DOWN 8 s (boarding window), rises 4 at 2 studs/s, UP 1.5 s, sinks at 2 studs/s (cycle 13.5 s). Puff speed = clamp(entry x 0.9, 3.5, 12) studs/s along the exit line.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- **geyser_column** (slide): pivot [0.0, 0.0, -26.5], axis [0, 1, 0], speed 2.0 studs/s, ping-pong 0.0..4.0 studs with pauses 8 s at 0, 1.5 s at 4, phase 0.0, cycle 13.50 s. Blockers (relative to pivot at angle/offset 0): box [3.0, 4.0, 3.0] at [0, -2.0, 0]. Visual: Basalt platform 3x3 on a steam column at the cliff foot. Collider = a 3x4x3 box whose top is the platform: offset 0 = top flush with the basin felt (y 0, box y -4..0, sunk in a shaft), offset 4 = top flush with the upper green (y 4). Profile: pause DOWN 8 s (boarding window, steam simmering) -> rise 4 at 2 studs/s -> pause UP 1.5 s (big puff + whistle) -> sink 4 at 2 studs/s.
- **lift geyser_lift**: rectangle centre [0.0, 0.0, -26.5] +- [1.5, 1.5] -> exit [0.0, 4.0, -29.6] dir [-0.2514, -0.9679], exit speed = clamp(in x 0.9, 3.5, 12.0) studs/s. Platform top = the trigger. Boarding: while the platform is flush (cycle t in [0, 8) s) a ball whose centre rolls onto it is held in its steam-vent dimple (script: anchor it, record its entry speed). It rides up; at t = 10.1 s (0.1 s into the top pause) the geyser puffs it onto the upper green from [0, 4, -29.6] along exit.dir at clamp(entry speed x 0.9, 3.5, 12) studs/s. A ball that drops in from the upper green is held and puffed out the same way at the next release. Drop-ins from the upper green use a trigger 0.15 wider each side (lift.drop_half_size, x +-1.65) so a ball slipping past the trimmed upper-rail ends into the clearance slot beside the column is held too. Lift schedule: cycle 13.5 s, boarding while t mod cycle in [0, 8) s, release at 10.1 s, column = moving part `geyser_column`. **Engine contract:** hold (anchor) the ball once its centre is on the platform, carry it with the platform, and at the release time set its velocity exactly as above.

## Timing check (`tools/timing_check.py`, 96 phases; actual fuzz counts per line)
- geyser_column [intended] tee shot onto the geyser platform while it is flush (lifted to the upper green): blocked 40/96 (40 stops + 0 kicks), deflected 0, **Studio estimate 41.7%** (stops + 0.36 kicks), passed 58.3%, traps 0, fuzz 100000 shots: timeouts 0, pinned rests 0, escapes 0, excluded rests 0
- geyser_column [ace] brute-force ace line: blocked 39/96 (39 stops + 0 kicks), deflected 0, **Studio estimate 40.6%** (stops + 0.36 kicks), passed 59.4%, traps 0

### vr_comfort (exact hole-local studs)

```json
{
  "tier_steps": {
    "id": "geyser_steps",
    "where": "outside the basin's east rail, x 9..12, z -16..-28",
    "rise": 4.0,
    "steps": 5,
    "tread": 1.5,
    "railing": "3.5-high railing with solid lower board on the open (west) side; parapet along the upper green's south edge east of the shaft"
  },
  "note": "the player walks up timber steps beside the cliff; the ball rides the geyser"
}
```

## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [-4.0, 11.5, -45.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +4.17 studs).

## Playtest stats (clear; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.78 | 9.0% | 78% | 0.1% | 0 / 0 | [180, 824, 558, 245, 119, 46, 16, 12] |
| average | 3.47 | 0.0% | 58% | 0.4% | 0 / 0 | [0, 452, 706, 509, 204, 69, 39, 21] |

## Props for the 3D modeler (decoration only, sizes in studs)
Moving hexagonal basalt platform with steam-vent dimple, pivot = platform top centre (P1); translucent steam column (P1); Steamwhistle Geyser cone (P1, landmark); cliff face with brass rivets (P2); green/amber signal lamp (P1); timber steps for the player (P1); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [-4.0, 4.0, -45.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `steamwhistle_geyser` at [-10.5, 4.0, -33.0] (LANDMARK) size [6, 7, 6]: Steamwhistle Geyser: a 6-wide basalt cone outside the upper green's west rail; its steam column puffs to 60 studs every 20 s and whistles (visual only). A brass pressure gauge on the platform's side shows the cycle
- `geyser_platform` at [0.0, 0, -26.5] size [3.0, 4, 3.0]: Moving mesh: hexagonal basalt platform (top 3x3, pivot = platform top centre at offset 0) riding a translucent steam column; a shallow steam-vent dimple in the top holds the ball. Visual must cover the collider box exactly
- `cliff_face` at [0, 0, -28.0] size [16, 4, 1]: Basalt cliff face between the tiers (4 high) with frost streaks; the shaft behind the platform is lined with brass rivets
- `signal_lamp` at [3.0, 4.5, -28.3] size [0.6, 1.0, 0.4]: Green/amber steam lamp on the cliff face: green while the platform is flush (boarding window), amber while it rides
- `geyser_arrow` at [0.0, 0.0, -18.0] size [1.4, 0.01, 2.0]: Glowing felt arrow decal pointing at the platform, with a little 'wait for the green lamp' icon

## Concept prompt
First-person VR view at eye height from a mini golf tee at night on a steaming lagoon island: a felt lane leads to a small basin at the foot of a 4-stud basalt cliff, where a hexagonal stone platform rises on a white steam column toward an upper green with a red flag; a basalt geyser cone beside it blasts a tall steam plume into the aurora sky; turquoise hot springs, frosted palms and brass lanterns. Style: stylised 3D storybook render matching the Aurora Archipelago menu card: floating snow-capped slate-violet rock islands over a soft lilac cloud sea at night, thick rounded moonlit snow, translucent glowing glacier-cyan ice and crystal clusters, warm brass lanterns on chunky snow-capped timber posts, snowy blue-green pines, bright green felt with a white ball and a red flag, green and violet aurora ribbons across a starry indigo sky, the Starfrost Spire glowing on the skyline, soft bloom, cosy and whimsical, chunky Roblox-friendly shapes, no text, no UI.
