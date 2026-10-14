assert(game.PlaceId==0 and not game:FindService("NetworkClient"))
local ss=game.ServerStorage
local function audit(course)
 local result={images={},carriers={},placeholders=0}
 for _,p in course:GetDescendants() do
  if p:IsA("Decal") and p.Name=="HintImage" then
   table.insert(result.images,{path=p:GetFullName(),asset=p.Texture,face=p.Face.Name})
  elseif p:IsA("BasePart") and p:GetAttribute("StageAl2Hint") then
   assert(not p.CanCollide and not p.CanQuery and not p.CanTouch)
   if p.Name=="FeltDecalCarrier" then
    local top=p.CFrame.ZVector
    assert(top:Dot(p:GetAttribute("ImageTopDirection"))>.99999)
    local hole=p:FindFirstAncestor("Hole9") or p:FindFirstAncestor("Hole14")
    local params=RaycastParams.new() params.FilterType=Enum.RaycastFilterType.Include
    local felt={} for _,v in hole.Geometry:GetDescendants() do if v:IsA("BasePart") and v:HasTag("GolfSurface") then table.insert(felt,v) end end
    params.FilterDescendantsInstances=felt
    local hit=workspace:Raycast(p.Position+Vector3.new(0,2,0),Vector3.new(0,-4,0),params)
    assert(hit,"missing felt beneath carrier")
    local lift=p.Position.Y+p.Size.Y/2-hit.Position.Y
    assert(math.abs(lift-.03)<.001,"wrong felt lift")
    table.insert(result.carriers,{path=p:GetFullName(),imageTop={top.X,top.Y,top.Z},lift=lift,collide=p.CanCollide,query=p.CanQuery,touch=p.CanTouch})
   end
  end
 end
 assert(#result.images==5 and #result.carriers==3)
 for _,row in {{9,"sign_bypass"},{9,"felt_arrow_bypass"},{14,"safe_bank_sign"},{14,"safe_bank_arrow"},{14,"timing_arrow"}} do
  assert(not course['Hole'..row[1]].Decor[row[2]]:FindFirstChild("Placeholder"))
 end
 return result
end
local report={live=audit(workspace.CourseSugarloaf)}
local before={}
for _,p in workspace.CourseSugarloaf:GetDescendants() do if p:IsA('BasePart') and p:GetAttribute('StageAl2Hint') then before[p:GetFullName()]={p.CFrame,p.Size} end end
require(ss.SugarloafHints:Clone()).Apply(workspace.CourseSugarloaf)
for _,p in workspace.CourseSugarloaf:GetDescendants() do if p:IsA('BasePart') and p:GetAttribute('StageAl2Hint') then local b=before[p:GetFullName()] assert(b and b[1]==p.CFrame and b[2]==p.Size,'hint pose drift') end end
report.idempotent=true
local data=require(ss.CourseData.SugarloafCanyon:Clone())
local subset=table.clone(data) subset.holes={data.holes[9],data.holes[14]}
local name="StageAL2Reference"
assert(not workspace:FindFirstChild(name))
local ok,err=pcall(function()
 require(ss.CourseBuilder:Clone()).Build(subset,require(ss.CourseData.SugarloafLayout:Clone()),{folder=name,courseId="sugarloaf_canyon",palette="sugarloaf"})
 report.rebuild=audit(workspace[name])
end)
if workspace:FindFirstChild(name) then workspace[name]:Destroy() end
assert(ok,err)
local preload={}
game.ContentProvider:PreloadAsync({"rbxassetid://107264623944550","rbxassetid://131067632603421","rbxassetid://123495746026639","rbxassetid://82085948994874","rbxassetid://139894260913924"},function(id,status) preload[id]=status.Name end)
report.preload=preload
return game.HttpService:JSONEncode(report)
