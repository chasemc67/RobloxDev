# Generates Sugarloaf Canyon silhouette sheets from props.md envelopes (studs). Views: front=X-Y, side=Z-Y, top=X-Z.
import math, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from PIL import Image
def R(x0,y0,w,h): return [(x0,y0),(x0+w,y0),(x0+w,y0+h),(x0,y0+h)]
def C(cx,cy,r): return ("c",cx,cy,r)
def arch(w,h,t,leg,n=24):  # arch front: two legs + curved span
    pts=[(-w/2,0),(-w/2+leg,0)]
    ri=w/2-leg; 
    for i in range(n+1):
        a=math.pi-math.pi*i/n; pts.append((ri*math.cos(a), h-t-ri*.9+ri*.9*math.sin(a)))
    pts+= [(w/2-leg,0),(w/2,0)]
    for i in range(n+1):
        a=math.pi*i/n; pts.append((w/2*math.cos(a), h-t-ri*.9+(ri*.9+t)*math.sin(a)))
    return pts
def mesa(w,h,cap=.5): # flat top, slightly rounded edges, taper
    return [(-w/2,0),(w/2,0),(w/2*.86,h-cap),(w/2*.8,h),(-w/2*.8,h),(-w/2*.86,h-cap)]
P={}
def prop(name,env,note,front,side,top): P[name]=dict(env=env,note=note,f=front,s=side,t=top)
# ---- landmarks
prop("H1 trailhead_arch",[9.5,10,1.2],"Timber gate: 2 square posts (1.2) + crossbeam with sign board hung below.\nFlat-topped beam overhang 0.4 each side; no rounded arch. Reads as a ranch gate.",
 [R(-4.75,0,1.2,9),R(3.55,0,1.2,9),R(-4.75,9,9.5,1),R(-3,7,6,1.6)],[R(-.6,0,1.2,10)],[R(-4.75,-.6,9.5,1.2)])
prop("H2 headframe",[8,16,6],"Mine headframe: A-frame trestle tapering to a top sheave wheel (r1.5).\nBack-leg brace on side view; open lattice, not a solid tower.",
 [[(-4,0),(-2.8,0),(-.6,13),(.6,13),(2.8,0),(4,0),(1,14.5),(-1,14.5)],C(0,14.5,1.5)],
 [[(-3,0),(-1.8,0),(0,12),(.5,12),(.6,0),(1.8,0),(1,14.5),(-1,14.5)],R(-.3,13,.6,3)],[R(-4,-3,1.2,1.2),R(2.8,-3,1.2,1.2),R(-.8,-.8,1.6,1.6),R(-4,1.8,8,1.2)])
prop("H3 ranger_station",[10,18,10],"Raised lookout cabin on 4 stilts (cabin 8x6x8 at y8), pitched roof to 18.\nStilts + open deck underneath = strong silhouette; roof overhang 1 each side.",
 [R(-4,0,.8,8),R(3.2,0,.8,8),R(-4,8,8,6),[(-5,14),(5,14),(0,18)]],[R(-4,0,.8,8),R(3.2,0,.8,8),R(-4,8,8,6),R(-5,14,10,1.5)],[R(-5,-5,10,10),R(-4,-4,.8,.8),R(3.2,3.2,.8,.8)])
prop("H4 geode_wall",[3,14,18],"Thin rock slab (3 thick) with a cracked-open geode oval (6x8) facing the lane.\nRagged irregular top edge, crystals stay inside the outline (no spikes past 14).",
 [[(-1.5,0),(1.5,0),(1.2,12),(.4,14),(-1,13),(-1.5,11)]],[[(-9,0),(9,0),(8,10),(6,13),(3,14),(-2,12.5),(-6,13.5),(-8.5,11)],("c",0,7,3.5)],[[(-1.5,-9),(1.5,-9),(1.2,9),(-1.2,9)]])
prop("H5 echo_walls",[16,44,46],"Two tall slot walls (16 total width incl. channel) with smooth pink/cream stripe bands.\nInner faces near-vertical and smooth; tops flat with rounded lip. Keep dressing 4 back from channel rim.",
 [[(-8,0),(-2,0),(-2.3,44),(-7,43)],[(2,0),(8,0),(7,43),(2.3,44)]],[mesa(46,44,1.5)],[R(-8,-23,6,46),R(2,-23,6,46)])
prop("H6 bell_tower",[3,9,3],"Slim square bell tower: 2-post frame, bell under a small pyramid roof.\nRead the bell outline clearly at tee distance.",
 [R(-1.5,0,.5,7),R(1,0,.5,7),[(-1.5,7),(1.5,7),(0,9)],[(-.8,4.5),(.8,4.5),(.5,6.5),(-.5,6.5)]],[R(-1.5,0,.5,7),R(1,0,.5,7),[(-1.5,7),(1.5,7),(0,9)]],[R(-1.5,-1.5,3,3)])
prop("H7 rope_bridges",[8,4,32],"Plank deck with solid rope-rail parapets (4 tall); see rope_rail/skirt table for exact boxes.\nSlight visual sag only in rope ropes; deck collision stays flat.",
 [R(-2.5,0,.5,4),R(2,0,.5,4),R(-2.5,0,5,.3)],[R(-16,0,32,.3),[(-16,4),(0,3.2),(16,4),(16,3.6),(0,2.8),(-16,3.6)]],[R(-2.5,-16,5,32)])
prop("H8 gumdrops",[2.4,2.4,2.4],"Gumdrop: dome with flat base, slightly bulged sides, sugar-crystal bumps tiny.\nSame shape caps the hoodoos.",
 [[(-1.2,0),(1.2,0)]+[(1.2*math.cos(a/20*math.pi),2.4*math.sin(a/20*math.pi)**.7) for a in range(21)]],
 [[(-1.2,0),(1.2,0)]+[(1.2*math.cos(a/20*math.pi),2.4*math.sin(a/20*math.pi)**.7) for a in range(21)]],[C(0,0,1.2)])
prop("H9 pump_house",[16,8,6],"Long low shed with lean-to roof; windpump hub at [0,4.12] on its face.\nKeep it boxy, roof slopes front to back (side view).",
 [R(-8,0,16,6.5),R(-8.3,6.5,16.6,1.5)],[[(-3,0),(3,0),(3,6),(-3,8)]],[R(-8,-3,16,6)])
prop("H10 sluice_flume",[5,4,16],"Open U-channel flume on trestle legs (base at y-1.8).\nChannel walls thin (0.3), straight runs; legs every 4.",
 [[(-2.5,1),(-2.2,1),(-2.2,3.6),(2.2,3.6),(2.2,1),(2.5,1),(2.5,4),(-2.5,4)],R(-2,0,.4,1),R(1.6,0,.4,1)],[R(-8,3,16,1),R(-7,0,.4,3),R(-3,0,.4,3),R(1,0,.4,3),R(5,0,.4,3)],[R(-2.5,-8,5,16)])
prop("H11 lock_keeper_hut",[5,7,5],"Small square hut, gable roof, one door, chimney stub.\nCompact and cute; roof overhang 0.4.",
 [R(-2.1,0,4.2,4.5),[(-2.5,4.5),(2.5,4.5),(0,7)],R(1,5,.6,2)],[R(-2.1,0,4.2,4.5),R(-2.5,4.5,5,1.4)],[R(-2.5,-2.5,5,5)])
prop("H12 intake_tower",[7,16,7],"Round intake tower (d7) with crenellated or capped top, base 1.2 below felt.\nSlight taper; one band of windows; no spire.",
 [[(-3.5,0),(3.5,0),(3.2,14),(3.5,14),(3.5,16),(-3.5,16),(-3.5,14),(-3.2,14)]],[[(-3.5,0),(3.5,0),(3.2,14),(3.5,14),(3.5,16),(-3.5,16),(-3.5,14),(-3.2,14)]],[C(0,0,3.5)])
prop("H13 maze_rock",[7,4,24],"Long low rock wall: hoodoo stubs along a sandstone spine, gumdrop caps.\nFaces facing corridors square-ish (bumpers), tops lumpy.",
 [mesa(7,4,.4)],[[(-12,0),(12,0),(12,3)]+[(12-i*3,3+(.8 if i%2 else 0)) for i in range(9)]],[R(-3.5,-12,7,24)])
prop("H14 cableway_trestle",[10,11.35,1.5],"Two-legged timber trestle (A legs) with crossbeam at 11.35 carrying hinge at 10.35.\nBucket hangs 9 below hinge (see timing sheet).",
 [[(-5,0),(-3.8,0),(-2.5,10.35),(2.5,10.35),(3.8,0),(5,0),(3.5,11.35),(-3.5,11.35)]],[R(-.75,0,1.5,11.35)],[R(-5,-.75,10,1.5)])
prop("H15 sugar_dune",[30,6,34],"Broad smooth powdered-sugar dune, base at -2.2; long windward slope, crisp crest.\nOnly the outline/envelope; felt slopes come from holes.json.",
 [[(-15,0),(15,0),(10,3),(2,6),(-6,4.5)]],[[(-17,0),(17,0),(6,6),(-4,5)]],[[(-15,-12),(-5,-17),(10,-15),(15,0),(9,16),(-6,17),(-14,8)]])
prop("H16 sinkhole_rim",[3.4,.3,3.4],"Flat stone ring (outer 3.4, inner ~2.6), 0.3 high, flush-ish.\nNo raised lip that blocks the ball beyond 0.3.",
 [R(-1.7,0,3.4,.3)],[R(-1.7,0,3.4,.3)],[C(0,0,1.7),("hole",0,0,1.3)])
prop("H17 gnomon",[1.6,9,6],"Sundial gnomon: right-triangle blade 6 long rising to 9, 1.6 thick.\nCrisp straight hypotenuse; sits on r7.5 plinth (timing sheet).",
 [R(-.8,0,1.6,9)],[[(-3,0),(3,0),(-3,9)]],[R(-.8,-3,1.6,6)])
prop("H18 arch_gate",[10,13,4],"Natural sandstone arch: chunky legs (2.2), thick span; underside ≥8 over ramp.\nOrganic but flat-topped, stripe bands, not a perfect semicircle.",
 [arch(10,13,2.5,2.2)],[[(-2,0),(2,0),(1.6,13),(-1.6,13)]],[R(-5,-2,2.2,4),R(2.8,-2,2.2,4),R(-5,-2,10,4)])
# ---- timing meshes + flag
vane=[]
for k in range(4):
    a=k*math.pi/2; ca,sa=math.cos(a),math.sin(a)
    for i in range(12):
        cx=-1.1+.2*i
        H9=[3.2786,3.3349,3.3804,3.4154,3.4402,3.4551]; h=H9[min(i,11-i)]; cy=-(0.6+h/2)
        pts=[(cx-.1,cy-h/2),(cx+.1,cy-h/2),(cx+.1,cy+h/2),(cx-.1,cy+h/2)]
        vane.append([(x*ca-(y)*sa, x*sa+y*ca+4.12) for x,y in pts])
prop("H9 windpump rotor",[8.2,8.2,.4],"4 broad lollipop vanes, 2.4 wide, radial 0.6..4.1, tips circularly clipped.\nHub at y4.12 (pivot). Collision = 12 strips 0.2 wide per vane (holes.json); vanes flat 0.4 thick.",
 vane+[C(0,4.12,.6)],[R(-.2,0,.4,8.24)],[R(-4.1,-.2,8.2,.4)])
prop("H6 sluice_gate",[7,1,.6],"Timber board 7 long, 1 tall, 0.6 thick, 45° pointed ends in plan (top view).\nPivot = bottom centre; slides 7 west into wall pocket.",
 [R(-3.5,0,7,1)],[R(-.3,0,.6,1)],[[(-3.5,0),(-3.2,-.3),(3.2,-.3),(3.5,0),(3.2,.3),(-3.2,.3)]])
prop("H11 lock_gate + deck + lip",[3.6,1.2,.5],"Gate leaf 3.6x1.2x0.5 (sinks 1.3). Deck felt 3.2x3.35x0.15 (dashed in top).\nQuay lip 3.6x1.5x0.2 red/cream stripes. Gate 4.33 st/s, dwell down 5.5/up 4.6 (10.7s);\ndeck rise 6.1-7.1, top 7.1-9.1; lip flush 7.0-9.2.",
 [R(-1.8,0,3.6,1.2)],[R(-.25,0,.5,1.2),R(-4,0,3.35,.15)],[R(-1.8,-.25,3.6,.5),R(-1.6,-3.85,3.2,3.35)])
prop("H14 ore_bucket",[2.1,11.35,1.8],"Tapered ore bucket 2.1x2x1.8 on 9-stud hanger, curved rocker skid (14 strips 0.15x0.15,\n0.27..0.41 deep) under it; low point 0.06 above felt, bucket bottom 0.35.",
 [R(-.1,2.35,.2,9),[(-1.05,.35),(1.05,.35),(1.05,2.35),(-1.05,2.35)],[(-1.05, 0.0794), (-0.9, -0.0254), (-0.75, -0.0374), (-0.6, -0.0473), (-0.45, -0.055), (-0.3, -0.0604), (-0.15, -0.0637), (0.0, -0.0637), (0.15, -0.0604), (0.3, -0.055), (0.45, -0.0473), (0.6, -0.0374), (0.75, -0.0254), (0.9, 0.0794), (1.05, 0.35), (-1.05, 0.35)]],[R(-.1,2.35,.2,9),[(-.8,.35),(.8,.35),(.9,2.35),(-.9,2.35)],R(-.075,.35-.4137,.15,.4137)],[R(-1.05,-.9,2.1,1.8)])
prop("H17 shadow_arm x4",[23,.9,23],"4 low slate bars r8.2..11.5, 3.6 wide, 0.9 tall around plinth r7.5.\nSquare ends; plinth = 48-strip disc.",
 [R(-11.5,0,3.3,.9),R(8.2,0,3.3,.9),R(-7.5,0,15,.6)],[R(-11.5,0,3.3,.9),R(8.2,0,3.3,.9),R(-7.5,0,15,.6)],
 [C(0,0,7.5),R(8.2,-1.8,3.3,3.6),R(-11.5,-1.8,3.3,3.6),R(-1.8,8.2,3.6,3.3),R(-1.8,-11.5,3.6,3.3)])
prop("Flag (all holes)",[2.15,7.5,.15],"Pole 7.5 tall, d0.15; banner 2x1.2x0.05 #e03c31 at top.\nVisual only, no collision.",
 [R(-.075,0,.15,7.5),R(.075,6.3,2,1.2)],[R(-.075,0,.15,7.5),R(-.025,6.3,.05,1.2)],[C(0,0,.075),R(.075,-.025,2,.05)])
SHEETS=[("sheet01-gates-buildings.png",["H1 trailhead_arch","H2 headframe","H3 ranger_station","H6 bell_tower","H9 pump_house","H11 lock_keeper_hut"]),
 ("sheet02-rock-landforms.png",["H4 geode_wall","H5 echo_walls","H13 maze_rock","H15 sugar_dune","H18 arch_gate","H8 gumdrops"]),
 ("sheet03-water-cable-crown.png",["H7 rope_bridges","H10 sluice_flume","H12 intake_tower","H14 cableway_trestle","H16 sinkhole_rim","H17 gnomon"]),
 ("sheet04-timing-meshes-flag.png",["H6 sluice_gate","H9 windpump rotor","H11 lock_gate + deck + lip","H14 ore_bucket","H17 shadow_arm x4","Flag (all holes)"])]
def draw(ax,shapes,title,col="#3a2a2a"):
    xs,ys=[],[]
    for s in shapes:
        if isinstance(s,tuple) and s[0] in("c","hole"):
            _,cx,cy,r=s; ax.add_patch(Circle((cx,cy),r,fc="white" if s[0]=="hole" else col,ec=col,lw=.5,zorder=3 if s[0]=="hole" else 2,alpha=1 if s[0]=="hole" else .9)); xs+=[cx-r,cx+r]; ys+=[cy-r,cy+r]
        else:
            ax.add_patch(Polygon(s,closed=True,fc=col,ec=col,lw=.5,alpha=.9)); xs+=[p[0] for p in s]; ys+=[p[1] for p in s]
    x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys); pad=max(x1-x0,y1-y0)*.15+.3
    ax.set_xlim(x0-pad,x1+pad); ax.set_ylim(y0-pad,y1+pad); ax.set_aspect("equal")
    span=max(x1-x0,y1-y0); step=[.25,.5,1,2,5,10][sum(span>t for t in (1.5,4,10,25,60))]
    ax.set_xticks([i*step for i in range(math.floor((x0-pad)/step),math.ceil((x1+pad)/step)+1)])
    ax.set_yticks([i*step for i in range(math.floor((y0-pad)/step),math.ceil((y1+pad)/step)+1)])
    ax.grid(True,lw=.4,color="#bbb"); ax.tick_params(labelsize=6)
    ax.set_title(f"{title}  {x1-x0:.2f} x {y1-y0:.2f} st (grid {step})",fontsize=7)
for fn,names in SHEETS:
    fig,axs=plt.subplots(len(names),4,figsize=(15,3.1*len(names)),gridspec_kw=dict(width_ratios=[1,1,1,1.25]))
    fig.suptitle(f"Sugarloaf Canyon — silhouettes — {fn[:-4]}   (units: studs; front=X/Y, side=Z/Y, top=X/Z, -Z = north/toward tee-lane)",fontsize=11)
    for row,n in zip(axs,names):
        p=P[n]; draw(row[0],p["f"],"FRONT"); draw(row[1],p["s"],"SIDE"); draw(row[2],p["t"],"TOP",col="#6a4a3a")
        row[3].axis("off"); e=p["env"]
        row[3].text(0,.95,n,fontsize=11,weight="bold",va="top",transform=row[3].transAxes)
        row[3].text(0,.72,f"Envelope X{e[0]} x Y{e[1]} x Z{e[2]} studs",fontsize=8,va="top",transform=row[3].transAxes)
        row[3].text(0,.55,p["note"],fontsize=8,va="top",wrap=True,transform=row[3].transAxes)
    plt.tight_layout(rect=[0,0,1,.97]); fig.savefig(fn,dpi=90); plt.close(fig)
ims=[Image.open(f) for f,_ in SHEETS]; w=600
th=[im.resize((w,int(im.height*w/im.width))) for im in ims]
H=max(t.height for t in th); cs=Image.new("RGB",(w*len(th),H),"white")
for i,t in enumerate(th): cs.paste(t,(i*w,0))
cs.save("contact.jpg",quality=85)
with open("index.md","w") as f:
    f.write("# Sugarloaf Canyon — silhouette sheets\n\nGenerated by `make_sheets.py` from `props.md` envelopes (studs). Simple Python drawing, no image gen ($0). Shapes inside envelopes are interpretive where props.md only gives a bounding box; exact collision always comes from holes.json/props.md tables.\n\nContact sheet: `contact.jpg`\n\n")
    for fn,names in SHEETS: f.write(f"- `{fn}`: "+", ".join(names)+"\n")
    f.write("\nNot drawn (no dimensions in props.md): P3 scatter (lollipop cacti, ore, crystals, hoodoo spires), mine-head world building, lift cages, gondola cabin, dam (boxes given in table), Old Sugarloaf terrain (formula).\n")
