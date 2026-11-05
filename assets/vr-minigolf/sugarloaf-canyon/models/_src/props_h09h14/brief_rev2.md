# Rev 2: H14 dock ORE ONLY. Edit gen_tankdock.py in place (back up first to gen_tankdock_rev1.py). Do not change h09_water_tank or any non-ore dock geometry (deck, posts, beam, crates, steps, caps). Keep self-checks passing and dock < 3000 tris (currently 1468).
Ore heap on the existing ore crate (do not move the crate):
- A chunky mound: 1 big central RockCandyLilac rounded heap (loft or several fat octahedra, widths 0.5-0.9) filling the crate top and rising to ~1.0-1.2 above the rim, top <= 3.9 (beam bottom is 4.15; keep >= 0.2 below it).
- Clearly drapes over TWO crate sides: the crate side facing +x (toward the ramp/tee) and the side facing +z. Spill crystals hang over those rims (overhang 0.3-0.45 past the crate face) and 3-4 crystals sit tumbled on the deck at the foot of those two sides. Keep all ore x <= -5.4 and inside the env box.
- Pink: 7-9 FAT Bubblegum crystals, chunky hexagonal prisms with pointed tips (6-sided, radius 0.18-0.3, length 0.6-1.2), tilted 15-40 deg outward from the heap, clustered like h14-concept.png's pink rock-candy pile, some on the draped sides.
Update the dock note honestly, print tris.
