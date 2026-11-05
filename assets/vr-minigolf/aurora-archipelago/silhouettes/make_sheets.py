# Aurora Archipelago silhouette sheets (studs). Views: FRONT = X-Y (looking -Z from the tee side), SIDE = Z-Y, TOP = X-Z.
# Black = the prop's silhouette; grey = context (felt line, supports that belong to another prop, collider outline). Shapes follow
# props.md / holes.json envelopes; the left column is the reference image (3D Model Bot preview or the hole's concept art).
import math, os, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); PV = os.path.join(ROOT, "models/previews/props_batch1")
def R(x0, y0, w, h): return [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)]
def C(cx, cy, r): return ("c", cx, cy, r)
def G(shape): return ("g", shape)            # grey context
def ell(cx, cy, rx, ry, a0=0, a1=360, n=40): return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
def blob(w, h, flat=0.0):  # rounded boulder/mound, flat base
    return [(-w / 2, 0)] + [(w / 2 * math.cos(math.radians(a)), h * math.sin(math.radians(a)) ** 0.6) for a in range(0, 181, 10)][::-1][::-1] + [(-w / 2, 0)]
def mound(w, h): return [(-w / 2, 0)] + [(w / 2 * -math.cos(math.radians(a)), h * math.sin(math.radians(a)) ** 0.5) for a in range(0, 181, 10)] + [(w / 2, 0)]
def branch_coral(w, h, seed=1, trunk=0.5):
    """branching coral front: trunk splitting 2-3 times into flattened fans with round tips, crown spread to width w"""
    out = []
    segs = []
    def br(x, y, ang, L, t, d):
        x2, y2 = x + L * math.sin(math.radians(ang)), y + L * math.cos(math.radians(ang))
        segs.append((x, y, x2, y2, t, d))
        if d == 0: return
        for da in ((-38, 34) if d % 2 else (-46, 2, 42)):
            br(x2, y2, ang * 0.6 + da + ((seed * 13 + d * 7) % 11) - 5, L * 0.8, t * 0.75, d - 1)
    br(0, 0, (seed % 3 - 1) * 4, h * 0.34, trunk, 3)
    xs = [q for sg in segs for q in (sg[0], sg[2])]; ys = [q for sg in segs for q in (sg[1], sg[3])]
    sx = (w * 0.86) / max(1e-6, max(xs) - min(xs)); sy = (h * 0.9) / max(ys); cx = (max(xs) + min(xs)) / 2
    for x, y, x2, y2, t, d in segs:
        X, Y, X2, Y2 = (x - cx) * sx, y * sy, (x2 - cx) * sx, y2 * sy
        ang = math.atan2(X2 - X, Y2 - Y); nx, ny = math.cos(ang) * t / 2, -math.sin(ang) * t / 2
        out.append([(X - nx, Y - ny), (X + nx, Y + ny), (X2 + nx * .85, Y2 + ny * .85), (X2 - nx * .85, Y2 - ny * .85)])
        if d == 0:  # flattened fan tip
            out.append(ell(X2, Y2, max(t * 1.4, w * 0.07), max(t * 1.0, h * 0.045)))
    return out
def fit(shapes, W, H):  # scale crown to envelope
    return shapes
P = []
def prop(sheet, hole, name, env, note, ref, front, side, top, ylab=None):
    P.append(dict(sheet=sheet, hole=hole, name=name, env=env, note=note, ref=ref, f=front, s=side, t=top))
def drawv(ax, shapes, title, dims):
    for s in shapes:
        grey = isinstance(s, tuple) and s[0] == "g"
        if grey: s = s[1]
        col = "#9a9aa8" if grey else "black"
        if isinstance(s, tuple) and s[0] == "c": ax.add_patch(Circle((s[1], s[2]), s[3], fc=col, ec=col, lw=0))
        elif isinstance(s, tuple) and s[0] == "ring": ax.add_patch(Circle((s[1], s[2]), s[3], fc="none", ec=col, lw=s[4]))
        elif isinstance(s, tuple) and s[0] == "line": ax.plot(s[1], s[2], color=col, lw=s[3])
        else: ax.add_patch(Polygon(s, closed=True, fc=col, ec=col, lw=0.3))
    ax.set_aspect("equal"); ax.autoscale_view()
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim(); pad = max(x1 - x0, y1 - y0) * 0.12 + 0.2
    ax.set_xlim(x0 - pad, x1 + pad); ax.set_ylim(y0 - pad, y1 + pad)
    ax.axhline(0, color="#4da37a", lw=1.2, zorder=0) if title != "TOP" else None
    ax.set_title(f"{title}  {dims}", fontsize=9); ax.tick_params(labelsize=7); ax.grid(alpha=0.25)
def sheet(tag, title, out):
    rows = [p for p in P if p["sheet"] == tag]
    fig = plt.figure(figsize=(22, 3.0 * len(rows) + 1.2), dpi=90)
    fig.suptitle(title, fontsize=18, fontweight="bold", y=0.998)
    for i, p in enumerate(rows):
        W, H, D = p["env"]
        ax = fig.add_subplot(len(rows), 5, 5 * i + 1); ax.axis("off")
        if p["ref"] and os.path.exists(p["ref"]):
            im = Image.open(p["ref"]).convert("RGB"); im.thumbnail((520, 300)); ax.imshow(im)
        ax.set_title(f"{p['hole']}  {p['name']}\nenvelope W×H×D = {W:g} × {H:g} × {D:g} studs", fontsize=10, fontweight="bold", loc="left")
        drawv(fig.add_subplot(len(rows), 5, 5 * i + 2), p["f"], "FRONT", f"W {W:g} × H {H:g}")
        drawv(fig.add_subplot(len(rows), 5, 5 * i + 3), p["s"], "SIDE", f"D {D:g} × H {H:g}")
        drawv(fig.add_subplot(len(rows), 5, 5 * i + 4), p["t"], "TOP", f"W {W:g} × D {D:g}")
        ax = fig.add_subplot(len(rows), 5, 5 * i + 5); ax.axis("off")
        ax.text(0, 1, p["note"], fontsize=9, va="top", wrap=True, family="DejaVu Sans")
    fig.tight_layout(rect=(0, 0, 1, 0.99)); fig.savefig(out); plt.close(fig); print("wrote", out)
CON = lambda n: os.path.join(ROOT, f"h{n:02d}-concept.png")
PVf = lambda f: os.path.join(PV, f)
# ---------------------------------------------------------------- batch 1
S = "b1"
prop(S, "H1", "harbour_lantern", [0.9, 9, 0.9], "Warm-timber post 0.4 sq to y 7.6, brass lantern box 0.9 × 1.2 on a short bracket,\nlantern bottom 7.8. PointLight #FFB861 r14 b0.8.\nBase [-6,0,-24] beside the west rail (outside felt).", PVf("h01_harbour_lantern_34.png"),
     [R(-.2, 0, .4, 7.8), R(-.45, 7.8, .9, 1.2), [(-.3, 9.0), (.3, 9.0), (0, 9.0 + 0.0001)]], [R(-.2, 0, .4, 7.8), R(-.45, 7.8, .9, 1.2)], [R(-.45, -.45, .9, .9), G(C(0, 0, .2))])
prop(S, "H1", "snow_boulder", [4.4, 5, 4.4], "Slate-violet boulder skin over the 3×3×3 bumper (yaw 45, grey).\nFlat-faced base EXACTLY the collider from felt to y 2.5; chunky rounded snow cap above, ≤ 5 high.\nFlat SE bank face with mint glow line.", PVf("h01_snow_boulder_34.png"),
     [[(-2.12, 0), (2.12, 0), (2.12, 2.5), (1.8, 3.6), (0.9, 4.6), (-0.4, 5), (-1.6, 4.3), (-2.12, 2.9)]],
     [[(-2.12, 0), (2.12, 0), (2.12, 2.6), (1.4, 4.2), (0, 4.9), (-1.5, 4.4), (-2.12, 2.6)]], [[(0, -2.12), (2.12, 0), (0, 2.12), (-2.12, 0)], G([(0, -2.12), (2.12, 0)])])
crook = [R(-.175, 0, .35, 10.6)] + [[(3.85 * t - .0, 10.6 + 0.9 * math.sin(math.pi * t) * (1 - t * .3)), (3.85 * t, 10.6 + 0.9 * math.sin(math.pi * t) * (1 - t * .3) + .3)] for t in []]
arm = [(x, 10.6 + 1.2 * math.sin(math.pi * x / 4.6)) for x in [i * 0.2 for i in range(0, 20)]]
arm_poly = [(x, y) for x, y in arm] + [(x, y - .3) for x, y in arm][::-1]
prop(S, "H2", "lantern_crook + lantern_cue", [4.35, 11, 0.5], "Shepherd's-crook post 0.35 sq at [-13.6,0,-46], outside the west rail (grey).\nCurved arm (0.3 thick, underside ≥ y 10.4) reaches 3.85 east to over the cup;\ndrop rod 0.1 to the lantern 0.9 × 1.2 (y 9..10.2). Nothing below 10.4 over felt.", PVf("h02_lantern_cue_34.png"),
     [R(-.175, 0, .35, 11.0), arm_poly, R(3.8, 10.2, .1, 1.0), R(3.4, 9.0, .9, 1.2), G(R(1.1, 0, .5, 1.5)), G(R(1.6, -.05, 3, .05))],
     [R(-.175, 0, .35, 11.0), R(-.25, 10.4, .5, .6), R(-.45, 9.0, .9, 1.2)], [R(-.175, -.175, .35, .35), R(0, -.15, 3.85, .3), R(3.4, -.45, .9, .9), G(R(1.1, -3, .5, 6))])
lint = [(x, 8.6 + 0.6 * math.cos(math.pi * x / 5)) for x in [-2.5 + .25 * i for i in range(21)]]
prop(S, "H2", "lintel_left/mid/right (x3)", [5, 1.2, 1.2], "Frosted ice-arch lintel, LEGLESS, underside exactly y 8 (VR head room)\nwith a plank sign hung on its face. Each end rests on a basalt rock pillar\n(grey) outside the rail / on the drift wall top, never in the burrow width.", PVf("h02_lintel_mid_34.png"),
     [[(-2.5, 8)] + [(x, 8) for x, _ in lint] + [(2.5, 8)] + [(x, y + .6) for x, y in lint][::-1], R(-.9, 7.1, 1.8, .7), G(R(-3.3, 0, .8, 8.6)), G(R(2.5, 0, .8, 8.6))],
     [R(-.6, 8, 1.2, 1.2), G(R(-.6, 0, 1.2, 8))], [R(-2.5, -.6, 5, 1.2), G(R(-3.3, -.6, .8, 1.2)), G(R(2.5, -.6, .8, 1.2))])
prop(S, "H2", "rookery_drift", [24, 5, 26], "Long rounded snow drift dressing the 2.4-high burrow walls (grey);\nmouths are round cuts, burrows OPEN-TOPPED. Drift dressing ≤ y 5\nso the flag reads over it. Snowpuff peek-holes on top.", PVf("h02_rookery_drift_34.png"),
     [mound(24, 5), G(R(-11, 0, 3, 3.5)), G(R(-2, 0, 4, 3.5)), G(R(7, 0, 4, 3.5))], [mound(26, 5)], [[(x*12, y*13) for x, y in [(math.copysign(1, math.cos(t)) * (abs(math.cos(t)) ** 0.35), math.copysign(1, math.sin(t)) * (abs(math.sin(t)) ** 0.35)) for t in [i * math.pi / 40 for i in range(81)]]], G(R(-11, -13, 3, 18)), G(R(-2, -13, 4, 12)), G(R(7, -13, 4, 26))])
prop(S, "H3", "ice_plank", [2.4, 0.8, 26], "Rail-less glowing ice plank, felt on top (2 wide), 26 long straight over the gap.\nTranslucent glacier cyan, crystal-core neon strip down each edge;\ndeck ≥ 0.6 thick / skirt to y -0.6.", PVf("h03_ice_plank_34.png"),
     [R(-1.2, -.6, 2.4, .6), R(-1.2, 0, .2, .2), R(1.0, 0, .2, .2)], [R(-13, -.6, 26, .6)], [R(-1.2, -13, 2.4, 26), G(R(-1, -13, 2, 26))])
prop(S, "H3", "ice_bridge", [5, 2, 26], "Railed ice bridge: glass deck under the felt, chunky snow-capped\ntimber ball rails (colliders 0.5 wide) both sides, posts every 4.", PVf("h03_ice_bridge_34.png"),
     [R(-2.5, -.6, 5, .6), R(-2.5, 0, .5, 1.5), R(2.0, 0, .5, 1.5), C(-2.25, 1.6, .35), C(2.25, 1.6, .35)], [R(-13, -.6, 26, .6), R(-13, 0, 26, 1.2)] + [R(-13 + 4 * i, 0, .5, 1.8) for i in range(7)], [R(-2.5, -13, 5, 26), G(R(-2, -13, 4, 26))])
prop(S, "H3", "glimmer_islet", [20, 30, 20], "Small floating island (view cue, 24 east of the gap): inverted rocky cone\nwith slate-violet roots, flat snowy top, glowing ice-crystal cluster on top;\nGlimmer Icefall pours off one side.", PVf("h03_glimmer_islet_34.png"),
     [[(-10, 12), (10, 12), (7, 4), (2, -14), (-3, -10), (-8, 4)], R(-8, 12, 16, 2), [(-3, 14), (-2, 20), (-1, 14)], [(-1, 14), (0.5, 24), (2, 14)], [(2, 14), (3, 19), (4, 14)]],
     [[(-10, 12), (10, 12), (8, 4), (1, -14), (-6, 2)], R(-8, 12, 16, 2), [(-2, 14), (0, 23), (2, 14)]], [ell(0, 0, 10, 10)])
S = "b1b"
prop(S, "H5", "steamwhistle_geyser (cone)", [6, 7, 6], "Basalt cone at [-16.75,4,-36] OUTSIDE the upper green's west rail\n(base x -19.75..-13.75; rail outer face x -13). Vent crater on top;\nsteam column (visual only) puffs to 60 every 20 s.", CON(5),
     [[(-3, 0), (3, 0), (1.6, 5.8), (1.0, 7), (-1.0, 7), (-1.6, 5.8)], G(R(3.25, 0, .5, 1.5))], [[(-3, 0), (3, 0), (1.6, 5.8), (1.0, 7), (-1.0, 7), (-1.6, 5.8)]], [C(0, 0, 3), ("ring", 0, 0, 1.0, 2), G(R(3.25, -3, .5, 6))])
prop(S, "H5", "geyser_platform (moving)", [3, 4, 3], "Hexagonal-look basalt platform; collider = 3×4×3 box (square faces!).\nPivot = platform top centre. Steam-vent dimple in top, brass gauge flush\non the side. Rides 0..4 at 2 studs/s.", PVf("h05_geyser_column_34.png"),
     [R(-1.5, -4, 3, 4), G(R(-1.5, -4, 3, .01))], [R(-1.5, -4, 3, 4)], [R(-1.5, -1.5, 3, 3), ("ring", 0, 0, .4, 1.5)])
prop(S, "H5", "cliff_face_w / cliff_face_e", [10.85, 3.5, 0.5], "Basalt cliff skin on the upper tier's south face, UNDER the felt slab (y 0..3.5),\nz -28.05..-28.55; two pieces either side of the shaft (x ±1.65).\nFrost streaks; rivets on the shaft side. Felt slab + rail in grey.", CON(5),
     [R(1.65, 0, 10.85, 3.5), R(-12.5, 0, 10.85, 3.5), G(R(-12.5, 3.6, 25, .4)), G(R(-1.5, 0, 3, 3.5))], [R(-.25, 0, .5, 3.5), G(R(-.25, 3.6, 3, .4))], [R(1.65, -.25, 10.85, .5), R(-12.5, -.25, 10.85, .5)])
prop(S, "H5", "signal_lamp", [0.6, 1.0, 0.4], "Green/amber steam lamp on the cliff face at [-9.5,2,-27.6], just outside\nbasin_rail7 (grey, x -8..-8.5), base y 2, top y 3. Brass housing,\nround lens facing the tee.", CON(5),
     [R(-.3, 0, .6, 1.0), G(C(0, .5, .2)), G(R(1.25, -2, .5, 1.5))], [R(-.2, 0, .4, 1.0)], [R(-.3, -.2, .6, .4)])
steps = [R(-1.5 + 0, 0, 3, .8 * (i + 1)) for i in range(5)]
prop(S, "H5", "geyser_steps", [3, 4, 12], "Timber steps for the player at [15,0,-23]: x 13.5..16.5, z -17..-29,\n5 steps (1.5 tread) rising 4 to a y-4 landing east of upper_rail11.\n3.5-high railing with solid lower board on the open (west) side.", CON(5),
     [R(-1.5, 0, 3, 4), R(-1.5, 4, .2, 3.5)], [[(6, 0)] + [p for i in range(5) for p in ((6 - 1.5 * i, 0.8 * (i + 1)), (6 - 1.5 * (i + 1), 0.8 * (i + 1)))] + [(-6, 4), (-6, 0)], R(-6, 4, 7.5, .2), R(-6, 4, .2, 3.5), R(1.3, 4 - 4 + .8 * 5 - 0.0 - 0.0, .2, 0.0001)], [R(-1.5, -6, 3, 12)] + [G(R(-1.5, -6 + 1.5 * i, 3, .05)) for i in range(6)])
prop(S, "H7", "coral clump (x10, both sides)", [3, 6, 2.4], "BRANCHING coral, not sticks: 0.5 trunk splits 2-3 times into 3-5 flattened\nfan branches with rounded swollen tips; crown ≈ 0.5 × height, depth 0.4 × height.\nHeights 3-6 (list in props.md). Bubblegum / tangerine / mint, neon tips.", PVf("h07_coral_fans_34.png"),
     branch_coral(3, 6, 1), branch_coral(2.4, 6, 3, .45), [ell(0, 0, 1.5, 1.2), G(C(0, 0, .25))])
prop(S, "H8", "giant_coral (landmark)", [7, 14, 7], "Giant coral-ice tree outside the west rail at [-10.5,0,-18].\nThick trunk (1.4) forking 3 times into wide flattened fan crowns;\nbubblegum + tangerine, glowing tips. Crown widest at 10-13.", PVf("h08_giant_coral_34.png"),
     branch_coral(7, 14, 2, 1.4), branch_coral(6, 14, 5, 1.2), [ell(0, 0, 3.5, 3.5), G(C(0, 0, .7))])
prop(S, "H8", "coral bumper skin (coral_1..7)", [2.8, 4, 1.4], "Flat-faced base EXACTLY the bumper box (grey; e.g. 2.4×1 yaw -35, top y 1.6),\nthen a branching coral cluster above 1.6, widening no more than the envelope.\nThe base faces are what the ball hits.", PVf("h08_coral_2_34.png"),
     [R(-1.2, 0, 2.4, 1.6)] + [[(x, y + 1.6 * 0 + 0) for x, y in s] if not isinstance(s, tuple) else s for s in []] + [(lambda L: L)(s) for s in branch_coral(2.8, 2.6, 4, .4) if isinstance(s, tuple)] , [R(-.5, 0, 1, 1.6)], [[(-1.2 * math.cos(.61) + .5 * math.sin(.61), 1.2 * math.sin(.61) + .5 * math.cos(.61)), (1.2 * math.cos(.61) + .5 * math.sin(.61), -1.2 * math.sin(.61) + .5 * math.cos(.61)), (1.2 * math.cos(.61) - .5 * math.sin(.61), -1.2 * math.sin(.61) - .5 * math.cos(.61)), (-1.2 * math.cos(.61) - .5 * math.sin(.61), 1.2 * math.sin(.61) - .5 * math.cos(.61))]])
# coral bumper: shift branch crown up onto the base
_cb = P[-1]; _cr = []
for s in branch_coral(2.8, 2.6, 4, .4):
    if isinstance(s, tuple): _cr.append(("c", s[1], s[2] + 1.4, s[3]))
    else: _cr.append([(x, y + 1.4) for x, y in s])
_cb["f"] = [R(-1.2, 0, 2.4, 1.6)] + _cr
_cb["s"] = [R(-.5, 0, 1, 1.6)] + [([(x * .5, y) for x, y in s] if not isinstance(s, tuple) else ("c", s[1] * .5, s[2], s[3])) for s in _cr]
# ---------------------------------------------------------------- H9-H13, H15-H17
S = "b2"
def conch(w, h):
    pts = [(w / 2 * math.cos(math.radians(a)) * (0.6 + 0.4 * a / 360), h / 2 + h / 2 * math.sin(math.radians(a)) * (0.6 + 0.4 * a / 360)) for a in range(0, 361, 15)]
    return [pts, [(w / 2, h / 2), (w / 2 + w * .05, h * .1), (w * .1, 0)]]
prop(S, "H9", "conch_entry", [5, 4.5, 5], "Giant spiral conch, candy coral-ice pink/cream with a glowing lip, lying at the\nspit end with its MOUTH over the teleport ring (ball rolls in). Mouth opening\n≥ 2 wide at felt level; spire points away from the tee.", CON(9),
     [ell(0, 2.25, 2.5, 2.25), G(ell(0, .9, 1.1, .9))], [[(-2.5, 0), (2.5, 0), (2.4, 1.8), (1.2, 3.6), (-.4, 4.5), (-1.8, 3.6), (-2.5, 2)]], [[(-2.5, 0), (-1.2, 2.5), (1.5, 2.2), (2.5, 0), (1.5, -2.2), (-1.2, -2.5)], G(ell(-1.2, 0, .9, 1.1))])
prop(S, "H9", "conch_exit", [4, 4, 4], "Twin conch on the green's east edge (teleport exit), mouth toward the cup;\nsame shape as the entry at 0.8 scale, sparkle puff at the mouth.", CON(9),
     [ell(0, 2, 2, 2), G(ell(0, .8, .9, .8))], [[(-2, 0), (2, 0), (1.9, 1.6), (1, 3.2), (-.3, 4), (-1.4, 3.2), (-2, 1.6)]], [[(-2, 0), (-1, 2), (1.2, 1.8), (2, 0), (1.2, -1.8), (-1, -2)]])
prop(S, "H10", "bobsled_hut", [5, 7, 5], "Striped red-and-cream bobsled start hut outside the run's west wall:\nboxy 4.4 cabin, steep gable roof to 7 with 0.3 overhang, brass bell under\nthe ridge, toy bobsled parked at the door.", CON(10),
     [R(-2.2, 0, 4.4, 4.2), [(-2.5, 4.2), (2.5, 4.2), (0, 7)], C(0, 3.6, .35)], [R(-2.2, 0, 4.4, 4.2), R(-2.5, 4.2, 5, 2.8)], [R(-2.5, -2.5, 5, 5), G(R(-.05, -2.5, .1, 5))])
prop(S, "H11", "fishing_hut", [3, 6, 3], "Snowpuff ice-fishing hut on the berg: striped canvas A-tent 3 × 3,\nstove-pipe chimney to 6 puffing steam; fishing hole + rod beside it.", CON(11),
     [[(-1.5, 0), (1.5, 0), (0, 4.2)], R(.6, 2.5, .25, 3.5)], [R(-1.5, 0, 3, 3.6), [(-1.5, 3.6), (1.5, 3.6), (0, 4.2)], R(.4, 2.5, .25, 3.5)], [R(-1.5, -1.5, 3, 3), G(C(.7, .7, .15))])
prop(S, "H11", "ice_floe (moving)", [7, 1.2, 1.0], "Slab 6.4 long × 1.0 wide × 0.636 thick with 45° pointed ends to x ±3.5\n(collider, grey). Snow + mini snowpuff on top ≤ 1.2 high INSIDE the footprint.\nPivot = floe centre; slides -7..0 on x.", CON(11),
     [[(-3.5, .318), (-3.2, 0), (3.2, 0), (3.5, .318), (3.2, .636), (-3.2, .636)], [(-2.6, .636), (2.6, .636), (2, .9), (-2.2, .85)], ell(1.2, .95, .25, .25)], [R(-.5, 0, 1, .636), R(-.4, .636, .8, .25)], [[(-3.5, 0), (-3.0, -.5), (3.0, -.5), (3.5, 0), (3.0, .5), (-3.0, .5)]])
prop(S, "H12", "icebreaker", [16, 8, 6], "Beached toy icebreaker straddling the channel: red hull (faces = hull13-18 colliders),\ncream deckhouse, red funnel to 8 puffing steam. 2.4-wide paddle slot\nkept clear (grey). Bow points west.", CON(12),
     [[(-8, 3), (-6, 0), (7, 0), (8, 3)], R(-3, 3, 7, 2.2), R(1.5, 5.2, 1.4, 2.8), G(R(-1.2, 0, 2.4, 3))], [[(-3, 3), (-2.4, 0), (2.4, 0), (3, 3)], R(-1.8, 3, 3.6, 2.2), R(-.7, 5.2, 1.4, 2.8)], [[(-8, 0), (-5, -3), (8, -3), (8, 3), (-5, 3)], G(R(-1.2, -3, 2.4, 6))])
pw = []
for k in range(4):
    a = k * math.pi / 2; ca, sa = math.cos(a), math.sin(a)
    for pts in ([(-1.2, .6), (1.2, .6), (1.2, 4.1), (-1.2, 4.1)],):
        pw.append([(x * ca - y * sa, x * sa + y * ca + 4.16) for x, y in pts])
prop(S, "H12", "paddle_wheel (moving)", [8.2, 8.2, 0.4], "Red-and-cream paddle wheel, pivot = hub [0,4.16], axis +Z, 30°/s.\n4 broad timber paddles 2.4 wide × 0.4 thick, r 0.6 → 4.1 (lowest edge 0.06 over\nfelt). Rims/spokes only at r ≤ 3.9 within z ±0.2.", CON(12),
     [("ring", 0, 4.16, 3.9, 3)] + [C(0, 4.16, .6)] + [[(-1.2, 4.16 - 4.1), (1.2, 4.16 - 4.1), (1.2, 4.16 - .6), (-1.2, 4.16 - .6)], [(-1.2, 4.16 + .6), (1.2, 4.16 + .6), (1.2, 8.26), (-1.2, 8.26)], [(-4.1, 2.96), (-.6, 2.96), (-.6, 5.36), (-4.1, 5.36)], [(.6, 2.96), (4.1, 2.96), (4.1, 5.36), (.6, 5.36)]],
     [R(-.2, .06, .4, 8.2)], [R(-4.1, -.2, 8.2, .4)])
prop(S, "H13", "carousel_canopy + hub", [16, 12, 16], "Brass-and-ice carousel: striped canopy (underside y 9, ≥ 8 over felt) on a central\nbrass pole 0.8; snowpuff weathervane to 12. Hub base r 7.5 × 1.2 (48-sided, grey\ncollider strips) - not a playing surface.", CON(13),
     [[(-8, 9), (8, 9), (6, 10.6), (0, 11.2), (-6, 10.6)], R(-.4, 1.2, .8, 7.8), R(-.1, 11.2, .2, .8), R(-7.5, 0, 15, 1.2)], [[(-8, 9), (8, 9), (6, 10.6), (0, 11.2), (-6, 10.6)], R(-.4, 1.2, .8, 7.8), R(-7.5, 0, 15, 1.2)], [C(0, 0, 8), G(("ring", 0, 0, 7.5, 1))])
prop(S, "H13", "carousel_arms (moving)", [23, 0.9, 3.6], "4 sled-runner arms at 0/90/180/270, runners r 8.2..11.5 × 0.9 high × 3.6 wide\n(mesh = collider). Sleds + snowpuffs above 0.9 inside the footprint, < 4.\nSpokes ≥ 1.4 over felt at r < 8.2. Pivot = hub centre, +Y, 15°/s.", CON(13),
     [R(-11.5, 0, 3.3, .9), R(8.2, 0, 3.3, .9), R(-8.2, 1.4, 16.4, .3), G(R(-7.5, 0, 15, 1.2))], [R(-11.5, 0, 3.3, .9), R(8.2, 0, 3.3, .9), R(-8.2, 1.4, 16.4, .3)],
     [R(8.2, -1.8, 3.3, 3.6), R(-11.5, -1.8, 3.3, 3.6), R(-1.8, 8.2, 3.6, 3.3), R(-1.8, -11.5, 3.6, 3.3), G(C(0, 0, 7.5))])
S = "b2b"
prop(S, "H15", "lip_ice", [7, 4, 1], "Frozen-fall lip: glassy icicle curtain down the 4-stud step under the lane's\nopen end (y -4..0 local, here 0..4). Ragged icicle bottom edge, flat top flush\nunder the felt edge.", CON(15),
     [[(-3.5, 4), (3.5, 4)] + [(3.5 - .5 * i, (0.0 if i % 2 else 0.8)) for i in range(15)]], [[(-.5, 4), (.5, 4), (.3, 0), (-.2, .6)]], [R(-3.5, -.5, 7, 1)])
prop(S, "H15", "great_frozen_falls (envelope)", [26, 40, 8], "World mesh east of the basin (anchor = view cue): a 26-wide frozen cascade\npouring off the terrace edge into the cloud sea. Bulging ice tiers, vertical\nflutes; wider at the bottom.", CON(15),
     [[(-11, 40), (11, 40), (12, 26), (13, 12), (13, 0), (-13, 0), (-12, 14), (-12, 28)]], [[(-4, 40), (0, 40), (2, 26), (4, 0), (-4, 0), (-4, 20)]], [R(-13, -4, 26, 8)])
prop(S, "H16", "moonwell", [20, 2, 18], "Moonstone well: pale pearl coping round the funnel (rail skins y -1.3..1.0,\nshown 0..2.3), felt slopes dressed as worn moonstone flags, glowing\nice-crystal crescent spout at z -30.", CON(16),
     [R(-10, 0, 1, 2.3), R(9, 0, 1, 2.3), G([(-9, 1.3), (0, .5), (9, 1.3)])], [R(-9, 0, 1, 2.3), R(8, 0, 1, 2.3)], [("ring", 0, 0, 9.0, 6), G(C(0, -8, .8))])
prop(S, "H17", "crystal_piers (x2)", [3, 1.5, 9], "Two glowing crystal piers 3 wide × 9 long reaching from both rims toward\neach other (z -20.5 / -37.5); frosted ice rails; deck ≥ 0.6 thick or skirt to\ny -0.6. Crystal prisms under the deck ends.", CON(17),
     [R(-1.5, -.6, 3, .6), R(-1.5, 0, .4, 1.5), R(1.1, 0, .4, 1.5), [(-1, -.6), (0, -2.5), (1, -.6)]], [R(-4.5, -.6, 9, .6), R(-4.5, 0, 9, 1.2), [(3, -.6), (4, -3), (4.5, -.6)]], [R(-1.5, -4.5, 3, 9)])
prop(S, "H17", "span_lamp", [0.6, 2.4, 0.6], "Crystal timing lamp beside the pier mouth at [-2.4,0,-15]: hex crystal on a\nshort post; glows mint (span solid), violet (fading), dark (gone).", CON(17),
     [R(-.15, 0, .3, 1.4), [(-.3, 1.4), (.3, 1.4), (.3, 2.1), (0, 2.4), (-.3, 2.1)]], [R(-.15, 0, .3, 1.4), [(-.3, 1.4), (.3, 1.4), (.3, 2.1), (0, 2.4), (-.3, 2.1)]], [C(0, 0, .3)])
prop(S, "H17", "aurora_ribbon + light_span", [3, 60, 8], "Neon ribbon pouring out of the sky (mint #5CFFB0 → violet #B07CFF), only above\ny 10 (grey = clear zone), pooling into the light span deck 3 × 0.4 × 8 (felt\n`light_span`). Toggle 9 s cycle, collider only while solid.", CON(17),
     [R(-1.5, 0, 3, .4), [(-1.5, 10), (1.5, 10), (2.5, 35), (1, 60), (-1, 60), (-2.5, 35)], G(R(-1.5, .4, 3, 9.6))], [R(-4, 0, 8, .4), [(-4, 10), (4, 10), (3, 35), (5, 60), (-3, 60), (-2, 35)]], [R(-1.5, -4, 3, 8)])
if __name__ == "__main__":
    sheet("b1", "Aurora Archipelago - silhouettes, batch 1 (H1, H2, H3)  |  studs  |  black = prop, grey = context", os.path.join(HERE, "sheet01-batch1-h01-h03.png"))
    sheet("b1b", "Aurora Archipelago - silhouettes, batch 1 (H5, H7, H8)  |  studs  |  black = prop, grey = context", os.path.join(HERE, "sheet02-batch1-h05-h08.png"))
    sheet("b2", "Aurora Archipelago - silhouettes (H9-H13)  |  studs  |  black = prop, grey = context", os.path.join(HERE, "sheet03-h09-h13.png"))
    sheet("b2b", "Aurora Archipelago - silhouettes (H15-H17)  |  studs  |  black = prop, grey = context", os.path.join(HERE, "sheet04-h15-h17.png"))
