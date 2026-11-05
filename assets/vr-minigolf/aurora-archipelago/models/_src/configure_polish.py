"""Apply deterministic edits from prepolish source backups; never runs Blender."""
from pathlib import Path
S=Path(__file__).resolve().parent
p=S/'props_batch3/gen_batch3.py';src=p.with_name('gen_batch3_prepolish.py').read_text()
a=src.index('def puff(');b=src.index('for j in range(2):',a)
src=src[:a]+'from polish_shapes import puff,palm,buoy,ramp_lanterns,ice_bank,finish\n\n'+src[b:]
a=src.index("for dx in [-.65,.65]:",src.index("p=make(14,'buoy_float')"));b=src.index("p=make(14,'safe_side_sign')",a)
src=src[:a]+'buoy(p)\n'+src[b:]
a=src.index('for dz in [-3.5,0,3.5]:',src.index("p=make(18,'ramp_lanterns')"));b=src.index('override(p,',a)
src=src[:a]+'ramp_lanterns(p)\n'+src[b:]
a=src.index('for xx in [-4.85,4.85]:',src.index("p=make(4,'ice_channel_edge'"));b=src.index('override(p,',a)
src=src[:a]+'ice_bank(p)\n'+src[b:]
src=src.replace("(S/'parts.json').write_text(json.dumps(out))","out=finish(out,S)\n(S/'parts.json').write_text(json.dumps(out))")
p.write_text(src)
p=S/'props_batch1/fitcheck_batch1.py';src=p.with_name('fitcheck_batch1_prepolish.py').read_text()
src=src.replace('import json,math','import json,math,hashlib,sys')
src=src.replace("H={h['number']", "assert hashlib.md5((D/'holes.json').read_bytes()).hexdigest()=='fb913741b5dd4812b6d2318e258bcc46'\nCHANGED=set(json.loads((S/'polish_ids.json').read_text()))\nH={h['number']",1)
idx=src.index('\ndef triangles(p):')
src=src[:idx]+"\nMODE='preflight fan triangulation' if '--preflight' in sys.argv else 'Blender actual triangles'\nif '--preflight' in sys.argv:CACHE=None\nelse:\n    build=json.loads((S/'build_report.json').read_text())\n    assert build.get('parts_sha256')==hashlib.sha256((S/'parts.json').read_bytes()).hexdigest(),'Stale Blender build; use --preflight'\n    assert build.get('triangles_sha256')==hashlib.sha256((S/'triangles.json').read_bytes()).hexdigest(),'Stale Blender triangles'\n"+src[idx:]
src=src.replace("if minimum[0]<.1-1e-5:fail.append('rail clearance <0.1')","required=.15 if p['id'] in CHANGED else .1\n    if minimum[0]<required-1e-5:fail.append('rail clearance below required buffer')")
src=src.replace('felt_hits=0','felt_hits=0;feltvals=[]')
src=src.replace("head=hit(q,[0,4,0],[f['size'][0]-.00002,8-.00002,f['size'][1]-.00002])", "buffer=.3 if p['id'] in CHANGED else -.00002\n            head=hit(q,[0,4,0],[f['size'][0]+buffer,8-.00002,f['size'][1]+buffer])\n            live=q[~exempt]\n            if len(live):feltvals.append((clearance(live,dict(center=[0,4,0],size=[f['size'][0],8,f['size'][1]])),f['id']))")
src=src.replace("r=dict(id=p['id']", "if p['id'] in CHANGED:\n        if sum(tris.values())>900 and 'giant' not in p['id']:fail.append('small coral >900')\n        if sum(tris.values())>=3000:fail.append('coral >=3000')\n        if any(p.get(k) is not False for k in ['can_collide','can_query','can_touch']):fail.append('interaction flags')\n    felt=min(feltvals) if feltvals else (None,'source skin/mover')\n    r=dict(hole=p['hole'],min_felt_clearance=felt[0],nearest_felt=felt[1],id=p['id']")
src=src.replace("and 'coral_' in p['id']",'')
src=src.replace('dict(all_pass=allpass,parts=results,hole_tris=totals)',"dict(mode=MODE,parts_sha256=hashlib.sha256((S/'parts.json').read_bytes()).hexdigest(),heavy_counts=heavy,all_pass=allpass,parts=results,hole_tris=totals)")
p.write_text(src)
print('Configured batch3 generator and current-source batch1 preflight.')
