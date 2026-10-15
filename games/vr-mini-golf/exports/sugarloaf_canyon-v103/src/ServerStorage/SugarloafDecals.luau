-- Stage zf1: 29 approved Game Art Bot images. Reuse every placeholder instance.
-- Asset provenance: tools/stage_zf1_assets.json. No collision surface is changed.
local Decals = {}
local GAP = 0.08
local specs = {
 {hole=2,name="sign_left",asset="rbxassetid://132295848610548",position=Vector3.new(-13.55,0,-12.0),size=Vector3.new(1.8,3.2,0.25)},
 {hole=2,name="sign_mid",asset="rbxassetid://140468413273474",position=Vector3.new(-1.2,8,-15.4),size=Vector3.new(3.0,1.0,0.2)},
 {hole=2,name="sign_right",asset="rbxassetid://79477609841941",position=Vector3.new(13.55,0,-12.0),size=Vector3.new(1.8,3.2,0.25)},
 {hole=2,name="felt_arrow_left",asset="rbxassetid://82045355627361",position=Vector3.new(-9.5,0.0,-14.0),size=Vector3.new(1.4,0.01,2.0)},
 {hole=2,name="felt_arrow_right",asset="rbxassetid://136490984306039",position=Vector3.new(9.0,0.0,-14.0),size=Vector3.new(1.4,0.01,2.0)},
 {hole=3,name="sign_plank",asset="rbxassetid://96229015344567",position=Vector3.new(2.2,0,-30.8),size=Vector3.new(1.6,2.6,0.2)},
 {hole=3,name="sign_bridge",asset="rbxassetid://78901465650444",position=Vector3.new(-13.578,0,-25.155),size=Vector3.new(1.8,3.2,0.25)},
 {hole=3,name="route_arrow_plank",asset="rbxassetid://132467328579602",position=Vector3.new(0,0,-25),size=Vector3.new(1.4,0.01,2.0)},
 {hole=3,name="route_arrow_bridge",asset="rbxassetid://92616507344160",position=Vector3.new(-8.5,0,-25),size=Vector3.new(1.4,0.01,2.0)},
 {hole=6,name="sign_overflow",asset="rbxassetid://77257179355965",position=Vector3.new(12.55,0,-21.0),size=Vector3.new(1.8,3.2,0.25)},
 {hole=6,name="felt_arrow_overflow",asset="rbxassetid://84814341457933",position=Vector3.new(9.5,0.0,-23.5),size=Vector3.new(1.4,0.01,2.0)},
 {hole=6,name="flood_marks",asset="rbxassetid://98287707564328",position=Vector3.new(-11.8,0,-22.0),size=Vector3.new(0.3,4,3)},
 {hole=10,name="felt_arrow_deck",asset="rbxassetid://109316462498294",position=Vector3.new(0.0,0.0,-10.0),size=Vector3.new(2.4,0.01,3.0)},
 {hole=11,name="felt_arrow_lock",asset="rbxassetid://99616139650559",position=Vector3.new(0.0,0.0,-18.0),size=Vector3.new(1.4,0.01,2.0)},
 {hole=12,name="sign_pier",asset="rbxassetid://78028777110381",position=Vector3.new(2.756,0,-22.795),size=Vector3.new(1.6,2.6,0.2)},
 {hole=12,name="sign_shore",asset="rbxassetid://134938154207517",position=Vector3.new(-17.55,0,-24.0),size=Vector3.new(1.8,3.2,0.25)},
 {hole=12,name="felt_arrow_pier",asset="rbxassetid://123303838002269",position=Vector3.new(0.0,0.0,-20.0),size=Vector3.new(1.4,0.01,2.0)},
 {hole=12,name="felt_arrow_shore",asset="rbxassetid://75338689222423",position=Vector3.new(-13.5,0.0,-24.0),size=Vector3.new(1.4,0.01,2.0)},
 {hole=13,name="sign_west",asset="rbxassetid://140303880645441",position=Vector3.new(-14.9,0,-10.0),size=Vector3.new(1.8,3.2,0.25)},
 {hole=13,name="sign_centre",asset="rbxassetid://101624286616515",position=Vector3.new(2.943,0,-17.796),size=Vector3.new(1.8,3.2,0.25)},
 {hole=13,name="sign_east",asset="rbxassetid://135547768972998",position=Vector3.new(14.9,0,-10.0),size=Vector3.new(1.8,3.2,0.25)},
 {hole=13,name="route_arrow_west",asset="rbxassetid://129854043886070",position=Vector3.new(-11.5,0,-13),size=Vector3.new(1.4,0.01,2.0)},
 {hole=13,name="route_arrow_centre",asset="rbxassetid://111870680131624",position=Vector3.new(0,0,-13),size=Vector3.new(1.4,0.01,2.0)},
 {hole=13,name="route_arrow_east",asset="rbxassetid://131569293724014",position=Vector3.new(11.5,0,-13),size=Vector3.new(1.4,0.01,2.0)},
 {hole=15,name="slope_arrows",asset="rbxassetid://129059764709956",position=Vector3.new(0.0,-2.2,-24.0),size=Vector3.new(20,0.01,2)},
 {hole=15,name="lip_chevrons",asset="rbxassetid://91089251317155",position=Vector3.new(0,0,-9.5),size=Vector3.new(7,0.01,1)},
 {hole=16,name="felt_arrow_sink",asset="rbxassetid://104339454768598",position=Vector3.new(0.0,0.0,-10.0),size=Vector3.new(1.4,0.01,2.0)},
 {hole=18,name="sign_rim",asset="rbxassetid://130671607077130",position=Vector3.new(-13.55,0.8,-42.0),size=Vector3.new(1.8,3.2,0.25)},
 {hole=18,name="felt_arrow_bank",asset="rbxassetid://86154332587382",position=Vector3.new(1.0,0.0,-10.0),size=Vector3.new(2.0,0.01,2.6)},
}
local function visual(part)
 part.Anchored = true
 part.CanCollide, part.CanQuery, part.CanTouch = false, false, false
 part.CastShadow = false
 part:SetAttribute("VisualQueryDisabled", true)
 part:SetAttribute("StageZf1DecalCarrier", true)
end
local function surfaceAt(hole, position)
 local geometry = hole:FindFirstChild("Geometry")
 local best, bestY
 for _, p in geometry and geometry:GetDescendants() or {} do
  if p:IsA("BasePart") and p.CanCollide and p.Name == "Felt" then
   local normal = p.CFrame.UpVector
   if normal.Y < 0.5 then continue end
   local top = p.Position + normal * p.Size.Y / 2
   local y = top.Y - (normal.X * (position.X-top.X) + normal.Z * (position.Z-top.Z))/normal.Y
   local hit = Vector3.new(position.X,y,position.Z)
   local lp = p.CFrame:PointToObjectSpace(hit)
   if math.abs(lp.X)<=p.Size.X/2 and math.abs(lp.Z)<=p.Size.Z/2 and (not bestY or y>bestY) then
    best, bestY = p, y
   end
  end
 end
 return best, bestY
end
function Decals.Apply(course)
 assert(course, "Sugarloaf decal course missing")
 local report = {placed={}, missing={}}
 for _, spec in specs do
  local hole = course:FindFirstChild("Hole"..spec.hole)
  local decor = hole and hole:FindFirstChild("Decor")
  local target = decor and decor:FindFirstChild(spec.name)
  local placeholder = target and target:FindFirstChild("Placeholder")
  if not placeholder then table.insert(report.missing,spec.name); continue end
  local sign = string.sub(spec.name,1,5)=="sign_"
  local face
  for _,p in placeholder:GetDescendants() do
   if p:IsA("BasePart") and ((sign and p.Name=="SignBoard") or (not sign and not face)) then face=p end
  end
  if not face then table.insert(report.missing,spec.name); continue end
  -- Capture original sign orientation once: subsequent Apply calls are stable.
  local baseCF = face:GetAttribute("StageZf1OriginalCFrame") or face.CFrame
  face:SetAttribute("StageZf1OriginalCFrame",baseCF)
  local frame = CFrame.new(hole:GetAttribute("HoleOrigin")) * CFrame.Angles(0,math.rad(hole:GetAttribute("HoleYaw") or 0),0)
  local position = frame:PointToWorldSpace(spec.position)
  for _,p in placeholder:GetDescendants() do
   if p:IsA("BasePart") then
    assert(not p.CanCollide,"Decal placeholder unexpectedly collidable: "..p:GetFullName())
    if p~=face and p.Name~="SignPost" then p.Transparency=1 end
    -- Remove old text from boards; the uploaded illustration contains the lettering.
    for _,child in p:GetChildren() do
     if child:IsA("SurfaceGui") then child.Enabled=false end
    end
   end
  end
  visual(face)
  face.Material=Enum.Material.SmoothPlastic
  face.Color=Color3.fromRGB(245,235,211)
  local decalFace=Enum.NormalId.Top
  if sign then
   local wide=spec.name=="sign_mid"
   face.Size=wide and Vector3.new(3,0.8,0.2) or Vector3.new(1.6,3.2,0.2)
   -- The board sits wholly in front of the .2-stud post with an .08 gap.
   face.CFrame=baseCF * CFrame.new(0,0,-0.28)
   face.Transparency=0
   decalFace=Enum.NormalId.Front
  elseif spec.name=="flood_marks" then
   face.Size=Vector3.new(1.5,3,0.2)
   local inward=frame:VectorToWorldSpace(Vector3.new(1,0,0))
   face.CFrame=CFrame.lookAt(position+Vector3.new(0,1.5,0)+inward*0.38,position+Vector3.new(0,1.5,0)+inward*1.38)
   face.Transparency=0
   decalFace=Enum.NormalId.Front
  else
   local surface,y=surfaceAt(hole,position)
   if not surface then table.insert(report.missing,spec.name..": no felt below"); continue end
   local normal=surface.CFrame.UpVector
   position=Vector3.new(position.X,y,position.Z)
   face.Size=Vector3.new(math.max(.2,spec.size.X),.2,math.max(.2,spec.size.Z))
   -- Carrier is transparent; the image plane, not its invisible underside, is .08 above felt.
   position += normal*(GAP-face.Size.Y/2)
   if spec.name=="slope_arrows" then
    -- Art chevrons point toward image +X. Make image +X the physical downhill tangent.
    local downhill=(Vector3.new(0,-1,0)-normal*Vector3.new(0,-1,0):Dot(normal)).Unit
    -- Top-face UV right is local -X (its image top is local +Z).
    local right=-downhill
    local back=right:Cross(normal).Unit
    face.CFrame=CFrame.fromMatrix(position,right,normal,back)
    face:SetAttribute("ImageRightDirection",downhill)
    face:SetAttribute("DownhillDot",downhill.Y)
   else
    local imageTop=frame:VectorToWorldSpace(Vector3.new(0,0,-1))
    imageTop=(imageTop-normal*imageTop:Dot(normal)).Unit
    -- Roblox Top image top points along carrier local +Z, as in SugarloafHints.
    face.CFrame=CFrame.fromMatrix(position,normal:Cross(imageTop).Unit,normal,imageTop)
    face:SetAttribute("ImageTopDirection",imageTop)
   end
   face.Transparency=1
   face:SetAttribute("FeltLift",GAP)
  end
  local image=face:FindFirstChild("StageZf1Image") or Instance.new("Decal")
  image.Name="StageZf1Image"
  image.Texture=spec.asset
  image.Face=decalFace
  image.Parent=face
  table.insert(report.placed,{name=spec.name,hole=spec.hole,asset=spec.asset,path=face:GetFullName(),face=decalFace.Name})
 end
 course:SetAttribute("StageZf1DecalsPlaced",#report.placed)
 return report
end
return Decals
