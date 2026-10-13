"""Read-only visual flags and H15 test-physics audit in active native Play."""
import json
from pathlib import Path
from run_playtests import Studio
s=Studio()
code='''local c=workspace.CourseSugarloaf local out={dock={},h15={},signs={}}
for _,p in c.Hole14.StageAJVisuals.h14_loading_dock:GetDescendants() do if p:IsA("BasePart") then
 table.insert(out.dock,{name=p.Name,collide=p.CanCollide,query=p.CanQuery,touch=p.CanTouch,queryDisabled=p:GetAttribute("VisualQueryDisabled")})
end end
for _,p in c.Hole15.Geometry:GetDescendants() do if p:IsA("BasePart") and p:GetAttribute("WallId") then
 local prop=p.CurrentPhysicalProperties table.insert(out.h15,{wall=p:GetAttribute("WallId"),density=prop.Density,friction=prop.Friction,elasticity=prop.Elasticity,weight=prop.FrictionWeight})
end end
for _,n in {9,14} do for _,a in c["Hole"..n].Decor:GetChildren() do if a.Name:find("sign") or a.Name:find("arrow") then table.insert(out.signs,a:GetFullName()) end end end
out.orePlaceholder=c.Hole14.Decor.ore_piles:FindFirstChild("Placeholder")~=nil
out.pumpPlaceholder=c.Hole9.Decor.pump_house:FindFirstChild("Placeholder")~=nil
return game.HttpService:JSONEncode(out)'''
result={dm:json.loads(s.luau(code,dm)) for dm in ('Server','Client')}
for dm,r in result.items():
 assert len(r['dock'])==5 and len(r['h15'])==12
 assert all(not v['collide'] and not v['query'] and not v['touch'] and v['queryDisabled'] for v in r['dock'])
 assert all(abs(v['friction']-.1)<1e-6 and v['weight']==100 for v in r['h15'])
 assert not r['orePlaceholder'] and not r['pumpPlaceholder']
Path('playtests/stage-al/runtime-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('Native server/client: 5 visual-only dock meshes, 12 H15 test rails, placeholders absent; signs recorded')
