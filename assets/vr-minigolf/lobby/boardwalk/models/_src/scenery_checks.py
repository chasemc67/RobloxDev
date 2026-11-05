"""Independent FBX triangle clearance, Euclidean distance and immutable-file audit."""
import bpy,json,hashlib,itertools
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import closest_point_on_tri
import bwlib as L
from pass3_checks import clearance,intersects

def segment_distance(p1,q1,p2,q2):
    d1=q1-p1;d2=q2-p2;r=p1-p2;a=d1.dot(d1);e=d2.dot(d2);f=d2.dot(r)
    if a<=1e-12 and e<=1e-12:return r.length
    if a<=1e-12:s=0;t=max(0,min(1,f/e))
    else:
        c=d1.dot(r)
        if e<=1e-12:t=0;s=max(0,min(1,-c/a))
        else:
            b=d1.dot(d2);den=a*e-b*b;s=max(0,min(1,(b*f-c*e)/den)) if den>1e-12 else 0
            t=(b*s+f)/e
            if t<0:t=0;s=max(0,min(1,-c/a))
            elif t>1:t=1;s=max(0,min(1,(b-c)/a))
    return (p1+d1*s-p2-d2*t).length

def distance(objs,mn,mx):
    corners=[Vector(v) for v in itertools.product(*[(mn[k],mx[k]) for k in range(3)])]
    edges=[(a,b) for i,a in enumerate(corners) for b in corners[i+1:] if sum(abs(a[k]-b[k])>1e-8 for k in range(3))==1]
    best=float('inf')
    for o in objs:
        o.data.calc_loop_triangles()
        for t in o.data.loop_triangles:
            vs=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
            lo=[min(v[k] for v in vs) for k in range(3)];hi=[max(v[k] for v in vs) for k in range(3)]
            lower=sum(max(mn[k]-hi[k],lo[k]-mx[k],0)**2 for k in range(3))**.5
            if lower>=best-1e-7:continue
            if intersects(vs,mn,mx):return 0
            for v in vs:best=min(best,sum(max(mn[k]-v[k],v[k]-mx[k],0)**2 for k in range(3))**.5)
            for c in corners:best=min(best,(c-closest_point_on_tri(c,*vs)).length)
            for a,b in zip(vs,vs[1:]+vs[:1]):
                for c,d in edges:best=min(best,segment_distance(a,b,c,d))
    return best

def run_scenery(root,man,check):
    root=Path(root);mins={}
    for e in man['props']:
        if not e['name'].startswith('bw_scn_'):continue
        L.reset_scene();bpy.ops.import_scene.fbx(filepath=str(root/e['fbx']))
        objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];mn,mx=L.bbox_blender(objs)
        check(abs(mn.z)<.002 and abs(mn.x+mx.x)<.002 and abs(mn.y+mx.y)<.002,e['name']+' measured base-centre pivot')
        a=e['pivot_position_arch_local']
        for o in objs:o.location=Vector((a[0],-a[2],a[1]))
        bpy.context.view_layer.update()
        check(clearance(objs,(-11,-30,0),(11,8,18)),e['name']+' no triangle in six-stud expanded corridor box')
        d=distance(objs,(-5,-24,0),(5,2,12));mins[e['name']]=round(d,5)
        check(d>=5.999,e['name']+' minimum triangle-to-corridor Euclidean distance '+format(d,'.5f')+' studs')
        check(e['triangles']<20000,e['name']+' strict <20k triangle cap')
        check(2<=len(e['collision'])<=6 and all(len(b['center'])==len(b['size'])==3 and all(v>0 for v in b['size']) for b in e['collision']),e['name']+' 2-6 simple solid collision boxes')
        check(not e['can_collide'] and not e['foliage_can_collide'] and not e['crystals_can_collide'],e['name']+' decoration/foliage/crystal MeshParts noncolliding')
        check('BW_Atlas' in e['materials'] and 'BW_Backdrop' in e['materials'],e['name']+' shared atlas + opaque vertex-colour material')
        check(not any(o.type=='LIGHT' for o in bpy.context.scene.objects),e['name']+' no real lights')
        for b in e['collision']:
            c=[b['center'][k]+a[k] for k in range(3)];s=b['size'];lo=[c[k]-s[k]/2 for k in range(3)];hi=[c[k]+s[k]/2 for k in range(3)]
            check(any(hi[k]<[-11,0,-8][k] or lo[k]>[11,18,30][k] for k in range(3)),e['name']+' collision '+b['name']+' outside expanded corridor')
    for e in man['props']:
        if not e.get('anchor_position_arch_local'):continue
        L.reset_scene();bpy.ops.import_scene.fbx(filepath=str(root/e['fbx']))
        objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];a=e['anchor_position_arch_local']
        for o in objs:o.location=(a[0],-a[2],a[1])
        bpy.context.view_layer.update()
        check(clearance(objs,(-4.999,-24,.001),(4.999,2,11.999)),e['name']+' lantern extended-opening triangle clearance')
        check(clearance(objs,(-4.999,-1.499,.001),(4.999,1.499,9.999)),e['name']+' lantern trigger clearance')
        mn,mx=L.bbox_blender(objs)
        check(mn.z>=12 or mx.x<=-6 or mn.x>=6,e['name']+' low lanterns at least 1 stud outside corridor X')
    backup=root/'_backup_pass3'
    immutable=[e for e in man['props'] if not e['name'].startswith('bw_scn_') and not e['name'].startswith('bw_arch_lantern_grove_lantern_')]
    for e in immutable:
        f=root/e['fbx'];old=backup/e['fbx']
        check(old.exists() and hashlib.sha256(f.read_bytes()).digest()==hashlib.sha256(old.read_bytes()).digest(),e['name']+' FBX byte-identical to pass3')
    old=json.loads((backup/'manifest.json').read_text())
    for c in ('lantern_grove','sugarloaf_canyon','aurora_archipelago'):
        e=next(q for q in man['props'] if q['name']=='bw_arch_'+c);b=next(q for q in old['props'] if q['name']==e['name'])
        for k in ('collision','portal_trigger','portal_surface'):
            check(e[k]==b[k],c+' unchanged '+k)
    (root/'_src'/'clearance_pass4.json').write_text(json.dumps(mins,indent=2))
