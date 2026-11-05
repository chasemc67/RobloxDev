import math
from PIL import Image, ImageDraw, ImageFont
D='/workspace/gameart/pirate-shipwreck/r4-start-ship/'
FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';F='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
f=lambda p,s:ImageFont.truetype(p,s)
BG=(18,28,40);GOLD=(255,236,170);TXT=(225,232,242)
WOOD=(110,70,40);DWOOD=(80,50,30);POST=(100,72,50);POST2=(122,90,64);THATCH=(200,165,90);ROCK=(115,100,92);SAND=(226,184,128);FELT=(105,185,98);FLAME=(240,110,30)
CW,CH=800,600; M=30; W=3*CW+4*M
HEAD=110; LAB=70; DESC=150; PLANH=360; PAL=190
H=HEAD+LAB+CH+DESC+PLANH+PAL+60
c=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(c)
d.text((M,40),'START SHIP: 3 OPTIONS  (Pirate Shipwreck, Look B Golden Hour Hideaway)',font=f(FB,38),fill=GOLD,anchor='lm')
d.text((M,84),'Player spawns in the captain\'s cabin, walks out onto the deck, then down a gangplank to the pad 1 tee. Hull intact, no hole. Ship ~320 long x 90 wide x 60 tall studs, mast tip ~160, deck ~Y24.',font=f(F,20),fill=(210,220,230),anchor='lm')
def wrap(t,ft,w):
    out=[];cur=''
    for x in t.split():
        if d.textlength((cur+' '+x).strip(),font=ft)<=w: cur=(cur+' '+x).strip()
        else: out.append(cur);cur=x
    out.append(cur);return out
opts=[
('A','UPRIGHT GALLEON','Level beached galleon, stern cabin at the left. Door opens forward onto the main deck, then a long straight gangplank drops off the midship sand side to the tee. Most readable, easiest to build and collide.'),
('B','LISTING SHIP + RAMP','Ship leans ~15 degrees on the sand, cabin raised at the stern. Door opens onto a short stair, then a wide slanted ramp-gangplank down the low side to the tee. Most dramatic silhouette, most "shipwreck".'),
('C','SHIP ON ROCKY JETTY','Bow rests on a rock shelf, stern floats in the lagoon. Cabin door faces a wooden pier; midship gangplank to the pier, then a lantern dock walk to the tee on the sand. Most variety: water, rock and dock.')]
def hull(cx,cy,L,Wd,ang):
    # pointed bow on +x
    pts=[(-L/2,-Wd/2*0.8),(L*0.18,-Wd/2),(L/2,0),(L*0.18,Wd/2),(-L/2,Wd/2*0.8)]
    a=math.radians(ang);return [(cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a)) for x,y in pts]
def rot(cx,cy,x,y,ang):
    a=math.radians(ang);return (cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a))
def arrow(dr,p,q,col,w=4):
    dr.line([p,q],fill=col,width=w)
    a=math.atan2(q[1]-p[1],q[0]-p[0]);s=12
    dr.polygon([q,(q[0]-s*math.cos(a-0.45),q[1]-s*math.sin(a-0.45)),(q[0]-s*math.cos(a+0.45),q[1]-s*math.sin(a+0.45))],fill=col)
def dash(dr,pts,col,w=4):
    for p,q in zip(pts,pts[1:]):
        n=int(math.dist(p,q)//14)
        for i in range(0,n,2):
            a=i/n;b=min((i+1)/n,1)
            dr.line([(p[0]+(q[0]-p[0])*a,p[1]+(q[1]-p[1])*a),(p[0]+(q[0]-p[0])*b,p[1]+(q[1]-p[1])*b)],fill=col,width=w)
def tag(dr,xy,t,col=(255,255,255),sz=15,anchor='mm'):
    ft=f(FB,sz);b=dr.textbbox(xy,t,font=ft,anchor=anchor)
    dr.rounded_rectangle((b[0]-5,b[1]-3,b[2]+5,b[3]+3),radius=5,fill=(15,20,30));dr.text(xy,t,font=ft,fill=col,anchor=anchor)
S=1.65
def hullpts(n=24):
    pts=[]
    # stern flat-ish rounded (x=-160) to pointed bow (x=+160); half width 45
    for i in range(n+1):
        x=-160+320*i/n
        t=(x+160)/320
        hw=45*(1-t**3.2)**0.8 if t>0.0 else 40
        hw=min(45,hw+ (10 if t<0.08 else 0))*(0.88+0.12*min(1,t*6))
        pts.append((x,-hw))
    return pts+[(x,-y) for x,y in reversed(pts)]
def plan(k):
    w=CW;h=PLANH-30
    im=Image.new('RGB',(w,h),SAND);p=ImageDraw.Draw(im)
    PATH=(255,230,80);DOOR=(255,60,50)
    ox,oy,ang={'A':(400,120,0),'B':(390,125,-9),'C':(330,110,0)}[k]
    T=lambda x,y:rot(ox,oy,x*S,y*S,ang)
    def poly(pts,**kw):p.polygon([T(*q) for q in pts],**kw)
    def box(x0,y0,x1,y1,**kw):poly([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],**kw)
    # water
    if k=='A': p.rectangle((0,0,w,170),fill=(60,150,170))
    if k=='B':
        p.polygon([(0,0),(w,0),(w,95),(0,185)],fill=(60,150,170))
    if k=='C':
        p.rectangle((0,0,w,200),fill=(60,150,170))
        p.polygon([(560,0),(w,0),(w,205),(600,205),(520,120),(540,60)],fill=ROCK,outline=(80,70,64))
    # sand wet edge
    # hull
    poly(hullpts(),fill=DWOOD,outline=(40,25,15))
    # deck (inset)
    poly([(x*0.93,y*0.82) for x,y in hullpts()],fill=WOOD)
    # deck planks
    for xx in range(-140,140,28):
        a1=T(xx,-30);a2=T(xx,30);p.line([a1,a2],fill=(98,62,36),width=1)
    # masts
    for mx in (-70,10,95): 
        q=T(mx,0);p.ellipse((q[0]-7,q[1]-7,q[0]+7,q[1]+7),fill=DWOOD,outline=(30,20,10))
    # cabin (stern)
    cab=(-155,-34,-100,34) if k!='B' else (110,-33,155,33)
    if k=='B': cab=(-155,-33,-108,33)
    box(*cab,fill=DWOOD,outline=(40,25,15))
    cx0=(cab[0]+cab[2])/2
    tag(p,T(cx0,0),'CABIN',sz=13)
    # door on cabin forward wall, arrow
    dpos=T(cab[2],0)
    arrow(p,T(cab[2]-14,0),T(cab[2]+24,0),DOOR,4) if k!='C' else arrow(p,T(-128,10),T(-128,50),DOOR,4)
    # gangplank + path
    if k=='A':
        path=[T(cab[2]+24,0),T(10,0),T(10,45)]
        gp=[(0,40),(22,40),(22,100),(0,100)] # stud coords
        poly(gp,fill=POST2,outline=DWOOD)
        tee=(T(11,0)[0]+30,285);dash(p,path+[T(11,100),tee],PATH)
    if k=='B':
        path=[T(cab[2]+24,0),T(-60,0),T(-60,38)]
        poly([(-82,36),(-38,36),(-26,100),(-94,100)],fill=POST2,outline=DWOOD)
        tee=(T(-60,100)[0]+20,285);dash(p,path+[T(-60,95),tee],PATH)
    if k=='C':
        # pier along sand side of ship
        box(-150,48,60,68,fill=POST2,outline=DWOOD)
        for xx in range(-145,60,35):
            q=T(xx,70);p.ellipse((q[0]-4,q[1]-4,q[0]+4,q[1]+4),fill=DWOOD)
        poly([(-30,38),(-8,38),(-8,52),(-30,52)],fill=POST2,outline=DWOOD) # gangplank to pier
        tee=(T(60,58)[0]+60,285)
        # dock walk
        p.rectangle((T(60,48)[0]-1,T(60,48)[1],T(60,48)[0]+(tee[0]-T(60,48)[0])+0,T(60,48)[1]+20),fill=POST2,outline=DWOOD)
        path=[T(cab[2]+24,0),T(-100,0)]
        # door faces pier: re-aim door arrow across to pier
        p.polygon([(0,0)],fill=None) if False else None
        dash(p,[T(-128,52),T(-128,58),T(60,58),(tee[0],T(60,58)[1]),tee],PATH)
    # tee
    p.ellipse((tee[0]-60,tee[1]-34,tee[0]+60,tee[1]+34),fill=FELT,outline=(60,120,60),width=3)
    p.ellipse((tee[0]-5,tee[1]-5,tee[0]+5,tee[1]+5),fill=(30,30,30))
    p.rectangle((tee[0]+20,tee[1]-20,tee[0]+23,tee[1]+-2),fill=(235,235,235));p.polygon([(tee[0]+23,tee[1]-20),(tee[0]+40,tee[1]-14),(tee[0]+23,tee[1]-8)],fill=(210,50,40))
    tag(p,(tee[0]-70,tee[1]),'PAD 1 TEE',col=(190,255,190),sz=15,anchor='rm')
    # labels
    lab={'A':[('GANGPLANK',(T(11,70)[0]+70,T(11,70)[1])),('bow',T(165,0)),('stern',T(-175,0))],
         'B':[('RAMP',(T(-60,70)[0]+70,T(-60,70)[1])),('bow',T(168,0)),('stern',T(-175,0)),('ship tilts ~15 deg, low side toward sand',(215,232))],
         'C':[('DOCK PIER',(T(-70,80)[0],T(-70,80)[1]+18)),('GANGPLANK',(T(-19,20)[0]+78,T(-19,20)[1])),('ROCK SHELF',(660,130)),('bow',T(168,-6)),('stern',T(-178,0))]}[k]
    for t,xy in lab:tag(p,xy,t,sz=13)
    tag(p,(80,22),'lagoon',sz=13)
    p.rectangle((0,0,w-1,h-1),outline=(10,15,22),width=3)
    tag(p,(w-96,h-16),'TOP-DOWN PLAN',sz=13,col=GOLD)
    return im
for i,(k,name,desc) in enumerate(opts):
    x=M+i*(CW+M)
    y=HEAD
    d.text((x,y+LAB//2),f'OPTION {k}:  {name}',font=f(FB,32),fill=GOLD,anchor='lm')
    im=Image.open(D+f'raw/{k}.png').convert('RGB').resize((CW,CH),Image.LANCZOS)
    c.paste(im,(x,y+LAB))
    yy=y+LAB+CH+14
    for l in wrap(desc,f(F,20),CW):
        d.text((x,yy),l,font=f(F,20),fill=TXT);yy+=27
    py=y+LAB+CH+DESC
    c.paste(plan(k),(x,py))
    # legend under plan
    ly=py+PLANH-14
    d.line([(x,ly),(x+30,ly)],fill=(255,230,80),width=4);d.text((x+38,ly),'player path',font=f(F,15),fill=TXT,anchor='lm')
    d.line([(x+150,ly),(x+180,ly)],fill=(255,90,70),width=4);d.text((x+188,ly),'cabin door / facing',font=f(F,15),fill=TXT,anchor='lm')
# palette
py=H-PAL-20
d.text((M,py),'PALETTE (Look B)',font=f(FB,26),fill=GOLD)
sw=[('wood',WOOD),('dark wood',DWOOD),('post wood',POST),('post wood light',POST2),('thatch',THATCH),('rock',ROCK),('sand',SAND),('felt',FELT),('torch flame',FLAME)]
n=len(sw);sx=(W-2*M-(n-1)*14)//n
for i,(nm,col) in enumerate(sw):
    x=M+i*(sx+14);d.rounded_rectangle((x,py+44,x+sx,py+124),radius=8,fill=col,outline=(240,240,240),width=2)
    d.text((x+sx//2,py+142),nm,font=f(FB,18),fill=(255,255,255),anchor='mm')
    d.text((x+sx//2,py+164),'%d,%d,%d'%col,font=f(F,17),fill=TXT,anchor='mm')
c.save(D+'start_ship_options.png');print(c.size)
