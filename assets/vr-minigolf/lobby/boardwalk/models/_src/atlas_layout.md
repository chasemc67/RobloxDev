# bw_atlas_1024.png layout (one shared 1024x1024 atlas, 8-bit RGB, no metadata)
Grid of 128px cells (8x8). UV islands snap to cells; tiling surfaces use vertical-strip trim rows (tile in U).
| Rows (px y) | Content |
|---|---|
| 0-255   | Wood trims: plank warm #B5835A w/ dark gaps #7A4E2D (row0), post/beam #8A5A34 grain (row1) |
| 256-383 | Brass trim gradient #8C6A2A -> #C9A04A -> #E8C979 (bevel strip) ; Rope #CDB38A twist strip |
| 384-511 | Parchment #F1E2BE w/ ink #4A2F1A border; nameplate blanks (text is SurfaceGui/decal, not baked) |
| 512-639 | Awning stripes #E2574C/#F6EBD8 (8 stripes across 1024) ; stone footing #8D8A86 |
| 640-767 | Turf #6FBF5A / fringe #4F9A43 ; sandstone bands #D9714A/#F0C9A0 |
| 768-895 | Bark #6B4429 ; leaves #E58A3A #C9473A #E8C24C blob swatches ; crystal #7B5BD6 |
| 896-1023| Flat swatch cells (16 x 64px): every palette hex as a solid colour for vertex-colour-like flat props, Neon glow #FFC867 and crystal tip #9FE6F2 (used on separate Neon MeshParts) |
Materials per FBX: `BW_Atlas` (all opaque) + optional `BW_Neon` (emissive parts as their own MeshPart, flat colour, no texture). Backdrop (#21) vertex colour only.
