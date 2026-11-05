# Aurora Archipelago: Theme Bible

VR mini golf for Roblox, **course 3. 18 holes, total par 53** (front 27, back 26). A ring of floating, snow-capped rock islands hangs
over a glowing cloud sea at night. Green and violet aurora ribbons ripple overhead, ice-crystal clusters glow, brass lanterns burn
on wooden posts, and translucent ice bridges and frozen waterfalls pour off the island edges. The icy-tropical twist: warm turquoise
hot-spring lagoons with frosted palms, a reef of candy-bright coral-ice, a whistling geyser, and **snowpuffs** (round, original
penguin-puffin whimsy figures) watching every hole. The islands climb anticlockwise round the **Starfrost Spire**, a giant floating
aurora-crystal spire.
Reference art: `../store/ui/card_soon_auroraarchipelago_color_clean.png` (the menu card).

Status: **Phase 2 done.** `holes.json` (built by `tools/build_holes.py`) specs all 18 holes; every hole meets every sim target (`playtest-log.md`, round p2), with notes and layouts in `hNN-notes.md` / `hNN-layout.png`. The world validator is CLEAN (`world/validation.md`).

Units: studs. **1 stud = 0.3 m**, Y up, +X east, -Z north. Physics is the same as Lantern Grove and Sugarloaf Canyon (`tools/README.md`):
g 32.7, rolling deceleration 0.5 + 0.25·v, rails 0.63, bumpers 0.65, cup capture < 5.33 studs/s, cup radius 0.5, ball radius 0.08,
max putt 19.78 studs/s (60 studs on flat felt). Lanes 7-8 wide, greens 12-18, rails 1 high x 0.5 thick. **New surface for H4**: ice
felt, a low-friction felt type. It needs a calibrated `decel_scale` in the sim and the matching friction in Studio before tuning
(start at 0.35 x normal deceleration, measure in Studio).

## Mood

It should feel like a snow globe at bedtime: hushed, glowing and cosy, with a wink. Snow is thick, soft and rounded. Rock is chunky
slate-violet. Everything you touch is warm timber and brass. The cold is never hostile: steam curls off the hot springs, palms wear
frost like sugar, and coral grows in ice-lolly colours. The snowpuffs (round bodies, stubby wings, orange beaks, little knitted
scarves) waddle, peek out of burrows and turn their heads to follow your ball.

What's gentle: every drop is railed. The void below is a soft lilac cloud sea, not darkness. A missed ball over a gap just respawns
(+1). Nothing moves you except rides you choose.

**What's big in VR:** the Starfrost Spire rises 240 studs (72 m) above its island, tip y 340. You look *up* at it from every tee,
even the summit. The cloud sea sits 24-186 studs below your feet depending on the island. The Aurora Skybridge is 135 studs long,
146 studs above the clouds, with railings you can lean on. The Great Frozen Falls pour 146 studs off the Icefall Terraces into the
clouds.

## World arc (6 zones, low to high, anticlockwise round the Spire)

| Zone | Holes | Ground y | Where | Feel / what it teaches |
|---|---|---|---|---|
| **Lanternfall Landing** | H1-H3 | 60 | South-west: the lowest island + Glimmer Islet | Harbour quay with lanterns, the snowpuff rookery. Teaches the bank, tunnels, and the risky vs safe bridge over open sky |
| **Steamwhistle Lagoons** | H4-H6 | 84 | South-east: the geothermal island | Warm and steamy: two turquoise hot springs, frosted palms, Steamwhistle Geyser. Ice felt, the first mover (geyser lift), side slope |
| **Candyfrost Reef** | H7-H9 | 112 | East: reef island + conch islet | Candy coral-ice gardens. Moguls, bumpers, the conch teleport |
| **Driftfloe Shelf** | H10-H12 | 146 | North-east: frozen shelf | Floe Pond with toy floes, bobsled hut, beached icebreaker. Half-pipe, then two timing obstacles |
| **Icefall Terraces** | H13-H15 | 182 | North: reached by the Aurora Skybridge | Frozen falls pouring into the clouds. Carousel sweeper, bell pendulum, icefall drop |
| **Skylight Summit** | H16-H18 | 222 | North-west: the highest island | The showpiece: moonwell, timed aurora bridge, the Halo Arch finale. Gondola home |

The route climbs 162 studs in steps: Lantern Stair (+24), then four slow lifts: Steam (+28), Coral (+34), Icefall (+36) and
Crystal (+40). The world reveals itself as you go. You start low and **enclosed** among the rookery drifts, **open up** on the
bridges, get **enclosed again** on the reef and terraces, and finish **open** on the summit, where every earlier island is spread out
below. The **Snowpuff Sky Gondola** glides 162 studs back down to the quay where you started, so the course is a loop.

## Palette

| Role | Name | Hex |
|---|---|---|
| Felt (main) | Pine felt | `#4FA83D` |
| Felt (highlight / raised tiers) | Spring felt | `#86C24A` |
| Felt (shadow / night side) | Deep felt | `#2F7A3A` |
| Ice felt (H4 glide strip) | Glassy ice felt | `#9FE3F2` |
| Snow (lit) | Moonlit snow | `#F4F6FF` |
| Snow (shadow) | Lilac snow shadow | `#C9C3EC` |
| Rock (cliffs) | Slate-violet rock | `#5E6177` |
| Rock (dark undersides) | Deep basalt | `#3A3550` |
| Rails / posts | Warm timber | `#8A5A33` |
| Rail caps | Snow cap | `#FFFFFF` |
| Brass (lanterns, fittings) | Lantern brass | `#C9A04A` |
| Lantern glow | Ember glow | `#FFB861` |
| Ice (bridges, crystals) | Glacier cyan | `#8FE3FF` |
| Ice glow (inner) | Crystal core | `#BFF6FF` |
| Aurora glow 1 | Aurora mint | `#5CFFB0` |
| Aurora glow 2 | Aurora teal | `#3DE2C8` |
| Aurora glow 3 | Aurora violet | `#B07CFF` |
| Aurora glow 4 | Aurora pink edge | `#FF7AD9` |
| Hot-spring water | Lagoon turquoise | `#2FD6C8` |
| Steam / foam | Steam white | `#E9FBFF` |
| Coral-ice 1 / 2 / 3 | Bubblegum / tangerine / mint | `#FF6FB5` / `#FFA552` / `#6FFFD2` |
| Frosted palm | Palm teal + frost | `#2E8B6A` + `#E6FBFF` |
| Snowy pine | Pine blue-green | `#2F6B4F` |
| Snowpuff body / belly / beak | Ink, cream, orange | `#222233` / `#FFF4E2` / `#FF9A3C` |
| Cup flags | Flag red | `#E03C31` |
| Teleport pads | Aurora lime | `#D8FF6A` |
| Sky (zenith) | Night indigo | `#141A44` |
| Sky (horizon twilight, SW) | Twilight lilac | `#9C8CE0` |
| Cloud sea (top) | Cloud lilac-white | `#CFC8EE` |
| Distance haze | Haze periwinkle | `#8C8FD6` |
| Moon | Moon pearl | `#F4F1FF` |
| Stars | Starlight | `#FFFFFF` |

The card's palette carries through: lilac cloud sea, white snow, slate rock, cyan ice, green and violet aurora, orange lanterns.
The warm accents (brass, ember, turquoise, coral) keep the night cosy and are what make it read as different from Lantern Grove
(warm green forest) and Sugarloaf Canyon (sunset desert).

## Materials (Roblox)

- **Felt**: SmoothPlastic or Fabric with a subtle noise texture, no reflectance. **Ice felt (H4)**: Glass-look visual (Transparency
  0.15, Reflectance 0.15) over a collider with a custom PhysicalProperties friction calibrated to the sim's ice decel. Felt arrows
  mark one-way and sloped pieces.
- **Rails**: chunky snow-capped timber meshes with brass bolts (visual). Collision is invisible parts straight from holes.json, as on the earlier courses.
- **Terrain** (see `world/materials-map.png`): Snow on island tops, Rock on cliffs over 45°, Slate on 30-45° shoulders, Ice on Floe
  Pond, Glacier on the icefall lips, Basalt and Sand round the hot springs, Cobblestone on walkways, Salt under hole pads.
  **Air below y 30**: the cloud floor is void.
- **Cloud sea**: a soft emissive cloud mesh plus particle puffs at y 36, with Atmosphere haze. It's not terrain and not walkable.
  A respawn plane sits at y 40.
- **Ice bridges, crystals, frozen falls, Halo Arch**: Glass, Transparency 0.3, Reflectance 0.1, with a faint Neon inner core (`#BFF6FF`).
  The **aurora** pieces (Skybridge deck, H17 bridge, ribbons) are Neon plus animated gradient textures shifting mint → violet.
- **Hot springs**: Terrain water tinted `#2FD6C8`, WaterTransparency 0.5, steam particles. Steamwhistle Falls is a Beam with steam.
- **Coral-ice**: SmoothPlastic with a Neon core, bright candy colours.
- **Lights**: brass lanterns (PointLight `#FFB861`, range 14, brightness 0.8) on every walkway (`world.json lantern_posts`). Crystal
  clusters and coral use a PointLight `#8FE3FF` / coral colour at brightness 0.4. The Spire carries a big SurfaceLight glow plus Bloom.

## Lighting (night, launch)

- **Night with a low moon.** The moon and its twilight band sit at **bearing 220° (SW), elevation 14°** (`world.json moon`). In
  Studio, set ClockTime ~20.6 and calibrate GeographicLatitude so the moon direction matches. **No tee plays within 45° of it**
  (validated). The moon is the side or back view while putting and the set-piece view from greens, the Skybridge and Skylight Point.
- **Aurora** in the north sky (bearings 300-60°, elevations 25-75°): animated ribbon meshes, emissive only. Most tees play north into it.
- Ambient `#2A2E5C`, OutdoorAmbient `#5A5E9C`, Brightness 1.2, ColorShift_Top `#B9C4FF`, ColorShift_Bottom `#6A4FA8`,
  EnvironmentDiffuseScale 0.6.
- Atmosphere: Density 0.32, Offset 0.15, Color `#9C8CE0`, Decay `#3A3470`, Glare 0.3, Haze 1.6 (periwinkle distance, like the card).
- Bloom intensity 0.9, size 30, threshold 1.1 (lanterns, crystals and aurora bloom). SunRays off. ColorCorrection: contrast +0.05, saturation +0.1, tint `#F2F0FF`.
- Shadows soft. Keep felt readable: each green gets one overhead warm lantern ≥ 8 above the felt, plus the moonlight.
- Particles: light snowfall (rate 6, slow), steam at the lagoons and the geyser, sparkle motes round the Spire and the crystals.

## Landmarks and set pieces

1. **Starfrost Spire** (skyline anchor): a faceted aurora-crystal spire on Spire Isle at (0, -40). The island top is y 100, the spire
   240 tall (tip y 340), with crystal shards slowly orbiting at r 50-90. **Visible from all 18 tees** (validated, tip LOS clear from every tee).
2. **Halo Arch**: a translucent glowing ice arch over H18's green, 46 wide, 34 tall, with an 18-stud clear opening. It frames the aurora.
3. **Great Frozen Falls** and the twin, Summit, Glimmer and Reef icefalls: frozen ice cascades off the island rims into the clouds.
4. **Steamwhistle Geyser**: a basalt cone on the lagoon island. A steam column puffs to 60 studs every 20 s and whistles like a kettle (visual only).
5. **Hot springs**: Steamwhistle Lagoon (with Steamwhistle Falls, a warm steaming ribbon off the south rim) and Kettle Lagoon.
6. **Snowpuff Rookery**, **Candyfrost Coral Garden**, **Floe Pond** (frozen, toy floes, ice-fishing hut).
7. **Far horizon**: 16 decorative islets in the gaps, 16 far floating islands (r 760-960) and 12 distant island-mountains (r 1150-1600)
   rising out of three cloud rings. A sister landmark, **Ice-Arch Isle**, sits on the SW horizon with the moon behind it, plus paper sky-lanterns.

**Set pieces between holes**
- **Glimmer Ice Bridge** (52 long, railed, 60 above the clouds), H3 → H4, then the **Lantern Stair**: a lantern-lit rock spine, 30 steps, +24.
- **Steam Lift** (+28), a brass steam-driven cage; **Coral Lift** (+34); **Icefall Lift** (+36) onto the Aurora Landing pinnacle.
- **Coral Ice Bridge** (50 long) out to the conch islet.
- **Aurora Skybridge** (135 long, railed, glowing green and violet deck), Aurora Landing → Icefall Terraces: the V3 vista.
- **Crystal Lift** (+40), an ice-crystal cage onto the summit.
- **Snowpuff Sky Gondola** (−162 over 869 studs, ~3 min): a seated lantern cabin from Skylight Point back down to Lantern Quay Plaza.

## The 18 holes (concepts)

Each hole has one headline gimmick and none repeats. Footprints are W x L in studs (local, including the 6-stud tee pad), reserved in
`world/world.json`. Pars are design targets that the sim will confirm.

| # | Hole | Zone | Par | Footprint | Landmark | Gimmick (one line) |
|---|---|---|---|---|---|---|
| 1 | Lantern Quay | Lanternfall Landing | 2 | 18 x 46 | Harbour lantern, Spire dead ahead | **Bank shot**: a snow-capped boulder's 45° face turns the ball onto an offset green |
| 2 | Snowpuff Burrows | Lanternfall Landing | 3 | 26 x 58 | Snowpuff rookery | **Tunnel choice**: three snow burrows (short and tight, long and safe, a dead end that rolls back) |
| 3 | Glimmer Crossing | Lanternfall Landing | 3 | 26 x 76 (span 26) | Glimmer Islet + icefall | **Rail-less vs safe bridge** over the open-sky Glimmer Gap; misses respawn at the bridge entry |
| 4 | Glissade | Steamwhistle Lagoons | 3 | 24 x 64 | Frosted palms, ice slide | **Ice felt**: a glassy low-friction strip; pace control into a snow-felt green |
| 5 | Geyser Hop | Steamwhistle Lagoons | 3 | 26 x 62 (2 tiers, +4) | Steamwhistle Geyser | **Geyser lift** (mover): a basalt platform rides a steam column up 4, pauses, sinks back |
| 6 | Palm Lagoon | Steamwhistle Lagoons | 3 | 30 x 66 | Kettle Lagoon | **Side-slope green** tilted toward a hot-spring pool hazard (respawn beside it) |
| 7 | Mogul Meadow | Candyfrost Reef | 3 | 26 x 62 | Coral-ice fans | **Rolling dips**: four snow moguls of opposing planar slopes |
| 8 | Coral Pinball | Candyfrost Reef | 3 | 26 x 60 | Giant coral-ice branches | **Bumper field**: static flat-faced coral bumpers at set angles |
| 9 | Conch Shortcut | Candyfrost Reef | 4 | 34 x 78 | Twin spiral conches | **Teleport**: into one conch, out of another near the green, or the long reef route |
| 10 | Bobsled Bend | Driftfloe Shelf | 3 | 24 x 64 | Bobsled start hut | **Half-pipe**: an S-bend bobsled channel with banked felt walls |
| 11 | Floe Drift | Driftfloe Shelf | 3 | 26 x 62 | Floe Pond | **Drifting ice floe** (mover): slides across the lane, pauses, drifts back; 45° pointed ends |
| 12 | Icebreaker Wheel | Driftfloe Shelf | 3 | 26 x 60 | Toy icebreaker | **Vertical rotor** (mover): a paddle wheel on a horizontal axle; signed bypass lane |
| 13 | Snowpuff Carousel | Icefall Terraces | 3 | 30 x 62 | Carousel canopy | **Horizontal sweeper** (mover): four arms round a solid central hub |
| 14 | Bell Buoy | Icefall Terraces | 3 | 24 x 60 | Bell gantry with icicles | **Pendulum** (mover): a brass icicle bell swings across the lane |
| 15 | Frozen Falls | Icefall Terraces | 2 | 20 x 46 (2 tiers, −4) | Great Frozen Falls | **Drop between levels**: over a frozen-fall lip into a basin green 4 below |
| 16 | Moonwell | Skylight Summit | 2 | 20 x 46 | Moonstone well | **Funnel** bowl, with the cup set off the funnel's exit line |
| 17 | Aurora Bridge | Skylight Summit | 3 | 26 x 70 (span 26) | Aurora ribbon bridge | **Timed light bridge** (mover): fades in, holds, dims away; or the fixed ice bridge the long way |
| 18 | Halo Arch | Skylight Summit | 4 | 36 x 82 | Halo Arch, Spire to the SE | **Finale**: ramp up to a raised green under the Halo Arch, reading a crystal bank on the way |

**Gimmick families**, so the variety is visible:
- static geometry: bank (H1), side slope (H6), rolling dips (H7), bumpers (H8), half-pipe (H10), funnel (H16);
- surface: ice felt (H4, new to the series);
- level changes: icefall drop (H15), ramp to a raised green (H18, finale);
- route choice: tunnels (H2), rail-less vs safe bridge (H3), conch teleport vs long route (H9);
- timing obstacles, each with a **different motion type** (no repeats):

| Hole | Mover | Motion type | Starting spec for tuning |
|---|---|---|---|
| H5 | Geyser platform | **vertical lift (piston with dwell)** | 4-stud rise at 2 studs/s, 2.0 s down (boarding window), 1.5 s up |
| H11 | Ice floe | **linear slide with dwell** | 3.5 studs/s, 1.0 s / 1.5 s pauses, 45° pointed ends |
| H12 | Paddle wheel | **vertical rotor (horizontal axle)** | 4 broad clipped vanes, 30-40 °/s, signed bypass |
| H13 | Carousel arms | **horizontal rotor (vertical axle)** | 4 arms, 20-25 °/s, solid hub excludes rests within 7 studs |
| H14 | Icicle bell | **pendulum swing** | peak ≤ 17 °/s, bell turned 30° to the swing plane (no ping-pong) |
| H17 | Aurora bridge | **appear-vanish toggle (fade with dwell)** | solid 2.2 s, 0.6 s fade, gone 1.8 s; collider only when fully solid |

**Run timing checks at 96+ phases** (and verify 120) for every mover once holes.json exists, plus the 100k soft-lock fuzz. Target
25-50% blocked phases on the intended line, aiming the sim ~10 points above the in-engine target until Studio calibrates it.

## Par spread and difficulty curve

**Par spread:** three par 2s (H1, H15, H16), thirteen par 3s, two par 4s (H9, H18). Total **53**: Landing 8, Lagoons 9, Reef 10,
Shelf 9, Terraces 8, Summit 9.

- **H1-H3 (learn)**: one idea each (bank, tunnels, a gap with a forgiving respawn). Wide felt (8), flags visible from every tee.
- **H4-H6 (read)**: surface and slope reading. The ice felt teaches pace; the first mover, H5, is slow with a long, obvious boarding window.
- **H7-H9 (commit)**: pace over moguls, angles off bumpers, then the first par 4 with a teleport risk/reward.
- **H10-H12 (systems)**: banked channel, then two timing obstacles (floe slider, paddle wheel), each with a reliable safe line ~1 stroke longer.
- **H13-H15 (precision)**: carousel and pendulum timing, then a short, sharp drop par 2.
- **H16-H18 (payoff)**: a short funnel par 2, the timed aurora bridge, and the Halo Arch finale. It should feel grand but not punishing
  (target good-player average at or under par + 0.7).

Same sim targets as the earlier courses: good HIO 0.2-10% with a brute-force ace line on every hole; good average within par − 0.7 …
par + 1; skill gap (average − good) ≥ 0.3; average ≤ par + 1.5; stroke cap ≤ 1%; 0 escapes, 0 traps, 0 timeouts.

## VR comfort

- **No forced locomotion.** Walking is optional everywhere. Every zone hub has a teleport pad (`world.json teleport_points`: Lantern
  Quay Plaza, Lantern Stair Top, Steam Lift Top, Coral Lift Top, Skybridge West, Crystal Lift Top, plus Aurora Landing and Skylight
  Point). The standard next-tee teleport lands on `holes[].tee_teleport`, 3 studs behind each tee box (validated flat).
- **Lifts and gondola**: lifts are open cages at a constant **3 studs/s** (0.9 m/s; the cap is 4) with 1-s eased starts and no jolts.
  They have solid floors, 3.5-stud railings all round, and the horizon stays visible. The gondola is a seated, enclosed cabin at
  5 studs/s. Every ride has a "teleport instead" pad at both ends. The player never moves while turning.
- **Railings on every drop edge**: each walkway side gets a chunky 3.5-stud railing (1.05 m) wherever the ground drops more than
  4 studs within **5.5 studs** of its edge. That's stricter than the recipe's 2.5. Every bridge is railed on both sides. Hub pads and
  viewpoints near a drop get parapets (the Aurora Landing pinnacle has a full perimeter parapet). Every pad keeps ≥ 11 studs of
  snow apron to the cliff edge, so no hole edge sits on a drop.
- **Gaps in holes (H3, H17)**: a player-only guard (collision group *PlayerGuard*, 4 high) runs along both gap rims and both sides of
  any rail-less ball bridge, so the ball passes but the player can't. A railed 4-wide walk-on ice deck runs beside the safe ball
  bridge so the player can follow the ball. Ball misses respawn at the gap edge (+1).
- **The void**: no terrain below y 30. Any character below y 40 is faded out and placed on the last tee-teleport pad, with no fall
  animation. A ball below y 40 resets by the hole's hazard rule (+1).
- **Head clearance**: nothing hangs lower than **8 studs** (2.4 m) over any felt or walkway (validated against backdrop pieces,
  overhead walkways, the gondola cabin and lantern posts). The Halo Arch opening is 18 clear. Moving obstacles are the only exception and stay below 4 studs.
- **Moon not in your eyes**: no tee plays within 45° of the moon (bearing 220). Tees play N, NE, E or W (W is 50° off; validated per hole).
- **Big drops are framed, not looked down into from a tee**: the cloud sea is seen from railed bridges and lifts. The in-hole drop (H15) is 4 studs, with felt arrows.
- **Flags**: 7.5-stud poles on every cup. H2's burrows may hide the flag by design; give it a lantern cue over the green.

## Build notes for the builder

- Place holes with `holeRoot = CFrame.new(origin) * CFrame.Angles(0, math.rad(yaw_deg), 0)` from world.json (check: yaw 90 turns
  local -Z to world -X). Build collision straight from holes.json once it exists (invisible, Anchored, CanCollide; felt `center` = top surface).
- Terrain: `world/README.md` (heightmap mapping, void rule, terrain job list). Build **no voxels below y 30**. Hang the
  `island_underside` meshes under each island and lay the cloud deck at y 36.
- Railings: every segment with `rails` in world.json, 3.5 high with a solid lower board. Bridges are railed on both sides.
- Movers (H5, H11, H12, H13, H14, H17): colliders must be **CanCollide and moved every frame** (CFrame per Heartbeat or a constraint),
  following the holes.json motion profiles including dwell. H17's bridge collider exists only while the bridge is fully solid.
- Ice felt (H4): get the friction value calibrated in Studio first (fire a fixed putt, measure roll distance), then feed it to the sim.
- Stroke timeout safety net 20 s; stroke cap 8.
