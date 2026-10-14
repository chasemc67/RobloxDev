-- Stage al2: approved image assets, visual-only hints preserved by course rebuilds.
local Hints = {}
local specs = {
 {hole=9, name="sign_bypass", id="107264623944550", sign=true},
 {hole=14, name="safe_bank_sign", id="131067632603421", sign=true},
 -- Directions are hole-local: transform the authored route into the rotated course.
 {hole=9, name="felt_arrow_bypass", id="123495746026639", direction=Vector3.new(0,0,-1)},
 -- Toward the west/left rail ahead of the tee, consistent with the printed bank cue.
 {hole=14, name="safe_bank_arrow", id="82085948994874", direction=Vector3.new(-1,0,-1).Unit},
 {hole=14, name="timing_arrow", id="139894260913924", direction=Vector3.new(0,0,-1)},
}
local function visual(p)
 p.Anchored=true
 p.CanCollide,p.CanQuery,p.CanTouch=false,false,false
 p.CastShadow=false
 p:SetAttribute("VisualQueryDisabled",true)
 p:SetAttribute("StageAl2Hint",true)
end
function Hints.Apply(course)
 local report={placed={},removedParts={}}
 for _,spec in specs do
  local hole=course:FindFirstChild("Hole"..spec.hole)
  local decor=hole and hole:FindFirstChild("Decor")
  local target=decor and decor:FindFirstChild(spec.name)
  if not target then continue end
  local anchor=target:FindFirstChild("Anchor")
  assert(anchor and anchor:IsA("BasePart"),"hint anchor missing: "..spec.name)
  local old=target:FindFirstChild("Placeholder")
  -- These five targets have primitive placeholders, not imported sign meshes.
  if old then
   for _,p in old:GetDescendants() do
    if p:IsA("BasePart") then table.insert(report.removedParts,p:GetFullName()) end
   end
   old:Destroy()
  end
  local prior=target:FindFirstChild("HintVisual")
  if prior then prior:Destroy() end
  local model=Instance.new("Model") model.Name="HintVisual"
  local face=Instance.new("Part") visual(face)
  if spec.sign then
   -- Same board center/front as the former block; portrait ratio matches the PNG.
   face.Name="SignBoard" face.Size=Vector3.new(1.8,3.2,.15)
   local pos=anchor.Position+Vector3.new(0,1.1,0)
   local normal=spec.hole==9 and Vector3.new(-1,0,0) or Vector3.new(0,0,-1)
   face.CFrame=CFrame.lookAt(pos,pos+normal)
   face.Color=Color3.fromRGB(133,87,55) face.Material=Enum.Material.Wood
   local post=Instance.new("Part") visual(post)
   post.Name="SignPost" post.Size=Vector3.new(.2,3.2,.2)
   post.CFrame=CFrame.new(anchor.Position-normal*.2) post.Color=face.Color post.Material=face.Material
   post.Parent=model
  else
   face.Name="FeltDecalCarrier" face.Size=Vector3.new(1.4,.01,2)
   local pos=Vector3.new(anchor.Position.X,anchor.Position.Y-anchor.Size.Y/2+.025,anchor.Position.Z)
   local direction=CFrame.Angles(0,math.rad(hole:GetAttribute("HoleYaw") or 0),0):VectorToWorldSpace(spec.direction)
   -- Roblox Top-face image top maps to local +Z, opposite the part LookVector.
   face.CFrame=CFrame.lookAt(pos,pos-direction)
   face.Transparency=1
   face:SetAttribute("ImageTopDirection",direction)
   face:SetAttribute("HoleLocalImageTopDirection",spec.direction)
   face:SetAttribute("FeltLift",.03)
  end
  local decal=Instance.new("Decal") decal.Name="HintImage"
  decal.Texture="rbxassetid://"..spec.id
  decal.Face=spec.sign and Enum.NormalId.Front or Enum.NormalId.Top
  decal.Parent=face face.Parent=model model.Parent=target
  table.insert(report.placed,{name=spec.name,assetId=spec.id,path=decal:GetFullName()})
 end
 return report
end
return Hints
