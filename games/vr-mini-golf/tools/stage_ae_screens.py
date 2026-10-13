"""Save local-only Edit screenshots for visual QA (do not commit images)."""
import base64
from pathlib import Path
from run_playtests import Studio
s=Studio();assert s.mode()[0]=='Edit'
out=Path('playtests/stage-ae/screens');out.mkdir(exist_ok=True)
views={
 'h3-station':([-100,34,-4665],[-75,26,-4689]),
 'h4-geode':([245,35,-4645],[220,25,-4679]),
 'h8-floors':([385,97,-4935],[360,70,-4970]),
 'h9-rotor':([329,80,-5102],[347.75,74,-5110]),
 'h11-lock':([137,125,-5260],[150,118,-5273.25]),
}
for name,(cam,look) in views.items():
 r=s.m.req('tools/call',{'name':'screen_capture','arguments':{'studio_id':s.id,'capture_id':name,'camera_position':cam,'look_at_position':look}})
 c=next(c for c in r['result']['content'] if c['type']=='image')
 p=out/(name+('.png' if c['mimeType']=='image/png' else '.jpg'));p.write_bytes(base64.b64decode(c['data']));print(p)
