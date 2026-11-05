import json,numpy as np
from PIL import Image,ImageDraw,ImageFont
D='/workspace/RobloxDev/assets/vr-minigolf/sugarloaf-canyon/'
T=json.load(open(D+'models/_src/props_h09h14/triangles.json'))
def sil(tris,ax,size=420):
  P=np.array(tris);X=P[...,ax[0]];Y=P[...,1]
  lo=min(X.min(),0);s=(size-40)/max(X.max()-X.min(),Y.max()-Y.min());ox=(size-(X.max()-X.min())*s)/2
  im=Image.new('RGB',(size,size),'white');d=ImageDraw.Draw(im)
  for x,y in zip(X,Y): d.polygon([(ox+(a-X.min())*s,size-20-b*s) for a,b in zip(x,y)],fill='black')
  return im
rows=[('h09_water_tank','h09-concept.png',(1540,340,1840,660),[(2,'side (z)'),(0,'front (x)')]),
      ('h14_loading_dock','h14-concept.png',(1150,620,1680,830),[(0,'front (x)'),(2,'side (z)')])]
font=ImageFont.load_default()
sheet=Image.new('RGB',(4*440,2*480),'white');d=ImageDraw.Draw(sheet)
for r,(pid,cp,box,views) in enumerate(rows):
  c=Image.open(D+cp).convert('RGB').crop(box);c.thumbnail((420,420));sheet.paste(c,(10,r*480+40))
  d.text((10,r*480+10),f'{pid}: concept crop ({cp})',fill='black',font=font)
  for i,(ax,lab) in enumerate(views):
    sheet.paste(sil(T[pid],(ax,)),(450+i*440,r*480+40));d.text((450+i*440,r*480+10),f'silhouette {lab}',fill='black',font=font)
  pv=Image.open(D+f'models/previews/props_h09h14/{pid}_34.png').convert('RGB');pv.thumbnail((420,420));sheet.paste(pv,(1330,r*480+40))
  d.text((1330,r*480+10),'3/4 preview',fill='black',font=font)
sheet.save(D+'silhouettes/sheet05-h09-tank-h14-dock.png');print('ok')
