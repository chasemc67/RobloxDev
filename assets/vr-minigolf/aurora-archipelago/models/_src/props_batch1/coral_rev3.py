"""Scoped coral revision; preserve every unrelated asset and immutable backup."""
import json, math, shutil, hashlib, datetime, subprocess, sys
from pathlib import Path
S=Path(__file__).resolve().parent; D=S.parents[2]; M=D/'models'; PV=M/'previews/props_batch1'
def read(p): return json.loads(p.read_text())
def write(p,v): p.write_text(json.dumps(v,indent=2))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,log):
    with (S/log).open('w') as f:
        subprocess.run(args,cwd=D,stdout=f,stderr=subprocess.STDOUT,check=True)
def blender(script,log):
    run(['powershell','-NoProfile','-File',str(M/'_src/run_blender.ps1'),'-Script',str(S/script),'-Log','props_batch1/'+log],log+'.launcher')
def main():
    assert hashlib.md5((D/'holes.json').read_bytes()).hexdigest()=='2f1402fe19fc98a303c4e58dae680be9'
    old=read(M/'props_batch1_manifest.json'); parts=read(S/'parts.json')
    ids={p['id'] for p in parts if (p['hole']==7 and 'coral_' in p['id']) or (p['hole']==8 and 'coral' in p['id'])}; assert len(ids)==18
    stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    backup=S/'_backup_rev2_corals'/('current_before_rev3_'+stamp)
    paths=[M/p['fbx'] for p in old['parts'] if p['id'] in ids]+[PV/(i+'_34.png') for i in ids]
    paths += [PV/n for n in ['h07_34.png','h08_34.png','contact_sheet.jpg','silhouette_compare_h07.jpg','silhouette_compare_h08.jpg']]
    paths += [M/'props_batch1_manifest.json',M/'fitcheck_props_batch1.txt',M/'README.md',S/'summary.md',S/'parts.json',S/'triangles.json',S/'build_report.json',S/'fitcheck_report.json',S/'fbx_validation.json']
    for p in paths:
        if p.exists():
            dest=backup/p.relative_to(D); dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,dest)
    untouched={str(p.relative_to(D)):sha(p) for p in (M/'fbx/props_batch1').glob('*.fbx') if p.stem not in ids}
    untouched.update({str(p.relative_to(D)):sha(p) for p in PV.glob('*_34.png') if p.stem[:-3] not in ids and p.name not in ['h07_34.png','h08_34.png']})
    write(S/'coral_rev3_unchanged.json',untouched); write(S/'coral_rev3_ids.json',sorted(ids))
    # Load only reusable helper definitions, never execute the batch generator.
    env={'__file__':str(S/'gen_batch1.py')}; source=(S/'gen_batch1.py').read_text(); exec(source[:source.index('# H1:')],env)
    Part=env['Part']; tube=env['tube']; roty=env['roty']; H=env['H']
    heights=[4.5,6,3.5,5.5,4,4,5.5,3,6,4.5]; changes=[]
    def blob(q,col,c,size):
        x,y,z=c; w,h,d=size
        rings=[[[x+w*.5*sc*math.cos(math.tau*k/6),y+h*t,z+d*.5*sc*math.sin(math.tau*k/6)] for k in range(6)] for sc,t in [(.35,0),(.92,.2),(1,.55),(.7,.88)]]
        rings.append([[x,y+h,z]]); q.loft(col,rings)
    for p in parts:
        if p['id'] not in ids: continue
        seed=sorted(ids).index(p['id']); count=3+seed%3; q=Part(p['id'],p['hole'],[0,0,0])
        col=next(iter(p['groups'])); yaw=0; base=0; scale=1.
        if p['hole']==7:
            idx=next(i for i,x in enumerate(parts) if x['id']==p['id'])
            a=next(a for a in H[7]['decoration_anchors'] if a['name']==p['id'][4:]); h=a['approx_size'][1]; w=.5*h; d=.4*h
        elif 'giant' in p['id']:
            h=14; w=4; d=4; scale=4/7 # Exact 4x14x4 occluder limits crown width.
        else:
            collider=next(x for x in H[8]['walls'] if x['id']==p['skin_ids'][0]); base=1.6; h=2.4; w=1.2; d=min(.96,collider['size'][2]*.8); yaw=collider['yaw']; scale=d/.96
            q.box(col,[0,.8,0],[collider['size'][0],1.6,collider['size'][2]],yaw)
        r=.075*h; fork=[0,base+.3*h,0]
        tube(q,col,[0,base,0],fork,r,r*.9,n=5)
        for k in range(count):
            u=k/(count-1)-.5; x=u*w*.62; z=((k+seed)%3-1)*d*.05
            mid=[x*.45,base+h*.47,z*.4]; end=[x*.82,base+h*.62,z*.8]; tip=[x,base+h*(.74+.025*((k+seed)%2)),z]
            for aa,bb,rr in [(fork,mid,r*.8),(mid,end,r*.7),(end,tip,r*.6)]: tube(q,col,aa,bb,rr,rr*.85,flatten=.45,n=5)
            # Adjacent swollen lobes overlap horizontally and vertically into one crown.
            blob(q,col,[x,base+h*(.62+.025*((k+seed)%2)),z],[w*.38,h*.355,d*.9])
            blob(q,'CoralMint',[x,base+h*(.87+.025*((k+seed)%2)),z-d*.27],[w*.13,h*.06,d*.16])
        # Transform coral only; base is already in collider yaw.
        if yaw:
            for mat,(vs,fs) in q.g.items():
                start=8 if mat==col else 0
                vs[start:]=[roty(v,yaw) for v in vs[start:]]
        p['groups']={k:dict(verts=v,faces=f) for k,(v,f) in q.g.items()}
        note=f'Coral rev3: {count} flattened fans, three branch stages after short 0.3H trunk of thickness 0.15H; overlapping swollen rounded crown and mint neon tip cores. Crown {w:g} x {d:g}, coral height {h:g} above y{base:g}.'
        if scale<1: note+=f' Crown depth/width limited minimally to source occluder/authorized footprint (ratio {scale:.6f}); height retained.'
        p['notes'].append(note); changes.append(dict(id=p['id'],height=h,width=w,depth=d,limitation=note))
    write(S/'parts.json',parts); write(S/'coral_rev3_shapes.json',changes)
    # Invalidate changed triangle caches for source preflight.
    cache=read(S/'triangles.json'); cache={k:v for k,v in cache.items() if k not in ids}; write(S/'triangles.json',cache)
    run([sys.executable,str(S/'fitcheck_batch1.py')],'coral_rev3_preflight.log')
    src=(S/'build_skipfix.py').read_text().replace("skipfix_ids.json","coral_rev3_ids.json").replace('for n in [5]:','for n in [7,8]:').replace("props_batch1.blend'","props_batch1_corals_rev3.blend'")
    (S/'build_corals_rev3.py').write_text(src)
    blender('build_corals_rev3.py','coral_rev3_build.log')
    run([sys.executable,str(S/'fitcheck_batch1.py')],'coral_rev3_exported.log')
    blender('verify_batch1.py','coral_rev3_verify.log')
    assert read(S/'fitcheck_report.json')['all_pass'] and read(S/'fbx_validation.json')['all_pass']
    for path,digest in untouched.items(): assert sha(D/path)==digest,path
    new=read(M/'props_batch1_manifest.json'); prev={p['id']:p for p in old['parts']}
    for p in new['parts']:
        if p['id'] not in ids: assert p==prev[p['id']]
        else: assert p['pivot_hole_local']==prev[p['id']]['pivot_hole_local'] and p['pivot_world']==prev[p['id']]['pivot_world']
    from PIL import Image,ImageOps,ImageDraw
    sheet=Image.new('RGB',(1200,660),'#222233'); draw=ImageDraw.Draw(sheet)
    for i,n in enumerate([1,2,3,5,7,8]):
        sheet.paste(ImageOps.contain(Image.open(PV/f'h{n:02d}_34.png'),(400,300)),((i%3)*400,(i//3)*330)); draw.text(((i%3)*400+12,(i//3)*330+305),f'H{n:02d} / Coral rev3' if n in [7,8] else f'H{n:02d}',fill='white')
    sheet.save(PV/'contact_sheet.jpg',quality=94)
    B=Image.open(D/'silhouettes/sheet02-batch1-h05-h08.png').convert('RGB')
    for n,lo,hi in [(7,716,848),(8,848,1134)]:
        ps=[p for p in new['parts'] if p['id'] in ids and p['hole']==n]; top=300 if n==7 else 540
        im=Image.new('RGB',(1700,top+240*math.ceil(len(ps)/5)+40),'white'); dr=ImageDraw.Draw(im); dr.text((15,10),f'H{n:02d} Coral rev3 / supplied silhouette and CPU renders',fill='black')
        im.paste(ImageOps.contain(B.crop((0,lo*2,B.width,hi*2)),(1700,top-35)),(0,35))
        for i,p in enumerate(ps):
            x=i%5*340; y=top+i//5*240; im.paste(ImageOps.contain(Image.open(PV/(p['id']+'_34.png')),(330,210)),(x,y)); dr.text((x+8,y+215),p['id'],fill='black')
        im.save(PV/f'silhouette_compare_h{n:02d}.jpg',quality=94)
    text='\n\n## Coral rev3\n\n18 coral assets rebuilt with short thick trunks, three branching stages into 3–5 flattened fans, overlapping rounded swollen crown tips and mint neon cores. All anchors, pivots, colours and unrelated exports preserved. Headless Blender via run_blender.ps1, Cycles CPU. Exported triangle fitcheck ALL PASS: YES; FBX reimport ALL PASS: YES.\n\n| Coral | Tris before | Tris after |\n|---|---:|---:|\n'
    for p in new['parts']:
        if p['id'] in ids: text+=f"| {p['id']} | {prev[p['id']]['tris']} | {p['tris']} |\n"
    text+='\nGiant crown limited from 7 to 4 studs wide to remain inside its exact 4×14×4 occluder; coral height remains 14. H8 narrow bumper crown depths limited from .96 to .8 to remain in the source occluders, with exact collider bases retained; coral height remains 2.4 above the 1.6 base. Other clumps retain requested crown sizes. Every coral remains under 900 tris; every material mesh under 20k.\n\nCurrent-state backup: `'+str(backup.relative_to(D))+'`. Original backup preserved. Evidence: coral_rev3_preflight.log, coral_rev3_exported.log, coral_rev3_verify.log, coral_rev3_unchanged.json.\n'
    with (S/'summary.md').open('a',encoding='utf-8') as f:f.write(text)
    with (M/'README.md').open('a',encoding='utf-8') as f:f.write('\n\n## Coral rev3\n\n18 H7/H8 coral exports updated; overlapping lumpy crowns, flattened branching fans and neon tips. Fitcheck and FBX reimport ALL PASS. Other assets unchanged. See [_src/props_batch1/summary.md](_src/props_batch1/summary.md#coral-rev3) for triangle changes and footprint limits.\n')
    write(S/'coral_rev3_completion.json',dict(backup=str(backup),changed=sorted(ids),all_pass=True))
    print('READY_FOR_VISUAL_REVIEW',flush=True)
if __name__=='__main__':
    try:main()
    except Exception as e:
        (S/'failed_corals.flag').write_text('Coral rev3 failed: '+repr(e)+'\nSee coral_rev3 logs.\n'); raise
