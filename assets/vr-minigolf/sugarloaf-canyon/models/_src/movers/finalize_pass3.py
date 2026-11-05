import json,datetime,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
S=Path(__file__).resolve().parent;O=S.parent;B=S.parents[1]
r=json.loads((S/'fitcheck_results_pass3.json').read_text());m=json.loads((S/'movers_manifest.json').read_text())
assert r['all_pass'],'fitcheck must pass'
verify=json.loads((S/'export_verification_pass3.json').read_text());assert len(verify)==6 and all(e['pass_mesh_counts'] and e['pass_bbox'] and e['pass_origins'] and e['pass_material_merge'] for e in verify)
renderdir=O/'previews/cycles/final';views=[('rest','eye'),('rest','34'),('max','eye'),('max','34')]
for e in m['movers']:
 for state,view in views:assert (renderdir/f"{e['id']}_{state}_{view}.png").exists()
for state in ('rest','max'):assert (renderdir/f'h11_tee_{state}_eye.png').exists()
for rel,expected in json.loads((S/'input_hashes.json').read_text()).items():
 if rel.startswith('lib') or rel.endswith('holes.json'):assert hashlib.sha256((B/rel).read_bytes()).hexdigest()==expected,rel+' modified'
notes={
'h06_sluice_gate':'Derived from revised blocker thickness .636; existing face bands lie within that envelope.',
'h06_sluice_frame':'East post lower end y=2.6 clears revised pocket top y=2.55; x=3.98 unchanged. Wheel centre y=3.3, tie centres y=2.75 clear new pocket walls.',
'h11_lock_lift':'Re-pivoted to north hinge [0,0,-25]; full deck 3.2 x 3.35 centred z=-23.325, south strip removed. Red #B83A35 / cream #FFF0C9 bands .6 along x on transverse edges, .6 along z on side edges, .18 wide fascia; final renders provide readability review.',
'h11_lock_gate':'Face bands and iron inlaid inside exact .5 blocker depth to preserve .15 cut clearance.',
'h11_lock_chamber':'Support/wheel x moved +/-3 to +/-4.8 to clear revised funnel backing. Signal housing centre [0,5.9,-26], size [.8,1.2,.3]; lamps [0,6.18,-25.8] and [0,5.62,-25.8]. Slot cheeks width reduced 3.9 to 3.3 to clear approach guides.',
'h11_quay_lip':'Exact revised 3.6 x 1.5 x .2, top y=5 raised / y=4 lowered. Six .6 alternating x bands #B83A35/#FFF0C9. FBX bottom-centre pivot [0,3.5,-25.45] is [0,-.75,0] offset from holes_rev centre pivot [0,4.25,-25.45].'}
for e in m['movers']:
 e['validation_status']='PASS_WITH_REQUIRED_STUDIO_CUTS';e['clearances']=r['results'][e['id']];e['minimum_non_exempt']=r['per_prop_minima'][e['id']]
 e['required_collision_cuts']=[x for x in r['cuts'] if x['prop']==e['id']]
 e['notes']=notes.get(e['id'],'Re-derived from holes_rev.json; rebuilt FBX.')
 e['roundtrip']=next(x for x in verify if x['id']==e['id'])
 if e['id']=='h11_lock_lift':e['motion']=dict(cycle_s=10.6,rise=4,rise_start=5.5,rise_end=7.5,tilt_release_end=7.65,return_end=9.15,tilt_deg=4,tilt_axis=[-1,0,0],hinge_edge='north z=-25',static_lock_felt='REMOVE/HIDE; replace collision with moving deck')
 if e['id']=='h11_quay_lip':
  e['motion']=dict(cycle_s=10.6,axis=[0,-1,0],raised_offset=0,flush_offset=-1,sink_start=7.4,sink_end=7.5,hold_end=7.65,rise_end=7.75,speed=10)
  e['params_status']='FINAL holes_rev.json'
  e['spec_centre_pivot']=[0,4.25,-25.45];e['export_pivot_offset']=[0,-.75,0]
m.update({'pass':3,'required_studio_cuts':r['cuts'],'minimum_non_exempt':r['minimum'],'per_prop_minima':r['per_prop_minima'],'preview_engine':'Cycles OptiX','preview_status':'FINAL'})
m.pop('proposed_additional_cuts_pending_decision',None)
sheet=Image.new('RGB',(1600,6*350+330),(35,29,37));draw=ImageDraw.Draw(sheet)
for row,e in enumerate(m['movers']):
 for col,(state,view) in enumerate(views):
  im=Image.open(renderdir/f"{e['id']}_{state}_{view}.png").convert('RGB');im.thumbnail((400,310));sheet.paste(im,(col*400,row*350+30));draw.text((col*400+5,row*350+8),f"{e['id']} {state} {view}",fill='white')
for col,state in enumerate(('rest','max')):
 im=Image.open(renderdir/f'h11_tee_{state}_eye.png').convert('RGB');im.thumbnail((400,300));sheet.paste(im,(col*400,2130));draw.text((col*400+5,2110),f'H11 actual tee, VR eye 5: {state}',fill='white')
sheet.save(renderdir/'contact_sheet.png');m['previews']=[str(p.relative_to(O)) for p in sorted(renderdir.glob('*.png'))]
(S/'movers_manifest.json').write_text(json.dumps(m,indent=2))
lines=['# SRV-132 H6 + H11 movers pass 3', 'ALL PASS against holes_rev.json, the source of truth. Both input JSON files and protected library remain unchanged. Six FBX round trips pass counts, bounds, origins, material merge and budgets.', '', '| Prop | Hole-local export pivot | World pivot | Tris | MeshParts | Minimum |', '|---|---|---|---:|---:|---|']
for e in m['movers']:
 b=e['minimum_non_exempt'];lines.append(f"| {e['id']} | {e['pivot']} | {e['world_pivot']} | {e['tris']} | {e['MeshParts']} | {b['clearance']:.9f} / {b['obstacle']} |")
lines+=['',*notes.values(),'', 'H11 cycle 10.6 s: gate down dwell 4.85, rises 4.85-5.5, up dwell 4.45, lowers 9.95-10.6. Lift rise 5.5-7.5, tilt/release 7.5-7.65, return 7.65-9.15, north hinge tilt 4 degrees.', 'Lip finite-speed interpretation: speed 10 requires .1 s transitions. Sink 7.4-7.5; top is exactly y=4 only in [7.5,7.65); rise 7.65-7.75. motion.lua and sweep use this same schedule.', '', 'Approved cut targets include revised split descendants; no additional cut volumes added. Residual cut-target clearance >=.15; other non-contact pairs >=.05; H6 gate/east post >=.15. Static support felt contacts are explicit in certificate.', 'Overall minimum: '+json.dumps(r['minimum']), '', 'Validation: fitcheck_movers_pass3_validated.txt (overall/per-prop minima and locations); fitcheck_results_pass3.json. Triangle/OBB SAT conservative separation, full-cycle .005 s samples and explicit tilt sweep.', 'Final Cycles OptiX renders: out/previews/cycles/final/<prop>_{rest,max}_{eye,34}.png, actual H11 tee rest/max, contact_sheet.png. Sequential process-gated Blender launches, 30 s polling when busy.', 'All six FBXs rebuilt. Re-sync exports with their manifest pivots; decorative meshes CanCollide=false, gameplay collision derives from revised JSON.']
(S/'movers_pass3_summary.md').write_text('\n'.join(lines),encoding='utf-8')
m['source_of_truth']='in/holes_rev.json';m['source_sha256']=hashlib.sha256((B/'in/holes_rev.json').read_bytes()).hexdigest()
(S/'movers_manifest.json').write_text(json.dumps(m,indent=2))
(S/'README.md').write_text('SRV-132 pass 3: see movers_pass3_summary.md. Source of truth in/holes_rev.json. Six exports, validated certificate, 10.6 s motion.lua and FINAL Cycles OptiX previews.\n')
with (S/'PROGRESS.md').open('a') as f:f.write('\n- '+datetime.datetime.now().astimezone().isoformat()+' Pass 3 COMPLETE: all six ALL PASS; FBX roundtrip verified; 26 FINAL Cycles OptiX views and contact sheet; summary/manifest/motion updated; protected input hashes unchanged.\n')
(O/'DONE.txt').write_text('SRV-132 PASS 3 COMPLETE\nALL PASS (holes_rev approved collision cuts).\nSummary: src/movers_pass3_summary.md\nValidation: src/fitcheck_movers_pass3_validated.txt\nFINAL: previews/cycles/final/contact_sheet.png\n')
