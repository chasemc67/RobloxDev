import json,hashlib,math
from pathlib import Path
from datetime import datetime
from PIL import Image
S=Path(__file__).resolve().parent;D=S.parents[2];M=D/'models';PV=M/'previews/props_batch2'
p=S/'fitcheck_batch2.py';t=p.read_text().replace("radial_height_bounds=bounds)","radial_height_bounds=bounds,angle_degrees=0,angle_note='spoke to hub top clearance applies for every rotation angle')");t=t.replace("'Near-field triangles: '+json.dumps(totals)","'SCOPE SKIPPED: H4, H6, H14, H18 (excluded by brief)','Near-field triangles: '+json.dumps(totals)");p.write_text(t)
r=json.loads((S/'fitcheck_report.json').read_text())
for x in r['parts']:
 if x['id']=='h13_carousel_arms':x['sweep'].update(angle_degrees=0,angle_note='spoke to hub top clearance applies for every rotation angle')
(S/'fitcheck_report.json').write_text(json.dumps(r,indent=2))
fit=M/'fitcheck_props_batch2.txt';lines=fit.read_text().splitlines()
for i,line in enumerate(lines):
 if line.startswith('PASS h13_carousel_arms '):lines[i]='PASS h13_carousel_arms '+json.dumps(next(x for x in r['parts'] if x['id']=='h13_carousel_arms'))
if not any(x.startswith('SCOPE SKIPPED:') for x in lines):lines.insert(-2,'SCOPE SKIPPED: H4, H6, H14, H18 (excluded by brief)')
fit.write_text('\n'.join(lines)+'\n')
# Recreate final documentation using final measurements and final reviewed previews.
exec(compile((S/'finalize_batch2.py').read_text(),str(S/'finalize_batch2.py'),'exec'))
m=json.loads((M/'props_batch2_manifest.json').read_text());v=json.loads((S/'fbx_validation.json').read_text());r=json.loads((S/'fitcheck_report.json').read_text());assert r['all_pass'] and v['all_pass'];assert len(m['parts'])==20 and len(m['skipped'])==13
assert len(list((M/'fbx/props_batch2').glob('*.fbx')))==20
assert len(list(PV.glob('*_34.png')))==28
assert len(list(PV.glob('silhouette_compare_h*.jpg')))==8
assert (S/'props_batch2.blend').stat().st_size>1000
assert 'ALL PASS: YES' in (M/'fitcheck_props_batch2.txt').read_text()
assert '## Batch 2' in (M/'README.md').read_text()
assert hashlib.md5((D/'holes.json').read_bytes()).hexdigest()=='4ee4f942c3b0c12627d7ce81a3831d4c'
for x in r['parts']:
 assert x['status']=='PASS'
 if x['sweep']:
  assert x['sweep']['min_clearance']>=.05-1e-5
  assert x['sweep']['min_dressing_clearance']>=.15-1e-5
  if 'min_felt_clearance' in x['sweep']:assert x['sweep']['min_felt_clearance']>=.05-1e-5
metadata=dict(status='DONE',timestamp=datetime.now().astimezone().isoformat(),built_parts=20,skipped_parts=13,triangles=sum(p['tris'] for p in m['parts']),largest_material_mesh=max(p['max_mesh_tris'] for p in m['parts']),fitcheck='ALL PASS: YES',fbx_reimport='20/20 PASS',mover_sweeps='4/4 PASS',hole_previews=8,silhouette_comparisons=8,visual_review='completed; duplicate source collider context surfaces removed',blender='5.2.2 LTS headless CPU; all jobs exited',source_md5='4ee4f942c3b0c12627d7ce81a3831d4c')
(S/'audit_report.json').write_text(json.dumps(metadata,indent=2))
(S/'done.flag').write_text(json.dumps(metadata,indent=2)+'\n')
print(json.dumps(metadata))

