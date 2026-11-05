"""Pass 6 (holes.json v2, playtest Rounds 5/6): new static decoration props. No collision (decoration only).

  cup_flag_h01..h09        cup flag per hole (pass 7: banded pole + big red-and-cream pennant + hole number)
  h2_chute_sign_left/right arrow fingerposts outside the H2 lane rails ('Bold Line' + rabbit / 'Safe Line')
  h2_chute_arrow_decal     glowing leaf-arrow decal flush on the H2 felt (x2)
  h4_side_gap_post         small lantern posts on the H4 plaza rail tops (x2)
  h5_respawn_stone         glowing marker stone flush in the H5 felt at the root-bridge entry (stream respawn point)
  h8_alcove_bank_cladding  root-bark skin on the H8 alcove back-wall bank (flush on the banked felt plane)
  h8_door_pocket           root-knot pockets the H8 root door slides into (x2)
  h9_pendulum_root_beam    root beam (+ root legs) the H9 lantern pendulum hangs from
  h9_tunnel_dip_trim       root-and-moss trim under the H9 tunnel rails following the 0.4 rolling dip
Placements are computed from ../holes.json (source of truth) at import time.
"""
import math, random
import bmesh
from mathutils import Vector, Matrix
from registry import prop
from lglib import M, R, TAU, text_bm
import lglib
import dressing_lib as DL

FONT = "/usr/share/fonts/truetype/sand-box/google/Lilita One/LilitaOne-Regular.ttf"
HOLES = {h["number"]: h for h in DL.load_holes()}


def _yaw_to(src, dst):
    """yaw (deg) that turns local +Z toward dst (hole-local x/z): local +Z -> (sin yaw, cos yaw)."""
    dx, dz = dst[0] - src[0], dst[2] - src[2]
    return round(math.degrees(math.atan2(dx, dz)), 2)


def _anchor(n, name):
    return [a for a in HOLES[n]["decoration_anchors"] if a["name"] == name][0]


# ============================================================================ cup flags
# pass 7 (legibility from the tee): bigger bright red-and-cream pennant + thicker banded pole. The pole top (gold knob)
# stays exactly at holes.json cup.flag.top; holes.json pole_diameter / banner_size (0.15, 2.0 x 1.2) are the Round-5
# minimums, these are the visual sizes (still collision false).
FLAG_POLE_D = 0.30                    # was holes.json 0.15
FLAG_BANNER = (3.2, 2.0, 0.08)        # pennant length from the pole, hoist height, thickness (was 2.0 x 1.2 x 0.05)
FLAG_TIP_H = 1.1                      # pennant height at the free end (tapers from FLAG_BANNER[1] at the hoist)
FLAG_TOP_GAP = 0.22                   # banner top edge this far under the pole top (the knob sits above it)


def _pennant(pb, mat, w, h0, h1, t, x0, z0, amp=0.1, nx=12):
    """Tapered pennant in the local x-z (Blender) plane: x0..x0+w, top edge z0, bottom edge z0 - h(u) with h going
    h0 -> h1; a gentle wave in y grows away from the pole. Returns (wave(u), bottom(u))."""
    wave = lambda u: amp * u * math.sin(u * math.pi * 1.6)
    bot = lambda u: z0 - (h0 + (h1 - h0) * u)
    b = bmesh.new()
    rows = []
    for side in (-1, 1):
        row = []
        for i in range(nx + 1):
            u = i / nx
            x, y = x0 + w * u, wave(u) + side * t / 2
            row.append((b.verts.new((x, y, z0)), b.verts.new((x, y, bot(u)))))
        rows.append(row)
    f, k = rows[1], rows[0]
    for i in range(nx):
        b.faces.new((f[i][0], f[i][1], f[i + 1][1], f[i + 1][0]))
        b.faces.new((k[i][0], k[i + 1][0], k[i + 1][1], k[i][1]))
        b.faces.new((f[i][0], f[i + 1][0], k[i + 1][0], k[i][0]))
        b.faces.new((f[i][1], k[i][1], k[i + 1][1], f[i + 1][1]))
    b.faces.new((f[0][0], k[0][0], k[0][1], f[0][1]))
    b.faces.new((f[nx][0], f[nx][1], k[nx][1], k[nx][0]))
    bmesh.ops.recalc_face_normals(b, faces=b.faces)
    pb.add(mat, b)
    return wave, bot


def _face_strip(pb, mat, x0, w, u0, u1, ztop, zbot, wave, y_off, sgn, nx=12):
    """One-sided strip on a pennant face (sgn -1 = front, Blender -Y; +1 = back), following the wave.
    ztop(u) / zbot(u) give the strip edges."""
    b = bmesh.new()
    cols = []
    for i in range(nx + 1):
        u = u0 + (u1 - u0) * i / nx
        x, y = x0 + w * u, wave(u) + sgn * y_off
        cols.append((b.verts.new((x, y, zbot(u))), b.verts.new((x, y, ztop(u)))))
    for i in range(nx):
        q = (cols[i][0], cols[i + 1][0], cols[i + 1][1], cols[i][1])       # CCW seen from -Y -> normal -Y
        b.faces.new(q if sgn < 0 else q[::-1])
    pb.add(mat, b)


def _cup_flag(n):
    h = HOLES[n]
    fl = h["cup"]["flag"]
    H_ = fl["pole_height"]
    bw, bh, bt = FLAG_BANNER

    def fn(pb):
        r = FLAG_POLE_D / 2
        pb.cyl("Cream", r, r, H_ + 0.25, 12, loc=(0, 0, (H_ - 0.25) / 2))               # pole (0.25 down the cup)
        z = 0.45
        while z < H_ - bh - 0.9:                         # red bands (red-and-cream pole), tops >= 0.48 under the pennant
            pb.cyl("FlagRed", r + 0.012, r + 0.012, 0.42, 12, loc=(0, 0, z + 0.21), smooth=False)
            z += 0.84
        pb.cyl("Iron", r + 0.03, r + 0.03, 0.08, 12, loc=(0, 0, 0.04), smooth=False)  # ferrule at the felt
        pb.sphere("CapGold", r + 0.07, loc=(0, 0, H_), segs=10, rings=6)               # top knob = flag.top
        # pennant: hoist at the pole, top edge FLAG_TOP_GAP under the pole top. Front = Roblox +Z (Blender -Y)
        x0, z0 = r * 0.5, H_ - FLAG_TOP_GAP
        wave, bot = _pennant(pb, "FlagRed", bw, bh, FLAG_TIP_H, bt, x0, z0)
        yo = bt / 2 + 0.006
        hoist_u = 0.42 / bw
        for sgn in (-1, 1):
            # cream hoist band, cream top + bottom borders (both faces)
            _face_strip(pb, "Cream", x0, bw, 0.0, hoist_u, lambda u: z0 - 0.02, lambda u: bot(u) + 0.02, wave, yo, sgn, 2)
            _face_strip(pb, "Cream", x0, bw, hoist_u, 0.97, lambda u: z0 - 0.02, lambda u: z0 - 0.2, wave, yo, sgn)
            _face_strip(pb, "Cream", x0, bw, hoist_u, 0.97, lambda u: bot(u) + 0.2, lambda u: bot(u) + 0.02, wave, yo,
                        sgn)
            # big cream hole number in the red field, reading correctly on each face
            un = (0.42 + 0.72) / bw
            zc = (z0 + bot(un)) / 2
            t = text_bm(str(n), size=1.45, extrude=0.014, font_path=FONT)
            zs = [v.co.z for v in t.verts]
            zmid = (max(zs) + min(zs)) / 2
            rot = Matrix.Identity(4) if sgn < 0 else Matrix.Rotation(math.pi, 4, "Z")
            yy = max(wave(un - 0.12), wave(un), wave(un + 0.12)) if sgn > 0 else min(wave(un - 0.12), wave(un), wave(un + 0.12))
            pb.add("Cream", t, Matrix.Translation((x0 + bw * un, yy + sgn * (bt / 2 + 0.004), zc - zmid)) @ rot)
        # small gold tie rings where the pennant meets the pole
        for zz in (z0 - 0.12, z0 - bh + 0.12):
            pb.torus("CapGold", r + 0.03, 0.035, 12, 4, loc=(0, 0, zz))
    return fn


for _n, _h in HOLES.items():
    _fl = _h["cup"]["flag"]
    _cup = _h["cup"]["position"]
    _yaw = _yaw_to(_cup, _h["tee"]["position"])
    prop(f"cup_flag_h{_n:02d}", [f"H{_n}"], "P1", target=[FLAG_BANNER[0], _fl["pole_height"], FLAG_POLE_D],
         group="flags", origin="pole foot at the cup centre on the felt (pole runs 0.25 down into the cup)",
         front="+Z = banner face (yaw it toward the tee)",
         notes=(f"H{_n} cup flag (pass 7: enlarged for legibility from the tee): {_fl['pole_height']}-stud pole, "
                f"{FLAG_POLE_D} dia with red/cream bands (holes.json minimum {_fl['pole_diameter']}), "
                f"{FLAG_BANNER[0]} x {FLAG_BANNER[1]} tapered {_fl['banner_color']} pennant (tip {FLAG_TIP_H} tall; "
                f"holes.json minimum {_fl['banner_size'][0]}x{_fl['banner_size'][1]}) with a cream hoist band, cream "
                "borders and a big cream hole number on both faces, gold knob at the pole top (= holes.json "
                "cup.flag.top, unchanged). NO COLLISION: CanCollide/CanTouch/CanQuery = false "
                "(the ball passes through it; holes.json cup.flag.collision = false)."),
         placements=[dict(hole=f"H{_n}", pos=list(_cup), yaw=_yaw, collision=False,
                          flag_top=list(_fl["top"]), note="pos = cup.position; yaw turns the banner face to the tee")]
         )(_cup_flag(_n))


# ============================================================================ H2 chute signs + felt arrows
def _chute_sign(text, rabbit):
    def fn(pb):
        # post (0.25 square, 3.2 tall) + slate footing
        pb.box("Slate", (0.42, 0.42, 0.2), loc=(0, 0, 0.1), bevel=0.05)
        pb.box("Oak", (0.25, 0.25, 3.0), loc=(0, 0, 1.6), bevel=0.03)
        pb.cyl("Shingle", 0.24, 0.02, 0.2, 4, loc=(0, 0, 3.2), rot=(0, 0, 45), smooth=False)
        # arrow board along local -Z (Blender +Y): 1.8 long, tip at the far end, faces = +-X
        L, Hb, T = 1.8, 0.6, 0.12
        y0, y1 = -0.35, -0.35 + L
        poly = [(y0, -Hb / 2), (y1 - 0.45, -Hb / 2), (y1 - 0.45, -Hb / 2 - 0.14), (y1, 0.0),
                (y1 - 0.45, Hb / 2 + 0.14), (y1 - 0.45, Hb / 2), (y0, Hb / 2)]
        # prism poly is (x, y) extruded along z -> map: poly x -> Blender Y, poly y -> Blender Z, depth -> Blender X
        Mb = Matrix.Translation((0, 0, 2.55)) @ Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
        pb.prism("Oak", poly, T, matrix=Mb)
        pb.prism("RootBark", [(y0 - 0.04, -Hb / 2 - 0.04), (y0 + 0.08, -Hb / 2 - 0.04), (y0 + 0.08, Hb / 2 + 0.04),
                              (y0 - 0.04, Hb / 2 + 0.04)], T + 0.04, matrix=Mb)
        for sx in (-1, 1):
            # text on both faces, reading along the board; face normal = sx * Blender X
            t = text_bm(text, size=0.24, extrude=0.01, font_path=FONT)
            rz = Matrix.Rotation(math.radians(90 if sx > 0 else -90), 4, "Z")   # text faces -Y -> faces +-X
            yt = 0.55 if not rabbit else 0.66
            pb.add("Cream", t, Matrix.Translation((sx * (T / 2 + 0.012), yt, 2.47)) @ rz)
            if rabbit:      # little rabbit head (2 ears) near the post end
                yb = y0 + 0.24
                xx = sx * (T / 2 + 0.012)
                pb.sphere("Cream", 0.1, loc=(xx, yb, 2.5), scale=(0.25, 1, 1), segs=8, rings=5)
                for dy in (-0.05, 0.05):
                    pb.sphere("Cream", 0.045, loc=(xx, yb + dy, 2.68), scale=(0.25, 0.8, 2.2), segs=6, rings=4)
        # hanging mini lantern under the board tip end
        pb.torus("Iron", 0.04, 0.012, 6, 3, loc=(0, y1 - 0.6, 2.2), rot=(90, 0, 90))
        pb.lantern(0.36, loc=(0, y1 - 0.6, 1.78), hook=False)
    return fn


for _side, _text, _rab in (("left", "Bold Line", True), ("right", "Safe Line", False)):
    _a = _anchor(2, f"chute_sign_{_side}")
    _f = _a["facing"]
    _yaw = round(math.degrees(math.atan2(-_f[0], -_f[1])), 2)       # local -Z -> facing
    prop(f"h2_chute_sign_{_side}", ["H2"], "P1", target=list(_a["approx_size"]), group="hero",
         origin="post foot centre on the ground", front="arrow board points along local -Z",
         notes=(f"Fingerpost outside the H2 lane {_side} rail: '{_text}'" + (" + rabbit icon" if _rab else "") +
                " carved on both faces of a 1.8-long arrow board (at 2.25-2.85 high) that points into the "
                f"{_side} chute (holes.json facing {_f}); mini lantern under the tip (Neon core)."),
         placements=[dict(hole="H2", pos=list(_a["position"]), yaw=_yaw, note=f"local -Z = facing {_f}")]
         )(_chute_sign(_text, _rab))


@prop("h2_chute_arrow_decal", ["H2"], "P1", target=[1.4, 0.01, 2.0], group="hero",
      origin="centre, bottom on the felt top (0.01 thick)", front="arrow points local -Z",
      notes="Glowing leaf-arrow decal flush on the H2 lane felt (0.01 thick, Neon), pointing -Z into each chute. "
            "Decal only: no collision, sits ON the felt.",
      placements=[dict(hole="H2", pos=list(_anchor(2, f"chute_arrow_{s}")["position"]), yaw=0) for s in ("left", "right")])
def chute_arrow(pb):
    # leaf body (ellipse) + chevron head pointing Blender +Y (= Roblox -Z), all 0.01 thick
    leaf = [(0.32 * math.sin(math.pi * i / 16) * (1 - 0.25 * (i / 16)), -1.0 + 1.25 * i / 16) for i in range(17)]
    poly = [(x, y) for x, y in leaf] + [(-x, y) for x, y in reversed(leaf[1:-1])]
    pb.prism("Glow", poly, 0.008, loc=(0, 0, 0.004))
    head = [(-0.7, 0.25), (0.0, 1.0), (0.7, 0.25), (0.42, 0.25), (0.0, 0.66), (-0.42, 0.25)]
    pb.prism("Firefly", head, 0.01, loc=(0, 0, 0.005))
    pb.prism("Moss", [(-0.03, -0.95), (0.03, -0.95), (0.03, 0.2), (-0.03, 0.2)], 0.01, loc=(0, 0, 0.005))


# ============================================================================ H4 side-gap lantern posts
_h4 = HOLES[4]
_rail_top = {w["id"]: w["center"][1] + w["size"][1] / 2 for w in _h4["walls"]}
_sg = _anchor(4, "side_gap_lanterns")["position"]


@prop("h4_side_gap_post", ["H4"], "P2", target=[0.4, 2.5, 0.4], group="hero",
      origin="post foot centre, on the rail top", front="lantern hangs toward local +X",
      notes="Small timber lantern post standing ON the H4 plaza rail tops (x = +-7.25, z -17) to mark the side gaps. "
            "Paper lantern on top (Neon core: PointLight Range 8, Brightness 1, #FFB347).",
      placements=[dict(hole="H4", pos=[-_sg[0], _rail_top["rail3"], _sg[2]], yaw=180, note="west plaza rail top"),
                  dict(hole="H4", pos=[_sg[0], _rail_top["rail13"], _sg[2]], yaw=0, note="east plaza rail top")])
def side_gap_post(pb):
    pb.box("Iron", (0.4, 0.4, 0.06), loc=(0, 0, 0.03))
    pb.box("Oak", (0.22, 0.22, 1.7), loc=(0, 0, 0.9), bevel=0.03)
    pb.box("RootBark", (0.36, 0.36, 0.08), loc=(0, 0, 1.78))
    pb.lantern(0.62, loc=(0, 0, 1.82), hook=False)
    pb.cyl("Shingle", 0.22, 0.02, 0.1, 4, loc=(0, 0, 2.45), rot=(0, 0, 45), smooth=False)


# ============================================================================ H5 respawn stone
_rs = HOLES[5]["hazards"][0].get("respawn") or _anchor(5, "bridge_respawn_stone")["position"]


@prop("h5_respawn_stone", ["H5"], "P2", target=[0.8, 0.02, 0.8], group="hero",
      origin="centre, bottom on the felt top (0.02 tall: flush)", front="n/a",
      notes="Glowing mossy marker stone set flush in the H5 felt at the root-bridge entry: the stream hazard's "
            "respawn point (holes.json hazards[stream].respawn). 0.02 tall, no collision.",
      placements=[dict(hole="H5", pos=list(_rs), yaw=0, note="= holes.json stream respawn point")])
def respawn_stone(pb):
    poly = [(0.4 * math.cos(TAU * k / 10 + 0.2) * (1 + 0.04 * math.sin(k * 2.3)),
             0.4 * math.sin(TAU * k / 10 + 0.2) * (1 + 0.04 * math.sin(k * 2.3))) for k in range(10)]
    pb.prism("Slate", poly, 0.014, loc=(0, 0, 0.007))
    pb.prism("Moss", [(x * 0.92, y * 0.92) for x, y in poly[:4]] + [(0, 0)], 0.004, loc=(0, 0, 0.016))
    ring = []
    for k in range(16):
        a = TAU * k / 16
        ring.append((0.22 * math.cos(a), 0.22 * math.sin(a)))
    inner = [(x * 0.7, y * 0.7) for x, y in ring]
    for k in range(16):           # glowing rune ring (16 thin segments)
        q = [ring[k], ring[(k + 1) % 16], inner[(k + 1) % 16], inner[k]]
        pb.prism("ShroomGlow", q, 0.004, loc=(0, 0, 0.016))
    pb.prism("ShroomGlow", [(-0.05, -0.05), (0.05, -0.05), (0.05, 0.05), (-0.05, 0.05)], 0.004, loc=(0, 0, 0.016))


# ============================================================================ H8 alcove bank cladding
_ab = [f for f in HOLES[8]["felt"] if f["id"] == "alcove_bank"][0]


def _bank_y(x_local_hole):
    """Height of the alcove_bank plane at hole-local x (planar, from holes.json: yaw 180, slope x, rise -0.5)."""
    c = _ab["center"]
    sx = _ab["size"][0]
    yaw = math.radians(_ab.get("yaw", 0))
    # piece-local x of a hole point: lx = dx*cos(yaw) - dz*sin(yaw) (dz = 0 along the centre line)
    lx = (x_local_hole - c[0]) * math.cos(yaw)
    return c[1] + _ab["slope"]["rise"] * lx / sx


@prop("h8_alcove_bank_cladding", ["H8"], "P1", target=list(_anchor(8, "alcove_bank_cladding")["approx_size"]),
      group="hero", origin="hole-local (8.35, 0, -11.5): bank centre line, base y 0 (= the bank's low edge)",
      front="n/a",
      notes=("Stone skin laid ON the H8 alcove back-wall bank (holes.json felt 'alcove_bank': x 7.7..9, z -8..-15, "
             "rising 0.5 to the east against rail15). Its top follows the banked plane 0.02 above it (never more "
             "than 0.03), so the ball rolls on the real felt plane under it. No collision. v210b: Limestone #B8AFA0 "
             "(was RootBark #5B3A22), one part __Limestone; the 5 moss streaks (overlapping coplanar boxes) removed."),
      placements=[dict(hole="H8", pos=list(_anchor(8, "alcove_bank_cladding")["position"]), yaw=0)])
def alcove_cladding(pb):
    cx = _anchor(8, "alcove_bank_cladding")["position"][0]
    x0, x1 = _ab["center"][0] - _ab["size"][0] / 2, _ab["center"][0] + _ab["size"][0] / 2
    z0, z1 = _ab["center"][2] - _ab["size"][1] / 2, _ab["center"][2] + _ab["size"][1] / 2
    nx, nz = 4, 14
    b = bmesh.new()
    top, bot = [], []
    for i in range(nx + 1):
        xh = x0 + (x1 - x0) * i / nx
        rt, rb = [], []
        for j in range(nz + 1):
            zh = z0 + (z1 - z0) * j / nz
            y = _bank_y(xh)
            rt.append(b.verts.new(R(xh - cx, y + 0.02, zh + 11.5)))
            rb.append(b.verts.new(R(xh - cx, y - 0.06, zh + 11.5)))
        top.append(rt)
        bot.append(rb)
    for i in range(nx):
        for j in range(nz):
            b.faces.new((top[i][j], top[i + 1][j], top[i + 1][j + 1], top[i][j + 1]))
            b.faces.new((bot[i][j], bot[i][j + 1], bot[i + 1][j + 1], bot[i + 1][j]))
    for i in range(nx):
        for G, j in ((0, 0), (1, nz)):
            b.faces.new((top[i][j], bot[i][j], bot[i + 1][j], top[i + 1][j]))
    for j in range(nz):
        for i in (0, nx):
            b.faces.new((top[i][j], top[i][j + 1], bot[i][j + 1], bot[i][j]))
    bmesh.ops.recalc_face_normals(b, faces=b.faces)
    pb.add("Limestone", b)          # v210b: bank backing renders as stone (was RootBark)
    # v210b: the 5 flush moss streaks are gone (not stone; 2 of them overlapped coplanar = z-fighting)


# ============================================================================ H8 door pockets
_door = [m for m in HOLES[8]["moving_parts"] if m["id"] == "root_door"][0]
_rails8 = {w["id"]: w for w in HOLES[8]["walls"]}


def _pocket_z():
    """Rail lines the door crosses (outer faces) and how far the door end gets past them."""
    piv = _door["pivot"]
    half = _door["blockers"][0]["size"][2] / 2
    lo, hi = _door["range"]
    out = []
    for rid in ("rail16", "rail14"):
        w = _rails8[rid]
        zc = w["center"][2]
        sgn = 1 if zc > piv[2] else -1
        reach = piv[2] + sgn * (half + (hi if sgn > 0 else -lo))
        if (reach - (zc - sgn * w["size"][0] / 2)) * sgn > 0:      # Round 7: only ends that cross the rail line
            out.append((rid, zc, sgn, reach))
    return out


# Round 7: how far the door end gets past the rail centre line (1.35 in pass 6, 2.05 now) -> pocket depth
POCKET_D = max([abs(reach - zc) for (_r, zc, _s, reach) in _pocket_z()] or [1.35])
# v210 (door clearance review): the whole pocket mesh is scaled X x1.4 about the origin (x 0 = door centre line),
# raised +0.17 and moved 0.05 deeper (local -Z = away from the door). Origin / placement unchanged, so the Studio
# CFrame stays the same; only the FBX geometry moves. Door <-> pocket mesh clearance over the whole slide >= 0.187.
POCKET_SX, POCKET_RAISE, POCKET_DEEPER = 1.4, 0.17, 0.05


@prop("h8_door_pocket", ["H8"], "P1", target=[1.3, 1.5, POCKET_D + 0.7], group="hero",
      origin="centre of the junction rail line under the door path, base on the felt level (y 0)",
      front="+Z = the slot side (faces the felt / door); yaw 180 = north rail16, 0 = south rail14",
      notes=("Root-knot pocket the H8 root door slides into where its travel crosses a junction rail line. Round 7: "
             "only the south one (rail16, z -7.75): open (+4) the door end passes the rail centre line by "
             f"{POCKET_D:.2f}; the north end never reaches rail14. A hollow bark housing (inner slot "
             f"{0.95 * POCKET_SX:.2f} wide x 1.2 high from y {POCKET_RAISE:g}, {POCKET_D + 0.25 + POCKET_DEEPER:.2f} "
             "deep from the rail's inner face) straddles the rail. v210: mesh scaled X x1.4 about the origin, raised "
             f"+{POCKET_RAISE:g}, {POCKET_DEEPER:g} deeper (away from the door); origin/placement unchanged; "
             "door <-> pocket clearance >= 0.187 over the whole slide. "
             "In Studio, NOTCH the visual rail kit over x 4.2..5.3 where a pocket sits (the invisible collision "
             "rail stays). No collision."),
      placements=[dict(hole="H8", pos=[_door["pivot"][0], 0.0, zc], yaw=(180 if sgn > 0 else 0),
                       note=f"{rid}: door end reaches z {reach:.2f}") for (rid, zc, sgn, reach) in _pocket_z()])
def door_pocket(pb):
    # local: +Z (Blender -Y) toward the door / felt side. Rail line at 0 (rail 0.5 thick: z -0.25..0.25).
    # housing walls at |x| 0.48..0.68, roof 1.2..1.45, back plate at z -1.62 (door end reaches z -1.35)
    D = POCKET_D                       # door end reaches local z -D (pass 6: 1.35; Round 7: 2.05)
    # v210: everything below goes through this frame (Blender: +Y = local -Z = deeper, +Z = up)
    pb.frame = pb.frame @ Matrix.Translation((0, POCKET_DEEPER, POCKET_RAISE)) @ Matrix.Diagonal((POCKET_SX, 1, 1, 1))
    L = D - 0.05
    for sx in (-1, 1):
        pb.box("RootBark", (0.22, 1.8, L), loc=R(sx * 0.58, 0.65, -L / 2), bevel=0.06)
    pb.box("RootBark", (1.36, 1.8, 0.26), loc=R(0, 1.33, -L / 2), bevel=0.08)
    pb.box("RootBark", (1.36, 0.22, 1.45), loc=R(0, 0.72, -(D + 0.27)), bevel=0.06)
    # knotted root mass over the top + flared slot lips
    for k, (x, z, s) in enumerate(((-0.3, -0.9 * D / 1.35, 0.7), (0.35, -0.4, 0.65), (0.0, -1.4 * D / 1.35, 0.6))):
        pb.rock("RootBark", (s, s, s * 0.7), loc=R(x, 1.42, z), seed=40 + k, amp=0.2, smooth=True)
    for sx in (-1, 1):
        pb.tube("RootBark", [R(sx * 0.62, 0.05, 0.13), R(sx * 0.64, 0.7, 0.14), R(sx * 0.5, 1.35, 0.12)],
                [0.1, 0.09, 0.07], 6, wobble=0.1, seed=sx + 3)
    pb.sphere("Moss", 0.5, loc=R(0, 1.62, -0.7 * D / 1.35), scale=(1.2, 1.6 * D / 1.35, 0.3), segs=8, rings=4)
    pb.cyl("Cream", 0.04, 0.05, 0.2, 6, loc=R(0.62, 1.55, -0.1))
    pb.sphere("ShroomGlow", 0.11, loc=R(0.62, 1.67, -0.1), scale=(1, 1, 0.55), segs=8, rings=4)


# ============================================================================ H9 pendulum root beam
_pend = [m for m in HOLES[9]["moving_parts"] if m["id"] == "lantern_pendulum"][0]
_PV = _pend["pivot"]
# pass 9 (Round 8): the hinge moved to x 21.2 but the beam stays centred on its anchor (x 22): beam, legs and side
# lanterns are offset by anchor x - hinge x; only the hinge bracket stays at the origin (= hinge)
_BEAM_DX = [a for a in HOLES[9]["decoration_anchors"] if a["name"] == "pendulum_beam"][0]["position"][0] - _PV[0]


@prop("h9_pendulum_root_beam", ["H9"], "P1", target=[16, 1.2, 1.2], group="hero",
      origin=f"the pendulum HINGE (course-local H9 {list(_PV)}); beam bottom 0.25 above it; beam centred "
             f"{_BEAM_DX:+.2f} along X from the hinge (on its anchor)",
      front="spans local X",
      notes=("Gnarled root beam spanning the H9 chamber at y 9.2..10.4 over z -38.5 (beam x 14..30 = 16 long, "
             "1.2 thick), iron hinge bracket at the hinge (Round 8: x 21.2, 0.8 west of the beam middle) (the h9_lantern_pendulum hinge pin sits in it). The beam "
             "is ~25 studs from the giant tree's inner wall, so two root legs carry it down to the floor OUTSIDE "
             "the chamber rails (feet at x 12.4 / 31.6, >= 0.1 outside every rail): whole prop ~19.8 x 10 x 1.9. "
             "Two small paper lanterns hang from the beam (Neon cores). The swing envelope (bob + chain, +-30 deg) "
             "stays >= 1 stud from every part except the hinge bracket. No collision."),
      placements=[dict(hole="H9", pos=list(_PV), yaw=0)])
def pendulum_beam(pb):
    rnd = random.Random(19)
    f0 = pb.frame
    pb.frame = f0 @ Matrix.Translation((_BEAM_DX, 0, 0))
    # main beam (Blender x), centre 0.85 above the hinge
    pts = [(-8.0 + 16 * i / 10, 0.05 * math.sin(i * 1.7), 0.85 + 0.08 * math.sin(i * 1.1)) for i in range(11)]
    pb.tube("RootBark", pts, [0.62, 0.58, 0.56, 0.55, 0.6, 0.62, 0.6, 0.55, 0.56, 0.58, 0.62], 9, wobble=0.12, seed=3)
    pb.tube("RootBark", [(-7.6, 0.3, 1.05), (-3.0, 0.42, 1.2), (2.0, 0.38, 1.15), (7.6, 0.28, 1.0)], 0.22, 6,
            wobble=0.2, seed=5)
    # legs: from the beam ends curving out and down to the floor (feet 7.96 below the hinge = local felt y 1.0)
    floor = -(_PV[1] - 1.0)
    for sx in (-1, 1):
        leg = [(sx * 7.6, 0, 0.8), (sx * 8.7, 0.05, 0.0), (sx * 9.4, -0.05, -2.5), (sx * 9.6, 0.05, -5.5),
               (sx * 9.6, 0, floor + 0.3)]
        pb.tube("RootBark", leg, [0.6, 0.55, 0.5, 0.5, 0.62], 8, wobble=0.15, seed=7 + sx)
        pb.tube("RootBark", [(sx * 8.4, 0.3, 0.3), (sx * 9.6, 0.35, -3.0), (sx * 9.4, 0.3, floor + 0.2)],
                [0.25, 0.22, 0.26], 6, wobble=0.2, seed=11 + sx)
        pb.rock("RootBark", (1.3, 1.2, 0.7), loc=(sx * 9.6, 0, floor), seed=21 + sx, amp=0.15)
        pb.rock("Moss", (1.1, 1.0, 0.25), loc=(sx * 9.6, 0, floor + 0.55), seed=23 + sx, amp=0.1)
        # small hanging lantern beside each leg top (outside the swing envelope, |x| >= 6.5)
        x = sx * 6.6
        pb.cyl("Iron", 0.015, 0.015, 0.9, 4, loc=(x, 0, -0.05))
        pb.lantern(0.7, loc=(x, 0, -1.2))
    pb.frame = f0
    # hinge bracket: two iron cheeks either side of the pin (pin along Blender Y at the origin)
    for sy in (-1, 1):
        pb.box("Iron", (0.34, 0.08, 0.7), loc=(0, sy * 0.4, 0.15))
    pb.box("Iron", (0.5, 0.92, 0.12), loc=(0, 0, 0.42))
    for x in (-0.9, 0.9):
        pb.torus("Iron", 0.66, 0.06, 12, 4, loc=(x, 0, 0.85), rot=(0, 90, 0))
    pb.frame = f0 @ Matrix.Translation((_BEAM_DX, 0, 0))
    for x in (-5.0, -1.8, 3.2, 5.6):
        pb.sphere("Moss", 0.55, loc=(x + rnd.uniform(-0.3, 0.3), 0, 1.42), scale=(1.4, 0.9, 0.3), segs=8, rings=4)


# ============================================================================ H9 tunnel dip trim
_ti = [f for f in HOLES[9]["felt"] if f["id"] == "tunnel_in"][0]
_to = [f for f in HOLES[9]["felt"] if f["id"] == "tunnel_out"][0]
_x0, _x1 = _ti["center"][0] - _ti["size"][0] / 2, _to["center"][0] + _to["size"][0] / 2
_xm = _ti["center"][0] + _ti["size"][0] / 2
_ytop = _ti["center"][1] - _ti["slope"]["rise"] / 2          # felt at the tunnel ends (rise -0.4 -> ends 1.0)
_ybot = _ti["center"][1] + _ti["slope"]["rise"] / 2          # dip crease (0.6)
_rails9 = {w["id"]: w for w in HOLES[9]["walls"]}
_ZN = _rails9["rail8"]["center"][2]      # north tunnel rail line (z -21.75)
_ZS = _rails9["rail4"]["center"][2]      # south tunnel rail line (z -29.25)
_DIP_ORIGIN = [(_x0 + _x1) / 2, _ybot, _ti["center"][2]]


def dip_felt_y(x):
    if x <= _x0 or x >= _x1:
        return _ytop
    if x <= _xm:
        return _ytop + (_ybot - _ytop) * (x - _x0) / (_xm - _x0)
    return _ybot + (_ytop - _ybot) * (x - _xm) / (_x1 - _xm)


@prop("h9_tunnel_dip_trim", ["H9"], "P2", target=[6, 0.4, 7], group="hero",
      origin=f"hole-local {_DIP_ORIGIN}: middle of the dip crease (x 11), base = crease felt height",
      front="n/a",
      notes=("Root-and-moss trim filling the wedge between the H9 tunnel felt dip (down 0.4 from x 8 to 11, back up "
             "to x 14) and the straight 1-stud visual rail kit (rail8 north / rail4 south, which stays level at "
             "the corridor felt height 1.0). Two strips, each exactly on its rail's footprint (0.5 thick, outside "
             "the felt): bottom follows the dip, top = 1.0 (+ a small moss lip). No collision."),
      placements=[dict(hole="H9", pos=list(_DIP_ORIGIN), yaw=0)])
def dip_trim(pb):
    ox, oy, oz = _DIP_ORIGIN
    for k, zr in enumerate((_ZN, _ZS)):
        zl = zr - oz
        # profile in the x-y plane: bottom follows the felt, top flat at the corridor felt height
        xs = [_x0 + (_x1 - _x0) * i / 12 for i in range(13)]
        poly = [(x - ox, dip_felt_y(x) - oy) for x in xs] + [(_x1 - ox, _ytop - oy + 0.04), (_x0 - ox, _ytop - oy + 0.04)]
        # prism: poly (x, y) extruded along z -> Blender (x, z), depth along Blender Y (= Roblox z)
        Mp = Matrix.Translation(R(0, 0, zl)) @ Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
        pb.prism("RootBark", poly, 0.48, matrix=Mp)
        # roots twisting along the strip + moss tufts on its top
        pts = [R(x - ox, (dip_felt_y(x) + _ytop) / 2 - oy + 0.02 * math.sin(x * 3), zl + 0.12 * math.sin(x * 2 + k))
               for x in xs[1:-1:2]]
        pb.tube("RootBark", pts, 0.1, 6, wobble=0.2, seed=k)
        for x in (_x0 + 1.2, (_x0 + _x1) / 2, _x1 - 1.2):
            pb.sphere("Moss", 0.3, loc=R(x - ox, _ytop - oy + 0.05, zl), scale=(1.6, 0.8, 0.3), segs=8, rings=4)
        pb.cyl("Cream", 0.03, 0.04, 0.16, 6, loc=R(_xm - ox + 0.6, _ytop - oy + 0.1, zl))
        pb.sphere("ShroomGlow", 0.09, loc=R(_xm - ox + 0.6, _ytop - oy + 0.2, zl), scale=(1, 1, 0.55), segs=8, rings=4)
