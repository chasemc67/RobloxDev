# HERO LOOK pass 4

Completed render-only pass: Cycles OptiX GPU, 128 samples, denoised, six 1920x1080 PNGs. Four preview rounds inspected. A terrain-intersecting fourth-round junction camera was reverted to the clear third-round view; the prematurely launched full batch was stopped and superseded by the complete final batch.

Exposure: AgX +1.35 (one stop above pass3). Camera-ray world: linearized #FFB98A peach horizon to #4FC8D8 turquoise upper sky, strength .65; separate lavender ambient (.38,.28,.6), strength .65. Lavender overhead area fill 650000, size 1100. West warm sun energy 3.8, color (1,.57,.28), angle 5 degrees. Shadow rock reads rose/lavender; foam and pale terrain remain bright without broad flat white clipping.

Sun directions are game Y-up directions toward the sun; Blender directions use rb(). General bearing/elevation 270/25: (-.906308,.422618,0). Arch 270/8: (-.990268,.139173,0). Sun disc size 120 at distance 2500 (about 2.75 degrees); arch eye ray crosses near x=-469 at y210, safely below measured lintel y223.2.

Imported sunset_arch vertex bounds, local game: [-8.8073,-2.4000,-25.7199] to [8.9460,46.6473,25.9067]. Central inner lintel measured from vertices with abs(local z)<3 is world y223.200. Real near arch at (-478,190.4,205) remains visible with terrain and placed Crown pieces; ground occupies the bottom third. No arch-specific terrain/piece hiding. Existing distant-card visibility rules retained.

| Shot | Eye (game x,y,z) | Target | Horizontal FOV |
|---|---|---|---|
| old_sugarloaf_skyline | [75.0, 23.0, 505.0] | [80.0, 88.0, -130.0] | 58? |
| dam_crest_walk | [0.0, 36.0, -200.0] | [0.0, 61.0, -302.0] | 90? |
| narrows_crystal_walls | [280.0, 27.0, 310.0] | [280.0, 31.0, 240.0] | 75? |
| junction_town | [125.0, 47.0, 550.0] | [225.0, 24.0, 420.0] | 92? |
| world_vista | [1000.0, 1080.0, 1000.0] | [0.0, 70.0, 0.0] | 58? |
| sunset_arch_from_crown | [-355.0, 194.0, 205.0] | [-478.0, 211.0, 205.0] | 55? |

Render-only additions: three distant warm-lit cumulus clusters (12 smooth ellipsoid puffs); downstream spillway sheet width20, top y108 z-299.6 to base y16.8 z-297.7, offset in front of opaque dam body to stay visible; 27 blue-white vertical streak ribbons; low-density .035 base-spray volumes (three ellipsoids); elliptical plunge foam ring y17.25 centred z-288. Source water/fall meshes retained. Sun lighting, sky, fill and cameras changed only in assembled render scene.

Files: `_src/render_hero.py`; backup `_src/render_hero_pass3.py`; `previews/hero/{shot}.png` (six named shots above); `previews/hero/sugarloaf_canyon_hero.blend`; `previews/hero/render_report.json`; `previews/hero/contact_sheet.png`; `previews/hero/compare_vs_vistas.png`; logs `_src/pass4_preview1.log` through `pass4_preview4.log`, `_src/pass4_final.log`; `_src/PROGRESS.md`; `_src/pass4_done.flag`.

FBX directory, layout.json, manifest.json and FBX source textures were untouched. No mover work or unrelated briefs used. Skyline, narrows and world-vista camera definitions retained.

Remaining gaps vs V1?V4b: supplied geometry has broad bare sand rather than lush green putting paths, fewer props and coarse cliff silhouettes. V1 lacks the reference foreground green/building staging; V2 keeps the supplied lift and terrace composition; V3 junction row now sits left and recedes, but river is mostly outside frame and plaza remains sparse; it does not resemble the reference rope bridge. Crown ground is peach terrain, not a reference-like green fairway, and distant cards remain visible through the opening. Cloud puffs are stylized simple forms rather than detailed atmospheric cumulus. Warm west-facing edges improved, but arch east face deliberately receives lavender shadow light. Dam shows one tall cascade with restrained spray rather than the reference multiple falls. No geometry reconstruction attempted.
