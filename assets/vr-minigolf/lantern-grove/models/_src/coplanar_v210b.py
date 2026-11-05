"""v210b coplanar-overlap (z-fighting) check, pure numpy (runs inside Blender's Python or plain python3).

A z-fight pair = two triangles that
  * lie in the same plane (normals parallel within 0.5 deg, plane offsets within PLANE_TOL = 0.006 studs; the
    pre-v210b backing cap top sat 0.005 above a rail-kit cap top),
  * face the SAME way (n1 . n2 > 0; back-to-back contact faces are not counted: Roblox culls back faces), and
  * overlap with a positive area (> AREA_TOL stud^2) when projected into that plane,
  * and belong to different pieces: a different part (material mesh) or a different loose island of the same part.
Touching / shared edges have zero overlap area and are not counted.

count_overlaps(parts) -> dict(pairs=N, faces=number of distinct triangles involved, by_parts={"A|B": pairs},
                              area=total overlap area, examples=[...])
parts = {part_name: T} with T = (n, 3, 3) float triangle array (any common frame).
"""
import numpy as np

PLANE_TOL = 0.006        # same-facing faces closer than this (studs) z-fight at play distance
ANG_TOL = 0.99996        # cos(0.5 deg)
AREA_TOL = 1e-5


def islands(T, decimals=5):
    """Loose-island id per triangle (triangles sharing a vertex position are connected)."""
    n = len(T)
    if n == 0:
        return np.zeros(0, int)
    P = np.round(T.reshape(-1, 3), decimals)
    _, inv = np.unique(P, axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    parent = np.arange(inv.max() + 1)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    V = inv.reshape(n, 3)
    for a, b, c in V:
        ra, rb, rc = find(a), find(b), find(c)
        parent[rb] = ra
        parent[find(rc)] = ra
    return np.array([find(v[0]) for v in V])


def _clip(poly, a, b):
    """Sutherland-Hodgman: keep the part of poly left of the directed edge a->b (2D)."""
    out = []
    if not poly:
        return out
    ex, ey = b[0] - a[0], b[1] - a[1]
    side = lambda p: ex * (p[1] - a[1]) - ey * (p[0] - a[0])
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        sp, sq = side(p), side(q)
        if sp >= 0:
            out.append(p)
        if (sp >= 0) != (sq >= 0):
            t = sp / (sp - sq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def _area(poly):
    s = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        s += x1 * y2 - x2 * y1
    return s / 2


def tri_overlap_area(t1, t2, u, v):
    a = [(float(p @ u), float(p @ v)) for p in t1]
    b = [(float(p @ u), float(p @ v)) for p in t2]
    if _area(a) < 0:
        a = a[::-1]
    if _area(b) < 0:
        b = b[::-1]
    poly = a
    for i in range(3):
        poly = _clip(poly, b[i], b[(i + 1) % 3])
        if len(poly) < 3:
            return 0.0
    return abs(_area(poly))


def count_overlaps(parts, max_examples=8, return_pairs=False):
    """return_pairs: also list every pair as ((part, tri index in that part), (part, tri index), area)."""
    names, tris, isl, local = [], [], [], []
    for k, (name, T) in enumerate(sorted(parts.items())):
        T = np.asarray(T, float).reshape(-1, 3, 3)
        if not len(T):
            continue
        names += [name] * len(T)
        local += list(range(len(T)))
        tris.append(T)
        isl.append(islands(T) + k * 10_000_000)
    if not tris:
        return dict(pairs=0, faces=0, by_parts={}, area=0.0, examples=[], **({"pair_list": []} if return_pairs else {}))
    T = np.concatenate(tris)
    I = np.concatenate(isl)
    names = np.array(names)
    N = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    ln = np.linalg.norm(N, axis=1)
    ok = ln > 1e-9
    N[ok] /= ln[ok, None]
    D = np.einsum("ij,ij->i", N, T[:, 0])
    # bucket by rounded normal + plane offset (also neighbour offset bins against rounding at bin edges)
    key_n = np.round(N * 200).astype(int)
    key_d = np.floor(D / (PLANE_TOL * 4)).astype(int)
    buckets = {}
    for i in np.nonzero(ok)[0]:
        kn = tuple(key_n[i])
        buckets.setdefault((kn, key_d[i]), []).append(i)
    lo, hi = T.min(1), T.max(1)
    seen, pairs, faces, by, area, ex, plist = set(), 0, set(), {}, 0.0, [], []
    for (kn, kd), idx in buckets.items():
        cand = list(idx)
        for dd in (-1, 1):
            cand += buckets.get((kn, kd + dd), [])
        if len(cand) < 2:
            continue
        cand = np.array(sorted(set(cand)))
        for i in idx:
            js = cand[cand > i]
            js = js[(I[js] != I[i])]
            if not len(js):
                continue
            js = js[np.all(lo[js] <= hi[i] + 1e-6, 1) & np.all(hi[js] >= lo[i] - 1e-6, 1)]
            js = js[(N[js] @ N[i] > ANG_TOL) & (np.abs(D[js] - D[i]) < PLANE_TOL)]
            if not len(js):
                continue
            n = N[i]
            u = np.cross(n, [1.0, 0, 0] if abs(n[0]) < 0.9 else [0, 1.0, 0])
            u /= np.linalg.norm(u)
            v = np.cross(n, u)
            for j in js:
                key = (min(i, j), max(i, j))
                if key in seen:
                    continue
                seen.add(key)
                a = tri_overlap_area(T[i], T[j], u, v)
                if a > AREA_TOL:
                    pairs += 1
                    area += a
                    faces.update((int(i), int(j)))
                    plist.append(((str(names[i]), local[i]), (str(names[j]), local[j]), a))
                    pk = "|".join(sorted((str(names[i]), str(names[j]))))
                    by[pk] = by.get(pk, 0) + 1
                    if len(ex) < max_examples:
                        ex.append(dict(parts=pk, area=round(a, 5), centre=np.round(T[i].mean(0), 3).tolist(),
                                       normal=np.round(n, 3).tolist()))
    out = dict(pairs=pairs, faces=len(faces), by_parts=by, area=round(area, 5), examples=ex)
    if return_pairs:
        out["pair_list"] = plist
    return out


if __name__ == "__main__":
    # self-test: two coplanar same-facing quads overlapping (z-fight) + a back-to-back pair (not counted)
    q = lambda z, s=1.0, f=False: np.array([[[0, 0, z], [s, 0, z], [s, s, z]], [[0, 0, z], [s, s, z], [0, s, z]]])[
        :, ::(-1 if f else 1)]
    r = count_overlaps({"A": q(0), "B": q(0, 0.5)})
    assert r["pairs"] >= 2 and r["faces"] >= 3, r
    r2 = count_overlaps({"A": q(0), "B": q(0, 1.0, True)})
    assert r2["pairs"] == 0, r2
    r3 = count_overlaps({"A": q(0), "B": q(0.01, 0.5)})
    assert r3["pairs"] == 0, r3
    print("coplanar_v210b self-test ok", r)
