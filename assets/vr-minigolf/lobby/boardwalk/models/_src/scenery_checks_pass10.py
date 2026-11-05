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
            check((not e['collision']) if e['name']=='bw_scn_aurora_crown' or 'sugarloaf_crystals_' in e['name'] else 2<=len(e['collision'])<=6,e['name']+' collision policy (pure crystal crown noncolliding)')
            check(('BW_Crown_Crystal' in e['materials']) if e['name']=='bw_scn_aurora_crown' else ('Glow_Crystal' in e['materials'] if 'sugarloaf_crystals_' in e['name'] else ('BW_Bark_VC' in e['materials'] and 'BW_Backdrop' in e['materials'] if 'trunk_' in e['name'] else 'BW_Rock_VC' in e['materials'] if 'aurora_rocks_' in e['name'] else 'BW_Atlas' in e['materials'] and 'BW_Backdrop' in e['materials'])),e['name']+' exact crown material / shared atlas and vertex colour')
            check(not e['can_collide'] and not e['foliage_can_collide'] and not e['crystals_can_collide'],e['name']+' decorative mesh collision off')
            for b in e['collision']:
                c=[b['center'][k]+a[k] for k in range(3)];lo=[c[k]-b['size'][k]/2 for k in range(3)];hi=[c[k]+b['size'][k]/2 for k in range(3)]
                for label,(zlo,zhi) in zones.items():
                    check(any(hi[k]<zlo[k] or lo[k]>zhi[k] for k in range(3)),e['name']+' collision '+b['name']+' outside '+label)
        check(not any(o.type=='LIGHT' for o in bpy.context.scene.objects),e['name']+' no real lights')
    backup=root/'_backup_pass9'
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
    check(0<crown['triangles']<20000,'Aurora exact supplied six-crystal triangle count '+str(crown['triangles']))
    check((root/'_src/pass10_geo.py').read_bytes()==(root.parent.parent.parent/'pass10_geo.py').read_bytes(),'supplied crown source byte-identical')
    L.reset_scene();bpy.ops.import_scene.fbx(filepath=str(root/crown['fbx']))
    actual=[o.matrix_world@v.co for o in bpy.context.scene.objects if o.type=='MESH' for v in o.data.vertices]
    import pass10_geo
    build_crown=pass10_geo.build_crown
    exact=build_crown('reference_only')
    expected=[v.co.copy() for v in exact.data.vertices]
    check(all(min((v-w).length for w in actual)<.002 for v in expected) and all(min((v-w).length for w in expected)<.002 for v in actual),'crown exported vertices exactly match build_crown; no crystal nudges')
    oldprops={e['name']:e for e in old['props']}
    measures={}
    for name in ('bw_scn_sugarloaf_tower_w','bw_scn_sugarloaf_tower_e','bw_scn_sugarloaf_crystals_w','bw_scn_sugarloaf_crystals_e','bw_scn_sugarloaf_lollipop_cactus'):
        e=next(q for q in man['props'] if q['name']==name)
        check(e['triangles']>0,name+' valid geometry count')
        check('crystals_' not in name or hashlib.sha256((root/e['fbx']).read_bytes()).digest()!=hashlib.sha256((backup/e['fbx']).read_bytes()).digest(),name+' candy geometry rebuilt / retained tower and cactus')
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
    measures['crown']={'tallest_tip_Z':max(v.z for v in actual),'triangles':crown['triangles'],'nudges':[]}
    check(abs(max(v.z for v in actual)-27)<.3,'crown tallest tip Z27 +/-0.3')
    (root/'_src'/'measure_pass10.json').write_text(json.dumps(measures,indent=2))
    (root/'_src'/'clearance_pass10.json').write_text(json.dumps(mins,indent=2))

    import pass10_geo as G
    from mathutils.kdtree import KDTree
    for e in man['props']:
        name=e['name']
        if name!='bw_scn_aurora_crown' and not any(x in name for x in ['sugarloaf_crystals_','trunk_','aurora_rocks_']):continue
        L.reset_scene();bpy.ops.import_scene.fbx(filepath=str(root/e['fbx']))
        a=e['pivot_position_arch_local'];offset=Vector((a[0],-a[2],a[1]))
        objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
        if 'trunk_' in name:objs=[o for o in objs if o.data.materials[0].name.startswith('BW_Bark_VC')]
        actual=[o.matrix_world@v.co+offset for o in objs for v in o.data.vertices]
        side=-1 if name.endswith('_w') else 1
        ref=G.build_crown('reference') if name=='bw_scn_aurora_crown' else G.build_twisted_trunk(side) if 'trunk_' in name else G.build_aurora_rocks(side) if 'aurora_rocks_' in name else G.build_sugarloaf_crystals(side)
        expected=[v.co.copy() for v in ref.data.vertices]
        def tree(vs):
            kd=KDTree(len(vs))
            for i,v in enumerate(vs):kd.insert(v,i)
            kd.balance();return kd
        at=tree(actual);et=tree(expected)
        check(all(at.find(v)[2]<.002 for v in expected) and all(et.find(v)[2]<.002 for v in actual),name+' exact supplied vertices both directions')
        check(sum(L.tri_count([o]) for o in objs)==L.tri_count([ref]),name+' exact supplied triangle count')
        check(all('Col' in o.data.color_attributes for o in objs),name+' Col vertex colors retained')

        def colored_corners(oo,off):
            result=[]
            for o in oo:
                ca=o.data.color_attributes['Col']
                for lp in o.data.loops:
                    v=o.matrix_world@o.data.vertices[lp.vertex_index].co+off
                    co=ca.data[lp.index].color_srgb
                    result.append(tuple(round(x,3) for x in v)+tuple(round(x,2) for x in co))
            return sorted(result)
        ac=colored_corners(objs,offset);ec=colored_corners([ref],Vector((0,0,0)))
        def by_color(corners):
            groups={}
            for c in corners:groups.setdefault(c[3:],[]).append(Vector(c[:3]))
            return groups
        ag=by_color(ac);eg=by_color(ec)
        check(ag.keys()==eg.keys() and all(len(ag[c])==len(eg[c]) and all(tree(ag[c]).find(v)[2]<.003 for v in eg[c]) for c in eg),name+' source Col corner colors within FBX precision')

        if name=='bw_scn_aurora_crown':check(all(not p.use_smooth for o in objs for p in o.data.polygons),name+' flat facet normals')
        if any(x in name for x in ['crystals_','aurora_rocks_']):check((root/e['fbx']).read_bytes()!=(backup/e['fbx']).read_bytes(),name+' replaced pass9 FBX')
    changed={e['name'] for e in man['props'] if any(x in e['name'] for x in ['sugarloaf_crystals_','aurora_rocks_'])}
    for e in man['props']:
        if e['name'] not in changed:check((root/e['fbx']).read_bytes()==(backup/e['fbx']).read_bytes(),e['name']+' immutable pass8 bytes including lanterns')

    # Retained pass8 canopy: identical topology, colors, and world-space vertex positions.
    for e in man['props']:
        if 'lantern_grove_trunk_' not in e['name']:continue
        samples=[]
        for entry,folder in [(e,root),(oldprops[e['name']],backup)]:
            L.reset_scene();bpy.ops.import_scene.fbx(filepath=str(folder/entry['fbx']))
            a=entry['pivot_position_arch_local'];off=Vector((a[0],-a[2],a[1]))
            oo=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials[0].name.startswith('BW_Backdrop')]
            vv=sorted(tuple(round(x,3) for x in (o.matrix_world@v.co+off)) for o in oo for v in o.data.vertices)
            cc=sorted(tuple(round(x,5) for x in c.color_srgb) for o in oo for c in o.data.color_attributes['Col'].data)
            samples.append((vv,cc,sum(L.tri_count([o]) for o in oo)))
        av,bv=samples[0][0],samples[1][0]
        check(samples[0][1:]==samples[1][1:] and len(av)==len(bv) and all(tree([Vector(x) for x in av]).find(Vector(v))[2]<.003 for v in bv),e['name']+' canopy vertices/colors/topology identical within FBX precision')

    for e in man['props']:
        if 'aurora_rocks_' not in e['name']:continue
        a=e['pivot_position_arch_local']
        for b in e['collision']:
            c=[a[k]+b['center'][k] for k in range(3)];lo=[c[k]-b['size'][k]/2 for k in range(3)];hi=[c[k]+b['size'][k]/2 for k in range(3)]
            check(any(hi[k]<[-7.6,0,.3][k] or lo[k]>[-5.4,3.2,2.3][k] for k in range(3)),e['name']+' collision clear snowpuff footprint')

    from mathutils.bvhtree import BVHTree
    contact=[]
    for e in man['props']:
        if 'lantern_grove_trunk_' not in e['name']:continue
        L.reset_scene();bpy.ops.import_scene.fbx(filepath=str(root/e['fbx']))
        a=e['pivot_position_arch_local'];off=Vector((a[0],-a[2],a[1]))
        oo=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials[0].name.startswith('BW_Backdrop')]
        for o in oo:
            for v in o.data.vertices:v.co=o.matrix_world@v.co+off
            from mathutils import Matrix
            o.matrix_world=Matrix.Identity(4)
        bpy.context.view_layer.update();surface=BVHTree.FromPolygons([oo[0].matrix_world@v.co for v in oo[0].data.vertices],[list(p.vertices) for p in oo[0].data.polygons])
        for q in man['props']:
            aa=q.get('anchor_position_arch_local')
            if not aa or not q['name'].startswith('bw_arch_lantern_grove_lantern_') or aa[0]*a[0]<0:continue
            anchor=Vector((aa[0],-aa[2],aa[1]));d=min(surface.find_nearest(anchor+Vector((0,0,-j*.005)))[3] for j in range(101))
            # Cord radius .15; cap has five sides. Check distance plus recorded anchor containment.
            inside=next(x['inside_canopy'] for x in json.loads((root/'_src/anchors_pass10.json').read_text()) if x['name']==q['name'])
            check(inside or d<.14,q['name']+' cord touches retained canopy; distance '+str(d))
            contact.append(dict(name=q['name'],anchor=aa,cord_surface_distance=d,anchor_inside_canopy=inside))
    (root/'_src/anchor_contact_pass10.json').write_text(json.dumps(contact,indent=2))
