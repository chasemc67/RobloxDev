"""Simulated VR lobby layout verification through existing input hooks."""
import json,time
from pathlib import Path
from run_playtests import Studio,set_edit_attrs,clear_test_attrs,mcp_grab
s=Studio();assert s.mode()[0]=='Edit'
assert json.loads(s.luau('return game.HttpService:JSONEncode({place=game.PlaceId,role=workspace:GetAttribute("PlaceRole")})'))=={'place':0,'role':'lobby'}
set_edit_attrs(s,{'SimulateVR':True,'GolfTestMode':False})
s.start_play();time.sleep(5)
out={}
try:
 print(s.luau('local me=game.Players.LocalPlayer me.PlayerScripts:WaitForChild("GolfMenuDebug"):Invoke("close") local d=game.ReplicatedStorage.VRDebug local _,y=d.Head.Value:ToOrientation() d.Head.Value=CFrame.new(d.Head.Value.Position)*CFrame.Angles(0,y,0) me.PlayerScripts.GolfPointerDebug:Invoke("wrist",true) task.wait(1) return "ready"','Client'))
 out['wrist']=json.loads(s.luau('return game.HttpService:JSONEncode(game.Players.LocalPlayer.PlayerScripts.GolfPointerDebug:Invoke("state"))','Client'))
 mcp_grab(s,'playtests/stage-ag/lobby-wrist.png')
 for key in ['ButtonB','ButtonY']:
  print(s.luau('local me=game.Players.LocalPlayer me.PlayerScripts.GolfPointerDebug:Invoke("wrist","down") game.ReplicatedStorage.VRDebug.Button:Fire(Enum.KeyCode.'+key+',false) game.ReplicatedStorage.VRDebug.Button:Fire(Enum.KeyCode.'+key+',true) task.wait(0.6) return "opened"','Client'))
  out[key]=json.loads(s.luau(Path('tools/stage_ag_layout.luau').read_text(),'Client'))
  mcp_grab(s,'playtests/stage-ag/lobby-'+key+'.png')
  print(key,out[key])
  print(s.luau('game.ReplicatedStorage.VRDebug.Button:Fire(Enum.KeyCode.'+key+',false) game.ReplicatedStorage.VRDebug.Button:Fire(Enum.KeyCode.'+key+',true) task.wait(0.2) return game.Players.LocalPlayer.PlayerScripts.GolfPointerDebug:Invoke("state")','Client'))
 out['console']={dm:s.problems(dm) for dm in ['Server','Client']}
 Path('playtests/stage-ag/lobby-bounds.json').write_text(json.dumps(out,indent=2))
finally:
 s.stop_play();clear_test_attrs(s)
