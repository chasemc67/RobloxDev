"""Native local Sugarloaf fix2 acceptance checks. No save or publish operations."""
import json
from pathlib import Path
from run_playtests import Studio,set_edit_attrs,clear_test_attrs,wait_api,run_one
OUT=Path('playtests/stage-al'); runs=OUT/'sweep';runs.mkdir(exist_ok=True)
s=Studio();assert s.mode()[0]=='Edit'
assert s.luau('return game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient")')=='true'
spec=json.loads(Path('../../assets/vr-mini-golf/sugarloaf-canyon/holes.json').read_text())
movers={h['number'] for h in spec['holes'] if h.get('moving_parts')}
print('MOVER HOLES',sorted(movers),flush=True)
set_edit_attrs(s,{'GolfTestMode':True,'SimulateVR':False,'GolfTestOpts':json.dumps({'course':'sugarloaf_canyon','parts':'cupdrop,fuzz','fuzz':8,'seed':20261013})})
s.start_play();wait_api(s)
results={}
try:
 for n in range(1,19):
  opts={'course':'sugarloaf_canyon','parts':'cupdrop,fuzz'+(',slow' if n in movers else ''),'fuzz':8,'slow':6,'biased':12,'seed':20261013}
  s.luau('workspace:SetAttribute("GolfTestOpts", '+json.dumps(json.dumps(opts))+')','Client')
  results['h'+str(n)]={'default':run_one(s,'h'+str(n),'',str(runs),False,900,None)[0]}
  (runs/'results.json').write_text(json.dumps(results,indent=2)+'\n')
  print('COMPLETED HOLE',n,flush=True)
 (OUT/'console.json').write_text(json.dumps({dm:s.problems(dm) for dm in ['Server','Client']},indent=2)+'\n')
finally:
 s.stop_play();clear_test_attrs(s)
