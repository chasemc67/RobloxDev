"""Collider skins: every holes.json wall box gets a mesh that fills the box EXACTLY (faces coincide with the collider from
its bottom to its top) plus a cap inside the box footprint. Style per hole/wall (props.md 'Rail kit' + 'Tall-wall skins').
Bumpers (H1 boulder, H8 corals) and the H13 hub strips are skinned by their own hero props."""
import math
import holesdata as D
from aalib import hbox

CAP = {"timber": 0.22, "mogul": 0.22, "drift": 0.35, "berg": 0.3, "run": 0.25, "coral": 0.25, "hull": 0.15,
       "moonstone": 0.14, "crystal": 0.0, "ice": 0.22}
BODY = {"timber": "Timber", "mogul": "Timber", "drift": "SnowShadow", "berg": "Ice", "run": "SnowShadow",
        "coral": "CoralPink", "hull": "HullTeal", "moonstone": "Moonstone", "crystal": "Ice", "ice": "Ice"}
CAPM = {"timber": "Snow", "mogul": "Snow", "drift": "Snow", "berg": "Snow", "run": "Ice", "coral": "Snow",
        "hull": "Brass", "moonstone": "Moonstone", "ice": "Snow"}
TRIM = {"timber": "Brass", "mogul": "Brass", "coral": "CoralMint", "moonstone": "Silver", "crystal": "IceCore",
        "ice": "IceCore", "hull": "Brass"}
PROUD = 0.006   # flush trims sit 0.006 proud of the collider face (fitcheck tolerance 0.02)


def style(n, w):
    i = w["id"]
    if w.get("kind") == "bumper":
        return None                                   # skinned by snow_boulder / coral_N / hub_base
    if n == 2:
        return "drift"
    if n == 9:
        return "coral"
    if n == 10:
        return "run" if i.startswith("run_rail") else ("drift" if i.startswith("snowwall") else "timber")
    if n == 11:
        return "berg" if i.startswith("berg") else "drift"
    if n == 12 and (i.startswith("hull") or i in ("rail2", "rail3", "rail4", "rail5")):
        return "hull"
    if n == 16:
        return "moonstone"
    if n == 17 and i.startswith("pier"):
        return "ice"
    if n == 18:
        return "crystal"
    if n == 7 and i in ["rail%d" % k for k in list(range(2, 10)) + list(range(17, 25))]:
        return "mogul"
    return "timber"


def skin_wall(pb, n, w, k=0):
    st = style(n, w)
    if st is None:
        return None
    c, s, yaw = w["center"], w["size"], w.get("yaw", 0.0)
    y0, y1 = c[1] - s[1] / 2, c[1] + s[1] / 2
    y1j = y1 - 0.002 * (k % 4)          # tiny per-wall top offset: no coplanar z-fight where rails overlap at corners
    cap = CAP[st] if (y1 - y0) > 0.6 else 0.0
    yb = y1j - cap
    hbox(pb, BODY[st], (c[0], (y0 + yb) / 2, c[2]), (s[0], yb - y0, s[2]), yaw)
    if cap:
        hbox(pb, CAPM[st], (c[0], (yb + y1j) / 2, c[2]), (s[0], cap, s[2]), yaw, bevel=min(0.08, cap * 0.4))
    L = s[2]
    if st == "mogul":                      # thick rounded snow on the hump crests (inside the footprint)
        nl = max(1, int(L / 3.5))
        for j in range(nl):
            lz = -L / 2 + (j + 0.5) * L / nl
            ox, oz = D.yaw_rot(0, lz, yaw)
            hbox(pb, "Snow", (c[0] + ox, y1j + 0.1, c[2] + oz), (s[0] * 0.92, 0.2, min(1.4, L / nl * 0.6)), yaw, bevel=0.08)
    tm = TRIM.get(st)
    if tm and (y1 - y0) > 0.6 and L >= 1.0:
        yt = y1j - cap - (0.35 if st in ("timber", "mogul", "hull") else 0.5 * (y1 - y0 - cap))
        if st in ("timber", "mogul", "hull"):        # brass bolt plates every 2 studs on both long faces
            nb = max(1, int(L / 2 + 0.01))      # Round 4 walls: +0.01 so 5.99/15.99 (H12 stern line -0.01) keep 3/8 plates
            for j in range(nb):
                lz = -L / 2 + (j + 0.5) * L / nb
                for side in (-1, 1):
                    ox, oz = D.yaw_rot(side * (s[0] / 2 + PROUD / 2), lz, yaw)
                    hbox(pb, tm, (c[0] + ox, yt, c[2] + oz), (PROUD, 0.16, 0.16), yaw)
        else:                                        # continuous glow / inlay line along both long faces
            for side in (-1, 1):
                ox, oz = D.yaw_rot(side * (s[0] / 2 + PROUD / 2), 0, yaw)
                hbox(pb, tm, (c[0] + ox, yt, c[2] + oz), (PROUD, 0.1, L - 0.1), yaw)
    return st


def skin_hole(pb, n, only=None):
    used = {}
    for k, w in enumerate(D.H[n]["walls"]):
        if only and w["id"] not in only:
            continue
        st = skin_wall(pb, n, w, k)
        if st:
            used[w["id"]] = st
    return used
