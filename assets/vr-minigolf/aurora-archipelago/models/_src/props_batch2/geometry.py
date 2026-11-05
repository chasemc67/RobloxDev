"""Pure geometry generator. Source boxes determine bounds; details are proportional subdivisions."""
import json, math, ast
from pathlib import Path
import numpy as np
S=Path(__file__).resolve().parent
D=S.parents[2]
H={h['number']:h for h in json.loads((D/'holes.json').read_text())['holes']}
# Reuse Sugarloaf's material-group mesh builder and loft pattern, without its batch data.
ref=(D.parent/'ref/sugarloaf/gen_batch3.py').read_text()
exec(ref[ref.index('def roty'):ref.index('def anchor')])
exec(ref[ref.index('def loft'):ref.index('def circ')])
palette_tree=ast.parse((D.parent/'ref/aurora_p1_src/aalib.py').read_text())
PAL=next(ast.literal_eval(n.value) for n in palette_tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MATS' for t in n.targets))
P=[]; skipped=[]
def a(n,name): return next(x for x in H[n]['decoration_anchors'] if x['name']==name)
def part(n,name,pivot=None,skins=(),felt_skins=()):
    p=Part(f'h{n:02d}_{name}',n,pivot or a(n,name)['position']); p.skin_ids=list(skins);p.felt_skins=list(felt_skins);p.motion=None;P.append(p);return p
def box(p,m,c,size,yaw=0): p.box(m,[c[i]-p.anchor[i] for i in range(3)],size,yaw)
def bar(p,m,c,d,t): p.bar(m,[c[i]-p.anchor[i] for i in range(3)],[d[i]-p.anchor[i] for i in range(3)],t)
def mound(p,m,c,size,n=8):
    # Faceted eight-sided rounded loft, entirely contained in its source box.
    sx,sy,sz=size;cx,cy,cz=c
    rings=[]
    for scale,y in [(0.72,0),(1,.18),(.93,.53),(.62,.86),(.18,1)]:
        rings.append([[cx+sx/2*scale*math.cos(math.tau*i/n)-p.anchor[0],cy+sy*y-p.anchor[1],cz+sz/2*scale*math.sin(math.tau*i/n)-p.anchor[2]] for i in range(n)])
    p.loft(m,rings)
def lantern(p,c,size):
    x,y,z=c;w,h,d=size
    box(p,'Glow',[x,y+h*.45,z],[w*.61,h*.62,d*.61])
    for dx in [-1,1]:
        for dz in [-1,1]:box(p,'Brass',[x+dx*w*.42,y+h*.47,z+dz*d*.42],[w*.12,h*.85,d*.12])
    box(p,'Brass',[x,y+h*.07,z],[w,h*.14,d]);mound(p,'Brass',[x,y+h*.85,z],[w,h*.15,d])
    mound(p,'Snow',[x,y+h*.94,z],[w*.85,h*.06,d*.85])

# Rev2 organic, rounded, tapered geometry in the existing material-group pipeline.
def tube(p,m,aa,bb,r0,r1=None,flatten=1,n=5):
    a0=np.array(aa,float);b0=np.array(bb,float);d=b0-a0;d/=np.linalg.norm(d)
    u=np.cross(d,[0,0,1] if abs(d[2])<.9 else [1,0,0]);u/=np.linalg.norm(u);v=np.cross(d,u)
    rings=[]
    for c,r in [(a0,r0),(b0,r0 if r1 is None else r1)]:
        rings.append([(c+r*(u*math.cos(math.tau*i/n)+v*math.sin(math.tau*i/n)*flatten)-p.anchor).tolist() for i in range(n)])
    p.loft(m,rings)
def rounded(p,m,c,size,n=16):
    # Rounded rectangular footprint (superellipse), rounded vertical shoulder.
    x,y,z=c;w,h,d=size;rings=[]
    for sc,yy in [(.86,0),(1,.2),(.97,.57),(.83,.85),(.52,.98),(.1,1)]:
        ring=[]
        for i in range(n):
            t=math.tau*i/n;cc=math.cos(t);ss=math.sin(t)
            ring.append([x+w/2*sc*math.copysign(abs(cc)**.45,cc)-p.anchor[0],y+h*yy-p.anchor[1],z+d/2*sc*math.copysign(abs(ss)**.45,ss)-p.anchor[2]])
        rings.append(ring)
    p.loft(m,rings)
def bud(p,m,c,size):
    x,y,z=c;w,h,d=size
    p.loft(m,[[[x+w/2*sc*math.cos(math.tau*i/5)-p.anchor[0],y+h*yy-p.anchor[1],z+d/2*sc*math.sin(math.tau*i/5)-p.anchor[2]] for i in range(5)] for sc,yy in [(.45,0),(1,.5),(.3,1)]])
def coral(p,c,size,col='CoralPink',seed=0):
    x,y,z=c;w,h,d=size
    trunk=min(.5,w*.22) if h<8 else 1.4
    root=[x,y,z];fork=[x+(.04*w if seed%2 else -.04*w),y+h*.34,z]
    tube(p,col,root,fork,trunk/2,trunk*.44)
    count=3+seed%3
    for k in range(count):
        u=(k/(count-1)-.5);dx=u*w*.58;dz=((k+seed)%3-1)*d*.23
        mid=[x+dx*.47,y+h*(.56+.025*(k%2)),z+dz*.45]
        end=[x+dx,y+h*(.72+.03*(1-abs(u)*2)),z+dz]
        tube(p,col,fork,mid,trunk*.39,trunk*.29,.7)
        tube(p,col,mid,end,trunk*.29,trunk*.23,.65)
        # Third split makes broad flattened fan lobes instead of straight sticks.
        for side in [-1,1]:
            tip=[end[0]+side*w*.13,end[1]+h*.16,end[2]+side*d*.035]
            tube(p,col,end,tip,trunk*.23,trunk*.28,.6)
            rr=min(w*.075,h*.035)
            bud(p,col,[tip[0],tip[1]-rr*.6,tip[2]],[rr*2,rr*1.8,rr*1.15])
            bud(p,'CoralMint',[tip[0],tip[1]+rr*.55,tip[2]],[rr*1.2,rr*.55,rr*.7])
