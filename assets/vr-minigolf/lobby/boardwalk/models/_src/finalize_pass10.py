from pathlib import Path
import json,hashlib,datetime
from PIL import Image
import numpy as np
s=Path(__file__).parent;r=s.parent;job=r.parent.parent.parent;b=r/'_backup_pass9'
m=json.loads((r/'manifest.json').read_text());old=json.loads((b/'manifest.json').read_text());audit=[]
def check(ok,label):
 audit.append(('PASS ' if ok else 'FAIL ')+label)
 if not ok:raise RuntimeError(label)
changed={e['name'] for e in m['props'] if any(x in e['name'] for x in ['sugarloaf_crystals_','aurora_rocks_'])}
for n in ['fitcheck_pass10_validated.txt','reimport_check_pass10.txt']:check('RESULT: ALL PASS' in (s/n).read_text(),n)
for n in ['build','fitcheck','reimport','render']:
 data=(s/(n+'_pass10.log')).read_bytes();t=data.decode('utf-16' if data.startswith(b'\xff\xfe') else 'utf-8',errors='replace')
 check('Blender quit' in t and 'Traceback' not in t,n+' Blender exited successfully')
check((s/'pass10_geo.py').read_bytes()==(job/'pass10_geo.py').read_bytes(),'supplied source byte identical')
oldprops={e['name']:e for e in old['props']}
for e in m['props']:
 check(e['triangles']<20000,e['name']+' <20k')
 if e['name'] not in changed:
  check((r/e['fbx']).read_bytes()==(b/e['fbx']).read_bytes(),e['name']+' unchanged SHA256 '+hashlib.sha256((r/e['fbx']).read_bytes()).hexdigest())
  check(e==oldprops[e['name']],e['name']+' manifest entry unchanged')
 else:
  check((r/e['fbx']).read_bytes()!=(b/e['fbx']).read_bytes(),e['name']+' rebuilt')
  e['source_sha256']=hashlib.sha256((s/'pass10_geo.py').read_bytes()).hexdigest()
  e['notes']='Exact supplied pass10 geometry; tighter base candy clusters; Glow_Crystal emission0.2 from Col.' if 'crystals_' in e['name'] else 'Exact supplied taller ten-rock snowy mound; two collision boxes follow front outer and rear bounds, clear A/B and snowpuff.'
  (s/'manifest_parts'/(e['name']+'.json')).write_text(json.dumps(e,indent=1))
counts={e['name']:e['triangles'] for e in m['props']};total=sum(counts[i['asset']] for i in m['instances'])
check(total==m['totals']['tris_total'] and total<120000,'placed lobby <120k: '+str(total))
m['materials']['Glow_Crystal'].update(Material='Neon',roblox_material='Neon',preview_emission_strength=.2,colors=['#F59AC8','#FFF1A8'],note='Neon in Roblox, keep Brightness low / or use SmoothPlastic + slight glow if Neon blows out')
m['pass10_preview']=dict(view_transform='Standard',world_strength=.9,Glow_Tips_emission=1.5,Glow_Crystal_emission=.2,vertex_colour_attribute='Col',engine='BLENDER_EEVEE')
(r/'manifest.json').write_text(json.dumps(m,indent=1))
for c in ['lantern_grove','sugarloaf_canyon','aurora_archipelago']:
 for view in ['eye','34']:check(Image.open(r/'previews/portals'/(c+'_'+view+'.png')).size==(960,960),c+' '+view+' rendered')
check(Image.open(r/'previews/portals/aurora_crown_closeup.png').size==(960,960),'crown closeup rendered')
check((r/'previews/portals/portals_vs_concepts.png').exists(),'comparison sheet rendered')
# Side strips exclude the pink portal surface, testing visible crystal colors against the backed-up preview.
pixels={}
for view in ['eye','34']:
 samples=[]
 for folder in [r,b]:
  a=np.asarray(Image.open(folder/'previews/portals'/('sugarloaf_canyon_'+view+'.png')).convert('RGB')).astype(int)
  rr,gg,bb=a[:,:,0],a[:,:,1],a[:,:,2];mask=np.zeros(rr.shape,bool);mask[250:810,40:345]=True;mask[250:810,615:920]=True
  pink=mask&(rr>180)&(bb>145)&(rr-gg>25)&(bb-gg>15)
  yellow=mask&(rr>190)&(gg>180)&(rr-bb>25)&(gg-bb>20)&(rr-gg<25)&(bb>160)
  samples.append(dict(pink_pixels=int(pink.sum()),yellow_pixels=int(yellow.sum()),white_pixels=int((mask&(rr>245)&(gg>245)&(bb>245)).sum()),pink_median=np.median(a[pink],axis=0).tolist() if pink.any() else None,yellow_median=np.median(a[yellow],axis=0).tolist() if yellow.any() else None))
 pixels[view]=dict(pass10=samples[0],pass9=samples[1])
 check(samples[0]['pink_pixels']>100 and samples[0]['yellow_pixels']>100,view+' visible saturated pink/yellow candy pixels')
(s/'preview_colour_pass10.json').write_text(json.dumps(pixels,indent=2))
mins=json.loads((s/'clearance_pass10.json').read_text())
lines=['# Pass 10 completed','',f'Placed lobby: **{total:,} triangles**. Every mesh <20k; fitcheck and FBX reimport ALL PASS.','', 'Only four FBXs rebuilt from byte-identical pass10_geo.py: Sugarloaf west/east candy (tighter base clusters) and Aurora west/east snowy rocks (taller ten-rock mounds). No supplied shapes, positions or colors changed. All other FBXs verified by SHA256 against _backup_pass9, and their manifest entries remain identical.','', 'Two collision boxes per rock pile follow the new mound bounds: front outer section and rear section. The front inner edge leaves the snowpuff footprint clear; these are simple collision approximations. Zones A/B and trigger clearance independently measured against exported triangles. Snowpuff and six lantern anchors unchanged.','', 'Standard transform, Col vertex colors, bright flat lighting and established cameras retained. Glow_Crystal emission 0.2 from vertex color; source pink #F59AC8 / yellow #FFF1A8. Glow_Tips remains1.5 cyan. All six portal views, crown closeup and comparison sheet re-rendered using the established permitted Eevee fallback. Pixel evidence: preview_colour_pass10.json. Displayed swatches vary with lighting; source colors are independently checked against FBX corners.','', '## Triangles','', '| Mesh | Tris | Instances | Placed tris |','|---|---:|---:|---:|']
for e in m['props']:lines.append(f"|{e['name']}|{e['triangles']}|{e['builder_count']}|{e['tris_x_count']}|")
lines+=['','## Portal totals','','| Course | Tris |','|---|---:|']
for c in ['lantern_grove','sugarloaf_canyon','aurora_archipelago']:
 n=sum(e['triangles'] for e in m['props'] if e.get('course')==c or e['name'].startswith('bw_arch_'+c) or e['name']=='bw_portal_surface_'+c or e['name'] in ['bw_portal_apron','bw_arch_nameplate'] or c!='lantern_grove' and e['name']=='bw_coming_soon_sign');lines.append(f'|{c}|{n}|')
lines+=['','## Zone minima','','| Mesh | A | B | Trigger |','|---|---:|---:|---:|']
for name,d in mins.items():lines.append(f"|{name}|{d['A']}|{d['B']}|{d['trigger']}|")
lines+=['','No Roblox application opened or touched. Blender ran directly, sequentially; every own instance exited. Backup: _backup_pass9. Rebuild: build_pass10.py, fitcheck_pass10.py, reimport_pass10.py, render_pass10.py (Blender); compose_pass3.py and finalize_pass10.py (Python).']
(s/'pass10_summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
p=r/'README.md';t=p.read_text(encoding='utf-8').split('\n## Pass 10')[0];t+='\n## Pass 10 current authoritative assets\n\nOnly Sugarloaf crystal west/east and Aurora rock west/east FBXs rebuilt using exact pass10_geo.py. Tighter candy bases, taller snowy mounds with two collision boxes per pile clear of zones A/B and the snowpuff footprint. All other FBXs and their manifest entries unchanged from pass9. Standard/Col previews use Glow_Crystal emission 0.2, pink #F59AC8 / yellow #FFF1A8; Glow_Tips remains 1.5. Neon in Roblox: keep Brightness low, or use SmoothPlastic with slight glow if Neon blows out.\n\nFitcheck and reimport ALL PASS; placed lobby '+str(total)+' triangles, every mesh <20k. See [_src/pass10_summary.md](_src/pass10_summary.md) for counts, group totals, clearance and caveats. Pixel checks: _src/preview_colour_pass10.json. Backup: _backup_pass9. No Roblox application opened.\n';p.write_text(t,encoding='utf-8')
audit.append('RESULT: ALL PASS');(s/'artifact_audit_pass10.txt').write_text('\n'.join(audit)+'\n')
with (s/'PROGRESS_pass10.md').open('a') as f:f.write(datetime.datetime.now().isoformat()+' Export, fitcheck, reimport, render, hashes, pixel checks and documentation complete. All own Blender calls exited.\n')
print('ALL PASS',total,pixels)

