# Boardwalk lobby course portals: spec for 3D Model Bot

These upgrade the three decorative arches in the Golden Hour Boardwalk (Lobby C) into real teleport portals for the place split.
Sources: `boardwalk/lobby.json` (`portals[]`), `boardwalk/props.md` (#8–12, palette), and the pass-1 arches in `boardwalk/models/fbx/bw_arch_*.fbx`.
Concepts: `portal_lantern_grove.png`, `portal_sugarloaf_canyon.png`, `portal_aurora_archipelago.png` (sheet: `portals_sheet.jpg`).
Units are studs. Axes follow lobby.json: X east, Y up, Z south, deck top Y=0, yaw 0 faces north (-Z). The front faces south toward the spawn.

## Placement (from lobby.json, unchanged)
| id | position (center, base) | yaw | courseId | state today |
|---|---|---|---|---|
| arch_lantern_grove | (45, 0, 32) | 0 | lantern_grove | live |
| arch_sugarloaf_canyon | (110, 0, 32) | 0 | sugarloaf_canyon | coming_soon |
| arch_aurora_archipelago | (175, 0, 32) | 0 | aurora_archipelago | coming_soon |

## Shared dimensions (all three)
- Outer envelope: **16 W × 18 H × 4 D**, pivot at base center, front facing south (+Z) toward the spawn (match the pass-1 arch orientation exactly so the builder needs no changes).
- Inner opening: **10 W × 12 H**, bottom at Y=0 (flush with the deck, no step).
- Portal surface: a separate mesh `bw_portal_surface_<course>`, one quad 10×12 (2 tris) inset 0.5 behind the front face, UV 0–1. RobloxDevBot drives it with an animated Texture/Beam (see Glow).
- Nameplate: reuse `bw_arch_nameplate` (8×2×0.5, brass + parchment) centered on the lintel front at Y≈14.5. The course name is a **SurfaceGui** on the parchment face, not modeled text, so the state and name can change.
- "Coming soon" sign: reuse `bw_coming_soon_sign` (6×2) hanging from two rope loops under the nameplate. RobloxDevBot hides it when the course goes live.
- Apron: a 12×0.1×4 threshold plank strip in front (same deck atlas), so the walk-in reads.

## Trigger volume
- An invisible, non-colliding part, `PortalTrigger_<courseId>`, **10 W × 10 H × 3 D** (lobby.json `triggerSize`), centered in the opening at (x, 5, 32), CanCollide false, CanQuery false, Transparency 1.
- Behavior is RobloxDevBot's: walk in, then a 0.4 s fade and TeleportService to the course place, with no camera motion (lobby.json comfort rules). While a course is `coming_soon`, the trigger is off and the portal surface shows its dim idle state.
- Don't model the trigger. Only make sure no geometry intrudes into the 10×12 opening.

## Collision
- 3 boxes per arch (as in props.md): left leg 3×18×4, right leg 3×18×4, lintel 10×4×4 at Y 12–16 (adjust each to its silhouette, ±0.5). No mesh collision. Leaves, crystals, lanterns and the portal surface are CanCollide false.
- The opening (10×12) stays fully clear for VR players and their hands.

## Per-portal themes
### 1. Lantern Grove: gnarled lantern tree (budget 15k tris)
- Two twisting trunks that grow into a knotted lintel. Chunky leaf blobs in red, orange and gold, with 6 hanging paper lanterns on short rope cords, plus moss and a few autumn flowers at the roots.
- Colors: bark #6B4429 (dark #4A2F1A), leaves #E58A3A / #C9473A / #E8C24C, lantern glow Neon #FFC867, rope #CDB38A, brass #C9A04A.
- Glow: the portal surface is a warm amber swirl (#FFC867 → #E58A3A) scrolling slowly (UV offset ~0.05/s) with additive firefly sparkles (ParticleEmitter, ≤ 15 particles). The lantern globes are Neon and pulse ±15% at 0.5 Hz.

### 2. Sugarloaf Canyon: striped sandstone towers (budget 8k tris)
- Two stacked sandstone towers banded in horizontal stripes, a flat stone lintel, rock-candy crystal clusters on the shoulders, a small lollipop saguaro at the base, and 2 brass lanterns on the legs.
- Colors: sandstone #D9714A / #F0C9A0 bands, crystal Neon #F6A6C8 and #FFE08A, cactus #6FBF5A, lollipop #E2574C / #F6EBD8, brass #C9A04A.
- Glow: a pink-to-orange sunset swirl (#F6A6C8 → #F2A57E) slowly rotating, and the crystals shimmer (Neon, slow color tween between the two crystal hexes).

### 3. Aurora Archipelago: stacked ice crystals (budget 10k tris)
- Faceted purple crystal shards stacked into an arch on a dark rock base dusted with snow, with cyan glowing tips, 2 brass lanterns on short wooden posts, and an optional small snowpuff figure (separate mesh, ≤ 1.5k, counted in the budget).
- Colors: crystal #7B5BD6, tips Neon #9FE6F2, rock #3A3550, snow #EEF3F7, felt accent #36997A on the base mat, brass #C9A04A.
- Glow: aurora ribbons on the portal surface (green #5BE3A0 → violet #9B6BFF) scrolling vertically, crystal tips Neon with a slow breathing pulse, and ≤ 10 snowflake particles.

## Budget and materials
- Under 20k tris each (targets 15k / 8k / 10k, the same as the pass-1 numbers, so the 120k lobby total still holds; current total 48.7k).
- Use the shared 1024² `bw_atlas_1024.png` for wood, brass and rope. Use vertex colors for the bark, sandstone, crystal and rock where possible, and at most one extra 512² texture per portal. No alpha-blended leaves (alpha cutout at most). No real lights: Neon emissive only, and at most 1 PointLight per portal (counts toward the lobby's limit of 8).
- Use 2-segment bevels on chunky edges, rounded toy-like forms, and no detail under 0.3 studs.

## Export
- `bw_arch_<course>.fbx` (replaces pass 1, same names) + `bw_portal_surface_<course>.fbx`, under `boardwalk/models/fbx/`. Scale 1 BU = 1 stud, pivot at base center. Record the collision boxes in `manifest.json`.
- Moving parts (lanterns, snowpuff) go in separate meshes if they will animate. Render a preview PNG per portal, with a 2×5 reference capsule standing in the opening.
