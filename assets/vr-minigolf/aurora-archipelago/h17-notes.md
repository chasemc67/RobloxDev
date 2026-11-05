# Hole 17: Aurora Bridge (Par 3)

Zone: **Skylight Summit**. Gimmick: **Timed light bridge: an aurora ribbon span fades in, holds solid, then dims away; or take the fixed ice bridge the long way; misses respawn at the gap edge (+1)**.
Layout: `h17-layout.png`. Geometry: `holes.json` -> holes[16]. World placement (from `world/world.json`): origin [-165.0, 222.0, -262.0], yaw 0.0.
Tee [0, 0, 0], cup [2.2, 0.0, -56.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
An **aurora ribbon** pours out of the sky into a glowing **light span** between two crystal piers over the open-sky Aurora Gap; the fixed ice bridge runs to the right.

## Gimmick
Timed light bridge: an aurora ribbon span fades in, holds solid, then dims away; or take the fixed ice bridge the long way; misses respawn at the gap edge (+1).

## Intended shots
**Timing line:** straight over the crystal piers and the light span while it glows solid (birdie, ace line).
**Safe line:** the fixed railed ice bridge to the right, then two putts.

## Hole-in-one line
Brute-force search from the tee found ace lines (48 grid shots). The most robust: aim **287.0°** (atan2(dz,dx): direction (0.29, -0.96) in x/z, i.e. 17.0° right of straight -Z), speed **19.4 studs/s** (98% power), start phase t=0.0s of the moving parts. The red dashed line on the layout PNG traces it.

## Challenge
Appear/vanish toggle (cycle 9 s: fade in 0.6 s, solid 6 s, fade out 0.6 s, gone 1.8 s). The span's collider only exists while it is fully solid; a ball on it when it dims falls (+1, respawns at the light-route entry). The crystal lamp glows mint while it is solid.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- **aurora_span** (toggle = appear/vanish timed surface): felt ['light_span'], cycle 9 s, phase 0 s, profile fade_in 0.6 s, solid 6 s, fade_out 0.6 s, gone 1.8 s; collider ONLY in [0.6, 6.6) s of each cycle. Aurora ribbon span 3 x 8 (Neon, animated mint->violet gradient) between the crystal piers. Cycle 9 s from t=0: FADE IN 0.6 s (Transparency 1 -> 0, CanCollide false) -> SOLID 6 s (Transparency 0, CanCollide TRUE) -> FADE OUT 0.6 s (0 -> 0.85, CanCollide false) -> GONE 1.8 s (Transparency 1, CanCollide false). The collider exists ONLY in the solid window [0.6, 6.6) s; a ball on it when it switches off falls into the gap (+1, respawn at the light-route entry).
- **hazard aurora_gap** (pit): +1 stroke, ball placed at rest on the respawn point [0.0, 0.0, -14.5]

## Timing check (`tools/timing_check.py`, 96 phases; actual fuzz counts per line)
- aurora_span [intended] tee shot straight over the aurora light span (fixed crystal piers either side): blocked 40/96 (40 stops + 0 kicks), deflected 0, **Studio estimate 41.7%** (stops + 0.36 kicks), passed 58.3%, traps 0, fuzz 100000 shots: timeouts 0, pinned rests 0, escapes 0, excluded rests 0
- aurora_span [ace] brute-force ace line: blocked 0/96 (0 stops + 0 kicks), deflected 0, **Studio estimate 0%** (stops + 0.36 kicks), passed 100%, traps 0

### vr_comfort (exact hole-local studs)

```json
{
  "player_guards": [
    {
      "id": "guard_south_rim",
      "center": [
        0,
        2.0,
        -15.75
      ],
      "size": [
        26,
        4,
        0.3
      ],
      "yaw": 0,
      "note": "south gap rim (PlayerGuard: the ball passes)"
    },
    {
      "id": "guard_north_rim",
      "center": [
        0,
        2.0,
        -42.25
      ],
      "size": [
        26,
        4,
        0.3
      ],
      "yaw": 0,
      "note": "north gap rim"
    },
    {
      "id": "guard_light_w",
      "center": [
        -1.65,
        2.0,
        -29.0
      ],
      "size": [
        0.3,
        4,
        26
      ],
      "yaw": 0,
      "note": "both sides of the light route"
    },
    {
      "id": "guard_light_e",
      "center": [
        1.65,
        2.0,
        -29.0
      ],
      "size": [
        0.3,
        4,
        26
      ],
      "yaw": 0,
      "note": ""
    }
  ],
  "player_deck": {
    "id": "ice_walk_deck",
    "x": [
      8.5,
      12.5
    ],
    "z": [
      -16.0,
      -42.0
    ],
    "y": 0.0,
    "width": 4.0,
    "rails": "both, 3.5 high with solid lower board",
    "note": "railed walk-on ice deck beside the safe ball bridge"
  },
  "note": "player-only; the ball sees felt, rails and the pit/respawn"
}
```

## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [2.2, 7.5, -56.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +5.50 studs).

## Playtest stats (clear; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 3.12 | 6.9% | 62% | 0.4% | 0 / 0 | [137, 1049, 45, 2, 758, 1, 1, 7] |
| average | 3.57 | 0.0% | 52% | 0.0% | 0 / 0 | [0, 0, 1033, 810, 145, 11, 1, 0] |

## Props for the 3D modeler (decoration only, sizes in studs)
Aurora ribbon + light span (Neon, animated mint->violet, toggled collider) (P1, landmark); crystal piers (P1); fixed ice bridge + player deck (P1); timing lamp (P1); respawn stone (P1); signs + arrows (P1); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [2.2, 0.0, -56.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `aurora_ribbon` at [0, 0, -29.0] (LANDMARK) size [3, 60, 8]: An aurora ribbon pours down out of the sky (Neon, mint #5CFFB0 -> violet #B07CFF) and pools into the light span; it brightens as the span fades in and frays into sparkles as it dims. Ribbon above y 10 only
- `crystal_piers` at [0, 0, -29.0] size [4.0, 1.5, 26]: Two glowing crystal piers (3 wide, 9 long each) with frosted ice rails, reaching out from both rims toward each other
- `ice_bridge` at [6.0, 0, -29.0] size [5.0, 2, 26]: Fixed railed ice bridge (glass deck, snow-capped timber ball rails)
- `span_respawn_stone` at [0.0, 0.0, -14.5] size [0.8, 0.02, 0.8]: Glowing aurora-lime marker stone flush in the felt at the light-route entry: where a ball that falls into the gap reappears
- `span_lamp` at [-2.4, 0, -15.0] size [0.6, 2.4, 0.6]: Crystal timing lamp beside the pier mouth: glows mint while the span is solid, violet while it fades, dark while it is gone (visual cue)
- `sign_light` at [-2.6, 0, -13.0] size [1.6, 2.6, 0.2]: Sign 'Aurora span - wait for the glow!' beside the light route
- `sign_bridge` at [8.6, 0, -11.0] size [1.8, 3.2, 0.25]: Lantern sign 'Ice bridge - the long, safe way' pointing to the fixed bridge
- `route_arrow_light` at [0, 0, -12.0] size [1.4, 0.01, 2.0]: LIGHT SPAN: straight north (timed)
- `route_arrow_bridge` at [6.0, 0, -12.0] size [1.4, 0.01, 2.0]: ICE BRIDGE: north along the railed crossing

## Concept prompt
First-person VR view at eye height from a mini golf tee at night on a summit island: two glowing crystal piers reach out over an open-sky gap high above the lilac clouds and are joined by a shimmering green-and-violet aurora ribbon bridge that pours down from the sky; to the right a railed ice bridge; a green with a red flag beyond. Style: stylised 3D storybook render matching the Aurora Archipelago menu card: floating snow-capped slate-violet rock islands over a soft lilac cloud sea at night, thick rounded moonlit snow, translucent glowing glacier-cyan ice and crystal clusters, warm brass lanterns on chunky snow-capped timber posts, snowy blue-green pines, bright green felt with a white ball and a red flag, green and violet aurora ribbons across a starry indigo sky, the Starfrost Spire glowing on the skyline, soft bloom, cosy and whimsical, chunky Roblox-friendly shapes, no text, no UI.
