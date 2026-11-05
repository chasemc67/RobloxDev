from pathlib import Path
import shutil
S=Path('models/_src/props_batch1')
# Existing rev1 archive is immutable. Preserve any remaining pre-revision files separately.
B=S/'_backup_before_rev2'
for folder in [S,Path('models/fbx/props_batch1'),Path('models/previews/props_batch1')]:
 for p in folder.iterdir():
  if p.is_file():
   q=B/p.relative_to(Path('models'));q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for p in [Path('models/README.md'),Path('models/props_batch1_manifest.json'),Path('models/fitcheck_props_batch1.txt')]:
 q=B/p.relative_to(Path('models'));q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
g=(S/'gen_batch1.py').read_text();g=g[:g.index('# H1 post')]
g=g[:g.index('def coral(')]+g[g.index('def lantern('):]
g+='''
# Rev2 organic, rounded, tapered geometry in the existing material-group pipeline.
def tube(p,m,aa,bb,r0,r1=None,flatten=1,n=8):
    a0=np.array(aa,float);b0=np.array(bb,float);d=b0-a0;d/=np.linalg.norm(d)
    u=np.cross(d,[0,0,1]);u/=np.linalg.norm(u);v=np.cross(d,u)
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
def coral(p,c,size,col='CoralPink',seed=0):
    x,y,z=c;w,h,d=size
    trunk=min(.5,w*.22) if h<8 else 1.4
    root=[x,y,z];fork=[x+(.04*w if seed%2 else -.04*w),y+h*.34,z]
    tube(p,col,root,fork,trunk/2,trunk*.44)
    count=3+seed%3
    for k in range(count):
        u=(k/(count-1)-.5);dx=u*w*.77;dz=((k+seed)%3-1)*d*.23
        mid=[x+dx*.47,y+h*(.56+.025*(k%2)),z+dz*.45]
        end=[x+dx,y+h*(.82+.10*(1-abs(u)*2)),z+dz]
        tube(p,col,fork,mid,trunk*.39,trunk*.29,.7)
        tube(p,col,mid,end,trunk*.29,trunk*.23,.65)
        # Third split makes broad flattened fan lobes instead of straight sticks.
        for side in [-1,1]:
            tip=[end[0]+side*w*.075,end[1]+h*.045,end[2]+side*d*.035]
            tube(p,col,end,tip,trunk*.23,trunk*.28,.6)
            rr=min(w*.12,h*.045)
            mound(p,col,[tip[0],tip[1]-rr*.6,tip[2]],[rr*2,rr*1.8,rr*1.15],n=8)
            mound(p,'CoralMint',[tip[0],tip[1]+rr*.55,tip[2]],[rr*1.2,rr*.55,rr*.7],n=8)
# H1: silhouette 0.4 post, short bracket and smaller lantern.
p=part(1,'harbour_lantern');tube(p,'Timber',[-6,0,-24],[-6,8.8,-24],.2,.17)
tube(p,'Brass',[-6,8.7,-24],[-6.65,8.7,-24],.13,.1)
lantern(p,[-6.65,7.6,-24],[.9,1.2,.9]);rounded(p,'Snow',[-6,8.8,-24],[.4,.2,.4])
p=part(1,'snow_boulder',skins=['boulder']);w=next(w for w in H[1]['walls'] if w['id']=='boulder')
box(p,'Rock',[-1.3,1.25,-35.8],[3,2.5,3],45)
mound(p,'Rock',[-1.3,2.5,-35.8],[2.8,1.6,2.8],n=12)
mound(p,'Snow',[-1.3,3.65,-35.8],[2.65,1.35,2.65],n=12)
q=roty([0,0,1.496],45);box(p,'AuroraMint',[-1.3+q[0],.8,-35.8+q[2]],[2.5,.08,.008],45)
p.notes.append('Solid flat-faced footprint felt to y2.5, rounded inset cap to y5. Collider/rail gap .0786796564 is source exception.')
# H2 open-top cuts: rounded rectangles are constrained to source occluder interiors.
p=part(2,'rookery_drift')
for o in a(2,'rookery_drift')['occluders']:
    c=o['center'];s=o['size'];xmin,xmax=(-7.39,-2.61) if c[0]<0 else (3.11,6.39)
    zmin=c[2]-s[2]/2+.11;zmax=-16.61
    rounded(p,'SnowShadow',[(xmin+xmax)/2,0,(zmin+zmax)/2],[xmax-xmin,4.5,zmax-zmin])
    rounded(p,'Snow',[(xmin+xmax)/2,2.4,(zmin+zmax)/2],[xmax-xmin,2.6,zmax-zmin])
p.notes.append('Rounded rectangular masses cut around open burrows; full 24x26 drift silhouette conflicts with reachable felt and source occluders, so envelope is represented by source walls plus inset dressing.')
for name in ['lintel_left','lintel_mid','lintel_right']:
    p=part(2,name);x,y,z=p.anchor
    # Polygonal ice arch: flat high-clearance underside, tapered crown.
    yy=8.04 if name=='lintel_mid' else 8
    poly=[[-2.5,yy],[-2.5,8.65],[-1.4,9.05],[0,9.2],[1.4,9.05],[2.5,8.65],[2.5,yy]]
    vs=[[x+dx-p.anchor[0],dy-p.anchor[1],z+dz-p.anchor[2]] for dz in [-.6,.6] for dx,dy in poly];nn=len(poly)
    p.add('Ice',vs,[list(range(nn-1,-1,-1)),list(range(nn,nn*2))]+[[i,(i+1)%nn,(i+1)%nn+nn,i+nn] for i in range(nn)])
    box(p,'IceCore',[x,8.5,z],[4.5,.15,.22]);rounded(p,'Snow',[x,9.04,z],[2.8,.15,1])
    box(p,'Canvas',[x,8.45,z+.585],[2.3,.35,.02])
    # Supports part of each lintel. Bottom above wall top; no wall contact or burrow intrusion.
    ends=([-12.8,-7.15] if name=='lintel_left' else [-2.75,2.75] if name=='lintel_mid' else [6.1,11.85])
    for px in ends:
        rounded(p,'Basalt',[px,2.51,z-.7],[.5,5.55,.55])
        tube(p,'Basalt',[px,7.8,z-.7],[x+(-2.4 if px<x else 2.4),8.18,z],.22,.17)
    p.notes.append('Basalt pillars included in lintel asset, outside clear burrow width, start y2.51 above drift/rail tops. Middle underside y8.04 preserves slope headroom.')
p=part(2,'lantern_cue');lantern(p,p.anchor,a(2,'lantern_cue')['approx_size'])
p=part(2,'lantern_crook');x,y,z=p.anchor;tube(p,'Timber',[x,0,z],[x,10.6,z],.175,.15)
pts=[[x,10.6,z],[x+.6,10.8,z],[x+1.3,10.85,z],[x+2.1,10.82,z],[x+2.9,10.75,z],[-9.75,10.6,z]]
for aa,bb in zip(pts,pts[1:]):tube(p,'Brass',aa,bb,.15)
tube(p,'Brass',[-9.75,10.6,z],[-9.75,10.2,z],.045)
for name in ['sign_left','sign_right']:
    p=part(2,name);x,y,z=p.anchor;tube(p,'Timber',[x,0,z],[x,3.2,z],.125,.1)
    rounded(p,'Brass',[x,1.8,z],[1.8,1.4,.25]);box(p,'Canvas',[x,2.45,z+.12],[1.45,.75,.015])
    # Direction arrow in mint, on the front face.
    sg=1 if name=='sign_left' else -1
    p.add('AuroraMint',[[x+sg*dx-p.anchor[0],yy,z+.13-p.anchor[2]] for dx,yy in [(-.5,2.5),(.15,2.5),(.15,2.65),(.55,2.4),(.15,2.15),(.15,2.3),(-.5,2.3)]],[list(range(7))])
# H3 inverted floating rock cone, flat snow crown and icefall.
p=part(3,'glimmer_islet');x,y,z=p.anchor
rings=[]
for yy,r in [(y,0.1),(y+6,3),(y+17,7),(y+20,10),(y+21,9)]:
    rings.append([[x+r*math.cos(math.tau*i/14)-p.anchor[0],yy-p.anchor[1],z+r*math.sin(math.tau*i/14)-p.anchor[2]] for i in range(14)])
p.loft('Rock',rings);rounded(p,'Snow',[x,y+20,z],[18,1.3,18])
for k in range(5):
    xx=x+(k-2)*1.7;zz=z+(-1)**k*1.7;hh=5+(k%3)*2
    mound(p,'Ice',[xx,y+21,zz],[1.8,hh,1.6],n=6);tube(p,'IceCore',[xx,y+21,zz],[xx,y+20+hh,zz],.10,.035)
for k in range(4):rounded(p,'Ice',[x+7+k*.35,y+10,z-2+k*1.1],[.7,10,1])
p=part(3,'ice_plank',felt_skins=['plank'])
box(p,'Ice',[0,-.3,-37],[1.8,.6,26]);box(p,'Ice',[0,-.7,-37],[2.4,.2,26]);box(p,'Felt',[0,-.01,-37],[1.8,.02,26])
for x in [-.8,.8]:box(p,'IceCore',[x,-.22,-37],[.12,.12,25.8])
p=part(3,'ice_bridge',skins=['bridge_rail6','bridge_rail7','shore_rail4','shore_rail5','green_rail8','green_rail12'],felt_skins=['ice_bridge'])
box(p,'Ice',[6,-.65,-37],[5,.1,25.8]);box(p,'IceCore',[6,-.72,-37],[.8,.04,25.6]);box(p,'Ice',[6,-.2,-37],[4,.4,26])
for w in H[3]['walls']:
 if w['id'] in ['bridge_rail6','bridge_rail7']:
    c=w['center'];s=w['size'];box(p,'Timber',c,s,w['yaw'])
    rounded(p,'Snow',[c[0],.85,c[2]],[s[0],.15,s[2]])
    for zz in [-47,-43,-39,-35,-31,-27]:tube(p,'Timber',[c[0],.8,zz],[c[0],1.45,zz],.13,.10)
# H5 revised anchors.
m=H[5]['moving_parts'][0];p=part(5,'geyser_column',pivot=m['pivot']);p.motion=m
box(p,'Basalt',[0,-2,-26.5],[3,4,3])
for mat,y in [('MoveRed',-.45),('MoveCream',-.65)]:box(p,mat,[0,y,-26.5],[3,.12,3])
# Inset hexagonal tiles and vent retain square contact faces.
for xx in [-.75,.75]:
 for zz in [-27.25,-25.75]:
    mound(p,'Rock',[xx,-.12,zz],[1.35,.12,1.35],n=6)
box(p,'Brass',[0,-.02,-26.5],[.7,.04,.7]);box(p,'Ink',[0,-.01,-26.5],[.46,.02,.46])
box(p,'Brass',[0,-1.3,-25.01],[.55,.6,.015]);mound(p,'Glow',[0,-1.2,-25.018],[.25,.25,.01])
p=part(5,'steamwhistle_geyser');x,y,z=p.anchor
rings=[]
for yy,r in [(0,3),(2,2.55),(4.5,1.85),(6.5,1.2),(7,1),(7,.68),(6.65,.65)]:
 rings.append([[r*math.cos(math.tau*i/16),yy,r*math.sin(math.tau*i/16)] for i in range(16)])
p.loft('Basalt',rings);mound(p,'Ink',[x,y+6.6,z],[1.25,.05,1.25],n=16)
for name in ['cliff_face_w','cliff_face_e']:
 p=part(5,name);c=p.anchor;s=a(5,name)['approx_size'];box(p,'Basalt',[c[0],1.75,c[2]],s)
 for k in range(6):
    xx=c[0]-4.6+k*1.8;rounded(p,'Rock',[xx,.1,c[2]+.19],[1.4,3.3,.10]);rounded(p,'Snow',[xx,2.3,c[2]+.20],[.15,1,.08])
 p.notes.append('Exact envelope top y3.5 meets upper rail bottom y3.5: source contradicts 0.1 rail gate; skip if verified failure.')
p=part(5,'signal_lamp');x,y,z=p.anchor;rounded(p,'Brass',[x,y,z],[.6,1,.4]);rounded(p,'AuroraMint',[x,y+.35,z+.18],[.38,.38,.035])
p.notes.append('Signal lens green while flush; runtime amber state supplied by lift controller.')
p=part(5,'geyser_steps');x,y,z=p.anchor
for k in range(5):box(p,'Timber',[15,(k+1)*.4,-17-(k+.5)*1.5],[3,(k+1)*.8,1.5])
box(p,'Timber',[15,2,-26.75],[3,4,4.5])
pts=[[13.65,.8+3.5,-17.75],[13.65,2.4+3.5,-20.75],[13.65,4+3.5,-23.75],[13.65,7.5,-28.85]]
for aa,bb in zip(pts,pts[1:]):tube(p,'Timber',aa,bb,.10)
for aa in pts:tube(p,'Timber',[aa[0],aa[1]-3.5,aa[2]],aa,.10)
for aa,bb in zip(pts,pts[1:]):bar(p,'Timber',[aa[0],aa[1]-2.9,aa[2]],[bb[0],bb[1]-2.9,bb[2]],.32)
# H7 ten independent branching clumps at revised prose positions, no obsolete aggregate.
clumps=[('coral_w1',-6.5,-11,4.5,'CoralPink'),('coral_w2',-9,-18,6,'CoralOrange'),('coral_w3',-6,-24.5,3.5,'CoralMint'),('coral_w4',-10,-30,5.5,'CoralPink'),('coral_w5',-7,-35,4,'CoralOrange'),('coral_e6',7,-13.5,4,'CoralMint'),('coral_e7',9.5,-20.5,5.5,'CoralPink'),('coral_e8',6,-26,3,'CoralOrange'),('coral_e9',8.5,-31.5,6,'CoralMint'),('coral_e10',6.5,-35.5,4.5,'CoralPink')]
for k,(name,x,z,h,col) in enumerate(clumps):
 p=part(7,name,pivot=[x,0,z]);coral(p,p.anchor,[h*.5,h,h*.4],col,k)
p=part(7,'mogul_trim',skins=[w['id'] for w in H[7]['walls'] if abs(w['center'][0])==4.25 and -36<=w['center'][2]<=-8])
for w in H[7]['walls']:
 if w['id'] in p.skin_ids:
    c=w['center'];s=w['size'];box(p,'Timber',c,[s[0],s[1],s[2]-.2],w['yaw']);rounded(p,'Snow',[c[0],c[1]+s[1]/2-.16,c[2]],[s[0],.16,s[2]-.2])
p=part(8,'giant_coral');coral(p,p.anchor,[7,14,7],seed=2)
for i in range(1,8):
 w=next(w for w in H[8]['walls'] if w['id']==f'coral{i}');p=part(8,f'coral_{i}',skins=[w['id']]);box(p,'CoralPink',[w['center'][0],.8,w['center'][2]],[w['size'][0],1.6,w['size'][2]],w['yaw'])
 q=Part('tmp',8,[0,0,0]);coral(q,[0,1.6,0],[min(2.8,w['size'][0]*1.12),2.4,min(1.4,w['size'][2]*1.1)],seed=i)
 for mat,(vs,fs) in q.g.items():p.add(mat,[[v[0]+w['center'][0]-p.anchor[0],v[1]-p.anchor[1],v[2]+w['center'][2]-p.anchor[2]] for v in [roty(v,w['yaw']) for v in vs]],fs)
# Mandatory exceptions only for demonstrated source contradictions, applied by fitcheck selection.
out=[]
for p in P:out.append(dict(id=p.name,hole=p.hole,anchor=p.anchor,yaw_local=0,groups={m:dict(verts=v,faces=f) for m,(v,f) in p.g.items()},skin_ids=p.skin_ids,felt_skins=p.felt_skins,motion=p.motion,notes=p.notes))
(S/'parts.json').write_text(json.dumps(out));(S/'skipped.json').write_text(json.dumps(skipped,indent=2));(S/'palette.json').write_text(json.dumps(PAL,indent=2))
print('Generated',len(out),'rev2 parts')
'''
(S/'gen_batch1.py').write_text(g)
# Remove stale triangle cache before numeric generator check.
(S/'triangles.json').unlink()
