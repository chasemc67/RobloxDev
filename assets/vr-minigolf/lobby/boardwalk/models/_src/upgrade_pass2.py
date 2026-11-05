"""One-time source upgrade, never edits exports."""
from pathlib import Path
p=Path(__file__).parent
f=p/'props_arches.py'
s=f.read_text()
s=s.replace('size=[3.0, 12.0, 4.0]', 'size=[3.0, 18.0, 4.0]').replace('center=[-6.5, 6.0, 0.0]', 'center=[-6.5, 9.0, 0.0]').replace('center=[6.5, 6.0, 0.0]', 'center=[6.5, 9.0, 0.0]').replace('center=[0.0, 15.0, 0.0], size=[16.0, 6.0, 4.0]', 'center=[0.0, 14.0, 0.0], size=[10.0, 4.0, 4.0]')
# Preserve base frame rather than silently recentering an asymmetric themed silhouette.
s=s.replace('front=FRONT_SOUTH,', 'front=FRONT_SOUTH, pivot="local",')
s=s.replace('ico=3, freq=1.3', 'ico=2, freq=1.3')
a=s.index('    # 6 hanging lanterns')
b=s.index('    enforce_envelope(pb)',a)
s=s[:a]+'''    # Root moss and chunky flowers stay on the legs.
    for side in (-1,1):
        pb.blob((1.5,1.0,0.6),loc=(side*6.5,-1.1,0.4),ico=2,part="backdrop",color="#4F9A43")
        for j in range(3):
            pb.sphere(.3,loc=(side*(6.1+j*.5),-1.3,.8+j*.15),ico=1,part="backdrop",color="#E8C24C")
''' +s[b:]
s=s.replace('    # block lintel wall + crenellations','    # block lintel wall + crenellations')
a=s.index('    enforce_envelope(pb)',s.index('def sugarloaf(pb)'))
s=s[:a]+'''    pb.neon_hex="#F6A6C8"
    for side in (-1,1):
        for j in range(3):
            crystal(pb,(side*(5.8+j*.65),-.4,15.8),(side*.12,0,1),1.5+j*.2,.38)
    cactus(pb,(-6.6,-1.1,0.1),scale=.75)
''' +s[a:]
a=s.index('    enforce_envelope(pb)',s.index('def aurora(pb)'))
s=s[:a]+'''    for side in (-1,1):
        for z in (1.5,6.0,12.8):
            pb.blob((2.2,2.8,.6),loc=(side*6.6,0,z),ico=2,part="backdrop",color="#EEF3F7")
        pb.box((2.1,1.5,.3),loc=(side*6.6,-1.1,.2),bevel=.15,part="backdrop",color="#36997A")
''' +s[a:]
s+='''
# Pass2 separate runtime assets. All coordinates below are Blender X,Y,Z.
def cactus(pb,loc,scale=1):
    x,y,z=loc
    pb.cyl(.4*scale,.35*scale,3*scale,loc=(x,y,z+1.5*scale),part="backdrop",color="#6FBF5A")
    for side in (-1,1):
        pb.tube([(x,y,z+scale),(x+side*.8*scale,y,z+scale),(x+side*.8*scale,y,z+2*scale)],.25*scale,part="backdrop",color="#6FBF5A")
        pb.cyl(.5*scale,.5*scale,.3,loc=(x+side*.8*scale,y,z+2.2*scale),rot=(90,0,0),mapping=("flat","awn_red"))
    pb.cyl(.65*scale,.65*scale,.3,loc=(x,y,z+3.2*scale),rot=(90,0,0),mapping=("flat","awn_cream"))
    pb.torus(.4*scale,.15,loc=(x,y-.18,z+3.2*scale),rot=(90,0,0),mapping=("flat","awn_red"))

def brass_lantern(pb,x,y,z):
    pb.cyl(.15,.15,.6,loc=(x,y,z+.3),mapping=("flat","rope"))
    pb.cyl(.5,.35,.3,loc=(x,y,z-.15),mapping=("flat","brass"))
    pb.cyl(.38,.38,1,loc=(x,y,z-.8),part="neon")
    pb.cyl(.45,.45,.3,loc=(x,y,z-1.45),mapping=("flat","brass"))

for course,budget in (("lantern_grove",15000),("sugarloaf_canyon",8000),("aurora_archipelago",10000)):
    def surface(pb):
        pb.quad([(-5,-1.5,0),(5,-1.5,0),(5,-1.5,12),(-5,-1.5,12)])
        P=pb.parts["atlas"]
        P.uvs=[[(0,0),(1,0),(1,1),(0,1)]]
    prop("bw_portal_surface_"+course,"arches",target=[10,12,0],tris_max=2,front=FRONT_SOUTH,pivot="local",collision=[],notes="Intentional portal quad; exempt from decorative opening/trigger clearance. UV 0-1; runtime animated texture.")(surface)
    def lanterns(pb,c=course):
        if c=="lantern_grove":
            for x,z in ((-6.5,11),(6.5,11),(-6.5,7),(6.5,7),(-3.5,14),(3.5,14)):
                _lantern(pb,x,-1.3,z,.5,r=.45,h=1)
        else:
            for side in (-1,1):
                if c=="aurora_archipelago":
                    pb.box((.4,.4,2),loc=(side*6.5,-1.3,10.6),mapping=("flat","post"),bevel=.15)
                brass_lantern(pb,side*6.5,-1.3,12)
        enforce_envelope(pb)
    prop("bw_arch_"+course+"_lanterns","arches",target=[16,18,4],tris_max=1500,front=FRONT_SOUTH,pivot="local",collision=[],motion="Shared arch base pivot (0,0,0); pulse +/-15% at 0.5Hz; optional sway +/-3deg around listed cord anchors.",notes="Separate merged lantern set; same base-centre frame as arch.")(lanterns)

@prop("bw_portal_apron","arches",target=[12,.1,4],tris_max=100,front=FRONT_SOUTH,pivot="local",collision=[],notes="Place at (0,0,4) in arch-local Roblox axes. Top Y=0, no step; separate floor exempt from envelope and opening volume.")
def apron(pb):
    pb.box((12,4,.1),loc=(0,0,-.05),mapping=("deck","a"))

@prop("bw_arch_aurora_archipelago_snowpuff","arches",target=[3,3,2],tris_max=1500,front=FRONT_SOUTH,pivot="local",collision=[],motion="Arch base pivot; idle body bob <=0.1 studs, no locomotion.",notes="Snowpuff on left leg, all geometry outside opening.")
def snowpuff(pb):
    pb.sphere(1,loc=(-6.5,-.6,1.4),scale=(.85,.7,1.2),ico=2,part="backdrop",color="#3A3550")
    pb.sphere(.7,loc=(-6.5,-1.1,1.3),scale=(.85,.35,1),ico=2,part="backdrop",color="#EEF3F7")
    pb.sphere(.6,loc=(-6.5,-.6,2.4),ico=2,part="backdrop",color="#EEF3F7")
    pb.cyl(.3,0,.6,loc=(-6.5,-1.2,2.3),rot=(90,0,0),part="backdrop",color="#E58A3A")
    for x in (-6.8,-6.2):
        pb.sphere(.15,loc=(x,-1.05,2.55),ico=1,part="backdrop",color="#3A3550")
        pb.box((.4,.7,.3),loc=(x,-.6,.15),bevel=.12,part="backdrop",color="#E58A3A")
'''
f.write_text(s)
f=p/'bwlib.py';s=f.read_text().replace('"PROGRESS.md"','"PROGRESS_pass2.md"');f.write_text(s)
# Correct pivot metadata for fixed layout assets.
f=p/'build_all.py';s=f.read_text().replace('else "base centre: bbox centre X/Z, min Y = 0"','else "local origin (0,0,0), shared arch base centre" if p["pivot"] == "local" else "base centre: bbox centre X/Z, min Y = 0"');f.write_text(s)
print('Sources upgraded')
