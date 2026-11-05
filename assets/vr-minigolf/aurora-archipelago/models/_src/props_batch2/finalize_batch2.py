import json,math,hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
S=Path(__file__).resolve().parent;D=S.parents[2];M=D/'models';PV=M/'previews/props_batch2';NS=[9,10,11,12,13,15,16,17]
manifest=json.loads((M/'props_batch2_manifest.json').read_text());fit=json.loads((S/'fitcheck_report.json').read_text());verify=json.loads((S/'fbx_validation.json').read_text());assert fit['all_pass'] and verify['all_pass'];assert len(manifest['parts'])==len(fit['parts']);assert hashlib.md5((D/'holes.json').read_bytes()).hexdigest()=='4ee4f942c3b0c12627d7ce81a3831d4c'
for p in manifest['parts']:
 assert (M/p['fbx']).stat().st_size>1000
 assert p['tris']<20000 and p['max_mesh_tris']<20000
 assert Image.open(PV/(p['id']+'_34.png')).size==(1280,960)
 a=p['pivot_hole_local'];r=math.radians(p['world_yaw']);o=p['world_offset'];want=[a[0]*math.cos(r)+a[2]*math.sin(r)+o[0],a[1]+o[1],-a[0]*math.sin(r)+a[2]*math.cos(r)+o[2]];assert max(abs(x-y) for x,y in zip(want,p['pivot_world']))<1e-7
 assert not any(m['material'] in ['MoveRed','MoveCream','Cream','FlagRed'] for m in p['meshes']) or p['motion']
 if p['motion']:
  source=next(h for h in json.loads((D/'holes.json').read_text())['holes'] if h['number']==p['hole']);assert p['motion']==next(x for x in source['moving_parts'] if x['id']==p['id'].split('_',1)[1]);assert p['pivot_hole_local']==p['motion']['pivot']
sheet=Image.new('RGB',(1600,680),'#222233');dr=ImageDraw.Draw(sheet)
for i,n in enumerate(NS):
 im=Image.open(PV/f'h{n:02d}_34.png');assert im.size==(1280,960);sheet.paste(ImageOps.contain(im,(400,300)),((i%4)*400,(i//4)*340));dr.text(((i%4)*400+12,(i//4)*340+305),f'H{n:02d} Batch 2',fill='white')
sheet.save(PV/'contact_sheet.jpg',quality=95)
A=Image.open(D/'silhouettes/sheet03-h09-h13.png').convert('RGB');B=Image.open(D/'silhouettes/sheet04-h15-h17.png').convert('RGB');ranges={9:(A,27,273),10:(A,273,404),11:(A,404,653),12:(A,653,903),13:(A,903,1134),15:(B,28,430),16:(B,430,620),17:(B,620,1134)}
for n,(source,lo,hi) in ranges.items():
 pp=[p for p in manifest['parts'] if p['hole']==n];sk=[p for p in manifest['skipped'] if p['hole']==n];scale=source.height/1134;crop=source.crop((0,int(lo*scale),source.width,int(hi*scale)));height=550+220*math.ceil(len(pp)/4)+50*len(sk)
 out=Image.new('RGB',(1600,height),'white');dr=ImageDraw.Draw(out);out.paste(ImageOps.contain(crop,(1100,510)),(0,25));out.paste(ImageOps.contain(Image.open(PV/f'h{n:02d}_34.png'),(480,360)),(1110,60));dr.text((1110,430),f'H{n:02d}: source sheet and actual meshes',fill='black')
 for i,p in enumerate(pp):
  x=i%4*400;y=550+i//4*220;out.paste(ImageOps.contain(Image.open(PV/(p['id']+'_34.png')),(380,195)),(x,y));dr.text((x+8,y+195),p['id'],fill='black')
 yy=550+220*math.ceil(len(pp)/4)
 for i,p in enumerate(sk):dr.text((10,yy+i*50),('SKIPPED '+p['id']+': '+p['reason'])[:210],fill='#8A3232')
 out.save(PV/f'silhouette_compare_h{n:02d}.jpg',quality=95)
total=sum(p['tris'] for p in manifest['parts']);largest=max(p['max_mesh_tris'] for p in manifest['parts']);txt=f'# Batch 2\n\n{len(manifest["parts"])} built assets; {total:,} triangles; largest material mesh {largest:,}. ALL PASS: YES for built assets. FBX reimport checks all PASS. {len(manifest["skipped"])} source-conflicting or undefined pieces SKIPPED individually. Scope H9/H10/H11/H12/H13/H15/H16/H17; H4/H6/H14/H18 excluded. H15 is context-only because its requested pieces contradict gates or lack exact placement.\n\nSource holes.json MD5: 4ee4f942c3b0c12627d7ce81a3831d4c. Geometry takes priority over props.md and concept art. Both silhouette sheets inspected; available H9/H11/H12/H13/H17 paintovers used for mood. H10/H15/H16 paintovers absent.\n\n## Fitcheck and mover sweeps\n\nTriangle/OBB SAT against rails and 8-stud felt head volumes, slopes flattened by shear. Reported rail distances are conservative L-infinity lower bounds. Exact-source collider skins exempt their own colliders; low geometry stays in the footprint, with inset rounded snow shoulders. Flush cues stay below felt. Static rail minimum .1; mover minimum .05 per explicit batch 2 ruling; all nearby dressing >=.15. All meshes and files <20k; near field <34k/hole. Full continuous slide prisms and conservative 720-facet circumscribed rotation envelopes; no angle sampling gaps. Rotation minimum lower bound covers all angles. H12 critical felt angle computed from furthest vertex. Dressing checks use triangle radial intervals or triangle/translation-box SAT; central carousel axle against fixed pole is the only mechanical joint exception.\n\n'
txt+='Per-hole triangles: '+json.dumps(fit['hole_tris'])+'\n\n'
for r in fit['parts']:
 if r['sweep']:txt+='- '+r['id']+': '+json.dumps(r['sweep'])+'\n'
txt+='\n## Individual source contradictions\n\n'
for p in manifest['skipped']:txt+='- **'+p['id']+'**: '+p['reason']+'\n'
txt+='''
## Shape adaptations

- Open conch mouth uses an uncapped faceted shell loft with neon aperture rim, internal tapered spiral ridge and a visible exterior side spiral. Body follows exact rear occluder behind the spit ring, not approximate anchor-centred envelope. Exit retained as a source-conflict preview in preflight, then skipped for head volume.
- H10 tall-wall source boxes are fully filled with snow wall bodies, a glacier-ice lip and a white snow cap; all skin footprints match the source, including the S-run rails.
- Static red/cream requested by hut/ship concept text is superseded by mover-only colour rule: violet canvas, teal hull, warm timber/brass, white snow. Original palette and material names reused. No external bitmap textures required.
- Bobsled roof narrowed to 3.7 wide and 4 deep inside source envelope to retain .1 rail clearance; steep gable reaches y7, timber frame, bell and toy sled retained.
- Fishing tent depth reduced from 3 to 1.5 within its source envelope to clear pocket_w21; apex y4, chimney y6, source pivot unchanged.
- Icebreaker upper hull starts y1.11, above the y1 gameplay hull faces. Separate exact lower hull skins skipped at adjoining rail seam. Source hull halves and 2.4 wheel slot retained, cabins and brass funnel reach y8.
- Moonwell outer coping and crystals lie inside the two exact source occluders; 1.5-wide mass inset .1 per side to clear rail3/5. Source straight coping rails win over sheet's circular impression; no invented circular collider.
- Carousel exact source 48 strips form solid brass hub base, central post and 16-panel mint/violet canopy (underside9), weathervane to12. Four exact runners, elevated spokes, sleds and small snowpuffs.
- Aurora ribbon begins y10 and reaches y60 within 3x8 footprint; stationary timed deck is a separate mesh rooted at exact pivot. Runtime fade profile copied from holes.json. Crystal piers/bridge remain source-context-only where exact joins conflict with the required independent .1 rail gate.

## World pivot checks

1. H11 floe [0,0,-28] + offset [410,146,40], yaw0 -> [410,146,12].
2. H12 wheel [0,4.16,-17.75], offset [370,146,-60], yaw90 -> x=370-17.75=352.25, y=150.16, z=-60. World axis +X.
3. H10 hut [-7.5,0,-6], offset [510,146,60], yaw90 -> x=510-6=504, y=146, z=60-(-7.5)=67.5.

## Built assets

| ID | Triangles | Max material mesh | Local pivot | World pivot | Rail minimum |
|---|---:|---:|---|---|---:|
'''
by={r['id']:r for r in fit['parts']}
for p in manifest['parts']:txt+=f'| {p["id"]} | {p["tris"]} | {p["max_mesh_tris"]} | {p["pivot_hole_local"]} | {p["pivot_world"]} | {by[p["id"]]["min_rail_clearance"]:.6f} |\n'
txt+='''
## Rebuild and handoff

Run gen_batch2.py -> select_batch2.py (source-conflict list and measured raw preflight evidence are saved in preflight_fitcheck_report.json) -> build_batch2.py through models/_src/run_blender.ps1 -> fitcheck_batch2.py on actual build triangles -> verify_batch2.py through same runner -> finalize_batch2.py. gen/build/fitcheck reuse batch1 rev2 code copied into this source folder. Source-conflict evidence and rejected raw parts retained. FBX axes -Z/Y, scale1, embedded textures option enabled, root at asset zero pivot, one mesh per material. Place via manifest world pivot and placement yaw; all decoration CanCollide off. Motion metadata copied verbatim; runtime collider ownership stays with holes.json.

CPU Cycles12 samples at1280x960; eight hole context renders (H15 source blockout only), one render per built part, eight silhouette comparisons, contact sheet. props_batch2.blend and logs retained. No GUI Blender, Studio, restart or external messages. Existing batch1 artifacts untouched; overwritten README preserved in _backup. Completion flag follows image review, artifact audit and confirmation Blender exited.
'''
(S/'summary.md').write_text(txt,encoding='utf-8');r=M/'README.md';base=r.read_text(encoding='utf-8') if r.exists() else '# Aurora models\n';base=base.split('\n## Batch 2\n')[0];r.write_text(base+f'\n## Batch 2\n\n{len(manifest["parts"])} assets, {total:,} triangles; **ALL PASS: YES**, including all four full mover sweeps and FBX reimport. {len(manifest["skipped"])} individual source contradictions/undefined pieces skipped; H15 context-only.\n\n[Summary](_src/props_batch2/summary.md), [manifest](props_batch2_manifest.json), [fitcheck](fitcheck_props_batch2.txt), [contact sheet](previews/props_batch2/contact_sheet.jpg). Eight hole views and silhouette comparisons. Headless Blender5.2, CPU, -Z forward/Y up, scale1, exact pivots. Runtime motions copied from holes.json.\n',encoding='utf-8')
print('Artifacts and documentation validated; review previews and process exit before flag.')
