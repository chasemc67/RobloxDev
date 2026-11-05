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
    zones={'A':([-5,0,-12],[5,12,4]),'B':([-11,0,4],[11,18,34]),'trigger':([-5,0,-1.5],[5,10,1.5])}
    for e in man['props']:
        if not (e['name'].startswith('bw_scn_') or e.get('anchor_position_arch_local')):continue
        L.reset_scene();bpy.ops.import_scene.fbx(filepath=str(root/e['fbx']))
        objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];mn,mx=L.bbox_blender(objs)
        scenery=e['name'].startswith('bw_scn_')
        if scenery and e['name']!='bw_scn_aurora_crown':check(abs(mn.z)<.002 and abs(mn.x+mx.x)<.002 and abs(mn.y+mx.y)<.002,e['name']+' base-centre pivot')
        a=e.get('pivot_position_arch_local',e.get('anchor_position_arch_local'))
        for o in objs:o.location=Vector((a[0],-a[2],a[1]))
        bpy.context.view_layer.update();mins[e['name']]={}
        for label,(lo,hi) in zones.items():
            mn=(lo[0],-hi[2],lo[1]);mx=(hi[0],-lo[2],hi[1])
            d=distance(objs,mn,mx);mins[e['name']][label]=round(d,5)
            check(d>.0001,e['name']+' no triangle in zone '+label+'; minimum distance '+format(d,'.5f'))
        check(e['triangles']<20000,e['name']+' strict <20k cap')
        if scenery:
            check((not e['collision']) if e['name']=='bw_scn_aurora_crown' else 2<=len(e['collision'])<=6,e['name']+' collision policy (pure crystal crown noncolliding)')
            check(('BW_Crown_Crystal' in e['materials']) if e['name']=='bw_scn_aurora_crown' else 'BW_Atlas' in e['materials'] and 'BW_Backdrop' in e['materials'],e['name']+' exact crown material / shared atlas and vertex colour')
            check(not e['can_collide'] and not e['foliage_can_collide'] and not e['crystals_can_collide'],e['name']+' decorative mesh collision off')
            for b in e['collision']:
                c=[b['center'][k]+a[k] for k in range(3)];lo=[c[k]-b['size'][k]/2 for k in range(3)];hi=[c[k]+b['size'][k]/2 for k in range(3)]
                for label,(zlo,zhi) in zones.items():
                    check(any(hi[k]<zlo[k] or lo[k]>zhi[k] for k in range(3)),e['name']+' collision '+b['name']+' outside '+label)
        check(not any(o.type=='LIGHT' for o in bpy.context.scene.objects),e['name']+' no real lights')
    backup=root/'_backup_pass6'
    for e in man['props']:
        if e['name'].startswith('bw_scn_') or e['name'].startswith('bw_arch_lantern_grove_lantern_'):continue
        f=root/e['fbx'];old=backup/e['fbx']
        check(old.exists() and hashlib.sha256(f.read_bytes()).digest()==hashlib.sha256(old.read_bytes()).digest(),e['name']+' FBX unchanged from pass5')
    old=json.loads((backup/'manifest.json').read_text())
    for c in ('lantern_grove','sugarloaf_canyon','aurora_archipelago'):
        e=next(q for q in man['props'] if q['name']=='bw_arch_'+c);b=next(q for q in old['props'] if q['name']==e['name'])
        for k in ('collision','portal_trigger','portal_surface'):check(e[k]==b[k],c+' unchanged '+k)
    counts={e['name']:e['triangles'] for e in man['props']}
    total=sum(counts[i['asset']] for i in man['instances'])
    check(total==man['totals']['tris_total'] and total<120000,'placed lobby total '+str(total)+' <120000 from manifest instances')
    check(all(e['triangles']<20000 for e in man['props']),'all individual files strict <20k')
    crown=next(e for e in man['props'] if e['name']=='bw_scn_aurora_crown')
    check('Glow_Tips' in crown['materials'],'Aurora separate Glow_Tips material')
    check(crown['triangles']==276,'Aurora exact supplied six-crystal triangle count '+str(crown['triangles']))
    check((root/'_src/aurora_crown_explicit.py').read_bytes()==(root.parent.parent.parent/'aurora_crown_explicit.py').read_bytes(),'supplied crown source byte-identical')
    L.reset_scene();bpy.ops.import_scene.fbx(filepath=str(root/crown['fbx']))
    actual=[o.matrix_world@v.co for o in bpy.context.scene.objects if o.type=='MESH' for v in o.data.vertices]
    from aurora_crown_explicit import build_crown
    exact=build_crown('reference_only')
    expected=[v.co.copy() for v in exact.data.vertices]
    check(all(min((v-w).length for w in actual)<.002 for v in expected) and all(min((v-w).length for w in expected)<.002 for v in actual),'crown exported vertices exactly match build_crown; no crystal nudges')
    oldprops={e['name']:e for e in old['props']}
    measures={}
    for name in ('bw_scn_sugarloaf_tower_w','bw_scn_sugarloaf_tower_e','bw_scn_sugarloaf_crystals_w','bw_scn_sugarloaf_crystals_e','bw_scn_sugarloaf_lollipop_cactus'):
        e=next(q for q in man['props'] if q['name']==name)
        check(e['triangles']!=oldprops[name]['triangles'] or 'crystals_' in name,name+' revised geometry count/hash')
        check(hashlib.sha256((root/e['fbx']).read_bytes()).digest()!=hashlib.sha256((backup/e['fbx']).read_bytes()).digest(),name+' SHA256 changed from pass5')
        if 'tower' in name:
            import math
            L.reset_scene();bpy.ops.import_scene.fbx(filepath=str(root/e['fbx']))
            a=e['pivot_position_arch_local'];vs=[o.matrix_world@v.co+Vector((a[0],-a[2],a[1])) for o in bpy.context.scene.objects if o.type=='MESH' for v in o.data.vertices]
            def centre(lo,hi):
                pts=[v for v in vs if lo<=v.z<=hi]
                return Vector(tuple((min(v[k] for v in pts)+max(v[k] for v in pts))/2 for k in range(3)))
            base=centre(.2,1.4);top=centre(25.8,27.7)
            angle=math.degrees(math.atan2(abs(top.x-base.x),top.z-base.z))
            measures[name]={'base_centre':[base.x,base.z,-base.y],'top_centre':[top.x,top.z,-top.y],'lean_degrees':angle}
            check(8<=angle<=12 and abs(top.x)<abs(base.x),name+' measured inward lean '+str(angle))
            check(26<=max(v.z for v in vs)<=28,name+' approximately 27 tall')
        elif 'cactus' in name:
            original=json.loads((root/'_backup_pass5/manifest.json').read_text());original=next(q for q in original['props'] if q['name']==name)
            ratio=e['bbox_size_studs'][1]/original['bbox_size_studs'][1]
            measures[name]={'height_ratio_pass5':ratio}
            check(1.4<=ratio<=1.6,name+' 1.5x original height '+str(ratio))
    (root/'_src'/'measure_pass7.json').write_text(json.dumps(measures,indent=2))
    (root/'_src'/'clearance_pass7.json').write_text(json.dumps(mins,indent=2))
