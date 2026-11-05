# VR Mini Golf: Lobby options (SRV-136)
Each option has a concept painted from spawn at VR eye height (`concept_*.png`) and a top-down layout in studs (`layout_*.png`, 1 grid square = 20 studs). Contact sheet: `lobby_sheet.jpg`. Layout generator: `_layouts.py`.
The course board in every option is a physical brass-and-parchment kiosk about 15 studs in front of spawn, standing about 6 studs tall with its cards at eye height. It has 3 cards: Lantern Grove (live), Sugarloaf Canyon (coming soon) and Aurora Archipelago (coming soon). You pick a course by pointing at its card with the laser or by walking into its portal.

## VR comfort notes (all options)
- Spawn faces north toward the board, so there's no forced turn at spawn. Floors are flat or gently ramped (under 15°), with no stairs on the main paths.
- Main paths are at least 8 studs wide. Railings run along every edge or drop. Portals are walk-in arches with a short fade, with no camera motion.
- No moving floors or spinning set pieces near spawn. Cards and leaderboards are readable from 10 to 20 studs away. The lighting is steady and nothing flickers.
- Teleport and snap-turn friendly: the ground is open, with no low ceilings near spawn.

## A. Hollow Oak Clubhouse Plaza, 200 x 180 studs
**Pitch:** a giant hollow-oak clubhouse at dusk in the Lantern Grove forest, with three carved gates that lead into each course's world.
- Spawn at (100,150), and the course board at (100,135). The campfire plaza at the center connects to the gates at Lantern Grove (W), Sugarloaf (N) and Aurora (E).
- Practice green: 3 holes in the SW. Social spots: the campfire ring, hammocks and benches, and a tree-deck lounge up a ramp. Leaderboards on either side of the board.
- Props: hollow oak shell, decks and rope bridge, 3 stone gate arches, campfire with log seats, hammocks, lantern posts and strings, course board kiosk, 2 leaderboard boards, mushrooms and autumn shrubs.

## B. Skyward Orrery Islands, 240 x 200 studs
**Pitch:** floating islands at golden hour around a brass orrery fountain, each linked by bridge to a portal ring into its course. It's the most "hub world" option, and new courses get added as new islets.
- Spawn at (120,165), and the board at (120,150). The orrery fountain sits at the hub center. Railed bridges lead to the portal islets at Lantern Grove (NW), Sugarloaf (N) and Aurora (NE).
- Practice islet in the SE. Swings and picnic islet in the SW. Leaderboards on either side of the board.
- Props: 6 floating rock islands, a brass orrery fountain, 3 portal rings, rope bridges, railings, swings, picnic tables, signposts, lantern posts, a cloud sea skybox, and 2 banner leaderboards.

## C. Golden Hour Boardwalk, 220 x 150 studs
**Pitch:** a cozy seaside mini golf boardwalk at sunset, with three themed archways along the promenade, a windmill practice green and the Birdie Bites snack shack.
- Spawn at (100,100), and the board at (100,85). The promenade runs north to the arches at Lantern Grove (W), Sugarloaf (center) and Aurora (E).
- Practice green with a windmill in the E. Social spots: the Birdie Bites shack, pier seating to the SE, and benches. A leaderboard wall to the W.
- Props: plank deck modules, 3 themed arches (tree, sandstone, crystal), a windmill green, snack shack with awning, benches, barrels, string lights, the pier, and an ocean plane.

## Cost
3 x gpt-image-2.5-sunburst with references at 2048 px ≈ $0.22 total. Layouts were drawn locally with PIL.
