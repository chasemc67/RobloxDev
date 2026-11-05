# Golden Hour Boardwalk lobby: props for 3D Model Bot
Refs: `../concept_C_boardwalk.png` (spawn view), `concept_pier.png`, `concept_arches.png`, `layout_boardwalk_v1.png`. Placement and sizes come from `lobby.json` (studs, X east, Z south, deck top Y=0).
**Quest targets:** whole lobby ≤ 120k tris visible, ≤ 20k per mesh, ≤ 40 unique meshes, texture ≤ 1024² (512² for small props), one shared 1024² trim/atlas for wood, brass and rope. Prefer vertex color + atlas over many SurfaceAppearances. Use no alpha-blended foliage (alpha-cutout at most), and no real lights on props: lanterns use emissive (Neon) plus at most ~8 PointLights in the whole lobby. Bevel chunky edges (2 segments), keep shapes rounded and toy-like, and use no tiny detail under 0.3 studs.

## Palette (hex)
| Use | Hex |
|---|---|
| Deck plank warm | #B5835A |
| Deck plank dark / gaps | #7A4E2D |
| Post / beam wood | #8A5A34 |
| Brass trim | #C9A04A (highlight #E8C979, shadow #8C6A2A) |
| Parchment | #F1E2BE (ink #4A2F1A) |
| Lantern glow (Neon) | #FFC867 |
| Rope | #CDB38A |
| Green turf | #6FBF5A (fringe #4F9A43) |
| Awning stripes | #E2574C / #F6EBD8 |
| Sandstone (Sugarloaf arch) | #D9714A / #F0C9A0 bands |
| Crystal (Aurora arch) | #7B5BD6, #9FE6F2 tips (Neon) |
| Lantern-tree bark / leaves | #6B4429 / #E58A3A, #C9473A, #E8C24C |
| Stone footings | #8D8A86 |
| Ocean | #3E8FB0 (shallows #6FC2D1) |
| Sky/fog tint | #F2A57E |

## Props (size W×H×D studs · tris · material)
**Structure (modular, tiling)**
1. Deck plank module 10×1×10, tile 2 variants · 300 · wood atlas
2. Deck edge post + rope railing section, 10 long × 3.5 tall · 500 · wood/rope/brass caps
3. Pier piling cluster 2×6×2 (under the pier, every 10) · 250 · wood
4. Beach sand ground: plain Roblox terrain or a flat part, no mesh needed

**Course select and UI**
5. Course-select board 26×10×2 with 3 card slots (6×8), brass frame, 2 side lanterns, stone footing · 6k · wood/brass/parchment. Cards are separate textured planes (reuse `store/ui/card_*` art) so RobloxDevBot can swap states.
6. Leaderboard wall 14×10×2, 3 parchment panels (SurfaceGui), brass header plate · 3k
7. Signpost with 3 arrows (Practice, Leaderboards, Pier) 3×7×1 · 800

**Portals (each ~18 tall, 16 wide, 4 deep; inner opening 10×12, portal surface = separate plane)**
8. Lantern Grove arch: gnarled tree trunk arch, leaf clusters as chunky blobs, 6 hanging lanterns · 15k
9. Sugarloaf Canyon arch: two striped sandstone towers + lintel · 8k
10. Aurora Archipelago arch: stacked crystal arch, dark rock base · 10k
11. Arch nameplate (brass + parchment) 8×2×0.5, and a "Coming soon" hanging sign 6×2 · 400 each
12. Portal surface plane: 1 quad with an animated texture/beam, made by RobloxDevBot

**Practice green**
13. Green turf slab 34×0.4×20 with a rounded bumper rail 0.8 tall · 2k · turf + wood
14. Windmill 6×10×6 with separate blade mesh (rotates slowly, out of the spawn view) · 4k
15. Cup + flag 0.6×5 · 200; tee mat 2×0.1×2 · 20

**Social**
16. Birdie Bites shack 16×14×18: counter, striped awning, menu board, cupcake/candy props as a single merged mesh · 12k
17. Bench 6×2.5×2 · 600; picnic table 6×3×6 · 900
18. Barrel 2×3×2 · 300; crate 2×2×2 · 50; flower planter 4×2×2 · 1k
19. Beach umbrella 6×7×6 · 700
20. Lantern post 1×7×1 (emissive glass) · 400; string-light span 10–20 long (merged bulbs, emissive) · 300

**Backdrop (low detail, far)**
21. Sea stacks / rock arch silhouettes, far ocean · 3k total · vertex color only
22. Lantern-tree canopy cluster (NW corner) · 6k

## Rough budget
Arches 33k + board/leaderboard 10k + shack 12k + green/windmill 6k + deck/rail instances ~30k + small props ~15k + backdrop 9k ≈ 115k.

## Export
Export each prop as its own FBX, pivot at its base center, facing -Z (north) at yaw 0 to match lobby.json, at 1 Blender unit = 1 stud (scale 1.0 on import). Name them `bw_<prop>.fbx` under `assets/vr-minigolf/lobby/boardwalk/models/`. Use one collision box per prop (no mesh collision) except the arches, which use 3 boxes (2 legs + lintel). Render a preview PNG for each.
