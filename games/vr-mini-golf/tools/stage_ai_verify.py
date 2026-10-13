"""Native local Aurora v4 acceptance checks. No save or publish operations."""
import json
from pathlib import Path
from run_playtests import Studio,set_edit_attrs,clear_test_attrs,wait_api,run_one
OUT=Path('playtests/stage-ai'); runs=OUT/'sweep';runs.mkdir(exist_ok=True)
s=Studio();assert s.mode()[0]=='Edit'
assert s.luau('return game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient")')=='true'
spec=json.loads(Path('../../assets/vr-mini-golf/aurora-archipelago/holes.json').read_text())
movers={h['number'] for h in spec['holes'] if h.get('moving_parts')}
print('MOVER HOLES',sorted(movers),flush=True)
set_edit_attrs(s,{'GolfTestMode':True,'SimulateVR':False,'GolfTestOpts':json.dumps({'course':'aurora_archipelago','parts':'cupdrop,fuzz','fuzz':8,'seed':20261013})})
s.start_play();wait_api(s)
results={}
try:
 for n in range(1,19):
  opts={'course':'aurora_archipelago','parts':'cupdrop,fuzz'+(',slow' if n in movers else '')+(',biased' if n==4 else ''),'fuzz':8,'slow':6,'biased':12,'seed':20261013}
  s.luau('workspace:SetAttribute("GolfTestOpts", '+json.dumps(json.dumps(opts))+')','Client')
  results['h'+str(n)]={'default':run_one(s,'h'+str(n),'',str(runs),False,900,None)[0]}
  (runs/'results.json').write_text(json.dumps(results,indent=2)+'\n')
  print('COMPLETED HOLE',n,flush=True)
 code='''local m=workspace.CourseAurora.Hole17.Movers.Mover_aurora_span
 local p=m:FindFirstChild("TogglePart").Value local rows={} local start=workspace:GetServerTimeNow()
 repeat local t=workspace:GetServerTimeNow() local visual={}
 for _,v in m:GetDescendants() do if v:IsA("MeshPart") and v:GetAttribute("ToggleVisual") then table.insert(visual,{name=v.Name,transparency=v.Transparency,base=v:GetAttribute("ManifestTransparency"),collide=v.CanCollide,query=v.CanQuery,touch=v.CanTouch}) end end
 table.insert(rows,{t=t,elapsed=t-start,phase=t%9,collide=p.CanCollide,query=p.CanQuery,touch=p.CanTouch,visual=visual}) task.wait(0.05)
 until workspace:GetServerTimeNow()-start>=20
 _G.StageAISchedule=game.HttpService:JSONEncode({attributes=m:GetAttributes(),samples=rows}) return #_G.StageAISchedule'''
 length=int(s.luau(code,'Server',45))
 d=''.join(s.luau(f'return string.sub(_G.StageAISchedule,{i+1},{i+45000})','Server') for i in range(0,length,45000))
 (OUT/'h17-schedule.json').write_text(d+'\n')
 (OUT/'console.json').write_text(json.dumps({dm:s.problems(dm) for dm in ['Server','Client']},indent=2)+'\n')
finally:
 s.stop_play();clear_test_attrs(s)
