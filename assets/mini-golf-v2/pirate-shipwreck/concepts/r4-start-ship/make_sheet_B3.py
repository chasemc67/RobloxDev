import math
from PIL import Image, ImageDraw, ImageFont
D='/workspace/gameart/pirate-shipwreck/r4-start-ship/'
FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';F='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
f=lambda p,s:ImageFont.truetype(p,s)
BG=(18,28,40);GOLD=(255,236,170);TXT=(225,232,242)
WOOD=(110,70,40);DWOOD=(80,50,30);POST=(100,72,50);POST2=(122,90,64);THATCH=(200,165,90);ROCK=(115,100,92);SAND=(226,184,128);FELT=(105,185,98);FLAME=(240,110,30)
WATER=(60,150,170);DOOR=(255,60,50);PATH=(255,230,80);DIM=(255,255,255)
W=2400;M=30
HERO_W,HERO_H=1120,840
ROW1=110+56
SEC_Y=ROW1+HERO_H+40
SEC_H=600
PAL_Y=SEC_Y+60+SEC_H+30
H=PAL_Y+190+30
c=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(c)
d.text((M,40),'START SHIP B3: HOLE 1 ON THE SHIP, TWO-FLIGHT RAMP  (Pirate Shipwreck, Look B Golden Hour Hideaway)',font=f(FB,38),fill=GOLD,anchor='lm')
d.text((M,84),'Listing hull (~15 deg), LEVEL deck and cabin for VR comfort. Tee on deck, flight 1, landing (outer rail stops a straight shot), flight 2 turns ~30 deg to the pier. Only the ramp changed from B2.',font=f(F,20),fill=(210,220,230),anchor='lm')
def tag(dr,xy,t,col=(255,255,255),sz=15,anchor='mm'):
    ft=f(FB,sz);b=dr.textbbox(xy,t,font=ft,anchor=anchor)
    dr.rounded_rectangle((b[0]-5,b[1]-3,b[2]+5,b[3]+3),radius=5,fill=(15,20,30));dr.text(xy,t,font=ft,fill=col,anchor=anchor)
def arrow(dr,p,q,col,w=4):
    dr.line([p,q],fill=col,width=w)
    a=math.atan2(q[1]-p[1],q[0]-p[0]);s=13
    dr.polygon([q,(q[0]-s*math.cos(a-0.45),q[1]-s*math.sin(a-0.45)),(q[0]-s*math.cos(a+0.45),q[1]-s*math.sin(a+0.45))],fill=col)
def dash(dr,pts,col,w=4):
    for p,q in zip(pts,pts[1:]):
        n=max(2,int(math.dist(p,q)//14))
        for i in range(0,n,2):
            a=i/n;b=min((i+1)/n,1)
            dr.line([(p[0]+(q[0]-p[0])*a,p[1]+(q[1]-p[1])*a),(p[0]+(q[0]-p[0])*b,p[1]+(q[1]-p[1])*b)],fill=col,width=w)
def dim(dr,p,q,t,off=0,sz=15,vertical=False):
    dr.line([p,q],fill=DIM,width=2)
    for e in (p,q):
        if vertical: dr.line([(e[0]-7,e[1]),(e[0]+7,e[1])],fill=DIM,width=2)
        else: dr.line([(e[0],e[1]-7),(e[0],e[1]+7)],fill=DIM,width=2)
    tag(dr,((p[0]+q[0])/2+(off if vertical else 0),(p[1]+q[1])/2+(0 if vertical else off)),t,sz=sz)
# ---- hero
d.text((M,ROW1-28),'HERO 3/4 VIEW',font=f(FB,28),fill=GOLD,anchor='lm')
hero=Image.open(D+'raw/B3.png').convert('RGB').resize((HERO_W,HERO_H),Image.LANCZOS)
c.paste(hero,(M,ROW1))
tag(d,(M+700,ROW1+250),'LEVEL DECK + TEE',sz=18,col=(190,255,190))
tag(d,(M+620,ROW1+400),'FLIGHT 1',sz=18,col=(190,255,190));tag(d,(M+800,ROW1+330),'LANDING',sz=18,col=(190,255,190));tag(d,(M+380,ROW1+640),'FLIGHT 2',sz=18,col=(190,255,190))
tag(d,(M+330,ROW1+770),'CUP ON SAND',sz=18,col=(190,255,190));tag(d,(M+680,ROW1+790),'rock bumper',sz=16)
tag(d,(M+110,ROW1+550),'PIER',sz=18)
# ---- plan
PX=M+HERO_W+M;PW=W-PX-M
d.text((PX,ROW1-28),'TOP-DOWN PLAN  (ship ~320 x 90 studs)',font=f(FB,28),fill=GOLD,anchor='lm')
pl=Image.new('RGB',(PW,HERO_H),SAND);p=ImageDraw.Draw(pl)
S=2.1;ox,oy=PW//2+30,205   # ship centre px (low side = +y = down)
def T(x,y):return (ox+x*S,oy+y*S)
def poly(pts,**kw):p.polygon([T(*q) for q in pts],**kw)
def box(x0,y0,x1,y1,**kw):poly([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],**kw)
# water
poly([(-400,-300),(400,-300),(400,-47),(-196,-47),(-196,70),(-186,120),(-186,150),(-400,150)],fill=WATER)
# hull
hp=[]
n=28
for i in range(n+1):
    x=-160+320*i/n;t=(x+160)/320;hw=45*(1-t**3.2)**0.8;hw=min(45,hw+(10 if t<0.08 else 0))*(0.88+0.12*min(1,t*6));hp.append((x,hw))
hull=[(x,-y) for x,y in hp]+[(x,y) for x,y in reversed(hp)]
poly(hull,fill=DWOOD,outline=(40,25,15))
poly([(x*0.93,y*0.82) for x,y in hull],fill=WOOD)
for xx in range(-140,150,28):
    p.line([T(xx,-32),T(xx,32)],fill=(98,62,36),width=1)
for mx in (-60,15,95):
    q=T(mx,0);p.ellipse((q[0]-8,q[1]-8,q[0]+8,q[1]+8),fill=DWOOD,outline=(30,20,10))
# cabin (stern), door on low side
box(-152,-30,-92,26,fill=DWOOD,outline=(40,25,15))
tag(p,T(-122,-8),'CABIN',sz=15);tag(p,T(-122,10),'(spawn)',sz=13)
# outrigger platform (level deck extension) + tee pad
box(-134,26,-110,62,fill=POST2,outline=DWOOD)
box(-131,29,-113,43,fill=FELT,outline=(60,120,60))
# flight 1 (straight, south) y 62..114
box(-128,62,-116,114,fill=FELT,outline=(60,120,60),width=2)
box(-131,62,-128,114,fill=DWOOD);box(-116,62,-113,114,fill=DWOOD)
for yy in range(70,114,13):
    p.line([T(-128,yy),T(-116,yy)],fill=(80,160,80),width=1)
# landing 16x16 at Y12, y 114..130, x -130..-114 ; outer rail on south edge east part
box(-130,114,-114,130,fill=FELT,outline=(60,120,60),width=2)
box(-131,114,-129,130,fill=DWOOD);box(-115,114,-113,130,fill=DWOOD)
box(-123,129,-113,132,fill=(60,38,20))   # outer rail catches the straight shot
# flight 2: heads 30 deg west of south from landing SW corner; run 52, apron 16
hd=(-math.sin(math.radians(30)),math.cos(math.radians(30)));nd=(-hd[1],hd[0])
st=(-129,130)
def seg(a0,a1,wd,**kw):
    pts=[]
    for (aa,sg) in ((a0,-1),(a1,-1),(a1,1),(a0,1)):
        pts.append((st[0]+hd[0]*aa+nd[0]*sg*wd/2,st[1]+hd[1]*aa+nd[1]*sg*wd/2))
    poly(pts,**kw)
seg(0,52,12,fill=FELT,outline=(60,120,60),width=2)
for sg in (-1,1):
    pts=[]
    for aa,k in ((0,0),(52,0),(52,1),(0,1)):
        off=6+1.5*k if sg==1 else -6-1.5*k
        pts.append((st[0]+hd[0]*aa+nd[0]*off,st[1]+hd[1]*aa+nd[1]*off))
    poly(pts,fill=DWOOD)
seg(52,68,14,fill=FELT,outline=(60,120,60))
end=(st[0]+hd[0]*68,st[1]+hd[1]*68)
# rock bumper beside the lower end of flight 2, offset from apron
bump=(st[0]+hd[0]*44+nd[0]*-17+0,st[1]+hd[1]*44+nd[1]*-17)
bq=T(*bump);p.ellipse((bq[0]-9*S,bq[1]-8*S,bq[0]+9*S,bq[1]+8*S),fill=ROCK,outline=(80,70,64),width=2)
# pier
box(-224,20,-212,250,fill=POST2,outline=DWOOD)
for yy in range(24,250,22):
    q=T(-224,yy);p.ellipse((q[0]-5,q[1]-5,q[0]+5,q[1]+5),fill=DWOOD)
    q=T(-212,yy);p.ellipse((q[0]-5,q[1]-5,q[0]+5,q[1]+5),fill=DWOOD)
# rocks decor
for rx,ry,rr in [(-60,190,22),(-40,170,16),(-20,215,18),(10,185,12)]:
    q=T(rx,ry);p.ellipse((q[0]-rr*S,q[1]-rr*S*0.8,q[0]+rr*S,q[1]+rr*S*0.8),fill=ROCK,outline=(80,70,64))
# cup green + 12-stud clear zone
cup=(end[0]+hd[0]*32,end[1]+hd[1]*32)
cupc=T(*cup)
cr=12*S
p.ellipse((cupc[0]-28*S,cupc[1]-19*S,cupc[0]+28*S,cupc[1]+19*S),fill=FELT,outline=(60,120,60),width=3)
for i in range(0,360,12):
    a0=math.radians(i);a1=math.radians(i+6)
    p.line([(cupc[0]+cr*math.cos(a0),cupc[1]+cr*math.sin(a0)),(cupc[0]+cr*math.cos(a1),cupc[1]+cr*math.sin(a1))],fill=(255,255,255),width=2)
p.ellipse((cupc[0]-7,cupc[1]-7,cupc[0]+7,cupc[1]+7),fill=(25,25,25))
p.rectangle((cupc[0]+6,cupc[1]-30,cupc[0]+9,cupc[1]-2),fill=(235,235,235));p.polygon([(cupc[0]+9,cupc[1]-30),(cupc[0]+30,cupc[1]-23),(cupc[0]+9,cupc[1]-16)],fill=(210,50,40))
# arrows/path
tee=T(-122,36)
p.ellipse((tee[0]-6,tee[1]-6,tee[0]+6,tee[1]+6),fill=(255,255,255),outline=(0,0,0))
arrow(p,T(-122,-2),T(-122,22),DOOR,5)
dash(p,[T(-122,36),T(-122,126)],PATH,5)
dash(p,[T(-124,128),(st[0]+hd[0]*10,st[1]+hd[1]*10)] if False else [T(-122,126),T(-126,134)],PATH,5)
dash(p,[T(-126,134),T(st[0]+hd[0]*68-3,st[1]+hd[1]*68),T(*cup)],PATH,5)
# labels
tag(p,(T(-122,36)[0]+100,T(-122,36)[1]),'TEE ON DECK',col=(190,255,190),sz=16)
tag(p,(T(-122,88)[0]+130,T(-122,88)[1]),'FLIGHT 1: 12 wide, ~13 deg (Y24 to 12)',sz=15)
tag(p,(T(-114,122)[0]+120,T(-114,122)[1]),'LANDING 16x16 at Y12',sz=15)
tag(p,(T(-114,131)[0]+110,T(-114,138)[1]+10),'outer rail stops straight shot',sz=14,col=(255,200,150))
tag(p,(T(st[0]+hd[0]*30,st[1]+hd[1]*30)[0]+170,T(st[0]+hd[0]*30,st[1]+hd[1]*30)[1]+10),'FLIGHT 2: 12 wide, ~13 deg, turns ~30 deg to pier',sz=15)
tag(p,(T(*bump)[0]+105,T(*bump)[1]+34),'ROCK BUMPER',sz=14)
tag(p,(cupc[0]+150,cupc[1]),'CUP (sand), 12-stud clear zone',col=(190,255,190),sz=15)
tag(p,(T(-218,200)[0]-45,T(-218,200)[1]),'PIER',sz=16)
tag(p,T(-185,-12),'stern',sz=14);tag(p,T(175,0),'bow',sz=14)
tag(p,T(-55,0),'LEVEL main deck',sz=15)
tag(p,T(-60,-58),'door faces low (sand) side',sz=14,col=(255,160,150))
tag(p,T(60,190),'ROCK SHELF (decor, no ball)',sz=14)
tag(p,T(-300,-80),'lagoon',sz=15)
# dimension: ship length + beam
a=T(-160,-72);b=T(160,-72);dim(p,a,b,'~320 studs',off=-16)
dim(p,T(210,-45),T(210,45),'~90',off=34,vertical=True)
dim(p,T(-96,62),T(-96,114),'~52 run',off=0,vertical=True,sz=14)
p.rectangle((0,0,PW-1,HERO_H-1),outline=(10,15,22),width=3)
tag(p,(PW-90,HERO_H-18),'PLAN',sz=14,col=GOLD)
c.paste(pl,(PX,ROW1))
# ---- side section (cross-section along ball line: ship centreline -> low side -> sand)
d.text((M,SEC_Y+22),'SIDE SECTION along the shot line  (looking along the ship; low side and sand to the right)',font=f(FB,28),fill=GOLD,anchor='lm')
SW=W-2*M;sec=Image.new('RGB',(SW,SEC_H),(32,46,64));s=ImageDraw.Draw(sec)
K=6.6
X0=330;GY=SEC_H-70   # s=0 (ship centreline) px, ground y px
SX=lambda v:X0+v*K;SY=lambda v:GY-v*K
# sky gradient
for yy in range(SEC_H):
    t=yy/SEC_H;s.line([(0,yy),(SW,yy)],fill=(int(70+120*t),int(60+80*t),int(110+10*t)))
# water to the left? no: sand ground
s.rectangle((0,GY,SW,SEC_H),fill=SAND)
s.line([(0,GY),(SW,GY)],fill=(150,110,60),width=3)
# hull section, rotated 15deg cw about lower-right bilge
local=[(-45,62),(-42,30),(-30,8),(-12,0),(12,0),(30,8),(42,30),(45,62)]
ang=math.radians(15);pv=(30,8)
def rt(x,y):
    rx,ry=x-pv[0],y-pv[1]
    return (pv[0]+rx*math.cos(ang)+ry*math.sin(ang),pv[1]-rx*math.sin(ang)+ry*math.cos(ang))
rp=[rt(*q) for q in local]
miny=min(q[1] for q in rp);dy=-4-miny;dx=8
wp=[(q[0]+dx,q[1]+dy) for q in rp]
def inner(q):return q
s.polygon([(SX(a),SY(b)) for a,b in wp]+[(SX(wp[0][0]+4),SY(wp[0][1]-2))][:0],fill=DWOOD,outline=(40,25,15))
# interior hollow
inn=[(a*0.0,b) for a,b in []]
# deck at Y=24 level, from hull left to outrigger end
# find hull left/right x at y=24
def xat(side):
    pts=wp if side=='L' else wp
    return None
Ldeck=-40;Rdeck=62
s.rectangle((SX(Ldeck),SY(24),SX(Rdeck),SY(22)),fill=POST2,outline=DWOOD)
# struts to hull
for sx_ in (-30,0,30): s.line([(SX(sx_),SY(22)),(SX(sx_*0.6+dx*0.5),SY(2))],fill=DWOOD,width=5)
# outrigger support post
s.line([(SX(Rdeck-4),SY(22)),(SX(Rdeck-4),GY)],fill=POST,width=8)
# cabin on deck
s.rectangle((SX(-25),SY(24+30),SX(25),SY(24)),fill=DWOOD,outline=(40,25,15))
s.polygon([(SX(-28),SY(54)),(SX(0),SY(62)),(SX(28),SY(54))],fill=(100,60,34),outline=(40,25,15))
s.rectangle((SX(18),SY(24+16),SX(25),SY(24)),fill=(30,18,10)) # door
s.rectangle((SX(-14),SY(24+22),SX(-6),SY(24+14)),fill=(255,190,80))
tag(s,(SX(-5),SY(34)),'CABIN (level floor, spawn)',sz=13,col=(255,230,170))
# tilted mast
mb=(SX(-42),SY(24));mt=(SX(-15+160*math.sin(math.radians(15))*0.35),SY(24+160*0.6))
# mast tip ~160 shown cut off: draw to top with marker
mt=(SX(-42+60*math.sin(ang)),SY(24+60*math.cos(ang)))
s.line([mb,mt],fill=DWOOD,width=9);s.line([mb,mt],fill=(90,56,34),width=5)
tag(s,(mt[0],mt[1]-14),'mast leans with hull (tip ~160 above sand, cut off here)',sz=13)
# bulwark on high side
s.rectangle((SX(-43),SY(24+6),SX(-39),SY(24)),fill=DWOOD)
# tee pad on deck
s.rectangle((SX(30),SY(24+1.2),SX(42),SY(24)),fill=FELT,outline=(60,120,60))
s.ellipse((SX(36)-5,SY(26.5)-5,SX(36)+5,SY(26.5)+5),fill=(255,255,255),outline=(0,0,0))
tag(s,(SX(36),SY(24+9)),'TEE (on deck)',sz=14,col=(190,255,190))
# flights: unfolded along the ball path
run=12/math.tan(math.radians(13))   # ~52
f1=62;f1e=f1+run;lde=f1e+16;f2e=lde+run;ape=f2e+16;cx=ape+30
def ramp(x0,y0,x1,y1,col=FELT):
    s.polygon([(SX(x0),SY(y0)),(SX(x0),SY(y0-1.5)),(SX(x1),SY(y1-1.5)),(SX(x1),SY(y1))],fill=col,outline=(60,120,60))
    s.polygon([(SX(x0),SY(y0-1.5)),(SX(x1),SY(y1-1.5)),(SX(x1),SY(0)),(SX(x0),SY(0))],fill=(150,105,60),outline=DWOOD)
    s.line([(SX(x0),SY(y0+3.5)),(SX(x1),SY(y1+3.5))],fill=(80,170,80),width=4)
ramp(f1,24,f1e,12)
# landing
s.rectangle((SX(f1e),SY(12),SX(lde),SY(10.5)),fill=FELT,outline=(60,120,60))
for px_ in (f1e+2,lde-2): s.rectangle((SX(px_)-4,SY(10.5),SX(px_)+4,GY),fill=POST)
s.rectangle((SX(f1e+2),SY(12),SX(f1e+4),SY(12)),fill=DWOOD)
# outer rail on the landing (taller, catches straight shot)
s.rectangle((SX(lde)-5,SY(12+5.5),SX(lde)+5,SY(12)),fill=(60,38,20),outline=(30,20,10))
s.line([(SX(f1e),SY(12+3.5)),(SX(lde),SY(12+3.5))],fill=(80,170,80),width=4)
# flight 2 (unfolded, drawn paler: it turns ~30 deg out of this plane)
ramp(lde,12,f2e,0)
s.line([(SX(lde),SY(12+3.5)),(SX(f2e),SY(3.5))],fill=(80,170,80),width=4)
# apron + sand
s.rectangle((SX(f2e),SY(1.5),SX(ape),SY(0)),fill=FELT)
s.rectangle((SX(ape),SY(0.8),SX(cx+22),SY(0)),fill=FELT,outline=(60,120,60))
# rock bumper near bottom of flight 2
bx=f2e-14;s.polygon([(SX(bx-9),GY),(SX(bx-6),SY(7)),(SX(bx+2),SY(9)),(SX(bx+9),SY(5)),(SX(bx+10),GY)],fill=ROCK,outline=(80,70,64))
tag(s,(SX(bx+10),SY(30)),'rock bumper (beside, off the apron)',sz=13)
# cup
s.rectangle((SX(cx)-6,GY,SX(cx)+6,GY+9),fill=(25,25,25))
s.line([(SX(cx+8),SY(0)),(SX(cx+8),SY(22))],fill=(235,235,235),width=3);s.polygon([(SX(cx+8),SY(22)),(SX(cx+8)+26,SY(19)),(SX(cx+8),SY(16))],fill=(210,50,40))
tag(s,(SX(cx),GY+28),'CUP on sand (Y~0)',sz=14,col=(190,255,190))
dim(s,(SX(cx-12),SY(-12)),(SX(cx+12),SY(-12)),'12 clear each side',sz=13)
# arc labels
ax=SX(f1e);ay=SY(12)
s.arc((ax-90,ay-90,ax+90,ay+90),start=180-13,end=180,fill=(255,255,255),width=3)
tag(s,(ax-60,ay-30),'~13 deg',sz=14)
ax=SX(f2e);ay=SY(0)
s.arc((ax-90,ay-90,ax+90,ay+90),start=180-13,end=180,fill=(255,255,255),width=3)
tag(s,(ax-60,ay-30),'~13 deg',sz=14)
tag(s,(SX(f1e+8),SY(12)+34),'LANDING 16 x 16, Y12',sz=14,col=(190,255,190))
tag(s,(SX(f1e+10),SY(12)-70),'landing outer rail: a straight shot stops here',sz=14,col=(255,200,150))
tag(s,(SX(f1+26),SY(24)-48),'FLIGHT 1  12 wide, run ~52, Y24 to 12',sz=14,col=(190,255,190))
tag(s,(SX(lde+45),SY(12)-105),'FLIGHT 2 (shown unfolded, turns ~30 deg toward pier), run ~52, Y12 to 0',sz=14,col=(190,255,190))
# ground label
tag(s,(SX(95),GY+26),'sand  Y = 0',sz=14)
s.line([(SX(-48),SY(24)),(SX(70),SY(24))],fill=(255,255,255),width=1)
tag(s,(SX(52),SY(24)-22),'LEVEL deck Y~24',sz=15)
tag(s,(SX(-20),SY(-6)),'hull tilts ~15 deg (keel buried)',sz=14)
s.line([(SX(f1),GY),(SX(f1),SY(-14))],fill=DIM,width=1)
dim(s,(SX(f1),SY(-12)),(SX(f1e),SY(-12)),'~52',sz=13)
dim(s,(SX(lde),SY(-12)),(SX(f2e),SY(-12)),'~52',sz=13)
dim(s,(SX(f1e),SY(-12)),(SX(lde),SY(-12)),'16',sz=13)
dim(s,(SX(-45),SY(70)),(SX(45),SY(70)),'~90 beam',sz=14)
tag(s,(SX(62),SY(60)+16),'outrigger deck ~18 long',sz=13)
tag(s,(SX(f2e+8),SY(8)),'felt apron 16',sz=13)
tag(s,(SX(cx-5),SY(45)),'~30 studs of sand to cup',sz=14)
c.paste(sec,(M,SEC_Y+50))
# palette
py=PAL_Y
d.text((M,py),'PALETTE (Look B)',font=f(FB,26),fill=GOLD)
sw=[('wood',WOOD),('dark wood',DWOOD),('post wood',POST),('post wood light',POST2),('thatch',THATCH),('rock',ROCK),('sand',SAND),('felt',FELT),('torch flame',FLAME)]
n=len(sw);sx=(W-2*M-(n-1)*14)//n
for i,(nm,col) in enumerate(sw):
    x=M+i*(sx+14);d.rounded_rectangle((x,py+44,x+sx,py+124),radius=8,fill=col,outline=(240,240,240),width=2)
    d.text((x+sx//2,py+142),nm,font=f(FB,18),fill=(255,255,255),anchor='mm')
    d.text((x+sx//2,py+164),'%d,%d,%d'%col,font=f(F,17),fill=TXT,anchor='mm')
c.save(D+'start_ship_B3_hole1.png');print(c.size)
