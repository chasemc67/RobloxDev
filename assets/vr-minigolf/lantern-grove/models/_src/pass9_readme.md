## Pass 9: H9 pendulum base plinth (holes.json Round 9)

Full log: `_src/pass9_summary.md`. Fitcheck: ALL PASS, 218 checks (`_src/fitcheck_pass9_validated.txt`).

**`fbx/h9_lantern_pendulum.fbx`** (re-import; 1,820 tris, 5 MeshParts as before):
- **New base plinth**: a dark-iron weighted block 0.9 x 0.4 x 1.6 (X x Y x Z). It sits at yaw 0 in the course, i.e.
  turned -30 deg relative to the lantern body (which stays at yaw 30). It is centred under the body, and its bottom is
  0.062 below the body's bottom: 7.962 below the hinge, 0.034 above the felt at rest. Its corners stick out up to 0.118
  past the body's faces.
- The plinth is exactly the holes.json collider foot (`moving_parts.lantern_pendulum.blockers[1]`), so the invisible
  foot never stops a ball outside the visible lantern.
- It is merged into the existing **`h9_lantern_pendulum__Iron`** MeshPart, which also holds the hinge pin, so there are
  no new parts to weld. Set it up exactly as before (Iron = `#3B3A3F`, Metal).
- **Pivot = hinge, now Round 8/9 `(21.2, 8.996, -38.5)`** hole-local (pass 8 had x 22.0). Motion is now
  `angle(t) = 13 * sin(360 t / 4 s)` deg about +Z (pass 8 had +-30 / 5 s). Both come straight from holes.json.
- **Clearance:** sampled every 0.001 deg over the full holes.json range [-13, 13]. The plinth's lowest corner clears the
  chamber felt (y 1.0) by at least **0.0213 at +-3.235 deg** (0.034 at rest). The whole mesh has the same minimum.

**`fbx/h9_pendulum_root_beam.fbx`** (re-import): the origin is still the hinge (21.2). The beam, its legs and the side
lanterns are offset +0.8 in X so the beam stays centred on its anchor at x 22. Only the hinge bracket sits at the
origin.
