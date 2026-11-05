import json,math,shutil,hashlib,sys,subprocess
from pathlib import Path
S=Path(__file__).resolve().parent;D=S.parents[2];M=D/'models'
def read(p):return json.loads(p.read_text())
def write(p,v):p.write_text(json.dumps(v,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,log):
 with (S/log).open('w') as f:subprocess.run(args,cwd=D,stdout=f,stderr=subprocess.STDOUT,check=True)
def blender(script,b,log):run(['powershell','-NoProfile','-File',str(M/'_src/run_blender.ps1'),'-Script',str(M/f'_src/props_batch{b}'/script),'-Log',f'props_batch2/{log}'],log+'.launcher')
def prepare():
 assert hashlib.md5((D/'holes.json').read_bytes()).hexdigest()=='2f1402fe19fc98a303c4e58dae680be9'
 unchanged={};old={}
 for b in [1,2]:
  s=M/f'_src/props_batch{b}';ps=read(s/'parts.json');ids={p['id'] for p in ps if (b==1 and p['hole'] in [7,8] and 'coral' in p['id']) or (b==2 and p['id'] in ['h09_coral_spit','h15_ice_parapet','h17_ice_bridge'])}
  old[str(b)]=read(M/f'props_batch{b}_manifest.json')
  backup=s/'_backup_pre_rev4';assert backup.exists() if '--resume' in sys.argv else not backup.exists()
  paths=[p for p in s.iterdir() if p.is_file()]+list((M/f'fbx/props_batch{b}').glob('*'))+list((M/f'previews/props_batch{b}').glob('*'))+[M/f'props_batch{b}_manifest.json',M/f'fitcheck_props_batch{b}.txt',M/'README.md',M/'_src/PROGRESS.md']
  for p in paths:
   if p.exists() and '--resume' not in sys.argv:
    q=backup/p.relative_to(M);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
  for p in (M/f'fbx/props_batch{b}').glob('*.fbx'):
   if p.stem not in ids:unchanged[str(p.relative_to(D))]=sha(p)
  write(s/'rev4_ids.json',sorted(ids))
 
 if '--resume' not in sys.argv:write(S/'rev4_before.json',old);write(S/'rev4_unchanged.json',unchanged)
 sys.path.insert(0,str(S));import geometry as g
 H=g.H
 for b in ([2] if '--resume' in sys.argv else [1,2]):
  s=M/f'_src/props_batch{b}';ps=read(s/'parts.json');ids=set(read(s/'rev4_ids.json'))
  for p in ps:
   if p['id'] not in ids:continue
   q=g.Part(p['id'],p['hole'],[0,0,0]);col=next(iter(p['groups']))
   if b==1:
    seed=sorted(ids).index(p['id']);count=3+seed%3;base=0;yaw=0
    if p['hole']==7:
     a=next(a for a in H[7]['decoration_anchors'] if a['name']==p['id'][4:]);h=a['approx_size'][1];w=.5*h;d=.4*h
    elif 'giant' in p['id']:h=14;w=4;d=4
    else:
     wall=next(w for w in H[8]['walls'] if w['id']==p['skin_ids'][0]);base=1.6;h=2.4;w=1.2;d=min(.96,wall['size'][2]*.8);yaw=wall['yaw'];q.box(col,[0,.8,0],[wall['size'][0],1.6,wall['size'][2]],yaw)
    g.tube(q,col,[0,base,0],[0,base+.3*h,0],.075*h,.05*h,n=8)
    # Fan lobes diverge from the split, with explicit air gaps across the upper crown.
    lw=w/(count+(count-1)*.22);step=lw*1.22
    for k in range(count):
     x=(k-(count-1)/2)*step;z=((k+seed)%3-1)*d*.035;top=base+h*(1-.025*((k+seed)%3))
     rings=[]
     for t,sc in [(0,.13),(.25,.55),(.62,1),(.83,.96),(.95,.65),(1,.08)]:
      yy=base+.3*h+(top-base-.3*h)*t;xx=x*min(1,t*1.85)
      rings.append([[xx+lw*.5*sc*math.cos(math.tau*j/8),yy,z*t+d*.43*sc*math.sin(math.tau*j/8)] for j in range(8)])
     q.loft(col,rings);g.mound(q,'CoralMint',[x,top-h*.08,z-d*.28],[lw*.48,h*.065,d*.17],n=8)
    if yaw:
     for mat,(vs,fs) in q.g.items():
      start=8 if mat==col else 0;vs[start:]=[g.roty(v,yaw) for v in vs[start:]]
    p['notes'].append(f'Rev4: {count} separate flattened fan lobes; upper crown gaps {lw*.22:.4f}; rounded neon tips; trunk 0.15H to 0.10H at split 0.3H. Crown {w:g} x {d:g}. Prior footprint limits retained; collider base exact.')
   elif p['id']=='h17_ice_bridge':
    q.box('Ice',[0,-.3,0],[4,.6,24.7]);q.box('IceCore',[0,-.04,0],[3.6,.05,24.5])
    for x in [-2.25,2.25]:
     # Rounded bevelled timber rails stay inside their exact collider footprint.
     g.rounded(q,'Timber',[x,-.5,0],[.5,1.5,24.7],n=16)
     for z in [-12,-8,-4,0,4,8,12]:g.rounded(q,'Timber',[x,-.5,z],[.48,1.5,.45],n=4)
     for k in range(13):g.mound(q,'Snow',[x,1,-11.4+k*1.9],[.48,.3+.025*(k%3),1.9],n=6)
    for x in [-1.88,1.88]:g.rounded(q,'Snow',[x,-.14,0],[.22,.12,24.5],n=8)
    p['notes'].append('Rev4: bevelled rail edges; lumpy white snow caps ~0.3 thick; posts every 4 studs; frosted deck edges. All rail caps/posts within own collider footprint.')
   elif p['id']=='h15_ice_parapet':
    for k in range(7):
     x=-3.35+(k+.5)*6.7/7;hh=3.5+[-.35,.2,-.1,.4,-.25,.1,-.4][k]
     g.rounded(q,'IceGuard',[x,0,0],[6.7/7-.018,hh,.3],n=8)
     g.rounded(q,'Snow',[x,hh-.08,0],[6.7/7-.04,.08,.28],n=8)
    for k in [0,2,4,6]:
     x=-3.35+(k+.5)*6.7/7;hh=3.5+[-.35,.2,-.1,.4,-.25,.1,-.4][k]
     g.tube(q,'IceGuard',[x,hh-.07,.12],[x+.025,hh-.65-(k%3)*.12,.15],.06,.006,n=6)
    p['notes'].append('Rev4: seven chunky clear ice blocks, tops vary -0.4..+0.4; frosted tops and four front icicles. Intentional felt-overlap NOTE retained.')
   else:
    # Side skirt below felt. Nose flare reduced from .3 to .18 for the rail1 gap.
    w=3;d=12.2;n=32;rings=[]
    for yy,flare in [(0,.3),(.25,.22),(.75,.06),(1.0,0)]:
     ring=[]
     for j in range(n):
      t=math.tau*j/n;cx=math.cos(t);sz=math.sin(t);xx=(w/2+flare)*math.copysign(abs(cx)**.22,cx);zz=(d/2+(min(flare,.18) if sz>0 else flare))*math.copysign(abs(sz)**.22,sz)
      ring.append([xx,yy,zz])
     rings.append(ring)
    q.loft('CoralPink',rings)
    for side in [-1,1]:
     for k in range(19):
      z=-5.6+k*.6;x=side*(1.49+.12*(k%3)/2)
      g.mound(q,'CoralViolet' if 'CoralViolet' in read(S/'palette.json') else 'CoralPurple',[x,.25+(k%3)*.15,z],[.22,.24,.3],n=6)
    p['notes'].append('Rev4: bumpy pink/purple rock sides and polyp bumps; skirt flares 0.3 at bottom, locally reduced to 0.18 at north nose to retain >=0.1 rail clearance; all below felt underside.')
   p['groups']={m:dict(verts=v,faces=f) for m,(v,f) in q.g.items()}
   assert sum(len(f)-2 for gg in p['groups'].values() for f in gg['faces'])<=3000,p['id']
  write(s/'parts.json',ps);cache=read(s/'triangles.json');write(s/'triangles.json',{k:v for k,v in cache.items() if k not in ids})
  src=(s/('build_corals_rev3.py' if b==1 else 'build_skipfix_exit.py')).read_text()
  if b==1:src=src.replace('coral_rev3_ids.json','rev4_ids.json').replace('props_batch1_corals_rev3.blend','props_batch1_rev4.blend')
  else:src=src.replace("CHANGED={'h09_conch_exit'}", "CHANGED=set(json.loads((S/'rev4_ids.json').read_text()))").replace('for n in [9]:','for n in [9,15,17]:').replace('props_batch2.blend','props_batch2_rev4.blend')
  (s/'build_rev4.py').write_text(src)
if __name__=='__main__':
 try:prepare()
 except Exception as e:
  (S/'failed_rev4.flag').write_text(repr(e));raise
