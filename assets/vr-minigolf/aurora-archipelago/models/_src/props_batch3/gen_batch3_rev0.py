"""Plain Python only; hole-local Y-up geometry, pivot-relative material groups."""
from geometry import *
import hashlib
assert hashlib.md5((D/'holes.json').read_bytes()).hexdigest()=='fb913741b5dd4812b6d2318e258bcc46'
NS=[4,6,14,18]
def make(n,name,source=None,**kw):
 p=part(n,name,pivot=kw.pop('pivot',a(n,source or name)['position']),**kw);p.source=source or name;p.overrides=[];return p
def override(p,c,size,reason):
 p.overrides.append(dict(center=c,size=size,reason=reason));p.notes.append(reason)
def crystal(p,c,size,mat='Ice',n=6):
 x,y,z=c;w,h,d=size
 p.loft(mat,[[[x+w*sc/2*math.cos(i*math.tau/n)-p.anchor[0],y+h*yy-p.anchor[1],z+d*sc/2*math.sin(i*math.tau/n)-p.anchor[2]] for i in range(n)] for yy,sc in [(0,.7),(.2,1),(.75,.8),(1,.02)]])
def puff(p,c,sc=.8,bell=False):
 x,y,z=c;rounded(p,'Ink',c,[sc,sc*1.25,sc*.8],8)
 rounded(p,'Snow',[x,y+sc*.25,z+sc*.25],[sc*.65,sc*.75,sc*.35],8)
 bud(p,'Beak',[x,y+sc*.85,z+sc*.38],[sc*.3,sc*.18,sc*.3])
 rounded(p,'AuroraTeal',[x,y+sc*.75,z],[sc*1.02,sc*.16,sc*.85],8)
 box(p,'AuroraViolet',[x+sc*.22,y+sc*.55,z+sc*.39],[sc*.16,sc*.45,.08])
 for dx in [-.19,.19]:rounded(p,'Ink',[x+dx*sc,y+sc*.97,z+sc*.35],[.065,.075,.05],6)
 for dx in [-.55,.55]:tube(p,'Ink',[x+dx*sc*.6,y+sc*.55,z],[x+dx*sc,y+sc*.35,z+.05],sc*.1,n=5)
 if bell:crystal(p,[x+sc*.55,y+sc*.25,z+.15],[.25,.25,.25],'Brass');tube(p,'Brass',[x+sc*.55,y+sc*.45,z+.15],[x+sc*.55,y+sc*.65,z+.15],.03)
def palm(p,root,lean,height=11.5,phase=0):
 x,y,z=root;pts=[]
 for j in range(9):
  t=j/8;pts.append([x+lean*t*t,y+height*t,z+.14*math.sin(t*math.pi)])
 for j,(aa,bb) in enumerate(zip(pts,pts[1:])):
  tube(p,'Timber',aa,bb,.22-j*.011,.21-j*.011,n=6)
  tube(p,'SnowShadow',bb,[bb[0],bb[1]+.055,bb[2]],.22-j*.011,n=6)
 crown=pts[-1]
 for k in range(7):
  theta=phase+k*math.tau/7;direction=np.array([math.cos(theta),0,math.sin(theta)])
  rings=[]
  # broad pointed curved fronds, with a narrow snow ridge on each
  for t,w in [(0,.05),(.35,.38),(.7,.27),(1,.015)]:
   c=np.array(crown)+direction*(1.45*t)+[0,.25*math.sin(t*math.pi)-.9*t*t,0];side=np.array([-direction[2],0,direction[0]])*w
   rings.append([(c-side-p.anchor).tolist(),(c+side-p.anchor).tolist(),(c+side+[0,.055,0]-p.anchor).tolist(),(c-side+[0,.055,0]-p.anchor).tolist()])
  p.loft('AuroraTeal',rings)
  aa=np.array(crown)+direction*.3+[0,.12,0];bb=np.array(crown)+direction*1.2+[0,-.5,0];tube(p,'Snow',aa,bb,.06,.025,n=4)
 for vs,fs in p.g.values():
  for v in vs:v[1]=max(v[1],y-p.anchor[1])
for j in range(2):
 p=make(4,'frosted_palm_'+('a' if j==0 else 'b'),'frosted_palms');palm(p,[-8.12,0,-23.1+j*2.2],1.25,11.5-j*.6,j*.6)
 override(p,[-8,6,-22],[6,12,6],'Crown/segmented trunk override: source occluder describes only one straight trunk; two curved crowns required by brief.')
p=make(4,'steam_vents')
for dz in [-2,0,2]:
 rounded(p,'Basalt',[9,0,-20+dz],[.85,.45,1],8);rounded(p,'Ink',[9,.4,-20+dz],[.35,.08,.4],6)
 for j in range(3):rounded(p,'Steam',[9+.12*math.sin(j),.52+j*.25,-20+dz],[.4+j*.1,.25,.4],6)
for n in [4,6,14,18]:
 p=make(n,'snowpuffs');x,y,z=p.anchor
 if n==6:
  rounded(p,'Basalt',[x,y,z],[2.3,.3,1.8],8);rounded(p,'Lagoon',[x,y+.24,z],[2,.08,1.5],8)
 else:rounded(p,'Snow',[x,y,z],[2.4,.25,1.8],8)
 for j in range(3 if n in [4,18] else 2):
  dx=(j-1)*.68 if n in [4,18] else (j-.5)*.95
  puff(p,[x+dx,y+.25,z],.58 if n==4 else .72,n==14)
 if n==6:
  for dx in [-.7,.7]:rounded(p,'Steam',[x+dx,y+1.3,z-.5],[.35,.4,.3],6)
 if n==18:
  for j in range(3):box(p,'SnowShadow',[x+j*1.1-1.1,y+.3+j*.28,z-.9],[1,.6+j*.56,.8])
  for dx in [-.7,.7]:box(p,'Snow',[x+dx,y+1.9,z+.15],[.48,.35,.05])
p=make(6,'kettle_pool');x,y,z=p.anchor
box(p,'Lagoon',[x,y+.025,z],[5.65,.05,24.15]);box(p,'Basalt',[14.1,y+.12,z],[.35,.24,24])
for zz in [-44,-36,-28]:
 for j in range(3):rounded(p,'Steam',[13.3+.1*j,y+.25+j*.2,zz],[.5,.25,.5],6)
p=make(6,'frosted_palms')
for j in range(3):palm(p,[16.65,0,-37.3+j*2.3],-1.25,11.5-j*.3,j*.4)
override(p,[16.5,6,-35],[6,12,8],'Three curved trunks and crowns override the single straight-trunk occluder.')
p=make(6,'respawn_stone','pool_respawn_stone',felt_skins=['shelf_e']);x,y,z=p.anchor
# Match tilted felt exactly, including the small 0.00005 source rounding discrepancy.
f=next(f for f in H[6]['felt'] if f['id']=='shelf_e')
box(p,'Lime',[x,y-.012,z],[.8,.02,.8])
for vs,fs in p.g.values():
 for v in vs:v[1]+=(v[0]+x-f['center'][0])*f['slope']['rise']/f['size'][0]+f['center'][1]-y-.001
override(p,[x,y-.01,z],[.8,.06,.8],'Flush sloped stone follows exact shelf_e top, extending below anchor by .029 studs; thickness is below felt.')
p=make(14,'bell_gantry')
for xx in [-5.05,5.05]:
 box(p,'Timber',[xx,5.175,-24],[.65,10.35,.65]);box(p,'Brass',[xx,9.9,-24],[.7,.18,.7])
box(p,'Timber',[0,10.85,-24],[10,1,1]);box(p,'Snow',[0,11.27,-24],[9.9,.16,.95])
for xx in [-4.5,-3.5,3.5,4.5]:crystal(p,[xx,8.65,-24.37],[.18,1.7,.18])
override(p,[0,10,-24],[10,2.7,1],'Beam-only icicles extend down to y8.65, above felt headroom; source beam occluder extended for required icicles.')
override(p,[0,5.675,-24],[10.9,11.35,1.5],'Source leg occluders reach x +/-5.45 beyond approximate 10.2 envelope; source leg positions take priority.')
p=make(14,'icicle_bell',pivot=H[14]['moving_parts'][0]['pivot']);p.motion=H[14]['moving_parts'][0]
for b in p.motion['blockers']:box(p,'Brass',(p.anchor+np.array(b['center'])).tolist(),b['size'],b.get('yaw',0))
tube(p,'Brass',[0,2.35,-24],[0,10.15,-24],.085,n=8)
rounded(p,'Brass',[0,2.35,-24],[2.1,.38,2.1],12)
for j in range(8):
 t=j*math.tau/8;crystal(p,[.9*math.cos(t),2.35,-24+.9*math.sin(t)],[.13,.32,.13])
override(p,[0,5.2,-24],[2.75,10.3,2.75],'Mover envelope includes yaw30 cube, exact nine collider skid strips and 9-stud hanger. Source skid is the explicit contact-shape exemption to generic .15 felt gap; hinge ends .20 below beam.')
p=make(14,'buoy_float');x,y,z=p.anchor
for dx in [-.65,.65]:
 rings=[]
 for yy,rr in [(0,.42),(.3,.5),(.65,.42),(1,.32),(1.4,.08)]:rings.append([[x+dx+rr*math.cos(i*math.tau/10)-x,yy,z+rr*math.sin(i*math.tau/10)-z] for i in range(10)])
 for j in range(4):p.loft(['AuroraMint','AuroraViolet','Snow','Brass'][j],rings[j:j+2])
 for k in range(16):
  t=k*math.tau/16;u=(k+1)*math.tau/16;tube(p,'Snow',[x+.4*math.cos(t),y+.08,z+.9+.4*math.sin(t)],[x+.4*math.cos(u),y+.08,z+.9+.4*math.sin(u)],.045,n=4)
p=make(14,'safe_side_sign');x,y,z=p.anchor
box(p,'Timber',[x,y+1.35,z],[.2,2.7,.2]);box(p,'AuroraTeal',[x,y+2.45,z],[.65,.7,.2]);lantern(p,[x,y+2.8,z],[.22,.35,.22])
override(p,[x,y+1.6,z],[.65,3.2,.25],'Sign board extends beyond post-only occluder, within approx envelope and rail clearance.')
p=make(18,'halo_arch');x,y,z=p.anchor
# Continuous faceted arch: vertical feet joined into an elliptical crown.
path=[[-23,.5,-52],[-23,18.6,-52]]+[[23*math.cos(math.pi-i*math.pi/24),18.6+14.9*math.sin(math.pi-i*math.pi/24),-52] for i in range(1,24)]+[[23,18.6,-52],[23,.5,-52]]
for aa,bb in zip(path,path[1:]):tube(p,'Ice',aa,bb,.95,n=6);tube(p,'IceCore',aa,bb,.19,n=5)
override(p,[0,17.5,-52],[48,34,4],'Source feet x +/-23 with thickness conflict with nominal 46 width; 48-wide outer envelope follows feet occluders. Core crown follows supplied upper occluder; source y0.5 overrides older y0.8 notes.')
for name,c in [('crystal_bank_ne_deco',[6.5,0,-26.7]),('crystal_bank_sw_deco',[-19.2,0,-19.6])]:
 p=make(18,name)
 for j in range(3):
  cc=[c[0]+(j-1)*.65,0,c[2]-(j-1)*.65];crystal(p,cc,[.55,3.2+j*.35,.55]);crystal(p,[cc[0],.2,cc[2]],[.14,2.8+j*.35,.14],'IceCore')
 override(p,[c[0],2,c[2]],[2.2,4,2.2],'Backing rails lie within plaza felt: 3-5 high clusters cannot stand directly behind them with 8-stud headroom. Clusters relocated farther behind backing, beyond outer plaza rails; source anchor pivot unchanged. Documented placement/envelope override.')
p=make(18,'crystal_chute',skins=[w['id'] for w in H[18]['walls']])
for w in H[18]['walls']:
 if w['id'] in p.skin_ids:
  box(p,'Ice',w['center'],w['size'],w.get('yaw',0))
  # inset neon core does not change collider faces
  sz=[v*.65 for v in w['size']];box(p,'IceCore',w['center'],sz,w.get('yaw',0))
override(p,[0,1.2,-29],[36,3.4,64],'Exact rail9/divider meet rail8/rail10 at zero-clearance structural joins. Extend ice skin asset to the complete connected H18 source rail/backing network so every joined collider is an explicitly owned exact skin; no blanket adjacent-rail exception. Full source network overrides chute-only approximate envelope; 1.6 chute opening unchanged.')
p=make(18,'ramp_lanterns');x,y,z=p.anchor
for dz in [-3.5,0,3.5]:
 box(p,'Brass',[x,y+.55,z+dz],[.6,.8,.6]);lantern(p,[x,y+.95,z+dz],[.6,.8,.6])
p.notes.append('Posts begin 0.15 above divider top to satisfy rail gap; mounted visually by alignment. Current source anchor supersedes old notes.')
out=[]
for p in P:
 out.append(dict(id=p.name,hole=p.hole,source_anchor=p.source,anchor=p.anchor.tolist(),yaw_local=0,groups={m:dict(verts=v,faces=f) for m,(v,f) in p.g.items()},skin_ids=p.skin_ids,felt_skins=p.felt_skins,motion=p.motion,notes=p.notes,override_boxes=p.overrides,can_collide=False))
(S/'parts.json').write_text(json.dumps(out));(S/'skipped.json').write_text('[]')
print('Generated',len(out),'assets')
