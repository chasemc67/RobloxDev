"""Course-wide native ball checks for zf2 visual/collider isolation."""
import json,sys
from pathlib import Path
from run_playtests import Studio,set_edit_attrs,clear_test_attrs,wait_api,run_one
out=Path(sys.argv[1] if len(sys.argv)>1 else 'playtests/stage-zf1/sweep');out.mkdir(exist_ok=True)
s=Studio();assert s.mode()[0]=='Edit'
opts={'course':sys.argv[2],'parts':'cupdrop,fuzz,sweep','fuzz':2,'sweep':2,'seed':20261014}
set_edit_attrs(s,{'GolfTestMode':True,'SimulateVR':False,'GolfTestOpts':json.dumps(opts)})
s.start_play();wait_api(s)
results={}
try:
 for n in ([int(x) for x in sys.argv[3:]] if len(sys.argv)>3 else range(1,10) if opts['course']=='lantern_grove' else range(1,19)):  # (gg3: LG has 9; its h10 is the bonus hole)
  s.luau('workspace:SetAttribute("GolfTestOpts", '+json.dumps(json.dumps(opts))+')','Client')
  results['h'+str(n)]={'default':run_one(s,'h'+str(n),'',str(out),False,900,None)[0]}
  (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
  print('COMPLETED HOLE',n,flush=True)
 (out/'console.json').write_text(json.dumps({dm:s.problems(dm) for dm in ['Server','Client']},indent=2)+'\n')
finally:
 s.stop_play();clear_test_attrs(s)
