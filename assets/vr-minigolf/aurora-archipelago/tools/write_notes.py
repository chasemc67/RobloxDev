#!/usr/bin/env python3
"""Writes hNN-notes.md from holes.json + final sim results (+ timing check) + the hand-written design text below.
Adapted from Sugarloaf Canyon / Lantern Grove for Aurora Archipelago.   python3 tools/write_notes.py <sim tag> [--timing tools/out/timing-<tag>.json] [hole numbers...]"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sim as S
ROOT = os.path.normpath(os.path.join(HERE, ".."))
M = 0.3  # m per stud
STYLE = ("stylised 3D storybook render matching the Aurora Archipelago menu card: floating snow-capped slate-violet rock islands over a soft "
         "lilac cloud sea at night, thick rounded moonlit snow, translucent glowing glacier-cyan ice and crystal clusters, warm brass lanterns "
         "on chunky snow-capped timber posts, snowy blue-green pines, bright green felt with a white ball and a red flag, green and violet "
         "aurora ribbons across a starry indigo sky, the Starfrost Spire glowing on the skyline, soft bloom, cosy and whimsical, chunky "
         "Roblox-friendly shapes, no text, no UI")

TEXT = {
"h01": dict(
 landmark="A big brass **harbour lantern** on a frosted driftwood post glows beside the lane at Lantern Quay; at the far end a chunky snow-capped "
          "slate **boulder** sits in the back-left corner of the green, its flat south-east face turned 45° to the lane. The Starfrost Spire "
          "rises straight ahead.",
 shots="1. Roll straight up the 7-wide quay lane into the boulder's 45° face: it turns the ball east along the back of the offset green.\n"
       "2. The cup sits off that line toward the front of the green, so the second putt comes back toward you (two-putt par).",
 challenge="Teaches the bank. Pace matters more than line: too soft and the ball dies on the face, too firm and it runs the length of the green "
           "into the east rail. The ace needs a slightly angled tee shot so the bank sends the ball back toward the cup.",
 props="Harbour lantern on a 9-stud driftwood post (P1, landmark); snow-capped boulder over the 3x3 bumper turned 45° (visual up to 5 tall, must "
       "cover the collider at felt level) (P1); mooring bollards (P2); snowpuff trio (P2); flag 7.5 (P1).",
 prompt="First-person VR view from a mini golf tee at eye height on a snowy harbour quay at night: a straight green felt lane with chunky "
        "snow-capped timber rails runs past a big glowing brass harbour lantern on a driftwood post toward a huge snow-capped slate boulder in the "
        "far left corner, where the green opens to the right with a red flag; three round snowpuffs watch from a drift; the giant glowing "
        "Starfrost Spire rises dead ahead over the lilac cloud sea."),
"h02": dict(
 landmark="The **Snowpuff Rookery**: a long rounded snow drift with three round burrow mouths under frosted ice-arch lintels, snowpuffs peeking out "
          "of little side holes and sliding down its back.",
 shots="**Birdie line (left burrow):** a firm tee shot angled into the 3-wide open-top left burrow; it runs 18 studs and pops out on the green near "
       "the cup.\n**Safe line (right burrow):** into the right burrow, up its length to the crossover, then a long putt across the green.\n"
       "The middle burrow is a dead end whose floor rises 0.6: it always rolls the ball back into the plaza.",
 challenge="Route choice. The left burrow is tight and only fair from a good angle, the right one is reliable but costs a stroke, and the dead end "
           "punishes anyone who just aims straight. Signs and felt arrows mark each mouth; a brass lantern hangs 9 studs over the cup as the "
           "cue when the drift hides the flag.",
 props="Rookery drift with three burrow mouths, open-topped cuts (P1, landmark); frosted ice-arch lintels x3, underside y 8 (P1); route signs x2 + "
       "felt arrows x2 + roll-back chevrons (P1); lantern cue over the cup (P1); burrow lanterns (P2); snowpuffs (P2); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at a snowpuff rookery at night: the felt lane opens into a small plaza facing a "
        "long rounded snow drift with three round burrow mouths under glowing ice arches, a narrow one on the left, a middle one with a "
        "'dead end' plank, a wide one on the right; dozens of round penguin-puffin snowpuffs in knitted scarves peek out of the drift; a brass "
        "lantern glows over the hidden green beyond."),
"h03": dict(
 landmark="**Glimmer Islet** floats just east of the hole with its crystal cluster and the Glimmer Icefall pouring into the clouds. The hole "
          "crosses the open-sky **Glimmer Gap**: a rail-less glowing ice plank straight from the tee, or the railed ice bridge to the right "
          "with a railed walk-on deck beside it.",
 shots="**Risky line:** straight down the 2-wide rail-less plank, 26 studs over open sky, to the north island and the cup.\n**Safe line:** to "
       "the ice-bridge mouth on the right, across the railed bridge, then two putts on the north green.",
 challenge="Nerve and line. A ball that falls off the plank costs a stroke and **reappears at rest on the glowing marker stone at the plank entry** "
           "(not back at the tee). The ice bridge is a sure par. Player-only guards line both rims and the plank, so nobody walks into the gap.",
 props="Rail-less glowing ice plank 2.4x0.8x26 (P1); railed ice bridge + 4-wide railed player deck (P1); respawn marker stone (P1); route signs "
       "x2 + felt arrows x2 (P1); clear PlayerGuard panels on both rims and plank sides (P1); snowpuff with binoculars (P3); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee on a snowy island edge at night: a narrow rail-less glowing ice plank runs "
        "straight across an open-sky gap high above a lilac cloud sea to a green with a red flag; to the right a railed ice bridge with "
        "snow-capped timber rails and a walkway; a small floating islet with a glowing crystal cluster and a frozen waterfall hangs nearby."),
"h04": dict(
 landmark="Two **frosted palms** lean over a long glassy **ice slide** in the steam of Steamwhistle Lagoon; the snow-felt green waits at the end.",
 shots="1. Stroke the ball gently onto the ice: it barely slows on the glassy strip (about 0.35 x normal rolling deceleration) and glides onto "
       "the snow-felt green.\n2. Putt out on normal felt. A perfectly weighted tee shot can glide all the way to the cup.",
 challenge="Pace control. On ice a 5% power error moves the finish several studs; too hard and the ball runs to the back rail and bounces back, too "
           "soft and it stops on the ice where every putt is touchy. **The ice friction must be calibrated in Studio** (see the physics block).",
 props="Glassy ice felt strip (Glass look, Transparency 0.15, Reflectance 0.15) over a custom-friction collider (P1); frosted palms x2 (P1, "
       "landmark); ice-edge snowflake decal (P1); steam vents (P2); snowpuff on a belly-slide (P3); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at night beside steaming turquoise hot springs: a short felt lane runs onto a "
        "long shiny glassy ice strip that reflects the lantern light and the green and violet aurora, ending at a wide snow-felt green with a "
        "red flag; frosted palm trees dusted with snow lean over the slide; steam curls past brass lanterns."),
"h05": dict(
 landmark="**Steamwhistle Geyser**, a basalt cone beside the upper green, puffs and whistles; at the foot of the 4-stud basalt cliff a hexagonal "
          "**geyser platform** rides a steam column between the basin and the upper green.",
 shots="1. Roll onto the platform while it sits flush with the basin (the signal lamp is green): it holds the ball, rises 4 studs and puffs it out "
       "onto the upper green toward the cup (harder entry, stronger puff).\n2. Putt out on the upper green. If the platform is up, the ball "
       "bounces off its basalt side: wait and go again.",
 challenge="First mover: slow, with a long obvious boarding window. Timing beats power; the exact profile and the puff speed rule are below.",
 props="Moving hexagonal basalt platform with steam-vent dimple, pivot = platform top centre (P1); translucent steam column (P1); Steamwhistle "
       "Geyser cone (P1, landmark); cliff face with brass rivets (P2); green/amber signal lamp (P1); timber steps for the player (P1); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at night on a steaming lagoon island: a felt lane leads to a small basin at the "
        "foot of a 4-stud basalt cliff, where a hexagonal stone platform rises on a white steam column toward an upper green with a red flag; a "
        "basalt geyser cone beside it blasts a tall steam plume into the aurora sky; turquoise hot springs, frosted palms and brass lanterns."),
"h06": dict(
 landmark="**Kettle Lagoon**: a steaming turquoise hot-spring pool cut into the low east edge of a big tilted snow-felt shelf, frosted palms leaning "
          "over it.",
 shots="1. Aim left of the flag: the whole shelf falls gently east toward the pool, so a straight putt curls right.\n2. Read the break on the "
       "second putt too; the cup sits in the middle of the slope.",
 challenge="Slope reading. The shelf falls 0.42 across 29 studs, the steepest plane where a ball can still come to rest, so every putt breaks. "
           "A ball that curls into the pool reappears on the basalt stone beside it (+1).",
 props="Hot-spring pool with basalt rim and steam (P1, landmark); respawn stone (P1); frosted palms x3 (P2); wind-ripple slope chevrons on the "
       "felt (P1); snowpuff foot-bath (P3); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at night: a wide snow-felt green tilts gently to the right toward a steaming "
        "turquoise hot-spring pool with a basalt rim, frosted palms leaning over the water, a red flag in the middle of the slope; snowpuffs "
        "relax in a little steaming foot-bath with towels on their heads; aurora overhead."),
"h07": dict(
 landmark="Candy-bright **coral-ice fans** glow in clumps along a snowy meadow; the lane runs over four rounded snow **moguls**.",
 shots="1. A firm, straight tee shot over the four moguls (each a hump and a hollow of opposing planar slopes) onto the green.\n2. Putt out.",
 challenge="Pace: too soft and the ball settles in a hollow between moguls; too hard and it runs to the back rail. The humps rise +0.5 and dip -0.3.",
 props="Coral-ice fan clumps in candy colours outside both rails (P1, landmark); snow-capped mogul rail trim (P1); toboggan snowpuff (P3); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at night: a felt lane rolls over four rounded snowy humps and hollows toward a "
        "wide green with a red flag; glowing candy-coloured coral made of ice (bubblegum pink, tangerine, mint) lines both sides; a snowpuff "
        "rides a tiny toboggan; aurora and stars above, floating islands in the distance."),
"h08": dict(
 landmark="Giant **coral-ice branches** in bubblegum pink and tangerine glow from inside; seven flat-faced coral bumpers stand in the reef corridor.",
 shots="1. Read the coral faces: a firm tee shot off the first branches pings the ball down the corridor (bumper restitution 0.65).\n"
       "2. The cup is tucked into the green's west side, off the natural exit line: usually a second putt.",
 challenge="Angles. The corals turn a straight shot unpredictably; good players pick the line that comes off two faces toward the cup.",
 props="Coral-ice branch clusters x7 dressing the bumper bases (P1); giant coral tree (P1, landmark); scorekeeper snowpuffs (P3); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at night on a reef island: a wide felt corridor dotted with glowing coral-ice "
        "branches in candy pink, tangerine and mint, a giant glowing coral tree on the left, a red flag on the green beyond; snow on the "
        "rails, brass lanterns, aurora overhead."),
"h09": dict(
 landmark="Two **giant spiral conch shells** of candy coral-ice: one lies at the end of a rail-less reef spit over a shallow turquoise lagoon, "
          "its twin sits on the green's east edge.",
 shots="**Shortcut:** a measured putt down the rail-less spit into the conch ring: the twin conch blows the ball out toward the cup (birdie or "
       "better).\n**Long route:** bank into the reef walk on the west, play up it, then onto the green (par).",
 challenge="Risk and reward: the spit has no rails and a ball in the lagoon goes back to where it was struck (+1).",
 props="Conch pair (entry over the ring; exit aimed at the cup) (P1, landmark); spit deck (P1); reef lagoon with coral heads (P2); route signs + "
       "felt arrows (P1); snorkelling snowpuffs (P3); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at night on a coral reef island: a felt lane leads to a narrow rail-less spit "
        "running out over a shallow glowing turquoise lagoon to a giant pink spiral conch shell; a twin conch sits beside a far green with a "
        "red flag; a railed reef path curves round the left; coral-ice glows under the water."),
"h10": dict(
 landmark="A striped **bobsled start hut** with brass bells stands at the top of an icy S-bend bobsled run of packed snow.",
 shots="1. Tee shot into the first (right-hand) bend, riding the outside bank round.\n2. Up the middle straight and round the second (left-hand) "
       "bend.\n3. Out of the run onto the green. A perfect firm tee shot rides both banks and carries to the cup.",
 challenge="Ride the banks: pace decides how high the ball rides and where it leaves each bend.",
 props="Bobsled start hut with bells (P1, landmark); packed-snow run walls kept low (P1); ice lips on the rails (P1); cheering snowpuff "
       "bobsled teams (P3); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at night: a green felt bobsled channel with banked icy sides curves right, then "
        "left, between rounded packed-snow walls; a striped bobsled start hut with brass bells stands beside the tee; a red flag waits at the "
        "end; snowpuffs cheer with tiny flags; aurora and the frozen Floe Pond beyond."),
"h11": dict(
 landmark="Frozen **Floe Pond** with toy floes frozen in, a snowpuff **ice-fishing hut** puffing from its stove pipe; an ice floe with pointed ends "
          "drifts back and forth across the neck.",
 shots="**Timing line:** tee shot through the 6-wide neck while the floe is parked in its pocket, into the green: birdie chance.\n"
       "**Safe line:** from the pond into the east side channel, up it to the crossover, then putt: a sure par.",
 challenge="Linear slide with dwell, slow and readable. The floe's pointed 45° ends never bat a ball along its track (Lantern Grove lesson).",
 props="Ice floe slab with pointed ends, a snowpuff riding it (moving mesh, pivot = floe centre at offset 0) (P1); marker posts (P2); ice-fishing "
       "hut (P1, landmark); side-channel sign + felt arrow (P1); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at night on a frozen pond shelf: a felt lane widens into a basin, then narrows "
        "to a neck where a chunky ice floe with a snowpuff riding on it drifts sideways across the way; a striped ice-fishing hut puffs smoke "
        "on the bank; a side channel curves off to the right; a red flag beyond."),
"h12": dict(
 landmark="A beached toy **icebreaker** (red hull, cream deckhouse, red funnel) straddles the channel; its red-and-cream **paddle wheel** turns across "
          "the channel on a horizontal axle.",
 shots="**Timing line:** a firm putt through the 2.4-wide channel between paddles: birdie chance.\n**Safe line:** the signed bypass round the "
       "stern, then putt: par.",
 challenge="Vertical rotor: broad paddles with clipped tips; pick the gap or take the bypass.",
 props="Icebreaker hull + deckhouse + funnel (P1, landmark); paddle wheel, 4 paddles r 4.1, pivot = hub, axis +Z (P1); bypass sign + felt arrow "
       "(P1); sailor snowpuffs (P3); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at night on a frozen shelf: a small toy icebreaker boat sits across a felt "
        "channel, its big red-and-cream paddle wheel turning over the felt; a red funnel puffs steam; a bypass lane curves round its stern to a "
        "green with a red flag; snowpuffs in sailor hats on crates."),
"h13": dict(
 landmark="A brass-and-ice **carousel** with a striped canopy and a snowpuff weathervane stands in the middle of a square green; four sled-runner "
          "arms carrying snowpuffs on little sleds sweep round its solid round base.",
 shots="**Timing line:** a tee shot round the base past the sweeping arms to the east-side cup.\n**Safe line:** stop at the marker outside the "
       "sweep, then time a short putt.",
 challenge="Horizontal rotor. The solid base keeps every ball out of the middle (no rests within 7 studs of the hub).",
 props="Carousel canopy (underside y 9) and brass pole (P1, landmark); solid round base r 7.5 (P1); four arm meshes with sled snowpuffs, pivot = "
       "hub (P1); music-box lanterns (P2); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at night on an icy terrace: a square green with a brass-and-ice carousel in the "
        "middle, its striped canopy topped by a snowpuff weathervane, four low arms carrying snowpuffs on little sleds sweeping round over the "
        "felt; a red flag at the far right; the Great Frozen Falls glowing at the terrace edge."),
"h14": dict(
 landmark="A timber **bell gantry** hung with icicles swings a brass **icicle bell** across the lane; a short ramp climbs to a raised green.",
 shots="**Timing line:** straight at the flag under the bell when it swings clear.\n**Safe side:** hug a rail past the bell's touch band, then "
       "up the ramp.",
 challenge="Pendulum, peak 14 °/s; the bell is turned 30° to the swing plane and a square collider foot under its lip makes clean stops.",
 props="Bell gantry with icicles on the beam only (P1, landmark); brass icicle bell with skid plate over the collider foot, pivot at the hinge "
       "(P1); safe-side sign + timing arrow (P1); buoys (P3); hand-bell snowpuffs (P3); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at night on an icy terrace: a timber gantry hung with icicles swings a big brass "
        "bell slowly across the felt lane; beyond it a short ramp climbs to a raised green with a red flag; snowpuffs ring little hand-bells; "
        "the Starfrost Spire glows to the south behind you, aurora ahead."),
"h15": dict(
 landmark="The **Great Frozen Falls** pour 146 studs off the terrace edge into the clouds right beside the basin green; the hole's own lip is a "
          "little frozen fall.",
 shots="1. Putt over the open lip: the ball drops 4 studs into the basin (keeping ~80% of its speed) and rolls toward the cup.\n"
       "2. Tap in. The basin's back slope returns firm shots.",
 challenge="Pace and line over a blind drop; felt chevrons warn it is one-way. A clear ice parapet across the lip keeps players (not balls) back.",
 props="Icicle curtain under the lip (P1); lip parapet, clear ice, PlayerGuard (P1); chevrons x2 (P1); player steps beside the drop (P1); "
       "snowpuff on an ice ledge (P3); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at night on the edge of a terrace: a short felt lane ends at an icicle-fringed "
        "lip with a clear ice parapet, dropping to a basin green below with a red flag; right beside it a huge frozen waterfall pours "
        "off the island edge into the glowing lilac clouds far below; aurora overhead."),
"h16": dict(
 landmark="The **Moonwell**: a moonstone funnel bowl with silver inlay, ringed with glowing ice crystals, draining through a crescent-moon spout.",
 shots="1. Roll into the well: its two slopes gather the ball into the trough and out of the spout.\n2. The cup sits off the spout's line, so it "
       "is usually a short second putt; a ball that leaves the spout angling right can drop.",
 challenge="Funnel with the cup deliberately off the exit line so the funnel doesn't make it an ace machine.",
 props="Moonstone coping and slope dressing (P1, landmark); crystal clusters on the rim (P2); crescent spout glow decal (P1); telescope snowpuff "
       "(P3); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at night on the highest summit island: a round pearly moonstone well funnels "
        "down to a crescent-shaped spout, glowing ice crystals on its rim, a green beyond with a red flag; a snowpuff peers through a brass "
        "telescope; every lower island glitters below in the lilac cloud sea."),
"h17": dict(
 landmark="An **aurora ribbon** pours out of the sky into a glowing **light span** between two crystal piers over the open-sky Aurora Gap; the "
          "fixed ice bridge runs to the right.",
 shots="**Timing line:** straight over the crystal piers and the light span while it glows solid (birdie, ace line).\n**Safe line:** the fixed "
       "railed ice bridge to the right, then two putts.",
 challenge="Appear/vanish toggle: the span's collider only exists while it is fully solid; a ball on it when it dims falls (+1, respawns at the "
           "light-route entry). The crystal lamp glows mint while it is solid.",
 props="Aurora ribbon + light span (Neon, animated mint->violet, toggled collider) (P1, landmark); crystal piers (P1); fixed ice bridge + player "
       "deck (P1); timing lamp (P1); respawn stone (P1); signs + arrows (P1); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at night on a summit island: two glowing crystal piers reach out over an "
        "open-sky gap high above the lilac clouds and are joined by a shimmering green-and-violet aurora ribbon bridge that pours down "
        "from the sky; to the right a railed ice bridge; a green with a red flag beyond."),
"h18": dict(
 landmark="The **Halo Arch**, a translucent glowing ice arch 34 studs tall, spans the raised final green and frames the aurora; the Starfrost Spire "
          "rises to the south-east and every island lies below.",
 shots="1. Tee shot up the lane into the north-east crystal bank: it turns the ball west across the plaza.\n2. The south-west crystal bank turns "
       "it north up the ramp onto the raised green under the arch.\n3. Putt out; the cup sits east of the ramp line.",
 challenge="Finale: read two crystal banks and the 1.2-stud ramp. Grand but not punishing.",
 props="Halo Arch (P1, landmark, world dressing; opening 18 clear); crystal walls over both banks (P1); ramp lanterns (P2); felt arrows + "
       "chevrons (P1); snowpuff grandstand (P2); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at night on the highest summit: a felt lane runs into faceted glowing ice-crystal "
        "bank walls, a ramp climbs to a raised green under a huge translucent glowing ice arch framing the green and violet aurora; a red flag "
        "on the green; snowpuffs in a grandstand of snow blocks; the giant Starfrost Spire glows to the right."),
}


def design_text(h):
    """Keep narrative dimensions synchronized with the generated geometry where they matter."""
    t = dict(TEXT[h["id"]])
    n = h["number"]
    movers = h.get("moving_parts", [])
    if n == 5:
        m = movers[0]; tp = h["teleports"][0]; lf = tp["lift"]
        t["challenge"] = (f"First mover: platform DOWN {m['dwell'][0]['s']:g} s (boarding window), rises 4 at {m['speed']:g} studs/s, UP "
                          f"{m['dwell'][1]['s']:g} s, sinks at {m['speed']:g} studs/s (cycle {lf['cycle_s']:g} s). Puff speed = clamp(entry x "
                          f"{tp['speed_factor']:g}, {tp['min_speed']:g}, {tp['max_speed']:g}) studs/s along the exit line.")
    elif n == 11:
        m = movers[0]
        t["challenge"] = (f"Linear slide with dwell: {m['speed']:g} studs/s, pauses {m['dwell'][0]['s']:g} s blocking and {m['dwell'][1]['s']:g} s "
                          f"parked (cycle {S.cycle_period(m):.2f} s). Pointed 45° ends never bat a ball along the track.")
    elif n == 12:
        m = movers[0]
        t["challenge"] = f"Vertical rotor at {m['speed']:g} °/s: broad paddles with clipped tips; pick the gap or take the bypass."
    elif n == 13:
        m = movers[0]
        t["challenge"] = (f"Horizontal rotor at {m['speed']:g} °/s. The solid base keeps every ball out of the middle (no rests within 7 studs "
                          "of the hub).")
    elif n == 14:
        m = movers[0]
        t["challenge"] = (f"Pendulum ±{m['amplitude_deg']:g}° over {m['period_s']:g} s (peak {m['speed']:.0f} °/s); the bell is turned "
                          f"{m['blockers'][0]['yaw']:g}° to the swing plane and a square collider foot under its lip makes clean stops.")
    elif n == 17:
        m = movers[0]
        p = {q["state"]: q["s"] for q in m["profile"]}
        t["challenge"] = (f"Appear/vanish toggle (cycle {m['period_s']:g} s: fade in {p['fade_in']:g} s, solid {p['solid']:g} s, fade out "
                          f"{p['fade_out']:g} s, gone {p['gone']:g} s). The span's collider only exists while it is fully solid; a ball on it "
                          "when it dims falls (+1, respawns at the light-route entry). The crystal lamp glows mint while it is solid.")
    return t


def exact_metadata(h):
    sections = []
    for key in ('collision_cuts', 'vr_comfort', 'player_teleport_points', 'safe_route', 'vr_clearance', 'rest_exclusion'):
        if h.get(key):
            sections.append(f"### {key} (exact hole-local studs)\n\n```json\n" + json.dumps(h[key], indent=2) + "\n```\n")
    return "\n".join(sections)


def mp_lines(h):
    out = []
    for m in h.get("moving_parts", []):
        if m["type"] == "swing":
            b = m["blockers"][0]
            extra = "".join(f"; blocker {q + 2}: box {c['size']} centred {c['center']}" + (f" yaw {c['yaw']:g}" if c.get("yaw") else "")
                            for q, c in enumerate(m["blockers"][1:]))
            out.append(f"- **{m['id']}** (swing = pendulum): pivot (hinge) {m['pivot']}, axis {m['axis']}, angle(t) = {m['amplitude_deg']}° x "
                       f"sin(360°·t/{m['period_s']} s + {m.get('phase', 0)}°), peak {m['speed']:.0f}°/s. Blocker: box {b['size']} centred {b['center']} "
                       f"from the pivot hanging straight down{extra}. Visual: {m.get('visual', '')}")
            continue
        if m["type"] == "toggle":
            prof = ", ".join(f"{q['state']} {q['s']:g} s" for q in m["profile"])
            out.append(f"- **{m['id']}** (toggle = appear/vanish timed surface): felt {m['felt_ids']}, cycle {m['period_s']:g} s, phase {m['phase_s']:g} s, "
                       f"profile {prof}; collider ONLY in [{m['solid_window'][0]:g}, {m['solid_window'][1]:g}) s of each cycle. {m.get('visual', '')}")
            continue
        unit = m["speed_units"]
        rng = "continuous" if m["range"] is None else f"ping-pong {m['range'][0]}..{m['range'][1]} {'deg' if m['type'] == 'rotate' else 'studs'}"
        bl = "; ".join(f"box {b['size']} at {b['center']}" + (f" yaw {b['yaw']}" if b.get('yaw') else "") +
                       (f" roll {b['roll']}" if b.get('roll') else "") for b in m["blockers"])
        if m.get("dwell"):
            rng += " with pauses " + ", ".join(f"{d['s']:g} s at {d['at']:g}" for d in m["dwell"])
        out.append(f"- **{m['id']}** ({m['type']}): pivot {m['pivot']}, axis {m['axis']}, speed {m['speed']} {unit}, {rng}, "
                   f"phase {m.get('phase', 0)}, cycle {S.cycle_period(m):.2f} s. Blockers (relative to pivot at angle/offset 0): {bl}. "
                   f"Visual: {m.get('visual', '')}")
    for t in h.get("teleports", []):
        trig = (f"rectangle centre {t['entry']['center']} +- {t['entry']['half_size']}" if t["entry"].get("half_size")
                else f"entry {t['entry']['center']} r {t['entry']['radius']}")
        line = (f"- **{'lift' if t.get('kind') == 'lift' else 'teleport'} {t['id']}**: {trig} -> exit {t['exit']['center']} dir {t['exit']['dir']}, "
                f"exit speed = clamp(in x {t['speed_factor']}, {t['min_speed']}, {t['max_speed']}) studs/s. {t.get('visual', '')}")
        if t.get("lift"):
            lf = t["lift"]
            line += (f" Lift schedule: cycle {lf['cycle_s']:g} s, boarding while t mod cycle in [{lf['board'][0]:g}, {lf['board'][1]:g}) s, release "
                     f"at {lf['release_s']:g} s, column = moving part `{lf['column']}`. **Engine contract:** hold (anchor) the ball once its centre is "
                     "on the platform, carry it with the platform, and at the release time set its velocity exactly as above.")
        out.append(line)
    for hz in h.get("hazards", []):
        if hz.get("reset") == "respawn":
            out.append(f"- **hazard {hz['id']}** ({hz['type']}): +{hz['penalty']} stroke, ball placed at rest on the respawn point {hz['respawn']}")
        else:
            out.append(f"- **hazard {hz['id']}** ({hz['type']}): +{hz['penalty']} stroke, ball back to where the stroke started")
    return out or ["- none"]


def main():
    args = sys.argv[1:]
    tag = args.pop(0)
    tim = None
    if "--timing" in args:
        i = args.index("--timing")
        tim = json.load(open(args[i + 1]))
        del args[i:i + 2]
    only = {int(x) for x in args}
    course = json.load(open(os.path.join(ROOT, "holes.json")))
    sim = {h["id"]: h for h in json.load(open(os.path.join(HERE, "out", f"sim-{tag}.json")))["holes"]}
    for h in course["holes"]:
        if only and h["number"] not in only:
            continue
        t = design_text(h)
        s = sim.get(h["id"], {})
        st = s.get("stats", {})
        hs = s.get("hio_search") or {}
        tee, cup = h["tee"]["position"], h["cup"]["position"]
        if hs.get("line"):
            ln = hs["line"]
            a = math.radians(ln["aim_deg"])
            hio = (f"Brute-force search from the tee found ace lines ({hs.get('hits') or hs.get('refine_hits')} grid shots). "
                   f"The most robust: aim **{ln['aim_deg']:.1f}°** (atan2(dz,dx): direction ({math.cos(a):.2f}, {math.sin(a):.2f}) in x/z, "
                   f"i.e. {abs(90 - (ln['aim_deg'] - 180)):.1f}° {'left' if ln['aim_deg'] < 270 else 'right'} of straight -Z), "
                   f"speed **{ln['speed']:.1f} studs/s** ({ln['speed'] / S.V_MAX * 100:.0f}% power)"
                   + (f", start phase t={ln['phase']:.1f}s of the moving parts" if h.get("moving_parts") else "")
                   + ". The red dashed line on the layout PNG traces it.")
        else:
            hio = "No ace line found by the brute-force search."
        fl = h["cup"].get("flag") or {}
        los = s.get("flag_los") or {}
        flag_txt = (f"Flag: {fl.get('pole_height')}-stud pole ({fl.get('pole_diameter')} diameter) in the cup, {fl.get('banner_size')} "
                    f"{fl.get('banner_color')} banner at the top {fl.get('top')}; visual only, no collision. Tee eye (5.5 up) -> flag top: "
                    f"**{'visible' if los.get('visible') else 'blocked by ' + ', '.join(los.get('blocked_by', []))}** "
                    f"(min clearance {los.get('clearance', 0):+.2f} studs)"
                    + (". Moving parts crossing the sightline: " + ", ".join(f"{k} {v * 100:.0f}% of its cycle" for k, v in los.get('moving', {}).items() if v)
                       if any((los.get('moving') or {}).values()) else "") + ".")
        par = h["par"]
        stats = "\n".join(f"| {k} | {v['avg']:.2f} | {v['hio'] * 100:.1f}% | {sum(v['dist'][:par]) / v['n'] * 100:.0f}% | {v['capped'] * 100:.1f}% | "
                          f"{v['escapes']} / {v['timeouts']} | {v['dist']} |" for k, v in st.items())
        timing_txt = ""
        if tim:
            rows = [r for r in tim["results"] if r["hole"] == h["number"]]
            if rows:
                phase_counts = ", ".join(str(n) for n in sorted({r['n'] for r in rows}))
                timing_txt = f"\n## Timing check (`tools/timing_check.py`, {phase_counts} phases; actual fuzz counts per line)\n" + "\n".join(
                    f"- {r['part']} [{r['line']}] {r['desc']}: blocked {r['counts']['blocked']}/{r['n']} ({r['counts']['stops']} stops + "
                    f"{r['counts']['kicks']} kicks), deflected {r['counts']['deflected']}, **Studio estimate {r['est_pct']:g}%** (stops + 0.36 kicks), "
                    f"passed {r['pass_pct']:g}%, traps {r['trap']}" + (f", fuzz {r['fuzz']['n']} shots: timeouts {r['fuzz'].get('timeouts', 0)}, pinned rests {r['fuzz'].get('pinned_rests', 0)}, escapes {r['fuzz'].get('escapes', 0)}, excluded rests {r['fuzz'].get('excluded_rests', 0)}" if r.get('fuzz', {}).get('n') else "")
                    for r in rows) + "\n"
        md = f"""# Hole {h['number']}: {h['name']} (Par {h['par']})

Zone: **{h['zone']}**. Gimmick: **{h['gimmick']}**.
Layout: `h{h['number']:02d}-layout.png`. Geometry: `holes.json` -> holes[{h['number'] - 1}]. World placement (from `world/world.json`): origin {h['world_offset']}, yaw {h.get('world_yaw', 0)}.
Tee {tee}, cup {cup} (radius {h['cup']['radius']}). Units: studs (1 stud = {M} m).

## Landmark
{t['landmark']}

## Gimmick
{h['gimmick']}.

## Intended shots
{t['shots']}

## Hole-in-one line
{hio}

## Challenge
{t['challenge']}

## Moving parts / teleports / hazards (exact specs, also in holes.json)
{chr(10).join(mp_lines(h))}
{timing_txt}
{exact_metadata(h)}
## Flag and sightline
{flag_txt}

## Playtest stats ({tag}; actual plays: {", ".join(f"{k}={v['n']}" for k,v in st.items())})
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
{stats}

## Props for the 3D modeler (decoration only, sizes in studs)
{t['props']}

Decoration anchors (position in hole-local studs):
{chr(10).join(f"- `{a['name']}` at {a['position']}{' (LANDMARK)' if a.get('landmark') else ''}{' size ' + str(a['approx_size']) if a.get('approx_size') else ''}: {a['notes']}" for a in h['decoration_anchors'])}

## Concept prompt
{t['prompt']} Style: {STYLE}.
"""
        open(os.path.join(ROOT, f"h{h['number']:02d}-notes.md"), "w").write(md)
        print("wrote", f"h{h['number']:02d}-notes.md")


if __name__ == "__main__":
    main()
