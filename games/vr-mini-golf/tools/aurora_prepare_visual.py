#!/usr/bin/env python3
"""Normalize the local FBX import from its world-space manifest; never upload."""
import json
from pathlib import Path
from holes_to_lua import REPO, to_lua
from run_playtests import Studio

manifest = json.loads((Path(REPO) / 'assets/vr-mini-golf/aurora-archipelago/blockout_aurora_manifest.json').read_text())
objects = {o['name']: o for h in manifest['holes'] for o in h['objects']}
code = 'local specs=' + to_lua(objects) + '''
assert(game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient"), "LOCAL ONLY")
local root=workspace:FindFirstChild("blockout_aurora") or workspace.CourseAurora.Blockout
local count,hidden=0,0
local missing={}
for _,p in root:GetDescendants() do
 if p:IsA("BasePart") then
  local spec=specs[p.Name]
  if spec then
   local b=spec.bbox_roblox_world
   if b then
    local mn,mx=Vector3.new(unpack(b[1])),Vector3.new(unpack(b[2]))
    p.Size=mx-mn
    -- Importer baked a 180 degree Y rotation into the mesh vertices.
    p.CFrame=CFrame.new((mn+mx)/2)*CFrame.Angles(0,math.pi,0)
   end
   local cat=spec.category
   -- Keep generated felt/cup holes and live mover visuals visible, avoiding duplicate static skins.
   if cat=="clearance" or cat=="cupclear" or cat=="guard" or cat=="felt" or cat=="moving" or cat=="toggle" then
    p.Transparency=1 hidden+=1
   end
  else table.insert(missing,p.Name) end
  p.Anchored=true p.CanCollide=false p.CanQuery=false p.CanTouch=false
  count+=1
 end
end
root.Name="Blockout" root.Parent=workspace.CourseAurora root.WorldPivot=CFrame.identity
root:SetAttribute("ImportUndoYaw",180) root:SetAttribute("VisualOnly",true)
local toggle=workspace.CourseAurora.Hole17.Movers.Mover_aurora_span
game:GetService("CollectionService"):AddTag(toggle,"GolfMover")
toggle:SetAttribute("Speed",0) toggle:SetAttribute("Phase",0)
return {parts=count,hidden=hidden,missing=missing,upload=false}
'''
if __name__ == '__main__':
    result = Studio().luau(code)
    print(result)
    json.loads(result)  # fail instead of accepting a Studio error string
    Path('playtests/stage-ac2/import.json').write_text(result + '\n')
