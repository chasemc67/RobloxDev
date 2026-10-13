"""Save Edit screenshots; no place/cloud saves or uploads."""
import base64,json
from pathlib import Path
from run_playtests import Studio
s=Studio();assert s.mode()[0]=='Edit'
out=Path('playtests/stage-af/screens');out.mkdir(exist_ok=True)
views={
 'h07-bridges':([365,95,-4868],[342,71,-4892]),
 'h08-gumdrops':([374,78,-4980],[360,71,-4996]),
 'h09-pump-house':([377,85,-5087],[351,77,-5113]),
 'h10-flume':([315,134,-5255],[290,115,-5278]),
 'h11-lock':([177,132,-5245],[155,119,-5267]),
 'h12-tower':([-140,134,-5238],[-162,121,-5264]),
 'h13-maze':([-271,169,-5238],[-295,152,-5262]),
 'h14-trestle':([-275,167,-5154],[-300,155,-5176]),
 'h15-drifts':([-269,169,-5064],[-300,149,-5091]),
 'h16-sinkhole':([-276,209,-4848],[-300,190,-4872]),
 'h17-gnomon':([-322,210,-4780],[-345,194,-4804]),
 'h18-arch':([-404,211,-4766],[-429,195,-4790])}
for name,(cam,look) in views.items():
 r=s.m.req('tools/call',{'name':'screen_capture','arguments':{'studio_id':s.id,'capture_id':name,'camera_position':cam,'look_at_position':look}})
 c=next(c for c in r['result']['content'] if c['type']=='image')
 p=out/(name+('.png' if c['mimeType']=='image/png' else '.jpg'));p.write_bytes(base64.b64decode(c['data']));print(p,flush=True)
