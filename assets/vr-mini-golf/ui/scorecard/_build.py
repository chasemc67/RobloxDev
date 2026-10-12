import math
from PIL import Image, ImageDraw, ImageEnhance
H=lambda h:tuple(int(h[i:i+2],16) for i in (1,3,5))
WOOD,DARK,POST=H('#B5835A'),H('#7A4E2D'),H('#8A5A34')
BR,BRS,PARCH=H('#C9A04A'),H('#8C6A2A'),H('#F1E2BE')
S=1024
def gear(g,c,cy,ro,ri,hole,col,teeth=8):
    pts=[]
    for i in range(teeth*4):
        a=i*2*math.pi/(teeth*4)
        r=ro if (i%4) in (1,2) else ri
        pts.append((c+r*math.cos(a),cy+r*math.sin(a)))
    g.polygon(pts,fill=col); g.ellipse([c-ri*.98,cy-ri*.98,c+ri*.98,cy+ri*.98],fill=col)
def make(pressed):
    b=Image.new('RGBA',(S,S),(0,0,0,0)); g=ImageDraw.Draw(b)
    k=S/512; dy=int(10*k) if pressed else 0
    if not pressed: g.ellipse([16*k,28*k,S-16*k,S-4*k],fill=(40,22,10,110))
    else: g.ellipse([20*k,30*k,S-20*k,S-8*k],fill=(40,22,10,70))
    E=lambda x0,y0,x1,y1:[x0*k,y0*k+dy,x1*k,y1*k+dy]
    g.ellipse(E(16,12,496,492),fill=DARK); g.ellipse(E(34,30,478,474),fill=BR)
    g.ellipse(E(46,42,466,462),fill=BRS); g.ellipse(E(54,50,458,454),fill=WOOD)
    L=Image.new('RGBA',(S,S),(0,0,0,0)); lg=ImageDraw.Draw(L)
    for y in range(96,432,46): lg.line([(0,y*k+dy),(S,y*k+dy)],fill=POST+(255,),width=int(6*k))
    M=Image.new('L',(S,S),0); ImageDraw.Draw(M).ellipse(E(58,54,454,450),fill=255)
    b.paste(L,(0,0),Image.composite(L.split()[3],M,M).point(lambda v:v) if False else Image.fromarray(__import__('numpy').minimum(__import__('numpy').array(L.split()[3]),__import__('numpy').array(M))))
    g=ImageDraw.Draw(b)
    c=256*k; cy=250*k+dy
    gear(g,c,cy,172*k,128*k,0,DARK)        # outline
    gear(g,c,cy,150*k,108*k,0,PARCH)
    g.ellipse([c-50*k,cy-50*k,c+50*k,cy+50*k],fill=DARK)
    g.ellipse([c-30*k,cy-30*k,c+30*k,cy+30*k],fill=WOOD)
    im=b.resize((256,256),Image.LANCZOS)
    if pressed:
        r,gg,bb,a=im.split(); rgb=ImageEnhance.Brightness(Image.merge('RGB',(r,gg,bb))).enhance(.82)
        im=Image.merge('RGBA',(*rgb.split(),a))
    return im
make(False).save('settings_button.png'); make(True).save('settings_button_pressed.png')
