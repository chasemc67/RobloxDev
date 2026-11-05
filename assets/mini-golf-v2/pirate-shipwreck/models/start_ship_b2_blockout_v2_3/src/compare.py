# Blender: -- W  -> W/compare.json : imports ref/*.fbx and reexport/*.fbx, compares names, origins, scale, tri counts, bbox
import bpy,sys,os,json
W=sys.argv[sys.argv.index('--')+1];res={}
def load(p):
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=p);d={}
    for o in bpy.data.objects:
        mw=o.matrix_world;e=dict(type=o.type,loc=[round(v,4) for v in mw.translation],scale=[round(v,5) for v in mw.to_scale()],rot=[round(v,5) for v in mw.to_euler()])
        if o.type=='MESH':
            co=[mw@v.co for v in o.data.vertices];e['tris']=sum(len(p.vertices)-2 for p in o.data.polygons);e['verts']=len(o.data.vertices)
            e['bbmin']=[round(min(c[i] for c in co),3) for i in range(3)];e['bbmax']=[round(max(c[i] for c in co),3) for i in range(3)];e['mats']=[m.name for m in o.data.materials]
        d[o.name]=e
    return d
for f in sorted(os.listdir(os.path.join(W,'ref'))):
    a=load(os.path.join(W,'ref',f));b=load(os.path.join(W,'reexport',f));mm=[]
    if set(a)!=set(b): mm.append(dict(names_only_ref=sorted(set(a)-set(b)),names_only_new=sorted(set(b)-set(a))))
    for n in set(a)&set(b):
        for k in ('type','loc','scale','rot','tris','verts','bbmin','bbmax'):
            if a[n].get(k)!=b[n].get(k): mm.append(dict(obj=n,key=k,ref=a[n].get(k),new=b[n].get(k)))
    res[f]=dict(objects=len(a),tris={n:v['tris'] for n,v in b.items() if 'tris' in v} if f!='start_ship_b2_col.fbx' else sum(v.get('tris',0) for v in b.values()),
      mats_ref=sorted({m for v in a.values() for m in v.get('mats',[])}),mats_new=sorted({m for v in b.values() for m in v.get('mats',[])}),mismatches=mm)
json.dump(res,open(os.path.join(W,'compare.json'),'w'),indent=1);print('COMPARED')
