# Boardwalk lobby dressing options (Lobby C)
These options dress the existing `../boardwalk/lobby.json` layout (220×150 studs). The arches, the course board and the spawn stay where they are, and the portals follow `../portals-spec.md`. The palette and budget rules come from `../boardwalk/props.md`: ≤120k tris for the lobby, ≤20k per mesh, the shared 1024² atlas, Neon emissive, and ≤8 PointLights. The centerpiece goes in the open plaza between the spawn (~100,0,100) and the board, and it must stay ≥8 studs from every path.
Images: `X_hero.png` (VR eye height from the spawn), `X_map.png` (top-down dressing map), and `options_sheet.jpg` (all of them side by side). Generation cost: $0.27.

## A. Lighthouse Festival (golden-hour sunset)
**Pitch:** a candy-striped lighthouse with a golf-ball lantern room anchors a harbour festival strung with bunting and lights.
- Centerpiece: lighthouse 14 Ø × 45 H, red/cream stripes (#E2574C / #F6EBD8), golf-ball lantern room (Neon #FFC867) and a rotating beam (Beam, 0.1 rev/s). ≤15k tris. The beam is a separate mesh.
- Clusters: moored rowboats ×3 (bobbing), buoys ×6, a net + crate + barrel pile ×3, a lobster-pot stack, a festival bench ring around the lighthouse base, flower planters.
- Ambient: gulls circling the lighthouse (3, on a looped path), bunting radiating from the lighthouse to 6 lantern posts, string lights, a waving pennant on top, sea shimmer.
- Leaderboard: a harbour signboard 14×10, brass frame, flip-number tiles (SurfaceGui), and a bunting crown.

## B. Golf-Ball Fountain Carnival (blue-hour dusk)
**Pitch:** a giant spinning golf ball rides a fountain plume in the middle of a pocket-sized seaside carnival.
- Centerpiece: a fountain basin 24 Ø with a 6 Ø golf ball that spins and bobs on a water column (ParticleEmitter + Beam jets), and an underwater glow ring (Neon #9FE6F2). ≤12k tris.
- Clusters: a mini carousel 16 Ø with golf-ball "mounts" (rotates at 0.05 rev/s, ≤12k), 4 striped tents (#E2574C / #F6EBD8), popcorn and candy carts ×2, a balloon bunch ×3, and an optional small Ferris wheel in the backdrop (low-poly, ≤5k).
- Ambient: rotating carousel, fountain spray, bobbing balloons, pennant flags, chasing bulb lights (Neon tween).
- Leaderboard: a carnival marquee 16×10 with a chasing bulb border, a red/cream striped header, and a SurfaceGui score panel.

## C. Hot-Air Balloon Dock (bright late morning)
**Pitch:** three tethered patchwork balloons, one per course, bob above a wooden dock tower like a launch pad to each world.
- Centerpiece: a dock tower 12×30×12 with 3 tethered balloons (Lantern orange #E58A3A, Sugarloaf pink stripes #D9714A / #F0C9A0, Aurora violet #7B5BD6), each 10 Ø, bobbing ±1 stud and swaying, ropes #CDB38A. ≤18k total.
- Clusters: coin telescopes ×3 facing the sea, picnic blankets + baskets, kite stands, canvas sun-sails, wind-chime posts, flower planters, a rope-and-crate loading area by the tower.
- Ambient: drifting kites, flapping sails, wind chimes (sound), gulls, slow-moving clouds.
- Leaderboard: a wooden scoreboard tower 10×16 with a mini balloon on top and parchment banner panels (SurfaceGui).

## Shared fixes for all options
- Replace the broken leaderboard with the board styled for the chosen option. Its SurfaceGui is RobloxDevBot's.
- Dress the bare arches as described in `../portals-spec.md`.
- Each option adds roughly 45–60k tris, which fits within the 120k limit on top of the current 48.7k.
