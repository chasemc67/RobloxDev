from pathlib import Path
p=Path('models/_src/props_batch1/gen_batch1.py');s=p.read_text().replace('flatten=1,n=8','flatten=1,n=6').replace("[px,7.8,z-.7],[x+(-2.4 if px<x else 2.4),8.18,z]","[px,8.3,z-.7],[x+(-2.4 if px<x else 2.4),8.3,z]")
s=s.replace("[min(2.8,w['size'][0]*1.12),2.4,min(1.4,w['size'][2]*1.1)]","[w['size'][0]*.83,2.4,w['size'][2]*.75]")
# Rounded swollen tips with 3 compact rings (24 tris), keeping each small coral under 900.
s=s.replace("mound(p,col,[tip[0],tip[1]-rr*.6,tip[2]],[rr*2,rr*1.8,rr*1.15],n=8)","bud(p,col,[tip[0],tip[1]-rr*.6,tip[2]],[rr*2,rr*1.8,rr*1.15])").replace("mound(p,'CoralMint',[tip[0],tip[1]+rr*.55,tip[2]],[rr*1.2,rr*.55,rr*.7],n=8)","bud(p,'CoralMint',[tip[0],tip[1]+rr*.55,tip[2]],[rr*1.2,rr*.55,rr*.7])")
s=s.replace('def coral(p,c,size,col=',"def bud(p,m,c,size):\n    x,y,z=c;w,h,d=size\n    p.loft(m,[[[x+w/2*sc*math.cos(math.tau*i/6)-p.anchor[0],y+h*yy-p.anchor[1],z+d/2*sc*math.sin(math.tau*i/6)-p.anchor[2]] for i in range(6)] for sc,yy in [(.45,0),(1,.5),(.3,1)]])\ndef coral(p,c,size,col=")
# Deterministic skips for exact conflicting source envelopes (do not resize source geometry).
s=s.replace('out=[]\nfor p in P:',"P=[p for p in P if p.name not in ['h05_cliff_face_w','h05_cliff_face_e']]\nfor name in ['cliff_face_w','cliff_face_e']:skipped.append(dict(id='h05_'+name,hole=5,reason='Exact source box touches upper side rail (0 clearance) and upper south rail bottom y3.5; required >=0.1. SKIPPED rather than alter anchor or box.'))\nout=[]\nfor p in P:")
p.write_text(s)
