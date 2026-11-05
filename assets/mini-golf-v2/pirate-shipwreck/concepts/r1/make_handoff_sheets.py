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
def sheet(raw,out,title,sub,labels,specs):
    im=Image.open(R+'raw/sheets/'+raw).convert('RGB');w,h=im.size
    pw=w//2;ph=h//2
    SP=330
    c=Image.new('RGB',(w,h+100+SP),BG);d=ImageDraw.Draw(c)
    c.paste(im,(0,100))
    d.text((24,34),title,font=fnt(FB,36),fill=GOLD,anchor='lm')
    d.text((24,76),sub,font=fnt(F,20),fill=(210,220,230),anchor='lm')
    for i,l in enumerate(labels):
        x=(i%2)*pw+14;y=100+(i//2)*ph+14
        b=d.textbbox((x,y),l,font=fnt(FB,22));d.rounded_rectangle((b[0]-8,b[1]-6,b[2]+8,b[3]+6),radius=8,fill=(15,20,30,230))
        d.text((x,y),l,font=fnt(FB,22),fill=(255,255,255))
    y=100+h+24
    colw=(w-60)//2
    for ci,col in enumerate(specs):
        x=24+ci*(colw+12)
        d.text((x,y),col[0],font=fnt(FB,22),fill=GOLD)
        yy=y+34
        for line in col[1]:
            for j,l in enumerate(wrap(d,line,fnt(F,19),colw-30)):
                d.text((x+(0 if j==0 else 18),yy),('- ' if j==0 else '')+l,font=fnt(F,19),fill=(225,232,242));yy+=26
            yy+=2
    c.save(R+out)
sheet('wreck_raw.png','3d-1-wreck-sheet.png','HERO 1: THE WRECK  (Look B palette, handoff draft)','Front, side and top silhouettes plus a 3/4 view. Build the hull first; sails and rigging are a separate mesh.',
['FRONT (bow)','SIDE (tilted ~15 degrees)','TOP-DOWN','3/4 VIEW'],
[('Shape notes',['Ship leans aground about 15 degrees to the left, bow up on the beach, stern in the surf.',
'Rubber-duck figurehead: big grumpy yellow duck, eyepatch, tiny captain hat (own small mesh part, chunky, readable from 60 studs).',
'Main mast snapped halfway and leaning over, tall enough to be the landmark seen from most holes. Foremast shorter, mizzen stub at the stern.',
'Hull planks big and chunky, 2 or 3 broken holes in the hull, stern cabin with lantern posts.',
'Original look: patchwork red and cream sails, small square cabin windows. No skull flag, no copied ship.']),
('props.md: wreck',['Size: about 220 studs long, 70 wide, hull 45 tall, main mast tip about 120 studs above the waterline.',
'Meshes: (1) hull + deck + cabin <= 18k tris, (2) masts + sails + rigging <= 12k tris, (3) duck figurehead <= 3k tris. All under 20k.',
'Colors (Look B): weathered plank (140,90,55), dark wood trim (84,52,34), sail cream (238,222,190), sail red (196,60,50), duck yellow (245,196,40).',
'Glow parts (separate, Neon or PointLight): 6 to 8 lantern globes, amber (255,190,80).',
'Pad clearance: leave a flat, empty plank-deck area at the stern side and the beach side for pad 1; nothing taller than 3 studs within 25 studs of the pad centre. Hull is scenery only, no collision with the ball.'])])
sheet('cave_raw.png','3d-2-cave-cliff-sheet.png','HERO 2: THE CAVE CLIFF  (Look B palette, handoff draft)','Front, side and top silhouettes plus a 3/4 view. The flat sand ledges are open space for hole pads, they are not gameplay surfaces.',
['FRONT','SIDE','TOP-DOWN (open ledges = pad space)','3/4 VIEW'],
[('Shape notes',['Tall grey-violet rock cliff, stepped terraces, wide arched cave mouth near the top with a warm amber glow inside.',
'Stone staircase climbs from the jungle edge to the mouth, with a thin waterfall down one side and a small pool at the foot.',
'Cliff is the second landmark, visible from the beach and jungle, so keep the top silhouette bold and simple.',
'Stone slab pads sit on the ledges, built by the course builder. Rock, vines and palms frame them but never sit on them.',
'No skeletons in this mesh. The pirate remains are separate gag props placed inside.']),
('props.md: cave cliff',['Size: about 240 studs wide, 150 tall, 140 deep. Cave mouth about 40 wide by 36 tall.',
'Meshes: (1) cliff rock lower half <= 16k tris, (2) cliff rock upper half + cave arch <= 16k tris, (3) stairs + railings <= 4k tris. Vines and palms are separate small parts.',
'Colors (Look B): rock grey-violet (110,92,120), rock shadow (70,56,90), vine green (30,100,60), stair stone (150,130,120), cave glow amber (255,150,50).',
'Glow parts: cave mouth interior light (PointLight, range 40) and 6 lantern posts along the stairs.',
'Pad clearance: leave at least 4 flat ledges roughly 60 x 45 studs each, with 8 studs of empty space around each pad.'])])
