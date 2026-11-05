"""Deterministic pass-2 rules; heightmap visibility and conservative scatter sightline bounds."""
import json, math
from pathlib import Path
import numpy as np
from PIL import Image
SRC = Path(__file__).resolve().parent
MODELS = SRC.parent
COURSE = MODELS.parent

def world_point(h, p):
    a = math.radians(h['world_yaw']); c, s = math.cos(a), math.sin(a)
    x,y,z = p; ox,oy,oz = h['world_offset']
    return np.array([x*c+z*s+ox,y+oy,-x*s+z*c+oz])

def sightlines():
    result = []
    for h in json.loads((COURSE/'holes.json').read_text())['holes']:
        tee = world_point(h,h['tee']['position'])
        cup = world_point(h,h['cup']['position'])
        result.append((h['number'],tee+[0,5,0],cup+[0,7.5,0],cup+[0,1,0]))
    return result

def member_bounds(m):
    # Variant cache supplies actual extents, expanded 25% for procedural seed variation.
    t = np.load(SRC/'_cache'/'tris'/(m['variant']+'.npy')).reshape(-1,3)
    lo,hi = t.min(0),t.max(0)
    center=(lo+hi)/2; half=(hi-lo)/2*1.25+0.25
    a=math.radians(m.get('yaw',0)); c,s=math.cos(a),math.sin(a)
    rot=np.array([[c,0,s],[0,1,0],[-s,0,c]])
    scale=m.get('scale',1)
    return np.array(m['pos'])+rot@center*scale,abs(rot)@half*scale

def segment_box(a,b,center,half,margin=1.5):
    lo,hi=center-half-margin,center+half+margin
    d=b-a; t0,t1=0.,1.
    for k in range(3):
        if abs(d[k])<1e-9:
            if a[k]<lo[k] or a[k]>hi[k]: return False
        else:
            u,v=sorted(((lo[k]-a[k])/d[k],(hi[k]-a[k])/d[k]))
            t0=max(t0,u); t1=min(t1,v)
            if t0>t1: return False
    return True

def hits(m):
    center,half=member_bounds(m)
    return [n for n,a,b,c in sightlines() if segment_box(a,b,center,half) or segment_box(a,c,center,half)]

def apply(layout):
    if 'pass2' in layout: return layout['pass2']
    removed={str(n):0 for n,*_ in sightlines()}; changed=[]; removed_ids=[]
    for name,cl in layout['clusters'].items():
        if not name.startswith('scatter_'): continue
        keep=[]
        for k,m in enumerate(cl['members']):
            m['seed']=k*17+3
            hh=hits(m)
            if hh:
                for n in hh: removed[str(n)]+=1
                removed_ids.append({'cluster':name,'member':m,'holes':hh})
            else: keep.append(m)
        if len(keep)!=len(cl['members']): changed.append(name)
        cl['members']=keep
    # 64-stud stretches on the outer square rim. Test terrain crest itself,
    # at endpoints/centre, from tees and walkway samples spaced <=16 studs.
    hm=np.asarray(Image.open(COURSE/'world'/'heightmap.png'),dtype=float)/65535*260
    def height(x,z):
        return hm[np.clip(np.asarray(z+640,dtype=int),0,1279),np.clip(np.asarray(x+640,dtype=int),0,1279)]
    w=json.loads((COURSE/'world'/'world.json').read_text())
    observers=[(f'H{n}',a) for n,a,*_ in sightlines()]
    for p in w['paths']:
        for k,seg in enumerate(p['segments']):
            if seg['type'] not in ('walk','ramp','stairs','landing','bridge','dam_crest','on_hole'): continue
            a,b=np.array(seg['start']),np.array(seg['end'])
            for t in np.linspace(0,1,max(2,math.ceil(np.linalg.norm(b-a)/16)+1)):
                observers.append((f"{p['id']}:{k}",a+(b-a)*t+[0,5,0]))
    coverage=[]; candidates=0
    for side in range(4):
        for q in range(20):
            u=-608+64*q
            x,z=((u,-632),(632,u),(u,632),(-632,u))[side]
            base=float(height(x,z)); visible=[]; candidates+=1
            for label,eye in observers:
                found=False
                for du in (-28,0,28):
                    tx,tz=(x+du,z) if side%2==0 else (x,z+du)
                    target=np.array([tx,float(height(tx,tz))+0.75,tz])
                    d=target-eye; length=np.linalg.norm(d[[0,2]])
                    ts=np.linspace(0,1,max(2,math.ceil(length/2)+1))[1:-1]
                    ray=eye[None,:]+ts[:,None]*d
                    if np.all(ray[:,1]>height(ray[:,0],ray[:,2])+0.15): found=True; break
                if found: visible.append(label)
            if not visible: continue
            # Short silhouette blade, buried beneath local crest; never cliff kit.
            y0=base-12
            inst={'piece':'rim_silhouette','pos':[x,round(y0,2),z],'yaw':[0,90,0,90][side],
                  'scale':[1,1,1],'src':f'rim_{side}_{q}',
                  'note':'Visible outer-rim silhouette; CastShadow off; no cliff kit.'}
            layout['instances'].append(inst)
            coverage.append({'stretch':inst['src'],'pos':inst['pos'],'visible_from':sorted(set(visible))})
    report={'rim_candidates':candidates,'rim_covered':len(coverage),'observer_samples':len(observers),
            'rim_coverage':coverage,'removed_per_hole':removed,'removed_unique':len(removed_ids),
            'removed_members':removed_ids,'affected_clusters':changed,
            'method':'Rim crest rays vs 16-bit heightfield at <=2-stud intervals; walkway observers <=16 studs. Scatter segment vs variant AABB expanded 25% + 0.25, then 1.5-stud corridor; flag and cup+1 endpoints.'}
    layout['pass2']=report
    layout['counts']={}
    for i in layout['instances']: layout['counts'][i['piece']]=layout['counts'].get(i['piece'],0)+1
    layout['assumptions'] += [report['method'],f"Pass2: {len(coverage)}/{candidates} visible rim stretches receive 64-wide low-poly striped silhouettes (CastShadow off); no outer rim cliff kit.",f"Pass2: removed {len(removed_ids)} scatter members; per-hole counts {removed}; stable member seeds retained."]
    return report

if __name__=='__main__':
    p=MODELS/'layout.json'; l=json.loads(p.read_text()); r=apply(l); p.write_text(json.dumps(l,indent=1))
    print(json.dumps({k:v for k,v in r.items() if k not in ('rim_coverage','removed_members')},indent=1))
