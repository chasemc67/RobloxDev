"""Save baseline geometry and collision evidence for stage zf1 (read only)."""
import json
from pathlib import Path
from run_playtests import Studio
s=Studio(); assert s.mode()[0]=='Edit'
code='''local r={parts={},placeholders={}} for _,p in workspace:GetDescendants() do if p:IsA('BasePart') then local v={path=p:GetFullName(),class=p.ClassName,cf={p.CFrame:GetComponents()},size={p.Size.X,p.Size.Y,p.Size.Z},transparency=p.Transparency,collide=p.CanCollide,query=p.CanQuery,touch=p.CanTouch,material=p.Material.Name,tags=p:GetTags()} if p.CanCollide then local q=p.CurrentPhysicalProperties v.physics={q.Density,q.Friction,q.Elasticity,q.FrictionWeight,q.ElasticityWeight} end table.insert(r.parts,v) if p:FindFirstAncestor('Placeholder') then table.insert(r.placeholders,v) end end end _G.ZF1Inventory=game.HttpService:JSONEncode(r) return #_G.ZF1Inventory'''
n=int(s.luau(code));raw=''.join(json.loads(s.luau('return game.HttpService:JSONEncode(_G.ZF1Inventory:sub(%d,%d))'%(i+1,i+40000))) for i in range(0,n,40000))
p=Path('playtests/stage-zf1/inventory-before.json'); p.write_text(raw+'\n')
r=json.loads(raw);print('parts',len(r['parts']),'placeholder parts',len(r['placeholders']),'visible',sum(x['transparency']<1 for x in r['placeholders']))
