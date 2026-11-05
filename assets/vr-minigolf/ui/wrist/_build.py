from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import random, math
random.seed(7)
S=4  # supersample
def ss(w,h): return Image.new("RGBA",(w*S,h*S),(0,0,0,0))
def down(im,w,h): return im.resize((w,h),Image.LANCZOS)
def rr(d,box,r,**k): d.rounded_rectangle([c*S for c in box],r*S,**k)
def noise(w,h,scale,seed):
    random.seed(seed); n=Image.new("L",(w//scale+2,h//scale+2))
    n.putdata([random.randint(0,255) for _ in range(n.width*n.height)])
    return n.resize((w,h),Image.BICUBIC)
W,H=1024,784
BRASS_D=(122,78,30); BRASS=(196,140,58); BRASS_L=(246,206,120)
PARCH=(250,232,198); PARCH_D=(228,196,148)
# --- card ---
mask=ss(W,H); d=ImageDraw.Draw(mask)
rr(d,(8,8,W-8,H-8),56,fill=(255,255,255,255)); outer=down(mask,W,H).split()[3]
mask=ss(W,H); d=ImageDraw.Draw(mask)
rr(d,(42,42,W-42,H-42),34,fill=(255,255,255,255)); inner=down(mask,W,H).split()[3]
# brass gradient
br=Image.new("RGB",(W,H))
bd=ImageDraw.Draw(br)
for y in range(H):
    t=y/H; k=0.5+0.5*math.cos(t*math.pi*2.2)
    bd.line([(0,y),(W,y)],fill=tuple(int(BRASS_D[i]+(BRASS_L[i]-BRASS_D[i])*(0.35+0.5*k)) for i in range(3)))
br=ImageChops.multiply(br,Image.merge("RGB",[noise(W,H,3,1).point(lambda v:220+v//8)]*3))
# bevel: highlight ring + dark ring
card=Image.new("RGBA",(W,H),(0,0,0,0)); card.paste(br,(0,0),outer)
ring=ss(W,H); d=ImageDraw.Draw(ring)
rr(d,(14,14,W-14,H-14),50,outline=(255,236,170,200),width=5)
rr(d,(36,36,W-36,H-36),38,outline=(80,46,14,255),width=8)
card=Image.alpha_composite(card,down(ring,W,H))
# rivets
rv=ss(W,H); d=ImageDraw.Draw(rv)
for x,y in [(25,25),(W-25,25),(25,H-25),(W-25,H-25),(W//2,24),(W//2,H-24)]:
    d.ellipse([(x-9)*S,(y-9)*S,(x+9)*S,(y+9)*S],fill=(92,56,18,255))
    d.ellipse([(x-7)*S,(y-8)*S,(x+5)*S,(y+4)*S],fill=(255,226,150,255))
card=Image.alpha_composite(card,down(rv,W,H))
# parchment
p=Image.new("RGB",(W,H),PARCH)
n1=noise(W,H,40,2); n2=noise(W,H,6,3)
pd=Image.new("RGB",(W,H),PARCH_D)
p=Image.composite(pd,p,Image.blend(n1,n2,0.3).point(lambda v:max(0,v-90)))
# vignette
vg=Image.new("L",(W,H),0); ImageDraw.Draw(vg).rounded_rectangle([60,60,W-60,H-60],60,fill=255)
vg=vg.filter(ImageFilter.GaussianBlur(40))
p=Image.composite(p,Image.new("RGB",(W,H),(214,170,112)),vg)
card.paste(p,(0,0),inner)
# zones (subtle inset panels)
Z=ss(W,H); d=ImageDraw.Draw(Z)
zones={"header":(80,72,W-80,212)}
ZH=223
cw=(W-80-80-28)//2
for i,name in enumerate(["par","stroke","total","best"]):
    cx=80+(i%2)*(cw+28); cy=236+(i//2)*(ZH+22)
    zones[name]=(cx,cy,cx+cw,cy+ZH)
for name,b in zones.items():
    rr(d,b,26,fill=(176,112,52,40),outline=(150,92,40,150),width=4)
    if name!="header":
        x0,y0,x1,y1=b; d.ellipse([(x0+22)*S,(y0+55)*S,(x0+134)*S,(y0+167)*S],fill=(255,244,220,170),outline=(176,112,52,170),width=4*S)
card=Image.alpha_composite(card,down(Z,W,H))
# header flourish: brass divider line under header
card.save("wrist_card_bg_nobuttons.png")
# --- icons ---
DARK=(74,40,18,255); AMB=(232,140,40,255); GOLD=(250,196,70,255); CREAM=(255,240,210,255)
def icon(fn,name):
    im=ss(128,128); d=ImageDraw.Draw(im); fn(d)
    im=down(im,128,128)
    # dark outline halo for legibility
    a=im.split()[3].filter(ImageFilter.MaxFilter(7))
    halo=Image.new("RGBA",(128,128),DARK); halo.putalpha(a)
    out=Image.alpha_composite(halo,im); return out
P=lambda pts:[(x*S,y*S) for x,y in pts]
def flag(d):
    d.rounded_rectangle([34*S,14*S,44*S,112*S],4*S,fill=CREAM)
    d.polygon(P([(44,16),(104,36),(44,58)]),fill=AMB)
    d.ellipse([20*S,100*S,96*S,120*S],fill=GOLD)
def par(d):
    d.ellipse([18*S,18*S,110*S,110*S],fill=GOLD)
    d.ellipse([34*S,34*S,94*S,94*S],fill=CREAM)
    d.ellipse([52*S,52*S,76*S,76*S],fill=AMB)
def club(d):
    d.line(P([(88,12),(52,100)]),fill=CREAM,width=12*S)
    d.rounded_rectangle([24*S,92*S,72*S,114*S],9*S,fill=GOLD)
    d.ellipse([84*S,94*S,108*S,118*S],fill=CREAM)
def star(d):
    pts=[]
    for i in range(10):
        r=52 if i%2==0 else 22; a=-math.pi/2+i*math.pi/5
        pts.append((64+r*math.cos(a),68+r*math.sin(a)))
    d.polygon(P(pts),fill=GOLD)
    d.polygon(P([(64+(r*0.55)*math.cos(-math.pi/2+i*math.pi/5),68+(r*0.55)*math.sin(-math.pi/2+i*math.pi/5)) for i,r in enumerate([52 if i%2==0 else 22 for i in range(10)])]),fill=(255,226,130,255))
def total(d):  # scorecard with tally bars
    d.rounded_rectangle([22*S,14*S,106*S,114*S],12*S,fill=CREAM)
    for k,y in enumerate([34,58,82]):
        d.rounded_rectangle([36*S,y*S,(92-k*14)*S,(y+12)*S],6*S,fill=AMB)
icons={n:icon(f,n) for n,f in [("hole",flag),("par",par),("stroke",club),("best",star),("total",total)]}
# --- pointer dot ---
im=Image.new("RGBA",(64,64),(0,0,0,0))
for r in range(32,0,-1):
    t=r/32; a=int(255*(1-t)**1.6)
    col=(255,int(150+105*(1-t)),int(40+180*(1-t)**3))
    ImageDraw.Draw(im).ellipse([32-r,32-r,32+r,32+r],fill=col+(min(255,a+ (255 if r<9 else 0)),))

# --- hover glow 9-slice 128x128, margins 40 ---
G=128; g=Image.new("L",(G,G),0); gd=ImageDraw.Draw(g)
gd.rounded_rectangle([20,20,G-21,G-21],18,outline=255,width=8)
glow=g.filter(ImageFilter.GaussianBlur(9)).point(lambda v:min(255,v*2))
core=g
alpha=ImageChops.lighter(glow,core.point(lambda v:v))
hg=Image.new("RGBA",(G,G),(255,170,60,0)); hg.putalpha(alpha)
cr=Image.new("RGBA",(G,G),(255,228,160,0)); cr.putalpha(core.filter(ImageFilter.MinFilter(3)))
hg=Image.alpha_composite(hg,cr); 
# --- mock ---
F="/usr/share/fonts/truetype/sand-box/google/Fredoka/Fredoka-VariableFont_wdth,wght.ttf"
def font(sz):
    f=ImageFont.truetype(F,sz)
    try: f.set_variation_by_name("Bold")
    except Exception: pass
    return f
NUM=(74,36,14); LAB=(156,82,24); HEAD=(255,248,232)
m=card.copy(); d=ImageDraw.Draw(m)
x0,y0,x1,y1=zones["header"]
m.alpha_composite(icons["hole"].resize((100,100),Image.LANCZOS),(x0+14,y0+20))
d.text((x0+130,y0+70),"HOLE 9",font=font(76),fill=NUM,anchor="lm")
d.text((x1-28,y0+70),"Lantern Swing",font=font(40),fill=LAB,anchor="rm")
for name,lab,val in [("par","PAR","3"),("stroke","STROKE","2"),("total","TOTAL","+1"),("best","BEST","-2")]:
    x0,y0,x1,y1=zones[name]
    m.alpha_composite(icons[name].resize((96,96),Image.LANCZOS),(x0+30,y0+63))
    d.text((x0+160,y0+78),lab,font=font(38),fill=LAB,anchor="lm")
    d.text((x0+160,y0+144),val,font=font(78),fill=NUM,anchor="lm")
m.save("wrist_card_mock_nobuttons.png")
print(zones)
