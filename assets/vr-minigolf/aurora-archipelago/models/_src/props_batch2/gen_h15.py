"""H15-only additive world cascade; reuse batch material-group lofts."""
from geometry import *
import hashlib
W=json.loads((D/'world/world.json').read_text())
assert hashlib.md5((D/'world/world.json').read_bytes()).hexdigest()=='37b98eef418e222641b6560df52da638'
w=next(w for w in W['waterfalls'] if w['name']=='Great Frozen Falls')
p=Part('h15_great_frozen_falls',15,w['bottom'])
height=w['top'][1]-w['bottom'][1];width=w['width'];depth=8
# Seven full 20-stud sections plus the six-stud lip section, joined in one
# watertight fluted curtain. Foot broadens, top narrows as on the sheet.
ys=sorted(set([0,height]+[float(y) for y in range(10,146,10)]))
rings=[]
for y in ys:
 t=y/height;hw=width/2*(1-.14*t);hz=depth/2*(1-.3*t)
 # continuous corrugated front and back; alternate bulges make ice tiers
 bulge=.45*math.sin(math.pi*y/20)**2
 front=[[(-1+2*i/24)*hw,y,-hz+(.42 if i%2 else 0)+bulge] for i in range(25)]
 back=[[(1-2*i/24)*hw,y,hz-(.35 if i%2 else 0)] for i in range(25)]
 rings.append(front+back)
p.loft('Ice',rings)
# Embedded narrow neon flutes, tapered at cloud-deck foot and terrace lip.
for j in range(11):
 x=(j-5)*2.15;rr=[]
 for y in ys:
  t=y/height;cx=x*(1-.14*t);r=.13 if 0<y<height else .025
  rr.append([[cx+r*math.cos(math.tau*k/6),y,-2.35+.17*math.sin(y/20)+r*math.sin(math.tau*k/6)] for k in range(6)])
 p.loft('IceCore',rr)
p.notes=['World waterfall top/bottom supersede 26x40x8 view-cue envelope; 26x146x8 actual bounds. Sheet taper, bulging tiers and vertical flutes retained. Tileable 20-stud cadence, final six-stud section. Foot ends at cloud deck y36; cloud obscuration supplied by world, no invented cloud mesh.']
part=dict(id=p.name,hole=15,anchor=w['bottom'],yaw_local=0,motion=None,skin_ids=[],felt_skins=[],notes=p.notes,groups={m:dict(verts=v,faces=f) for m,(v,f) in p.g.items()})
(S/'h15_part.json').write_text(json.dumps(part,indent=2))
(S/'h15_other_fbx_hashes.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (D/'models/fbx/props_batch2').glob('*.fbx') if f.stem!=p.name},indent=2))
print('Generated',p.name,'world base',w['bottom'],'height',height)
