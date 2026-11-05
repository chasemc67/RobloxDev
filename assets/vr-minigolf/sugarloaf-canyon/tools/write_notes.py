#!/usr/bin/env python3
"""Writes hNN-notes.md from holes.json + final sim results (+ timing check) + the hand-written design text below.
Adapted from Lantern Grove.   python3 tools/write_notes.py <sim tag> [--timing tools/out/timing-<tag>.json] [hole numbers...]"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sim as S
ROOT = os.path.normpath(os.path.join(HERE, ".."))
M = 0.3  # m per stud
STYLE = ("candy-striped sunset desert canyon, pink and cream banded sandstone, rock-candy crystals, lollipop saguaros, warm golden "
         "low sun from the west, lilac haze, chunky whimsical Roblox-friendly shapes, no text")

TEXT = {
"h01": dict(
 landmark="A candy-striped timber **trailhead arch** spans the lane with a swirl-lollipop sign; at the far end a big pink-and-cream striped "
          "**boulder** sits in the back-left corner of the green, its flat south-east face turned 45° to the lane.",
 shots="1. Roll straight up the 7-wide lane into the boulder's 45° face: it turns the ball east along the back of the offset green.\n"
       "2. The cup sits off that line toward the front of the green, so the second putt comes back toward you (two-putt par).",
 challenge="Teaches the bank. Pace matters more than line: too soft and the ball dies on the face, too firm and it runs the length of the green "
           "into the east rail. The ace needs a slightly angled tee shot so the bank sends the ball back toward the cup.",
 props="Trailhead arch 9.5x10x1.2 with lollipop sign (P1); striped boulder dressing over the 3x3 bumper turned 45°, visual up to 6 tall, must cover "
       "the collider at felt level (P1); lollipop saguaro 4x12x4 (P2); hitching post + trough (P3); flag 7.5 (P1).",
 prompt="First-person VR view from a mini golf tee at eye height on a sandy canyon floor: a straight emerald felt lane with pink sandstone "
        "rails runs under a candy-striped timber trailhead arch hung with a giant swirl lollipop sign, toward a huge pink-and-cream striped "
        "boulder in the far left corner and a green that opens to the right with a red flag. Old Sugarloaf, a striped dome, on the skyline."),
"h02": dict(
 landmark="A candy-striped **mine headframe** stands over a striped rock face with three timbered tunnel portals: a tight 2-wide one on the left, "
          "a 4-wide middle one with a 'DEAD END - NO GOLD' plank (its floor climbs 1.2 to a back wall, so the ball comes back), and a long 4-wide one on the right.",
 shots="**Birdie line (left tunnel):** a firm tee shot angled into the 2-wide left tunnel; it runs 18 studs and drops out onto the green, "
       "straight at the cup by the tunnel exit.\n**Safe line (right tunnel):** into the right tunnel, up its 32 studs to the crossover, then a 17-stud "
       "putt across the green.\nThe middle tunnel always spits the ball back into the plaza.",
 challenge="Route choice. The left tunnel is tight and only fair from a good angle, the right one is reliable but costs a stroke, and the dead end "
           "punishes anyone who just aims straight. Signs and felt arrows mark each portal.",
 props="Mine headframe 8x16x6 with pulley wheel (P1); striped rock face with 3 portals (P1); plank signs x3 (P1); ore carts x2 on a rail spur (P2); "
       "miner's lanterns in the right tunnel (P2); felt arrow decals x2 (P1); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at an old candy-striped mine: the felt lane opens into a small plaza facing a "
        "banded pink rock face with three timber tunnel mouths, a narrow one on the left, a middle one with a 'dead end' plank, a wide one on the "
        "right, under a red-and-white striped mine headframe. Ore carts full of pink rock candy, lanterns, warm sunset light."),
"h03": dict(
 landmark="The **ranger station** on stilts with a fire-lookout cupola watches over the turquoise Sugarloaf River. Two crossings: a rail-less peeled "
          "**log plank** straight from the tee, and the railed **ranger footbridge** off to the west.",
 shots="**Risky line:** straight down the 2-wide rail-less plank, 22 studs over the river, to the north bank and the cup (a 55-stud max-power putt "
       "can ace it).\n**Safe line:** to the footbridge mouth, across the railed bridge, then two putts on the north bank.",
 challenge="Nerve and line. A ball that falls off the plank costs a stroke and **reappears at rest on the glowing marker stone at the plank entry** "
           "(not back at the tee). The footbridge is a sure par.",
 props="Ranger station + lookout cupola 10x18x10 (P1, world dressing); peeled-log plank 2.6x1.2x22 (P1); railed footbridge with rope railings "
       "6x3x22 (P1); respawn marker stone flush in the felt (P1); signs x2 (P1); river rocks, canoe (P3); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee on a riverbank in a candy-striped canyon at sunset: a narrow rail-less log "
        "bridge runs straight across a clear turquoise river to a green with a red flag; to the left a railed timber footbridge with rope railings; "
        "a ranger station on stilts with a lookout cupola; Old Sugarloaf beyond."),
"h04": dict(
 landmark="A giant cracked-open **pink geode** glows in the west wall of Rock Candy Narrows; five flat-faced rock-candy crystal clusters stand in the "
          "12-wide slot as pinball bumpers.",
 shots="1. Read the crystal faces: a firm tee shot off the first crystals pings the ball down the slot (bumper restitution 0.65).\n"
       "2. The cup is tucked in the far right corner, off the natural exit line of the crystals: usually a second putt.",
 challenge="Angles. The crystals turn a straight shot unpredictably; good players pick the line that comes off two faces toward the cup corner.",
 props="Rock-candy crystal clusters x5 (glass, neon core) dressing the bumper bases (P1); giant geode in the slot wall (P1, landmark); "
       "slot-wall crystal sprinkles (P2); flag 7.5 (P1).",
 prompt="First-person VR view at eye height in a narrow slot canyon: tall smooth pink-and-cream banded walls, a ribbon of rose sky above, a green felt "
        "corridor dotted with glowing pink and amber rock-candy crystal clusters, a huge glowing geode in the left wall, a red flag at the far end."),
"h05": dict(
 landmark="Wave-carved **Echo Slot**: smooth pink-and-cream walls curve around an S-bend half-pipe channel whose felt banks rise either side.",
 shots="1. Tee shot into the first (right-hand) bend, riding the outside bank round.\n2. Up the middle straight and round the second (left-hand) bend.\n"
       "3. Out of the channel mouth onto the green.\nA perfect max-power tee shot rides both banks and carries to the cup.",
 challenge="Ride the banks: pace decides how high the ball rides and where it leaves each bend. The slot walls hide the flag from the tee by design: "
           "a glowing rock-candy crystal hangs 9.5 studs over the cup as the cue.",
 props="Wave-carved slot-wall dressing hugging the channel (P1, landmark); rounded sandstone lips on the half-pipe rails (P1); hanging crystal cue "
       "over the cup, no collision (P1); flag 7.5 (P1).",
 prompt="First-person VR view at eye height in a deep slot canyon: a green felt half-pipe channel with gently banked sides curves right, then left, "
        "between wave-smoothed pink and cream sandstone walls; a glowing pink crystal hangs on a rope far ahead over the hidden cup; soft bounce light."),
"h06": dict(
 landmark="An old timber **sluice gate** with peppermint bands and a hand-wheel winch slides across the slot neck; a little **flood-warning bell tower** "
          "stands on the rock beside it.",
 shots="**Timing line:** tee shot through the 6-wide neck while the gate is open (it pauses open 2.0 s, closed 1.5 s), into the green: birdie chance.\n"
       "**Safe line:** from the basin into the east overflow channel, up its 21 studs to the crossover, then putt: a sure par.",
 challenge="First timing obstacle, slow and readable. The gate's pointed ends never bat a ball along its track (Lantern Grove lesson).",
 props="Sluice gate board 7x1.2x0.6 with pointed ends (moving mesh, pivot = gate centre at offset 0) (P1); gate frame posts + beam (P1); bell tower "
       "3x9x3 (P1); overflow arrow sign + felt arrow (P1); flood marks sign (P3); flag 7.5 (P1).",
 prompt="First-person VR view at eye height in a slot canyon: a felt lane widens into a basin, then narrows to a neck crossed by a sliding timber "
        "sluice gate with red-and-white stripes and a big winch wheel; a tiny bell tower on the rock; an overflow channel curving off to the right."),
"h07": dict(
 landmark="**Taffy Gap**: two rope bridges with plank decks cross a 30-stud striped chasm, with a hoodoo island between them.",
 shots="**Normal play:** 1) across bridge 1 to the island; 2) from the island through bridge 2 onto the far green; 3-4) putt.\n"
       "**Ace line:** a near-max-power putt threads both bridges in one straight line (the bridges are offset so only a 0.3°-wide line runs clean).",
 challenge="Long and committed. The island's ends are open to the gap: a ball that falls in **respawns at rest on the island marker stone** (+1).",
 props="Rope bridges x2 (plank deck, rope hand-lines, posts) (P1, landmark); island hoodoo with gumdrop cap (P2); island respawn marker (P1); "
       "crumbly lip trim on the open island ends (P2); flag 7.5 (P1).",
 prompt="First-person VR view at eye height on a candy-striped mesa top at sunset: a felt lane runs to a narrow rope bridge over a deep striped "
        "chasm, a small rock island with a hoodoo, a second rope bridge beyond and a green with a red flag on the far rim; big open sky."),
"h08": dict(
 landmark="Car-sized sugar-dusted **gumdrops** in cherry, lemon and lime line Gumdrop Gulch; two smaller ones guard the green.",
 shots="1. Pace the tee shot over the four humps (short gumdrop bumps: each rises 0.12 over a 0.3-stud ramp and drops back over 0.3, with 9.87-stud level floors between) and onto the green.\n2. Putt round the gumdrops to the cup.",
 challenge="Pace control: too soft settles on a level floor between humps (every rest is on level ground: ramps are 0.4 slope, floors 0), too firm runs through the green. Aces need exactly the right pace from the tee.",
 props="Big gumdrop boulders (P2); 2 gumdrop dressings over the 1.8 bumpers (P1, landmark); taffy-striped rail trim following the humps (P2); flag 7.5 (P1).",
 prompt="First-person VR view at eye height on a sunny mesa top: a felt lane rolls over four gentle humps like a ribbon of taffy toward a green "
        "guarded by giant sugar-dusted gumdrops in cherry, lemon and lime, a red flag beyond; candy-striped mesas all around."),
"h09": dict(
 landmark="A prospector's **windpump** on a timber pump house turns three swirl-lollipop vanes across the pump-house tunnel mouth; a striped water tank stands by the green.",
 shots="**Timing line:** tee shot through the 2.4-wide pump-house tunnel between vanes (a vane blocks about a third of the time), out onto the green.\n"
       "**Safe line:** east along the approach into the bypass round the back of the pump house, then a long putt.",
 challenge="Second timing obstacle, a different motion (vertical rotor). Good players time the vanes; the bypass costs about a stroke.",
 props="Windpump wheel with 3 lollipop vanes (moving mesh, pivot = hub, axis +Z) (P1); pump house with tunnel (P1, landmark); water tank (P2); "
       "bypass sign + felt arrow (P1); flag 7.5 (P1).",
 prompt="First-person VR view at eye height on a mesa top: a felt lane leads to a timber pump house whose windpump wheel of giant swirl lollipops "
        "turns slowly in front of a small tunnel; a path curves round the back; a striped water tank and a red flag beyond."),
"h10": dict(
 landmark="A timber **sluice flume** with peppermint-striped gate frames drops the ball 3.6 studs down a 16-long chute into a spillway basin; the Peppermint Dam rises beyond.",
 shots="1. Roll into the chute mouth: the ball accelerates down the chute into the basin and climbs its back slope.\n2. Putt to the cup on the right side of the basin.",
 challenge="One-way: big glowing chevrons on the chute and a 'ONE WAY' felt arrow on the deck show the ball won't come back. Pace into the chute "
           "barely matters; where it comes off the back slope does.",
 props="Sluice flume casing 5x4x16 with striped gate frames and a sheet of water beside the felt (P1, landmark); chute chevrons x4 + deck arrow (P1); "
       "basin back wall (P2); flag 7.5 (P1).",
 prompt="First-person VR view at eye height on a high bench beside a peppermint-striped dam: a short felt deck tips into a steep timber sluice "
        "chute with glowing chevrons, dropping into a round basin green with a red flag; the reservoir and the dam's spillway falls beyond."),
"h11": dict(
 landmark="A canal **lock** of peppermint concrete with brass winches, a lock-keeper's hut and a red/green signal lamp lifts the ball 4 studs onto the quay.",
 shots="1. Roll into the lock chamber while the gate is down (it is open 5.5 s, closed 2.8 s while the platform rides). The platform lifts the ball and "
       "the sluice rush pushes it out along the quay at half its entry speed (1.5-7 studs/s).\n2. Putt on the upper green.\n"
       "Ace: a firm entry sends the ball out fast enough to roll the 16 studs to the cup.",
 challenge="Timing the gate (the green lamp is the cue) and choosing the entry pace, which sets the exit roll.",
 props="Lock chamber walls + timber raft platform (moving, rises 4) (P1); lock gate leaf 3.6x1.2x0.5 (moving, sinks into a slot) (P1); winch posts (P1); "
       "lock-keeper's hut (P1, landmark); signal lamp (P1); felt arrow (P1); flag 7.5 (P1).",
 prompt="First-person VR view at eye height on a reservoir bench: a felt lane funnels into a small canal lock of red-and-white striped concrete "
        "with brass winches and a lock gate; above it a quay and an upper green with a red flag; a lock-keeper's hut with a striped gauge."),
"h12": dict(
 landmark="A domed peppermint **intake tower** stands in Sugarloaf Reservoir beside a rail-less timber pier with a glowing brass intake grate.",
 shots="**Shortcut:** 1) putt along the pier and sink the ball in the intake grate 2 studs from the open end (r 0.3); it shoots out of the outflow pipe "
       "on the green aimed at the cup. 2) putt.\n**Shoreline route:** 1) into the shoreline channel, 2) up it to the green, 3-4) putt across.",
 challenge="Risk/reward: overshoot the pier and the ball goes in the reservoir (+1, back to the stroke start). The shoreline is the reliable par.",
 props="Intake tower 7x16x7 (P1, landmark); timber pier without rails (P1); brass grate with lime glow ring (P1); outflow pipe mouth (P1); signs x2 + "
       "felt arrows x2 (P1); flag 7.5 (P1).",
 prompt="First-person VR view at eye height on a reservoir shore at sunset: a felt lane leads onto a narrow rail-less timber pier ending at a glowing "
        "brass grate, a domed red-and-white intake tower standing in turquoise water; a channel follows the shoreline to a green with a red flag."),
"h13": dict(
 landmark="A cluster of striped **hoodoo spires** with balanced gumdrop caps; low banded rock walls split the maze into three corridors.",
 shots="**Centre (birdie/ace):** straight through the 4-wide centre corridor past two staggered hoodoos onto the green.\n"
       "**West (safe):** into the west corridor, up it past one hoodoo onto the green, then putt across.\n**East:** the scenic route, ending far from the cup.",
 challenge="Line through the hoodoos. A gumdrop-glass lantern hangs over the cup as the cue where hoodoos hide the flag.",
 props="Hoodoo spires x5 over the bumper bases (P1); banded maze rock walls (P1, landmark); lantern cue, no collision (P1); signs x3 (P1); flag 7.5 (P1).",
 prompt="First-person VR view at eye height on a high bench among striped hoodoo spires topped with giant gumdrops: three felt corridors between "
        "low banded rock walls, the middle one dotted with hoodoos, a gumdrop lantern hanging over a hidden cup ahead."),
"h14": dict(
 landmark="A timber **cableway trestle** swings a riveted ore bucket heaped with rock candy across the lane; a ramp climbs to a raised loading-dock green.",
 shots="**Timing line:** straight at the flag under the bucket (it stops about a third of direct shots), up the 0.8 ramp, two putts.\n"
       "**Safe line:** down the right side of the 8-wide lane, clear of the bucket's reach, then up the ramp.",
 challenge="Pendulum timing, Lantern Grove-tuned: a small ±11° swing with a collider foot square to the shot line, so it stops balls instead of kicking them.",
 props="Cableway trestle with hanger (P1, landmark); ore bucket 1.8x2x1.8 (moving mesh, pivot at the hinge) with a base skid plate matching the "
       "1.0x0.4x1.6 collider foot (P1); loading-dock ramp (P2); ore piles (P3); flag 7.5 (P1).",
 prompt="First-person VR view at eye height on a high bench under an old timber cableway: an ore bucket full of pink rock candy swings slowly across "
        "a felt lane, beyond it a short ramp to a raised loading-dock green with a red flag; striped hoodoos and the Crown cliffs."),
"h15": dict(
 landmark="A powdered-sugar **dune** whose felt face tilts across the line toward the east-north-east, with sand-sled tracks and a striped sled on the lip.",
 shots="1. Drop off the lane lip onto the dune face, aimed well uphill (west): the slope curls the ball east and slightly downhill toward the green.\n"
       "2. Off the dune's lower edge onto the two-tier green; putt down to the cup on the lower tier.",
 challenge="Reading a side slope. Wind-ripple chevrons in the felt show the fall line; chevrons at the lip say the face is one-way.",
 props="Sugar-dune dressing and sled (P1, landmark); felt fall-line chevrons and lip chevrons (P1); dune cliff skirt over the green (P2); tier lip (P2); flag 7.5 (P1).",
 prompt="First-person VR view at eye height at the top of a powdered-sugar dune: the felt drops onto a broad face tilted to the right with sled tracks, "
        "curving down to a two-tier green with a red flag; striped hoodoos and the Crown mesa beyond, golden low sun from the left."),
"h16": dict(
 landmark="A crystal-lined **sinkhole** in the sandstone deck, glowing pink, with a rope railing; the funnel bowl green lies 3.6 studs below.",
 shots="1. Putt into the 2.4x2.4 sinkhole: the ball drops into the bowl under the deck and rolls out north.\n2. Putt in the funnel bowl.",
 challenge="Pace through the drop: the ball keeps 80% of its speed, and the bowl's side slopes gather it toward the centre line.",
 props="Sinkhole rim with crystals (P1, landmark); deck slab over the bowl's south end (P1); felt arrow (P1); bowl rim crystals (P2); flag 7.5 (P1).",
 prompt="First-person VR view at eye height on the top of a mesa: a short felt deck with a glowing crystal-lined hole in it, rope railing round the "
        "deck, and below beyond the deck edge a sunken bowl green with a red flag; panorama of striped mesas at sunset."),
"h17": dict(
 landmark="A giant stone **sundial**: a candy-striped gnomon at the centre of an octagonal green ringed by candy-coloured hour stones; two slate shadow arms sweep round it.",
 shots="1. Tee shot round the gnomon past the sweeping arms (20°/s) toward the far side of the dial.\n2. Putt to the cup behind the gnomon.",
 challenge="Horizontal sweeper: pick the side and the moment. The arms are slow and low (0.9 tall).",
 props="Gnomon fin 9 tall (P1, landmark); shadow-arm meshes (moving, pivot dial centre, axis +Y) (P1); hour stones x12 (P2); flag 7.5 (P1).",
 prompt="First-person VR view at eye height on the summit plateau: a felt lane opens onto a large octagonal sundial green with a tall striped gnomon "
        "and two slate shadow arms slowly sweeping round, candy-coloured hour stones on the rim, a red flag behind the gnomon, the sunset to the left."),
"h18": dict(
 landmark="A natural candy-striped **arch** spans the ramp, framing the sunset; a twin **geode** shortcut glows on the plateau; the cliff-edge green looks "
          "over the whole canyon.",
 shots="1. Play round the hoodoo at the end of the tee lane into the banked NE corner, west past the junction into the banked NW corner and up the ramp under the arch.\n"
       "2. From the plateau: into the geode (it pops out by the cup) for a birdie try, or up the rim lane.\n3-4. Putt on the cliff-edge green.\n"
       "Ace: a full tee shot that rides both banks and the ramp straight into the geode.",
 challenge="The finale strings the course together: bank, climb, shortcut or safe route. The geode exit uses 0.7 times entry speed, clamped to 1.5–7 studs/s: only a "
           "ball arriving fast holes out, a gentle plateau putt leaves a tap-in.",
 props="Natural arch over the ramp (P1, landmark); hoodoo with gumdrop cap (P1); geode entry + exit (P1); cliff-edge rope railing (P1); rim sign (P1); "
       "felt arrow (P1); flag 7.5 (P1). The big Sunset Arch backdrop is world dressing.",
 prompt="First-person VR view at eye height on the highest mesa at sunset: a felt lane with a striped hoodoo ahead, banked corners leading to a ramp "
        "under a natural candy-striped stone arch, a glowing violet geode on the plateau beyond, a cliff-edge green with a red flag and the whole canyon below."),
}



def design_text(h):
    """Keep narrative dimensions synchronized with generated authoring geometry."""
    t = dict(TEXT[h["id"]])
    n = h["number"]
    felt = {p["id"]: p for p in h["felt"]}
    movers = h.get("moving_parts", [])
    if n == 2:
        left, right, mid = (felt[k] for k in ("left_tunnel", "right_tunnel", "mid_tunnel"))
        t.update(landmark=f"Candy-striped mine headframe and three portals: open-top left shortcut {left['size'][0]:g} studs wide, gentle middle dead end, and right route {right['size'][1]:g} studs long.",
                 shots="Choose the open-top left shortcut for the short line, or the signed right route and crossover. The middle dead end gently returns the ball to the plaza.",
                 challenge=f"Route choice with clear sightlines. Middle floor rise {abs(mid['slope']['rise']):g}; right-route lanterns keep at least 8 studs of head clearance.",
                 props="Open-top left channel with roof only at the portals; timber portals, mine headframe, elevated lanterns, route signs and felt arrows. Use exact anchors below.")
        t['prompt'] = "Eye-height VR view of a candy-striped mine with three timber portals, an open-top shortcut on the left, a gentle dead-end route and lanterns high above the right route; clear view of the ball."
    elif n == 4:
        t['shots'] = "1. Read the crystal faces and bank into the corridor. 2. Approach the offset cup corner. 3. Finish the putt. A precise bank can beat par."
        t['challenge'] = f"Par {h['par']}: reading crystal-face angles and controlling the exit pace."
    elif n == 6:
        m = movers[0]
        t['shots'] = "Time the signed central gate opening, or use the east overflow route. The exact gate dwell times and collision pockets are listed below."
        t['props'] = f"Sliding gate main body {m['blockers'][0]['size']} plus its exact end-cap blockers listed below; authored rail/rock pocket, frame, bell tower, overflow sign and arrows. Keep all listed cut clearances."
    elif n == 7:
        t['landmark'] = "Two rope-trim bridges with solid 3.5-stud parapets and opaque side skirts cross Taffy Gap via a hoodoo island. A shallow visual floor and mist hide the deep chasm."
        t['props'] = "Solid parapets and skirts on both bridges, opaque gap floor/mist, four optional player teleport pads, island hoodoo and respawn marker. Exact boxes and pads are listed below."
        t['prompt'] = "Eye-height VR view of candy-striped canyon bridges with tall solid parapets and opaque skirts, a hoodoo island, clear teleport pads and soft mist over a shallow visible floor; felt paths and a red flag ahead."
    elif n == 9:
        m = movers[0]
        count = len({round(b.get('roll', 0) % 360, 3) for b in m['blockers']})
        t['landmark'] = f"A prospector's windpump turns {count} broad swirl-lollipop vanes across its tunnel mouth."
        t['shots'] = "Time the central tunnel shot between vanes, or follow the signed east bypass around the pump house. Measured stop rates appear below."
        t['props'] = f"Windpump with {count} clipped-tip vane assemblies, pivot {m['pivot']}, speed {m['speed']:g} degrees/s; exact collider boxes below. Pump house, tank and bypass signs."
    elif n == 11:
        top = next(m for m in movers if m["id"] == "lock_lift_deck")["schedule"]["release"]
        t['shots'] = f"Roll onto the moving lock deck while the entry gate is down. The deck carries its own felt and collision, rises to the quay, and releases the ball during the fully raised interval. The level top dwell lasts {top[1]-top[0]:g} s. The widened 11-stud return lane and 15-stud-long broad approach provide room for blocked-shot re-putts. The striped quay lip opens 0.1 s before top arrival and closes 0.1 s after descent starts (exact windows below). Then putt to the cup."
        t['props'] = "Moving lock deck with carried felt, slotted gate and relieved static rails, plus an interlocked red/cream striped quay lip. Use the exact mover profiles and collision-cut boxes below; no static felt bridges the moving chamber."
    elif n == 14:
        m = movers[0]
        t['shots'] = "Time the central line under the bucket, or choose the intentionally signposted SAFE BANK along the west rail outside the bucket; the right edge is another safe option. The legacy 256.5-degree ace bypass is intentional."
        t['challenge'] = f"Pendulum timing with a square collision foot; swing ±{m['amplitude_deg']:g} degrees, period {m['period_s']:g}s. Stops and deflections are measured below."
        t['props'] = f"Bucket {m['blockers'][0]['size']}, matching skid-foot {m['blockers'][1]['size']}, pivot {m['pivot']}; trestle, SAFE BANK sign and route arrows. See exact blocker offsets below."
    elif n == 17:
        m = movers[0]
        exclusion = h.get('rest_exclusion', {})
        t['landmark'] = f"A stone sundial with {len(m['blockers'])} moving shadow-arm collision boxes around pivot {m['pivot']}; centre exclusion: {exclusion.get('method', 'see exact geometry')}."
        t['shots'] = f"Choose the side and time the shadow arms at {m['speed']:g} degrees/s, then putt to the cup. Follow the playable route around the centre exclusion."
        slopes = [{k:p.get(k) for k in ('id','center','size','slope')} for p in h['felt'] if p.get('slope')]
        t['challenge'] = "The centre must not retain a resting ball within 7 studs. Current sloped felt (empty means flat): " + json.dumps(slopes, separators=(',', ':')) + ". See phase and rest-audit evidence below."
        t['props'] = "Gnomon dressing, moving shadow arms sized exactly to the listed collision boxes, hour stones and flag; preserve the authored centre exclusion and playable ring."
        t['prompt'] = "Eye-height VR view of a candy-striped stone sundial, moving slate shadow arms, a sandstone centre plinth excluding the central disk from play, colourful hour stones and a red flag; warm western golden-hour light."
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
        if m["type"] in ("lift", "quay_lip"):
            out.append(f"- **{m['id']}** ({m['type']}): {m.get('visual', '')} Exact moving profile (felt centres hole-local, blocker centres relative to pivot):\n\n```json\n" + json.dumps(m, indent=2) + "\n```\n")
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
        if t.get("ride"):
            line += f" Ride: {t['ride']['motion']} (platform: {t['ride']['platform']}; lock cycle {t['ride']['cycle_s']} s)."
        out.append(line)
        if t.get("ride", {}).get("gate_sill_retention"):
            out += ["", "**Required engine retention contract:** " + t["ride"]["capture"], "", "```json", json.dumps(t["ride"]["gate_sill_retention"], indent=2), "```", "The Python lift advances to scheduled release; passive geometry alone is not certified without this retainer.", ""]
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
