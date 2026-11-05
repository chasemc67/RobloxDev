from PIL import Image, ImageDraw, ImageFont
R='/workspace/gameart/pirate-shipwreck/r1/'
FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';F='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
fnt=lambda p,s:ImageFont.truetype(p,s)
BG=(18,28,40);GOLD=(255,236,170)
def wrap(d,t,f,w):
    out=[];cur=''
    for x in t.split():
        if d.textlength((cur+' '+x).strip(),font=f)<=w: cur=(cur+' '+x).strip()
        else: out.append(cur);cur=x
    out.append(cur);return out
# ---- props sheet
props=[(1,'Duck figurehead','Wreck bow, part of the wreck mesh or its own piece','about 22 studs tall, 3k tris','Yellow (245,196,40), eyepatch dark, hat dark wood; no glow'),
(2,'Backward cannon','Wreck deck beside pad 1-2','about 14 long, 2.5k tris + 6 cannonballs (200 tris each)','Bronze (150,110,50), carriage wood; small smoke puff is a particle'),
(7,'Coconut casualty','Jungle entry, pad 10, beside the pad','palm 55 tall (3k tris), flat skeleton 14 long (1.5k tris)','Palm green (60,150,60), bone (240,232,210), hat dark; coconut brown (120,75,40)'),
(10,'Flytrap burp','Jungle, pads 13-14','about 30 tall, 4k tris','Plant green (70,170,70), jaw red (200,60,70), striped socks red/cream; no glow'),
(11,'Croc nap','Rest stop near pad 14','about 40 long, 4k tris','Croc green (80,140,60), hat dark, cutlass grey; no glow'),
(13,"Captain's last nap",'Cave, beside pad 18','throne+gold pile about 30 tall, 6k tris','Bone throne, gold (255,200,60), coin pile; soft amber PointLight')]
cols=3;cw=640;th=360;ch=th+70;gx=20;hdr=110
W=cols*cw+(cols+1)*gx;H=hdr+2*(ch+gx)+10
c=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(c)
d.text((gx,40),'HERO 3: GAG PROPS  (mood sketches, silhouettes come after Chase picks)',font=fnt(FB,34),fill=GOLD,anchor='lm')
d.text((gx,82),'Six hero props for 3D Model Bot, wreck and cave cliff come first. Sizes are in studs, triangle budgets are per prop. Props sit beside pads, never on them.',font=fnt(F,18),fill=(210,220,230),anchor='lm')
for i,(n,t,pl,sz,col) in enumerate(props):
    x=gx+(i%cols)*(cw+gx);y=hdr+(i//cols)*(ch+gx)
    d.rounded_rectangle((x,y,x+cw,y+ch),radius=12,fill=(30,44,60))
    im=Image.open(R+'raw/gags/g%02d.png'%n).convert('RGB').resize((th,th),Image.LANCZOS)
    c.paste(im,(x+10,y+10))
    tx=x+th+30
    d.text((tx,y+30),'#%d  %s'%(n,t),font=fnt(FB,19),fill=(255,255,255))
    yy=y+70
    for lab,val in [('Place',pl),('Size',sz),('Colors',col)]:
        d.text((tx,yy),lab,font=fnt(FB,17),fill=GOLD);yy+=24
        for l in wrap(d,val,fnt(F,17),cw-th-50): d.text((tx,yy),l,font=fnt(F,17),fill=(220,228,240));yy+=22
        yy+=10
    d.text((x+14,y+th+40),'Chunky, readable at 40 studs. White cartoon skeleton, no gore.',font=fnt(F,16),fill=(160,175,195))
c.save(R+'3d-3-props-sheet.png')
# ---- palette sheet
sw=[('Sky top, dusk violet',(150,90,150),'sky, Atmosphere decay'),
('Horizon glow',(255,140,70),'sunset band, ColorShift_Top'),
('Sun key light',(255,170,100),'warm key, bloom'),
('Shadow violet',(70,45,100),'shadow fill, Ambient'),
('Warm sand',(226,184,128),'beach, trails'),
('Dark wood',(84,52,34),'pad rims, trim, dock'),
('Weathered plank',(140,90,55),'hull, boardwalk'),
('Slate stone',(70,76,92),'pad rims in cave and jungle'),
('Rock grey-violet',(110,92,120),'cliff, boulders'),
('Jungle green',(30,100,60),'shaded foliage'),
('Leaf light',(90,170,70),'lit foliage'),
('Lagoon teal',(30,120,140),'water'),
('Sail cream',(238,222,190),'sails'),
('Sail red',(196,60,50),'sails, flags'),
('Duck yellow',(245,196,40),'figurehead, accents'),
('Lantern amber',(255,190,80),'lanterns, cave glow'),
('PAD FELT',(100,230,135),'all hole pads (see right)'),
('Flag red',(235,55,55),'tall cup flag')]
hexs=lambda c:'#%02X%02X%02X'%c
W,H=1920,1200
c=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(c)
d.text((30,36),'LOOK B: GOLDEN HOUR HIDEAWAY  -  palette and Roblox lighting',font=fnt(FB,36),fill=GOLD,anchor='lm')
d.text((30,76),'For RobloxDevBot. Values are a starting point, tune in a headset. Pads must stay bright and high-contrast.',font=fnt(F,20),fill=(210,220,230),anchor='lm')
ka=Image.open(R+'raw/lookB.png').convert('RGB').resize((560,315),Image.LANCZOS);c.paste(ka,(30,110))
# swatches
sx=620;sy=110;sc=6;sw_w=165;sw_h=70
for i,(n,col,use) in enumerate(sw):
    x=sx+(i%6)*(sw_w+12)+0;y=sy+(i//6)*(sw_h+58)
    d.rectangle((x,y,x+sw_w,y+sw_h),fill=col,outline=(255,255,255),width=3 if n=='PAD FELT' else 1)
    d.text((x,y+sw_h+4),n,font=fnt(FB,14),fill=(255,255,255))
    d.text((x,y+sw_h+22),'%s  %d,%d,%d'%(hexs(col),*col),font=fnt(F,13),fill=GOLD)
    d.text((x,y+sw_h+38),use,font=fnt(F,12),fill=(170,185,205))
# lighting table
ly=520
d.text((30,ly),'ROBLOX LIGHTING (Lighting service)',font=fnt(FB,24),fill=GOLD)
rows=[('ClockTime','17.7 (low sun, 18.0 is flat sunset)'),('GeographicLatitude','25'),('Brightness','2.6'),('Ambient','Color3 (95, 62, 100)'),
('OutdoorAmbient','Color3 (150, 105, 120)'),('ColorShift_Top','Color3 (255, 165, 95)'),('ColorShift_Bottom','Color3 (120, 80, 140)'),
('EnvironmentDiffuseScale / Specular','0.6 / 0.5'),('ShadowSoftness','0.35'),('GlobalShadows','true (keep, but see pad lights)'),('ExposureCompensation','0.2')]
y=ly+40
for k,v in rows:
    d.text((30,y),k,font=fnt(FB,17),fill=(255,255,255));d.text((410,y),v,font=fnt(F,17),fill=(220,228,240));y+=25
d.text((30,y+6),'ATMOSPHERE',font=fnt(FB,22),fill=GOLD);y+=40
for k,v in [('Density','0.28 (low, do not hide the pads)'),('Offset','0.25'),('Color','Color3 (255, 176, 140)'),('Decay','Color3 (140, 90, 120)'),('Glare / Haze','0.4 / 1.4')]:
    d.text((30,y),k,font=fnt(FB,17),fill=(255,255,255));d.text((410,y),v,font=fnt(F,17),fill=(220,228,240));y+=25
# post effects column
px=700;y=ly
d.text((px,y),'POST EFFECTS AND SKY',font=fnt(FB,24),fill=GOLD);y+=40
for k,v in [('Bloom','Intensity 0.35, Size 24, Threshold 1.1'),('ColorCorrection','Saturation 0.1, Contrast 0.08, Tint (255, 240, 225)'),('SunRays','Intensity 0.08, Spread 0.6'),
('DepthOfField','OFF (VR comfort)'),('Sky','Sunset skybox with a big sun low on the horizon, a few pink cloud streaks; or Clouds Cover 0.35, Density 0.5, Color (255, 190, 170)'),
('Water','Terrain water color (30,120,140), transparency 0.5, reflectance 0.35')]:
    d.text((px,y),k,font=fnt(FB,17),fill=(255,255,255))
    for j,l in enumerate(wrap(d,v,fnt(F,17),340)): d.text((px+170,y+j*22),l,font=fnt(F,17),fill=(220,228,240))
    y+=max(28,22*len(wrap(d,v,fnt(F,17),340))+6)
# pad box
bx=1250;by=520
d.rounded_rectangle((bx,by,W-30,H-30),radius=14,fill=(30,44,60),outline=GOLD,width=2)
d.text((bx+20,by+20),'HOLE PADS: BRIGHT AND CLEAR IN VR',font=fnt(FB,24),fill=GOLD)
# demo strip
dx=bx+20;dy=by+66
d.rectangle((dx,dy,dx+620,dy+90),fill=(226,184,128))
d.rectangle((dx+180,dy+10,dx+440,dy+80),fill=(84,52,34))
d.rectangle((dx+200,dy+22,dx+420,dy+68),fill=(100,230,135))
d.text((dx+310,dy+45),'PAD FELT',font=fnt(FB,16),fill=(20,50,30),anchor='mm')
d.text((dx+80,dy+45),'sand',font=fnt(F,16),fill=(60,40,20),anchor='mm');d.text((dx+540,dy+45),'sand',font=fnt(F,16),fill=(60,40,20),anchor='mm')
d.text((dx+190,dy+8),'dark wood rim',font=fnt(F,12),fill=(255,255,255))
y=dy+110
items=['Felt: Color3 (100, 230, 135), hex #64E687, SmoothPlastic, Reflectance 0, no texture. It is a cool mint green, so it never reads as the warm sand or the orange sunset light.',
'Luminance contrast with sand is only about 1.1, so felt NEVER touches sand. Every pad gets a dark rim 3 to 4 studs wide: dark wood (84,52,34) on the beach and wreck, slate (70,76,92) in jungle and cave. Felt to rim 6:1, rim to sand 6:1.',
'Light surroundings: keep sand, pale rock and cream sails at least 6 studs back from the felt edge.',
'Soft light per pad: one PointLight on a lantern post or hidden in the rim, Range 16, Brightness 1.0, Color (255,245,225), Shadows off. Raises the felt brightness and keeps shadows from darkening the cup.',
'Cup: dark ring, tall red flag (235,55,55) on a cream pole at least 14 studs tall, visible from the tee.',
'Shade check: never put a pad fully in the shadow of the wreck or cliff. If the felt looks darker than the sand in a headset, raise the pad light Brightness to 1.6.']
for it in items:
    ls=wrap(d,it,fnt(F,16),W-30-bx-50)
    for j,l in enumerate(ls): d.text((dx+(0 if j==0 else 14),y),('- ' if j==0 else '')+l,font=fnt(F,16),fill=(225,232,242));y+=21
    y+=7
c.save(R+'lookB-palette-lighting.png')
