"""Stage sc11 item 1: whole-base gap of Look7 pieces (render mesh underside per column vs true ground).
For each piece: XZ grid (STEP studs) over its bounding box; top = first hit going DOWN from above; underside = first render-mesh hit going UP from below (EditableMesh
RaycastLocal on the piece's own MeshParts); ground = sc10_place.trueground from top + 120 (200-stud ray) (topmost render surface of Terrain +
visible non-dressing parts). Column gap = underside - ground (> 0 = air under the mesh, < 0 = buried).
  PYTHONPATH=tools python3 tools/sc11_caps.py OUT.json id [id ...]
"""
import json, sys
from pathlib import Path
import sc10_place as P
from sc5_util import studio, fetch
STEP = 1.0


def columns(s, ids):
    lua = Path('/tmp/sc11/underside.luau').read_text().replace('__IDS__', ','.join(map(str, ids))).replace('__STEP__', str(STEP))
    U = json.loads(fetch(s, '_G.SC5Out', lua, timeout=900))
    q = [{'id': '%s:%d' % (i, k), 'pts': [[c[0], u['top'] + 120, c[2]]]} for i, u in U.items() for k, c in enumerate(u['cols'])]
    G = P.trueground(s, q)
    out = {}
    for i, u in U.items():
        rows = []
        for k, c in enumerate(u['cols']):
            g = G['%s:%d' % (i, k)][0]
            rows.append({'x': c[0], 'z': c[2], 'under': c[1], 'top': c[3], 'ground': g[0] if g else None, 'groundPart': g[1].split('.')[-1] if g else None,
                         'gap': round(c[1] - g[0], 3) if g else None})
        gaps = [r['gap'] for r in rows if r['gap'] is not None]
        fl = [g for g in gaps if g > 0.1]
        snap = -((max(gaps) if gaps else 0) + 0.05)
        vis = [r for r in rows if r['ground'] is not None and r['top'] + snap > r['ground'] + 0.1]
        visNow = [r for r in rows if r['ground'] is not None and r['top'] > r['ground'] + 0.1]
        out[i] = {'snapDy': snap, 'visibleColsNow': len(visNow), 'visibleColsAfterSnap': len(vis),
                  'maxVisibleHeightAfterSnap': max([r['top'] + snap - r['ground'] for r in vis], default=0),
                  'maxVisibleHeightNow': max([r['top'] - r['ground'] for r in visNow], default=0),'bottom': u['bottom'], 'top': u['top'], 'columns': len(rows), 'noGround': sum(r['gap'] is None for r in rows),
                  'maxGap': max(gaps) if gaps else None, 'minGap': min(gaps) if gaps else None, 'floatCols': len(fl),
                  'floatFrac': round(len(fl) / len(gaps), 3) if gaps else None, 'rows': rows}
    return out


if __name__ == '__main__':
    s = studio(); ids = [int(x) for x in sys.argv[2:]]
    r = columns(s, ids); Path(sys.argv[1]).write_text(json.dumps(r) + '\n')
    for i, v in r.items():
        print(i, {k: v[k] for k in v if k != 'rows'})
