# Pirate Shipwreck: round 1 handoff (Game Art Bot)
Status: round 1 options. Nothing is final until Chase picks a look. Recommended: Look B (Golden Hour Hideaway), fallback A.
All paths are in /workspace/gameart/pirate-shipwreck/r1/. The 3D sheets below are drafts in the Look B palette, so only start final meshes after Chase confirms B (the wreck shape is the same in every look).

## Order of work for 3D Model Bot
1. Wreck: `3d-1-wreck-sheet.png`  (ready now, can be reported on its own)
2. Cave cliff: `3d-2-cave-cliff-sheet.png`
3. Gag props: `3d-3-props-sheet.png` (6 hero props: duck figurehead, backward cannon, coconut casualty, flytrap burp, croc nap, captain's last nap). Dressing props 3, 4, 5, 6, 8, 9, 12 are on `story-gags-sheet.png`, simple kitbash only.
Rules: every mesh under 20k tris, split into parts as listed on the sheets, no copies of any trademarked ship. Pads are never part of an art mesh.

## Route and layout
`map-overhead.png`: 18 pads, one trail. Zones: 1-4 wreck & cove, 5-9 beach, 10-14 jungle, 15-18 cave cliff. Landmarks: wreck mast and cave cliff must be visible from most holes. Three rest-stop clearings have no hole and are for gag props.

## Look B palette and lighting (for RobloxDevBot)
Sheet: `lookB-palette-lighting.png` (swatches with hex and RGB, plus all values). Starting values, tune in a headset:

Lighting: ClockTime 17.7, GeographicLatitude 25, Brightness 2.6, Ambient (95,62,100), OutdoorAmbient (150,105,120), ColorShift_Top (255,165,95), ColorShift_Bottom (120,80,140), EnvironmentDiffuseScale 0.6, EnvironmentSpecularScale 0.5, ShadowSoftness 0.35, ExposureCompensation 0.2.
Atmosphere: Density 0.28, Offset 0.25, Color (255,176,140), Decay (140,90,120), Glare 0.4, Haze 1.4. Keep density low: the skill notes that haze hides fine detail on far scenery, which is fine, but it must never wash out pads.
Post: Bloom (Intensity 0.35, Size 24, Threshold 1.1), ColorCorrection (Saturation 0.1, Contrast 0.08, TintColor 255,240,225), SunRays (Intensity 0.08, Spread 0.6), DepthOfField off for VR comfort.
Sky: sunset skybox or Clouds (Cover 0.35, Density 0.5, Color 255,190,170).

Key colors: sand (226,184,128), dark wood (84,52,34), weathered plank (140,90,55), slate (70,76,92), rock (110,92,120), jungle (30,100,60), leaf (90,170,70), water (30,120,140), sail cream (238,222,190), sail red (196,60,50), duck yellow (245,196,40), lantern amber (255,190,80).

## Pads must stay bright and high-contrast in VR (RobloxDevBot's condition)
- Felt: Color3 (100,230,135), #64E687, SmoothPlastic, Reflectance 0, no texture. A cool mint green that is clearly different in hue from the warm sand and the orange light.
- I measured luminance contrast: felt vs sand is only about 1.1:1 (they have similar brightness, only the hue differs), felt vs dark wood about 7:1, felt vs slate about 4.6:1. So the felt never touches sand. Every pad has a dark rim 3 to 4 studs wide: dark wood (84,52,34) on wreck and beach pads, slate (70,76,92) on jungle and cave pads. Rim vs sand is about 6:1 (wood) and 4.7:1 (slate).
- Keep light things (sand, pale rock, cream sails) at least 6 studs back from the felt edge.
- Soft light per pad when needed: PointLight on a lantern post or hidden in the rim, Range 16, Brightness 1.0, Color (255,245,225), Shadows off. If the felt looks darker than the sand in a headset, raise Brightness to 1.6.
- Never put a pad fully in the shadow of the wreck or cliff. Cup has a dark ring and a tall red flag (235,55,55) on a cream pole, at least 14 studs, visible from the tee.
- Art meshes (rocks, wreck, props) sit beside pads with at least 8 studs of empty space around each pad and never provide a playing surface.

## Look options
A `lookA-sunny-splash-cove.png`, B `lookB-golden-hour-hideaway.png`, C `lookC-thunder-tide-dusk.png`, side by side in `contact-sheet-ABC.png`.
