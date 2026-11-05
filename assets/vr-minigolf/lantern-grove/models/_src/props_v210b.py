"""v210b (Lantern Grove H9 game-art review): mint lip along the top edge of the H9 bank.

  h9_bank_lip  0.05 x 0.05 #6CC79F strip on the high (top) edge of every H9 bank (holes.json: bank1 only), in the
               bank backing's frame (same origin / yaw as its bank_backing_stone placement). It sits entirely
               OUTSIDE the playable felt: in plan it lies inside the *_backing wall's collision footprint, starting
               LIP_GAP behind the felt's high edge, and its ends stop where it would enter a rail wall box. Its front
               face is 0.009 proud of the backing's felt-facing stone face, so the mint line shows. Visual only:
               CanCollide off, SmoothPlastic, no emission / glow, no light.
"""
import numpy as np
from registry import prop
import dressing_lib as DL

HOLES = {h["number"]: h for h in DL.load_holes()}
LIP = 0.05                  # lip section (studs): 0.05 deep x 0.05 tall
LIP_GAP = 0.001             # behind the felt edge (plan)
BACKING_FACE = 0.24         # felt-facing stone face of bank_backing_stone (backing-local x = -0.24)


def bank_lips(hole=9):
    """[(bank, wall, pos, yaw, x0, x1, y0, y1, z0, z1)] lip box per bank, in the backing frame (Roblox axes)."""
    h = HOLES[hole]
    walls = {w["id"]: w for w in h["walls"]}
    out = []
    for f in h["felt"]:
        if f.get("kind") != "bank":
            continue
        w = walls[f["id"] + "_backing"]
        fc, wc = np.array(f["center"], float), np.array(w["center"], float)
        Rw = DL.yaw_mat(w["yaw"])
        base = fc[1] - abs(f["slope"]["rise"]) / 2          # bank low edge = the backing's base (placement y)
        top = fc[1] + abs(f["slope"]["rise"]) / 2           # bank high edge height
        lb = (fc - wc) @ Rw                                 # bank centre in the backing frame
        side = -1.0 if lb[0] < 0 else 1.0                   # the felt is on this side of the backing (local x)
        # the bank's high edge must be the one against the backing (bank and wall share the yaw)
        assert f["yaw"] == w["yaw"] and np.sign(f["slope"]["rise"]) == -side, (f["id"], lb)
        edge = lb[0] - side * f["size"][0] / 2              # felt high edge (backing-local x)
        x_front = edge - side * LIP_GAP                     # LIP_GAP behind the edge, away from the felt
        x0, x1 = sorted((x_front, x_front - side * LIP))
        y0, y1 = top - base, top - base + LIP
        half = f["size"][1] / 2

        def clear(z):
            for r in h["walls"]:
                if r["id"] == w["id"]:
                    continue
                Rr, rc = DL.yaw_mat(r.get("yaw", 0)), np.array(r["center"], float)
                hs = np.array(r["size"], float) / 2
                if base + y1 < rc[1] - hs[1] or base + y0 > rc[1] + hs[1]:
                    continue
                for x in (x0, x1):
                    for dz in (-1e-9, 1e-9):
                        p = wc + Rw @ np.array([x, 0, z + dz])
                        l = (p - rc) @ Rr
                        if abs(l[0]) <= hs[0] and abs(l[2]) <= hs[2]:
                            return False
            return True
        zs = np.round(np.arange(-half, half + 1e-9, 0.001), 4)
        ok = np.array([clear(z) for z in zs])
        i0 = int(np.argmin(np.abs(zs)))
        assert ok[i0]
        a = i0
        while a > 0 and ok[a - 1]:
            a -= 1
        b = i0
        while b < len(zs) - 1 and ok[b + 1]:
            b += 1
        out.append(dict(bank=f["id"], wall=w["id"], pos=[round(v, 4) for v in [wc[0], base, wc[2]]], yaw=w["yaw"],
                        x0=x0, x1=x1, y0=y0, y1=y1, z0=float(zs[a]), z1=float(zs[b]), felt_edge_x=edge, side=side))
    return out


LIPS = bank_lips(9)


@prop("h9_bank_lip", ["H9"], "P1", target=[0.05, 0.05, 10.4], group="rail_kit",
      origin="the H9 bank backing's origin (same pos / yaw as its bank_backing_stone placement): backing centre line, "
             "base = felt under the bank",
      front="-X (local): faces the bank felt",
      notes=("v210b H9 game-art review: 0.05 x 0.05 lip along the top (high) edge of the H9 bank, colour #6CC79F, "
             "SmoothPlastic, separate MeshPart h9_bank_lip__BankLip. Visual only: CanCollide/CanQuery/CanTouch off, "
             "no emission / glow, no PointLight. Entirely outside the playable felt: in plan it sits 0.001 behind the "
             "bank's high edge inside the bank1_backing wall footprint (fitcheck_v210b). Its ends stop at the rail5 / "
             "rail4 walls."),
      placements=[dict(hole="H9", pos=L["pos"], yaw=L["yaw"], note=f"{L['bank']} top edge ({L['wall']} frame)")
                  for L in LIPS])
def h9_bank_lip(pb):
    L = LIPS[0]
    # Roblox backing-local box -> Blender (x, -z, y)
    sx, sy, sz = L["x1"] - L["x0"], L["z1"] - L["z0"], L["y1"] - L["y0"]
    cx, cz, cy = (L["x0"] + L["x1"]) / 2, (L["z0"] + L["z1"]) / 2, (L["y0"] + L["y1"]) / 2
    pb.box("BankLip", (sx, sy, sz), loc=(cx, -cz, cy))
