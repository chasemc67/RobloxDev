assert(game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient"),"LOCAL ONLY")
local course=workspace.CourseSugarloaf
local ids={"trailhead_arch","headframe","ranger_station","geode_wall","echo_walls","bell_tower"}
local changed={}
local timing={[6]="sluice_gate",[9]="windpump_wheel",[14]="ore_bucket",[17]="shadow_arm"}
for n=1,18 do
 local h=course["Hole"..n]
 for _,name in {"Flag","FlagPole"} do
  local p=h:FindFirstChild(name)
  if p and p:IsA("BasePart") then p.Transparency=1 table.insert(changed,p:GetFullName()) end
 end
 for _,id in {"cup_flag",ids[n] or "",timing[n] or ""} do
  local anchor=h.Decor:FindFirstChild(id)
  local p=anchor and anchor:FindFirstChild("Placeholder")
  if p then
   for _,v in p:GetDescendants() do
    if v:IsA("BasePart") then assert(not v.CanCollide,"physical placeholder") v.Transparency=1 end
   end
   table.insert(changed,p:GetFullName())
  end
 end
end
for _,m in course.Hole17.Movers:GetDescendants() do
 if m:IsA("Model") and m.Name:match("^h17_shadow_arm_head_") then
  for _,p in m:GetDescendants() do if p:IsA("BasePart") then
   assert(not p.CanCollide,"physical old shadow head") p.Transparency=1
  end end
  table.insert(changed,m:GetFullName())
 end
end
return game.HttpService:JSONEncode(changed)
