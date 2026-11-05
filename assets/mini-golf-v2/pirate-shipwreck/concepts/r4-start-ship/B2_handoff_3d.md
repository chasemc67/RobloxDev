# Start Ship B2: hole 1 on the ship (handoff for 3D Model Bot)
Sheet: start_ship_B2_hole1.png. Hero art: raw/B2.png. Palette: Look B (wood 110,70,40; dark 80,50,30; post 100,72,50 / 122,90,64; felt 105,185,98; sand 226,184,128; rock 115,100,92; flame 240,110,30).

Layout (studs): ship ~320 long x 90 beam x 60 tall, mast tip ~160. Deck Y=24, sand Y=0. Stern at -X, cabin on centreline at stern (about 60 x 55 footprint, ~30 tall). Cabin door faces the low (sand) side.
Hull + masts + sails + rigging lean ~15 deg toward the sand side, keel buried. Deck, cabin floor, outrigger platform, tee pad and ramp are all LEVEL / on a fixed grade, not tilted.

Shot line: cabin door -> tee pad on deck (12 x 14 felt, ~6 studs from the door) -> level outrigger platform (~18 long, sticks out past the hull's low side, on 2 or 3 posts) -> ramp -> flat felt apron 16 -> ~36 studs of sand -> cup (felt green ~60 x 40 on sand, beside the pier).
Ramp: 12 wide (inside the rails), 13 deg (12 to 15 ok), 24 rise -> ~104 studs of run, 2 studs thick, felt top, wood stringer underneath. Felt-lined side rails ~3.5 high, with posts every ~16 studs and rope trim; ball must not leave the ramp. Gap in the low-side bulwark for the ramp mouth, with a lantern post on each side. Pier: separate prop, west of the ramp, ~10 wide, runs from the lagoon to the sand, beside the cup.

Mesh split (each < 20k tris):
1. hull shell, intact, no holes, tilted, ~15k
2. deck + cabin + outrigger platform, level, ~12k
3. masts + sails + rigging + flags (plain cream sails, plain red flags, no emblem), ~12k
4. ramp (surface, rails, stringer), ~6k, on its own origin so the course builder can nudge slope and length
5. pier + lantern posts, ~5k
6. small dressing (barrels, crates, anchor, rope), separate
Glow parts (lanterns) are separate Neon or PointLight parts.

Collision (invisible, simple parts, not mesh collision):
- Deck, cabin floor, outrigger platform: one flat CanCollide box each, top at Y=24, with cabin wall boxes and a bulwark box on the high side. Players must not slip off the deck edge, so use rail boxes 4 high along the open edges (except the ramp mouth).
- Ramp: one wedge/rotated box for the felt surface and two thin box rails. Felt surface needs ball friction and bounce like the other felt, rails bounce the ball. Do not use mesh collision for the ramp.
- Hull, masts, sails, rigging: scenery. Hull below the deck is CanCollide off, or a few simple boxes just to keep players out. Sails and rigging: no collision.
- Players must be able to walk the ramp too, so the 13 deg slope is OK for the Humanoid.
- Keep the area within 12 studs of the cup clear of props so the green stays flat.
Open points for RobloxDevBot: the ball's speed down a 104-stud ramp is high. The apron, felt friction and a gentle end bump may be needed so it doesn't overshoot. Tune with playtests; a short flat felt run before the ramp mouth also helps the ball settle.
