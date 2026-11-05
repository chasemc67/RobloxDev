#!/usr/bin/env python3
"""Writes hNN-notes.md from holes.json + final sim results + the hand-written design text below.
    python3 tools/write_notes.py <sim tag> [hole numbers...]"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sim as S
ROOT = os.path.normpath(os.path.join(HERE, ".."))
M = 0.3  # m per stud

TEXT = {
"h01": dict(
 landmark="A timber torii-style **Lantern Gate** straddles the ramp: two posts outside the rails, a curved crossbeam ~6 studs (1.8 m) "
          "overhead and two big paper lanterns hanging just above head height in VR. Beyond it a red maple and a mossy boulder frame the green.",
 shots="1. Roll up the lane and the gentle 0.5-stud ramp into the **45° timber deflector** at the back-right of the green. "
       "The board turns the ball west along the back of the green.\n"
       "2. The cup is tucked in the **front-left corner** of the green, behind the corner where the lane rail meets the green. "
       "The second putt comes back toward you, 6–8 studs.",
 challenge="Teaches the course's two basics: pace up a ramp, and reading a bank. The cup sits in the shadow of the lane corner, "
           "so there is no straight putt to it from the tee, but its 7.5-stud flag is visible over the rails. The safe play is a two-putt off the deflector.",
 props="Lantern torii gate 9x7x1.2 (P1); 2 paper lanterns L (P1); welcome sign post 2x3x0.4 (P2); red maple 10x16x10 (P2); "
       "mossy boulder 4x3x4 (P2); deflector plank cladding along the `deflector` wall 10x1x0.5 (P1); leaf piles (P3); flag 7.5 (P1).",
 prompt="First-person VR view from a putting tee at golfer eye height (about 5.5 ft), looking up a short emerald-green mini golf lane "
        "edged by low limestone rails with oak caps. A gentle ramp leads through a carved timber torii gate hung with two glowing "
        "amber paper lanterns, onto a wide raised green. A slanted timber board guards its back-right corner. The red flag is "
        "tucked low at the near-left corner of the green, half-hidden behind the rail corner. Late golden-hour autumn sun through "
        "red maples and golden birches, drifting leaves, a mossy boulder, soft haze, warm cozy fairy-forest storybook style, "
        "Roblox-friendly chunky shapes."),
"h02": dict(
 landmark="A **giant acorn** (3x4x3) sits on an old stump that splits the end of the upper lane into two 2.5-stud chutes. "
          "Below the 1.5-stud (0.45 m) ledge is a wide lower green with a mossy **rabbit hole** on the left.",
 shots="1. Pick a chute. The **left chute** is the aggressive line: a firm putt drops through it and runs diagonally across the lower green "
       "toward the cup in the far right corner. Overcook it and the rabbit hole waits. "
       "The **right chute** is safer: drop through softly and leave a short uphill-free putt.\n"
       "2. Putt out on the flat lower green.",
 challenge="First drop on the course. Players learn that the ball keeps about 80% of its speed after falling, and that the line "
           "changes once it lands. The rabbit hole punishes left-chute shots that are too hard (+1 and replay). Arrow signs and glowing "
           "felt arrows show both chutes from the tee, and the 7.5-stud flag is visible over the ledge.",
 props="Giant acorn 3x4x3 (P1); stump (cladding for `stump` block 3x1.2x1) (P1); lantern posts at both chutes 0.5x3x0.5 (P1); "
       "rabbit-hole rim 3x0.5x3 (P2); squirrel hut on post 3x5x3 (P3); leaf piles (P3); flag 7.5 (P1); **chute signs (new)**: two carved arrow "
       "signs on posts outside the rails at (±5.2, 0, -16.5) 1.8x3.2x0.25 ('Bold Line' left with a rabbit icon, 'Safe Line' right), and two glowing "
       "leaf-arrow decals flush on the felt at (±2.75, 0, -17) 1.4x2.0 pointing into the chutes (P1).",
 prompt="First-person VR view from a mini golf tee at eye height, looking down a straight green felt lane with stone-and-oak rails. "
        "At the end of the lane a huge glossy acorn sits on a mossy stump, splitting the lane edge into two narrow gaps with lantern "
        "posts. Beyond and below, a wide lower green with a red flag in the far right corner and a small mossy rabbit hole on the left. "
        "Autumn forest edge in warm afternoon light, orange and gold leaves drifting, a tiny squirrel hut on a post, soft hazy "
        "sunbeams, cozy storybook fairy-forest style."),
"h03": dict(
 landmark="A **red-cap mushroom house** whose thick cream stem has an arched tunnel straight through it (opening 7 wide x 3 high). "
          "The felt runs inside. A fat spotted **toadstool stool** guards the cup on the green.",
 shots="1. Hit up the lane into the **steep banked corner** (a 45° pitched bank backed by a rail). It swings the ball right, "
       "through the stem tunnel.\n"
       "2. The second bank swings it left up the leg onto the green. A strong first putt can ride both banks and reach the green.\n"
       "3. Putt around the toadstool stool to the cup.",
 challenge="Pace through two banks. Too soft and the ball stalls in the tunnel. Too hard and it climbs the bank, clatters off the backing rail "
           "and loses its line. The stool forces the last putt to curl in from the left.",
 props="Mushroom house large with stem tunnel 10x12x10 (P1); mushroom house medium 7x9x7 (P1); toadstool stool cladding for "
       "`toadstool_stool` 2x1.8x2 (P1); bank cladding (rounded stone banks on bank1/bank2, 1.2-stud plane, 9 long) (P1); "
       "small toadstool cluster 3x2.5x3 (P2); lantern string 12x1x0.3 (P2).",
 prompt="First-person VR view at eye height from a mini golf tee in a mushroom village. A green felt lane runs ahead to a steeply "
        "banked stone corner that curves right, straight into an arched tunnel bored through the thick cream stem of a giant "
        "red-capped mushroom house with round glowing windows. Beyond, the path banks left again toward a lantern-strung green "
        "with a fat spotted toadstool beside the red flag. Little wooden porches, tiny doors, paper lanterns, orange and red "
        "autumn foliage, warm late-afternoon light, cozy whimsical fairy-tale style."),
"h04": dict(
 landmark="The **Puffball Carousel**: a toadstool hub in the middle of a widened plaza, turning a padded 2-arm bar of puffball stalks "
          "(6 studs across) at a lazy 30°/s. Lantern posts on the plaza rails mark the two side gaps. Mushroom houses flank the plaza, "
          "and a raised green sits beyond a short ramp.",
 shots="**Birdie line (timing):** time the tee shot straight through the plaza past the turning bar and run it up the 0.6-stud ramp "
       "onto the green; 2) putt. A ball clipped by the bar caroms off the padded arm (bumper restitution 0.65) at the bar's surface speed.\n"
       "**Safe line (side gap, ~1 stroke longer):** 1) a firm, accurate putt down the right side of the plaza, between the arm tips and "
       "the rail (gap 3.9 studs wide), stopping just past the carousel; 2) straight up the ramp onto the green; 3) putt out.",
 challenge="First timing obstacle. The bar is slow enough to read in VR (a full turn every 12 s, an arm passes every 6 s). Skilled players "
           "take the side gap for a near-certain par or time the bar for birdie; players who fire at the flag through the carousel "
           "get knocked back about half the time. Diagonal shots up the ramp curl back, so come in straight.",
 props="Puffball carousel bar (moving, pivot hub centre, axis +Y, 30°/s) 6x1x0.7 padded arms + puffballs (P1, **rebuild: shorter**); "
       "toadstool hub 1.4x2x1.4 (P1); mushroom houses x2 7–8x9–10x7–8 (P1); green lantern posts 0.5x3.5x0.5 (P1); side-gap lantern posts "
       "0.4x2.5x0.4 on the plaza rail tops at x ±7.25, z -17 (P2, new); paper lanterns (P2); flag 7.5 (P1).",
 prompt="First-person VR view from a mini golf tee at eye height looking into a cobbled mushroom-village plaza. A small carousel of "
        "giant white puffballs on two short padded stalks slowly turns on a red toadstool hub in the middle of the green felt, with "
        "clear gaps on both sides marked by little lantern posts on the rails. Behind it a short ramp climbs to a raised round green "
        "with a tall red flag, flanked by lantern posts. Red-capped mushroom houses with glowing round windows on both sides, strings "
        "of paper lanterns, falling maple leaves, golden afternoon light, playful cozy fairy-forest style."),
"h05": dict(
 landmark="The **Rootbridge**: a gnarled, arched root bridge only 1.8 studs (0.54 m) wide and with no rails, spanning a clear babbling "
          "stream straight in line with the tee. To the left is a roofed **covered plank bridge** with lanterns. A glowing marker stone "
          "at the root-bridge entry shows where a ball that falls in comes back.",
 shots="**Risk line (good players):** one firm, dead-straight putt across the arched root bridge, finishing near the cup. Then a short putt (birdie or par). "
       "If it falls in the stream: +1 stroke and the ball respawns at the bridge entry (0, 0, -13.5), so the retry is a 13-stud bridge putt, not a full replay.\n"
       "**Safe line:** 1) line up with the covered bridge on the shore; 2) putt through it; 3) approach; 4) putt out.",
 challenge="Nerve: a small aim error over 28 studs drops the ball in the stream. Since Round 5 a miss costs a stroke plus a short, easier "
           "retry from the bridge entry, so the bridge stays tempting after a splash. The covered bridge costs about a stroke but is almost risk-free.",
 props="Arched root bridge 3.5x3x14 (P1); covered plank bridge with shingle roof 7x6x14 (P1); stream water surface + banks (P1); "
       "bridge respawn marker stone 0.8x0.02x0.8 flush in the felt at (0, 0, -13.5) (P2, new); mossy stepping stones 2x1x2 (P3); "
       "small upstream waterfall 6x8x3 (P2); lanterns on the covered bridge (P1); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee on a grassy stream bank. Straight ahead, a narrow arched bridge "
        "made of twisted tree roots, topped with a thin strip of green felt and no railings, crosses a sparkling clear stream to "
        "a wide green with a tall red flag. A softly glowing mossy stone marks the foot of the root bridge. To the left, a cozy roofed "
        "wooden covered bridge with hanging lanterns offers the safe way across. Mossy stepping stones, a small waterfall upstream, "
        "autumn trees in red and gold, warm afternoon light and mist over the water, storybook fairy-forest style."),
"h06": dict(
 landmark="A timber **water mill** whose big paddle wheel (radius 3.6, 2 paddle boards) turns slowly across the flume. "
          "Its paddles dip through a slot in the felt and sweep downstream. A mill race sits behind a gap in the near rail.",
 shots="1. Bank off the first timber deflector board into the flume and time the run under the wheel.\n"
       "2. The second board kicks the ball north up the low 0.25-stud ramp onto the green beside the waterfall.\n"
       "3. Putt out. A full-power, well-timed tee shot can ride everything to the green (the ace line).",
 challenge="Timing a vertical obstacle: the paddles block the flume about 19% of the time, and a paddle that catches the ball "
           "shoves it downstream. The gap into the mill race punishes a ball deflected sideways.",
 props="Mill wheel (moving, axle centre, axis +Z, 30°/s) 1x7.2x8 (P1); mill house 9x10x8 (P1); timber deflector boards x2 "
       "cladding 10x1x0.5 (P1); mill race water + banks (P1); waterfall beside the green 6x12x4 (P1); flour sacks & crates (P3).",
 prompt="First-person VR view from a mini golf tee at eye height. The green felt lane turns right at a slanted timber board into "
        "a wooden flume, where a large water-mill paddle wheel slowly turns, its paddles dipping through the felt and splashing. "
        "A rustic timber mill house stands beside it with lanterns in the windows. Beyond, a second board turns the course up a short "
        "ramp to a green beside a tumbling waterfall with a red flag. A glinting mill race, autumn leaves, warm golden light and "
        "spray mist, cozy storybook style."),
"h07": dict(
 landmark="A **three-step waterfall** cascading into a pool on the left. The hole steps down beside it over two felt terraces, "
          "with a **floating log** with whittled, pointed ends sliding back and forth across the middle tier and pausing at each end.",
 shots="1. Drop off the top tier (full width), cross the middle tier past the sliding log (shoot while it rests at the west end), and thread the **2.5-stud gap** (x 4 to 6.5) that "
       "drops to the bottom tier. The bottom tier's east half slopes down toward the west and carries the ball across toward the flag side.\n"
       "2–3. The cup sits deep in the north-west part of the bottom green (-2.5, -36.5), beyond where the slope drops tee shots, so the "
       "second putt is a real one.",
 challenge="Two drops plus a timing obstacle (Round 7): the 6-stud log slides ±6 studs at 3.5 studs/s, its ends stopping 1 stud short of "
           "each rail. It **pauses 1.0 s at the west end** (the gap line is open) and **1.5 s at the east end**, where it lies right across "
           "the line to the gap. Cycle 9.36 s. Fired at 24 evenly spaced timings, the intended tee shot is blocked or deflected 46% of the time and passes "
           "54% of the time, with no traps. The pointed ends knock a ball sideways out of the log's track, so it can no longer be batted "
           "back and forth along the track (the old soft-lock). A deflected ball can still be shoved toward the waterfall pool (gap in the "
           "middle tier's left rail = hazard). The narrower lower gap and the "
           "deeper cup reward an accurate tee shot and a well-paced putt.",
 props="Three-step waterfall cascade 8x14x10 (P1); floating log (moving, slides along X ±6 at 3.5 studs/s, pauses 1.0 s west / 1.5 s east; ends 1.0 short of the rails) **6x0.8x0.8 with pointed (45°, whittled/root-knot) ends**: collision = 5.2x0.8x0.8 box + two 0.566x0.8x0.566 boxes turned 45° at the ends (P1, **rebuild**); "
       "pool water (P1); lantern posts at the lower gap 0.5x3x0.5 at x 3.75 and 6.75 (P1, **move**: gap is now x 4..6.5); ferns & red leaf "
       "bushes (P3); stone terrace faces (P1); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at the top of a series of green felt terraces stepping down "
        "beside a beautiful three-tiered waterfall that pours into a misty pool on the left. On the middle terrace a mossy log "
        "with whittled pointed ends floats sideways across the path, pausing at each rail. Two lanterns mark a narrow gap down to the bottom green, where a tall red "
        "flag waits in the far corner. Rocks covered in moss and ferns, red and golden autumn trees, rainbow in the spray, warm sunlight, cozy fairy-forest style."),
"h08": dict(
 landmark="The roots of the giant hollow tree arch over the course. In a dead-end alcove a **root knot holds a glowing firefly ring** "
          "(0.9 studs across), guarded by a root door that shuts across the alcove mouth, waits, then slides into a pocket in the knot wall. The alcove's back wall is a "
          "banked root slope. Its twin ring stands in the far corner of the upper green.",
 shots="**Shortcut:** 1) bank off the junction's back rail (or play to the junction); 2) wait for the root door to open (it rests in its pocket for 2.2 s) and thread the firefly ring. "
       "It teleports the ball to the upper green's north-east corner (9, 1.5, -47) and rolls it toward the cup: a firm ring shot can "
       "drop straight in, a soft one leaves a short putt; 3) putt out. A miss climbs the back-wall bank and rolls back out of the alcove.\n"
       "**Long route (par route, shortened in Round 5):** 1) up the lane to the junction; 2) along it softly into the banked corner; "
       "3) one committed putt up the 1.5-stud climb, which the top bank turns onto the connector and the green; 4) putt out.",
 challenge="The ring is a fair target (radius 0.45) guarded by a timing gate (Round 7): the root door (3.6 long) **stays shut across the ring "
           "line for 1.8 s**, slides 4 studs south into its pocket at 3 studs/s, **stays open 2.2 s**, then slides back. Cycle 6.67 s. "
           "Fired at 24 evenly spaced timings, the intended bank shot is blocked or deflected 50% of the time and passes 50% of the time, with no traps. The long route is now about a stroke shorter (the flat run before the climb is gone) "
           "and is a genuine par.",
 props="Root knot arch with firefly ring (entry, ring glow **0.9 across**) 3x4x4 (P1, **resize ring**); alcove back-wall bank cladding "
       "1.3x0.5x7 root bark over the banked plane x 7.7..9 (P1, new); exit firefly ring 2.5x3x1 at (9, 1.5, -47) (P1, **move**); "
       "sliding root door (moving, slides along Z 0..+4.0 at 3 studs/s: closed at 0 for 1.8 s, open at +4.0 for 2.2 s) **0.7x1x3.6** with one pocket in "
       "the south root-knot wall (door fully hidden at +4.0); the old north pocket is no longer needed (P1, **rebuild**); "
       "hollow-tree base & arching roots 30x40x30 (P1); glowing mushrooms 2x1.5x2 (P2); bank cladding (P1); flag 7.5 (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at the foot of an enormous golden hollow tree whose roots arch "
        "overhead like a cathedral. The green felt lane opens into a junction. To the right, a dead-end nook inside a gnarled root knot "
        "holds a glowing ring of fireflies, a carved root door sliding shut across its mouth and back into the knot wall. To the left, a "
        "short banked path climbs between the roots to an upper green with a tall red flag. Fireflies, glowing mushrooms, amber lanterns, "
        "dusky golden light filtering through the leaves, magical cozy fairy-forest style."),
"h09": dict(
 landmark="The **heart of the giant hollow tree**: you putt up a ramp, round a banked corner and through a **root portcullis** "
          "into a tunnel in the trunk, where the felt **dips and rises** (the course's only rolling dip). Inside, a lantern-lit chamber "
          "ends at the **heart well**, where a **great lantern swings on a chain** across the mouth of the drop to the heart green below. "
          "Three big amber lanterns hang high above the heart green and light it.",
 shots="1. A strong putt up the 1-stud ramp rides the banked corner east and, if the root gate is up, rolls through the tunnel's dip into the chamber.\n"
       "2. The root deflector turns the ball north. Time the swinging lantern (it swings slowly, once every 4 s), or play to the edge of the 8-stud well mouth, and drop 1.5 studs into the heart.\n"
       "3. The heart green slopes gently away from the drop; the cup sits in its north-east part (26, -0.8, -52). Putt out.\n"
       "**Secret:** a tiny glowing **Lantern Knot** in the corridor floor at (6.5, 1.0, -23.0), half a stud past the root gate and one stud in "
       "from the corridor's south rail, teleports the ball to the heart green's north-west corner and rolls it east along the back of the green toward the cup. "
       "It is the hole's ace route.",
 challenge="Finale combining everything: ramp pace, a bank, a vertical gate (open ~70% of its 4 s cycle), a rolling dip (a weak shot settles "
           "in the tunnel), a deflector, a swinging lantern and a drop. Round 8 (after RobloxDevBot measured it in Studio): the hinge sits right over "
           "the chamber shot line (x 21.2), the lantern swings a short, readable ±11° every 4 s (Round 10, was ±13°), and a collider foot hangs below the ball's centre, so a ball that meets "
           "the lantern is stopped instead of rolling under it. The foot is 1.0x0.4x1.6, square to the swing (yaw 0), 0.037 above the felt, "
           "with a matching base plinth on the lantern mesh. Round 10: Studio showed that only the foot's square north face really stops a ball; side and corner hits shove it on through, "
           "so the swing was shortened to keep that face over the line longer. At the ends of its swing the lantern hangs beside the line (centre 1.34 studs east or west of the hinge) and the ball rolls past. "
           "Fired at 24 evenly spaced timings, the intended chamber shot is blocked 58% of the time (10 pass), with no traps; "
           "on RobloxDevBot's in-engine test line the sim blocks 40-60% at 7-9 studs/s (55% at 7.75 over 80 timings); calibrated to Studio (31% at ±13°) that is about 44% in-engine. The 1.6x1.6 square lantern is turned 30°, so a hit knocks the "
           "ball out of the swing plane and it can never be batted back and forth along it. The three amber lanterns over the green are decoration only, "
           "8 studs above the felt. The secret knot rewards players who explore.",
 props="Giant hollow tree trunk with chamber and heart 34x60x34 (P1); root portcullis gate (moving, slides along Y 0..1.8 at 0.9 studs/s) "
       "0.8x1.4x7.4 (P1); **great lantern pendulum** (moving, Round 8: hinge at **(21.2, 8.996, -38.5)**, axis +Z, **±11° (Round 10, was ±13°), period 4 s**; "
       "chain 7 long; lantern bob **1.6x1.8x1.6 square lantern turned 30° about the vertical** whose bottom hangs 0.096 above the felt at rest, "
       "plus a **collider foot 1.0x0.4x1.6, yaw 0** (square to the swing; centred 7.759 below the hinge, bottom 0.037 above the felt at rest), "
       "covered by a **base plinth on the lantern mesh** of the same size and yaw (its corners stick out up to 0.14 past the lantern's faces)) "
       "(P1, **rebuild**); root beam over the chamber 16x1.2x1.2 (P1, still centred at x 22; the hinge is on it at x 21.2); "
       "trunk tunnel arch 7x5x8 with root-and-moss trim following the 0.4 dip (P2); root deflector cladding 15x1x0.5 (P1); "
       "heart-well root rim 8x0.6x1 (P2); Lantern Knot 1.2x1.2x0.6 + exit knot 1.0x0.3x1.0 (P2); **3 hanging amber lanterns** 1.2x1.8x1.2 "
       "(NEW, replace the old 'dozens of lanterns' cluster) at (18.5, -47.5), (28.5, -46.5), (20, -51.5), bottoms at y 7.2 = 8 studs above the green felt, "
       "chains up into the canopy, warm PointLights; decoration only, no collision (P1); "
       "glowing mushrooms (P2); flag 8 (P1). The old lantern bar + lantern post are removed.",
 prompt="First-person VR view at eye height from a mini golf tee at the base of a colossal hollow golden tree. A green felt lane "
        "climbs a ramp to a banked stone corner, then turns into an arched tunnel in the trunk where the felt dips and rises, behind "
        "a portcullis of twisted roots that rises and falls. Through the opening, a warm glow: inside the hollow tree three big amber paper "
        "lanterns hang high above the heart green, and a great square brass-and-paper lantern swings slowly on a long chain across the mouth "
        "of a round sunken heart green with a tall red flag. Fireflies, glowing mushrooms, golden autumn canopy, magical evening light, "
        "grand finale feel, cozy fairy-forest storybook style."),
}


def mp_lines(h):
    out = []
    for m in h.get("moving_parts", []):
        if m["type"] == "swing":
            b = m["blockers"][0]
            extra = "".join(f"; blocker {q + 2}: box {c['size']} centred {c['center']}" + (f" yaw {c['yaw']:g}" if c.get("yaw") else "")
                            for q, c in enumerate(m["blockers"][1:]))
            out.append(f"- **{m['id']}** (swing = pendulum): pivot (hinge) {m['pivot']}, axis {m['axis']} (swings in the plane "
                       f"perpendicular to it), angle(t) = {m['amplitude_deg']}° x sin(360°·t/{m['period_s']} s + {m.get('phase', 0)}°), "
                       f"peak angular speed {m['speed']:.0f}°/s at the bottom. Blocker: bob box {b['size']} centred {b['center']} from the "
                       f"pivot when hanging straight down{extra}. Visual: {m.get('visual', '')}")
            continue
        unit = m["speed_units"]
        rng = "continuous" if m["range"] is None else f"ping-pong {m['range'][0]}..{m['range'][1]} {'deg' if m['type']=='rotate' else 'studs'}"
        bl = "; ".join(f"box {b['size']} at {b['center']}" + (f" yaw {b['yaw']}" if b.get('yaw') else "") +
                       (f" roll {b['roll']}" if b.get('roll') else "") for b in m["blockers"])
        period = S.cycle_period(m)
        if m.get("dwell"):
            rng += " with pauses " + ", ".join(f"{d['s']:g} s at {d['at']:g}" for d in m["dwell"])
        out.append(f"- **{m['id']}** ({m['type']}): pivot {m['pivot']}, axis {m['axis']}, speed {m['speed']} {unit}, {rng}, "
                   f"phase {m.get('phase', 0)}, cycle {period:.2f} s. Blockers (relative to pivot at angle/offset 0): {bl}. "
                   f"Visual: {m.get('visual', '')}")
    for t in h.get("teleports", []):
        out.append(f"- **teleport {t['id']}**: entry {t['entry']['center']} r {t['entry']['radius']} -> exit {t['exit']['center']} "
                   f"dir {t['exit']['dir']}, exit speed = clamp(in x {t['speed_factor']}, {t['min_speed']}, {t['max_speed']}) studs/s")
    for hz in h.get("hazards", []):
        if hz.get("reset") == "respawn":
            out.append(f"- **hazard {hz['id']}** ({hz['type']}): a ball that falls in gets +{hz['penalty']} stroke and is placed at rest "
                       f"on the respawn point {hz['respawn']} (not back at the stroke start)")
    return out or ["- none"]


def main():
    tag = sys.argv[1]
    only = {int(x) for x in sys.argv[2:]}
    course = json.load(open(os.path.join(ROOT, "holes.json")))
    sim = {h["id"]: h for h in json.load(open(os.path.join(HERE, "out", f"sim-{tag}.json")))["holes"]}
    for h in course["holes"]:
        if only and h["number"] not in only:
            continue
        t = TEXT[h["id"]]
        s = sim.get(h["id"], {})
        st = s.get("stats", {})
        hs = s.get("hio_search") or {}
        tee, cup = h["tee"]["position"], h["cup"]["position"]
        xs = [p["center"][0] for p in h["felt"]]
        if hs.get("line"):
            ln = hs["line"]
            a = math.radians(ln["aim_deg"])
            hio = (f"Brute-force search from the tee found ace lines ({hs.get('hits') or hs.get('refine_hits')} grid shots). "
                   f"The most robust: aim **{ln['aim_deg']:.1f}°** (atan2(dz,dx): direction ({math.cos(a):.2f}, {math.sin(a):.2f}) in x/z, "
                   f"i.e. {abs(90 - (ln['aim_deg'] - 180)):.1f}° {'left' if ln['aim_deg'] < 270 else 'right'} of straight -Z), "
                   f"speed **{ln['speed']:.1f} studs/s** ({ln['speed'] / 19.78 * 100:.0f}% power)"
                   + (f", start phase t={ln['phase']:.1f}s of the moving parts" if h.get("moving_parts") else "")
                   + ". The red dashed line on the layout PNG traces it.")
        else:
            hio = "No ace line found by the brute-force search."
        fl = h["cup"].get("flag") or {}
        los = s.get("flag_los") or {}
        flag_txt = (f"Flag: {fl.get('pole_height')}-stud pole ({fl.get('pole_diameter')} diameter) standing in the cup, {fl.get('banner_size')} "
                    f"{fl.get('banner_color')} banner at the top {fl.get('top')}; visual only, no collision. "
                    f"Line of sight from the tee eye (5.5 studs above the tee) to the flag top: "
                    f"**{'visible' if los.get('visible') else 'blocked by ' + ', '.join(los.get('blocked_by', []))}** "
                    f"(min clearance over rails/felt/props {los.get('clearance', 0):+.2f} studs)"
                    + (". Moving parts crossing the sightline: " + ", ".join(f"{k} {v * 100:.0f}% of its cycle" for k, v in los.get('moving', {}).items() if v)
                       if any((los.get('moving') or {}).values()) else "") + ".")
        stats = "\n".join(f"| {k} | {v['avg']:.2f} | {v['hio'] * 100:.1f}% | {v['capped'] * 100:.1f}% | {v['dist']} |" for k, v in st.items())
        md = f"""# Hole {h['number']}: {h['name']} (Par {h['par']})

Zone: **{h['zone']}**. Gimmick: **{h['gimmick']}**.
Layout: `h{h['number']:02d}-layout.png`. Geometry: `holes.json` -> holes[{h['number'] - 1}]. World offset {h['world_offset']}, yaw {h.get('world_yaw', 0)}.
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

## Moving parts / teleports (exact specs, also in holes.json)
{chr(10).join(mp_lines(h))}

## Flag and sightline
{flag_txt}

## Playtest stats (final, {tag}, 2000 plays per skill)
| Skill | Avg strokes | HIO | Capped (8) | Strokes 1..8 |
|---|---|---|---|---|
{stats}

## Props for 3D Model Bot (decoration only, sizes in studs)
{t['props']}

Decoration anchors (position in hole-local studs):
{chr(10).join(f"- `{a['name']}` at {a['position']}{' (LANDMARK)' if a.get('landmark') else ''}{' size ' + str(a['approx_size']) if a.get('approx_size') else ''}: {a['notes']}" for a in h['decoration_anchors'])}

## Concept prompt
{t['prompt']}
"""
        open(os.path.join(ROOT, f"h{h['number']:02d}-notes.md"), "w").write(md)
        print("wrote", f"h{h['number']:02d}-notes.md")


if __name__ == "__main__":
    main()
