import sys,json,math,datetime
sys.dont_write_bytecode=True
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
SRC=Path(__file__).resolve().parent; BASE=SRC.parents[1]; OUT=SRC.parent
sys.path.insert(0,str(BASE/'lib'));sys.path.insert(0,str(SRC))
import sclib as L
# textures.py is the reference texture generator; use its existing PNG outputs.
from registry_movers import REG,HOLES,motion
L.lglib.TEX_DIR=str(BASE/'textures')
L.MATS.update(LipRed=('#B83A35','SmoothPlastic',0,0,'warning red'),LipCream=('#FFF0C9','SmoothPlastic',0,0,'warning cream'))
L.MATS.update(Brass=('#C9973A','Metal',0,0,'brass'),SignalRed=('#FF3028','Neon',3,0,'toggle red'),SignalGreen=('#63FF67','Neon',3,0,'toggle green'))
L.MATS.update(Slate=('#5E6670','Slate',0,0,'sundial shadow-arm slate'),Mist=('#F6D3E1','SmoothPlastic',0,0.5,'H7 gap mist: Transparency 0.5, CastShadow off, CanCollide off (optional ForceField/Neon variant at Transparency 0.85)'),
    PadLime=('#D8FF6A','Neon',0.8,0,'player teleport pad frame, sour-apple lime (course.md)'),PadCore=('#2F5D3A','SmoothPlastic',0,0,'player teleport pad centre'))
import gen_pass4 as G4
import gen_pass5 as G5
L.MATS.update(Collider=('#FF00FF','SmoothPlastic',0,1,'COLLISION-ONLY: Transparency 1, CanCollide true, CastShadow false, CanQuery/CanTouch true'),
    RespawnGlow=('#7FE7FF','Neon',1.0,0,'island respawn marker glow (ball respawn point; distinct from the lime player pads)'))
def can_collide(e):return bool(e.get('collision_only') or e.get('collidable'))
class RecordedPB(L.PB):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.components=[]
    def add(self,mat,tbm,matrix=None,smooth=False,free=True):
        from mathutils import Matrix
        mtx=self.frame@(matrix or Matrix.Identity(4));pts=[mtx@v.co for v in tbm.verts]
        lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
        comp=dict(material=mat,center=[(lo[0]+hi[0])/2,(lo[2]+hi[2])/2,-(lo[1]+hi[1])/2],size=[hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]])
        # Pass 4: exact convex part (Roblox pivot-relative verts, face planes n.x<=d, edge directions) for SAT fitcheck.
        c=tbm.copy();bmesh.ops.transform(c,matrix=mtx,verts=c.verts);c.normal_update()
        rb=lambda v:[float(v.x),float(v.z),float(-v.y)]
        planes={};edges={}
        cen=[sum(rb(v.co)[i] for v in c.verts)/len(c.verts) for i in range(3)]
        for f in c.faces:
            if f.normal.length<1e-9:continue
            n=rb(f.normal.normalized());d=sum(a*b for a,b in zip(n,rb(f.verts[0].co)))
            if sum(a*b for a,b in zip(n,cen))>d:n=[-x for x in n];d=-d  # outward for a convex part
            key=tuple(round(x,6) for x in n)
            planes[key]=n+[max(d,planes[key][3]) if key in planes else d]
        for ed in c.edges:
            v=ed.verts[1].co-ed.verts[0].co
            if v.length<1e-9:continue
            v=rb(v.normalized());k=max(range(3),key=lambda i:abs(v[i]))
            if v[k]<0:v=[-x for x in v]
            edges[tuple(round(x,5) for x in v)]=v
        comp.update(verts=[rb(v.co) for v in c.verts],planes=list(planes.values()),edges=list(edges.values()))
        c.free();self.components.append(comp)
        return super().add(mat,tbm,matrix,smooth,free)
def log(s):
    with (SRC/'PROGRESS.md').open('a') as f:f.write('\n- '+datetime.datetime.now().astimezone().isoformat()+' '+s+'\n')
def box(p,m,c,s,bevel=0):p.box(m,(s[0],s[2],s[1]),loc=L.R(*c),bevel=bevel)
def wheel(p,x,y,z):
    p.cyl('Iron',.65,.65,.14,24,loc=L.R(x,y,z),rot=(90,0,0))
    p.cyl('Brass',.18,.18,.22,16,loc=L.R(x,y,z-.1),rot=(90,0,0))
    for a in range(0,360,60):
        r=math.radians(a);p.cyl('Brass',.055,.055,.12,8,loc=L.R(x+.48*math.cos(r),y+.48*math.sin(r),z-.1),rot=(90,0,0))
def board(p):
    # Exact union of source boxes, including 45 degree diamond ends.
    box(p,'Timber',(0,.5,0),(6.4,1,.636))
    for x in (-3.2,3.2):p.box('Timber',(.4243,.4243,1),loc=L.R(x,.5,0),rot=(0,0,45))
    for i in range(10):
        for z in (-.309,.309):box(p,'PepRed' if i%2==0 else 'MintWhite',(-2.925+i*.65,.5,z),(.65,.9,.018))
    for x in (-2.4,2.4):box(p,'Iron',(x,.5,.31),(.13,.92,.02))
def generate(e):
    p=RecordedPB(e['id']);n=e['id']
    if n=='h06_sluice_gate':
        p.frame.translation.z=.02
        board(p)
    elif n=='h06_sluice_frame':
        for x in (-12,3.98):
            box(p,'Timber',(x,5.8 if x>0 else 4.5,0),(.6,6.4 if x>0 else 9,.6),.025)
        box(p,'Timber',(-4.01,8.3,0),(16.58,.6,1.3),.04)
        wheel(p,-4.6,3.3,-.65)
        for z in (-.62,.62):box(p,'Iron',(-7,2.75,z),(7,.15,.14))
    elif n=='h11_lock_gate':
        box(p,'Timber',(0,.6,0),(3.6,1.2,.5))
        for i in range(6):
            for z in (-.241,.241):box(p,'PepRed' if i%2==0 else 'MintWhite',(-1.5+i*.6,.6,z),(.6,1.08,.018))
        for x in (-1.3,1.3):box(p,'Iron',(x,.6,.24),(.12,1.08,.02))
    elif n=='h11_lock_lift':
        box(p,'Timber',(0,-.075,1.675),(2.84,.15,2.99))
        for i in range(6):
            lo=-1.6+i*.6;hi=min(1.6,lo+.6)
            for z in (.09,3.26):box(p,'LipRed' if i%2==0 else 'LipCream',((lo+hi)/2,-.075,z),(hi-lo,.15,.18))
        for x in (-1.51,1.51):
            for i in range(6):
                lo=.18+i*.6;hi=min(3.17,lo+.6)
                if hi>lo:box(p,'LipRed' if i%2==0 else 'LipCream',(x,-.075,(lo+hi)/2),(.18,.15,hi-lo))
    elif n=='h11_quay_lip':
        prm=e['params'];w,d,h=prm['width'],prm['depth'],prm['height']
        for i in range(6):
            box(p,'LipRed' if i%2==0 else 'LipCream',(-w/2+.3+i*.6,h/2,0),(.6,h,d))
    elif n in G5.GEN:
        G5.GEN[n](p)
    elif n in G4.GEN:
        G4.GEN[n](p)
    else:
        for x in (-4.8,4.8):
            box(p,'MintWhite',(x,2,0),(.4,4,2.8),.03)
            for z in (-1.1,1.1):
                p.cyl('Brass',.14,.14,.55,12,loc=L.R(x,4.275,z))
                p.cyl('Brass',.22,.22,.08,12,loc=L.R(x,4.55,z))
        for x in (-4.8,4.8):
            box(p,'Timber',(x,1.25,0),(.4,2.5,.4),.03);wheel(p,x,1.7,-.25)
        # Slot cheeks, clear of both gate faces. No static red/cream bands.
        # p8: approach felt is a .4-thick slab (y -.4..0); cheek tops lowered to y -.5 to clear it.
        for z in (2.35,2.55):box(p,'Iron',(0,-1.0,z),(3.3,1.0,.08))
        box(p,'Iron',(0,5.9,-3.0),(.8,1.2,.3),.04)
        for y,m in ((6.18,'SignalRed'),(5.62,'SignalGreen')):p.sphere(m,.19,loc=L.R(0,y,-2.8),scale=(1,.45,1),segs=16,rings=8)
    (SRC/(e['id']+'_components.json')).write_text(json.dumps(p.components,indent=2))
    return L.finalize(p,bpy.context.scene.collection)
def camera(pos,target):
    c=bpy.data.objects.get('Camera')
    if not c:
        c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));bpy.context.scene.collection.objects.link(c)
    c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=42;bpy.context.scene.camera=c
def preview(e,root,obs,view,path):
    mn,mx=L.bbox_blender(obs);target=(mn+mx)*.5;span=max(mx-mn)
    camera((target.x+span*.95,target.y-span*1.6,5 if view=='eye' else target.z+span*.9),target)
    sc=bpy.context.scene;sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)
def world_xform(e,v,direction=False):
    if e.get('world'):return list(v)
    h=HOLES[e['hole']];a=math.radians(h['world_yaw']);x,y,z=v
    w=[x*math.cos(a)+z*math.sin(a),y,-x*math.sin(a)+z*math.cos(a)]
    return w if direction else [w[i]+h['world_offset'][i] for i in range(3)]
def main():
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    only=args[args.index('--only')+1].split(',') if '--only' in args else [e['id'] for e in REG]
    previews='--no-preview' not in args
    entries=json.loads((SRC/'movers_manifest.json').read_text())['movers']
    for e in [x for x in REG if x['id'] in only]:
        log('Building '+e['id']);bpy.ops.wm.read_factory_settings(use_empty=True);L.lglib._scratch=None
        root,obs=generate(e);sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.color_type='TEXTURE';sc.display.shading.light='STUDIO';sc.display.shading.show_cavity=True
        sc.render.resolution_x=800;sc.render.resolution_y=650;sc.render.resolution_percentage=100
        for o in obs:
            if o.data.materials[0].name=='Mist':
                m=o.data.materials[0];b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');b.inputs['Alpha'].default_value=0.5
                try:m.surface_render_method='BLENDED'
                except Exception:pass
                o.visible_shadow=False
        bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
        for o in obs:o.select_set(True);o['CanCollide']=can_collide(e)
        bpy.context.view_layer.objects.active=root
        fbx=OUT/'fbx'/(e['id']+'.fbx')
        bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,axis_forward='-Z',axis_up='Y',global_scale=1,path_mode='COPY',embed_textures=True,add_leaf_bones=False,bake_anim=False)
        meshes=[];triangles=[]
        for o in obs:
            o.data.calc_loop_triangles()
            for t in o.data.loop_triangles:
                triangles.append([[float(o.data.vertices[j].co.x),float(o.data.vertices[j].co.z),float(-o.data.vertices[j].co.y)] for j in t.vertices])
            meshes.append(dict(name=o.name,material=o.data.materials[0].name,tris=len(o.data.loop_triangles)))
        (SRC/(e['id']+'_triangles.json')).write_text(json.dumps(triangles))
        mn,mx=L.bbox_blender(obs)
        item=dict(e,fbx=str(fbx.relative_to(OUT)).replace(chr(92),'/'),world_pivot=world_xform(e,e['pivot']),meshes=meshes,tris=sum(x['tris'] for x in meshes),MeshParts=len(meshes),CanCollide=can_collide(e),bbox=L.to_roblox_bbox(mn,mx))
        item['bbox_format']='[size, center] in pivot-relative Roblox coordinates'
        item['holes']=[HOLES[e['hole']]['id']] if e['hole'] is not None else ['world']
        if e['hole'] is not None:item['hole_world']=dict(offset=HOLES[e['hole']]['world_offset'],yaw=HOLES[e['hole']]['world_yaw'])
        if 'axis' in e and e['hole'] is not None:item['world_axis']=world_xform(e,e['axis'],True)
        if 'instances' in e:item['instances']=[dict(i,world_pivot=world_xform(e,i['pivot'])) for i in e['instances']]
        item['materials']={m['material']:dict(color=L.MATS[m['material']][0],roblox_material=L.MATS[m['material']][1],emission=L.MATS[m['material']][2],transparency=L.MATS[m['material']][3],note=L.MATS[m['material']][4]) for m in meshes}
        if e['moving'] and e['id'] in ('h06_sluice_gate','h11_lock_gate'):item['motion']=next(m for m in HOLES[e['hole']]['moving_parts'] if m['id'] in ('sluice_gate','lock_gate'))
        mpid={'h11_lock_lift':'lock_lift_deck','h11_quay_lip':'quay_lip','h09_windpump_vanes':'windpump','h14_ore_bucket':'ore_bucket','h09_windpump_vanes_collision':'windpump','h14_ore_bucket_foot_collision':'ore_bucket','h17_shadow_arms':'shadow_arm'}.get(e['id'],'shadow_arm' if e['id'].startswith('h17_shadow_arm_head_') else None)
        if mpid:item['motion']=next(m for m in HOLES[e['hole']]['moving_parts'] if m['id']==mpid)
        if 'chamber' in e['id']:item['lights']=[dict(position=[0,5,-25.4],range=6,brightness=1,meshes=['SignalRed','SignalGreen'],rule='green while gate down; red otherwise')]
        entries=[x for x in entries if x['id']!=item['id']];entries.append(item)
        sc.world=bpy.data.worlds.new('PreviewWorld');sc.world.color=(.22,.18,.25)
        sc.display.shading.background_type='WORLD'
        # Preview-only five-stud reference capsule (saved in the .blend for renders), excluded from FBX and triangle cache.
        ref=L.PB('preview_capsule');ref.cyl('Brass',.3,.3,4.4,16,loc=(-4.8,-1.6,2.5))
        for z in (.3,4.7):ref.sphere('Brass',.3,loc=(-4.8,-1.6,z),segs=16,rings=8)
        _,refobs=L.finalize(ref,sc.collection)
        if previews:
            for view in ('eye','34'):preview(e,root,obs+refobs,view,OUT/'previews'/(e['id']+'_'+view+'.png'))
        bpy.ops.wm.save_as_mainfile(filepath=str(SRC/(e['id']+'.blend')))
    order=[e['id'] for e in REG]
    man=json.loads((SRC/'movers_manifest.json').read_text());man['movers']=sorted(entries,key=lambda x:order.index(x['id']) if x['id'] in order else 99)
    (SRC/'movers_manifest.json').write_text(json.dumps(man,indent=2));log('Built '+','.join(only)+': FBX, blend, components (convex parts), triangles')
if __name__=='__main__':main()
