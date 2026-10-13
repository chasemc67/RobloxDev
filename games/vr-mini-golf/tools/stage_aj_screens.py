"""Capture local viewport evidence through Studio MCP; screenshots remain uncommitted."""
import base64
from pathlib import Path
from run_playtests import Studio
shots=[('h8-new-ground',[385,100,-4950],[360,70,-4970]),('h9-approved-tank',[385,85,-5108],[370,74,-5121.65]),('h15-new-deflector',[-325,175,-5070],[-300,147,-5085]),('h7-island',[355,92,-4880],[333.5,74,-4891]),('h17-hour-stones',[-368,213,-4800],[-345,191,-4809])]
st=Studio();out=Path('playtests/stage-aj/screens');out.mkdir(exist_ok=True)
try:
 for name,pos,target in shots:
  r=st.m.req('tools/call',{'name':'screen_capture','arguments':{'studio_id':st.id,'capture_id':'stage-aj-'+name,'camera_position':pos,'look_at_position':target}})
  for c in r['result']['content']:
   if c.get('type')=='image':(out/(name+'.png')).write_bytes(base64.b64decode(c['data']))
  print(name,flush=True)
finally:st.m.p.terminate()
