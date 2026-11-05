## Pass 10: H9 plinth resized to Round 10, and a new VR wrist bracer

Full log: `_src/pass10_summary.md`. Fitcheck: ALL PASS, 234 checks (`_src/fitcheck_pass10_validated.txt`).

**`fbx/h9_lantern_pendulum.fbx`** (re-import; 1,820 tris, same 5 MeshParts):
- **The plinth is now 1.0 x 0.4 x 1.6** (X along the swing x Y x Z; it was 0.9 long in pass 9). It is the holes.json
  Round 10 collider foot (`blockers[1]`).
  - Yaw 0 in the course, which is -30 deg relative to the lantern body.
  - Centred under the body. Bottom 0.059 below the body's bottom, which is 7.959 below the hinge and 0.037 above the felt
    at rest.
  - Corners stick out up to 0.143 past the body's faces.
  - It is still part of `h9_lantern_pendulum__Iron`.
- **Pivot = hinge (21.2, 8.996, -38.5)**, the same as holes.json.
- **The swing is now `angle(t) = 11 * sin(360 t / 4 s)` deg about +Z** (it was +-13 deg).
- **Clearance:** sampled every 0.001 deg over [-11, 11]. The plinth's lowest corner clears the felt by at least
  **0.0213 at +-3.595 deg**, and the whole mesh has the same minimum.

**`fbx/vr_wrist_bracer.fbx`** (new; 978 tris, decoration only): a leather-and-brass bracer for the VR off-hand forearm
(~0.35 stud diameter).
- **MeshParts:**
  - `vr_wrist_bracer__Leather`: `#8A5530`, Leather;
  - `__LeatherDark` (straps): `#5B3A22`, Leather;
  - `__Brass` (end rings, bezel, buckles, rivets): `#C9973A`, Metal;
  - `__Glow`: a tiny amber gem, `#FFB347`, Neon;
  - **`WristFace`**: `#2E2620`, SmoothPlastic.
- **Axes (prop-local, Roblox):**
  - **+X points along the forearm toward the fingers.**
  - **+Y points out of the back of the wrist.** This is the WristFace normal, toward the viewer's face when the wrist is
    turned up.
  - **+Z = X cross Y** points across the wrist (thumb side on a left arm). The mesh is mirror-symmetric in Z, so it fits
    either arm.
- **Pivot = wrist centre:** on the forearm axis, at the bracer's mid-length. The FBX root and every part origin are at
  (0, 0, 0).
- **Sleeve:** 0.46 long (x -0.23..0.23). Outer radius 0.214 at the elbow end and 0.199 at the wrist end; inner radius
  0.192 / 0.177.
- **`WristFace`:**
  - A flat quad (2 tris), exactly **0.32 x 0.20 studs (16:10)**: 0.32 along +X, 0.20 along Z.
  - **Centre (0, 0.238, 0) from the pivot**, normal **+Y**.
  - UVs fill 0..1 exactly: U runs along +X (toward the fingers), V along -Z.
  - A brass bezel frame rises 0.014 around its edges.
- **SurfaceGui:** put it on `WristFace` with Face = Top (the +Y face). The canvas is 0.32 x 0.20 studs, e.g. FixedSize
  800 x 500.
  - The GUI's width runs along +X. GUI up should be -Z, matching the UV V direction.
  - Confirm the up direction in Studio once. If the text reads upside down, rotate the content 180 deg.
- **Setup:** CanCollide / CanTouch / CanQuery false, Massless true. Weld it to the off-hand with an offset back up the
  wrist.
- **Previews:** `previews/vr_wrist_bracer_eye.png` (glancing at a turned-up wrist), `_34.png`, and `_face.png`. The face
  view shows a UV test card on WristFace: red = GUI top-left, green = top-right, blue = bottom-left, arrow = +U. The card
  is in the preview only.
