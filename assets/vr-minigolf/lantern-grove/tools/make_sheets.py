#!/usr/bin/env python3
"""Build holes_layouts_sheet.jpg and holes_concepts_sheet.jpg from hNN-*.png. Run from lantern-grove/."""
import json,os
from PIL import Image,ImageDraw,ImageFont
H=json.load(open('holes.json'))['holes']; tot=sum(h['par'] for h in H)
f=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',s)
def sheet(kind,out,tw=900):
    ims=[Image.open(f"{h['id']}-{kind}.png").convert('RGB') for h in H]
    th=max(int(tw*im.height/im.width) for im in ims); cap=50; pad=24; head=90
    g=Image.new('RGB',(3*tw+4*pad,head+3*(th+cap+pad)+pad),(22,26,24)); d=ImageDraw.Draw(g)
    d.text((pad,25),f"Lantern Grove - 9-hole {kind}s (total par {tot})",font=f(40),fill=(255,214,60))
    for i,(h,im) in enumerate(zip(H,ims)):
        im.thumbnail((tw,th)); x=pad+(i%3)*(tw+pad); y=head+(i//3)*(th+cap+pad)
        g.paste(im,(x,y)); d.text((x,y+th+8),f"{i+1}. {h['name']} - par {h['par']}",font=f(26),fill=(240,240,240))
    q=88
    while True:
        g.save(out,quality=q)
        if os.path.getsize(out)<3e6 or q<50: break
        q-=8
    print(out,os.path.getsize(out))
sheet('layout','holes_layouts_sheet.jpg'); sheet('concept','holes_concepts_sheet.jpg')
