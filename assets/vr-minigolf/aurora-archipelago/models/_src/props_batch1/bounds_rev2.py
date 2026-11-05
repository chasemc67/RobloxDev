from pathlib import Path
import json,math
S=Path('models/_src/props_batch1');P={p['id']:p for p in json.loads((S/'parts.json').read_text())}
for path in [Path('models/props_batch1_manifest.json'),S/'build_report.json']:
 d=json.loads(path.read_text())
 for r in d['parts']:
  vs=[v for g in P[r['id']]['groups'].values() for v in g['verts']];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];a=r['pivot_hole_local']
  r['bbox_asset_local']=[lo,hi];r['bbox_hole_local']=[[lo[i]+a[i] for i in range(3)],[hi[i]+a[i] for i in range(3)]]
  r['bbox']=r['bbox_asset_local'];r['dimensions']=[hi[i]-lo[i] for i in range(3)]
 path.write_text(json.dumps(d,indent=2))
p=S/'build_batch1.py';s=p.read_text();needle="r['lights']=[]";s=s.replace(needle,"vs=[v for g in p['groups'].values() for v in g['verts']];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]\n    r['bbox_asset_local']=[lo,hi];r['bbox_hole_local']=[[lo[i]+a[i] for i in range(3)],[hi[i]+a[i] for i in range(3)]];r['bbox']=r['bbox_asset_local'];r['dimensions']=[hi[i]-lo[i] for i in range(3)]\n    "+needle);p.write_text(s)
p=S/'finalize_rev2.py';s=p.read_text().replace('crown remains within source horizontal occluder despite the wider allowed sheet envelope','built crown follows the supplied seven-stud sheet envelope and passes the source rail/felt gates');p.write_text(s)
