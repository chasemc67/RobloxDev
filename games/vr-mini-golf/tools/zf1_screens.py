"""Save repeatable Studio MCP camera evidence as PNGs."""
import base64,io,json,sys
from pathlib import Path
from run_playtests import Studio
from PIL import Image
s=Studio()
views={
 'sc':([-296,151,-5074],[-311,146.8,-5086]),
 'decals-h15':([-288,157,-5082],[-300,147.8,-5091]),
 'decals-h13':([-288,157,-5284],[-297.4,152.7,-5274.8]),
}
key=sys.argv[1];name=sys.argv[2];pos,target=views[key]
r=s.m.req('tools/call',{'name':'screen_capture','arguments':{'studio_id':s.id,'capture_id':'zf1-'+name,'camera_position':pos,'look_at_position':target}})
img=next(c for c in r['result']['content'] if c.get('type')=='image')
Image.open(io.BytesIO(base64.b64decode(img['data']))).save('logs/stages/zf1-'+name+'.png')
Path('playtests/stage-zf1/views.json').write_text(json.dumps(views,indent=2)+'\n')
