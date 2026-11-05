# Lantern Grove props: pass 9 summary (2026-10-11): H9 pendulum base plinth

Brief: `_src/brief_pass9.md`. Step log: `_src/pass9_progress.md`. Before: `_src/manifest_before_pass9.json`.
holes.json, world and fly files were only read, never edited. Only PIDs this job started were waited on.

## Result

- **Fitcheck: ALL PASS, 218 checks** against the live Round-9 holes.json (12:02). That is 209 from pass 8 plus 9 new
  pass-9 checks, 4 of them negative tests. Saved as `_src/fitcheck_pass9_validated.txt` (= `_src/fitcheck.txt`).
- **Pivot / hinge: H9 (21.2, 8.996, -38.5)** hole-local, read from holes.json (`moving_parts.lantern_pendulum.pivot`).
  - It matches the brief's expected Round 8/9 value. No discrepancy with holes.json.
  - The pass-8 manifest and FBX were still at the Round-7 hinge x 22.0 and +-30 deg / 5 s. Both now follow holes.json:
    x 21.2 and **angle(t) = 13 sin(360 t / 4 s)** deg about +Z.
- **Plinth**, measured on the re-imported FBX:
  - Dark iron, 0.9 x 0.4 x 1.6 (X x Y x Z), at course yaw 0 = **-30 deg relative to the lantern body** (body yaw 30).
  - Centred under the body (offset < 0.001).
  - Bottom **0.062 below the body bottom**: 7.962 below the hinge, 0.034 above the felt at rest.
  - Corners stick out **0.118** past the body faces (props.md: "up to 0.12").
  - It equals holes.json `blockers[1]` (the collider foot) to within 0.001 on every face.
- **Swings rigidly:** the plinth is part of the `h9_lantern_pendulum__Iron` MeshPart, together with the hinge pin and
  the bob iron. Every part's origin is the hinge (offset 0). At every angle over +-13 deg (0.25-deg steps), the
  transformed plinth corners match the transformed collider-foot corners within 1.3e-6.
- **Felt clearance:**
  - Method: exact plinth geometry (12 tris; 866 surface points including all 8 corners) against the actual felt height
    under each point, using holes.json felt pieces (the flat `chamber` felt, y 1.0; every point is over felt). Sampled
    at **26,001 angles, 0.001-deg steps**, over the **full holes.json motion range [-13, 13]** (amplitude 13, period 4 s).
  - **Min clearance 0.0213 at -3.235 deg** (and symmetrically at +3.235). This is the bottom corner's lowest point,
    matching the analytic 8.996 - hypot(0.45, 7.962) - 1.0 = 0.0213.
  - 0.034 at rest, and 0.0213 for the whole mesh (all FBX vertices, 0.01-deg steps). Required: >= 0.02.
- **Tris:** `h9_lantern_pendulum` 1,828 -> **1,820**. The plinth adds 12; the old 20-tri bottom finial, now hidden inside
  the plinth, was dropped. Every prop is < 20k (max 6,536).

## New fitcheck rules (`_src/fitcheck_pass9.py`, exec'd last by `fitcheck.py`)

1. The plinth (`__Iron` geometry below body bottom + 0.4) is exactly the foot box: inside it within 0.001, reaching
   every face. It is centred under the body, 0.062 below the body bottom (taken from the holes.json blockers).
2. Rigid swing (as above).
3. Clearance >= 0.02 over the full holes.json range at 0.001 deg, against the exact felt.
4. The whole mesh clears >= 0.02.
5. FBX tris < 20k and == manifest.
6. **Negative tests, all flagged:**
   - the plinth 0.01 lower (min 0.0113);
   - the plinth at the body's yaw +30 (0.34 outside the foot);
   - no plinth;
   - the plinth 20 % wider.

**Updated older checks:**
- `fitcheck.py`: the bob is tested against the **union** of the holes.json blockers.
- `fitcheck_pass6.py`: the bob bottom = the lowest blocker bottom (the foot); the swing envelope includes the foot box.

## Side fix: root beam

The beam's origin is the hinge, so it followed the hinge to x 21.2. Its east/west legs then touched a rail (fitcheck
run 1: min rail gap 0.00). props.md / the holes.json anchor `pendulum_beam` keep the beam centred at x 22. So the beam,
legs, side lanterns and moss are now offset +0.8 in X (`_BEAM_DX`, read from the anchor), and only the hinge bracket
stays at the origin. The rerun gives min rail gap 0.37 and min felt gap 0.87, and the swing envelope is clear of the
beam.

## Files

- **FBX:** `fbx/h9_lantern_pendulum.fbx` (rebuilt, 1,820 tris), `fbx/h9_pendulum_root_beam.fbx` (rebuilt, 1,650 tris).
- **Previews:** `previews/h9_lantern_pendulum_eye.png`, `previews/h9_lantern_pendulum_34.png`,
  `previews/h9_pendulum_root_beam_{eye,34}.png`, and `previews/assembly_h09_tee.png` (H9 tee view, 32 spp; the
  pendulum is at the right, beside the beam). `tee_contact_sheet.png` rebuilt.
- **Docs:** `manifest.json` (only the `h9_lantern_pendulum` and `h9_pendulum_root_beam` entries changed: placement,
  motion, fit/notes, bbox, parts) and `README.md` (new "Pass 9" section from `_src/pass9_readme.md`).
- **Code:**
  - `_src/props_moving.py`: plinth from `blockers[1]`;
  - `_src/props_pass6.py`: beam offset;
  - `_src/fitcheck.py`, `_src/fitcheck_pass6.py`, `_src/fitcheck_pass9.py` (new);
  - `_src/make_docs.py`: pass-9 README block and title.
- `lantern_grove_props.blend` was not rebuilt (no full build). Dressing was not re-run: the envelope check passes
  against the existing dressing.

## What RobloxDevBot pulls in

1. **Re-import `fbx/h9_lantern_pendulum.fbx`** (Stud scale, keep hierarchy). It has the same 5 MeshParts as before
   (`__CapGold`, `__Glow`, `__Iron`, `__MoveCream`, `__MoveRed`); the plinth is inside `__Iron` (#3B3A3F, Metal).
   - Decoration only: CanCollide / CanTouch / CanQuery = false. Weld the parts to one another (or set PrimaryPart).
   - Pivot = hinge (21.2, 8.996, -38.5) hole-local.
   - Drive it with `hingeCF * CFrame.fromAxisAngle(Vector3.zAxis, math.rad(13 * math.sin(2*math.pi*t/4)))`, the same
     CFrame as the invisible collider foot and bob blockers. The plinth then covers the foot at every angle.
   - The Glow PointLight is unchanged (Range 14, Brightness 2, #FFB347).
2. **Re-import `fbx/h9_pendulum_root_beam.fbx`**, placed at the hinge (21.2, 8.996, -38.5), yaw 0. The beam itself now
   sits centred at x 22, with the bracket over the hinge.
3. Nothing else changed: no new lights, no dressing changes.

## Open issues

1. **The plinth is a plain sharp-edged iron block.** Any bevel, rivet or trim would either leave a foot corner
   uncovered or poke outside the collider, and clearance is already near the 0.02 floor (0.0213). The block reads fine
   in the previews (dark weighted base under the red lantern).
2. **The H9 pendulum spot light** (`dressing.holes.H9.spot_lights` `H9_lantern_pendulum_moving_part`) is still at
   hole-local (22.0, 9.0, -36.5), positioned from the Round-7 hinge. It is outside the envelope and lights the same
   area. A future `dressing_world.py` run will re-centre it on x 21.2; it was not re-run here, to keep the dressing
   unchanged.
3. The minimum felt clearance of 0.0213 has no margin for an in-engine felt that sits higher than holes.json's y 1.0.
   The collider foot has the same clearance, so the visual can never touch felt that the collider doesn't.
