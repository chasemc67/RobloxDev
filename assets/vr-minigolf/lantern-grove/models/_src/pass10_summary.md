# Lantern Grove props: pass 10 summary (2026-10-11): H9 plinth Round 10 + VR wrist bracer

Brief: `_src/brief_pass10.md`. Step log: `_src/pass10_progress.md`. Before: `_src/manifest_before_pass10.json`.
holes.json, world and fly files were only read, never edited. Only PIDs this job started were waited on.

## Result

- **Fitcheck: ALL PASS, 234 checks** against the live Round-10 holes.json (15:11). That is the 218 pass-9 checks plus 16
  new pass-10 checks, 7 of them negative tests. Saved as `_src/fitcheck_pass10_validated.txt` (= `_src/fitcheck.txt`).
- **No discrepancies.** The brief, props.md, h09-notes.md and holes.json all agree:
  - foot 1.0 x 0.4 x 1.6, yaw 0, centred 7.759 below the hinge;
  - hinge (21.2, 8.996, -38.5), axis +Z;
  - swing 11 deg amplitude, 4 s period, range [-11, 11].

## Job 1: H9 plinth (`fbx/h9_lantern_pendulum.fbx`, 1,820 tris, unchanged count)

- The plinth is built from holes.json `blockers[1]`, so a rebuild picked up the Round 10 size. Measured on the
  re-imported FBX:
  - **1.000 (X, along the swing) x 0.400 x 1.600**, course yaw 0 = **-30 deg relative to the body** (body yaw 30);
  - centred under the body (offset < 0.001), and equal to the collider foot within 0.001 on every face;
  - bottom **0.059 below the body bottom**: 7.959 below the hinge, **0.037 above the felt at rest**;
  - corners stick out **0.143** past the body faces (props.md: "up to 0.14").
- **Pivot = hinge (21.2, 8.996, -38.5)**, the same as holes.json. Every part origin is the hinge. The plinth is in
  `__Iron` with the hinge pin, so it swings rigidly: corner deviation 1.3e-6 over +-11 deg.
- **Motion** (manifest): `angle(t) = 11 * sin(360 t / 4 s)` deg about +Z, range [-11, 11]. It was +-13 deg.
- **Felt clearance**, checked with the exact plinth geometry (866 surface points incl. corners) against the holes.json
  felt:
  - sampled at 22,001 angles, every 0.001 deg over [-11, 11];
  - **min 0.0213 at +-3.595 deg**, matching the analytic 8.996 - hypot(0.5, 7.959) - 1.0;
  - the whole mesh has the same minimum (0.0213);
  - required: >= 0.02.
- **Previews refreshed:** `previews/h9_lantern_pendulum_{eye,34}.png`.
- `h9_pendulum_root_beam` was not rebuilt, because the hinge did not change. `assembly_h09_tee.png` was not
  re-rendered: a 0.1-stud change is not visible from the tee.

**New fitcheck rules** (`_src/fitcheck_pass10.py`, exec'd after `fitcheck_pass9.py`; the pass-9 rules are data-driven
and now run over [-11, 11]):
1. The holes.json foot, hinge and swing equal the Round 10 spec.
2. The FBX plinth measures 1.0 x 0.4 x 1.6 and sits 0.059 below the body.
3. The manifest motion equals holes.json.
4. Clearance sampling covers the full [-11, 11].
5. Negative tests, all flagged:
   - the Round 9 0.9 plinth;
   - the plinth 0.005 lower (0.0163);
   - the manifest left at +-13;
   - the plinth 0.05 off-centre.

## Job 2: `fbx/vr_wrist_bracer.fbx` (new, 978 tris)

- A leather sleeve, 0.46 long, with brass end rings. Two dark straps with brass buckles go under the wrist. On the back
  of the wrist there is a raised leather pad with brass rivets, plus a brass bezel holding the face. A tiny amber Glow gem
  sits on the bezel's finger end.
- **MeshParts:**

  | MeshPart | Tris | Colour | Material |
  |---|---|---|---|
  | `vr_wrist_bracer__Leather` | 212 | `#8A5530` | Leather |
  | `__LeatherDark` | 248 | `#5B3A22` | Leather |
  | `__Brass` | 468 | `#C9973A` | Metal |
  | `__Glow` | 48 | `#FFB347` | Neon |
  | **`WristFace`** | 2 | `#2E2620` | SmoothPlastic |

- **Size:** bbox 0.462 x 0.49 x 0.452. The sleeve's inner radius is 0.177 at the wrist and 0.192 at the elbow, so it
  fits a 0.35 forearm. Outer radius 0.199 / 0.214.
- **Axes (prop-local, Roblox):**
  - **+X points along the forearm toward the fingers.**
  - **+Y points out of the back of the wrist = the WristFace normal.**
  - **+Z = X cross Y** points across the wrist (thumb side on a left arm). The mesh is mirror-symmetric in Z.
- **Pivot = wrist centre** (forearm axis, mid-length). The root and all part origins are at (0, 0, 0).
- **WristFace:**
  - a flat 2-tri quad, **0.32 (X) x 0.20 (Z) studs, aspect 1.6000**;
  - **centre (0, 0.238, 0) from the pivot**, normal +Y;
  - UVs fill 0..1 exactly (U along +X, V along -Z);
  - recessed 0.014 inside the bezel frame, and no geometry covers it.
- **Verified on the re-imported FBX:** WristFace dims, flatness, aspect, centre, normal, and the exact per-corner UVs;
  tris < 2k and equal to the manifest; origins; forearm fit. Negative tests flagged: a face 0.21 deep, a flipped normal,
  and half-filling UVs.
- **Previews:** `previews/vr_wrist_bracer_eye.png` (the player glancing at a turned-up wrist), `_34.png`, and
  `_face.png`. The face view is face-on with a UV test card: red top-left, green top-right, blue bottom-left, arrow =
  +U toward the fingers. The card is preview only; the FBX material is flat.
- **Docs and sheet:** the bracer is in `contact_sheet.png` (rebuilt). Its manifest entry has a `vr_attach` block with
  the axes, sleeve, wrist_face size, offset, normal, UVs and SurfaceGui notes.

## Code changed

- `_src/props_pass10.py` (new).
- `registry.py`: `extra=` / `previews_fn=` on `@prop`.
- `build_all.py`: imports props_pass10, renamed-part material lookup, custom preview views.
- `lglib.py`: Leather, LeatherDark, Brass and WristFace materials; `box_uv_objects` skips `lg_keep_uv`.
- `fitcheck.py`: exec's pass 10.
- `fitcheck_pass9.py`: header text only.
- `fitcheck_pass10.py` (new).
- `props_moving.py`: comment and Round-10 label text.
- `make_docs.py`: pass-10 README block and title.
- `pass10_readme.md`.

## What RobloxDevBot pulls in

1. **Re-import `fbx/h9_lantern_pendulum.fbx`** with the same setup as pass 9:
   - same 5 MeshParts; the plinth is in `__Iron`;
   - pivot = hinge (21.2, 8.996, -38.5);
   - drive it with `hingeCF * CFrame.fromAxisAngle(Vector3.zAxis, math.rad(11 * math.sin(2*math.pi*t/4)))`, the same
     CFrame as the collider foot and bob.
2. **Import `fbx/vr_wrist_bracer.fbx`** (new):
   - weld it to the off-hand: +X toward the fingers, +Y out of the back of the wrist, pivot at the wrist centre;
   - CanCollide / CanTouch / CanQuery false, Massless;
   - put a SurfaceGui on `WristFace`, Face = Top, canvas 0.32 x 0.20 (e.g. 800 x 500 FixedSize).
3. Nothing else changed: no world, dressing or light changes.

## Open issues

1. **SurfaceGui up direction:** for Face = Top, the GUI width runs along +X. GUI up is expected to be -Z (the same as the
   UV V direction), but it was not confirmed in Studio. If the GUI reads upside down, rotate its content 180 deg.
2. **The H9 plinth clearance is 0.0213,** with no margin if the in-engine felt sits above y 1.0. The collider foot has the
   same clearance.
3. **The H9 pendulum spot light is still at x 22.0** (carried over from pass 9). It is unchanged.

## Pass 10b (Round 5): bracer face resized to 0.37 x 0.28

WristFace is now 0.37 x 0.28 (ratio 1.321, for the approved 1024x784 card), centre still (0, 0.238, 0), normal +Y, UVs
0-1 (U +X, V -Z). Brass bezel widened to 0.414 x 0.324 outer, leather pad 0.45 x 0.34. Straps, end rings and sleeve
(fits a 0.35 forearm, inner radius 0.177) unchanged. 978 tris, same 5 MeshParts. Fitcheck ALL PASS (235). Built on the
Windows PC. Previous FBX/previews: `_src/pass10b_old/`.
