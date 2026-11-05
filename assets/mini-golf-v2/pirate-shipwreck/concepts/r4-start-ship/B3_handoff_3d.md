# Start Ship B3: hole 1 on the ship, two-flight ramp (handoff for 3D Model Bot)
Sheet: start_ship_B3_hole1.png. Hero art: raw/B3.png (redrawn from B2 with only the ramp changed). B2 files are unchanged. Palette: Look B (wood 110,70,40; dark 80,50,30; post 100,72,50 / 122,90,64; rock 115,100,92; felt 105,185,98; sand 226,184,128; flame 240,110,30).

Unchanged from B2: ship ~320 x 90 x 60 studs, mast tip ~160, hull + masts + sails tilt ~15 deg with the keel buried, deck Y=24 and cabin floor LEVEL, cabin at the stern on the centreline with the door on the low (sand) side, tee pad 12 x 14 about 6 studs from the door, level outrigger platform ~18 long past the hull on 2 or 3 posts, pier beside the cup, intact hull, plain cream sails, plain red flags, no skull.

## Changed: ramp = 3 separate meshes, each on its own origin
Shot line: tee -> outrigger platform -> FLIGHT 1 -> LANDING -> FLIGHT 2 -> apron -> ~30 studs of sand -> cup.
1. **flight1**: 12 wide inside the rails, ~13 deg (12 to 15 ok), top edge at Y=24, bottom edge at Y=12. Run ~52 studs. 2 studs thick, felt top, wood stringer. Origin at the top-centre edge (where it meets the outrigger platform), pointing straight out from the cabin door.
2. **landing**: flat felt, 16 x 16, top at Y=12, on 4 wooden posts to the sand. Felt-lined rails on all open sides, ~3.5 high. The south (outer) edge rail is a solid, slightly taller rail (~5.5) on its east part, so a straight shot down flight 1 hits it. Origin at the centre of the north edge (where flight 1 arrives). The SW corner is open (12 wide) for flight 2.
3. **flight2**: 12 wide, ~13 deg, top at Y=12, bottom at Y=0, run ~52 studs, then a flat felt apron ~16 long at Y~0 that merges into the sand (apron slightly wider, ~14). Heading turns ~30 deg toward the pier (west of straight) from the landing's SW corner. Origin at the top-centre edge, with the yaw baked in 0 deg, so the course builder applies the 30 deg turn by rotating the origin.
Each flight ~3k to 5k tris, landing ~3k. Rails with posts every ~16 studs and rope trim, lantern posts at the flight 1 mouth.
Rock bumper: one separate small rock prop (~18 x 16 studs footprint, ~6 to 9 high) beside the lower end of flight 2, on the east side, offset about 17 studs from the flight centreline, not on the apron. Keep ~12 studs around the cup clear of any prop (bumper, rocks, lanterns, pier).

## Collision (simple invisible parts, no mesh collision)
- flight1 and flight2: one rotated box or wedge each for the felt surface (top at the slope), plus two thin box rails each (~3.5 high). Felt gets the ball's felt friction and bounce, rails bounce. Players walk the 13 deg slope.
- landing: one flat box at Y=12 plus rail boxes. The outer rail box has the same bounce as the other rails and must be tall enough that a fast ball can't jump it (5.5+).
- Deck, cabin floor, outrigger platform: flat boxes with tops at Y=24, cabin wall boxes, edge rail boxes ~4 high on open edges except the flight 1 mouth.
- Hull below deck, masts, sails, rigging: scenery, no collision (or a few simple boxes to keep players out). Rock bumper: a simple box or sphere collider with ball bounce.
- No gaps or lips at the joins (platform to flight 1, flight 1 to landing, landing to flight 2, flight 2 to apron). Overlap the seams by ~0.5 stud so the ball doesn't catch.

## Notes for RobloxDevBot
- The landing is where speed is lost. A straight shot hits the outer rail and bounces west toward flight 2's mouth. Check in playtests that the ball reliably finds the mouth and doesn't escape over the SW corner. Tune rail height, friction, and the bounce of the outer rail.
- Mesh pivots at the joins let the builder tweak the ramp turn (28 to 32 deg) without remodelling.
