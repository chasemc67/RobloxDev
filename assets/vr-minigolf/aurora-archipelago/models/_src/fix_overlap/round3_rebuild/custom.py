import numpy as np,trimesh,sys
sys.path.insert(0,'/workspace/aa3');from metrics import parts_of
def box(lo,hi):
    lo=np.array(lo,float);hi=np.array(hi,float);return trimesh.creation.box(extents=hi-lo,transform=trimesh.transformations.translation_matrix((lo+hi)/2))
def fit_y(m,y0,y1):
    m=m.copy();b=m.bounds;v=m.vertices.copy();v[:,1]=y0+(v[:,1]-b[0,1])*(y1-y0)/(b[1,1]-b[0,1]);m.vertices=v;return m
def objs_from(lst):
    out={}
    for name,m in lst:
        o=out.setdefault(name,dict(name=name,verts=[],tris=[]));b=len(o['verts'])
        o['verts']+=m.vertices.tolist();o['tris']+=(np.asarray(m.faces)+b).tolist()
    return list(out.values())
G=0.086
def head(N,cx,cz,y0,plate_hw,glow_hw,glow_h,cap,snow,mat):
    yp=y0+0.2;yg0=yp+G;yg1=yg0+glow_h;yc0=yg1+G;yc1=yc0+0.2;ys0=yc1+G;ys1=ys0+0.2
    return [(N+'__Brass',box([cx-plate_hw,y0,cz-plate_hw],[cx+plate_hw,yp,cz+plate_hw])),
            (N+'__Glow',box([cx-glow_hw,yg0,cz-glow_hw],[cx+glow_hw,yg1,cz+glow_hw])),
            (N+'__Brass',fit_y(cap,yc0,yc1)),(N+'__Snow',fit_y(snow,ys0,ys1))]
def ramp_lanterns(objects):
    N='h18_ramp_lanterns';P=parts_of(objects);out=[]
    caps=[m for n,m in P if n.endswith('Brass') and len(m.faces)==76]
    snows=[m for n,m in P if n.endswith('Snow')]
    for z0 in (-3.5,0.0,3.5):
        cap=min(caps,key=lambda m:abs(m.centroid[2]-z0));snow=min(snows,key=lambda m:abs(m.centroid[2]-z0))
        out+=[(N+'__Timber',box([-.3,.446,z0-.3],[.3,5.614,z0+.3])),
              (N+'__Brass',box([-.449,.16,z0-.475],[1.449,.36,z0+.475]))]
        out+=head(N,0,z0,5.70,.3,.183,0.40,cap,snow,None)
    return objs_from(out)
def bobsled(objects):
    N='h10_bobsled_hut';P=parts_of(objects);out=[]
    lant=lambda m: m.bounds[0,1]>4.0 and m.bounds[1,1]<4.75 and abs(m.centroid[0])<0.3
    cap=[m for n,m in P if n.endswith('Brass') and len(m.faces)==76][0]
    snow=[m for n,m in P if n.endswith('Snow')][0]
    for n,m in P:
        if lant(m): continue
        if n.endswith('Brass') and m.bounds[1,1]<0.25:   # sled runners -> 0.2 boxes under the hull
            cx=m.centroid[0];out.append((n,box([cx-.1,.014,m.bounds[0,2]],[cx+.1,.214,m.bounds[1,2]])));continue
        out.append((n,m))
    out+=head(N,0,1.8,4.10,.225,.137,0.30,cap,snow,None)
    return objs_from(out)
def lip_ice(objects):
    return objs_from([(n,m) for n,m in parts_of(objects) if abs(m.volume)>1e-6 and m.is_watertight])
def loft(rings):
    V=[];F=[];k=len(rings[0])
    for r in rings: V+=r
    for i in range(len(rings)-1):
        for j in range(k):
            a,b=i*k+j,i*k+(j+1)%k;c,d=a+k,b+k;F+=[[a,b,d],[a,d,c]]
    n=len(rings)-1
    for j in range(1,k-1): F.append([0,j+1,j]);F.append([n*k,n*k+j,n*k+j+1])
    m=trimesh.Trimesh(np.array(V),np.array(F),process=True);trimesh.repair.fix_normals(m);return m
def falls(objects):
    out=[];ice=[m for n,m in parts_of(objects) if n.endswith('__Ice')][0]
    for n,m in parts_of(objects):
        if n.endswith('IceCore'):
            ys=np.round(m.vertices[:,1],3);levels=sorted(set(ys))
            keep=[l for l in levels if abs(l%20)<1e-6 or l==levels[-1]]
            rings=[]
            for l in keep:
                P=m.vertices[ys==l];c=P.mean(0);ang=np.arctan2(P[:,2]-c[2],P[:,0]-c[0]);P=P[np.argsort(ang)].copy()
                P[:,1]=min(max(l,0.12),145.88)
                for _ in range(40):   # keep every ring >=0.12 inside the ice (push toward ice centre plane z=0)
                    sd=trimesh.proximity.signed_distance(ice,P)
                    if sd.min()>=0.12: break
                    P[:,2]+=0.02
                rings.append(P.tolist())
            m=loft(rings)
            S=np.vstack([m.vertices,trimesh.sample.sample_surface_even(m,4000,seed=1)[0]])
            for _ in range(60):   # uniform push toward the ice centre plane until every sample is >=0.12 inside
                if trimesh.proximity.signed_distance(ice,S).min()>=0.12: break
                m.apply_translation([0,0,0.02]);S[:,2]+=0.02
            if not m.is_watertight or m.volume<=0: raise RuntimeError('core loft bad')
        out.append((n,m))
    return objs_from(out)
