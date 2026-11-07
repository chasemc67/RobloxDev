# CHANGELOG

## R3.1, tiny final base polish (2026-11-07)
Input `inputs/pirate_thumbnail_round3.blend` @7c3b54b (sha256 `308623f2…249085`, unchanged). Output `pirate_thumbnail_round3_1.blend` (sha256 `9f60c84e…8956f`).

- **Green:** `RO3_RenderOnly_PuttingGreen` changed in vertex Z only, with X/Y and footprint identical.
  - Turf dropped 0.12.
  - Rolled rim crest reduced from +0.55 to +0.09 over the turf plane.
  - Dark skirt foot sunk 0.03 into the sand under each boundary vertex.
  - Lip (crest above sand) changed from mean 1.27 / max 1.70 to mean 0.69 / max 1.12 studs.
  - Exposed skirt changed from mean 1.01 / max 1.42 to mean 0.61 / max 1.02 studs.
- **Cup, pole and ball:** z −0.12 only, so the cup is aligned and the ball sits on the turf.
- **Flag cloth:** yawed +36° about the pole axis (plus the −0.12 drop).
  - The tip moved −65.7 px horizontally at 1920 and is now clear of the right rock edge.
  - The cloth stays below the face.
- **Unused image:** `KIT_v22_palette_mat_palette.png` (0 users) kept via a fake user so the save doesn't drop it.
- **Previews:** one 1920x1080 render (CPU, 128 spp, denoise), plus 1280x720, 320x180 and 160x90 downsamples, with grayscale copies at all four sizes.
- **Unchanged:** camera, ship and the rest of the staging. The validator found no other diffs.
- **Caveats:** a residual dark skirt shows on the side where the sand falls away, and the flag's projected red area is about half of R3's (see README).
