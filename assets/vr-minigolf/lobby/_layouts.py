from PIL import Image, ImageDraw, ImageFont
import math
F="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def f(s):
    try: return ImageFont.truetype(F,s)
    except: return ImageFont.load_default()
S=7  # px per stud
COL=dict(spawn=(80,170,255),menu=(212,160,60),portal=(170,90,220),green=(110,190,90),social=(240,140,90),lb=(150,100,60),path=(225,205,165))
def make(name,title,size,ground,items,paths):
    W,H=size; M=60
    im=Image.new("RGB",(W*S+2*M,H*S+2*M+90),(244,234,210)); d=ImageDraw.Draw(im)
    P=lambda x,y:(M+x*S,M+90+y*S)
    d.text((M,18),title,fill=(70,45,20),font=f(30)); d.text((M,56),f"{W} x {H} studs   grid = 20 studs   north = up",fill=(90,70,40),font=f(18))
    for kind,shape in ground:
        c={"grass":(196,222,160),"deck":(214,184,140),"void":(190,215,240),"water":(150,200,230),"sand":(232,214,170)}[kind]
        if shape[0]=="r": d.rectangle([P(*shape[1:3]),P(*shape[3:5])],fill=c,outline=(120,100,70))
        else: x,y,r=shape[1:]; d.ellipse([P(x-r,y-r),P(x+r,y+r)],fill=c,outline=(120,100,70))
    for g in range(0,W+1,20): d.line([P(g,0),P(g,H)],fill=(0,0,0,0) if False else (225,215,190),width=1)
    for g in range(0,H+1,20): d.line([P(0,g),P(W,g)],fill=(225,215,190),width=1)
    for a,b in paths: d.line([P(*a),P(*b)],fill=COL["path"],width=8*S//2)
    for k,x,y,w,h,lab in items:
        d.rectangle([P(x-w/2,y-h/2),P(x+w/2,y+h/2)],fill=COL[k],outline=(50,35,20),width=2)
        d.text((P(x,y)[0],P(x,y+h/2)[1]+4),lab,fill=(40,25,10),font=f(15),anchor="ma")
    d.rectangle([0,0,im.width-1,im.height-1],outline=(150,110,50),width=6)
    lx=im.width-230
    for i,(k,t) in enumerate([("spawn","Spawn"),("menu","Course-select board"),("portal","Course portal"),("green","Practice green"),("social","Social spot"),("lb","Leaderboard")]):
        d.rectangle([lx,18+i*12-0,lx+10,28+i*12],fill=COL[k]) if False else None
    # legend bottom
    y0=im.height-34;x=M
    for k,t in [("spawn","Spawn"),("menu","Course select"),("portal","Portal"),("green","Practice green"),("social","Social"),("lb","Leaderboard"),("path","Path")]:
        d.rectangle([x,y0,x+18,y0+18],fill=COL[k],outline=(50,35,20)); d.text((x+24,y0),t,fill=(40,25,10),font=f(15)); x+=150
    im.save(name)
# A treehouse: 200x160
make("layout_A_treehouse.png","A. Hollow Oak Clubhouse Plaza",(200,180),
 [("grass",("r",0,0,200,180)),("deck",("e",100,95,55)),("deck",("e",100,30,26))],
 [("spawn",100,150,10,10,"Spawn (faces N)"),("menu",100,135,24,4,"Course board"),
  ("portal",30,60,14,8,"Lantern Grove gate"),("portal",100,22,14,8,"Sugarloaf gate (soon)"),("portal",170,60,14,8,"Aurora gate (soon)"),
  ("green",42,130,40,28,"Practice green 3 holes"),("social",100,90,14,14,"Campfire ring"),("social",150,125,22,14,"Hammocks / benches"),
  ("social",100,42,24,10,"Tree deck lounge (ramp)"),("lb",128,140,10,4,"Leaderboard"),("lb",72,140,10,4,"Daily best")],
 [((100,150),(100,90)),((100,90),(30,60)),((100,90),(100,22)),((100,90),(170,60)),((100,140),(42,130)),((100,140),(150,125))])
# B islands 240x200
make("layout_B_islands.png","B. Skyward Orrery Islands",(240,200),
 [("void",("r",0,0,240,200)),("grass",("e",120,120,55)),("grass",("e",40,45,24)),("grass",("e",120,30,24)),("grass",("e",200,45,24)),("grass",("e",205,150,26)),("grass",("e",35,150,22))],
 [("spawn",120,165,10,10,"Spawn (faces N)"),("menu",120,150,26,4,"Course board"),("social",120,115,16,16,"Orrery fountain"),
  ("portal",40,40,14,8,"Lantern Grove ring"),("portal",120,25,14,8,"Sugarloaf ring (soon)"),("portal",200,40,14,8,"Aurora ring (soon)"),
  ("green",205,150,34,26,"Practice islet"),("social",35,150,22,14,"Swings / picnic"),("lb",150,150,10,4,"Leaderboard"),("lb",90,150,10,4,"Weekly")],
 [((120,120),(40,45)),((120,120),(120,30)),((120,120),(200,45)),((150,140),(205,150)),((90,140),(35,150))])
# C boardwalk 220x140
make("layout_C_boardwalk.png","C. Golden Hour Boardwalk",(220,150),
 [("water",("r",0,0,220,150)),("sand",("r",0,0,220,40)),("deck",("r",10,40,210,110)),("deck",("r",150,110,180,148))],
 [("spawn",100,100,10,10,"Spawn (faces N)"),("menu",100,85,26,4,"Course board"),
  ("portal",45,30,16,8,"Lantern Grove arch"),("portal",110,30,16,8,"Sugarloaf arch (soon)"),("portal",175,30,16,8,"Aurora arch (soon)"),
  ("green",145,65,34,20,"Practice green + windmill"),("social",195,80,18,16,"Birdie Bites shack"),("social",165,135,22,14,"Pier seating"),
  ("social",45,95,24,10,"Benches"),("lb",25,65,10,14,"Leaderboard wall")],
 [((100,100),(100,55)),((100,55),(45,30)),((100,55),(110,30)),((100,55),(175,30)),((100,100),(165,135))])
