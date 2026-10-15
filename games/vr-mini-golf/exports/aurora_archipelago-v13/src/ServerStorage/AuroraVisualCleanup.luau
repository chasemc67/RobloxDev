-- Stage au5: visual-only cleanup. Original gameplay parts are never moved or resized.
local Cleanup = {}
local function parts(root)
 local out={} for _,p in root:GetDescendants() do if p:IsA('BasePart') then table.insert(out,p) end end return out
end
local function visibleCopy(p, parent, name, cf, size)
 local q=p:Clone()
 for _,c in q:GetChildren() do c:Destroy() end
 for _,tag in q:GetTags() do q:RemoveTag(tag) end
 q.Name=name;q.CFrame=cf;q.Size=size
 q.Anchored=true;q.CanCollide=false;q.CanQuery=false;q.CanTouch=false
 q:SetAttribute('VisualQueryDisabled',true);q:SetAttribute('AU5Visual',true)
 q.Parent=parent
 return q
end
function Cleanup.Apply(course)
 local r={blockoutHidden=0,baseCopies=0,sign=false,stone=false}
 if course.Name~='CourseAurora' then return r end
 -- Keep the folder for AuroraPropsBuilder's presentation-only lookups.
 local b=course:FindFirstChild('Blockout')
 if b then for _,p in parts(b) do
  assert(not p.CanCollide,'AU5: unexpected Blockout collider '..p:GetFullName())
  p.Transparency=1;p.CanCollide=false;p.CanQuery=false;p.CanTouch=false
  p:SetAttribute('AU5HiddenBlockout',true);r.blockoutHidden+=1
 end end
 local h14=course:FindFirstChild('Hole14')
 local sign=h14 and h14:FindFirstChild('h14_safe_side_sign',true)
 if sign and not sign:GetAttribute('AU5Separated') then
  for _,p in parts(sign) do assert(not p.CanCollide) end
  -- Shift away from the outside rail. Separate the face from its post by .08.
  sign:PivotTo(sign:GetPivot()+Vector3.new(0,0,0.28))
  local post=sign:FindFirstChild('h14_safe_side_sign__Timber',true)
  local face=sign:FindFirstChild('h14_safe_side_sign__AuroraTeal',true)
  local brass=sign:FindFirstChild('h14_safe_side_sign__Brass',true)
  local glow=sign:FindFirstChild('h14_safe_side_sign__Glow',true)
  local snow=sign:FindFirstChild('h14_safe_side_sign__Snow',true)
  if post and face then
   face.CFrame=face.CFrame+face.CFrame.ZVector*((post.Size.Z+face.Size.Z)/2+0.081)
  end
  if face and brass and glow and snow then
   local top=math.max(face.Position.Y+face.Size.Y/2,post.Position.Y+post.Size.Y/2)
   for _,p in {brass,glow,snow} do
    local y=top+0.081+p.Size.Y/2
    p.CFrame=p.CFrame+Vector3.new(0,y-p.Position.Y,0);top=y+p.Size.Y/2
   end
  end
  -- Rebase the visual finalizer so its cached v4 poses cannot undo this correction.
  for _,p in parts(sign) do
   p:SetAttribute('ZF1BaseCF',p.CFrame);p:SetAttribute('ZF1BaseSize',p.Size)
   if p:GetAttribute('ZF1MeshTerrainBaseCF') then p:SetAttribute('ZF1MeshTerrainBaseCF',p.CFrame);p:SetAttribute('ZF1MeshTerrainBaseSize',p.Size) end
  end
  sign:SetAttribute('AU5Separated',true);r.sign=true
 end
 local h6=course:FindFirstChild('Hole6')
 local stone=h6 and h6:FindFirstChild('h06_respawn_stone',true)
 if stone and not stone:GetAttribute('AU5Separated') then
  local params=RaycastParams.new();params.FilterType=Enum.RaycastFilterType.Include
  local colliders={} for _,p in parts(h6) do if p.CanCollide then table.insert(colliders,p) end end
  params.FilterDescendantsInstances=colliders
  for _,p in parts(stone) do
   assert(not p.CanCollide)
   p.Size=Vector3.new(math.max(.2,p.Size.X),math.max(.2,p.Size.Y),math.max(.2,p.Size.Z))
   local top=-math.huge
   for _,x in {-1,1} do for _,z in {-1,1} do
    local v=p.CFrame:PointToWorldSpace(Vector3.new(x*p.Size.X/2,0,z*p.Size.Z/2))
    local hit=workspace:Raycast(v+Vector3.new(0,10,0),Vector3.new(0,-20,0),params)
    assert(hit,'AU5 missing stone support');top=math.max(top,hit.Position.Y)
   end end
   local y=top+.081+p.Size.Y/2
   if p.Position.Y<y then p.CFrame=p.CFrame+Vector3.new(0,y-p.Position.Y,0) end
  end
  stone:SetAttribute('AU5Separated',true);r.stone=true
 end
 -- Stage au6: stack the two visible respawn layers above the unchanged shelf.
 -- Both are non-gameplay visuals; rebase every cached pose used by VisualSeparation.
 if stone then
  local marker=h6.Hazards:FindFirstChild('RespawnStone')
  local lime=stone:FindFirstChild('h06_respawn_stone__Lime',true)
  local layers={}
  if marker then table.insert(layers,marker) end
  if lime then table.insert(layers,lime) end
  local function halfY(p)
   return (math.abs(p.CFrame.RightVector.Y)*p.Size.X+math.abs(p.CFrame.UpVector.Y)*p.Size.Y+math.abs(p.CFrame.ZVector.Y)*p.Size.Z)/2
  end
  local supports={}
  for _,p in parts(h6) do if p.CanCollide or (p.Transparency<1 and p.Name=='Visual_Felt') then table.insert(supports,p) end end
  for _,p in layers do
   assert(not p.CanCollide and not p.CanQuery and not p.CanTouch,'AU6 protected stone layer')
   p.Size=Vector3.new(math.max(.2,p.Size.X),math.max(.2,p.Size.Y),math.max(.2,p.Size.Z))
   local top=-math.huge
   -- Analytic top plane avoids CanQuery=false omitting the visible felt skin.
   for _,support in supports do
    local n=support.CFrame.UpVector
    if math.abs(n.Y)>.9 then
     for _,x in {-1,1} do for _,z in {-1,1} do
      local wx=p.Position.X+x*.4 local wz=p.Position.Z+z*.4
      local plane=support.Position+n*support.Size.Y/2
      local y=plane.Y-(n.X*(wx-plane.X)+n.Z*(wz-plane.Z))/n.Y
      local q=support.CFrame:PointToObjectSpace(Vector3.new(wx,y,wz))
      if math.abs(q.X)<=support.Size.X/2+.001 and math.abs(q.Z)<=support.Size.Z/2+.001 then top=math.max(top,y) end
     end end
    end
   end
   assert(top>-math.huge,'AU6 missing shelf')
   if p==lime and marker then top=math.max(top,marker.Position.Y+halfY(marker)) end
   local y=top+.081+halfY(p)
   if p.Position.Y<y then p.CFrame=p.CFrame+Vector3.new(0,y-p.Position.Y,0) end
   p:SetAttribute('ZF1BaseCF',p.CFrame);p:SetAttribute('ZF1BaseSize',p.Size)
   if p:GetAttribute('ZF1MeshTerrainBaseCF') then
    p:SetAttribute('ZF1MeshTerrainBaseCF',p.CFrame);p:SetAttribute('ZF1MeshTerrainBaseSize',p.Size)
   end
  end
  stone:SetAttribute('AU6Separated',true);r.stone=true
 end
 local h5=course:FindFirstChild('Hole5')
 local col=h5 and h5:FindFirstChild('h05_geyser_column',true)
 if col then
  local basalt=col:FindFirstChild('h05_geyser_column__Basalt',true)
  if basalt then
   for _,p in h5.Geometry:GetChildren() do
    if p:IsA('BasePart') and p.Name=='Base' and not p:GetAttribute('AU5GeyserCut') then
     -- Subtract the column's full vertical travel footprint from the presentation only.
     local low=Vector3.new(math.huge,0,math.huge);local high=Vector3.new(-math.huge,0,-math.huge)
     for _,mesh in parts(col) do if mesh.Transparency<1 then
     for _,x in {-1,1} do for _,z in {-1,1} do
      local v=p.CFrame:PointToObjectSpace(mesh.CFrame:PointToWorldSpace(Vector3.new(x*mesh.Size.X/2,0,z*mesh.Size.Z/2)))
      low=Vector3.new(math.min(low.X,v.X-.081),0,math.min(low.Z,v.Z-.081))
      high=Vector3.new(math.max(high.X,v.X+.081),0,math.max(high.Z,v.Z+.081))
     end end
     end end
     local x0,x1=-p.Size.X/2,p.Size.X/2;local z0,z1=-p.Size.Z/2,p.Size.Z/2
     local a,c=math.max(x0,low.X),math.min(x1,high.X)
     local d,e=math.max(z0,low.Z),math.min(z1,high.Z)
     if a<c and d<e then
      local rectangles={{x0,a,z0,z1},{c,x1,z0,z1},{a,c,z0,d},{a,c,e,z1}}
      for i,box in rectangles do
       local sx,sz=box[2]-box[1],box[4]-box[3]
       if sx>=.2 and sz>=.2 then
        visibleCopy(p,h5.Geometry,'AU5BaseVisual'..i,p.CFrame*CFrame.new((box[1]+box[2])/2,0,(box[3]+box[4])/2),Vector3.new(sx,p.Size.Y,sz))
        r.baseCopies+=1
       end
      end
      p.Transparency=1;p:SetAttribute('AU5GeyserCut',true)
     end
    end
   end
  end
 end
 return r
end
return Cleanup
