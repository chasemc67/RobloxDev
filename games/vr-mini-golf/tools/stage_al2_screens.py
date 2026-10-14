"""Local Edit visual checks; PNG/JPEG evidence remains uncommitted."""
import base64,json
from pathlib import Path
from run_playtests import Studio
s=Studio();assert s.mode()[0]=='Edit'
assert s.luau('return game.PlaceId==0 and not game:FindService("NetworkClient")')=='true'
out=Path('playtests/stage-al2/screens');out.mkdir(exist_ok=True)
views={
 'h09-sign-approach':([338,73,-5098.4],[343,72.5,-5098.4]),
 'h09-arrow-approach':([345,74,-5100.5],[352,70,-5100.5]),
 'h14-sign-approach':([-297,153,-5196],[-295,152.7,-5191]),
 'h14-bank-arrow-approach':([-296,154,-5196],[-299,150,-5192]),
 'h14-timing-arrow-approach':([-300,154,-5189],[-300,150,-5182]),
 'h09-tee':([330,74,-5110],[343,71.7,-5100]),
 'h14-tee':([-300,154,-5200],[-299,151,-5188]),
}
for name,(pos,target) in views.items():
 r=s.m.req('tools/call',{'name':'screen_capture','arguments':{'studio_id':s.id,'capture_id':'al2-'+name,'camera_position':pos,'look_at_position':target}})
 img=next(c for c in r['result']['content'] if c.get('type')=='image')
 (out/(name+'.jpg')).write_bytes(base64.b64decode(img['data']))
 print(name,flush=True)
(out.parent/'views.json').write_text(json.dumps(views,indent=2)+'\n')
