from PIL import Image, ImageDraw, ImageFont
import math
R='/workspace/gameart/pirate-shipwreck/r1/'
FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SS=2
W,H=1920,1080
MX,MY,MW,MH=0,110,1520,855
base=Image.open(R+'raw/map_base1.png').convert('RGB').resize((MW*SS,MH*SS),Image.LANCZOS)
cv=Image.new('RGB',(W*SS,H*SS),(18,28,40))
cv.paste(base,(MX*SS,MY*SS))
d=ImageDraw.Draw(cv,'RGBA')
def font(p,s): return ImageFont.truetype(p,s*SS)
def P(x,y):  # display coords (819 wide) -> canvas
    k=MW/819
    return ((MX+x*k)*SS,(MY+y*k)*SS)
ZC={'wreck':(232,85,61),'beach':(242,182,50),'jungle':(47,168,79),'cave':(142,91,214)}
pads=[(1,'wreck',230,310),(2,'wreck',283,312),(3,'wreck',377,334),(4,'wreck',469,347),
(5,'beach',560,358),(6,'beach',656,369),(7,'beach',721,343),(8,'beach',713,276),(9,'beach',654,211),
(10,'jungle',541,284),(11,'jungle',470,227),(12,'jungle',367,199),(13,'jungle',287,172),(14,'jungle',211,107),
(15,'cave',290,47),(16,'cave',446,59),(17,'cave',541,114),(18,'cave',604,70)]
rest=[(199,45),(360,73),(620,156)]
# route: smooth through pad centers
pts=[(205,318)]+[(x,y) for _,_,x,y in pads]+[(604,38)]
def cr(p0,p1,p2,p3,t):
    return tuple(0.5*((2*p1[i])+(-p0[i]+p2[i])*t+(2*p0[i]-5*p1[i]+4*p2[i]-p3[i])*t*t+(-p0[i]+3*p1[i]-3*p2[i]+p3[i])*t**3) for i in range(2))
curve=[]
ext=[pts[0]]+pts+[pts[-1]]
for i in range(1,len(ext)-2):
    for k in range(24):
        curve.append(cr(ext[i-1],ext[i],ext[i+1],ext[i+2],k/24))
curve.append(pts[-1])
cp=[P(*c) for c in curve]
# dashed route with dark underlay
def dashed(pl,dash,gap,width,fill):
    acc=0;on=True;seg=[pl[0]]
    for a,b in zip(pl,pl[1:]):
        L=math.dist(a,b)
        if L==0: continue
        pos=0
        while pos<L:
            step=min((dash if on else gap)-acc,L-pos)
            x=a[0]+(b[0]-a[0])*(pos+step)/L;y=a[1]+(b[1]-a[1])*(pos+step)/L
            if on: d.line([(a[0]+(b[0]-a[0])*pos/L,a[1]+(b[1]-a[1])*pos/L),(x,y)],fill=fill,width=width)
            pos+=step;acc+=step
            if acc>=(dash if on else gap)-1e-6: on=not on;acc=0
dashed(cp,22*SS,14*SS,7*SS,(20,20,20,200))
dashed(cp,22*SS,14*SS,4*SS,(255,255,255,255))
# arrows along route
def arrow(i):
    a=cp[i];b=cp[i+6];ang=math.atan2(b[1]-a[1],b[0]-a[0]);s=11*SS
    tip=(a[0]+math.cos(ang)*s,a[1]+math.sin(ang)*s)
    l=(a[0]+math.cos(ang+2.5)*s,a[1]+math.sin(ang+2.5)*s);r=(a[0]+math.cos(ang-2.5)*s,a[1]+math.sin(ang-2.5)*s)
    d.polygon([tip,l,r],fill=(255,255,255,255),outline=(20,20,20,255))
for i in range(12,len(cp)-8,48): arrow(i)
# rest stops
for x,y in rest:
    X,Y=P(x,y);r=9*SS
    d.rounded_rectangle((X-r,Y-r,X+r,Y+r),radius=3*SS,outline=(255,255,255,255),width=2*SS,fill=(0,0,0,120))
# pads
for n,z,x,y in pads:
    X,Y=P(x,y);c=ZC[z]
    # keep-clear ring (dashed)
    rr=36*SS
    for a in range(0,360,12):
        d.arc((X-rr,Y-rr,X+rr,Y+rr),a,a+6,fill=(255,255,255,230),width=2*SS)
    r=19*SS
    d.ellipse((X-r-2*SS,Y-r-2*SS,X+r+2*SS,Y+r+2*SS),fill=(255,255,255,255))
    d.ellipse((X-r,Y-r,X+r,Y+r),fill=c+(255,))
    f=font(FB,22 if n<10 else 19)
    tc=(25,25,25,255) if z=='beach' else (255,255,255,255)
    d.text((X,Y+1*SS),str(n),font=f,fill=tc,anchor='mm')
# start / end markers
def pill(x,y,text,fill=(15,20,30,225),fg=(255,255,255),size=17,anchor='mm',outline=(255,255,255,255)):
    f=font(FB,size);X,Y=P(x,y)
    bb=d.textbbox((X,Y),text,font=f,anchor=anchor)
    pad=7*SS
    d.rounded_rectangle((bb[0]-pad,bb[1]-pad,bb[2]+pad,bb[3]+pad),radius=8*SS,fill=fill,outline=outline,width=SS)
    d.text((X,Y),text,font=f,fill=fg,anchor=anchor)
pill(108,250,'START: WRECK (mast landmark)',fill=(150,40,25,235))
pill(612,14,'FINISH: CAVE CLIFF (landmark)',fill=(90,50,160,235),size=17)
pill(742,228,'Rock arch (set piece)',size=14)
pill(504,92,'Waterfall',size=14)
pill(380,275,'Palm grove (set piece)',size=14)
pill(70,400,'Lagoon & reefs',size=14)
pill(158,25,'Rest stop (no hole)',size=12)
pill(620,176,'Rest stop',size=12)
pill(360,95,'Rest stop',size=12)
# zone brackets labels near zones
pill(430,395,'ZONE 1-4  WRECK DECK & COVE',fill=ZC['wreck']+(240,),size=14)
pill(660,405,'ZONE 5-9  BEACH',fill=ZC['beach']+(240,),fg=(20,20,20),size=14)
pill(430,150,'ZONE 10-14  JUNGLE',fill=ZC['jungle']+(240,),size=14)
pill(310,22,'ZONE 15-18  CAVE CLIFF',fill=ZC['cave']+(240,),size=14)
# header / footer / legend
d.rectangle((0,0,W*SS,MY*SS),fill=(18,28,40,255))
d.text((30*SS,34*SS),'PIRATE SHIPWRECK  -  Island route map (round 1)',font=font(FB,38),fill=(255,236,170,255),anchor='lm')
d.text((30*SS,80*SS),'One walking trail: wreck -> beach -> jungle -> cave. 18 hole pads, each on its own built plank deck or stone slab. Scenery around pads, never on them.',font=font(F,19),fill=(210,220,230,255),anchor='lm')
d.rectangle((MX*SS,(MY+MH)*SS,MW*SS,H*SS),fill=(18,28,40,255))
d.text((30*SS,(MY+MH+30)*SS),'Landmarks: the wreck mast (bottom-left) and the cave cliff (top-right) should be visible from most holes. Big pieces keep a clear ring around every pad (dashed circle).',font=font(F,18),fill=(210,220,230,255),anchor='lm')
d.text((30*SS,(MY+MH+62)*SS),'Concept map only: pad positions are approximate, hole shapes come later. Pads are flat gameplay surfaces built by the course builder, art never stands in for them.',font=font(F,18),fill=(210,220,230,255),anchor='lm')
# legend
LX=MW+20
d.text((LX*SS,40*SS),'LEGEND',font=font(FB,28),fill=(255,236,170,255),anchor='lm')
y=95
zones=[('wreck','1-4  Wreck & cove','Plank-deck pad beside the hull, then cove pads along the sand'),
('beach','5-9  Beach','Open shoreline, rocks, driftwood, crabs'),
('jungle','10-14  Jungle','Palm grove, boot tree, flytrap, vines'),
('cave','15-18  Cave cliff','Stairs up the cliff, cave mouth, bone throne')]
for k,t,sub in zones:
    r=19*SS;X=(LX+22)*SS;Y=y*SS
    d.ellipse((X-r-2*SS,Y-r-2*SS,X+r+2*SS,Y+r+2*SS),fill=(255,255,255,255));d.ellipse((X-r,Y-r,X+r,Y+r),fill=ZC[k]+(255,))
    d.text(((LX+58)*SS,(y-10)*SS),t,font=font(FB,20),fill=(255,255,255,255),anchor='lm')
    # wrap sub
    words=sub.split();lines=[];cur=''
    for w in words:
        if d.textlength(cur+' '+w,font=font(F,15))<300*SS: cur=(cur+' '+w).strip()
        else: lines.append(cur);cur=w
    lines.append(cur)
    for i,l in enumerate(lines): d.text(((LX+58)*SS,(y+10+i*18)*SS),l,font=font(F,15),fill=(190,200,215,255),anchor='lm')
    y+=88
# symbols
y+=5
d.ellipse(((LX+22-19)*SS,(y-19)*SS,(LX+22+19)*SS,(y+19)*SS),outline=(255,255,255,255),width=2*SS)
d.text(((LX+58)*SS,y*SS),'Keep-clear ring around each pad',font=font(F,16),fill=(255,255,255,255),anchor='lm');y+=50
dashed([((LX+5)*SS,y*SS),((LX+40)*SS,y*SS)],12*SS,8*SS,4*SS,(255,255,255,255))
d.text(((LX+58)*SS,y*SS),'Walking trail (direction of play)',font=font(F,16),fill=(255,255,255,255),anchor='lm');y+=40
X=(LX+22)*SS;r=9*SS
d.rounded_rectangle((X-r,y*SS-r,X+r,y*SS+r),radius=3*SS,outline=(255,255,255,255),width=2*SS,fill=(0,0,0,120))
d.text(((LX+58)*SS,y*SS),'Rest stop, no hole (gag props)',font=font(F,16),fill=(255,255,255,255),anchor='lm');y+=55
d.text((LX*SS,y*SS),'Set pieces (3D hero):',font=font(FB,18),fill=(255,236,170,255),anchor='lm');y+=30
for t in ['Wreck with tall mast (start)','Cave cliff with waterfall (finish)','Rock arch on the east shore','Palm grove in the jungle core','Gag props, see gag sheet']:
    d.text(((LX+10)*SS,y*SS),'- '+t,font=font(F,16),fill=(220,228,240,255),anchor='lm');y+=26
cv.resize((W,H),Image.LANCZOS).save(R+'map-overhead.png')
