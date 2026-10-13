assert(game.PlaceId==0 and not game:FindFirstChildOfClass('NetworkClient'),'LOCAL ONLY')
local ids={'rope_bridges','gumdrops','pump_house','sluice_flume','lock_keeper_hut','intake_tower','maze_rock','cableway_trestle','sugar_dune','sinkhole_rim','gnomon','arch_gate'}
local changed={}
local function hide(p)
 assert(p:IsA('BasePart') and not p.CanCollide,'physical part must stay unchanged')
 if p.Transparency<1 then table.insert(changed,p:GetFullName()) end
 p.Transparency=1
end
for i,id in ids do
 local h=workspace.CourseSugarloaf['Hole'..(i+6)]
 local p=h.Decor[id]:FindFirstChild('Placeholder')
 if p then for _,v in p:GetDescendants() do if v:IsA('BasePart') then hide(v) end end end
end
-- Exact gumdrop collision boxes are in Geometry; these are obsolete nonphysical bumper skins.
for _,name in {'Bumper_gumdrop1','Bumper_gumdrop2'} do hide(workspace.CourseSugarloaf.Hole8.Rails[name]) end
return game.HttpService:JSONEncode(changed)
