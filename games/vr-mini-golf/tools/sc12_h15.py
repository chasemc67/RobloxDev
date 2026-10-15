"""Stage sc12 item 1: H15 dune_lean3 fillet (felt collider), from the live v79 collider frames.
The dune felt falls 5.71 deg toward rail2; along the dune side of dune_lean3 it falls 5.5 deg into the wall and 1.48 deg
along it (toward the north corner). A ball pressed on the lean3 face crawls/stalls (wall rub), so it never reaches the
0.6 drop at the north edge. The fillet is a thin felt box whose top rises from the dune surface (the crease, W from the
lean3 face) toward the wall at ALPHA deg (absolute), following the dune's along-wall fall: a ball runs along the crease,
off the wall, and exits over the north edge.
  PYTHONPATH=tools python3 tools/sc12_h15.py spec [W] [ALPHA]       (-> playtests/stage-sc12/h15-fillet-spec.json)
"""
import json, math, sys
import numpy as np
from pathlib import Path
from sc5_util import GAME

OUT = GAME / 'playtests/stage-sc12'
SRC = GAME / 'playtests/stage-sc11/h15-colliders.json'


def part(key):
    r = json.loads(SRC.read_text())
    P = {(p.get('wall') or p['path'].split('.')[-1] + ':' + str(p.get('piece'))): p for p in r['parts']}
    p = P[key]; c = p['cf']
    return np.array(c[:3]), np.array([c[3:6], c[6:9], c[9:12]]), np.array(p['size'])


def spec(W=0.3, ALPHA=15.0, north_trim=0.0, south_trim=0.6):
    dp, DR, ds = part('Felt:dune'); lp, LR, ls = part('dune_lean3')
    Yd = DR[:, 1]; top0 = dp + Yd * ds[1] / 2
    def ydune(x, z): return float((Yd @ top0 - Yd[0] * x - Yd[2] * z) / Yd[1])
    lX, lZ = LR[:, 0], LR[:, 2]
    w = -np.array([lX[0], 0, lX[2]]); w /= np.linalg.norm(w)        # lean3 normal into the main dune
    al = np.array([lZ[0], 0, lZ[2]]); al /= np.linalg.norm(al)       # along lean3 (+ = south)
    face = lp + w * ls[0] / 2; half = ls[2] / 2
    # north edge of the dune top: centre - Zd*15, along Xd
    Xd, Zd = DR[:, 0], DR[:, 2]
    nc = dp - Zd * ds[2] / 2; ne0 = nc + Xd * ds[0] / 2; ne1 = nc - Xd * ds[0] / 2
    def crease(t): q = face + al * t + w * W; return np.array([q[0], ydune(q[0], q[2]), q[2]])
    # north end: the crease point that lies on the north edge line (plan)
    e = (ne1 - ne0)[[0, 2]]; en = np.array([-e[1], e[0]]); en /= np.linalg.norm(en)
    def side(p): return float((p[[0, 2]] - ne0[[0, 2]]) @ en)
    inside = side(dp)
    lo, hi = -half, half
    for _ in range(60):   # bisect the crease t where side() crosses 0
        m = (lo + hi) / 2
        if (side(crease(m)) > 0) == (inside > 0): hi = m
        else: lo = m
    t_n = (lo + hi) / 2 + north_trim; t_s = half - south_trim
    c_n, c_s = crease(t_n), crease(t_s)
    Z = (c_s - c_n); L = float(np.linalg.norm(Z)); Z /= L
    up = math.tan(math.radians(ALPHA))
    Xc = np.array([w[0], -up, w[2]]); Xc /= np.linalg.norm(Xc)    # top-face X: from the wall down to the crease
    Y = np.cross(Z, Xc); Y /= np.linalg.norm(Y)
    if Y[1] < 0: Y = -Y
    X = np.cross(Y, Z); X /= np.linalg.norm(X)
    if X @ w < 0:                                  # keep the frame right-handed (det +1): flip Z, not X
        Z = -Z; X = np.cross(Y, Z); X /= np.linalg.norm(X)
    assert abs(np.linalg.det(np.column_stack([X, Y, Z])) - 1) < 1e-9
    ext = 0.10                                     # into the lean3 body (no slot at the wall)
    width = (W + ext) / float(np.array([X[0], X[2]]) @ np.array([w[0], w[2]]))
    thick = 0.4; SINK = 0.001                      # crease edge 0.001 below the dune surface: no lip
    mid = (c_n + c_s) / 2 - np.array([0, SINK, 0])
    topc = mid - X * width / 2                     # +X top edge = the crease
    centre = topc - Y * thick / 2
    R = np.column_stack([X, Y, Z])
    # checks: height of the fillet top above the dune at the lean3 face, crease, north-edge overhang
    def topy(x, z):  # fillet top plane
        return float((Y @ topc - Y[0] * x - Y[2] * z) / Y[1])
    fw = face + al * ((t_n + t_s) / 2)
    chk = {'crease_t': [t_n, t_s], 'length': L, 'width': width, 'slopeDeg': math.degrees(math.acos(Y[1])),
           'alongFallDeg': math.degrees(math.asin(-Z[1])) if Z[1] < 0 else -math.degrees(math.asin(Z[1])),
           'topAboveDuneAtFace': topy(fw[0], fw[2]) - ydune(fw[0], fw[2]),
           'topAboveDuneAtCrease': topy(*(c_n[[0, 2]] + c_s[[0, 2]]) / 2) - ydune(*(c_n[[0, 2]] + c_s[[0, 2]]) / 2),
           'northEdgeSideOfCreaseEnd': side(c_n), 'northEdgeSideOfWallEnd': side(c_n - w * W)}
    s = {'id': 'dune_lean3_fillet', 'W': W, 'alpha': ALPHA, 'cf': [*centre.tolist(), *R.flatten().tolist()],
         'size': [width, thick, L], 'checks': chk}
    (OUT / 'h15-fillet-spec.json').write_text(json.dumps(s, indent=1) + '\n')
    print(json.dumps(s, indent=1))
    return s


if __name__ == '__main__':
    a = sys.argv[2:]
    spec(*(float(x) for x in a)) if sys.argv[1] == 'spec' else None


def segments(W=0.4, N=15, FALL=0.6):
    """Stepped rest terrace along the dune side of dune_lean3: N level-across segments, each falling FALL deg along the
    wall (northward; FALL < 0.876 deg, so a ball can rest on it), each flush with the dune (0.001 below) at the outer edge
    of its NORTH end. The dune falls 1.48 deg along the wall, so each segment's outer edge lies below the dune further
    south (a step down from the dune onto the terrace, never a lip) and each joint steps down going north."""
    dp, DR, ds = part('Felt:dune'); lp, LR, ls = part('dune_lean3')
    Yd = DR[:, 1]; top0 = dp + Yd * ds[1] / 2
    def ydune(x, z): return float((Yd @ top0 - Yd[0] * x - Yd[2] * z) / Yd[1])
    lX, lZ = LR[:, 0], LR[:, 2]
    w = -np.array([lX[0], 0, lX[2]]); w /= np.linalg.norm(w)
    al = np.array([lZ[0], 0, lZ[2]]); al /= np.linalg.norm(al)       # + = south
    face = lp + w * ls[0] / 2; half = ls[2] / 2
    Xd, Zd = DR[:, 0], DR[:, 2]
    nc = dp - Zd * ds[2] / 2; ne0 = nc + Xd * ds[0] / 2; ne1 = nc - Xd * ds[0] / 2
    e = (ne1 - ne0)[[0, 2]]; en = np.array([-e[1], e[0]]); en /= np.linalg.norm(en)
    def side(p): return float((p[[0, 2]] - ne0[[0, 2]]) @ en)
    inside = side(dp)
    def edge(t): q = face + al * t + w * W; return np.array([q[0], ydune(q[0], q[2]), q[2]])
    lo, hi = -half, half
    for _ in range(60):
        m = (lo + hi) / 2
        if (side(edge(m)) > 0) == (inside > 0): hi = m
        else: lo = m
    t_n, t_s = (lo + hi) / 2, half - 0.02
    ts = np.linspace(t_n, t_s, N + 1)
    ext, thick, SINK = 0.10, 0.4, 0.001
    width = W + ext
    out = []
    for i in range(N):
        ta, tb = ts[i], ts[i + 1]                            # ta north, tb south
        P = edge(ta) - np.array([0, SINK, 0])                # outer edge, north end (flush)
        Z = np.array([al[0], math.tan(math.radians(FALL)), al[2]]); Z /= np.linalg.norm(Z)   # south, rising FALL
        X = np.array([w[0], 0, w[2]])                        # level across, toward the dune
        Y = np.cross(Z, X); Y /= np.linalg.norm(Y)
        if Y[1] < 0: Y = -Y
        X = np.cross(Y, Z); X /= np.linalg.norm(X)
        if X @ w < 0: Z = -Z; X = np.cross(Y, Z); X /= np.linalg.norm(X)
        R = np.column_stack([X, Y, Z]); assert abs(np.linalg.det(R) - 1) < 1e-9
        L = float((tb - ta) / (al @ np.array([Z[0], 0, Z[2]]) / np.linalg.norm([Z[0], Z[2]])) / math.cos(math.radians(FALL))) if False else float((tb - ta) / math.cos(math.radians(FALL)))
        zs = 1.0 if (Z @ al) > 0 else -1.0                   # Z points south (+t) or north
        topc = P + (Z * zs) * (L / 2) - X * (width / 2)
        centre = topc - Y * thick / 2
        def topy(x, z): return float((Y @ topc - Y[0] * x - Y[2] * z) / Y[1])
        S = edge(tb); Fn = face + al * ta; Fs = face + al * tb
        chk = {'outerNorthVsDune': topy(P[0], P[2]) - ydune(P[0], P[2]), 'outerSouthVsDune': topy(S[0], S[2]) - ydune(S[0], S[2]),
               'faceNorthVsDune': topy(Fn[0], Fn[2]) - ydune(Fn[0], Fn[2]), 'faceSouthVsDune': topy(Fs[0], Fs[2]) - ydune(Fs[0], Fs[2]),
               'slopeDeg': math.degrees(math.acos(Y[1]))}
        out.append({'id': 'dune_lean3_terrace_%02d' % (i + 1), 't': [float(ta), float(tb)], 'cf': [*centre.tolist(), *R.flatten().tolist()],
                    'size': [width, thick, L], 'checks': chk})
    # joint steps (going north): south end of segment i (north) vs north end of segment i+1... measured at the outer edge
    for i in range(N - 1):
        a, b = out[i], out[i + 1]
        out[i]['jointStepToSouthNeighbour'] = b['checks']['outerNorthVsDune'] - a['checks']['outerSouthVsDune']
    (OUT / 'h15-terrace-spec.json').write_text(json.dumps({'W': W, 'N': N, 'fallDeg': FALL, 'segments': out}, indent=1) + '\n')
    for s in out: print(s['id'], [round(x, 3) for x in s['t']], 'L %.3f' % s['size'][2], {k: round(v, 4) for k, v in s['checks'].items()}, round(s.get('jointStepToSouthNeighbour', 0), 4))
    return out


if __name__ == '__main__' and sys.argv[1] == 'segments':
    segments(*(float(x) if '.' in x else int(x) for x in sys.argv[2:]))
