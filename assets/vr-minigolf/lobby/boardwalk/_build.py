import json
from PIL import Image, ImageDraw, ImageFont
# Coordinates: studs. X=east, Z=south (Roblox convention; north = -Z), Y=up. Deck top surface Y=0. Origin = NW corner of bounds.
# yaw: degrees about +Y, 0 = facing -Z (north), 90 = facing -X (west) (Roblox CFrame.Angles(0,rad(yaw),0)).
def box(id,x,z,sx,sz,y=0,sy=1,yaw=0,**k): return dict(id=id,position=[x,y,z],size=[sx,sy,sz],yaw=yaw,**k)
J={
 "name":"Golden Hour Boardwalk Lobby","option":"C","version":1,
 "units":"studs","axes":{"x":"east","y":"up","z":"south (north = -Z)","yaw":"deg about +Y, 0 faces north (-Z)","origin":"NW corner of bounds, deck top at Y=0","position":"center of box"},
 "bounds":{"min":[0,-30,0],"max":[220,60,150],"killPlaneY":-25,"note":"Ocean plane at Y=-4 outside deck; invisible walls along bounds 40 tall"},
 "spawn":{"position":[100,0,100],"yaw":0,"radius":5,"note":"SpawnLocation top at Y=0; VR head ~Y 5. Faces course board 15 studs north. Keep 10-stud clear radius."},
 "courseSelectBoard":box("course_board",100,85,26,2,y=0,sy=10,yaw=0,cardCenterY=5.5,
   cards=[{"courseId":"lantern_grove","name":"Lantern Grove","state":"live","offsetX":-8},
          {"courseId":"sugarloaf_canyon","name":"Sugarloaf Canyon","state":"coming_soon","offsetX":0},
          {"courseId":"aurora_archipelago","name":"Aurora Archipelago","state":"coming_soon","offsetX":8}],
   interaction="laser-point or touch card; 6x8 stud cards, front faces south (+Z) toward spawn"),
 "portals":[
   box("arch_lantern_grove",45,32,16,4,y=0,sy=18,yaw=0,courseId="lantern_grove",state="live",triggerSize=[10,10,3],theme="gnarled lantern tree"),
   box("arch_sugarloaf_canyon",110,32,16,4,y=0,sy=18,yaw=0,courseId="sugarloaf_canyon",state="coming_soon",triggerSize=[10,10,3],theme="striped red sandstone"),
   box("arch_aurora_archipelago",175,32,16,4,y=0,sy=18,yaw=0,courseId="aurora_archipelago",state="coming_soon",triggerSize=[10,10,3],theme="purple ice crystal")],
 "practiceGreen":dict(**box("practice_green",145,65,34,20,y=0,sy=0.4),holes=[{"tee":[132,0.4,70],"cup":[158,0.4,60]},{"tee":[140,0.4,72],"cup":[150,0.4,58],"obstacle":"windmill at [150,0,64]"}],border="0.8 tall wooden bumper rail"),
 "shack":box("birdie_bites_shack",195,80,18,16,y=0,sy=14,yaw=90,counterFaces="west",note="Decor + emote spot; no shop"),
 "pierSeating":dict(**box("pier_seating",165,135,22,14,y=0,sy=1),seats=[[158,0,130],[172,0,130],[158,0,140],[172,0,140]],note="4 benches facing south to sunset"),
 "socialBenches":box("promenade_benches",45,95,24,10,y=0,sy=1),
 "leaderboardWall":box("leaderboard_wall",25,65,2,14,y=0,sy=10,yaw=-90,faces="east",panels=["Lantern Grove best","Daily","Weekly"]),
 "walkwayColliders":[
   box("deck_main",110,75,200,70,y=-0.5,sy=1,note="main promenade deck 10..210 x 40..110"),
   box("deck_pier",165,129,30,38,y=-0.5,sy=1,note="pier 150..180 x 110..148"),
   box("path_spawn_to_arches",100,55,10,30,y=-0.5,sy=1),
   box("sand_strip",110,20,220,40,y=-0.6,sy=1,note="beach behind arches, walkable")],
 "railings":[
   box("rail_south_w",80,110,140,0.6,y=1.75,sy=3.5,note="south deck edge 10..150"),
   box("rail_south_e",195,110,30,0.6,y=1.75,sy=3.5),
   box("rail_west",10,75,0.6,70,y=1.75,sy=3.5),
   box("rail_east",210,75,0.6,70,y=1.75,sy=3.5),
   box("rail_pier_w",150,129,0.6,38,y=1.75,sy=3.5),
   box("rail_pier_e",180,129,0.6,38,y=1.75,sy=3.5),
   box("rail_pier_s",165,148,30,0.6,y=1.75,sy=3.5)],
 "lighting":{"clockTime":18.3,"ambient":"#7A5A6E","outdoorAmbient":"#C99A7A","sunColor":"#FFB46A","fog":{"color":"#F2A57E","start":180,"end":420}},
 "comfort":["spawn faces board, no forced turn","all walk surfaces flat Y=0 except green (+0.4)","paths >= 8 studs","railings 3.5 tall on every water edge","portals: walk-in trigger + 0.4s fade, no camera motion"]}
json.dump(J,open("lobby.json","w"),indent=1)
# layout
S=6;M=60;W,H=220,150
f=lambda s:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",s)
im=Image.new("RGB",(W*S+2*M,H*S+2*M+110),(244,234,210));d=ImageDraw.Draw(im)
P=lambda x,z:(M+x*S,M+90+z*S)
def R(b,fill,lab=None,out=(60,40,20)):
    x,_,z=b["position"];sx,_,sz=b["size"]
    if b.get("yaw") in (90,-90): sx,sz=sz,sx
    d.rectangle([P(x-sx/2,z-sz/2),P(x+sx/2,z+sz/2)],fill=fill,outline=out,width=2)
    if lab: d.text((P(x,z+sz/2)[0],P(x,z+sz/2)[1]+3),lab,fill=(40,25,10),font=f(13),anchor="ma")
d.text((M,16),"Golden Hour Boardwalk - lobby layout v1 (from lobby.json)",fill=(70,45,20),font=f(28))
d.text((M,54),"220 x 150 studs | grid 10 studs (bold 50) | X east, Z south, north up | deck top Y=0",fill=(90,70,40),font=f(16))
d.rectangle([P(0,0),P(W,H)],fill=(150,200,230))
for c in J["walkwayColliders"][::-1]: R(c,(232,214,170) if "sand" in c["id"] else (214,184,140),out=(150,120,80))
for g in range(0,W+1,10): d.line([P(g,0),P(g,H)],fill=(120,110,90) if g%50==0 else (200,190,170),width=1)
for g in range(0,H+1,10): d.line([P(0,g),P(W,g)],fill=(120,110,90) if g%50==0 else (200,190,170),width=1)
for g in range(0,W+1,50): d.text(P(g,-4),str(g),fill=(60,40,20),font=f(12),anchor="mb")
for g in range(0,H+1,50): d.text(P(-2,g),str(g),fill=(60,40,20),font=f(12),anchor="rm")
for r in J["railings"]: R(r,(90,55,25),out=(90,55,25))
R(J["practiceGreen"],(110,190,90),"Practice green (2 holes, windmill)")
for h in J["practiceGreen"]["holes"]:
    for k,c in (("tee",(255,255,255)),("cup",(0,0,0))):
        x,_,z=h[k];d.ellipse([P(x-1,z-1),P(x+1,z+1)],fill=c)
R(J["shack"],(240,140,90),"Birdie Bites shack");R(J["pierSeating"],(240,170,120),"Pier seating")
for s in J["pierSeating"]["seats"]: R(box("",s[0],s[2],6,2),(120,80,40))
R(J["socialBenches"],(240,170,120),"Benches");R(J["leaderboardWall"],(150,100,60),"Leaderboard wall")
for p in J["portals"]:
    R(p,(170,90,220) if p["state"]=="live" else (150,130,170),p["id"].replace("arch_","")+(" (soon)" if p["state"]!="live" else ""))
    x,_,z=p["position"];t=p["triggerSize"];d.rectangle([P(x-t[0]/2,z+2),P(x+t[0]/2,z+2+t[2])],outline=(255,255,0),width=2)
R(J["courseSelectBoard"],(212,160,60),"Course-select board (faces S)")
x,_,z=J["spawn"]["position"];d.ellipse([P(x-5,z-5),P(x+5,z+5)],fill=(80,170,255),outline=(20,60,120),width=2)
d.polygon([P(x,z-9),P(x-3,z-4),P(x+3,z-4)],fill=(20,60,120));d.text((P(x,z+6)[0],P(x,z+6)[1]+2),"SPAWN (yaw 0, faces N)",fill=(20,40,90),font=f(13),anchor="ma")
y0=im.height-40;xx=M
for c,t in [((80,170,255),"Spawn"),((212,160,60),"Course board"),((170,90,220),"Portal live"),((150,130,170),"Portal soon"),((255,255,0),"Trigger"),((110,190,90),"Green"),((240,140,90),"Social"),((150,100,60),"Leaderboard"),((90,55,25),"Railing")]:
    d.rectangle([xx,y0,xx+16,y0+16],fill=c,outline=(50,35,20));d.text((xx+22,y0),t,fill=(40,25,10),font=f(14));xx+=140
d.rectangle([0,0,im.width-1,im.height-1],outline=(150,110,50),width=6)
im.save("layout_boardwalk_v1.png")
