from pathlib import Path
p=Path('models/_src/props_batch1/build_batch1.py');s=p.read_text();s=s.replace("rep.append(r);ROOTS", "r['lights']=[]\n    if p['id'] in ['h01_harbour_lantern','h02_lantern_cue']:\n        r['lights']=[dict(type='PointLight',colour='#FFB861',range=14,brightness=.8,position_asset_local=([-.65,8.14,0] if p['hole']==1 else [0,.54,0]))]\n    if p['id']=='h05_signal_lamp':r['runtime_signal']=dict(controller='geyser_lift',flush_colour='#5CFFB0',moving_colour='#FFB861',lens_material='AuroraMint')\n    if p['id']=='h05_steamwhistle_geyser':r['runtime_effect']=dict(type='steam_puff',height=60,period_seconds=20,collision=False,origin_asset_local=[0,7,0])\n    rep.append(r);ROOTS")
# No geometry change: metadata can also be applied to the already-validated reports.
p.write_text(s)
import json
for path in [Path('models/props_batch1_manifest.json'),Path('models/_src/props_batch1/build_report.json')]:
 d=json.loads(path.read_text())
 for r in d['parts']:
  r['lights']=[]
  if r['id'] in ['h01_harbour_lantern','h02_lantern_cue']:r['lights']=[dict(type='PointLight',colour='#FFB861',range=14,brightness=.8,position_asset_local=([-.65,8.14,0] if r['hole']==1 else [0,.54,0]))]
  if r['id']=='h05_signal_lamp':r['runtime_signal']=dict(controller='geyser_lift',flush_colour='#5CFFB0',moving_colour='#FFB861',lens_material='AuroraMint')
  if r['id']=='h05_steamwhistle_geyser':r['runtime_effect']=dict(type='steam_puff',height=60,period_seconds=20,collision=False,origin_asset_local=[0,7,0])
 path.write_text(json.dumps(d,indent=2))
