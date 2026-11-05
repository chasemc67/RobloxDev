# Hole 11: Floodgate Lock (Par 3)

Zone: **Sugarloaf Dam**. Gimmick: **Ball elevator: a canal-lock platform lifts the ball 4 studs and comes back down; roll in while the lock gate is down**.
Layout: `h11-layout.png`. Geometry: `holes.json` -> holes[10]. World placement (from `world/world.json`): origin [150.0, 116.0, -252.0], yaw 0.0.
Tee [0, 0, 0], cup [0.0, 4.0, -43.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A canal **lock** of peppermint concrete with brass winches, a lock-keeper's hut and a red/green signal lamp lifts the ball 4 studs onto the quay.

## Gimmick
Ball elevator: a canal-lock platform lifts the ball 4 studs and comes back down; roll in while the lock gate is down.

## Intended shots
Roll onto the moving lock deck while the entry gate is down. The deck carries its own felt and collision, rises to the quay, and releases the ball during the fully raised interval. The level top dwell lasts 2 s. The widened 11-stud return lane and 15-stud-long broad approach provide room for blocked-shot re-putts. The striped quay lip opens 0.1 s before top arrival and closes 0.1 s after descent starts (exact windows below). Then putt to the cup.

## Hole-in-one line
Brute-force search from the tee found ace lines (76 grid shots). The most robust: aim **266.5°** (atan2(dz,dx): direction (-0.06, -1.00) in x/z, i.e. 3.5° left of straight -Z), speed **19.8 studs/s** (100% power), start phase t=0.0s of the moving parts. The red dashed line on the layout PNG traces it.

## Challenge
Timing the gate (the green lamp is the cue) and choosing the entry pace, which sets the exit roll.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- **lock_gate** (slide): pivot [0, 0.0, -21.25], axis [0, 1, 0], speed 4.333333333333334 studs/s, ping-pong -1.3..0.0 studs with pauses 5.5 s at -1.3, 4.6 s at 0, phase -1.3, cycle 10.70 s. Blockers (relative to pivot at angle/offset 0): box [3.6, 1.2, 0.5] at [0, 0.6, 0]. Visual: Mitre-style lock gate (one leaf, 3.6 wide, 1.2 tall, 0.5 thick) that sinks into a slot in the felt to open (offset -1.3: top 0.1 below the felt) and rises to close (offset 0). It is down while the platform waits at the bottom and up while the platform rides
- **lock_lift_deck** (lift): Moving timber deck carries felt and solid collision; south gate slot ends at z=-21.65; deck stays level throughout rise, top dwell, and descent. Exact moving profile (felt centres hole-local, blocker centres relative to pivot):

```json
{
  "id": "lock_lift_deck",
  "type": "lift",
  "axis": [
    0,
    1,
    0
  ],
  "pivot": [
    0,
    0,
    -25
  ],
  "speed": 4.0,
  "period_s": 10.7,
  "felt": [
    {
      "id": "lock_deck_felt",
      "zone": "lock",
      "center": [
        0,
        0,
        -23.325
      ],
      "size": [
        3.2,
        3.35
      ],
      "yaw": 0,
      "slope": null,
      "thickness": 0.15,
      "edge_support": true
    }
  ],
  "blockers": [
    {
      "center": [
        0,
        -0.075,
        1.675
      ],
      "size": [
        3.2,
        0.15,
        3.35
      ],
      "yaw": 0
    }
  ],
  "schedule": {
    "rise": [
      6.1,
      7.1
    ],
    "release": [
      7.1,
      9.1
    ],
    "return_": [
      9.1,
      10.1
    ],
    "height": 4,
    "tilt_deg": 0
  },
  "visual": "Moving timber deck carries felt and solid collision; south gate slot ends at z=-21.65; deck stays level throughout rise, top dwell, and descent."
}
```

- **quay_lip** (quay_lip): Visible red/cream striped moving lip: top y=5 (same as quay rail20); sinks to top y=4 during interval [7.0, 9.2], surrounding the level top dwell [7.1,9.1]. Exact moving profile (felt centres hole-local, blocker centres relative to pivot):

```json
{
  "id": "quay_lip",
  "type": "quay_lip",
  "axis": [
    0,
    1,
    0
  ],
  "pivot": [
    0,
    4.25,
    -25.45
  ],
  "speed": 10,
  "period_s": 10.7,
  "blockers": [
    {
      "center": [
        0,
        0,
        0
      ],
      "size": [
        3.6,
        1.5,
        0.2
      ],
      "yaw": 0
    }
  ],
  "felt": [
    {
      "id": "lip_top",
      "zone": "quay",
      "center": [
        0,
        5,
        -25.45
      ],
      "size": [
        3.6,
        0.2
      ],
      "yaw": 0,
      "slope": null,
      "thickness": 1.5,
      "edge_support": true
    }
  ],
  "visual": "Visible red/cream striped moving lip: top y=5 (same as quay rail20); sinks to top y=4 during interval [7.0, 9.2], surrounding the level top dwell [7.1,9.1].",
  "schedule": {
    "flush": [
      7.0,
      9.2
    ]
  },
  "interlock": "flush from 0.1s before reaching top until 0.1s after descent starts",
  "clearance": 0.15,
  "appearance": {
    "pattern": "alternating_bands",
    "colors": [
      "#B83A35",
      "#FFF0C9"
    ],
    "axis": "x",
    "band_width": 0.6
  }
}
```

- **lift lock_lift**: rectangle centre [0.0, 0.0, -23.0] +- [1.9, 2.08] -> exit [0.0, 4.0, -27.0] dir [0.0, -1.0], exit speed = clamp(in x 0.5, 1.5, 7.0) studs/s. Lock chamber floor = lift platform: a ball that rolls onto it (past the sunken gate) is lifted to the quay and pushed out by the sluice rush (exit speed scales with the entry speed) Ride: while the gate is up: rise 4.0 at 4 studs/s (1 s), stay level for 2s and push the ball onto the quay at (0, 4, -27) heading -Z at clamp(entry speed x 0.5, 1.5, 7) studs/s, then drop back (1 s) before the gate sinks again (platform: lock_lift_deck carries its own felt and solid collision; no static lock felt; lock cycle 10.7 s).

**Required engine retention contract:** Retain any ball crossing the gate north face onto or above the deck, including elevated gate-top riders during initial rise; the enclosed chamber catches the drop, then releases at the scheduled quay exit. Late gate-top riders below a raised deck are held on the gate sill until the deck returns and take the NEXT ride. This gate-sill retention is an explicit transport abstraction that the engine implementation must reproduce.

```json
{
  "when": "gate-top rider north crossing below raised deck",
  "x_clamp": [
    -1.72,
    1.72
  ],
  "y": 1.2,
  "z": -21.49,
  "velocity": [
    0,
    0,
    0
  ],
  "hold_until_phase": 10.1,
  "next_release_phase": 7.1,
  "engine_requirement": "Physical or scripted retainer must clamp the rider on the gate top until the deck returns, then retain on deck for next ride."
}
```
The Python lift advances to scheduled release; passive geometry alone is not certified without this retainer.


## Timing check (`tools/timing_check.py`, 96 phases; actual fuzz counts per line)
- lock_gate [intended] tee shot into the lock chamber over the sunken gate: blocked 46/96 (46 stops + 0 kicks), deflected 1, **Studio estimate 47.9%** (stops + 0.36 kicks), passed 51%, traps 0, fuzz 100000 shots: timeouts 0, pinned rests 0, escapes 0, excluded rests 0
- lock_gate [ace] brute-force ace line: blocked 46/96 (46 stops + 0 kicks), deflected 0, **Studio estimate 47.9%** (stops + 0.36 kicks), passed 52.1%, traps 0

### collision_cuts (exact hole-local studs)

```json
[
  {
    "mover": "lock_gate",
    "targets": [
      "rail4",
      "rail5",
      "rail7",
      "rail8",
      "approach"
    ],
    "min": [
      -1.95,
      -1.45,
      -21.65
    ],
    "max": [
      1.95,
      1.35,
      -20.85
    ],
    "clearance": 0.15
  },
  {
    "mover": "lock_lift_deck",
    "targets": [
      "rail4",
      "rail5",
      "rail6",
      "rail7",
      "rail8",
      "quay_rail20",
      "quay",
      "approach"
    ],
    "min": [
      -1.75,
      -0.3,
      -25.15
    ],
    "max": [
      1.75,
      4.43,
      -20.85
    ],
    "clearance": 0.15
  },
  {
    "mover": "quay_lip",
    "targets": [
      "quay_rail20"
    ],
    "min": [
      -1.95,
      3.35,
      -25.15
    ],
    "max": [
      1.95,
      5.15,
      -24.35
    ],
    "clearance": 0.15
  },
  {
    "mover": "quay_lip",
    "targets": [
      "quay",
      "rail4",
      "rail5",
      "rail6",
      "rail7",
      "rail8"
    ],
    "min": [
      -1.95,
      2.35,
      -25.7
    ],
    "max": [
      1.95,
      5.15,
      -25.2
    ],
    "clearance": 0.15
  },
  {
    "mover": "quay_lip",
    "targets": [
      "rail5",
      "rail7"
    ],
    "min": [
      -1.95,
      2.35,
      -25.2
    ],
    "max": [
      1.95,
      5.15,
      -25.0
    ],
    "clearance": 0.15
  }
]
```

## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [0.0, 11.5, -43.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +5.02 studs).

## Playtest stats (p8-h11; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 3.07 | 7.0% | 71% | 0.9% | 0 / 0 | [140, 722, 553, 295, 136, 82, 36, 36] |
| average | 3.71 | 0.0% | 54% | 1.3% | 0 / 0 | [0, 330, 747, 481, 224, 109, 60, 49] |

## Props for the 3D modeler (decoration only, sizes in studs)
Moving lock deck with carried felt, slotted gate and relieved static rails, plus an interlocked red/cream striped quay lip. Use the exact mover profiles and collision-cut boxes below; no static felt bridges the moving chamber.

Decoration anchors (position in hole-local studs):
- `cup_flag` at [0.0, 4.0, -43.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `lock_keeper_hut` at [9, 0, -10] (LANDMARK) size [5, 7, 5]: Lock-keeper's hut with a brass winch and a striped barber-pole gauge (outside the east rail)
- `lock_chamber` at [0, 0, -23] size [6.6, 4.6, 2.8]: Peppermint-concrete lock chamber walls (4 tall, up to the quay) with brass bollards; the platform is a timber raft-deck that rides up inside it; approved wall centers x=+-3, z=-23, run 2.8; collision containment reaches y=4.6
- `gate_winches` at [-3.0, 0, -23.0] size [0.8, 2.5, 0.8]: Brass winch posts either side of the lock gate (outside the chamber walls)
- `felt_arrow_lock` at [0.0, 0.0, -18.0] size [1.4, 0.01, 2.0]: Glowing felt arrow decal pointing into the lock (with a little 'wait for the gate' clock icon)
- `gate_light` at [0, 5.0, -25.4] size [0.8, 1.2, 0.4]: Red/green lock signal lamp on the quay face above the chamber: green while the gate is down (visual timing cue)

## Concept prompt
First-person VR view at eye height on a reservoir bench: a felt lane funnels into a small canal lock of red-and-white striped concrete with brass winches and a lock gate; above it a quay and an upper green with a red flag; a lock-keeper's hut with a striped gauge. Style: candy-striped sunset desert canyon, pink and cream banded sandstone, rock-candy crystals, lollipop saguaros, warm golden low sun from the west, lilac haze, chunky whimsical Roblox-friendly shapes, no text.
