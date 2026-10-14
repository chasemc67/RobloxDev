import base64,io,json,sys
from pathlib import Path
from PIL import Image,ImageDraw
from run_playtests import Studio
OUT=Path('playtests/stage-au6')
s=Studio();assert s.mode()[0]=='Edit'
phase=sys.argv[1];images=[]
for hole,pos,target in [(18,[-237,239,-235],[-241,224,-257]),(6,[312,86,444],[310.5,84,441.75])]:
 r=s.m.req('tools/call',{'name':'screen_capture','arguments':{'studio_id':s.id,'capture_id':f'au6-h{hole}-{phase}','camera_position':pos,'look_at_position':target}})
 raw=next(c for c in r['result']['content'] if c.get('type')=='image')
 im=Image.open(io.BytesIO(base64.b64decode(raw['data']))).convert('RGB');im.save(OUT/f'h{hole}-{phase}.png')
 images.append((hole,im))
width=max(im.width for _,im in images);height=sum(im.height+30 for _,im in images)
board=Image.new('RGB',(width,height),'#131820');d=ImageDraw.Draw(board);y=0
for hole,im in images:
 d.text((12,y+7),f'Aurora H{hole} | stage au6 {phase}',fill='white');board.paste(im,(0,y+30));y+=im.height+30
board.save(f'logs/stages/au6-{phase}.png');print('saved',phase)
