# Rev 1: edit gen_tankdock.py in place (back it up first to gen_tankdock_rev0.py), rerun with python, keep all self-checks passing.
Allowed materials add: 'Bubblegum' (candy pink #F78FB3, existing Sugarloaf palette). Still NO red/cream/MintWhite/PepRed/Canvas/CreamTaffy/Cherry.
Each part must stay < 3000 tris (quads count 2).
## h09_water_tank
Add two wide RockCandyLilac bands on the barrel: one between hoop 1 (y3.9) and hoop 2 (y5.6), one between hoop 2 and hoop 3 (y7.2), each covering most of the gap (~0.25 margin to each hoop). Build them as open lofted sleeves (no caps) following the barrel bulge profile at radius +0.02 so they sit just proud of the timber and under the iron hoops. Stay inside the existing env box (x <= -9.7).
## h14_loading_dock (keep position: x -9.6..-4.65, z -35.35..-25.2)
1. Ore pile ~3x bigger: on the crate that has ore, a heap of RockCandyLilac octahedra that spills over the crate rim (crystals overhanging the rim edges ~0.2-0.3 and lower ones touching the crate sides), plus 6-8 tall pointy Bubblegum crystal shards poking up/out at angles (elongated octahedra or 4-sided pyramids, tilted). Heap top <= 3.4. Keep x <= -5.4.
2. Two tall corner posts (Timber, 0.4 square, Iron foot plate and a SOLID Iron cap) at the ramp-side edge corners: about x -4.95, z -25.6 and z -35.05, from y 0 to y 4.6, with a Timber cross beam 0.35x0.45 joining their tops along z (y 4.15..4.6) and two short diagonal knee braces. Nothing past x -4.7.
3. Fix the open-tube iron post caps: every post cap/foot must be a closed solid box (all 6 faces); check the box helper output, no missing top faces.
Update env_boxes to [[[-9.6,0,-35.35],[-4.65,4.7,-25.2]]] and the self-check y max accordingly. Update p.notes for both parts honestly. Print tris per part.
