# Pirate thumbnail R3.1: tiny final base polish

This is a render-only polish of the R3 lead (`Thumbnail_B_Lead_R3`). It makes two asset corrections and nothing else. There is no new composition, camera, ship, variant or text. **The full-res image is not Art approved yet. Keep the previews uncommitted.**

## Files
| file | sha256 |
|---|---|
| input `inputs/pirate_thumbnail_round3.blend` (@7c3b54b), before and after | `308623f2bae9139693273b487f7013da04db707985e2618040140f614f249085` (unchanged) |
| `pirate_thumbnail_round3_1.blend` (compressed, all 3 file images packed) | `9f60c84e005495dd34eb20ee83bb26da610bbfddf256275bd5ed9c8da3b8956f` |
| `previews/B_round3_1_1920x1080.png` (the one render: Cycles CPU, 128 spp, denoise) | `0a3639e54a7b59dab9e5499c14ff301fb4108fe804234bb95b3a5a9c7f0c302a` |
| `previews/B_round3_1_{1280x720,320x180,160x90}.png` and `_gray` for all four sizes (Lanczos downsamples of the same image, ITU-R 601 luma) | see `manifest.json` |

Scripts in `src/`, all taking `--source` and `--output`:
- `polish_round3_1.py`
- `render_round3_1.py`
- `make_downsamples_r3_1.py`
- `validate_round3_1.py`
- `rebuild_round3_1.ps1` runs the whole chain.
- `run_detached.ps1` is the schtasks helper.

Logs and debug output are in `logs/`:
- the polish report
- the flag-yaw probe sheets
- the ray-cast ID maps of the flag region
- the visual-check crop

## Exact changes (only these; the validator diffs every object, material, light, world, camera, image and scene setting)
### 1. `RO3_RenderOnly_PuttingGreen`: vertex Z only, 181/181 verts
- **X/Y are identical**, so the footprint is unchanged (max |dxy| = 0.0).
- Topology and materials are unchanged.
- Z changes range from -0.878 to +0.587. The positive ones are buried skirt-toe verts that follow the sand.

New profile per ring:

| ring | R3 | R3.1 |
|---|---|---|
| turf 0.80 and centre | | old planar turf −0.12 (planar shape kept) |
| rim 0.90 | | turf plane +0.06 |
| rim crest 0.955 | turf plane +0.55 | **turf plane +0.09** |
| rim shoulder 1.0 | turf plane +0.30 | turf plane +0.02 |
| skirt 1.03 | | **sand under each vertex −0.03** (per-vertex ray-cast onto the uneven sand) |
| skirt toe 1.055 | | sand −0.40 |

Lip height in studs, before → after (min / mean / max over the 30 boundary points):

| measure | before | after |
|---|---|---|
| rim crest above sand at skirt foot | 0.79 / 1.27 / 1.70 | **0.21 / 0.69 / 1.12** |
| exposed dark skirt (shoulder → sand) | 0.53 / 1.01 / 1.42 | **0.13 / 0.61 / 1.02** |
| rim crest above local turf plane | 0.55 | **0.09** |
| turf edge above sand | 0.29 / 0.74 / 1.11 | 0.17 / 0.62 / 0.99 |

### 2. Cup, pole and ball follow the turf
- `RO3_RenderOnly_Cup`, `RO3_RenderOnly_FlagPole` and `RO3_RenderOnly_GolfBall`: location Z −0.12 only, x/y unchanged.
- The cup stays at x/y (229.666, −77.437) and the pole stays centred in it.

### 3. `RO3_RenderOnly_FlagCloth`
- Same mesh (36 verts), rotated **+36° about the pole axis**, plus the −0.12 drop. The pole is not moved.
- The tip moved from (232.85, −71.53, 11.56) to (228.78, −70.79, 11.44). On screen that is u 0.9258 → 0.8915, which is **−65.7 px at 1920** horizontally and −0.7 px vertically.
- The tip is now clear of the right rock edge by about 10 px at 1920.
- The cloth stays below the face, with a vertical gap of 0.051 of frame height.

### Other datablock changes
- An ID property `RENDER_ONLY_round3_1` was added on the 5 golf objects.
- `KIT_v22_palette_mat_palette.png` (0 users in R3) was given a fake user so the save keeps it. It is packed. Without this, Blender silently dropped it.

## Validation (`manifest.json` → `checks`, all OK)
- Source sha is unchanged.
- Only the documented golf diffs exist. All ship meshes, materials and transforms, the lights, world and scenes are identical.
- Camera is exactly R3:
  - lens 25, horizontal sensor 36, shift 0
  - clip 0.5–30000, frame 1
  - same basis and evaluated matrix
  - the .blend keeps the R3 render settings of 1280x720 at 64 spp; 1920x1080 at 128 spp is set at render time only
- Green x/y footprint is unchanged.
- Cup, pole and ball moved in z only.
- All images are packed.
- The flag is below the face.
- The green is in frame.
- All 8 preview sizes are correct.

## Caveats (not redesigned)
- **Uneven sand.** The turf top stays planar. It could only drop 0.12 before interior sand (min clearance 0.226) would poke through. On the camera-facing side, where the sand falls away, a dark skirt band of up to ~1.0 stud is still visible (it was 1.4). It is much thinner than R3 but not zero. Removing it fully needs a tilted or reshaped turf or a sand mound, which is a redesign.
- **Flag.** A "tiny" yaw was not enough:
  - Negative yaw (toward the camera) barely moves the tip; it saturates on the rock top.
  - +10° to +30° slides the tip along the rock's diagonal edge, which is still tangent.
  - The first clean gap is at about +34° to +37°.
  - At +36° the cloth is more foreshortened, so its projected red area is about half of R3's. Please re-check the 160x90 golf cue.
- The whole sequence was one render and one visual check, with no extra rounds.
