import json,sys,numpy as np,trimesh,manifold3d as M
sys.path.insert(0,'/workspace/aa3')
from metrics import parts_of,PARTS,HOLES
from clearance import solids
GAP=0.08;CLR=0.15;TH=0.2;EPS=0.006
def to_man(m):
    mm=M.Mesh(vert_properties=np.asarray(m.vertices,np.float32),tri_verts=np.asarray(m.faces,np.uint32))
    r=M.Manifold(mm)
    if r.is_empty() or r.status()!=M.Error.NoError: return None
    return r
def to_tm(x):
    mm=x.to_mesh();t=trimesh.Trimesh(np.asarray(mm.vert_properties)[:,:3].astype(float),np.asarray(mm.tri_verts),process=True)
    t.update_faces(t.nondegenerate_faces(height=1e-7));t.remove_unreferenced_vertices();return t
def sgap(a,b,lim=1.0):
    from metrics import gap as fgap
    iv=(a^b).volume()
    if iv>1e-9:
        if iv>=0.999*min(a.volume(),b.volume()): return fgap(to_tm(a),to_tm(b))
        return -1.0
    return a.min_gap(b,lim)
def cube(h): return M.Manifold.cube([2*h]*3,True)
def hullish(x):
    h=x.hull()
    return h if h.volume()<=1.15*x.volume()+1e-9 else None
def dil(x,h):
    H=hullish(x)
    if H is not None: return H.minkowski_sum(cube(h))
    return M.Manifold.batch_boolean([f.hull().minkowski_sum(cube(h)) if f.hull().volume()<=1.15*f.volume() else f.minkowski_sum(cube(h)) for f in x.decompose()],M.OpType.Add)
def ero(x,h): return x.minkowski_difference(cube(h))
def thicken(m):
    obb=m.bounding_box_oriented;T=obb.primitive.transform;ext=obb.primitive.extents
    s=np.where(ext<TH+EPS,(TH+EPS)/np.maximum(ext,1e-4),1.0)
    if np.all(s==1): return m,False
    inv=np.linalg.inv(T);v=trimesh.transform_points(m.vertices,inv)*s
    return trimesh.Trimesh(trimesh.transform_points(v,T),m.faces.copy()),True
def solids_local(p):
    out=[]
    for b in solids(HOLES[p['hole']]):
        v=b['vertices']-np.array(p['anchor_local'])
        out.append(M.Manifold.hull_points(v.tolist()))
    return out
def rebuild(id,objects,order=None,notes=None,shift=None):
    p=PARTS[id];parts=parts_of(objects);log=[]
    items=[]
    for k,(name,m) in enumerate(parts):
        if shift and k in shift: m=m.copy();m.apply_translation(shift[k]);log.append(f'part {k} shifted {shift[k]}')
        m2,t=thicken(m)
        if t: log.append(f'part {k} {name.split("__")[1]} thickened to >= {TH}')
        mf=to_man(m2)
        if mf is None:
            m3=m2.copy();m3.merge_vertices(digits_vertex=4);trimesh.repair.fill_holes(m3);trimesh.repair.fix_normals(m3);mf=to_man(m3)
            if mf is None: mf=M.Manifold.hull_points(m2.vertices.tolist());log.append(f'part {k} {name.split("__")[1]} not closed: replaced by its convex hull')
            else: log.append(f'part {k} {name.split("__")[1]} not closed: holes filled')
        items.append(dict(k=k,name=name,orig=m,man=mf,vol=abs(mf.volume())))
    seq=order if order else sorted(range(len(items)),key=lambda i:-items[i]['vol'])
    cut=[dil(s,CLR+EPS) for s in solids_local(p)]
    placed=[]
    TRANSP=('__Ice','__Glass')
    def clean(x,i):
        keep=[]
        for f in x.decompose():
            if f.volume()<1e-6 or min(to_tm(f).bounding_box_oriented.primitive.extents)<TH-1e-4: log.append(f'part {i} dropped thin fragment vol {f.volume():.4f}')
            else: keep.append(f)
        return M.Manifold.batch_boolean(keep,M.OpType.Add) if keep else M.Manifold()
    for i in seq:
        it=items[i];x=it['man']
        for c in cut:
            if (x^c).volume()>1e-9: x=x-c;log.append(f'part {i} trimmed for felt/rail clearance')
        it['fin']=clean(x,i);it['man0']=it['fin'];placed.append(i)
    rank={k:n for n,k in enumerate(seq)};insets={};pockets={}
    for rnd in range(4):
        changed=False
        for a_ in placed:
            for b_ in placed:
                if rank[a_]>=rank[b_]: continue
                P=items[a_]['fin'];x=items[b_]['fin']   # P bigger/earlier, x smaller
                if P.is_empty() or x.is_empty(): continue
                if sgap(x,P,GAP+EPS)>=GAP+EPS/2: continue
                changed=True
                inside=(x^P).volume()/max(x.volume(),1e-12)
                if items[a_]['name'].endswith(TRANSP) and inside>0.5:
                    y=clean(x^ero(items[a_]['man0'],GAP+EPS),b_)
                    if y.volume()>0.5*x.volume():
                        items[b_]['fin']=y;insets.setdefault(a_,set()).add(b_);log.append(f'r{rnd} part {b_} inset {GAP} inside transparent part {a_}');continue
                items[a_]['fin']=clean(P-dil(x,GAP+EPS),a_);pockets.setdefault(a_,set()).add(b_);log.append(f'r{rnd} part {a_} pocketed {GAP} around part {b_}')
        for a_,ys in insets.items():
            for y in ys:
                for x in pockets.get(a_,()):
                    if x in ys: continue
                    Y=items[y]['fin']
                    if Y.is_empty(): continue
                    if sgap(Y,items[a_]['fin'],GAP+EPS)<GAP+EPS/2:
                        items[y]['fin']=clean(Y-dil(items[x]['fin'],2*(GAP+EPS)),y);log.append(f'r{rnd} inset part {y} cleared {2*GAP} from pocket of part {x}');changed=True
        if not changed: break
    for a_ in placed:
        for b_ in placed:
            if a_<b_ and not items[a_]['fin'].is_empty() and not items[b_]['fin'].is_empty():
                g=sgap(items[a_]['fin'],items[b_]['fin'],1.0)
                if g<GAP: log.append(f'WARN gap {a_}-{b_} {g:.4f}')
    objs={}
    for it in items:
        if it['fin'].is_empty(): log.append(f"part {it['k']} removed entirely");continue
        t=to_tm(it['fin']);o=objs.setdefault(it['name'],dict(verts=[],tris=[]))
        b=len(o['verts']);o['verts']+=t.vertices.tolist();o['tris']+=(t.faces+b).tolist()
    return objs,log
