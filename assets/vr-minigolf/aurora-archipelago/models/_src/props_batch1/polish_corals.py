"""Generate only the eighteen requested corals. Never launches Blender."""
import sys,json,math,hashlib,shutil
from pathlib import Path
import numpy as np
S=Path(__file__).resolve().parent;D=S.parents[2]
sys.path.insert(0,str(S.parent))
from polish_geometry import Mesh,components,count
MD5='fb913741b5dd4812b6d2318e258bcc46'
IDS=[f'h07_coral_w{i}' for i in range(1,6)]+[f'h07_coral_e{i}' for i in range(6,11)]+['h08_giant_coral']+[f'h08_coral_{i}' for i in range(1,8)]

def main():
    assert hashlib.md5((D/'holes.json').read_bytes()).hexdigest()==MD5
    target=S/'parts.json';backup=S/'parts_prepolish.json'
    if not backup.exists():shutil.copy2(target,backup)
    ps=json.loads(backup.read_text());shapes=[]
    for seed,p in enumerate(ps):
        if p['id'] not in IDS:continue
        col=next(iter(p['groups']));m=Mesh();giant='giant' in p['id'];skin=bool(p['skin_ids'])
        chunks=list(components(p['groups'][col]));domes=[g for g in chunks if len(g['verts']) in [48,70]]
        assert len(domes)==(21 if giant else 6),(p['id'],len(domes))
        for g in domes:m.add(col,g['verts'],g['faces'])
        if skin:m.add(col,p['groups'][col]['verts'][:8],p['groups'][col]['faces'][:6])
        # Root cap/base ring copied exactly; a thin leaning stem rises from it.
        root=chunks[0 if not skin else 1];n=len(root['verts'])//2
        root_ring=root['verts'][:n]
        base=min(v[1] for v in root_ring);v=np.array([v for g in domes for v in g['verts']]);height=float(v[:,1].max()-base)
        split_y=base+(2.8 if giant else height*.48)
        angle=3+seed%6;direction=-1 if seed%2 else 1
        shift=math.tan(math.radians(angle))*(split_y-base)*direction
        stem=np.array([shift,split_y,0.])
        radius=.05*height
        upper=[[shift+radius*math.cos(math.tau*i/n),split_y,radius*math.sin(math.tau*i/n)] for i in range(n)]
        m.loft(col,[root_ring,upper])
        centres=[np.mean(g['verts'],axis=0) for g in domes]
        # Three first forks each divide into two terminal branches, embedded in the retained lumps.
        for j in range(0,len(centres),2):
            tips=centres[j:j+2];mid=(stem+np.mean(tips,axis=0))/2
            m.tube(col,stem,mid,radius*.65,radius*.4,n=4)
            for tip in tips:m.tube(col,mid,tip,radius*.4,radius*.2,n=4)
        # Eight soft glow blobs sit between shoulder lumps; the crown envelope stays fixed.
        lo=v.min(axis=0);hi=v.max(axis=0);exposures=[]
        # Intersect rays with the retained crown: glow cores must actually emerge
        # through its gaps instead of being buried in a large lump.
        triangles=np.array([[g['verts'][f[0]],g['verts'][f[k]],g['verts'][f[k+1]]] for g in domes for f in g['faces'] for k in range(1,len(f)-1)])
        aa=triangles[:,0,:2];u=triangles[:,1,:2]-aa;vv=triangles[:,2,:2]-aa;det=u[:,0]*vv[:,1]-u[:,1]*vv[:,0];valid=np.abs(det)>1e-12
        def front(x,y):
            delta=np.array([x,y])-aa
            s=np.divide(delta[:,0]*vv[:,1]-delta[:,1]*vv[:,0],det,out=np.zeros_like(det),where=valid)
            t=np.divide(u[:,0]*delta[:,1]-u[:,1]*delta[:,0],det,out=np.zeros_like(det),where=valid)
            inside=valid&(s>=-1e-8)&(t>=-1e-8)&(s+t<=1+1e-8)
            z=triangles[:,0,2]+s*(triangles[:,1,2]-triangles[:,0,2])+t*(triangles[:,2,2]-triangles[:,0,2])
            return float(z[inside].max()) if inside.any() else None
        for j in range(8):
            a=centres[j%len(centres)];b=centres[(j+1)%len(centres)];c=(a+b)/2
            size=np.minimum([.34,.24,.34],(hi-lo)*.45)
            candidates=[]
            ry=float(np.ptp(np.array(domes[j%len(domes)]['verts'])[:,1])/2)
            for amount in [.75,.85,.93,.97]:
                y=float(np.clip(c[1]+ry*amount,lo[1]+size[1]/2,hi[1]-size[1]/2));z=front(c[0],y)
                if z is not None:candidates.append((min(.2,float(hi[2]-z)),y,z))
            assert candidates,(p['id'],j)
            exposure,y,z=max(candidates);c[1]=y
            # Six-sided, three-latitude rounded core actual Z radius is .375*size.
            radius_z=size[2]*.375;c[2]=min(z+.2-radius_z,hi[2]-radius_z)
            exposures.append(float(c[2]+radius_z-z))
            m.sphere('AuroraMint',c,size,n=6,steps=3)
        p['groups']=m.groups;p.update(can_collide=False,can_query=False,can_touch=False)
        p['notes'].append(f'Polish: retained rev6/rev7 lumpy crown and exact base; {angle} degree leaning thin trunk, paired fork branches, eight rounded AuroraMint Neon gap cores. Giant retains three stacked domes and 4-stud cap.')
        tris=count(m.groups);assert tris<(3000 if giant else 901),(p['id'],tris)
        shapes.append(dict(id=p['id'],old_tris=count(json.loads(backup.read_text())[seed]['groups']),new_tris=tris,lean_degrees=angle,glow_cores=8,core_proud_studs=exposures,retained_dome_components=len(domes)))
    target.write_text(json.dumps(ps));(S/'polish_ids.json').write_text(json.dumps(IDS,indent=2));(S/'polish_shapes.json').write_text(json.dumps(shapes,indent=2))
    print('Generated',len(shapes),'polished corals; max small tris',max(x['new_tris'] for x in shapes if 'giant' not in x['id']))
if __name__=='__main__':main()
