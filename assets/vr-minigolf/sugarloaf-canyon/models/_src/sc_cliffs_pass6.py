"""Sugarloaf Canyon pass 6 cliff kit: separate stepped, eroded towers with gaps, rounded tops, overhangs and gently
wavy strata. Replaces the cliff_w24_* / slot_w24_* geometry (same ids, same 24-wide panel envelope: local x +-12.5,
front relief <= 2.5 (Roblox local z >= -2.6), back <= 8.5, height h, so placements and footprints are unchanged) and
adds top-of-stack variants cliffT_w24_* / slotT_* with rounded tower tops. Also reworks rim_silhouette.

Panel = ONE tower column: half width tw(world y) narrows ~0.9 over every 12-stud world-y period and steps back out
under a cap-rock overhang at each period top (periodic in world y, so stacked panels continue seamlessly); both panel
edges are recessed 5 studs, so neighbours at the 21-stud spacing read as separate towers with ~5-stud gaps. The front
is eroded by noise + vertical fluting; the tower corners round back into the recess. Strata UVs: V = (local z + y0 +
wave(x)) / 36 with wave = 1.1 sin(pi x / 12) + 0.45 sin(2 pi x / 12 + 0.7 sin(...)) -> 0 at the panel edges.
"""
import math, random
import bmesh
from mathutils import Vector, Matrix
import sclib as L
from sclib import band_rows, nz, smooth01, ledge
from sc_pieces import Part, T, Rz, crystal_cluster, add_faces_bm
import sc_specs as SP

W_ = 24.0
RECESS = -5.0
BACK = -8.0
FRONT_MAX = 2.5


def wave(x, y=0.0):
    return 1.1 * math.sin(math.pi * x / 12.0) + 0.45 * math.sin(2 * math.pi * x / 12.0)


def tower_hw(zw, base):
    """Tower half width at WORLD height zw: tapers 0.9 over each 12-stud period, cap-rock flare in its top 1.2 studs."""
    f = (zw % 12.0) / 12.0
    cap = smooth01((f - 0.88) / 0.1)
    return base - 0.9 * f + 1.3 * cap


def overhang(zw):
    """Front push-out of the cap rock at each 12-stud period top, undercut just below it."""
    f = (zw % 12.0) / 12.0
    return 1.1 * smooth01((f - 0.88) / 0.08) - 0.6 * smooth01((f - 0.7) / 0.12) * (1 - smooth01((f - 0.88) / 0.05))


def tower_panel(name, h, phase, top=False, slot=False, seed=0):
    y0 = phase * 6.0
    kind = ("slot wall" if slot else "cliff") + (" stack-top" if top else "")
    pb = Part(name, y0=y0, role=f"pass-6 {kind} tower panel 24 x {h} (phase {phase})")
    pb.wave = wave
    rnd = random.Random(seed * 31 + h * 7 + phase + (100 if slot else 0) + (500 if top else 0))
    so = rnd.uniform(0, 50)
    base_hw = rnd.uniform(7.9, 8.8)
    rt = min(10.0, h * 0.75) if top else 0.0           # rounded-top region height
    zs = band_rows(0.0, float(h), y0, per_band=(0.0, 0.55, 0.9))
    if top:
        zs = sorted(set(zs) | {h - rt + rt * k / 6 for k in range(7)})
        zs = [z for z in zs if z <= h]
        zs = sorted(set(round(z, 4) for z in zs))

    def roundf(z):
        if not top or z <= h - rt:
            return 1.0
        u = (z - (h - rt)) / rt
        return max(0.22, math.sqrt(max(0.0, 1 - u ** 2.2)))

    def row(z):
        zw = z + y0
        rf = roundf(z)
        tw = tower_hw(zw, base_hw) * rf
        tw = min(tw, 9.8)
        edge_noise = 0.5 * nz(so, zw * 0.15, 0, 1.0, seed + 3)
        xs = [-12.0, -10.9, -(tw + 0.9), -tw, -tw * 0.62, -tw * 0.3, 0.0, tw * 0.3, tw * 0.62, tw, tw + 0.9, 10.9, 12.0]
        out = []
        for i, x in enumerate(xs):
            zwv = zw + wave(x) * 0.6
            fr = 0.75 + ledge(zwv, 0.9) + overhang(zwv) + 0.55 * nz(x, so, z, 0.11, seed) + 0.25 * math.sin(x * 1.3 + so)
            fr -= (1 - rf) * 3.2                                   # rounded top also leans back
            fr = min(fr, FRONT_MAX)
            if i in (0, 1, 11, 12):
                y = RECESS + 0.4 * nz(x, so + 9, z, 0.2, seed)
            elif i in (2, 10):
                y = RECESS + 1.4 + edge_noise
            elif i in (3, 9):
                y = min(fr * 0.45 - 0.9, FRONT_MAX - 1.0)
            else:
                y = fr
            zz = z
            if top and z > h - rt and i in (0, 1, 2, 10, 11, 12):
                # stack-top: the gap / shoulder columns stay low so the towers stand free above them
                zz = (h - rt) + (z - (h - rt)) * (0.18 if i in (0, 1, 11, 12) else 0.45)
                y = y - (z - (h - rt)) / rt * 1.5
            out.append(Vector((x, y, zz)))
        return out
    t = bmesh.new()
    V = [[t.verts.new(p) for p in row(z)] for z in zs]
    nc = len(V[0])
    for j in range(len(zs) - 1):
        for i in range(nc - 1):
            t.faces.new((V[j][i], V[j][i + 1], V[j + 1][i + 1], V[j + 1][i]))
    # top lip back into the rock (stack-top variants: the narrowed dome top closes onto a lip at the back)
    tb = [t.verts.new(Vector((v.co.x, BACK, v.co.z))) for v in V[-1]]
    for i in range(nc - 1):
        t.faces.new((V[-1][i], tb[i], tb[i + 1], V[-1][i + 1]))
    # side flaps from the recess back to the rock (every other row)
    js = list(range(0, len(zs), 2))
    if js[-1] != len(zs) - 1:
        js.append(len(zs) - 1)
    for side in (0, -1):
        col = [V[j][side] for j in js]
        bk = [t.verts.new(Vector((c.co.x, BACK, c.co.z))) for c in col[:-1]] + [tb[side]]
        for a in range(len(col) - 1):
            q = (col[a], col[a + 1], bk[a + 1], bk[a])
            t.faces.new(q if side == -1 else tuple(reversed(q)))
    bmesh.ops.recalc_face_normals(t, faces=t.faces)
    t.normal_update()
    fy = sum(f.normal.y * f.calc_area() for f in t.faces if abs(f.normal.z) < 0.5)
    if fy < 0:
        bmesh.ops.reverse_faces(t, faces=t.faces)
    pb.add("Strata", t)
    if slot:
        n = 2 if h <= 24 else 4
        for k in range(n):
            x = rnd.uniform(-5.5, 5.5)
            z = rnd.uniform(3, h - (rt + 2 if top else 4))
            crystal_cluster(pb, T(x, 0.2, z) @ Rz(0) @ Matrix.Rotation(math.radians(-62), 4, "X"),
                            size=rnd.uniform(2.2, 3.4), seed=seed + k * 13 + h, flat=True)
    return pb


def rim_silhouette():
    """64-wide flat rim blade: 4 separate stepped towers with gaps, rounded tops (CastShadow off, far silhouette)."""
    pb = Part("rim_silhouette", role="pass-6 low-poly rim silhouette: stepped towers with gaps, CastShadow off")
    pb.wave = wave
    rnd = random.Random(7)
    pts = [(-32.0, 0.0)]
    towers = [(-24.0, 6.5, 26.0), (-8.5, 5.5, 22.0), (7.0, 7.0, 28.0), (23.5, 6.0, 24.0)]
    for cx, hw, ht in towers:
        gap_h = rnd.uniform(5.0, 8.0)
        pts.append((cx - hw - 1.6, gap_h))
        steps = [(cx - hw, ht * 0.55), (cx - hw * 0.8, ht * 0.62), (cx - hw * 0.8, ht * 0.8), (cx - hw * 0.62, ht * 0.84)]
        pts += steps
        for k in range(1, 6):                                   # rounded top
            a = math.pi * (1 - k / 6)
            pts.append((cx + hw * 0.62 * math.cos(a), ht * 0.84 + (ht * 0.16) * math.sin(a)))
        pts += [(cx + hw * 0.62, ht * 0.84), (cx + hw * 0.82, ht * 0.78), (cx + hw * 0.82, ht * 0.6), (cx + hw, ht * 0.52)]
        pts.append((cx + hw + 1.6, rnd.uniform(5.0, 8.0)))
    pts.append((32.0, 0.0))
    t = bmesh.new()
    vs = [t.verts.new(Vector((x, 0.0, z))) for x, z in pts]
    t.faces.new(vs)
    bmesh.ops.triangulate(t, faces=list(t.faces))
    pb.add("Strata", t)
    return pb


def registry():
    out = []
    for slot, heights in ((False, SP.KIT_HEIGHTS), (True, SP.SLOT_HEIGHTS)):
        for h in heights:
            for ph in range(6):
                for top in (False, True):
                    pre = ("slot" if slot else "cliff") + ("T" if top else "")
                    pid = f"{pre}_w24_h{h}_p{ph}"
                    out.append(dict(
                        id_=pid, group="cliff_kit",
                        build=(lambda h=h, ph=ph, top=top, slot=slot, pid=pid:
                               [tower_panel(pid, h, ph, top=top, slot=slot, seed=7 if slot else 0)]),
                        notes=(f"Pass-6 {'slot-canyon wall' if slot else 'striped cliff'} tower panel 24 wide x {h} tall, "
                               f"strata phase {ph} (base y / 6 mod 6 = {ph}): one eroded tower with recessed edge gaps, "
                               f"12-stud stepped taper + cap-rock overhangs, wavy strata"
                               + ("; ROUNDED TOP - use for the top panel of a stack" if top else "")
                               + ("; rock-candy crystal clusters" if slot else "") + "."),
                        origin="base centre of the front face",
                        preview="std" if (ph == 3 and not slot) or (ph == 4 and slot) else "none"))
    out.append(dict(id_="rim_silhouette", group="far_card", build=lambda: [rim_silhouette()],
                    notes="Pass-6 64-wide low-poly striped rim silhouette: four separate stepped towers with gaps and "
                          "rounded tops (flat blade); visible stretches only, CastShadow off.",
                    origin="base centre", views=("34",)))
    return out
