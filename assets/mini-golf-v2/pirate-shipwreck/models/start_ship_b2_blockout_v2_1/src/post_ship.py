# box-side post: labels the raw previews, builds the contact sheet and manifest.json
import json,math,os,sys
from PIL import Image,ImageDraw,ImageFont
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));P=R+'/prev'
g=json.load(open(R+'/work/geom.json'));d=json.load(open(P+'/dump.json'));pm=json.load(open(P+'/plan_meta.json'))
def F(n):
    for f in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']:
        if os.path.exists(f):return ImageFont.truetype(f,n)
    return ImageFont.load_default()
def tag(dr,xy,t,col=(255,255,255),bg=(20,20,20),n=26):
    f=F(n);b=dr.textbbox(xy,t,font=f);dr.rectangle((b[0]-6,b[1]-4,b[2]+6,b[3]+4),fill=bg);dr.text(xy,t,font=f,fill=col)
# hero
im=Image.open(P+'/hero_3q.png').convert('RGB');dr=ImageDraw.Draw(im);tag(dr,(20,20),'3/4 hero: hull 15 deg, masts 18 deg, level deck, castle + forecastle');im.save(P+'/start_ship_b2_hero_3q.png')
# side: raw looks from +X (sand on the left); flip so sand is on the right
im=Image.open(P+'/side_section_raw.png').convert('RGB').transpose(Image.FLIP_LEFT_RIGHT);dr=ImageDraw.Draw(im)
s=im.width/330.0;y24=int(600+(60-24)*s);y0=int(600+60*s)
for x in range(0,im.width,28):dr.line((x,y24,x+14,y24),fill=(255,220,0),width=4)
tag(dr,(20,y24-52),'Y 24 deck + cabin floor = LEVEL',(255,220,0))
tag(dr,(20,20),'Side section through the door (x=-120), sand on the right');tag(dr,(20,70),'Hull lists 15 deg, masts+rigging 18 deg, toward the sand',(255,160,120))
tag(dr,(im.width-200,y0+14),'SAND',(235,215,170));dr.line((0,y0,im.width,y0),fill=(60,50,30),width=2)
im.save(P+'/start_ship_b2_side_section.png')
# plan
im=Image.open(P+'/plan_raw.png').convert('RGB');dr=ImageDraw.Draw(im);sc=pm['w']/pm['scale']
def px(x,z):return (pm['w']/2+(x-pm['cx'])*sc, pm['h']/2+(z-pm['cz'])*sc)   # top view: +X right, +Z down
for e in g['empties']:
    if e['name']=='CupRef' :continue
    x,z=px(e['pos'][0],e['pos'][2]);dr.ellipse((x-9,z-9,x+9,z+9),fill=(255,60,60),outline=(255,255,255),width=3);tag(dr,(x+16,z-16),e['name'],(255,230,230),(150,20,20),30)
for nm,pos in [('Flight1',(-120,88)),('Landing',(-120,114.5)),('Flight2 (30 deg)',(-140,150))]:
    x,z=px(*pos);tag(dr,(x+24,z-14),nm,(200,255,200),(20,60,20),22)
tag(dr,(20,20),'Top-down plan (cabin roof removed): Spawn, Tee1, RampStart');im.save(P+'/start_ship_b2_plan.png')
# door
im=Image.open(P+'/door_view.png').convert('RGB');dr=ImageDraw.Draw(im);tag(dr,(20,20),'From the cabin door: tee mat, ramp, 5-stud figure');im.save(P+'/start_ship_b2_door_view.png')
# contact sheet
names=[('start_ship_b2_hero_3q.png'),('start_ship_b2_side_section.png'),('start_ship_b2_plan.png'),('start_ship_b2_door_view.png')]
W,H=1000,750;T=70;sheet=Image.new('RGB',(W*2,H*2+T),(24,24,28));dr=ImageDraw.Draw(sheet)
dr.text((20,16),'Pirate Shipwreck - start ship B2/B3 blockout v2.1 (VR Mini Golf V2)',font=F(34),fill=(255,255,255))
for i,n in enumerate(names):sheet.paste(Image.open(P+'/'+n).resize((W,H),Image.LANCZOS),((i%2)*W,T+(i//2)*H))
sheet.save(R+'/start_ship_b2_contact_sheet.png');print('sheet ok')
# v2.1 close-ups
cl=[('closeup_landing_posts_raw.png','Landing support posts: tops now 0.5 BELOW the felt (were coplanar = z-fight)'),('closeup_landing_rail_join_raw.png','Flight1 -> landing rail joint: landing N-rail inner face recessed 0.05'),('closeup_platform_lamp_raw.png','Platform lamp post nudged 0.1 out; no coplanar faces with end rail')]
for f,t in cl:
    im=Image.open(P+'/'+f).convert('RGB');dr=ImageDraw.Draw(im);tag(dr,(20,20),t,n=30);im.save(P+'/start_ship_b2_v2_1_'+f.replace('_raw',''))
W2,H2=800,600;cs=Image.new('RGB',(W2*3,H2+60),(24,24,28));dr=ImageDraw.Draw(cs);dr.text((20,12),'start ship v2.1 fixed spots (close-ups)',font=F(30),fill=(255,255,255))
for i,(f,t) in enumerate(cl):cs.paste(Image.open(P+'/start_ship_b2_v2_1_'+f.replace('_raw','')).resize((W2,H2),Image.LANCZOS),(i*W2,60))
cs.save(R+'/start_ship_b2_v2_1_fix_closeups.png')
# manifest
obj=d['objects'];ex=g['info']
man=dict(name='start_ship_b2_blockout_v2_1',based_on='start_ship_b2_blockout_v2 (approved; folder untouched)',v2_1_fix=dict(summary='Part-level clip check of v2 found NO ramp/landing/flight/stair plank intersecting a post, mast, railing, support post or bumper outside designed joints. 3 coplanar-face (z-fighting) defects fixed; mesh tri counts and all origins identical to v2.',fixes=[dict(what='RampLanding 4 support posts: top at local y=0.0 was coplanar with the felt top (z-fight patch 2.4x2.4 per post, ~1.5 wide in the lane)',change='post top lowered to local y=-0.5 (post height 14 -> 13.5)',roblox_locations=[[-126.2,12.0,116.5],[-113.8,12.0,116.5],[-113.8,12.0,128.0],[-126.2,12.0,122.5]]),dict(what='RampLanding RailN_W/RailN_E inner face (x=+-6.0) coplanar with Flight1 rail inner face over 0.8 stud at the join',change='landing N-rail inner face moved to x=+-6.05 (rail 0.05 thinner)',roblox_locations=[[-126.0,13.9,114.5],[-114.0,13.9,114.5]]),dict(what='platform lamp posts (Dressing) had a face coplanar with the platform end-rail end face (x=-127.6 / -112.4)',change='lamp post x moved 0.1 outward',roblox_locations=[[-128.9,28.0,60.8],[-111.1,28.0,60.8]])],closeups=['start_ship_b2_v2_1_fix_closeups.png','prev/start_ship_b2_v2_1_closeup_landing_posts.png','prev/start_ship_b2_v2_1_closeup_landing_rail_join.png','prev/start_ship_b2_v2_1_closeup_platform_lamp.png']),units='studs (Roblox frame: +Y up, front +Z; 1 Blender unit = 1 stud; FBX exported -Z fwd / Y up)',
 files=dict(visual='start_ship_b2_visual.fbx',collision='start_ship_b2_col.fbx',ramp_pieces=['RampFlight1_own_origin.fbx','RampLanding_own_origin.fbx','RampFlight2_own_origin.fbx'],palette='start_ship_palette.png',contact_sheet='start_ship_b2_contact_sheet.png',previews=['prev/start_ship_b2_hero_3q.png','prev/start_ship_b2_side_section.png','prev/start_ship_b2_plan.png','prev/start_ship_b2_door_view.png'],src='src/'),
 meshes={k:dict(tris=v['tris'],size_studs=v['size'],bbox_min=v['roblox_min'],bbox_max=v['roblox_max'],origin=v['origin_roblox']) for k,v in obj.items()},
 total_tris=sum(v['tris'] for v in obj.values()),
 empties={e['name']:e['pos'] for e in g['empties']},
 ramp_pieces=dict(RampFlight1=dict(origin=ex['f1_origin'],note='12 wide, ~13 deg, Y24->Y12, run ~52; origin at top-centre of the slope'),
   RampLanding=dict(origin=ex['landing_origin'],note='16x16 at Y12 on 4 posts, SW corner open, south outer rail solid ~5.5 high on east part, felt rails ~3.5 high'),
   RampFlight2=dict(origin=ex['f2_origin'],built='STRAIGHT (runs +Z, no turn baked in)',studio_yaw_deg=ex['f2_yaw_deg'],studio_cframe='CFrame.new(origin) * CFrame.Angles(0, math.rad(-30), 0)',heading_after_yaw=ex['f2_heading'],note='12 wide, ~13 deg, Y12->Y0, then flat felt apron ~16 long x ~14 wide; joins overlap ~0.5')),
 props=dict(Pier=ex['pier_origin'],RockBumper=ex['bumper_origin']),
 v2_changes=dict(
  rock_bumper=dict(origin=ex['bumper_origin'],v1_origin=[-139.98,0.0,184.5],lateral_from_flight2_centreline=ex['bumper']['lateral'],along_flight2=ex['bumper']['along'],note='v1 was also 17 from the centreline but the 9-stud rock touched the apron edge; v2 is 21 so there is ~5 studs of clear sand between rock and apron edge (apron half width 7)'),
  stern_castle=dict(ex['castle'],note='hull bulwark raised 10 studs around the cabin (x -160..-95, tapering to 0 at x -65) both sides plus a transom plate; low side left open at the ramp gap; walls are part of the Hull mesh and tilt with the hull; cabin walls/roof unchanged'),
  forecastle=ex['forecastle'],bowsprit=dict(ex['bowsprit'],note='moved from Rigging into the Hull mesh (hull 15 deg frame), thicker, sits on 2 bitts on the forecastle; masts stays end at its tip'),
  tilt=dict(hull_deg=15,masts_sails_rigging_deg=18,note='kept the hull at 15: changing it would move the level-deck/hull cut and the tee/ramp footprint; the 3 deg extra on the masts reads fine. Deck, cabin, forecastle and ramps stay level'),
  paint_prep=dict(hull_planks_rgb=[110,70,40],wales_rgb=[80,50,30],palette_cells='Wood=(110,70,40) cell 0, WoodDk=(80,50,30) cell 1',hull_strips='outer skin strips 0 and 21 (sheer strake), 2 and 19 (upper wale), 5 and 16 (lower wale), 10 and 11 (keel) use WoodDk; all other outer and inner planking uses Wood')),
 cabin=ex['cabin'],tee_pad=ex['tee_pad'],
 cols=dict(count=len(g['cols']),file='start_ship_b2_col.fbx',pivot_convention='ramp COL_* are boxes whose object origin is the box centre; piece-local COL names are prefixed COL_Flight1/Landing/Flight2 and positioned in their piece frame (pivot field in geom.json); other COL_* are world-space (Hull, Deck, Cabin, Bulwark, Outrigger, Pier, RockBumper, PlatRail)',
   list=[dict(name=c['name'],centre=c['centre'],size=c['size'],pivot=c['pivot'],note=c.get('note','')) for c in g['cols']]),
 scale_note='1 stud = 1 Roblox stud. 5-stud character fits the 8 wide x 10 high cabin door; cabin interior is 16 high at the eaves (30 at the roof peak). Deck + cabin floor level at Y=24. Ship ~317 x 59 x 87 hull, mast tip ~160 up. Ramps 12 wide, felt-lined rails ~3.5 high.',
 deviations=['Cabin is 43 deep (z -19..24) instead of ~55: hull interior at Y24 is only ~66 wide','Masts merged into Rigging mesh','Dressing_Glow and CupRef empty are extras','Tee pad is a thin felt slab','Sand, water, mound, 5-stud figures in previews are preview-only, not exported','Hull is visually closed but not watertight; hull COL boxes are scenery'])
json.dump(man,open(R+'/manifest.json','w'),indent=1);print('manifest ok',man['total_tris'])
