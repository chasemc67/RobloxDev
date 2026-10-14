"""Requested native H9/H14 cup drops and eight completed random shots each."""
import json
from pathlib import Path
from run_playtests import Studio,set_edit_attrs,clear_test_attrs,wait_api,run_one
out=Path('playtests/stage-al2');runs=out/'sweep';runs.mkdir(exist_ok=True)
s=Studio();assert s.mode()[0]=='Edit'
assert s.luau('return game.PlaceId==0 and not game:FindService("NetworkClient")')=='true'
opts={'course':'sugarloaf_canyon','parts':'cupdrop,fuzz','fuzz':8,'seed':20261014}
set_edit_attrs(s,{'GolfTestMode':True,'SimulateVR':False,'GolfTestOpts':json.dumps(opts)})
s.start_play();wait_api(s)
results={}
try:
 for n in [9,14]:
  s.luau('workspace:SetAttribute("GolfTestOpts", '+json.dumps(json.dumps(opts))+')','Client')
  results['h'+str(n)]={'default':run_one(s,'h'+str(n),'',str(runs),False,900,None)[0]}
  (runs/'results.json').write_text(json.dumps(results,indent=2)+'\n')
  print('COMPLETED HOLE',n,flush=True)
 (out/'console.json').write_text(json.dumps({dm:s.problems(dm) for dm in ['Server','Client']},indent=2)+'\n')
finally:
 s.stop_play();clear_test_attrs(s)
