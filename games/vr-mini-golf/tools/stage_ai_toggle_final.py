"""Recheck H17 after hiding the covered felt render; unchanged collision, final native session."""
import json,shutil
from pathlib import Path
from run_playtests import Studio,set_edit_attrs,clear_test_attrs,wait_api
OUT=Path('playtests/stage-ai')
s=Studio();assert s.mode()[0]=='Edit'
set_edit_attrs(s,{'GolfTestMode':True,'SimulateVR':False,'GolfTestOpts':json.dumps({'course':'aurora_archipelago'})})
s.start_play();wait_api(s)
try:
 code=Path('tools/stage_ai_verify.py').read_text().split(" code='''",1)[1].split("'''",1)[0]
 code=code.replace('collide=p.CanCollide,query=p.CanQuery,touch=p.CanTouch,visual=visual','collide=p.CanCollide,query=p.CanQuery,touch=p.CanTouch,feltAlpha=p.Transparency,visual=visual')
 length=int(s.luau(code,'Server',45))
 d=''.join(s.luau(f'return string.sub(_G.StageAISchedule,{i+1},{i+45000})','Server') for i in range(0,length,45000))
 shutil.copy(OUT/'h17-schedule.json',OUT/'h17-schedule-before-visual-hide.json')
 (OUT/'h17-schedule.json').write_text(d+'\n')
 audit={}
 for dm in ['Server','Client']:
  audit[dm]=json.loads(s.luau('local count=0 local bad={} for _,m in workspace.CourseAurora:GetDescendants() do if m:GetAttribute("StageAIVisual") then for _,p in m:GetDescendants() do if p:IsA("MeshPart") then count+=1 if p.CanCollide or p.CanQuery or p.CanTouch then table.insert(bad,{name=p:GetFullName(),collide=p.CanCollide,query=p.CanQuery,touch=p.CanTouch}) end end end end end return game.HttpService:JSONEncode({meshes=count,bad=bad})',dm))
 (OUT/'runtime-visual-flags.json').write_text(json.dumps(audit,indent=2)+'\n')
 (OUT/'console-final.json').write_text(json.dumps({dm:s.problems(dm) for dm in ['Server','Client']},indent=2)+'\n')
 print('final schedule samples',len(json.loads(d)['samples']))
finally:
 s.stop_play();clear_test_attrs(s)
