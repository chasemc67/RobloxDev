# box: /workspace/.geo/bin/python make_manifest.py -> ../manifest.json (reads work/box_report.json, work/overlay.json, PC previews dump.json)
import json,os,math
H=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
r=json.load(open(f'{H}/work/box_report.json'));ov=json.load(open(f'{H}/work/overlay.json'))
dp=f'{H}/previews_cave_v2/dump.json';dump=json.load(open(dp)) if os.path.exists(dp) else {}
C=ov['cave_centre']
KIND={'cave_cliff_lower':'lower rock mass (y 0..64): chunky leaning rock slabs, foot boulders, tunnel floor/jambs/back wall, arch jambs',
 'cave_cliff_upper':'upper rock tiers (y 44..149) incl. the east summit; arch voussoirs + lintel over the mouth; waterfall backing wall',
 'cave_stairs':'stone stair flight from the mouth floor (y 28) down to the front (z +70), rails + torches',
 'cave_water':'wide white west-flank waterfall sheet (22 studs, white core) + foam + pool surface (swap to semi-transparent SmoothPlastic / Neon-ish white in Studio)',
 'cave_glow':'warm orange light cards + dim backdrop panels + floor glow set 55-64 studs deep at the back of the tunnel, plus the 6 stair lantern globes (swap to Neon + PointLight)',
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
man=dict(version='cave_v2',look='B Golden Hour Hideaway',units='studs (1 stud = 1 Blender unit, FBX exported 1:1)',
 frame='Roblox frame: +Y up, FRONT (cave mouth, stair flight, pool) = +Z (south), west flank (waterfall + pool) = -X. Origin = footprint centre at the base (y=0 is the rock base). Place all six FBXs at the same origin with identity rotation (yaw 0).',
 world_placement=dict(origin_world=C,yaw_deg=0,source='placements.json cave footprint (centre 563.5, 66, -606.5; 240 x 140; front faces +Z)',
   note='base y=0 maps to world y=66. The sheet terrain under it is not flat (see terrain_notes); sink/bury the base into the hill as needed.'),
 size=dict(rock_bbox_local=dict(min=allmin,max=allmax),width=round(allmax[0]-allmin[0],1),height=round(allmax[1]-allmin[1],1),depth=round(allmax[2]-allmin[2],1),
   target='about 240 x 150 x 140 (placements footprint x +-120, z +-70, height 150)',
   note='rock mass (lower+upper) stays inside x +-117, z +-70, y -0.5..149.4; foliage tops 142; stairs front edge z=70'),
 mouth=dict(centre_x_local=20,floor_y_local=28,width=60,height_arch_apex=54,spring_line_y_local=58,apex_y_local=82,floor_world_y=94,depth_z_local=[-30,34],was='40 wide x 36 tall in v1 (1.5x now)',note='mouth centre x local +20 = world 583.5 (placements centreX), floor y local 28 = world 94. Tunnel is a 64-stud-deep dead end (back wall z=-30); the warm glow is only at the back (z -29.7..-17), 55+ studs behind the mouth, as staggered light cards + a dim backdrop, not a slab over the mouth.'),
 glow=dict(kind='light cards (0.5 thick, staggered z -28.3..-23.1), 2 dim backdrop panels at z -29.55/-29.05, floor glow patches, 2 hanging globes at z -8',colours={'GlowDeep':[230,100,30],'GlowOrange':[255,140,40],'GlowHot':[255,176,70]},nearest_to_mouth_studs=64-17),
 waterfall=dict(x_local=-80,width=22,top_y_local=95.5,bottom_y_local=48.4,front_z_local=17,world_x=C[0]-80,was='13 wide, amber-blue in v1',colour='WhiteWater (240,250,252) centre 52% of width, WaterLt (170,224,236) edges, foam streaks and base splash'),
 pool=dict(centre_local=[-80,48.4,36],radius=19,surface_y_local=48.4,note='pool is inside the footprint, in front of the west flank, directly at the base of the waterfall (placements pool centre was 34 studs outside the face; adjust the course water if needed)'),
 stairs=dict(x_local=[0,40],z_local=[29.6,70],floor_top_y_local=28,front_y_local=10,steps=20,note='decorative stair flight 40 wide (v1 30); mouth floor y local 28 = world 94'),
 colour=dict(rock_base=[95,85,105],sandy_tops=[190,150,110],rule='top faces whose normal is within ~57 deg of the sun (-0.45,0.75,0.50 normalised: from the west-south-west, front) are Sandy (190,150,110) / SandyDk (171,133,98); the rest of the tops are slate-light / moss. Sides: lit side faces RockLt, shaded RockDk, base Rock (95,85,105).'),
 silhouette=dict(skyline='climbs west -> east: west shoulder ~100, east summit ~146 (max 149.4 incl. slab tilt); saddle at x~10',slabs='~257 chunky leaning slabs (9-12 x 6.5-8.8 studs), stacked in 2-4 segments with setbacks, tops tilted, lean up to 8-15 studs; no repeated hex columns; ~60 small ceiling columns only above the tunnel'),
 pad_clearance=dict(pads_checked=[15,16,17,18],art_clear=clear,rule='art-clear 54x84 rectangles vs the mesh x/z bounding footprint (studs); footprint front edge world z %.1f, x %.1f..%.1f'%(fz1,fx0,fx1)),
 not_a_gameplay_surface='Scenery only. No flat ledges, no pads, no putting surface, nothing meant to be walked on; every part should be CanCollide=false except optionally an invisible blocker the course builder adds. Stairs and tunnel are decorative.',
 parts=parts,generator=['src/wreck_lib.py','src/gen_cave.py','src/build_cave.py','src/render_cave.py','src/make_manifest.py','src/box_preview.py','src/prev_box.py'],
 previews='previews_cave_v2/',
 terrain_notes=['Heightmap terrain under the footprint is lower than y=66 at the back and flanks (base floats up to ~60 studs above ground there) and about 96-108 at the mouth/stairs (above the mouth floor y=94). Fix by sinking/burying the base or filling terrain; the mesh cannot adapt.'],
 deviations=['No pad ledges in the mesh (pads are never in art meshes).','Pool is a tub inside the footprint at local (-80,48.4,36), not 34 studs outside the face.','Stair rise is 18 studs (y 10 -> 28) at the front, not a full ground-to-mouth ramp.','Mouth ceiling is built from ~60 small hanging columns (arch roof is stepped, not a smooth vault).','The back (north) side is plain slabs with a few dark flat gaps; it faces away from every pad.','Foliage extends to x -115.5..118.2 and z 68.3; rock mass x -117..115, z -68.4..69.6; stairs to z 70.'],
 max_tris_per_mesh=max(v['tris'] for v in parts.values()),under_20k=all(v['tris']<20000 for v in parts.values()))
json.dump(man,open(f'{H}/manifest.json','w'),indent=1);print('ok',man['size'],clear)
