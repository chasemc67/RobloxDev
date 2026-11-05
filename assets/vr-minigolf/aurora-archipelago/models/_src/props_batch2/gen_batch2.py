from geometry import *
import hashlib
assert hashlib.md5((D/'holes.json').read_bytes()).hexdigest()=='4ee4f942c3b0c12627d7ce81a3831d4c'
NS=[9,10,11,12,13,15,16,17]
def skip(n,name,reason): skipped.append(dict(id=f'h{n:02d}_{name}',hole=n,reason=reason))
def relative_add(p,q,offset,yaw=0,roll=0):
 for mat,(vs,fs) in q.g.items():
  out=[]
  for v in vs:
   v=roty(v,yaw);r=math.radians(roll);v=[v[0]*math.cos(r)-v[1]*math.sin(r),v[0]*math.sin(r)+v[1]*math.cos(r),v[2]]
   out.append([v[i]+offset[i]-p.anchor[i] for i in range(3)])
  p.add(mat,out,fs)
def crystal(p,c,size,mat='Ice'):
 x,y,z=c;w,h,d=size
 p.loft(mat,[[[x+math.cos(i*math.tau/6)*w/2*sc-p.anchor[0],y+h*yy-p.anchor[1],z+math.sin(i*math.tau/6)*d/2*sc-p.anchor[2]] for i in range(6)] for yy,sc in [(0,.6),(.2,1),(.75,.85),(1,0)]])
def puff(p,c,size):
 x,y,z=c;w,h,d=size;rounded(p,'Ink',c,[w,h*.68,d],8);rounded(p,'MoveCream',[x,y+h*.6,z],[w*.66,h*.4,d*.66],8);bud(p,'Beak',[x,y+h*.73,z+d*.32],[w*.25,h*.14,d*.23])
def wallskins(n,name,ids,mat):
 p=part(n,name,pivot=([0,0,-36] if n==13 else [0,0,0]),skins=ids)
 for w in H[n]['walls']:
  if w['id'] not in ids:continue
  c=w['center'];sz=w['size']
  if n==10:
   bottom=c[1]-sz[1]/2;top=c[1]+sz[1]/2
   box(p,mat,[c[0],(bottom+top-.3)/2,c[2]],[sz[0],sz[1]-.3,sz[2]],w.get('yaw',0))
   box(p,'Ice',[c[0],top-.215,c[2]],[sz[0],.17,sz[2]],w.get('yaw',0))
   box(p,'Snow',[c[0],top-.065,c[2]],[sz[0],.13,sz[2]],w.get('yaw',0))
  else:box(p,mat,c,sz,w.get('yaw',0))
  # inset faceted shoulder remains inside source collision box
  q=Part('cap',n,[0,0,0]);rounded(q,'Snow',[0,sz[1]/2-.13,0],[sz[0]*.94,.13,sz[2]*.98],8);relative_add(p,q,c,w.get('yaw',0))
 return p
# Spiral shell bodies behind their mouths. Exit conflicts with felt overhead gate and is retained for preflight rejection.
for name,n in [('conch_entry',9),('conch_exit',9)]:
 p=part(n,name);anc=a(n,name);o=anc['occluders'][0];c=o['center'];w,h,d=o['size']
 # stepped spiral loft with a hollow open lip, faceted rib seams
 rings=[]
 for zoff,rr,cy in [(-d/2,.15,c[1]),(-d*.3,w*.4,c[1]),(0,w*.5,c[1]),(d*.25,w*.4,c[1]-.4),(d/2-.12,w*.24,c[1]-h*.25)]:
  rings.append([[c[0]+rr*math.cos(i*math.tau/16)-p.anchor[0],cy+rr*math.sin(i*math.tau/16)-p.anchor[1],c[2]+zoff-p.anchor[2]] for i in range(16)])
 p.loft('CoralPink',rings,cap0=True,cap1=False)
 # luminous faceted rim around the open aperture, entirely behind the playable spit
 rr=w*.24;cy=c[1]-h*.25;zz=c[2]+d/2-.12
 for k in range(16):
  t=k*math.tau/16;u=(k+1)*math.tau/16
  tube(p,'CoralMint',[c[0]+rr*math.cos(t),cy+rr*math.sin(t),zz],[c[0]+rr*math.cos(u),cy+rr*math.sin(u),zz],.05,n=4)
 # concentric tapered spiral ridge on the rear half, not across the mouth
 for k in range(20):
  t=k/20*math.pi*4;u=(k+1)/20*math.pi*4;rr=w*.35*(1-k/24);rr2=w*.35*(1-(k+1)/24)
  tube(p,'CoralOrange',[c[0]+rr*math.cos(t),c[1]+rr*math.sin(t),c[2]-d*.15],[c[0]+rr2*math.cos(u),c[1]+rr2*math.sin(u),c[2]-d*.15],.08,n=5)
 # Exterior spiral following the side surface of the shell loft.
 profiles=[(-d/2,.15,c[1]),(-d*.3,w*.4,c[1]),(0,w*.5,c[1]),(d*.25,w*.4,c[1]-.4),(d/2-.12,w*.24,c[1]-h*.25)]
 side=[]
 for j in range(49):
  tt=j/48*math.pi*4;sc=1-j/55;zz=-d*.05+d*.27*sc*math.sin(tt);yy=c[1]+h*.27*sc*math.cos(tt)
  aa,bb=next((aa,bb) for aa,bb in zip(profiles,profiles[1:]) if aa[0]<=zz<=bb[0]);f=(zz-aa[0])/(bb[0]-aa[0]);rr=aa[1]+f*(bb[1]-aa[1]);cy=aa[2]+f*(bb[2]-aa[2]);xx=math.sqrt(max(.001,rr*rr-(yy-cy)**2))
  side.append([c[0]+min(w/2-.06,xx),yy,c[2]+zz])
 for aa,bb in zip(side,side[1:]):tube(p,'CoralOrange',aa,bb,.04,n=4)
 p.notes.append('Shell constrained to holes.json occluder; static pink/orange instead of cream. Mouth orientation follows teleport entry/exit.')
# Underwater lagoon and thick spit skirt.
p=part(9,'reef_lagoon');z=H[9]['hazards'][0];box(p,'Lagoon',z['center'],[z['size'][0],.08,z['size'][1]])
p=part(9,'coral_spit',pivot=[0,0,-28.5],felt_skins=['spit']);box(p,'Rock',[0,-.5,-28.5],[3,1,13]);box(p,'IceCore',[0,-.03,-28.5],[2.8,.04,12.8])
wallskins(9,'reef_wall_skins',[w['id'] for w in H[9]['walls']],'CoralPink')
# Bobsled cabin: gable roof, timber frame, bell and parked sled within source envelope.
p=part(10,'bobsled_hut');x,y,z=p.anchor
box(p,'Canvas',[x,2.1,z],[3.75,4.2,4]);q=Part('roof',10,[0,0,0]);q.prism_zy([ ][0] if False else 'Timber',[(-1.85,4.2),(0,7),(1.85,4.2)],-2,2)
# prism_zy gable along depth; rotate to sheet front
relative_add(p,q,[x,0,z],90)
for dx in [-1.7,1.7]:tube(p,'Timber',[x+dx,0,z+2.01],[x+dx,4.2,z+2.01],.13)
box(p,'Timber',[x,1.3,z+2.025],[1.1,2.6,.05]);box(p,'Glow',[x+1.2,2.6,z+2.03],[.7,.8,.04]);lantern(p,[x,4.1,z+1.8],[.45,.6,.45])
for dx in [-.65,.65]:tube(p,'Brass',[x+dx,.12,z+1.5],[x+dx,.12,z+2.35],.07)
box(p,'HullTeal',[x,.4,z+1.95],[1.5,.18,.8]);p.notes.append('Violet canvas and timber replace prohibited static red/cream.')
wallskins(10,'snow_wall_skins',[w['id'] for w in H[10]['walls']],'SnowShadow')
# H10 plate coverage outside visible run is source-defined masking, kept for source conflict review.
p=part(10,'snow_walls')
for o in a(10,'snow_walls')['occluders']:rounded(p,'Snow',[o['center'][0],0,o['center'][2]],o['size'])
# Fishing tent, stove chimney, inset snow roof.
p=part(11,'fishing_hut');x,y,z=p.anchor
q=Part('tent',11,[0,0,0]);q.prism_zy('Canvas',[(-1.5,0),(0,4),(1.5,0)],-1.5,1.5);relative_add(p,q,[x,0,z],90)
# constrain tent depth to rear of pocket wall inside source envelope
for mat,(vs,fs) in p.g.items():
 for v in vs:v[2]*=.5
box(p,'Timber',[x,1.1,z+.73],[.6,2.2,.04]);tube(p,'Brass',[x+.7,2.6,z],[x+.7,6,z],.1);rounded(p,'Snow',[x,3.8,z],[.55,.2,1.4])
wallskins(11,'snowbank_skins',[w['id'] for w in H[11]['walls']],'SnowShadow')
p=part(11,'floe_frame')
for o in a(11,'floe_frame')['occluders']:
 x,y,z=o['center'];tube(p,'Timber',[x,0,z],[x,2.8,z],.23);rounded(p,'Snow',[x,2.8,z],[.5,.2,.5])
# exact slide blockers; cosmetic cap and tiny rider all within narrow slot
m=H[11]['moving_parts'][0];p=part(11,'ice_floe',pivot=m['pivot']);p.motion=m
for b in m['blockers']:box(p,'Ice',[m['pivot'][i]+b['center'][i] for i in range(3)],b['size'],b.get('yaw',0))
rounded(p,'Snow',[0,1,-28],[5.6,.1,.5],12);puff(p,[1.2,1,-28],[.18,.12,.18])
# Hull halves contain slot. Bottom follows exact hull colliders; cabins taper and remain inside source occluders.
p=part(12,'icebreaker')
p.notes.append('Hull solid upper dressing starts y1.11, .11 above gameplay hull faces, preserving wheel slot. Lower source hull skins separately unresolved at adjoining rail seam.')
skip(12,'hull_face_skins','Exact rail2/hull13 connections share endpoints with approach rail1; lower source skins have zero adjoining rail clearance. Upper icebreaker retained above y1.11.')
for o in a(12,'icebreaker')['occluders']:
 x,y,z=o['center'];w,h,d=o['size'];box(p,'HullTeal',[x,2.055,z],[w,1.89,d-.24]);box(p,'Canvas',[x,4,z],[w*.65,2,d*.7]);rounded(p,'Snow',[x,5,z],[w*.67,.4,d*.72]);box(p,'Glow',[x,4,z+d*.36],[w*.35,.7,.03])
x=4.6;box(p,'Brass',[x,6.7,-21],[1.2,2.6,1.2]);rounded(p,'Snow',[x,7.8,-21],[1.4,.2,1.4])
m=H[12]['moving_parts'][0];p=part(12,'paddle_wheel',pivot=m['pivot']);p.motion=m
for j,b in enumerate(m['blockers']):
 q=Part('paddle',12,[0,0,0]);q.box('MoveRed' if (j//6)%2==0 else 'MoveCream',b['center'],b['size']);relative_add(p,q,p.anchor,roll=b.get('roll',0))
# two segmented rim rings <=3.9 and spokes in depth .4
for i in range(64):
 t=math.tau*i/64;u=math.tau*(i+1)/64
 tube(p,'Brass',[3.8*math.cos(t),4.16+3.8*math.sin(t),-17.75],[3.8*math.cos(u),4.16+3.8*math.sin(u),-17.75],.08,n=4)
for i in range(8):
 t=math.tau*i/8;tube(p,'Brass',[0,4.16,-17.75],[3.7*math.cos(t),4.16+3.7*math.sin(t),-17.75],.09,n=4)
# Hub exact 48-strip footprint, then centre pole and 16-sided canopy underside 9.
ids=[w['id'] for w in H[13]['walls'] if w['id'].startswith('hub_plinth')]
p=wallskins(13,'hub_base',ids,'Brass')
p=part(13,'carousel_canopy',skins=ids);tube(p,'Brass',[0,1.2,-36],[0,9,-36],.4)
rings=[]
for yy,rr in [(9,8),(10.6,5.8),(11.3,.3)]:rings.append([[rr*math.cos(i*math.tau/16),yy,-36+rr*math.sin(i*math.tau/16)] for i in range(16)])
# alternate mint/violet canopy panels
for i in range(16):
 vs=[rings[j][k%16] for j,k in [(0,i),(0,i+1),(1,i+1),(1,i),(2,i+1),(2,i)]];p.add('AuroraMint' if i%2 else 'AuroraViolet',vs,[[0,1,2,3],[3,2,4,5]])
tube(p,'Brass',[0,11.2,-36],[0,12,-36],.06);rounded(p,'Snow',[0,11.55,-36],[.6,.4,.45],8)
m=H[13]['moving_parts'][0];p=part(13,'carousel_arms',pivot=m['pivot']);p.motion=m
for i,b in enumerate(m['blockers']):
 box(p,'MoveRed', [m['pivot'][j]+b['center'][j] for j in range(3)],b['size'],b['yaw'])
 q=Part('rider',13,[0,0,0]);q.box('MoveCream',[9.85,1.05,0],[2.8,.3,2.6]);puff(q,[9.85,1.2,0],[1.25,1.6,1.2]);relative_add(p,q,p.anchor,b['yaw']-180)
 q=Part('spoke',13,[0,0,0]);q.box('Brass',[4.2,1.55,0],[8.4,.25,.3]);relative_add(p,q,p.anchor,b['yaw']-180)
# H15 source curtain intersects reachable basin overhead: generate exact source then let gate show contradiction.
p=part(15,'lip_ice');x,y,z=p.anchor
poly=[[-3.5,0],[3.5,0],[3.5,-3.2]]
for i in range(14,-1,-1):poly.append([-3.5+i*.5,-4 if i%2 else -3.2])
# polygon x/y extruded along z
vs=[[xx,yy,zz] for zz in [-20.5,-19.5] for xx,yy in poly];cnt=len(poly);p.add('Ice',[[v[i]-p.anchor[i] for i in range(3)] for v in vs],[list(range(cnt-1,-1,-1)),list(range(cnt,2*cnt))]+[[i,(i+1)%cnt,(i+1)%cnt+cnt,i+cnt] for i in range(cnt)])
skip(15,'great_frozen_falls','Anchor explicitly a view cue for a world mesh; world/world.json absent. 26x40x8 envelope at hole cue overlaps basin/rails; no authoritative cascade world position or base defined. Cannot invent world placement.')
skip(15,'ice_parapet','props.md gives 8x3.5 but holes.json contains no parapet anchor or exact geometry.')
skip(15,'steps','props.md x -6..-9.5 does not define tread count/rise/landing; holes.json has no steps geometry.')
# Moonstone exact coping collider skins and crystal clusters in two source occluders.
wallskins(16,'moonstone_coping',[w['id'] for w in H[16]['walls']],'Moonstone')
p=part(16,'moonwell')
for o in a(16,'moonwell')['occluders']:
 x,y,z=o['center'];w,h,d=o['size'];rounded(p,'Moonstone',[x,0,z],[w-.2,h,d]);crystal(p,[x,.3,z-d*.35],[w*.6,1.7,w*.6]);crystal(p,[x,.3,z+d*.35],[w*.5,1.2,w*.5])
skip(16,'crescent_spout','Sheet calls spout z -30, inside reachable well/green felt; no source crescent solid geometry. A raised static crescent violates 8-stud head volume; retain gameplay spout collider and flush glow cue.')
# Piers: source decks with skirt to -.6, rail skins, inverted crystal prisms under ends.
p=part(17,'crystal_piers',skins=[f'pier_{s}_rail{i}' for s,inds in [('s',[6,7]),('n',[8,9])] for i in inds],felt_skins=['pier_s','pier_n'])
for zz in [-20.5,-37.5]:
 box(p,'Ice',[0,-.3,zz],[3,.6,9]);crystal(p,[0,-3,zz],[2.7,2.4,2.5]);box(p,'IceCore',[0,-.04,zz],[2.6,.05,8.8])
for w in H[17]['walls']:
 if w['id'] in p.skin_ids:box(p,'Ice',w['center'],w['size'],w['yaw'])
p=part(17,'ice_bridge',skins=['bridge_rail10','bridge_rail11'],felt_skins=['ice_bridge']);box(p,'Ice',[6,-.3,-29],[4,.6,26]);box(p,'IceCore',[6,-.04,-29],[3.8,.05,25.8])
for w in H[17]['walls']:
 if w['id'] in p.skin_ids:box(p,'Timber',w['center'],w['size'],w['yaw'])
p=part(17,'span_lamp');tube(p,'Brass',p.anchor,[-2.4,1.5,-15],.12);crystal(p,[-2.4,1.4,-15],[.6,1,.6],'AuroraMint')
p=part(17,'aurora_ribbon');rings=[]
for j in range(11):
 yy=10+5*j;xx=.25*math.sin(j*.7);ww=1.1+.35*math.sin(j*.45)
 rings.append([[xx-ww,yy,-33],[xx+ww,yy,-33],[xx+ww,yy,-25],[xx-ww,yy,-25]])
for j in range(10):p.add('AuroraMint' if j<5 else 'AuroraViolet',[[v[k]-p.anchor[k] for k in range(3)] for ring in rings[j:j+2] for v in ring],[[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]])
m=H[17]['moving_parts'][0];p=part(17,'aurora_span',pivot=m['pivot']);p.motion=m;box(p,'AuroraMint',[0,-.2,-29],[3,.4,8])
# Flush teleport and moon cues are geometry below the felt, no head-volume exemption above it.
for n,name,sz,mat in [(9,'conch_ring',[.6,.01,.6],'Lime'),(16,'spout_glow',[2,.01,2],'AuroraMint'),(17,'span_respawn_stone',[.8,.02,.8],'Lime')]:
 anc=[0,0,-33] if n==9 else a(n,name)['position'];p=part(n,name,pivot=anc,felt_skins=[f['id'] for f in H[n]['felt']])
 if name=='span_respawn_stone':box(p,mat,[anc[0],anc[1]-sz[1]/2,anc[2]],sz)
 elif name=='conch_ring':
  for j in range(32):
   t=j*math.tau/32;u=(j+1)*math.tau/32
   vs=[[rr*math.cos(tt),yy,rr*math.sin(tt)] for yy in [-.01,0] for rr,tt in [(.22,t),(.3,t),(.3,u),(.22,u)]]
   p.add(mat,vs,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]])
 else:
  # A pointed crescent flush below the source trough, not a rectangular decal.
  poly=[]
  for j in range(33):
   tt=math.pi*.5+j*math.pi/32;poly.append([math.cos(tt),math.sin(tt)])
  for j in range(33):
   tt=math.pi*1.5-j*math.pi/32;poly.append([.25+.8*math.cos(tt),math.sin(tt)])
  p.prism_xz(mat,poly,-.01,0)

out=[]
for p in P:out.append(dict(id=p.name,hole=p.hole,anchor=list(p.anchor),yaw_local=0,groups={m:dict(verts=v,faces=f) for m,(v,f) in p.g.items()},skin_ids=p.skin_ids,felt_skins=p.felt_skins,motion=p.motion,notes=p.notes))
(S/'parts.json').write_text(json.dumps(out));(S/'skipped.json').write_text(json.dumps(skipped,indent=2));(S/'palette.json').write_text(json.dumps(PAL,indent=2))
print('Generated',len(out),'pieces')
