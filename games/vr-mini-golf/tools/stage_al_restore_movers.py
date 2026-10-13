"""Undo unrelated diagnostic ApplyPhysics normalization using exact preflight values."""
import json
from pathlib import Path
from run_playtests import Studio
from holes_to_lua import to_lua
out=Path('playtests/stage-al')
a=json.loads((out/'before-colliders.json').read_text())
rows=[r for r in a if '.Movers.' in r['path'] and r['path'].endswith('_collision.Blocker')]
s=Studio();assert s.mode()[0]=='Edit'
code='local records='+to_lua(rows)+''' local out={}
assert(game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient"))
for _,r in records do local p=game for name in r.path:gmatch("[^.]+") do p=assert(p:FindFirstChild(name),name) end
 p.CustomPhysicalProperties=PhysicalProperties.new(unpack(r.physics))
 table.insert(out,{path=r.path,physics=r.physics})
end return game.HttpService:JSONEncode(out)'''
r=s.luau(code);json.loads(r);(out/'restored-mover-physics.json').write_text(r)
print(r)
