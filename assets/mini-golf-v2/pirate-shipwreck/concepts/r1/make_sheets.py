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
looks=[('A','Sunny Splash Cove','Bright tropical noon: turquoise lagoon, white sand, emerald jungle, cheerful and playful.','lookA'),
('B','Golden Hour Hideaway','Golden sunset with violet shadows and glowing lanterns: warm, cozy, a little mysterious.','lookB'),
('C','Thunder Tide Dusk','Stormy teal-and-indigo dusk, lightning, eerie green cave glow: spooky-fun, high contrast.','lookC')]
# individual labelled key art
slug={'A':'sunny-splash-cove','B':'golden-hour-hideaway','C':'thunder-tide-dusk'}
for k,n,desc,f in looks:
    im=Image.open(R+'raw/%s.png'%f).convert('RGB');w,h=im.size
    c=Image.new('RGB',(w,h+110),BG);c.paste(im,(0,0));d=ImageDraw.Draw(c)
    d.text((24,h+34),'LOOK %s  -  %s'%(k,n),font=fnt(FB,36),fill=GOLD,anchor='lm')
    d.text((24,h+80),desc,font=fnt(F,22),fill=(220,228,240),anchor='lm')
    c.save(R+'look%s-%s.png'%(k,slug[k]))
# contact sheet
CW=620;CH=349;G=20;top=90
W=3*CW+4*G;rows=CH+190
cs=Image.new('RGB',(W,top+rows+40),BG);d=ImageDraw.Draw(cs)
d.text((G,45),'PIRATE SHIPWRECK  -  overall look options (round 1)',font=fnt(FB,34),fill=GOLD,anchor='lm')
for i,(k,n,desc,f) in enumerate(looks):
    x=G+i*(CW+G);im=Image.open(R+'raw/%s.png'%f).convert('RGB').resize((CW,CH),Image.LANCZOS)
    cs.paste(im,(x,top))
    d.rounded_rectangle((x+10,top+10,x+58,top+58),radius=10,fill=(255,236,170));d.text((x+34,top+35),k,font=fnt(FB,32),fill=(20,20,20),anchor='mm')
    d.text((x,top+CH+34),n,font=fnt(FB,28),fill=(255,255,255),anchor='lm')
    for j,l in enumerate(wrap(d,desc,fnt(F,19),CW)): d.text((x,top+CH+72+j*26),l,font=fnt(F,19),fill=(210,220,235),anchor='lm')
d.text((G,top+rows+10),'Recommended: A or B for VR comfort (bright, readable), C as a night variant later. See recommendation in the report.',font=fnt(F,18),fill=(160,175,195),anchor='lm')
cs.save(R+'contact-sheet-ABC.png')
# gag sheet
gags=[('Duck figurehead','Wreck bow carved as a grumpy eye-patched rubber duck with a seagull hat.','wreck','Pad 1',True),
('Backward cannon','Cannon aimed at its own ship, cannonballs spilled, smoke puffing from the rear.','wreck','Pad 1-2',True),
('Hammock flop','Skeleton fell through his rope hammock, only boots and ribs poking out.','wreck','Pad 2',False),
('Crab thief','Giant crab runs off with a peg leg while its one-legged skeleton owner hops after it.','beach','Pad 5',False),
('Sand sunbather','Skeleton buried to the ribs in sand, sunglasses on, seagull nest on his skull.','beach','Pad 6-7',False),
("Fool's chest",'Treasure chest of seashells, starfish, one coin and one striped sock.','beach','Pad 8',False),
('Coconut casualty','Pirate pressed flat under a palm, coconut sitting on his squashed hat.','jungle','Pad 10',True),
('Monkey captain','Monkey in an oversized captain hat guarding a coconut stockpile.','jungle','Pad 11',False),
('Boot tree','Old boots hang from vines like fruit, one has a flower, one has a frog.','jungle','Pad 12-13',False),
('Flytrap burp','Giant flytrap with only striped legs and boots kicking out, hat left behind.','jungle','Pad 13-14',True),
('Croc nap','Sleepy croc wearing a captain hat, cutlass as a toothpick, a boot in its mouth.','jungle','Rest stop by pad 14',True),
('Dig here','Skeleton digs a deep hole on the map\'s X and finds a rubber duck.','cave','Pad 16',False),
("Captain's last nap",'Skeleton captain snoozing on a bone throne and gold pile, cobwebs on his hat.','cave','Pad 18',True)]
ZC={'wreck':(232,85,61),'beach':(242,182,50),'jungle':(47,168,79),'cave':(142,91,214)}
cols=5;cw=370;th=340;ch=th+125;gx=20;hdr=110;ftr=50
W=cols*cw+(cols+1)*gx;rows=3
H=hdr+rows*(ch+gx)+ftr
c=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(c)
d.text((gx,40),'PIRATE SHIPWRECK  -  story beats and gag props, in trail order (round 1)',font=fnt(FB,34),fill=GOLD,anchor='lm')
d.text((gx,82),'Star = 3D hero prop for 3D Model Bot. Others are small dressing (simple kitbash or part of the scenery). Skeletons are cartoony, no gore. Thumbnails are mood sketches, not final shapes.',font=fnt(F,18),fill=(210,220,230),anchor='lm')
for i,(t,cap,z,pad,hero) in enumerate(gags):
    x=gx+(i%cols)*(cw+gx);y=hdr+(i//cols)*(ch+gx)
    d.rounded_rectangle((x,y,x+cw,y+ch),radius=12,fill=(30,44,60))
    im=Image.open(R+'raw/gags/g%02d.png'%(i+1)).convert('RGB').resize((th,th),Image.LANCZOS)
    c.paste(im,(x+(cw-th)//2,y+8))
    d.ellipse((x+14,y+14,x+54,y+54),fill=ZC[z],outline=(255,255,255),width=3)
    d.text((x+34,y+35),str(i+1),font=fnt(FB,22),fill=(20,20,20) if z=='beach' else (255,255,255),anchor='mm')
    if hero:
        d.rounded_rectangle((x+cw-128,y+14,x+cw-14,y+46),radius=8,fill=(255,200,40));d.text((x+cw-71,y+31),'* 3D HERO',font=fnt(FB,16),fill=(20,20,20),anchor='mm')
    d.text((x+12,y+th+24),t,font=fnt(FB,21),fill=(255,255,255),anchor='lm')
    d.text((x+cw-12,y+th+24),pad,font=fnt(F,14),fill=ZC[z],anchor='rm')
    for j,l in enumerate(wrap(d,cap,fnt(F,16),cw-24)): d.text((x+12,y+th+52+j*21),l,font=fnt(F,16),fill=(205,215,230),anchor='lm')
# legend cell
i=13;x=gx+(i%cols)*(cw+gx);y=hdr+(i//cols)*(ch+gx)
d.text((x+10,y+20),'ZONES',font=fnt(FB,22),fill=GOLD,anchor='lm')
for j,(zn,lab) in enumerate([('wreck','Wreck & cove (pads 1-4)'),('beach','Beach (5-9)'),('jungle','Jungle (10-14)'),('cave','Cave cliff (15-18)')]):
    d.ellipse((x+10,y+50+j*36,x+34,y+74+j*36),fill=ZC[zn]);d.text((x+46,y+62+j*36),lab,font=fnt(F,18),fill=(255,255,255),anchor='lm')
d.text((x+10,y+215),'Not a gag, also hero meshes:',font=fnt(FB,16),fill=GOLD,anchor='lm')
d.text((x+10,y+240),'the wreck (tall mast) and the cave cliff.',font=fnt(F,16),fill=(220,228,240),anchor='lm')
d.text((x+10,y+275),'Rule: props sit beside pads, never on them.',font=fnt(F,16),fill=(220,228,240),anchor='lm')
c.save(R+'story-gags-sheet.png')
