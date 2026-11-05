# box: /workspace/.geo/bin/python make_manifest.py -> ../manifest.json (reads work/box_report.json, work/overlay.json, PC previews dump.json)
import json,os,math
H=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
r=json.load(open(f'{H}/work/box_report.json'));ov=json.load(open(f'{H}/work/overlay.json'))
dp=f'{H}/previews_cave_v1/dump.json';dump=json.load(open(dp)) if os.path.exists(dp) else {}
C=ov['cave_centre']
KIND={'cave_cliff_lower':'lower rock mass (y 0..64): basalt-style prism columns, boulders at the foot, tunnel + arch voussoirs',
 'cave_cliff_upper':'upper rock tiers (y 28..149) incl. summit; arch hood over the cave mouth',
 'cave_stairs':'stone stair flight from the mouth floor (y 28) down to the front (z +70), rails + torches',
 'cave_water':'west-flank waterfall sheet + pool surface (swap to Neon / semi-transparent SmoothPlastic; Transparency in Studio)',
 'cave_glow':'amber interior glow panels/lanterns inside the tunnel (swap to Neon + PointLight)',
 'cave_foliage':'palms, vines, moss/bushes (separate so Studio can set Plastic / transparency / CanCollide=false)'}
parts={};allmin=[1e9]*3;allmax=[-1e9]*3
for k,v in r.items():
    if not k.startswith('cave_'):continue
    b=v['bbox'];allmin=[min(a,c) for a,c in zip(allmin,b['min'])];allmax=[max(a,c) for a,c in zip(allmax,b['max'])]
    d=dict(fbx=f'{k}.fbx',kind=KIND[k],tris=v['tris'],size_studs_xyz=[round(b['max'][i]-b['min'][i],2) for i in range(3)],bbox=b,pivot=[0,0,0])
    if k in dump:d['tris_in_fbx_blender_import']=dump[k]['tris']
    parts[k]=d
# pad clearance: distance from each pad's art-clear rectangle to the mesh footprint (axis-aligned, world)
fx0,fx1=C[0]+allmin[0],C[0]+allmax[0];fz0,fz1=C[2]+allmin[2],C[2]+allmax[2]
def rect(p):
    x,y,z=p['pos'];t=math.radians(p['yaw']);X=(math.cos(t),-math.sin(t));Z=(math.sin(t),math.cos(t));a,b=p['clear'][0]/2,p['clear'][1]/2
    return [(x+sx*a*X[0]+sz*b*Z[0],z+sx*a*X[1]+sz*b*Z[1]) for sx,sz in((1,1),(1,-1),(-1,-1),(-1,1))]
def gap(poly):
    # approximate: min over dense samples of polygon boundary + interior of distance to axis-aligned rect
    import numpy as np
    (xa,za),(xb,zb),(xc,zc),(xd,zd)=poly;best=1e9;ov_=False
    for u in np.linspace(0,1,81):
        for v in np.linspace(0,1,81):
            x=xa+(xb-xa)*u+(xd-xa)*v;z=za+(zb-za)*u+(zd-za)*v
            dx=max(fx0-x,0,x-fx1);dz=max(fz0-z,0,z-fz1);best=min(best,math.hypot(dx,dz))
    return round(best,2)
clear={('pad%d'%p['n']):dict(pos=p['pos'],art_clear_gap_to_mesh_footprint_studs=gap(rect(p))) for p in ov['pads']}
man=dict(version='cave_v1',look='B Golden Hour Hideaway',units='studs (1 stud = 1 Blender unit, FBX exported 1:1)',
 frame='Roblox frame: +Y up, FRONT (cave mouth, stair flight, pool) = +Z (south), west flank (waterfall + pool) = -X. Origin = footprint centre at the base (y=0 is the rock base). Place all six FBXs at the same origin with identity rotation (yaw 0).',
 world_placement=dict(origin_world=C,yaw_deg=0,source='placements.json cave footprint (centre 563.5, 66, -606.5; 240 x 140; front faces +Z)',
   note='base y=0 maps to world y=66. The sheet terrain under it is not flat (see terrain_notes); sink/bury the base into the hill as needed.'),
 size=dict(rock_bbox_local=dict(min=allmin,max=allmax),width=round(allmax[0]-allmin[0],1),height=round(allmax[1]-allmin[1],1),depth=round(allmax[2]-allmin[2],1),
   target='about 240 x 150 x 140 (placements footprint x +-120, z +-70, height 150)',
   note='rock mass (lower+upper) stays inside x +-119, z +-70.2, y -0.7..149; foliage tops 146.7; stairs front edge z=70'),
 mouth=dict(centre_x_local=20,floor_y_local=28,width=40,height_arch_apex=60,floor_world_y=94,depth_z_local=[-12,34],note='mouth centre x local +20 = world 583.5 (placements centreX); tunnel interior is an open void: the glow part sits inside it. Interior is a short dead-end tunnel (back wall at z=-12), not a playable cave.'),
 waterfall=dict(x_local=-80,width=13,top_y_local=103,bottom_y_local=48.4,world_x=C[0]-80),
 pool=dict(centre_local=[-80,48.4,44],radius=19,surface_y_local=48.4,note='pool is inside the footprint, in front of the west flank (placements pool centre was 34 studs outside the face; adjust the course water if needed)'),
 stairs=dict(x_local=[0,40],z_local=[29.6,70],floor_top_y_local=28,front_y_local=10,steps=20,note='decorative stair flight; mouth floor y local 28 = world 94'),
 pad_clearance=dict(pads_checked=[15,16,17,18],art_clear=clear,rule='art-clear 54x84 rectangles vs the mesh x/z bounding footprint (studs); footprint front edge world z %.1f, x %.1f..%.1f'%(fz1,fx0,fx1)),
 not_a_gameplay_surface='Scenery only. No flat ledges, no pads, no putting surface, nothing meant to be walked on; every part should be CanCollide=false except optionally an invisible blocker the course builder adds. Stairs and tunnel are decorative.',
 parts=parts,generator=['src/wreck_lib.py','src/gen_cave.py','src/build_cave.py','src/render_cave.py','src/make_manifest.py','src/box_preview.py','src/prev_box.py'],
 previews='previews_cave_v1/',
 terrain_notes=['Heightmap terrain under the footprint is lower than y=66 at the back and flanks (base floats up to ~60 studs above ground there) and about 96-108 at the mouth/stairs (above the mouth floor y=94). Fix by sinking/burying the base or filling terrain; the mesh cannot adapt.'],
 deviations=['No pad ledges in the mesh (pads are never in art meshes).','Pool is a tub inside the footprint at local (-80,48.4,44), not 34 studs outside the face.','Stair rise is 18 studs (y 10 -> 28) at the front, not a full ground-to-mouth ramp.','Rock is stylized hex/pentagon prism columns (basalt look) rather than smooth boulders; sheet palette kept.','Foliage tops 146.7 and some palm fronds 1-3 studs inside the footprint edge.'],
 max_tris_per_mesh=max(v['tris'] for v in parts.values()),under_20k=all(v['tris']<20000 for v in parts.values()))
json.dump(man,open(f'{H}/manifest.json','w'),indent=1);print('ok',man['size'],clear)
