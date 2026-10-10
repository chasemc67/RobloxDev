#!/usr/bin/env python3
"""Writes hNN-notes.md from holes.json + final sim results + the hand-written design text below.
    python3 tools/write_notes.py <sim tag>"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
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
           "so you can't see a straight line to it from the tee. The safe play is a two-putt off the deflector.",
 props="Lantern torii gate 9x7x1.2 (P1); 2 paper lanterns L (P1); welcome sign post 2x3x0.4 (P2); red maple 10x16x10 (P2); "
       "mossy boulder 4x3x4 (P2); deflector plank cladding along the `deflector` wall 10x1x0.5 (P1); leaf piles (P3).",
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
           "changes once it lands. The rabbit hole punishes left-chute shots that are too hard (+1 and replay).",
 props="Giant acorn 3x4x3 (P1); stump (cladding for `stump` block 3x1.2x1) (P1); lantern posts at both chutes 0.5x3x0.5 (P1); "
       "rabbit-hole rim 3x0.5x3 (P2); squirrel hut on post 3x5x3 (P3); leaf piles (P3).",
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
 landmark="The **Puffball Carousel**: a toadstool hub in the middle of a widened plaza, turning a 2-arm bar of puffball stalks "
          "(9 studs across) at a lazy 36°/s. Mushroom houses flank the plaza, and a raised green sits beyond a short ramp.",
 shots="1. Time the shot through the plaza past the turning bar (or slip down a side gap). Run it up the 0.6-stud ramp onto the raised green.\n"
       "2–3. Putt out. A ball clipped by the bar caroms off at the bar's surface speed.",
 challenge="First timing obstacle. The bar is slow enough to read in VR (a full turn every 10 s, an arm passes every 5 s). "
           "Getting knocked back costs a stroke or two. Diagonal shots up the ramp curl back, so come in straight.",
 props="Puffball carousel bar (moving, pivot hub centre, axis +Y) 9x1x0.7 arms + puffballs (P1); toadstool hub 1.4x2x1.4 (P1); "
       "mushroom houses x2 7–8x9–10x7–8 (P1); green lantern posts 0.5x3.5x0.5 (P1); paper lanterns (P2).",
 prompt="First-person VR view from a mini golf tee at eye height looking into a cobbled mushroom-village plaza. A big carousel of "
        "giant white puffballs on curved stalks slowly turns on a red toadstool hub in the middle of the green felt. "
        "Behind it a short ramp climbs to a raised round green with a red flag, flanked by lantern posts. Red-capped mushroom houses with "
        "glowing round windows on both sides, strings of paper lanterns, falling maple leaves, golden afternoon light, "
        "playful cozy fairy-forest style."),
"h05": dict(
 landmark="The **Rootbridge**: a gnarled, arched root bridge only 1.8 studs (0.54 m) wide and with no rails, spanning a clear babbling "
          "stream straight in line with the tee. To the left is a roofed **covered plank bridge** with lanterns.",
 shots="**Risk line (good players):** one firm, dead-straight putt across the arched root bridge, finishing near the cup. Then a short putt (birdie or par).\n"
       "**Safe line:** 1) line up with the covered bridge on the shore; 2) putt through it; 3) approach; 4) putt out.",
 challenge="Pure nerve: a small aim error over 28 studs drops the ball in the stream (+1, replay from the tee). "
           "The covered bridge costs about a stroke but is almost risk-free.",
 props="Arched root bridge 3.5x3x14 (P1); covered plank bridge with shingle roof 7x6x14 (P1); stream water surface + banks (P1); "
       "mossy stepping stones 2x1x2 (P3); small upstream waterfall 6x8x3 (P2); lanterns on the covered bridge (P1).",
 prompt="First-person VR view at eye height from a mini golf tee on a grassy stream bank. Straight ahead, a narrow arched bridge "
        "made of twisted tree roots, topped with a thin strip of green felt and no railings, crosses a sparkling clear stream to "
        "a wide green with a red flag. To the left, a cozy roofed wooden covered bridge with hanging lanterns offers the safe way "
        "across. Mossy stepping stones, a small waterfall upstream, autumn trees in red and gold, warm afternoon light and mist "
        "over the water, storybook fairy-forest style."),
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
          "with a **floating log** sliding back and forth across the middle tier.",
 shots="1. Drop off the top tier (full width), cross the middle tier past the sliding log, and aim for the 3.5-stud gap that drops "
       "to the bottom tier. The bottom tier's east half slopes gently toward the cup side.\n"
       "2–3. Putt out on the bottom green.",
 challenge="Two drops plus a moving blocker: the log slides ±6 studs at 5 studs/s and will happily shove the ball toward the "
           "waterfall pool (gap in the middle tier's left rail = hazard). The landing slope carries the ball left after the second drop.",
 props="Three-step waterfall cascade 8x14x10 (P1); floating log (moving, slides along X) 5x0.8x0.8 (P1); pool water (P1); "
       "lantern posts at the lower gap 0.5x3x0.5 (P1); ferns & red leaf bushes (P3); stone terrace faces (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at the top of a series of green felt terraces stepping down "
        "beside a beautiful three-tiered waterfall that pours into a misty pool on the left. On the middle terrace a mossy log "
        "floats sideways across the path. Lanterns mark a narrow gap down to the bottom green, where a red flag waits. "
        "Rocks covered in moss and ferns, red and golden autumn trees, rainbow in the spray, warm sunlight, cozy fairy-forest style."),
"h08": dict(
 landmark="The roots of the giant hollow tree arch over the course. In a dead-end alcove a **root knot holds a glowing firefly ring**, "
          "guarded by a sliding root door. Its twin ring stands on the upper green.",
 shots="**Shortcut:** 1) bank off the junction's back rail (or play to the junction); 2) thread the sliding root door into the firefly ring. "
       "It teleports you to the upper green's far corner and sends the ball rolling toward the cup; 3–4) putt out.\n"
       "**Long route:** 1) to the junction; 2) along it into the banked corner; 3) up the long 1.5-stud climb; "
       "4) the top bank turns you onto the connector; 5) putt out.",
 challenge="The ring is small (radius 0.35) and the root door slides across the alcove mouth (±2.5 studs at 2 studs/s). "
           "A miss leaves the ball rattling in the alcove. The long route is safe but costs about a stroke.",
 props="Root knot arch with firefly ring (entry) 3x4x4 (P1); exit firefly ring 2.5x3x1 (P1); sliding root door (moving, slides along Z) "
       "0.7x1x3.2 (P1); hollow-tree base & arching roots 30x40x30 (P1); glowing mushrooms 2x1.5x2 (P2); bank cladding (P1).",
 prompt="First-person VR view at eye height from a mini golf tee at the foot of an enormous golden hollow tree whose roots arch "
        "overhead like a cathedral. The green felt lane opens into a junction. To the right, a dead-end nook inside a gnarled root knot "
        "holds a glowing ring of fireflies with a carved root door sliding across its mouth. To the left, a long banked path climbs "
        "away between the roots. Fireflies, glowing mushrooms, amber lanterns, dusky golden light filtering through the leaves, "
        "magical cozy fairy-forest style."),
"h09": dict(
 landmark="The **heart of the giant hollow tree**: you putt up a ramp, round a banked corner and through a **root portcullis** "
          "into a tunnel in the trunk. Inside, a lantern-lit chamber ends at the **heart well**, where a slowly turning lantern bar "
          "guards the drop to the heart green below. Dozens of lanterns hang in the hollow above.",
 shots="1. A strong putt up the 1-stud ramp rides the banked corner east and, if the root gate is up, runs through the tunnel into the chamber.\n"
       "2. The root deflector turns the ball north. Time the lantern bar and drop 1.5 studs into the heart.\n"
       "3. The heart green slopes gently toward the cup. Putt out.\n"
       "**Secret:** a tiny glowing **Lantern Knot** in the corridor floor just past the gate teleports the ball to the heart green's "
       "south-west corner, rolling toward the cup. It is the hole's ace route.",
 challenge="Finale combining everything: ramp pace, a bank, a vertical gate (open ~62% of its 4 s cycle), a deflector, a rotating bar and a drop. "
           "The secret knot rewards players who explore.",
 props="Giant hollow tree trunk with chamber and heart 34x60x34 (P1); root portcullis gate (moving, slides along Y) 0.8x1.4x7.4 (P1); "
       "lantern bar + post (moving, axis +Y, 40°/s) 6x1x0.6 (P1); trunk tunnel arch 7x5x8 (P2); root deflector cladding 15x1x0.5 (P1); "
       "heart-well root rim 8x0.6x1 (P2); Lantern Knot 1.2x1.2x0.6 (P2); hanging lanterns cluster 16x6x12 (P1); glowing mushrooms (P2).",
 prompt="First-person VR view at eye height from a mini golf tee at the base of a colossal hollow golden tree. A green felt lane "
        "climbs a ramp to a banked stone corner, then turns into an arched tunnel in the trunk, where a portcullis of twisted roots "
        "rises and falls. Through the opening, a warm glow: inside the hollow tree hundreds of paper lanterns hang above a "
        "lantern-lit chamber and a slowly turning lantern bar over a round heart green with a red flag. Fireflies, glowing "
        "mushrooms, golden autumn canopy, magical evening light, grand finale feel, cozy fairy-forest storybook style."),
}


def mp_lines(h):
    out = []
    for m in h.get("moving_parts", []):
        unit = m["speed_units"]
        rng = "continuous" if m["range"] is None else f"ping-pong {m['range'][0]}..{m['range'][1]} {'deg' if m['type']=='rotate' else 'studs'}"
        bl = "; ".join(f"box {b['size']} at {b['center']}" + (f" yaw {b['yaw']}" if b.get('yaw') else "") +
                       (f" roll {b['roll']}" if b.get('roll') else "") for b in m["blockers"])
        period = (360 / abs(m["speed"]) if m["range"] is None and m["type"] == "rotate"
                  else 2 * (m["range"][1] - m["range"][0]) / abs(m["speed"]))
        out.append(f"- **{m['id']}** ({m['type']}): pivot {m['pivot']}, axis {m['axis']}, speed {m['speed']} {unit}, {rng}, "
                   f"phase {m.get('phase', 0)}, cycle {period:.1f} s. Blockers (relative to pivot at angle/offset 0): {bl}. "
                   f"Visual: {m.get('visual', '')}")
    for t in h.get("teleports", []):
        out.append(f"- **teleport {t['id']}**: entry {t['entry']['center']} r {t['entry']['radius']} -> exit {t['exit']['center']} "
                   f"dir {t['exit']['dir']}, exit speed = clamp(in x {t['speed_factor']}, {t['min_speed']}, {t['max_speed']}) studs/s")
    return out or ["- none"]


def main():
    tag = sys.argv[1]
    course = json.load(open(os.path.join(ROOT, "holes.json")))
    sim = {h["id"]: h for h in json.load(open(os.path.join(HERE, "out", f"sim-{tag}.json")))["holes"]}
    for h in course["holes"]:
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
