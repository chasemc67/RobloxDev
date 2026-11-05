# Lantern Grove fix_zfight progress
- 2026-10-14 01:37 PT start. holes.json MD5 ee85a3af73ec339b326cf6ba20489b0a (recorded as baseline; no Aurora-style target given).
- Scope: h9_lantern_pendulum AND h9_lantern_pendulum_h9dim (H9 uses the h9dim variant via PropPlacements h9Dim.variants), lantern_span_20 (the H8 span), grass_tuft, gold_leaf_bush, h5_respawn_stone; leaf_pile measured only (H7 bush/pile overlap is placement). H8 EntryRing is built by CourseBuilder.luau (procedural parts), not an FBX -> out of scope, reported.
- Backup: /workspace/RobloxDev/assets/vr-minigolf/lantern-grove/models/_src/fix_zfight/_backup_20261014_0137 (tar of manifest + 7 approved FBX; sha256 of all fbx/*.fbx + manifest).
- 01:40 PT dump 3dmb_lg_dump0 exit 0; BEFORE metrics /workspace/lg/before_metrics.json (pendulum felt 0.037 at swing, 70 intersecting pairs, 56 parts <0.2; respawn stone felt 0.0, 83 intersecting; span_20 35 intersecting/355 coplanar; tuft 20 intersecting, all 16 blades 0.03 thick; bush 5 intersecting). Pendulum mesh is visual only (CourseBuilder uses invisible blocker colliders) so a small visual foot lift is gameplay-safe. Running rebuild v1.

## Result (2026-10-14 ~02:25 PT)
Outputs: models/fbx/fix_zfight/{6 FBX, fix_zfight_manifest.json, fix_zfight_fitcheck.json, silhouettes_fix_zfight.png}. Scripts: _src/fix_zfight/work/.
All 6 after (fresh Blender 5.2 reimport; import tris == built tris for every object; root/pivot + object + material names unchanged):
| asset | tris | intersect | gap<0.08 | coplanar | thin | min gap | felt / rail | IoU f/s/t | ray-thick min |
| gold_leaf_bush | 978 | 0 | 0 | 0 | 0 | .086 | 2.27/1.61 | .99/1.0/.99 | .0016 |
| grass_tuft | 384 | 0 | 0 | 0 | 0 | .086 | 2.08/1.53 | .76/.50/.50 | .0012 |
| h5_respawn_stone | 244 | 0 | 0 | 0 | 0 | .086 | .156/1.34 | 0/0/.99 (now .64 tall) | .0215 |
| h9_lantern_pendulum(+_h9dim) | 398/396 | 0 | 0 | 0 | 0 | .083 | .159 full ±11° swing/1.43 | .65/.66/.97 | .104 |
| lantern_span_20 | 2128 | 0 | 0 | 0 | 0 | .083 | 5.94/5.35 | .68/.96/.66 | .0052 |
Protected sha256 (157) verified unchanged. 3dmb_lg_* tasks deleted; no Blender running.
Open: pendulum body now red/cream/glow/cream stacked layers (bands not inlaid), chain simplified, bottom iron dropped; span Iron hooks object removed; tuft blades merged (gold mostly lost); respawn stone height change; EntryRing is code (CourseBuilder 1043-1046); bush/leaf_pile overlap is placement. Remaining thin wedges: ray-thickness < 0.2 at sharp corners/tapers on bush, tuft, stone, span (not cheap to fix without silhouette loss).

## Pendulum v5 (02:40 PT)
Body = rings red .243 / cream .206 / red .206 / cream .206 (gaps .086/.12/.086) cut from the true body sections, around a recessed Glow core (0.286 in, 0.086 clear), glow visible in slits (widest mid). Both pendulums 554 tris, 0 intersect, min gap .083, thick ≥.206, felt .159 full swing, rail 1.435, IoU .66/.67/.97 (chain .36 front: original thin ring links can't be reproduced at 0.2 thick; body .82). Import==build, roots/names/mats same. Manifest/fitcheck/sheet updated. Protected OK. Tasks deleted, no Blender.

## fix_zfight2 (03:55 PT) — Game Art Bot rejected the 0.64-tall respawn stone
H5 respawn stone rebuilt as a flat disc 0.206 thick at y .156–.362 (felt 0.156): ShroomGlow centre dot r .103, Slate annulus r .189–.395, Moss sector (−95°..−5°) split off with 0.086 radial gaps. 856 tris, 0 intersect/coplanar, gap .086, top IoU .81 (thin original glow ring can't be 0.2 wide inside a 0.39 disc). Out: fbx/fix_zfight2/. Grass tuft: no original blade could be added at ≥0.2 without touching the clumps (tried full and trimmed blades) — not done.

## fix_zfight5_uv (2026-10-15 ~11:40 PT) — H5 disc UVs
fix_zfight4/h5_respawn_stone.fbx had no UV map. Imported it unchanged (384 tris, 194 verts, slots Slate/ShroomGlow/Moss), added UVMap: top+bottom planar plan projection (u=0.5+x/0.79, v=0.5−z/0.79, image top = −Z), rim faces -> radial band r .47–.49 inside the opaque edge; h05_disc_color.png embedded and wired to all 3 slots. Geometry identical (dev 0.0). Out: fbx/fix_zfight5_uv/{h5_respawn_stone.fbx, h05_disc_color.png, manifest_fix_zfight5_uv.json, preview_h5_respawn_stone_top/close.png}. fix_zfight4 untouched. Built by Claude Code (claude-opus-5-5), schtask 3dmb_lg_j3 deleted, no Blender running.
