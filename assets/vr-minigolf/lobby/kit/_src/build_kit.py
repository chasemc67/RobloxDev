import bpy,sys,os,json,shutil
SRC=os.path.dirname(__file__);ROOT=os.path.dirname(SRC)
BOARD=os.path.abspath(os.path.join(ROOT,'../boardwalk/models/_src'));sys.path.insert(0,BOARD);sys.path.insert(0,SRC)
import bwlib as L
import registry
import props_kit
for folder in ('fbx','textures','previews'):os.makedirs(os.path.join(ROOT,folder),exist_ok=True)
shutil.copyfile(L.ATLAS_PATH,os.path.join(ROOT,'textures','bw_atlas_1024.png'))
entries=[]
for p in list(registry.PROPS):
    if not p['name'].startswith('kit_'):continue
    sc=L.reset_scene();col=bpy.data.collections.new(p['name']);sc.collection.children.link(col)
    pb=L.PB(p['name']);p['fn'](pb);objs=pb.finalize(col)
    offset=L.recenter_base(objs) if p['pivot']=='base' else (0,0,0)
    mn,mx=L.bbox_blender(objs);size,center=L.to_roblox_bbox(mn,mx)
    path=os.path.join(ROOT,'fbx',p['name']+'.fbx');L.export_fbx(objs,path)
    e=dict(name=p['name'],fbx='fbx/'+p['name']+'.fbx',bbox_size_studs=list(size),bbox_center_from_pivot=list(center),triangles=L.tri_count(objs),tris_max=p['tris_max'],materials=sorted({m.name for o in objs for m in o.data.materials}),pivot='top centre' if p['pivot']=='top' else 'shared local origin' if p['pivot']=='local' else 'base centre',front=p['front'],collision=[],can_collide=False,notes=p['notes'],motion=p['motion'])
    e['parts']=[dict(mesh=o.name,material=o.data.materials[0].name,triangles=L.tri_count([o]),color=o.data.materials[0].get('bw_hex'),roblox_material='Neon' if o.data.materials[0].name=='BW_Neon' else 'SmoothPlastic') for o in objs]
    if p['name']=='kit_stringlight_pole':e['hook_positions']=[[-.75,9,0],[.75,9,0]]
    if p['name']=='kit_banner_pole':e['cloth_attach']=[0,9,.3]
    if p['name'].startswith('kit_string_lights_span_'):
        span=int(p['name'].rsplit('_',1)[1]);e['hook_positions']=[[-span/2,2.25+offset[2],0],[span/2,2.25+offset[2],0]]
    if p['name']=='kit_flag_pennant_string':e['hook_positions']=[[-5,1.8+offset[2],0],[5,1.8+offset[2],0]]
    if p['name'].startswith('kit_planter_'):e['filler_attach']=[0,1.85,0]
    if p['name']=='kit_leaderboard_frame':e['panel_faces']=[dict(asset='kit_leaderboard_panel_'+str(i+1),center=[x,5,-.65],width=3.4,height=5.6,normal=[0,0,-1]) for i,x in enumerate((-4.3,0,4.3))]
    entries.append(e);L.log('kit build '+p['name']+' tris '+str(e['triangles']))
json.dump(dict(units='1 BU = 1 stud',axes='X east, Y up, front -Z; FBX -Z forward Y up, scale 1, textures embedded',materials={'BW_Atlas':'textures/bw_atlas_1024.png','BW_Neon':'Roblox Neon; preserve exported base colour','BW_Backdrop':'vertex colours Col'},props=entries),open(os.path.join(ROOT,'manifest.json'),'w'),indent=2)
assert all(e['triangles']<20000 for e in entries)
