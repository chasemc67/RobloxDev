## Pass 8: lantern-lit H9, rail lanterns on the H7 lower tiers and H8, brighter H8 glow (playtest round 2 + Game Art Bot lighting)

Full log: `_src/pass8_summary.md`. Every new PointLight is in **`manifest.lights[]`** (table below), which is separate
from the per-hole `lights[]`. The new lanterns' glow cores are deliberately left out of `dressing.holes.HN.lights[]`, so
no lantern gets two lights.

**New props** (`_src/props_pass8.py`; decoration only, no collision):

| Prop | Tris | Size | What |
|---|---|---|---|
| `lantern_large_hanging` | 384 | 1.4 x 10.7 x 1.35 (x0.85 as placed) | The `lantern_large` paper lantern (same mesh) on an 8.35-stud iron cord with a top ring. The origin is the lantern's bottom centre. |
| `rail_lantern_stake` | 172 | 0.5 x 1.9 x 0.5 | A small paper lantern on an oak stake, under the 2-stud tall-prop line, so it may stand right outside a rail. |
| `rail_lantern_crook` | 220 | 2.4 x 6.5 x 0.6 | An oak post with a crook arm along local +X. The lantern hangs 5.25..6.1 above the base, so it shows over H8's 3.9-tall walls. The post stays >= 3 back from the rail and the arm reaches 2 studs toward it. |

**H9** (holes.json Round 7 final, props.md):
- 3 `lantern_large_hanging` at scale 0.85 (a 1.2 x 1.8 x 1.2 lantern) on the decoration anchors `amber_lantern_1..3`
  over the heart green: (18.5, -47.5), (28.5, -46.5) and (20.0, -51.5).
- Each lantern's bottom is at y 7.2, 8 above the felt; the cord top is at y ~16.
- Each has a PointLight: Range 16, Brightness 3, Color3(255, 169, 87).
- They replace the hero `heart_lantern_cluster`, which is no longer placed (its FBX stays in `fbx/`).

**Rail lanterns:**
- About every 10 studs, outside both rails, on the H7 lower tiers (8 lanterns: 3 stakes, 5 crooks) and the whole of H8
  (15 crooks).
- Each has a PointLight: Range 10, Brightness 1.2, amber.
- Rules:
  - not clipping any rail (exact 2D gap >= 0.25);
  - not over any felt (exact);
  - visible over the rail top;
  - tall-prop and plant rules and the near-field budget all still apply.
- Where water (the H7 stream), a walkway (H7 east) or the H8 junction corner blocks every spot 8-12 studs on, the line
  skips ahead. Fitcheck re-tests every skipped spot.

**H8 glow:**
- Preview emission Firefly 4 -> 8 and ShroomGlow 3 -> 6.
- `manifest.emissive` gives the SurfaceAppearance emissive set-up and the textures `textures/firefly_emissive.png`,
  `shroomglow_emissive.png` and `glow_emissive_mask.png`.
- The firefly_glow spot_lights went from Brightness 2 / Range 12 to 3.5 / 14.
- 12 new soft glow lights in `manifest.lights[]` over the firefly clusters and glow shrooms.

**Checked by** `_src/fitcheck_pass8.py`, with negative tests. It checks:
- hanging height 7..9 above the felt and the corridor / green footprint;
- rail clip, felt, spacing and visibility;
- an amber lights[] entry at every lantern centre;
- the emissive boost.

**Round-7 moving props** (pass-8 addendum; sizes and motion are read from holes.json):
- `h7_floating_log`: 6 long with whittled pointed ends; slides +-6 at 3.5 studs/s with pauses.
- `h8_root_door`: 3.6 long; slides 0..4 at 3 studs/s with pauses. `h8_door_pocket` is now only the south pocket,
  2.05 deep.
- `h9_lantern_pendulum`: a square 1.6 x 1.8 x 1.6 bob turned 30 deg; hinge at y 8.996; swings +-30 deg over 5 s.
- `firefly_ring_entry`: glow disc r 0.45.
