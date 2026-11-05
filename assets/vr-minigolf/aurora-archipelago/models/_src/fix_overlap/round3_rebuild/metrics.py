import json,sys,numpy as np,trimesh,fcl
sys.path.insert(0,'/workspace/aa3')
from clearance import solids,measure
D='/workspace/RobloxDev/assets/vr-minigolf/aurora-archipelago/'
HOLES={h['number']:h for h in json.load(open(D+'holes.json'))['holes']}
PARTS={}
for b in (1,2,3):
    for p in json.load(open(D+f'models/props_batch{b}_manifest.json'))['parts']: PARTS[p['id']]=p
def parts_of(asset):
    """asset: list of objects {name,verts,tris}; returns list of (objname, island trimesh)"""
    out=[]
    for o in asset:
        m=trimesh.Trimesh(np.array(o['verts'],float),np.array(o['tris']),process=True)
        for i in m.split(only_watertight=False): out.append((o['name'],i))
    return out
def fobj(m):
    b=fcl.BVHModel();b.beginModel(len(m.vertices),len(m.faces));b.addSubModel(m.vertices,m.faces);b.endModel()
    return fcl.CollisionObject(b,fcl.Transform())
def gap(a,b):
    oa,ob=fobj(a),fobj(b)
    if fcl.collide(oa,ob,fcl.CollisionRequest(),fcl.CollisionResult()): return -1.0
    # containment: fcl BVH only tests surfaces
    if a.is_watertight and a.contains(b.vertices[:1]).any(): pass
    r=fcl.DistanceResult();fcl.distance(oa,ob,fcl.DistanceRequest(enable_nearest_points=True),r)
    return float(r.min_distance)
def thickness(m): return float(min(m.bounding_box_oriented.primitive.extents))
def coplanar_pairs(parts,tol=1e-3):
    T=[];L=[]
    for k,(n,m) in enumerate(parts):
        T.append(m.triangles);L+= [k]*len(m.faces)
    T=np.concatenate(T);L=np.array(L)
    n=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]);ar=np.linalg.norm(n,axis=1);n=n/np.maximum(ar[:,None],1e-12)
    lo=T.min(1)-tol;hi=T.max(1)+tol;cnt=0
    for i in range(len(T)):
        j=np.nonzero((L>L[i])&np.all(lo<=hi[i],1)&np.all(hi>=lo[i],1))[0]
        if not len(j): continue
        j=j[(np.abs(n[j]@n[i])>0.9999)&(np.abs((T[j,0]-T[i,0])@n[i])<tol)]
        if not len(j): continue
        from shapely.geometry import Polygon
        u=np.cross(n[i],[1,0,0] if abs(n[i][0])<.9 else [0,1,0]);u/=np.linalg.norm(u);w=np.cross(n[i],u)
        pi=Polygon([(p@u,p@w) for p in T[i]])
        for jj in j:
            if pi.intersection(Polygon([(p@u,p@w) for p in T[jj]])).area>1e-6: cnt+=1
    return int(cnt)
def report(id,asset,clear=True):
    p=PARTS[id];parts=parts_of(asset)
    r=dict(tris=int(sum(len(o['tris']) for o in asset)),verts=int(sum(len(o['verts']) for o in asset)),parts=len(parts),
           per_object={o['name'].split('__')[-1]:[len(o['verts']),len(o['tris'])] for o in asset})
    th=[thickness(m) for _,m in parts];r['min_thickness']=round(min(th),4);r['thin_parts']=int(sum(t<0.2-1e-6 for t in th))
    gaps=[];bad=0;inter=0
    for i in range(len(parts)):
        for j in range(i+1,len(parts)):
            a,b=parts[i][1],parts[j][1]
            if np.any(a.bounds[0]-0.2>b.bounds[1]) or np.any(b.bounds[0]-0.2>a.bounds[1]): continue
            g=gap(a,b);gaps.append(g)
            if g<0: inter+=1
            elif g<0.08-1e-6: bad+=1
    r['intersecting_pairs']=inter;r['stacked_lt_0.08']=bad;r['min_gap']=round(min(gaps),4) if gaps else None
    r['coplanar_tri_pairs']=coplanar_pairs(parts)
    if clear:
        T=np.concatenate([m.triangles for _,m in parts])+np.array(p['anchor_local'])
        c=measure(T,solids(HOLES[p['hole']]))
        r['rail']=round(c['rail']['clearance'],4);r['felt']=round(c['felt']['clearance'],4)
    return r
def silhouette(asset_a,asset_b,res=0.04):
    from PIL import Image,ImageDraw
    def tris(asset): return np.concatenate([np.array(o['verts'],float)[np.array(o['tris'])] for o in asset])
    A,B=tris(asset_a),tris(asset_b)
    lo=np.minimum(A.reshape(-1,3).min(0),B.reshape(-1,3).min(0))-res;hi=np.maximum(A.reshape(-1,3).max(0),B.reshape(-1,3).max(0))+res
    out={}
    for name,(u,v) in {'front':(0,1),'side':(2,1),'top':(0,2)}.items():
        W=int((hi[u]-lo[u])/res)+2;H=int((hi[v]-lo[v])/res)+2
        ims=[]
        for T in (A,B):
            im=Image.new('1',(W,H),0);dr=ImageDraw.Draw(im)
            for t in T: dr.polygon([((p[u]-lo[u])/res,(p[v]-lo[v])/res) for p in t],fill=1)
            ims.append(np.array(im,bool))
        a,b=ims;out[name]=round(float((a&b).sum()/max((a|b).sum(),1)),4)
    ba=A.reshape(-1,3);bb=B.reshape(-1,3)
    out['bbox_delta_max']=round(float(max(np.abs(ba.min(0)-bb.min(0)).max(),np.abs(ba.max(0)-bb.max(0)).max())),4)
    return out
def local_thickness(asset):
    """min over faces of inward ray distance to the opposite surface of the same part"""
    best=1e9
    for _,m in parts_of(asset):
        k=m.area_faces>1e-3
        c=m.triangles_center[k]-m.face_normals[k]*1e-4
        loc,ri,_=m.ray.intersects_location(c,-m.face_normals[k],multiple_hits=False)
        if len(ri):
            d=np.linalg.norm(loc-c[ri],axis=1);best=min(best,float(d.min()))
    return round(best,4)
