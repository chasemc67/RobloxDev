# Notes for the builder (from the orchestrator, 2026-10-03 20:10 PT)
New references from Game Art Bot are in this folder. READ README.md here first (proportions, which hand holds which weapon, arena size about 10-12 robot-widths across).
- Each of c01/c05/r05 has `-turnaround.png`, `-parts.png`, `-palette.png` / `-palette.md` (hex values). Use the palette hex values for vertex colors/materials.
- S04: `s04-topdown.png` (grid blockout), `s04-hero.png`, `s04-palette`. `textures/` has 1024px tileable `desk-wood.png`, `paper-grid-mat.png`, `plastic.png` (tint plastic for the other block colors).
Caveats:
- **C05 (Aero)**: the side view is closer to 3/4 and the back vent is invented, so trust the FRONT view and the parts sheet.
- **R05 (Kitsune)**: the left-hand talisman launcher is drawn too small on the turnaround, so use the PARTS-SHEET size.
- **S04**: where the top-down and hero shot disagree (an extra crate on the top fence, a blue piece on the left), go with the HERO shot.
