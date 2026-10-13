"""Read-only Play measurements for local Stage ag files; never saves or publishes."""
import json
from pathlib import Path
from run_playtests import Studio
s=Studio()
assert s.mode()[0] != 'Edit', 'Play first'
code='''
local m=workspace.CourseAurora.Hole17.Movers.Mover_aurora_span
local p=m:FindFirstChild("TogglePart").Value
local rows={}
local start=workspace:GetServerTimeNow()
repeat
 local t=workspace:GetServerTimeNow()
 table.insert(rows,{t=t,elapsed=t-start,phase=t%9,collide=p.CanCollide,query=p.CanQuery,touch=p.CanTouch})
 task.wait(0.04)
until workspace:GetServerTimeNow()-start>=20
return game:GetService("HttpService"):JSONEncode({attributes=m:GetAttributes(),part=p:GetFullName(),samples=rows})
'''
r=s.luau(code,'Server',timeout=45)
Path('playtests/stage-ag/h17-schedule.json').write_text(json.dumps(json.loads(r),indent=2))
print('wrote H17 20-second schedule')
