from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json, os, math
OUT='/workspace/RobloxDev/assets/vr-minigolf/sugarloaf-canyon/decals/'
F='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
WOOD=(150,96,64,255);CREAM=(255,250,244,255);INK=(48,32,72,255)
TEAL=(46,196,182,255);LILAC=(176,140,230,255);PINK=(255,128,191,255)
LIME=(160,214,52,255);AMBER=(255,184,48,255);SKY=(84,166,236,255)
S=4  # supersample
def font(px): return ImageFont.truetype(F,int(px))
def fit(d,text,maxw,px):
    while px>10:
        f=font(px); w=max(d.textbbox((0,0),l,font=f)[2] for l in text.split('\n'))
        if w<=maxw: return f
        px-=2
    return font(px)
def ctext(d,cx,y,text,maxw,px,fill,stroke=0,sf=None,sp=8):
    f=fit(d,text,maxw,px)
    d.multiline_text((cx,y),text,font=f,fill=fill,anchor='ma',align='center',spacing=sp,stroke_width=stroke,stroke_fill=sf)
    return d.multiline_textbbox((cx,y),text,font=f,anchor='ma',align='center',spacing=sp,stroke_width=stroke)[3]
def arrowpoly(cx,cy,w,h,dirn='up'):
    hw=w/2; hh=h*0.42; sw=w*0.22
    pts=[(0,-h/2),(hw,-h/2+hh),(sw,-h/2+hh),(sw,h/2),(-sw,h/2),(-sw,-h/2+hh),(-hw,-h/2+hh)]
    rot={'up':0,'right':90,'down':180,'left':270}[dirn]; a=math.radians(rot)
    return [(cx+x*math.cos(a)-y*math.sin(a), cy+x*math.sin(a)+y*math.cos(a)) for x,y in pts]
def finish(img,size,name):
    img=img.resize(size,Image.LANCZOS); p=OUT+name
    assert not os.path.exists(p),p
    img.save(p); return name
def glow(img,shape_draw,blur):
    m=Image.new('L',img.size,0); shape_draw(ImageDraw.Draw(m)); m=m.filter(ImageFilter.GaussianBlur(blur))
    g=Image.new('RGBA',img.size,INK[:3]+(0,)); g.putalpha(m.point(lambda v:int(v*0.75)))
    return Image.alpha_composite(img,g)
def sign(name,size,aspect,title,sub,col,arrow='up',icon=None):
    H=1024*S//2; W=int(H*aspect)
    img=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    r=int(W*0.06); b=int(W*0.045)
    d.rounded_rectangle([0,0,W-1,H-1],r,fill=WOOD)
    d.rounded_rectangle([b,b,W-1-b,H-1-b],int(r*0.8),fill=col)
    i=b+int(W*0.03); d.rounded_rectangle([i,i,W-1-i,H-1-i],int(r*0.6),fill=CREAM)
    y=ctext(d,W/2,H*0.05,title,W*0.8,W*0.17,col,stroke=int(W*0.006),sf=col,sp=int(W*0.01))
    if sub: ctext(d,W/2,y+H*0.03,sub,W*0.8,W*0.12,INK,sp=int(W*0.01))
    if icon: icon(d,W/2,H*0.62,W*0.22)
    if arrow:
        aw=W*0.5; ah=W*0.5
        d.polygon(arrowpoly(W/2,H*0.82,aw,ah,arrow),fill=col,outline=INK,width=max(2,S))
    return finish(img,size,name)
def plank(name,size,aspect,title,sub,col):
    W=1024*S//2; H=int(W/aspect)
    img=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    b=int(H*0.08); d.rounded_rectangle([0,0,W-1,H-1],int(H*0.12),fill=WOOD)
    d.rounded_rectangle([b,b,W-1-b,H-1-b],int(H*0.1),fill=col)
    i=b+int(H*0.05); d.rounded_rectangle([i,i,W-1-i,H-1-i],int(H*0.08),fill=CREAM)
    y=ctext(d,W/2,H*0.2,title,W*0.85,H*0.36,col,stroke=int(H*0.012),sf=INK)
    ctext(d,W/2,y+H*0.04,sub,W*0.85,H*0.2,INK)
    return finish(img,size,name)
def felt(name,size,aspect,label,col,kind='up',icon=None):
    H=640*S//2*2//2*2//2; H=1280; W=int(H*aspect)
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    ah=H*0.58; aw=W*0.8
    if kind=='up': poly=[arrowpoly(W/2,H*0.05+ah/2,aw,ah)]
    elif kind=='bank': poly=None
    def shape(dd,fill=255,outline=None,width=0):
        if kind=='up':
            dd.polygon(poly[0],fill=fill,outline=outline,width=width)
        else:  # S-curve: right then left, heading up
            pts=[]; n=60; amp=W*0.18; sw=W*0.11
            for k in range(n+1):
                t=k/n; y=H*0.6-t*H*0.4; x=W/2+amp*math.sin(t*2*math.pi)
                pts.append((x,y))
            [dd.ellipse([x-sw,y-sw,x+sw,y+sw],fill=fill) for x,y in [(pts[j][0]+(pts[j+1][0]-pts[j][0])*q/8,pts[j][1]+(pts[j+1][1]-pts[j][1])*q/8) for j in range(n) for q in range(8)]]
            tx,ty=pts[-1]; hw=W*0.3
            dd.polygon([(tx,ty-H*0.2),(tx+hw,ty+H*0.02),(tx-hw,ty+H*0.02)],fill=fill)
            if outline: pass
    img=glow(img,lambda dd:shape(dd,255),W*0.03)
    d=ImageDraw.Draw(img)
    if kind=='up':
        shape(d,CREAM); 
        # inner fill inset
        sc=0.93; cx,cy=W/2,H*0.05+ah/2
        d.polygon([(cx+(x-cx)*sc,cy+(y-cy)*sc) for x,y in poly[0]],fill=col)
    else:
        m=Image.new('L',img.size,0); shape(ImageDraw.Draw(m),255)
        e=m.resize((m.width//4,m.height//4)).filter(ImageFilter.MinFilter(5)).resize(m.size)
        img.paste(Image.new('RGBA',img.size,CREAM),(0,0),m); img.paste(Image.new('RGBA',img.size,col),(0,0),e); d=ImageDraw.Draw(img)
    if icon: icon(d,W/2,H*0.36,W*0.15)
    ctext(d,W/2,H*0.66,label,W*0.92,W*0.19,CREAM,stroke=int(W*0.02),sf=INK,sp=4)
    return finish(img,size,name)
def clock(d,cx,cy,r):
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=CREAM,outline=INK,width=int(r*0.15))
    d.line([(cx,cy),(cx,cy-r*0.65)],fill=INK,width=int(r*0.14)); d.line([(cx,cy),(cx+r*0.5,cy)],fill=INK,width=int(r*0.14))
def splash(d,cx,cy,r):
    for k in range(5):
        a=math.radians(-150+k*30); x=cx+math.cos(a)*r*0.9; y=cy+math.sin(a)*r*0.9
        d.ellipse([x-r*0.18,y-r*0.28,x+r*0.18,y+r*0.12],fill=SKY)
    d.ellipse([cx-r*1.1,cy,cx+r*1.1,cy+r*0.5],fill=SKY)
    d.ellipse([cx-r*0.7,cy+r*0.05,cx+r*0.7,cy+r*0.3],fill=CREAM)
def chev_strip(name,size,aspect,col,alpha,count,direction):
    H=512; W=int(H*aspect)
    img=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    c=col[:3]+(alpha,); o=CREAM[:3]+(alpha,)
    step=W/count
    for k in range(count):
        cx=step*(k+0.5)
        if direction=='up':
            w=min(step*0.7,H*1.0); h=H*0.55; t=H*0.17; y0=H*0.2
            pts=[(cx-w/2,y0+h),(cx,y0),(cx+w/2,y0+h),(cx+w/2-t*0.9,y0+h+0.0),(cx,y0+t*1.4),(cx-w/2+t*0.9,y0+h)]
        else:  # right, along long axis
            h=H*0.7; w=h*0.5; t=h*0.22; y0=(H-h)/2; x0=cx-w/2
            pts=[(x0,y0),(x0+t,y0),(x0+w+t,H/2),(x0+t,y0+h),(x0,y0+h),(x0+w,H/2)]
        d.polygon(pts,fill=c,outline=o,width=6)
    return finish(img,size,name)
def flood(name,size):
    W,H=768,1024
    img=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    for y,yr,a in [(330,'1927',230),(520,'1983',200),(690,'2019',180)]:
        d.rectangle([40,y,W-40,y+14],fill=SKY[:3]+(a,))
        for x in range(60,W-60,60): d.polygon([(x,y+14),(x+30,y+14),(x+15,y+36)],fill=SKY[:3]+(a,))
        f=font(60); d.text((W-60,y-10),yr,font=f,fill=CREAM,anchor='rb',stroke_width=5,stroke_fill=INK)
        d.text((60,y-10),'HIGH WATER',font=font(40),fill=CREAM,anchor='lb',stroke_width=4,stroke_fill=INK)
    # enamel plaque
    d.rounded_rectangle([110,40,W-110,250],36,fill=INK); d.rounded_rectangle([124,54,W-124,236],28,fill=SKY)
    d.rounded_rectangle([138,68,W-138,222],22,fill=CREAM)
    ctext(d,W/2,84,'FLASH FLOOD\nZONE',W-300,72,INK,sp=6)
    for cx in (156,W-156): d.ellipse([cx-8,145-8,cx+8,145+8],fill=INK)
    return finish(img,size,name)

M={}
M['sign_left']=sign('h02_sign_short_cut.png',(512,1024),1.8/3.2,'SHORT\nCUT','Tight!',LIME,'left')
M['sign_mid']=plank('h02_sign_dead_end.png',(1024,256),3.0,'DEAD END','No gold this way',AMBER)
M['sign_right']=sign('h02_sign_long_haul.png',(512,1024),1.8/3.2,'LONG\nHAUL','Safe - firm putt',LIME,'right')
M['felt_arrow_left']=felt('h02_felt_arrow_short_cut.png',(512,1024),0.7,'SHORT\nCUT',LIME)
M['felt_arrow_right']=felt('h02_felt_arrow_long_haul.png',(512,1024),0.7,'LONG\nHAUL',LIME)
M['sign_plank']=sign('h03_sign_log_plank.png',(512,1024),1.6/2.6,'LOG\nPLANK','No rails!',AMBER,'up',splash)
M['sign_bridge']=sign('h03_sign_footbridge.png',(512,1024),1.8/3.2,'FOOT-\nBRIDGE','The safe way',TEAL,'up')
M['route_arrow_plank']=felt('h03_route_arrow_plank.png',(512,1024),0.7,'RISKY\nPLANK',AMBER)
M['route_arrow_bridge']=felt('h03_route_arrow_bridge.png',(512,1024),0.7,'SAFE\nBRIDGE',TEAL)
M['sign_overflow']=sign('h06_sign_overflow.png',(512,1024),1.8/3.2,'OVER-\nFLOW','The long way round',SKY,'up')
M['felt_arrow_overflow']=felt('h06_felt_arrow_overflow.png',(512,1024),0.7,'OVERFLOW',SKY)
M['flood_marks']=flood('h06_flood_marks.png',(512,1024))
M['felt_arrow_deck']=felt('h10_felt_arrow_one_way.png',(512,1024),0.8,'ONE\nWAY',AMBER)
M['felt_arrow_lock']=felt('h11_felt_arrow_lock.png',(512,1024),0.7,'WAIT FOR\nGATE',SKY,icon=clock)
M['sign_pier']=sign('h12_sign_intake.png',(512,1024),1.6/2.6,'INTAKE','Shoot the pipe!',SKY,'up')
M['sign_shore']=sign('h12_sign_shoreline.png',(512,1024),1.8/3.2,'SHORE-\nLINE\nTRAIL','',TEAL,'up')
M['felt_arrow_pier']=felt('h12_felt_arrow_pier.png',(512,1024),0.7,'PIPE',SKY)
M['felt_arrow_shore']=felt('h12_felt_arrow_shore.png',(512,1024),0.7,'SHORE',TEAL)
M['sign_west']=sign('h13_sign_west.png',(512,1024),1.8/3.2,'LONG &\nEASY','',TEAL,'up')
M['sign_centre']=sign('h13_sign_centre.png',(512,1024),1.8/3.2,'STRAIGHT\nTHROUGH','Mind the hoodoos!',AMBER,'up')
M['sign_east']=sign('h13_sign_east.png',(512,1024),1.8/3.2,'SCENIC\nROUTE','',LILAC,'up')
M['route_arrow_west']=felt('h13_route_arrow_west.png',(512,1024),0.7,'SAFE\nWEST',TEAL)
M['route_arrow_centre']=felt('h13_route_arrow_centre.png',(512,1024),0.7,'SHORT\nCENTRE',AMBER)
M['route_arrow_east']=felt('h13_route_arrow_east.png',(512,1024),0.7,'SCENIC\nEAST',LILAC)
M['slope_arrows']=chev_strip('h15_slope_arrows.png',(2048,256),10.0,CREAM,110,10,'right')
M['lip_chevrons']=chev_strip('h15_lip_chevrons.png',(1024,128),7.0,AMBER,255,7,'up')
M['felt_arrow_sink']=felt('h16_felt_arrow_sink.png',(512,1024),0.7,'SINK-\nHOLE',PINK)
M['sign_rim']=sign('h18_sign_rim_trail.png',(512,1024),1.8/3.2,'RIM\nTRAIL','',LILAC,'up')
M['felt_arrow_bank']=felt('h18_felt_arrow_bank.png',(512,1024),2.0/2.6,'BANK IT',LILAC,kind='bank')
json.dump(M,open('/workspace/gameart/sc-decals/manifest_tmp.json','w'),indent=1)
print(len(M))
