# Portal surface textures (Boardwalk lobby)
These are for the 10×12 `bw_portal_surface_<course>` panels in `../portals-spec.md`. All of them are procedural (PIL + numpy, `_build.py`, cost $0). The swirl textures tile perfectly because they're built from periodic noise on a torus, so they scroll in any direction with no seam. The preview tiles each one 2×2 as a seam check: `preview_sheet.jpg`.

| file | size | use |
|---|---|---|
| portal_lantern_grove.png | 1024² RGB | amber/gold swirl (#C9473A → #E58A3A → #FFC867 → cream cores) |
| portal_sugarloaf.png | 1024² RGB | pink/peach sunset swirl (#D9714A, #F6A6C8, #F2C9A0) |
| portal_aurora.png | 1024² RGB | aurora ribbons, horizontal-ish bands (#4A2C9B, #9B6BFF, #2FB3A0, #5BE3A0) |
| portal_rim_glow.png | 512² RGBA | faint warm-white rounded-rect rim glow, alpha max ≈ 0.43, transparent center |

## Suggested Studio setup
- Panel: a Part (Material SmoothPlastic, or Neon for extra bloom) with two stacked `Texture` instances on the front face using the same image. StudsPerTileU/V = 10 for layer 1 and 6 for layer 2, so they move against each other.
- Scroll with OffsetStudsU/V in a RenderStepped loop:
  - Lantern Grove: layer 1 V +0.6 studs/s, layer 2 U −0.35 studs/s (a slow warm churn).
  - Sugarloaf: layer 1 U +0.45, layer 2 V −0.3.
  - Aurora: layer 1 U +0.8 (the ribbons drift sideways), layer 2 U −0.25 and V +0.15.
- "Rotate": tiled Textures can't rotate in Roblox, so to get a spin, put a `SurfaceGui` + `ImageLabel` on the face (Size 1.6×1.6 scale, centered, ClipsDescendants on the Frame) and tween its Rotation at ~6°/s (Aurora: no rotation, scroll only).
- Transparency: layer 1 at 0.15, layer 2 at 0.55. When `coming_soon`, set both layers +0.35 and halve the scroll speed for a dim idle state. With `SurfaceGui.LightInfluence = 0` and Brightness 1.5–2, the cores read as glowing without needing a light.
- Rim: `portal_rim_glow.png` on a SurfaceGui ImageLabel (or Decal) sized to the 10×12 opening, slightly in front of the panel (0.05 studs), with ImageTransparency 0.2 and ImageColor3 tinted per course (Lantern #FFC867, Sugarloaf #F6A6C8, Aurora #9FE6F2). It pulses: transparency 0.2↔0.45 at 0.5 Hz.
- On a teleport trigger, flash the rim to transparency 0 and double the scroll for 0.4 s, in sync with the fade.
