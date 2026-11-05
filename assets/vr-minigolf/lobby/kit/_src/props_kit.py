"""Modular decoration built with the shared boardwalk PB/atlas pipeline; Blender Z-up."""
import sys,os,math
SRC=os.path.dirname(__file__)
sys.path.insert(0,os.path.abspath(os.path.join(SRC,'../../boardwalk/models/_src')))
import bwlib as L
from registry import prop,FRONT_NORTH
def asset(name,target,pivot='base',notes='',motion=None):
    return prop('kit_'+name,'kit',target=target,tris_max=19999,front=FRONT_NORTH,pivot=pivot,collision=[],notes=notes,motion=motion)
def box(pb,size,loc,cell='post',b=.15,part='atlas',color=None):
    pb.box(size,loc=loc,mapping=('flat',cell),bevel=b,segs=2,part=part,color=color)
def pole(pb,h=9):
    box(pb,(1.5,1.5,.5),(0,0,.25),'stone')
    pb.cyl(.3,.23,h-.5,loc=(0,0,(h+.5)/2),mapping=('trim','beam',4))
    pb.cyl(.4,.4,.35,loc=(0,0,h-.2),mapping=('flat','brass'))
def bulb(pb,x,y,z):
    pb.cyl(.18,.18,.3,loc=(x,y,z),mapping=('flat','brass'))
    pb.sphere(.25,loc=(x,y,z-.35),ico=1,part='neon')
def lantern(pb,x,y,z):
    pb.cyl(.55,.45,.3,loc=(x,y,z+.65),mapping=('flat','brass'))
    pb.cyl(.4,.4,1,loc=(x,y,z),part='neon')
    pb.cyl(.5,.5,.3,loc=(x,y,z-.65),mapping=('flat','brass'))
@asset('stringlight_pole',[2,10,2],notes='Hook points local Roblox: (-0.75,9,0), (0.75,9,0).')
def stringpole(pb):
    pole(pb,9.5)
    pb.tube([(-.75,0,9),(-.75,0,9.6),(0,0,9.6),(.75,0,9.6),(.75,0,9)],.15,mapping=('flat','brass'))
for span in (10,20):
    def lights(pb,n=span):
        points=[(-n/2+i*n/20,0,1.6*(2*i/20-1)**2+.65) for i in range(21)]
        pb.tube(points,.15,segs=6,mapping=('flat','rope'))
        for i in range(int(n/2)+1):
            x=-n/2+i*2;z=1.6*(2*x/n)**2+.65;bulb(pb,x,0,z-.2)
    asset('string_lights_span_'+str(span),[span,3,1],notes='Base centre; end hook positions measured in manifest. Merged bulbs; no real lights.')(lights)
@asset('banner_pole',[4,10,2],notes='Cloth top pivot attach at Roblox (0,9,0.3).')
def bannerpole(pb):
    pole(pb,10);box(pb,(4,.4,.4),(0,0,9),'brass')
themes={'lantern_grove':'#E58A3A','sugarloaf_canyon':'#D9714A','aurora_archipelago':'#7B5BD6'}
for theme,color in themes.items():
    def banner(pb,c=color,t=theme):
        # Thick cloth, top pivot at zero, front Blender +Y / Roblox -Z.
        pb.loft([[(-1.5,-.15,z),(1.5,-.15,z),(1.5,.15,z),(-1.5,.15,z)] for z in (0,-2,-4.5)],part='backdrop',color=c)
        box(pb,(2.7,.3,.3),(0,.2,-.6),'brass')
        if t=='lantern_grove':pb.sphere(.8,loc=(0,.25,-2.3),scale=(1,.2,1),ico=2,part='backdrop',color='#E8C24C')
        elif t=='sugarloaf_canyon':
            for z in (-1.5,-2.5,-3.5):box(pb,(2.5,.3,.35),(0,.2,z),part='backdrop',color='#F0C9A0')
        else:
            pb.custom([(-.8,.3,-2.5),(0,.3,-1.3),(.8,.3,-2.5),(0,.3,-3.6)],[[0,1,2],[0,2,3]],part='backdrop',color='#9FE6F2')
    asset('banner_'+theme,[3,4.5,.6],pivot='top',motion='Top-centre pivot (0,0,0), sway +/-4 degrees, no flapping near spawn.')(banner)
@asset('flag_pennant_string',[10,2,1],notes='Base centre; measured end hooks in manifest; bunting is decoration only.')
def bunting(pb):
    pts=[(-5+i,0,1.8-.6*math.sin(math.pi*i/10)) for i in range(11)]
    pb.tube(pts,.15,segs=6,mapping=('flat','rope'))
    for i in range(9):
        x=-4.4+i*1.1;z=1.8-.6*math.sin(math.pi*(x+5)/10)
        pb.custom([(x-.4,0,z),(x+.4,0,z),(x,0,z-1)],[[0,1,2]],part='backdrop',color=list(themes.values())[i%3])
@asset('bench_a',[6,3.5,2.5])
def bench_a(pb):
    for x in (-2.3,2.3):
        for y in (-.7,.7):box(pb,(.5,.5,1.5),(x,y,.75),'brass')
    for y in (-.75,0,.75):box(pb,(6,.6,.35),(0,y,1.6),'plank')
    for z in (2.3,3):box(pb,(6,.4,.55),(0,-1,z),'plank')
    for x in (-2.6,2.6):box(pb,(.35,.4,2),(x,-1,2.3),'post')
@asset('bench_b',[6,3.5,2.5],notes='Neutral stone supports and log seat match forest, canyon and crystal settings.')
def bench_b(pb):
    for x in (-2.2,2.2):box(pb,(1.2,1.6,1.5),(x,0,.75),'stone',.3)
    pb.cyl(.55,.55,6,loc=(0,0,1.8),rot=(0,90,0),mapping=('trim','bark',6),segs=12)
    pb.cyl(.4,.4,6,loc=(0,-.8,2.8),rot=(0,90,0),mapping=('trim','bark',6),segs=12)
for shape in ('square','round'):
    def planter(pb,s=shape):
        if s=='square':
            box(pb,(3,3,.4),(0,0,.2),'brass')
            for x,y,sx,sy in ((-1.3,0,.4,3),(1.3,0,.4,3),(0,-1.3,2.2,.4),(0,1.3,2.2,.4)):
                box(pb,(sx,sy,1.8),(x,y,1.2),'plank')
            box(pb,(2.2,2.2,.3),(0,0,1.7),'ink')
        else:
            pb.lathe([(1.1,0),(1.35,.3),(1.5,1.8),(1.5,2.1),(1.1,2.1),(1.1,1.6)],segs=16,mapping=('flat','plank'))
            pb.cyl(1.1,1.1,.3,loc=(0,0,1.7),mapping=('flat','ink'))
    asset('planter_'+shape,[3,2.1,3],notes='Swap filler origin at Roblox (0,1.85,0).')(planter)
@asset('plant_autumn',[3,3,3],notes='Place origin in planter soil; separate swappable filler.')
def autumn(pb):
    for i,(x,y) in enumerate(((-.6,-.5),(.6,0),(0,.5))):
        pb.cyl(.15,.15,1.5+i*.3,loc=(x,y,.75+i*.15),mapping=('flat','bark'))
        pb.blob((1.6,1.6,1.8),loc=(x,y,1.8+i*.3),ico=2,part='backdrop',color=('#E58A3A','#C9473A','#E8C24C')[i])
@asset('plant_cactus_candy',[3,3.6,2])
def candy(pb):
    from props_arches import cactus
    cactus(pb,(0,0,0))
@asset('plant_crystal',[3,3.5,3])
def crystalplant(pb):
    from props_arches import crystal
    pb.neon_hex='#9FE6F2'
    for x,y,h in ((0,0,3.2),(-.7,0,2),(.7,.3,2.4),(0,-.7,1.6)):
        crystal(pb,(x,y,.3),(x*.15,y*.15,1),h,.4)
for double in (False,True):
    def lamp(pb,d=double):
        pole(pb,8)
        if d:
            box(pb,(3,.4,.4),(0,0,7.4),'brass');lantern(pb,-1.3,0,6.5);lantern(pb,1.3,0,6.5)
        else:lantern(pb,0,0,8)
    asset('lamp_post_double' if double else 'lamp_post',[4 if double else 1.5,9,1.5],notes='Merged Neon glass; no PointLights.')(lamp)
@asset('leaderboard_frame',[14,10,2],notes='3 recessed SurfaceGui panels; separate plane FBXs. Front Roblox -Z.')
def leaderboard(pb):
    box(pb,(14,1.5,.6),(0,0,.3),'stone')
    for x in (-6.6,6.6):box(pb,(.8,1.5,9.4),(x,0,5),'post')
    for z in (1.7,8.5,9.6):box(pb,(14,1.5,.5),(0,0,z),'brass')
    box(pb,(12.5,.4,.8),(0,.8,9),'parch')
    for x in (-4.3,0,4.3):
        box(pb,(4,.5,6),(x,0,5),'post')
        for dx in (-1.85,1.85):box(pb,(.3,.4,6),(x+dx,.6,5),'brass')
for i,x in enumerate((-4.3,0,4.3),1):
    def panel(pb,c=x):
        pb.quad([(c-1.7,.65,2.2),(c-1.7,.65,7.8),(c+1.7,.65,7.8),(c+1.7,.65,2.2)],mapping=('fit','parch_panel'))
    asset('leaderboard_panel_'+str(i),[3.4,5.6,0],pivot='local',notes='Shared frame base origin; SurfaceGui face rectangle local Roblox centre ('+str(x)+',5,-0.65), W3.4 H5.6; normal -Z.')(panel)
