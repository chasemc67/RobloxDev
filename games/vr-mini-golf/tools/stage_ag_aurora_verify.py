"""Local Aurora final checks; native Play, no file/cloud save operations."""
import json,time
from pathlib import Path
from run_playtests import Studio,set_edit_attrs,clear_test_attrs,wait_api,run_one,mcp_grab
s=Studio();assert s.mode()[0]=='Edit'
assert json.loads(s.luau('return game.HttpService:JSONEncode({place=game.PlaceId,role=workspace:GetAttribute("PlaceRole")})'))=={'place':0,'role':'aurora_archipelago'}
out=Path('playtests/stage-ag/aurora-final');out.mkdir(exist_ok=True)
set_edit_attrs(s,{'GolfTestMode':True,'SimulateVR':False,'GolfTestOpts':json.dumps({'course':'aurora_archipelago','parts':'fuzz,slow,cupdrop','fuzz':8,'slow':6,'seed':20261012})})
s.start_play();wait_api(s)
try:
 # Recheck boundary values on the final loaded profile.
 code='local mm=require(game.ReplicatedStorage.Golf.MoverMath:Clone()) local p={type="toggle",phase=0,period=9,solidStart=0.6,solidEnd=6.6} local rows={} for _,t in {0,0.599999,0.6,6.599999,6.6,8.999999,9,9.6,15.6,18.6} do table.insert(rows,{t=t,value=mm.value(p,t)}) end return game.HttpService:JSONEncode(rows)'
 Path('playtests/stage-ag/h17-boundaries-final.json').write_text(s.luau(code,'Server'))
 probe=Path('tools/stage_ag_probe.py').read_text().split("code='''",1)[1].split("'''",1)[0]
 Path('playtests/stage-ag/h17-schedule-final.json').write_text(s.luau(probe,'Server',45))
 results={}
 results['h17']={'default':run_one(s,'h17','',str(out),False,900,None)[0]}
 # Remaining 17 holes, including H4, each get the same three native cup putts.
 s.luau('workspace:SetAttribute("GolfTestOpts", [[{"course":"aurora_archipelago","parts":"cupdrop"}]])','Client')
 for n in range(1,19):
  if n==17:continue
  results['h'+str(n)]={'default':run_one(s,'h'+str(n),'',str(out),False,120,None)[0]}
  (out/'results.json').write_text(json.dumps(results,indent=2))
 # Desktop zero-hole scorecard fixture uses the real HUD in the current client.
 s.luau('local me=game.Players.LocalPlayer me:SetAttribute("Course","lobby") me.PlayerScripts.GolfMenuDebug:Invoke("close") me.PlayerScripts.GolfMenuDebug:Invoke("scorecard") task.wait(0.3) return "opened desktop zero-hole fixture"','Client')
 Path('playtests/stage-ag/desktop-scorecard-bounds.json').write_text(s.luau(Path('tools/stage_ag_layout.luau').read_text(),'Client'))
 mcp_grab(s,'playtests/stage-ag/desktop-scorecard.png')
 s.luau('local me=game.Players.LocalPlayer me.PlayerScripts.GolfMenuDebug:Invoke("scorecard") me:SetAttribute("Course","aurora_archipelago") return "restored"','Client')
 (out/'console.json').write_text(json.dumps({dm:s.problems(dm) for dm in ['Server','Client']},indent=2))
finally:
 s.stop_play();clear_test_attrs(s)
