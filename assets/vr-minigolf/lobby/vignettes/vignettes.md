# Lobby backdrop vignettes (one zone per course)
**Brief (revised by Chase):** far BACKDROP zones in the open space beyond the lobby floor, behind the row of portals (north of z≈32, past the beach), seen from a distance. No collision, and about 15k tris per zone. Use big simple shapes plus a few hero pieces, with no detail smaller than ~2 studs. Keep them consistent with lobby option A, the Lighthouse Festival (sunset harbor). Each zone is roughly centered behind its own arch (x 45 / 110 / 175) but can spread wide and tall, because it's scenery, not a set piece.
Images: `LG1–3.png`, `SL1–3.png`, `AU1–3.png` are the final views from the boardwalk looking past the portals (they use `../options/A_hero.png` as the reference). The sheet is `vignettes_sheet.jpg`. Superseded passes are in `pass1/` (scene inside the opening) and `pass2/` (a small diorama right behind each arch).
The triangle counts below are rough estimates, assuming vertex color plus the shared atlas, Neon for glow, and decimated far shapes.

## Lantern Grove
- **LG1 Lantern hill**: a broad hill of giant rounded autumn trees strung with big lanterns. Props: hill base 1.5k, 6 tree blobs (trunk + 2–3 canopy blobs) ×1.2k, 12 giant lanterns (Neon) ×150, a lantern string. **≈11k**
- **LG2 Colossal lantern tree** ⭐ *recommended*: one landmark tree with a huge glowing canopy, which reads instantly from the spawn and echoes the Lighthouse as a second vertical. Props: trunk + roots 3k, canopy 4 blobs 5k, 6 giant hanging lanterns 1k, a small island base 1.5k, 2 filler trees 2.5k. **≈13k**
- **LG3 Forest ridge + pagoda gate + waterfall**: three layered ridges, a lantern-lit gate and a waterfall. Props: 3 ridge cards 3k, gate 3k, a waterfall ribbon (scrolling texture) 0.5k, 8 tree blobs 6k. **≈13k**

## Sugarloaf Canyon
- **SL1 Mesas + gondola** ⭐ *recommended*: tall striped mesas with a red gondola on a long cable and a pink waterfall. It matches Chase's starting idea, and the moving gondola gives ambient motion. Props: 4 banded mesas 6k, gondola cabin 1.2k (tweens along the cable), cable + 2 pylons 0.8k, a waterfall ribbon 0.5k, 3 crystal clusters 1.5k, 2 lollipop saguaros 1.5k. **≈12k**
- **SL2 Candy dome range**: a low mesa range with a giant striped dome, a rope bridge and huge rock-candy crystals. Props: range 5k, dome 2k, bridge 1.5k, 5 crystals 2.5k. **≈11k**
- **SL3 Peppermint dam**: a giant dam with a spillway waterfall, gondola cables and banded cliffs. Props: dam 3k, cliffs 5k, spillway + 2 falls ribbons 1k, cables + cabin 2k. **≈11k**

## Aurora Archipelago
- **AU1 Ice floes + crystal spires under aurora**: dark water, floes and purple spires, with an aurora ribbon (a Beam with a scrolling texture) in the dusk sky. Props: 10 floes 2k, 7 spires 4k, aurora beams 0.2k, 2 snowpuffs 2k. **≈9k**
- **AU2 Floating islands** ⭐ *recommended*: three snow-capped islands floating over mist with frozen falls. It's the clearest silhouette at sunset, it's on-brand for the course, and the islands can bob slowly. Props: 3 islands 7.5k, 2 frozen-fall ribbons 0.5k, 6 crystal clusters 3k, a mist card 0.1k. **≈11k**
- **AU3 Giant crystal spire + ice bridge**: one huge spire on an ice shelf, a translucent bridge and a floating island. Props: spire 4k, shelf 2.5k, bridge 1k, island 3k, crystals 2k. **≈12.5k**

## Picks
Use **LG2, SL1 and AU2**. They give three distinct silhouettes (one tall tree, flat-topped mesas, floating islands), each has one ambient motion (the glowing lanterns, the gondola, the bobbing islands), and they leave the Lighthouse as the only tall striped vertical. They won't clash with options B or C, because the zones sit far back over the beach and sea.

## Notes for 3D Model Bot
- Set CanCollide/CanQuery/CanTouch to false on everything. Use one mesh per hero piece, merge the far fillers, and keep each zone ≤15k.
- Scale: zones are about 60–100 wide and 30–70 tall, placed 60–150 studs north of the arches. Tops above about 30 studs can use fog-tinted vertex colors (#F2A57E haze).

# Portal surfaces
`../portal_surfaces/portal_surface_{lantern_grove,sugarloaf,aurora}.png` are 1000×1200 opaque RGB, with the course name baked in (Lilita One on a dark rounded plate in the top quarter) and course key art below. They go under the scroll and pulse layers from `../portal_textures/`. Raw art is in `../portal_surfaces/_raw/`, and the preview is `portal_surfaces_preview.jpg`.
