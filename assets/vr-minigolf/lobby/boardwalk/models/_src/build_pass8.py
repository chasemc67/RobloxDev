import sys,os,json
from pathlib import Path
SRC=Path(__file__).parent;sys.path.insert(0,str(SRC))
import registry,bwlib as L
L.PROGRESS=str(SRC/'PROGRESS_pass8.md')
registry.load_all()
import props_scenery as S
import props_arches as A
import build_all
# Update closure default anchors without altering any arch geometry generator.
names=S.SCENERY+['bw_arch_lantern_grove_lantern_'+str(i).zfill(2) for i in range(1,7)]
for i in range(6):
    p=registry.by_name(names[len(S.SCENERY)+i]);p['fn'].__defaults__=('lantern_grove',S.ANCHORS[i])
build_all.build({n for n in names if 'lantern_grove' in n or 'aurora_rocks' in n})
exec((SRC/'export_candy_pass8.py').read_text())
# Wire the supplied build_crown result into the existing FBX/manifest path only.
import bpy,bmesh
L.reset_scene();ob=S.crown(None)
bpy.context.view_layer.objects.active=ob;ob.select_set(True)
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.separate(type='MATERIAL');bpy.ops.object.mode_set(mode='OBJECT')
objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
parts=[]
for o in objs:
    mat=o.data.materials[0];o.name='bw_scn_aurora_crown__'+mat.name
    mn,mx=L.bbox_blender([o]);sz,ct=L.to_roblox_bbox(mn,mx)
    parts.append(dict(mesh=o.name,material=mat.name,tris=L.tri_count([o]),color='#9FE6F2' if mat.name=='Glow_Tips' else None,roblox_material='Neon' if mat.name=='Glow_Tips' else 'SmoothPlastic',size=build_all.r3(sz),center_from_pivot=build_all.r3(ct)))
L.export_fbx(objs,str(SRC.parent/'fbx/bw_scn_aurora_crown.fbx'))
mn,mx=L.bbox_blender(objs);sz,ct=L.to_roblox_bbox(mn,mx)
from aurora_crown_v2 import CRYSTALS
ce=dict(name='bw_scn_aurora_crown',group='scenery',fbx='fbx/bw_scn_aurora_crown.fbx',front='south (+Z)',notes='Supplied v2 six-crystal crown; arch-base pivot required by source; collision off.',pivot='shared arch base centre (0,0,0), exact source',pivot_position_arch_local=[0,0,0],pivot_recenter_applied=[0,0,0],bbox_size_studs=build_all.r3(sz),bbox_center_from_pivot=build_all.r3(ct),bbox_min_roblox=build_all.r3([mn.x,mn.z,-mx.y]),bbox_max_roblox=build_all.r3([mx.x,mx.z,-mn.y]),target_size_studs=[0,0,0],triangles=L.tri_count(objs),tris_max=19999,materials=sorted({q['material'] for q in parts}),parts=parts,collision=[],motion=None,scalable=None,can_collide=False,foliage_can_collide=False,crystals_can_collide=False,course='aurora_archipelago',decoration_only=True,main_crystal_count=6,crystal_table=CRYSTALS,vertex_colour_attribute='Col',gradient_hex=['#7A4FD0','#8FE3EE'],preview_glow_strength=1.5)
(SRC/'manifest_parts/bw_scn_aurora_crown.json').write_text(json.dumps(ce,indent=1))
for c in ('lantern_grove','sugarloaf_canyon','aurora_archipelago'):
    f=SRC/'manifest_parts'/('bw_arch_'+c+'.json')
    old=json.loads((SRC.parent/'_backup_pass7'/'manifest.json').read_text())
    e=next(q for q in old['props'] if q['name']=='bw_arch_'+c)
    if c=='lantern_grove':
        e['attach_points']['lantern_cord_anchors']=S.ANCHORS
        for q,a in zip(e['moving_parts'],S.ANCHORS):q['anchor_position_arch_local']=a
    e['scenery_assets']=[json.loads((SRC/'manifest_parts'/(n+'.json')).read_text())['name'] for n in S.SCENERY if json.loads((SRC/'manifest_parts'/(n+'.json')).read_text())['course']==c]
    if c=='aurora_archipelago':e['snowpuff_position_arch_local']=[-6.5,0,1.25];e['snowpuff_asset_origin_arch_local']=[0,0,0]
    f.write_text(json.dumps(e,indent=1))
cf=SRC/'manifest_parts'/'bw_scn_aurora_crown.json'
ce=json.loads(cf.read_text());ce['neon_material']='Glow_Tips'
for part in ce['parts']:
    if part['material']=='Glow_Tips':part.update(color='#9FE6F2',roblox_material='Neon')
cf.write_text(json.dumps(ce,indent=1))
man=build_all.assemble()
man['lobby']='Golden Hour Boardwalk - pass8 standalone portal scenery'
for parent in list(man['instances']):
    if parent['asset'] not in ['bw_arch_'+c for c in ('lantern_grove','sugarloaf_canyon','aurora_archipelago')]:continue
    c=parent['asset'].removeprefix('bw_arch_')
    for e in man['props']:
        if e.get('course')!=c:continue
        a=e['pivot_position_arch_local']
        man['instances'].append(dict(id=parent['id']+'__'+e['name'],asset=e['name'],position=[round(parent['position'][k]+a[k],4) for k in range(3)],yaw=parent['yaw'],parent_id=parent['id'],solid=False))
for e in man['props']:
    e['builder_count']=sum(i['asset']==e['name'] for i in man['instances']);e['tris_x_count']=e['triangles']*e['builder_count']
man['totals'].update(instances=len(man['instances']),tris_total=sum(e['tris_x_count'] for e in man['props']))
man['pass8_clearance']={'zone_A':{'min':[-5,0,-12],'max':[5,12,4]},'zone_B':{'min':[-11,0,4],'max':[11,18,34]},'above_y18_allowed':True}
man['materials']['Glow_Crystal']={'Material':'Neon','vertex_colour_attribute':'Col','colors':['#F59AC8','#FFF1A8']}
man['materials']['Glow_Tips']={'roblox_material':'Neon','color':'#9FE6F2','note':'Aurora crown tips, separate material mesh'}
for e in man['props']:
    if e['name']=='bw_scn_aurora_crown':
        e['neon_material']='Glow_Tips'
        for p in e['parts']:
            if p['material']=='Glow_Tips':p.update(color='#9FE6F2',roblox_material='Neon')
(SRC.parent/'manifest.json').write_text(json.dumps(man,indent=1))
L.log('Pass7 built integrated scenery and six relocated hinge-pivot lanterns; manifest assembled.')
