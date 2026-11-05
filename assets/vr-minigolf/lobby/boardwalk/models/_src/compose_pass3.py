"""Compose rendered views and deterministic documentation; does not alter exports."""
from pathlib import Path
import json,datetime
from PIL import Image,ImageDraw,ImageOps
SRC=Path(__file__).parent;ROOT=SRC.parent;LOBBY=ROOT.parent.parent;KIT=LOBBY/'kit'
def thumb(path,w,h):
    return ImageOps.pad(Image.open(path).convert('RGB'),(w,h),color='#eee5d6')
def sheet(items,path,cols=3,w=400,h=400):
    canvas=Image.new('RGB',(cols*w,((len(items)+cols-1)//cols)*(h+35)),'#eee5d6');d=ImageDraw.Draw(canvas)
    for i,(label,p) in enumerate(items):
        x=(i%cols)*w;y=(i//cols)*(h+35);canvas.paste(thumb(p,w,h),(x,y));d.text((x+8,y+h+8),label,fill='#30281f')
    canvas.save(path)
courses=('lantern_grove','sugarloaf_canyon','aurora_archipelago');dest=ROOT/'previews/portals'
canvas=Image.new('RGB',(1600,3*485),'#eee5d6');d=ImageDraw.Draw(canvas)
for i,c in enumerate(courses):
    y=i*485
    canvas.paste(thumb(dest/(c+'_eye.png'),480,450),(0,y));canvas.paste(thumb(dest/(c+'_34.png'),480,450),(480,y));canvas.paste(thumb(LOBBY/('portal_'+c+'.png'),640,450),(960,y))
    d.text((12,y+459),c+' | eye at 5 studs + 2x5 capsule | 3/4 | supplied concept',fill='#30281f')
canvas.save(dest/'portals_vs_concepts.png')
