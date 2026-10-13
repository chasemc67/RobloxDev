"""Measure actual H11 constraint motion in Play against server-clock phase."""
import json,sys,time
from pathlib import Path
from run_playtests import Studio
s=Studio();s.start_play();time.sleep(5)
try:
 code='''
local m=workspace.CourseSugarloaf.Hole11.Movers.Mover_lock_gate
local mm=require(game.ReplicatedStorage.Golf.MoverMath)
local p=mm.fromModel(m)
local samples={} local t0=os.clock()
while os.clock()-t0<23 do
 local t=workspace:GetServerTimeNow()
 local want,rate=mm.value(p,t)
 table.insert(samples,{phase=t%10.7,actual=m.Drive.CurrentPosition,want=want,rate=rate})
 task.wait(0.025)
end
return game.HttpService:JSONEncode({profile=p,samples=samples})
'''
 r=json.loads(s.luau(code,'Server',timeout=50))
 r['console']={side:s.problems(side) for side in ['Server','Client']}
 Path(sys.argv[1]).write_text(json.dumps(r,indent=2)+'\n')
 print('samples',len(r['samples']),'profile',r['profile'],'console',r['console'])
finally:s.stop_play()
