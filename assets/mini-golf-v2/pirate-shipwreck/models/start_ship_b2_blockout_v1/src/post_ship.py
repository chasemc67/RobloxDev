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
im=Image.open(P+'/hero_3q.png').convert('RGB');dr=ImageDraw.Draw(im);tag(dr,(20,20),'3/4 hero: ship listing 15 deg in sand, level deck, ramp to pier');im.save(P+'/start_ship_b2_hero_3q.png')
# side: raw looks from +X (sand on the left); flip so sand is on the right
im=Image.open(P+'/side_section_raw.png').convert('RGB').transpose(Image.FLIP_LEFT_RIGHT);dr=ImageDraw.Draw(im)
s=im.width/330.0;y24=int(600+(60-24)*s);y0=int(600+60*s)
for x in range(0,im.width,28):dr.line((x,y24,x+14,y24),fill=(255,220,0),width=4)
tag(dr,(20,y24-52),'Y 24 deck + cabin floor = LEVEL',(255,220,0))
tag(dr,(20,20),'Side section through the door (x=-120), sand on the right');tag(dr,(20,70),'Hull + masts list 15 deg toward the sand',(255,160,120))
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
dr.text((20,16),'Pirate Shipwreck - start ship B2/B3 blockout v1 (VR Mini Golf V2)',font=F(34),fill=(255,255,255))
for i,n in enumerate(names):sheet.paste(Image.open(P+'/'+n).resize((W,H),Image.LANCZOS),((i%2)*W,T+(i//2)*H))
sheet.save(R+'/start_ship_b2_contact_sheet.png');print('sheet ok')
# manifest
obj=d['objects'];ex=g['info']
man=dict(name='start_ship_b2_blockout_v1',units='studs (Roblox frame: +Y up, front +Z; 1 Blender unit = 1 stud; FBX exported -Z fwd / Y up)',
 files=dict(visual='start_ship_b2_visual.fbx',collision='start_ship_b2_col.fbx',ramp_pieces=['RampFlight1_own_origin.fbx','RampLanding_own_origin.fbx','RampFlight2_own_origin.fbx'],palette='start_ship_palette.png',contact_sheet='start_ship_b2_contact_sheet.png',previews=['prev/start_ship_b2_hero_3q.png','prev/start_ship_b2_side_section.png','prev/start_ship_b2_plan.png','prev/start_ship_b2_door_view.png'],src='src/'),
 meshes={k:dict(tris=v['tris'],size_studs=v['size'],bbox_min=v['roblox_min'],bbox_max=v['roblox_max'],origin=v['origin_roblox']) for k,v in obj.items()},
 total_tris=sum(v['tris'] for v in obj.values()),
 empties={e['name']:e['pos'] for e in g['empties']},
 ramp_pieces=dict(RampFlight1=dict(origin=ex['f1_origin'],note='12 wide, ~13 deg, Y24->Y12, run ~52; origin at top-centre of the slope'),
   RampLanding=dict(origin=ex['landing_origin'],note='16x16 at Y12 on 4 posts, SW corner open, south outer rail solid ~5.5 high on east part, felt rails ~3.5 high'),
   RampFlight2=dict(origin=ex['f2_origin'],built='STRAIGHT (runs +Z, no turn baked in)',studio_yaw_deg=ex['f2_yaw_deg'],studio_cframe='CFrame.new(origin) * CFrame.Angles(0, math.rad(-30), 0)',heading_after_yaw=ex['f2_heading'],note='12 wide, ~13 deg, Y12->Y0, then flat felt apron ~16 long x ~14 wide; joins overlap ~0.5')),
 props=dict(Pier=ex['pier_origin'],RockBumper=ex['bumper_origin']),
 cabin=ex['cabin'],tee_pad=ex['tee_pad'],
 cols=dict(count=len(g['cols']),file='start_ship_b2_col.fbx',pivot_convention='ramp COL_* are boxes whose object origin is the box centre; piece-local COL names are prefixed COL_Flight1/Landing/Flight2 and positioned in their piece frame (pivot field in geom.json); other COL_* are world-space (Hull, Deck, Cabin, Bulwark, Outrigger, Pier, RockBumper, PlatRail)',
   list=[dict(name=c['name'],centre=c['centre'],size=c['size'],pivot=c['pivot'],note=c.get('note','')) for c in g['cols']]),
 scale_note='1 stud = 1 Roblox stud. 5-stud character fits the 8 wide x 10 high cabin door; cabin interior is 16 high at the eaves (30 at the roof peak). Deck + cabin floor level at Y=24. Ship ~317 x 59 x 87 hull, mast tip ~160 up. Ramps 12 wide, felt-lined rails ~3.5 high.',
 deviations=['Cabin is 43 deep (z -19..24) instead of ~55: hull interior at Y24 is only ~66 wide','Masts merged into Rigging mesh','Dressing_Glow and CupRef empty are extras','Tee pad is a thin felt slab','Sand, water, mound, 5-stud figures in previews are preview-only, not exported','Hull is visually closed but not watertight; hull COL boxes are scenery'])
json.dump(man,open(R+'/manifest.json','w'),indent=1);print('manifest ok',man['total_tris'])
