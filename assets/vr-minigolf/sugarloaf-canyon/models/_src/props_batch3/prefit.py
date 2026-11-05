# quick pre-Blender check: fan-triangulate parts.json -> /tmp/b3pre/{triangles,build_report}.json
import json, os
P = json.load(open('parts.json')); os.makedirs('/tmp/b3pre', exist_ok=True); T = {}; R = {'parts': []}
for p in P:
    tr = []; mx = 0
    for g in p['groups'].values():
        V = g['verts']; n = 0
        for f in g['faces']:
            for i in range(1, len(f)-1): tr.append([V[f[0]], V[f[i]], V[f[i+1]]]); n += 1
        mx = max(mx, n)
    T[p['id']] = tr; R['parts'].append(dict(id=p['id'], hole=p['hole'], anchor_local=p['anchor'], envelope=p['envelope'], tris=len(tr), max_mesh_tris=mx, notes=p['notes']))
json.dump(T, open('/tmp/b3pre/triangles.json', 'w')); json.dump(R, open('/tmp/b3pre/build_report.json', 'w'))
