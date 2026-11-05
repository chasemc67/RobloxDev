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
dr.text((20,16),'Pirate Shipwreck - start ship B2/B3 blockout v2.3 (VR Mini Golf V2)',font=F(34),fill=(255,255,255))
for i,n in enumerate(names):sheet.paste(Image.open(P+'/'+n).resize((W,H),Image.LANCZOS),((i%2)*W,T+(i//2)*H))
sheet.save(R+'/start_ship_b2_contact_sheet.png');print('sheet ok')
# v2.3 fixes before/after sheet
Pb=R+'/prev_before'
def lab(path,t):
    im=Image.open(path).convert('RGB');dr=ImageDraw.Draw(im);tag(dr,(20,20),t,n=34);return im
rows=[('roof_inside_raw.png','Cabin roof from inside the cabin (floor, looking up)'),('roof_deck_raw.png','Cabin roof from the deck (eye height, facing the cabin)'),('roof_outside_raw.png','Cabin roof from outside (high 3/4)'),
 ('waterline_mid_raw.png','Waterline close-up, midships, low side (water = world Y 0)'),('waterline_stern_raw.png','Waterline close-up, stern quarter'),('waterline_wide_raw.png','Waterline, looking along the keel from astern at water level (sky = see-through gap)')]
Wc,Hc=900,600;sh=Image.new('RGB',(Wc*2,Hc*len(rows)+80),(24,24,28));dr=ImageDraw.Draw(sh)
dr.text((20,18),'start ship v2.3: roof + settled hull.  v2.2 (left)  vs  v2.3 (right)',font=F(34),fill=(255,255,255))
for r,(f,t) in enumerate(rows):
    sh.paste(lab(Pb+'/'+f,'BEFORE v2.2 - '+t).resize((Wc,Hc),Image.LANCZOS),(0,80+r*Hc))
    sh.paste(lab(P+'/'+f,'AFTER v2.3 - '+t).resize((Wc,Hc),Image.LANCZOS),(Wc,80+r*Hc))
sh.save(R+'/start_ship_b2_v2_3_fixes.png')
# manifest: keep the v2.2 manifest, update in place
mp=R+'/manifest.json';man=json.load(open(mp));obj=d['objects']
old={k:v['tris'] for k,v in man['meshes'].items()}
man['name']='start_ship_b2_blockout_v2_3';man['based_on']='start_ship_b2_blockout_v2_2 (approved; folder untouched)'
for k,v in obj.items():man['meshes'][k].update(tris=v['tris'],size_studs=v['size'],bbox_min=v['roblox_min'],bbox_max=v['roblox_max'],origin=v['origin_roblox'])
man['total_tris']=sum(v['tris'] for v in obj.values())
ch=[k for k in obj if obj[k]['tris']!=old[k] or k in('Hull','DeckCabin')]
man['v2_3_change']=dict(summary='Scope reduced by the parent: NO new COL boxes (RobloxDevBot is doing bow deck-gap + hull-side collision in v27). Visual changes only: (1) visible cabin roof, (2) hull skirt so the wreck sits below the waterline.',
 roof=dict(root_cause='v2_2 roof panels were generated at x=0 (apex x passed as the mesh translation) instead of the cabin centre x=-120, so the cabin showed open sky and two grey slabs floated over midships near the mast.',
   fix='panels now centred on the cabin (x=-120), same slope/thickness/height as COL_CabinRoof_N/S (unchanged): ridge top at world Y 53.8 (hull-frame 53.2). Planks in Wood (110,70,40); WoodDk (80,50,30) eave band, gable rakes, ridge cap, plank-seam battens down the slope and underside rafters. Battens are 0.3-0.5 studs proud and embedded (no coplanar faces).',
   mesh='DeckCabin',tris_before=old['DeckCabin'],tris_after=obj['DeckCabin']['tris']),
 hull=dict(finding='MESH, not placement: v2_2 hull lowest point was world Y -0.43 at the stern, +0.95 at x=-5, +3.7 at x=40, +6.7 at x=70 (rising with the rocker to ~+25 at the bow) vs water at Y 0 -> see-through gap under the hull. Placement is hull-frame Y + 0.6 = world.',
   fix='OUTER hull skin extended down (skirt): lowest hull point is now hull-frame Y -2.1 = world Y -1.5 (1.5 studs below the waterline) from the stern to x~85, blending back to the original rocker by x~125 (bow rests on the beach; v26 probes show water under the ship up to ~x 85 and sand from ~x 105). Inner skin, deck, bulwark and the COL_HullExt boxes are unchanged.',
   mesh='Hull',tris_before=old['Hull'],tris_after=obj['Hull']['tris'],
   placement_note='No placement change needed: keep ship Y offset +0.6. Do NOT lower the whole ship instead: the deck/ramps/tee are level at 24 and v2_2 hull bottoms are 1-7 studs above water along x 0..70, so a pure Y offset would need about -2.5 (midships) to -8 (x=70) and would sink the deck.'),
 changed_meshes=['Hull','DeckCabin'],unchanged_meshes=[k for k in obj if k not in('Hull','DeckCabin')],
 cols=dict(count=190,status='start_ship_b2_col.fbx IDENTICAL to v2_2 (same 190 boxes, names, centres, sizes); start_ship_b2_col_extra.fbx not needed (no extra boxes were made)'),
 notes_for_RobloxDevBot=['Swap start_ship_b2_visual.fbx only (Hull + DeckCabin parts changed; same names/origins/scale, re-apply the same material mapping). COL FBX and ramp FBXs are unchanged.',
   'FYI: the 64 COL_HullExt_* boxes + COL_HullExt_Stern are in the COL FBX but the v26 build looked to be missing them (143 StartShip colliders); they are 40-stud pieces so coarse at the bow. P1 gap cause: 16-long deck slabs vs 12-long bulwark pieces at the narrowing bow.'],
 colours='no new palette colours; start_ship_palette.png unchanged',preview='start_ship_b2_v2_3_fixes.png')
json.dump(man,open(mp,'w'),indent=1);print('manifest ok',man['total_tris'])
