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
 x,y,z=c
 p.loft('Ink',[[[x+sc*.5*r*math.cos(i*math.tau/12)-p.anchor[0],y+sc*1.25*yy-p.anchor[1],z+sc*.4*r*math.sin(i*math.tau/12)-p.anchor[2]] for i in range(12)] for yy,r in [(0,.35),(.25,1),(.72,.9),(1,.1)]])
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
 for k in range(11):
  theta=phase+k*math.tau/11;direction=np.array([math.cos(theta),0,math.sin(theta)])
  rings=[]
  # broad pointed curved fronds, with a narrow snow ridge on each
  for t,w in [(0,.05),(.35,.48),(.7,.34),(1,.015)]:
   c=np.array(crown)+direction*(2.0*t)+[0,.25*math.sin(t*math.pi)-.9*t*t,0];side=np.array([-direction[2],0,direction[0]])*w
   rings.append([(c-side-p.anchor).tolist(),(c+side-p.anchor).tolist(),(c+side+[0,.055,0]-p.anchor).tolist(),(c-side+[0,.055,0]-p.anchor).tolist()])
  p.loft('AuroraTeal',rings)
  aa=np.array(crown)+direction*.3+[0,.12,0];bb=np.array(crown)+direction*1.7+[0,-.5,0];tube(p,'Snow',aa,bb,.06,.025,n=4)
 for vs,fs in p.g.values():
  for v in vs:v[1]=max(v[1],y-p.anchor[1])
for j in range(2):
 p=make(4,'frosted_palm_'+('a' if j==0 else 'b'),'frosted_palms');palm(p,[-8.12,0,-23.1+j*2.2],1.25,11.5-j*.6,j*.6)
 override(p,[-8,6,-22],[7.5,12.5,7.5],'Crown/segmented trunk override: source occluder describes only one straight trunk; two curved crowns required by brief.')
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
box(p,'Lagoon',[x,y+.025,z],[5.65,.05,24.15])
# Ten chunky boulders on the east pool rim, inset horizontally from the rail.
for j in range(10):mound(p,'Basalt' if j%2 else 'Rock',[13.75,y,-47+j*2.4],[1.1,.9,2.5],6)
for zz in [-44,-36,-28]:
 rings=[]
 for j in range(7):
  t=j/6;cc=np.array([12.7+.35*math.sin(t*math.tau),y+.2+t*1.5,zz+.25*math.cos(t*math.tau)])
  rings.append([(cc+[-.3*(1-t*.5),0,0]-p.anchor).tolist(),(cc+[.3*(1-t*.5),0,0]-p.anchor).tolist()])
 p.loft('Steam',rings,False,False)
override(p,[11.5,y+1.3,-36.25],[6,2.6,24.5],'Chunky boulder rim stays .20 inside east rail without touching it, rising .85 above water; steam curls above pool; west/north/south rim conflicts with shelf felt so chunky rim concentrated east.')
p=make(6,'frosted_palms')
for j in range(3):palm(p,[16.65,0,-37.3+j*2.3],-1.25,11.5-j*.3,j*.4)
override(p,[16.5,6,-35],[7.5,12.5,9],'Three curved trunks and crowns override the single straight-trunk occluder.')
p=make(6,'respawn_stone','pool_respawn_stone',felt_skins=['shelf_e']);x,y,z=p.anchor
# Match tilted felt exactly, including the small 0.00005 source rounding discrepancy.
f=next(f for f in H[6]['felt'] if f['id']=='shelf_e')
box(p,'Lime',[x,y-.012,z],[.8,.02,.8])
for vs,fs in p.g.values():
 for v in vs:v[1]+=(v[0]+x-f['center'][0])*f['slope']['rise']/f['size'][0]+f['center'][1]-y-.001
override(p,[x,y-.01,z],[.8,.06,.8],'Flush sloped stone follows exact shelf_e top, extending below anchor by .029 studs; thickness is below felt.')
p=make(14,'bell_gantry')
for xx in [-5.45,5.45]:
 box(p,'Timber',[xx,5.175,-24],[.8,10.35,.8])
 mound(p,'Snow',[xx,10.35,-24],[1, .45,1],8)
 tube(p,'Timber',[xx,8.5,-24],[xx*.65,10.6,-24],.2,n=4)
 for yy in [2,8.8,10]:tube(p,'Brass',[xx,yy,-24.42],[xx,yy,-24.52],.10,n=6)
box(p,'Timber',[0,10.85,-24],[11.7,1,1])
for xx in [-4.4,-2.2,0,2.2,4.4]:mound(p,'Snow',[xx,11.35,-24],[2.7,.4,1.2],6)
for aa,bb in [([-5.45,8.5,-25.5],[5.45,10.7,-25.5]),([5.45,8.5,-25.5],[-5.45,10.7,-25.5])]:tube(p,'Timber',aa,bb,.12,n=4)
for xx in [-4.5,-3.7,-3,3,3.7,4.5]:crystal(p,[xx,8.65,-24.37],[.24,1.7,.24])
override(p,[0,5.9,-24],[12,11.8,4],'Approved legs moved to x +/-5.45, .8 square; 1x1 beam, knees and X braces entirely above y8.3, lumpy snow caps, beam-only icicles above y8.65. Existing pivot unchanged.')
p=make(14,'icicle_bell',pivot=H[14]['moving_parts'][0]['pivot']);p.motion=H[14]['moving_parts'][0]
# The nine exact skid strips remain unchanged; collider cube is an envelope, not a boxy visible shell.
for b in p.motion['blockers'][1:]:box(p,'Brass',(p.anchor+np.array(b['center'])).tolist(),b['size'],b.get('yaw',0))
# Hollow lathed flared bell: outside then return up inside the mouth, no filled mouth cap.
profile=[(.50,.97),(.62,.99),(.85,.88),(1.3,.66),(1.9,.52),(2.2,.55),(2.35,.45),(2.65,.18),(2.70,.06),(2.57,.08),(2.25,.36),(1.9,.43),(1.3,.57),(.85,.79),(.62,.88),(.50,.86)]
rings=[[[r*math.cos(i*math.tau/20),yy-p.anchor[1],r*math.sin(i*math.tau/20)] for i in range(20)] for yy,r in profile]
p.loft('Brass',rings,False,False)
tube(p,'Brass',[0,2.65,-24],[0,10.1,-24],.10,n=8)
tube(p,'Brass',[-.38,9.8,-24],[.38,9.8,-24],.13,n=8)
tube(p,'Brass',[0,1.9,-24],[0,.78,-24],.06,n=8)
mound(p,'Brass',[0,.55,-24],[.4,.38,.4],10)
for j in range(10):
 t=j*math.tau/10;crystal(p,[.52*math.cos(t),2.35,-24+.52*math.sin(t)],[.14,.42,.14])
# Upper crown lip can widen only above the collider cube top.
p.loft('Brass',[[[r*math.cos(i*math.tau/20),yy-p.anchor[1],r*math.sin(i*math.tau/20)] for i in range(20)] for yy,r in [(2.36,.6),(2.42,.82),(2.50,.6)]])
override(p,[0,5.2,-24],[2.75,10.3,2.75],'Hollow 20-sided flared brass bell inside yaw30 cube envelope below y2.35; clapper visible in open mouth. Nine exact skid strips unchanged; crown ice above y2.35. Hanger/yoke ends .15 below beam.')
p=make(14,'buoy_float');x,y,z=p.anchor
for dx in [-.65,.65]:
 rings=[]
 for yy,rr in [(0,.42),(.3,.5),(.65,.42),(1,.32),(1.4,.08)]:rings.append([[x+dx+rr*math.cos(i*math.tau/10)-x,yy,z+rr*math.sin(i*math.tau/10)-z] for i in range(10)])
 for j in range(4):p.loft(['AuroraMint','AuroraViolet','Snow','Brass'][j],rings[j:j+2])
 mound(p,'Snow',[x+dx,y,z],[1.1,.14,1.1],6)
 for side in [-1,1]:tube(p,'Brass',[x+dx+side*.16,y+1.1,z],[x+dx+side*.12,y+1.65,z],.025,n=4)
 mound(p,'Glow',[x+dx,y+1.5,z],[.16,.16,.16],6)
 mound(p,'Brass',[x+dx,y+1.67,z],[.3,.08,.3],6)
 for k in range(8):
  t=k*math.tau/8;u=(k+1)*math.tau/8;tube(p,'Snow',[x+.4*math.cos(t),y+.08,z+.9+.4*math.sin(t)],[x+.4*math.cos(u),y+.08,z+.9+.4*math.sin(u)],.045,n=4)
p=make(14,'safe_side_sign');x,y,z=p.anchor
box(p,'Timber',[x,y+1.35,z],[.2,2.7,.2]);box(p,'AuroraTeal',[x,y+2.45,z],[.65,.7,.2]);lantern(p,[x,y+2.8,z],[.22,.35,.22])
override(p,[x,y+1.6,z],[.65,3.2,.25],'Sign board extends beyond post-only occluder, within approx envelope and rail clearance.')
p=make(18,'halo_arch');x,y,z=p.anchor
# Continuous faceted arch: vertical feet joined into an elliptical crown.
path=[[-23,.5,-52],[-23,18.6,-52]]+[[23*math.cos(math.pi-i*math.pi/24),18.6+14.9*math.sin(math.pi-i*math.pi/24),-52] for i in range(1,24)]+[[23,18.6,-52],[23,.5,-52]]
for aa,bb in zip(path,path[1:]):tube(p,'Ice',aa,bb,1.2,n=10);tube(p,'IceCore',aa,bb,.25,n=6)
override(p,[0,17.5,-52],[49,35,4],'Source feet x +/-23 with thickness conflict with nominal 46 width; 48-wide outer envelope follows feet occluders. Core crown follows supplied upper occluder; source y0.5 overrides older y0.8 notes.')
for name,c in [('crystal_bank_ne_deco',[6.5,0,-26.7]),('crystal_bank_sw_deco',[-19.2,0,-19.6])]:
 p=make(18,name)
 for j in range(10):
  cc=[c[0],0,c[2]+(j-4.5)*.48];rad=.52+.07*(j%3);height=3.3+.32*(j%5)
  for mat,r,h in [('Ice',rad,height),('IceCore',rad*.3,height*.88)]:
   rings=[]
   for yy,sc in [(0,.85),(.15,1),(.8,.9),(1,.02)]:
    rings.append([[cc[0]+r*sc*math.cos(i*math.tau/6)+yy*.2-p.anchor[0],yy*h-p.anchor[1],cc[2]+r*sc*math.sin(i*math.tau/6)-yy*.15-p.anchor[2]] for i in range(6)])
   p.loft(mat,rings)
 override(p,[c[0],2.5,c[2]],[5.5,5.1,5.5],'Ten overlapping fat leaning hex crystals, .52-.66 radius, 3.3-4.58 high, neon cores. Approved rev0 bank centres retained outside outer rails; pivot unchanged. Wall widened along outside rail.')
p=make(18,'crystal_chute',skins=[w['id'] for w in H[18]['walls']])
for w in H[18]['walls']:
 if w['id'] in p.skin_ids:
  box(p,'Ice',w['center'],w['size'],w.get('yaw',0))
  # inset neon core does not change collider faces
  sz=[v*.65 for v in w['size']];box(p,'IceCore',w['center'],sz,w.get('yaw',0))
override(p,[0,1.2,-29],[36,3.4,64],'Exact rail9/divider meet rail8/rail10 at zero-clearance structural joins. Extend ice skin asset to the complete connected H18 source rail/backing network so every joined collider is an explicitly owned exact skin; no blanket adjacent-rail exception. Full source network overrides chute-only approximate envelope; 1.6 chute opening unchanged.')
p=make(18,'ramp_lanterns');x,y,z=p.anchor
for dz in [-3.5,0,3.5]:
 # Divider x -9.5..-7.3; ramp edge -9.5, chute edge -7.3: cap inset .15 each side.
 box(p,'Brass',[-8.4,y+.25,z+dz],[1.898,.06,.95])
 # Lips on north/south faces only, terminating .15 above divider top.
 for side in [-1,1]:box(p,'Brass',[-8.4,y+.20,z+dz+side*.46],[1.898,.10,.03])
 box(p,'Timber',[x,y+2.95,z+dz],[.6,5.5,.6]);lantern(p,[x,y+5.7,z+dz],[.6,.9,.6])
override(p,[-8.4,y+3.4,z],[1.9,6.8,10],'Separate 1.9-wide foot caps inset .15 from both felt edges, plate bottom .22 above divider top; downward lips terminate .15 above divider top to respect rail gap. North/south downward lips shield gap from tee eye; 5.5-tall timber posts, Glow heads, brass caps. Pivot unchanged.')
p=make(4,'ice_channel_edge','ice_sheen')
for xx in [-4.85,4.85]:
 box(p,'Ice',[xx,.5,-23.7],[.35,.8,30.9]);box(p,'IceCore',[xx,.65,-23.7],[.12,.12,30.9])
override(p,[0,.6,-23.7],[10.1,1.2,30.9],'Ice edges .175 outside slide rails; north termination avoids green cross rail. Pivot = ice_sheen.')
p=make(4,'crystal_spire','frosted_palms',pivot=[-12,0,-18])
for j,(dx,dz,h) in enumerate([(0,0,10),(-1,.5,7),(1,.6,6.5),(.4,-.8,8)]):
 crystal(p,[-12+dx,0,-18+dz],[1.2,h,1.2]);crystal(p,[-12+dx,.1,-18+dz],[.25,h*.9,.25],'IceCore')
override(p,[-12,5,-18],[4,10,4],'NEW base-centre pivot [-12,0,-18], west of slide per concept spires; >5 studs from rail. Source frosted_palms region used only as contextual reference.')
p=make(14,'rail_bollards','bell_gantry',pivot=[0,0,0])
for xx in [-5.3,5.3]:
 for zz in [-13,-19,-29]:
  box(p,'Timber',[xx,1.25,zz],[.8,2.5,.8]);box(p,'Brass',[xx,1.8,zz],[.84,.16,.84]);mound(p,'Snow',[xx,2.5,zz],[.9,.25,.9],6)
override(p,[0,1.4,-21],[12,2.8,18],'NEW six bollards outside lane rails, >=.35 gap; documented hole-origin tee pivot [0,0,0].')
p=make(6,'tee_lantern','frosted_palms',pivot=[8.2,0,-4])
box(p,'Timber',[8.2,3.7,-4],[.9,7.4,.9]);lantern(p,[8.2,7.4,-4],[1,1.3,1])
override(p,[8.2,4.4,-4],[1.2,8.8,1.2],'NEW base-centre pivot [8.2,0,-4], east of tee; >=3 studs from tee rail, chunky 7.4 post and warm lantern.')
out=[]
for p in P:
 out.append(dict(id=p.name,hole=p.hole,source_anchor=p.source,anchor=p.anchor.tolist(),yaw_local=0,groups={m:dict(verts=v,faces=f) for m,(v,f) in p.g.items()},skin_ids=p.skin_ids,felt_skins=p.felt_skins,motion=p.motion,notes=p.notes,override_boxes=p.overrides,can_collide=False))
(S/'parts.json').write_text(json.dumps(out));(S/'skipped.json').write_text('[]')
print('Generated',len(out),'assets')
