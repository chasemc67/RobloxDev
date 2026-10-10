"""Authoring helpers for Lantern Grove holes (used by build_holes.py).

Conventions (mirrors holes.json "schema"):
  * studs, Y up, hole-local frame, tee near origin, play generally toward -Z.
  * Map view used everywhere in docs/renders: +X right, -Z up ("north").
  * yaw = degrees about +Y (right-handed, Roblox CFrame.Angles(0, yaw, 0)):
        world_x =  lx*cos(yaw) + lz*sin(yaw)
        world_z = -lx*sin(yaw) + lz*cos(yaw)
    so in the map view a positive yaw turns counter-clockwise.
  * felt "center" is the TOP-surface center. slope {axis, rise}: rise = height at the
    +axis end minus height at the -axis end (local axes), linear across the piece.
  * wall "center" is the box center; size [x, y, z] in the wall's local frame
    (we always author walls with local Z along the wall run, local X = thickness).
"""
import math

T = 0.5          # wall thickness
WALL_H = 1.0     # wall height above felt
r3 = lambda v: round(v, 4)


def yaw_of(dx, dz):
    """yaw (deg) that maps local +Z onto world direction (dx, dz)."""
    return math.degrees(math.atan2(dx, dz))


def rot(lx, lz, yaw_deg):
    a = math.radians(yaw_deg)
    c, s = math.cos(a), math.sin(a)
    return lx * c + lz * s, -lx * s + lz * c


def right_normal(dx, dz):
    """Map-view right-hand normal of a direction (x right, -z up)."""
    return -dz, dx


class Hole:
    def __init__(self, num, hid, name, par, zone, landmark, gimmick, world_offset, world_yaw=0.0):
        self.d = dict(number=num, id=hid, name=name, par=par, zone=zone, landmark=landmark,
                      gimmick=gimmick, world_offset=list(world_offset), world_yaw=world_yaw,
                      tee=None, cup=None, felt=[], walls=[], hazards=[], drops=[],
                      moving_parts=[], teleports=[], ai_waypoints={}, cup_from=None,
                      decoration_anchors=[], notes="")
        self._wn = 0

    # ---------------- felt ----------------
    def rect(self, fid, x0, x1, z0, z1, y=0.0, zone=None, slope=None, **flags):
        """Axis-aligned felt. slope=('z', y_at_z0, y_at_z1) or ('x', y_at_x0, y_at_x1)."""
        cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
        sx, sz = abs(x1 - x0), abs(z1 - z0)
        p = dict(id=fid, zone=zone or fid, center=None, size=[r3(sx), r3(sz)], yaw=0.0, slope=None)
        if slope is None:
            p["center"] = [r3(cx), r3(y), r3(cz)]
        else:
            ax, ya, yb = slope
            a0, a1 = (x0, x1) if ax == "x" else (z0, z1)
            # rise = h(max coord) - h(min coord)
            rise = (yb - ya) if a1 > a0 else (ya - yb)
            p["center"] = [r3(cx), r3((ya + yb) / 2), r3(cz)]
            p["slope"] = {"axis": ax, "rise": r3(rise)}
        p.update(flags)
        self.d["felt"].append(p)
        return p

    def seg(self, fid, p1, p2, width, y1=0.0, y2=None, zone=None, ext1=0.0, ext2=0.0, **flags):
        """Felt rectangle along a centreline p1->p2 (local +Z = p1->p2). Ramps y1->y2."""
        y2 = y1 if y2 is None else y2
        dx, dz = p2[0] - p1[0], p2[1] - p1[1]
        L = math.hypot(dx, dz)
        ux, uz = dx / L, dz / L
        a = (p1[0] - ux * ext1, p1[1] - uz * ext1)
        b = (p2[0] + ux * ext2, p2[1] + uz * ext2)
        cx, cz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        p = dict(id=fid, zone=zone or fid, center=[r3(cx), r3((y1 + y2) / 2), r3(cz)],
                 size=[r3(width), r3(L + ext1 + ext2)], yaw=r3(yaw_of(dx, dz)), slope=None)
        if abs(y2 - y1) > 1e-9:
            assert ext1 == 0 and ext2 == 0, "only extend flat segments"
            p["slope"] = {"axis": "z", "rise": r3(y2 - y1)}
        p.update(flags)
        self.d["felt"].append(p)
        return p

    def bank(self, fid, a, b, width, rise, outward, base_y=0.0, ext=1.0, zone=None):
        """Banked plane overlay: low (inner) edge along a->b at base_y, rising by `rise`
        over `width` toward `outward` ('L' or 'R' of a->b in map view)."""
        dx, dz = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dz)
        ux, uz = dx / L, dz / L
        nx, nz = right_normal(ux, uz)
        if outward == "L":
            nx, nz = -nx, -nz
        mx, mz = (a[0] + b[0]) / 2 + nx * width / 2, (a[1] + b[1]) / 2 + nz * width / 2
        yaw = yaw_of(dx, dz)
        lxx, lxz = rot(1, 0, yaw)         # local +X in world
        sign = 1 if (lxx * nx + lxz * nz) > 0 else -1
        p = dict(id=fid, zone=zone or fid, center=[r3(mx), r3(base_y + rise / 2), r3(mz)],
                 size=[r3(width), r3(L + 2 * ext)], yaw=r3(yaw),
                 slope={"axis": "x", "rise": r3(sign * rise)}, overlay=True, kind="bank")
        self.d["felt"].append(p)
        return p

    def bank_wall(self, fid, a, b, outward, width=1.2, rise=1.2, base_y=0.0, zone=None):
        """Steep (45-degree) banked plane across a corner, backed by a rail along its top edge.
        Inner (low) edge runs a->b flush with the base felt. Tested: turns ~75% of balls vs ~85% for a
        hard deflector, but with a softer, rolling feel (see playtest-log Round 2)."""
        p = self.bank(fid, a, b, width, rise, outward, base_y=base_y, ext=0.6, zone=zone)
        dx, dz = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dz)
        ux, uz = dx / L, dz / L
        nx, nz = right_normal(ux, uz)
        if outward == "L":
            nx, nz = -nx, -nz
        off = width + T / 2
        A = (a[0] + nx * off - ux * 1.5, a[1] + nz * off - uz * 1.5)
        B = (b[0] + nx * off + ux * 1.5, b[1] + nz * off + uz * 1.5)
        self.wall_free(A, B, base_y + rise, name=f"{fid}_backing", ybot=base_y - 0.5)
        return p

    # ---------------- walls ----------------
    def _box(self, name, cx, cz, ybot, ytop, length, yaw, thick=T, **kw):
        self._wn += 1
        w = dict(id=name or f"w{self._wn}", center=[r3(cx), r3((ybot + ytop) / 2), r3(cz)],
                 size=[r3(thick), r3(ytop - ybot), r3(length)], yaw=r3(yaw))
        w.update(kw)
        self.d["walls"].append(w)
        return w

    def wall_free(self, p1, p2, y, name=None, height=WALL_H, ybot=None, thick=T, ext=0.0, **kw):
        """Free-standing wall centred on the line p1->p2 (deflectors, blocks)."""
        dx, dz = p2[0] - p1[0], p2[1] - p1[1]
        L = math.hypot(dx, dz)
        cx, cz = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        yb = y - 0.5 if ybot is None else ybot
        return self._box(name, cx, cz, yb, y + height, L + 2 * ext, yaw_of(dx, dz), thick, **kw)

    def block(self, name, cx, cz, sx, sz, y, height=WALL_H, yaw=0.0, ybot=None, **kw):
        """Static block (rocks, stumps, hubs). size given as world x/z extents at yaw 0."""
        self._wn += 1
        yb = y - 0.5 if ybot is None else ybot
        w = dict(id=name, center=[r3(cx), r3((yb + y + height) / 2), r3(cz)],
                 size=[r3(sx), r3(y + height - yb), r3(sz)], yaw=r3(yaw), kind="bumper")
        w.update(kw)
        self.d["walls"].append(w)
        return w

    def wall_path(self, pts, ys, out="L", closed=False, ext=(0.5, 0.5), ybot=None, top=None, name="rail"):
        """Walls along a felt boundary polyline. pts = felt-edge vertices, ys = felt height at
        each vertex (scalar ok). Box inner face sits on the felt edge, thickness goes `out`.
        Corners are mitred so inner faces meet exactly at felt corners (no nubs, no notches)."""
        n = len(pts)
        if not isinstance(ys, (list, tuple)):
            ys = [ys] * n
        segs = list(range(n if closed else n - 1))
        dirs, nors = [], []
        for i in range(n if closed else n - 1):
            a, b = pts[i], pts[(i + 1) % n]
            dx, dz = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dz)
            ux, uz = dx / L, dz / L
            nx, nz = right_normal(ux, uz)
            if out == "L":
                nx, nz = -nx, -nz
            dirs.append((ux, uz, L))
            nors.append((nx, nz))

        def offset_meet(j, off):
            """intersection of offset lines of segments j-1 and j at vertex j."""
            C = pts[j]
            (ux0, uz0, _), (nx0, nz0) = dirs[j - 1], nors[j - 1]
            (ux1, uz1, _), (nx1, nz1) = dirs[j % len(dirs)], nors[j % len(nors)]
            # C + n0*off + s*u0 = C + n1*off + t*u1
            rx, rz = (nx1 - nx0) * off, (nz1 - nz0) * off
            det = ux0 * (-uz1) - uz0 * (-ux1)
            if abs(det) < 1e-9:
                return (C[0] + nx1 * off, C[1] + nz1 * off)
            s = (rx * (-uz1) - rz * (-ux1)) / det
            return (C[0] + nx0 * off + s * ux0, C[1] + nz0 * off + s * uz0)

        for i in segs:
            a = pts[i]
            j0, j1 = i, (i + 1) % n
            ux, uz, L = dirs[i]
            nx, nz = nors[i]
            proj = lambda P: (P[0] - a[0]) * ux + (P[1] - a[1]) * uz
            # start
            if not closed and i == 0:
                s0 = -ext[0]
            else:
                cands = [proj(pts[j0]), proj(offset_meet(j0, T / 2)), proj(offset_meet(j0, T))]
                s0 = min(cands)
            if not closed and i == len(segs) - 1:
                s1 = L + ext[1]
            else:
                cands = [proj(pts[j1]), proj(offset_meet(j1, T / 2)), proj(offset_meet(j1, T))]
                s1 = max(cands)
            cx = a[0] + ux * (s0 + s1) / 2 + nx * T / 2
            cz = a[1] + uz * (s0 + s1) / 2 + nz * T / 2
            y0, y1 = ys[j0], ys[j1]
            yb = (min(y0, y1) - 0.5) if ybot is None else ybot
            yt = (max(y0, y1) + WALL_H) if top is None else top
            self._box(f"{name}{self._wn + 1}", cx, cz, yb, yt, s1 - s0, yaw_of(ux, uz))

    # ---------------- other ----------------
    def tee(self, x, y, z, facing=(0, -1)):
        self.d["tee"] = {"position": [x, y, z], "aim_hint": list(facing)}

    def cup(self, x, y, z, radius=0.5):
        self.d["cup"] = {"position": [x, y, z], "radius": radius}

    def hazard(self, hid, kind, x0, x1, z0, z1, y, **kw):
        h = dict(id=hid, type=kind, center=[r3((x0 + x1) / 2), y, r3((z0 + z1) / 2)],
                 size=[r3(abs(x1 - x0)), r3(abs(z1 - z0))], yaw=0.0,
                 reset="previous_position", penalty=1)
        h.update(kw)
        self.d["hazards"].append(h)

    def drop(self, did, frm, to, edge, height, note=""):
        self.d["drops"].append(dict(id=did, **{"from": frm}, to=to, edge=edge, height=height, note=note))

    def rotor(self, mid, pivot, axis, speed_dps, blockers, rng=None, phase=0.0, visual=""):
        self.d["moving_parts"].append(dict(id=mid, type="rotate", pivot=pivot, axis=axis,
                                           speed=speed_dps, speed_units="deg/s", range=rng,
                                           phase=phase, blockers=blockers, visual=visual))

    def slider(self, mid, pivot, axis, speed, rng, blockers, phase=0.0, visual=""):
        self.d["moving_parts"].append(dict(id=mid, type="slide", pivot=pivot, axis=axis,
                                           speed=speed, speed_units="studs/s", range=rng,
                                           phase=phase, blockers=blockers, visual=visual))

    def teleport(self, tid, entry, radius, exit_, exit_dir, speed_factor=0.8, min_speed=2.0,
                 max_speed=8.0, visual=""):
        L = math.hypot(*exit_dir)
        self.d["teleports"].append(dict(id=tid, entry={"center": entry, "radius": radius},
                                        exit={"center": exit_, "dir": [r3(exit_dir[0] / L), r3(exit_dir[1] / L)]},
                                        speed_factor=speed_factor, min_speed=min_speed,
                                        max_speed=max_speed, visual=visual))

    def wp(self, skill, wid, pos, frm, carry=1.0, power_scale=1.0):
        self.d["ai_waypoints"].setdefault(skill, []).append(
            dict(id=wid, pos=pos, **{"from": frm}, carry=carry, power_scale=power_scale))

    def anchor(self, name, pos, notes, landmark=False, size=None):
        a = dict(name=name, position=pos, notes=notes)
        if landmark:
            a["landmark"] = True
        if size:
            a["approx_size"] = size
        self.d["decoration_anchors"].append(a)


def arm_blockers(n, r_in, r_out, thick, height, y_off=0.0, phase=0.0):
    """n arms radiating from a vertical pivot (blockers given at angle 0)."""
    out = []
    for k in range(n):
        yaw = phase + 360.0 * k / n
        rmid = (r_in + r_out) / 2
        x, z = rot(rmid, 0, yaw)
        out.append(dict(center=[r3(x), r3(y_off + height / 2), r3(z)],
                        size=[r3(r_out - r_in), r3(height), r3(thick)], yaw=r3(yaw)))
    return out
