-- Stage zf1. Deterministic build-level visual rules, independent of course physics.
-- Apply AFTER all imports, hints and decals. Original colliders never move/resize.
local CollectionService = game:GetService("CollectionService")
local Separation = {}
local GAP, MINIMUM, EPS = 0.08, 0.2, 0.00001
local function hole(p)
 local n=p
 while n and n~=workspace do
  local h=n.Name:match("^Hole(%d+)$")
  if h then return tonumber(h) end
  n=n.Parent
 end
 return 0
end
local function dimensions(s) return {s.X,s.Y,s.Z} end
local function vector(t) return Vector3.new(t[1],t[2],t[3]) end
local function exactBox(p)
 return p:IsA("Part") and (p.Shape==Enum.PartType.Block or p.Shape==Enum.PartType.Cylinder) and not p:FindFirstChildOfClass("SpecialMesh")
end
local function faces(p)
 local axes={p.CFrame.RightVector,p.CFrame.UpVector,p.CFrame.ZVector}
 local half={p.Size.X/2,p.Size.Y/2,p.Size.Z/2}
 local out={}
 for i=1,3 do
  -- Roblox cylinders run along local X. Their +/-X end caps are planar;
  -- the remaining OBB faces are curved-surface bounds and must not be moved.
  if p:IsA("Part") and p.Shape==Enum.PartType.Cylinder and i~=1 then continue end
  local u,v=i%3+1,(i+1)%3+1
  for _,sign in {-1,1} do
   table.insert(out,{axis=i,sign=sign,n=axes[i]*sign,c=p.Position+axes[i]*half[i]*sign,
    u=axes[u],v=axes[v],hu=half[u],hv=half[v]})
  end
 end
 return out
end
local function projectedOverlap(a,b,allowTilt)
 if not allowTilt and math.abs(a.n:Dot(b.n))<0.999999 then return false end
 for _,axis in {a.u,a.v,b.u,b.v} do
  local ac,bc=a.c:Dot(axis),b.c:Dot(axis)
  local ar=math.abs(a.u:Dot(axis))*a.hu+math.abs(a.v:Dot(axis))*a.hv
  local br=math.abs(b.u:Dot(axis))*b.hu+math.abs(b.v:Dot(axis))*b.hv
  if math.min(ac+ar,bc+br)-math.max(ac-ar,bc-br)<=EPS then return false end
 end
 return true
end
local function overlaps(a,b)
 return math.abs((b.c-a.c):Dot(a.n))<GAP-0.0005 and projectedOverlap(a,b)
end
local function name(p) return p:GetFullName() end
local function key(p)
 local c=p:GetAttribute("ZF1BaseCF") or p.CFrame
 return (p:GetAttribute("ZF1SourcePath") or name(p))..string.format("|%.5f|%.5f|%.5f",c.X,c.Y,c.Z)
end
local function topCarrier(p)
 for _,d in p:GetChildren() do
  if (d:IsA("Decal") or d:IsA("Texture")) and d.Transparency<1 and d.Face==Enum.NormalId.Top then return true end
 end
 return false
end
local function decorated(p)
 for _,c in p:GetChildren() do
  if ((c:IsA("Decal") or c:IsA("Texture")) and c.Transparency<1) or (c:IsA("SurfaceGui") and c.Enabled) then return true end
 end
 return false
end
function Separation.Apply(course, scenery)
 assert(course,"VisualSeparation requires a course")
 -- Optional authored scenery participates in the same face-pair pass, including course/world joins.
 local function descendants()
  local out=course:GetDescendants()
  if scenery and scenery~=course then
   for _,p in scenery:GetDescendants() do table.insert(out,p) end
  end
  return out
 end
 local report={gap=GAP,minimumThickness=MINIMUM,fixes={},exclusions={},unresolved={},colliderCopies={},thinAfter={},protectedFelt={},invariantFailures={}}
 local terrainParams=RaycastParams.new()
 terrainParams.FilterType=Enum.RaycastFilterType.Include
 terrainParams.FilterDescendantsInstances={workspace.Terrain}
 terrainParams.IgnoreWater=false
 local originals={}
 local records={}
 local detachedJoints={}
 local jointedParts={}
 local cloneJoints={}
 -- CFrame assignment to a welded visual otherwise moves the entire mover assembly,
 -- including invisible ball blockers. Disconnect joints for the complete edit pass,
 -- including baseline reset, then reconnect at their new visual-only relative pose.
 for _,j in descendants() do
  if (j:IsA("WeldConstraint") or j:IsA("JointInstance")) and j.Part0 and j.Part1 then
   jointedParts[j.Part0]=true;jointedParts[j.Part1]=true
   table.insert(detachedJoints,{joint=j,p0=j.Part0,p1=j.Part1,c0=j:IsA("JointInstance") and j.C0 or nil,
    c1=j:IsA("JointInstance") and j.C1 or nil,cf0=j.Part0.CFrame,cf1=j.Part1.CFrame})
   j.Part1=nil
  end
 end
 -- Collider originals retain tags, query flags, physical properties and exact pose.
 -- Their visual clones live outside Placeholder containers, so placeholder totals do not grow.
 local function visual(r)
  local p=r.part
  if not p.CanCollide then return p end
  local existing=p:FindFirstChild("ZF1VisualReference")
  if existing and existing:IsA("ObjectValue") and existing.Value then r.part=existing.Value;return r.part end
  local clone=p:Clone()
  for _,d in clone:GetDescendants() do
   if d:IsA("BaseScript") or d:IsA("ModuleScript") or d:IsA("Constraint") or d:IsA("JointInstance") or d:IsA("BasePart") then d:Destroy() end
  end
  for _,tag in CollectionService:GetTags(clone) do CollectionService:RemoveTag(clone,tag) end
  for attr in clone:GetAttributes() do clone:SetAttribute(attr,nil) end
  clone.Name="Visual_"..p.Name
  clone.CanCollide=false;clone.CanTouch=false;clone.CanQuery=false
  clone:SetAttribute("VisualQueryDisabled",true)
  clone:SetAttribute("ZF1VisualClone",true)
  clone:SetAttribute("ZF1SourcePath",r.name)
  clone:SetAttribute("ZF1BaseCF",p.CFrame);clone:SetAttribute("ZF1BaseSize",p.Size)
  local parent=p
  while parent.Parent and parent.Parent~=course and parent.Parent~=scenery do parent=parent.Parent end
  local folder=parent:FindFirstChild("ZF1VisualLayers")
  if not folder then folder=Instance.new("Folder");folder.Name="ZF1VisualLayers";folder.Parent=parent end
  clone.Parent=folder
  -- Moving collider skins must continue following the original mover at runtime.
  if not p.Anchored then table.insert(cloneJoints,{original=p,visual=clone}) end
  local reference=Instance.new("ObjectValue");reference.Name="ZF1VisualReference";reference.Value=clone;reference.Parent=p
  p:SetAttribute("ZF1OriginalTransparency",p.Transparency)
  p.Transparency=1
  for _,d in p:GetChildren() do
   if d:IsA("Decal") or d:IsA("Texture") then d:SetAttribute("ZF1OriginalTransparency",d.Transparency);d.Transparency=1
   elseif d:IsA("SurfaceGui") then d:SetAttribute("ZF1OriginalEnabled",d.Enabled);d.Enabled=false end
  end
  r.part=clone
  table.insert(report.colliderCopies,{name=r.name,hole=r.hole,category="collider-preservation",change="Original collider hidden; untagged noncolliding appearance copy; physical pose/size/properties unchanged"})
  return clone
 end
 for _,p in descendants() do
  if p:IsA("BasePart") and p.CanCollide then
   table.insert(originals,{p=p,cf=p.CFrame,size=p.Size,collide=p.CanCollide,query=p.CanQuery,touch=p.CanTouch,group=p.CollisionGroup,physical=p.CustomPhysicalProperties})
  end
  if p:IsA("BasePart") and (p.Transparency<1 or decorated(p)) then
   -- Reapplying starts from the same build baseline rather than accumulating offsets.
   if p:GetAttribute("ZF1BaseCF") then p.CFrame=p:GetAttribute("ZF1BaseCF");p.Size=p:GetAttribute("ZF1BaseSize") end
   table.insert(records,{part=p,name=p:GetAttribute("ZF1SourcePath") or name(p),hole=hole(p),box=exactBox(p),decorated=decorated(p),key=key(p),protectedFelt=(p:GetAttribute("ZF1SourcePath") or name(p)):match("%.Felt$")~=nil,protectedCarrier=topCarrier(p) and not p.CanCollide and (p:GetAttribute("ZF1SourcePath") or name(p)):match("%.Felt$")==nil})
  end
 end
 -- Narrow imported-art repair: only known boardwalk/landing/lift deck models.
 -- Move every material submesh together; never jitter a material component or
 -- touch a collidable/unanchored/jointed assembly to satisfy a mesh-bbox scan.
 local deckNames={walk_boardwalk_6x12__Timber=true,landing_6x4__SandBlock=true,lift_cage__Timber=true}
 local checkedModels={}
 for _,r in records do
  local trigger=r.part
  if not trigger:IsA("MeshPart") or not deckNames[trigger.Name] then continue end
  local model=trigger:FindFirstAncestorOfClass("Model")
  if not model or model==course or checkedModels[model] then continue end
  checkedModels[model]=true
  local members={}
  local safe=true
  for _,d in model:GetDescendants() do
   if d:IsA("BasePart") then
    table.insert(members,d)
    if d.CanCollide or not d.Anchored or jointedParts[d] then safe=false end
   elseif d:IsA("Constraint") or d:IsA("JointInstance") then safe=false end
  end
  if not safe then
   table.insert(report.exclusions,{name=name(model),hole=r.hole,category="mesh-terrain-assembly",change="Skipped imported deck: collidable, unanchored or jointed assembly"})
   continue
  end
  -- Dedicated originals survive the generic per-part baseline reset and prevent
  -- a second Apply from adding another lift to the model.
  for _,d in members do
   if not d:GetAttribute("ZF1MeshTerrainBaseCF") then
    d:SetAttribute("ZF1MeshTerrainBaseCF",d:GetAttribute("ZF1BaseCF") or d.CFrame)
    d:SetAttribute("ZF1MeshTerrainBaseSize",d:GetAttribute("ZF1BaseSize") or d.Size)
   end
   d.CFrame=d:GetAttribute("ZF1MeshTerrainBaseCF")
   d.Size=d:GetAttribute("ZF1MeshTerrainBaseSize")
  end
  local up=trigger.CFrame.UpVector
  local top=trigger.Position+up*trigger.Size.Y/2
  local hit=up.Y>0.95 and workspace:Raycast(top+Vector3.new(0,0.15,0),Vector3.new(0,-0.3,0),terrainParams) or nil
  local delta=hit and (hit.Position-top):Dot(up) or math.huge
  local lift=math.abs(delta)<=0.02 and GAP+math.max(0,delta)+0.001 or 0
  for _,d in members do
   d.CFrame=d:GetAttribute("ZF1MeshTerrainBaseCF")+up*lift
   -- The remaining visual pass starts from this complete model offset.
   d:SetAttribute("ZF1BaseCF",d.CFrame)
   d:SetAttribute("ZF1BaseSize",d.Size)
  end
  if lift>0 then
   table.insert(report.fixes,{name=name(model),hole=r.hole,category="imported-deck-terrain",change="Lifted complete noncolliding static imported model above terrain; material alignment preserved",lift=lift,trigger=name(trigger),partCount=#members})
  end
 end
 table.sort(records,function(a,b)
  -- Geometry first; decorative layers conform to it. Stable transform breaks repeated names.
  local ap=a.protectedFelt and -2 or (a.protectedCarrier and -1 or (a.name:find(".Geometry.",1,true) and 0 or 1))
  local bp=b.protectedFelt and -2 or (b.protectedCarrier and -1 or (b.name:find(".Geometry.",1,true) and 0 or 1))
  if a.protectedFelt and b.protectedFelt then
   local aa=a.part.Size.X*a.part.Size.Z
   local ba=b.part.Size.X*b.part.Size.Z
   if math.abs(aa-ba)>0.0001 then return aa>ba end
  end
  return ap==bp and a.key<b.key or ap<bp
 end)
 for _,r in records do
  local p=r.part
  local sz=dimensions(p.Size)
  local changed=false
  for i=1,3 do if sz[i]<MINIMUM-0.00001 then sz[i]=MINIMUM;changed=true end end
  if changed then
   local old=p.Size;p=visual(r)
   if not p:GetAttribute("ZF1BaseCF") then p:SetAttribute("ZF1BaseCF",p.CFrame);p:SetAttribute("ZF1BaseSize",p.Size) end
   p.Size=vector(sz)
   -- Thicken downwards to retain the rendered top height, particularly felt/cup plates.
   p.CFrame=p.CFrame*CFrame.new(0,-(p.Size.Y-old.Y)/2,0)
   table.insert(report.fixes,{name=r.name,hole=r.hole,category="minimum-thickness",change="Visual dimensions raised to >=0.2; local top held fixed",before={old.X,old.Y,old.Z},after=sz})
  end
  if r.protectedFelt then
   p=visual(r)
   if not p:GetAttribute("ZF1BaseCF") then p:SetAttribute("ZF1BaseCF",p.CFrame);p:SetAttribute("ZF1BaseSize",p.Size) end
   local baseCF=p:GetAttribute("ZF1BaseCF")
   local baseSize=p:GetAttribute("ZF1BaseSize")
   local up=baseCF.UpVector
   local originalTop=baseCF.Position+up*baseSize.Y/2
   -- Render putting surfaces at the physical roll plane. Raising them by the
   -- ball radius hides half the ball. Terrain intersections remain audit findings;
   -- this pass cannot alter terrain physics or silently lift the rendered green.
   local lift=0
   local thickness=math.max(baseSize.Y,MINIMUM)
   p.Size=Vector3.new(math.max(MINIMUM,baseSize.X-2*GAP),thickness,math.max(MINIMUM,baseSize.Z-2*GAP))
   p.CFrame=baseCF*CFrame.new(0,(baseSize.Y-thickness)/2+lift,0)
   r.protectedTop=originalTop+up*lift
   r.protectedUp=up
   table.insert(report.protectedFelt,{name=r.name,hole=r.hole,lift=lift,insetEachEdge=GAP})
   table.insert(report.fixes,{name=r.name,hole=r.hole,category="protected-felt-skin",change="Visual top retained at original collider plane; X/Z edges inset0.08; physical collider unchanged",lift=lift,insetEachEdge=GAP})
  end
 end
 -- Place active Top decals above the FINAL protected felt plane, not the old
 -- collider plane. Preserve CFrame rotation/UV direction; only translate up.
 for _,r in records do
  if not r.protectedCarrier then continue end
  local p=r.part
  if not p:GetAttribute("ZF1BaseCF") then p:SetAttribute("ZF1BaseCF",p.CFrame);p:SetAttribute("ZF1BaseSize",p.Size) end
  local top=p.Position+p.CFrame.UpVector*p.Size.Y/2
  local up=p.CFrame.UpVector
  local lift=0
  local carrierFace=nil
  for _,f in faces(p) do if f.axis==2 and f.sign==1 then carrierFace=f end end
  if carrierFace then
   for _,surface in records do
    if not surface.protectedFelt or surface.hole~=r.hole then continue end
    local felt=surface.part
    local feltFace=nil
    for _,f in faces(felt) do if f.axis==2 and f.sign==1 then feltFace=f end end
    if feltFace and up:Dot(feltFace.n)>0.7 and projectedOverlap(carrierFace,feltFace,true) then
     local delta=(feltFace.c-top):Dot(up)
     if math.abs(delta)<2 then lift=math.max(lift,delta+GAP+0.001) end
    end
   end
  end
  if lift>0 then
   p.CFrame+=up*lift
   table.insert(report.fixes,{name=r.name,hole=r.hole,category="decal-over-felt",change="Raised Top decal carrier >=0.08 above protected felt visual, retaining image orientation",lift=lift})
  end
  r.carrierMinimumTop=p.Position+up*p.Size.Y/2
  r.carrierUp=up
 end
 local exclusionKeys={}
 for i,r in records do
  local p=r.part
  local startCF,startSize=p.CFrame,p.Size
  local adjustments=0
  if r.box then
   for iteration=1,24 do
    local conflict=nil
    local pf=faces(p)
    for j=1,i-1 do
     local other=records[j];local q=other.part
     if other.box and (p.Position-q.Position).Magnitude<(p.Size.Magnitude+q.Size.Magnitude)/2+GAP then
      for _,a in pf do for _,b in other.finalFaces do
       if overlaps(a,b) then
        if a.n:Dot(b.n)<0 then
         -- Opposing faces bound adjacent solid volumes. These are buried interfaces,
         -- not two exposed surfaces rendering over one another.
         local k=tostring(i)..":"..tostring(j)..":"..a.axis..":"..a.sign
         if not exclusionKeys[k] then
          exclusionKeys[k]=true
          table.insert(report.exclusions,{name=r.name,other=other.name,hole=r.hole,category="internal-opposing-face",change="Retained connected solid interface; opposing normals, no shared exterior surface"})
         end
        else conflict={face=a,other=b};break end
       end
      end if conflict then break end end
     end
     if conflict then break end
    end
    if not conflict then break end
    p=visual(r)
    if not p:GetAttribute("ZF1BaseCF") then p:SetAttribute("ZF1BaseCF",p.CFrame);p:SetAttribute("ZF1BaseSize",p.Size) end
    local axis=conflict.face.axis
    if r.protectedFelt and axis==2 then
     -- Narrow cup/lock seam strips can already be below the minimum visual width.
     -- Trim the cheaper horizontal edge where possible; otherwise move that small
     -- visual strip laterally. Large playing rectangles are processed first.
     local b=conflict.other
     local a=conflict.face
     local contained=math.abs((a.c-b.c):Dot(a.n))<0.002
     for _,axisInfo in {{b.u,b.hu},{b.v,b.hv}} do
      local tangent,half=axisInfo[1],axisInfo[2]
      local extent=math.abs(a.u:Dot(tangent))*a.hu+math.abs(a.v:Dot(tangent))*a.hv
      if math.abs((a.c-b.c):Dot(tangent))+extent>half+0.00001 then contained=false end
     end
     if contained then
      -- A fully covered same-plane felt skin is redundant appearance, not a
      -- placeholder. Keep its original collider and instance; hide visual only.
      p.Transparency=1
      for _,d in p:GetChildren() do
       if d:IsA("Decal") or d:IsA("Texture") then d.Transparency=1
       elseif d:IsA("SurfaceGui") then d.Enabled=false end
      end
      p:SetAttribute("ZF1RedundantFeltSkin",true)
      r.disabled=true
      table.insert(report.fixes,{name=r.name,hole=r.hole,category="contained-felt-skin",change="Hidden redundant noncolliding felt appearance fully covered by earlier felt; collider and instance retained"})
      break
     end
     local candidates={}
     for _,k in {1,3} do
      local direction=k==1 and p.CFrame.RightVector or p.CFrame.ZVector
      local size=dimensions(p.Size)
      local center=p.Position:Dot(direction)
      local radius=size[k]/2
      local bc=b.c:Dot(direction)
      local br=math.abs(b.u:Dot(direction))*b.hu+math.abs(b.v:Dot(direction))*b.hv
      for _,sign in {-1,1} do
       local amount=sign==1 and (bc+br+GAP-(center-radius)) or ((center+radius)-(bc-br-GAP))
       if amount>0 then
        if size[k]-amount>=MINIMUM then
         table.insert(candidates,{k=k,direction=direction,sign=sign,amount=amount,trim=true,cost=amount})
        else
         table.insert(candidates,{k=k,direction=direction,sign=sign,amount=amount,trim=false,cost=amount*2})
        end
       end
      end
     end
     table.sort(candidates,function(a,b)return a.cost<b.cost end)
     local best=candidates[1]
     if not best then
      table.insert(report.unresolved,{name=r.name,hole=r.hole,category="protected-felt-height",change="No safe lateral solution for protected felt"})
      break
     end
     if best.trim then
      local size=dimensions(p.Size);size[best.k]-=best.amount;p.Size=vector(size)
      p.CFrame+=best.direction*best.sign*best.amount/2
     else
      -- Minimum-width strips cannot keep trimming. Solve horizontal exclusion
      -- intervals against ALL earlier felt faces, rather than ping-ponging
      -- between the two neighbors on either side of a narrow seam.
      local choices={}
      for _,k in {1,3} do
       local direction=k==1 and p.CFrame.RightVector or p.CFrame.ZVector
       local tangent=k==1 and p.CFrame.ZVector or p.CFrame.RightVector
       local size=dimensions(p.Size)
       local half=size[k]/2
       local tangentHalf=size[k==1 and 3 or 1]/2
       local center=p.Position:Dot(direction)
       local crossCenter=p.Position:Dot(tangent)
       local intervals={}
       for _,af in faces(p) do
        if af.axis~=2 then continue end
        for j=1,i-1 do
         for _,bf in records[j].finalFaces do
          if af.n:Dot(bf.n)<0.999999 or math.abs((bf.c-af.c):Dot(af.n))>=GAP then continue end
          local bc=bf.c:Dot(tangent)
          local br=math.abs(bf.u:Dot(tangent))*bf.hu+math.abs(bf.v:Dot(tangent))*bf.hv
          if math.min(crossCenter+tangentHalf,bc+br)-math.max(crossCenter-tangentHalf,bc-br)<=EPS then continue end
          local middle=bf.c:Dot(direction)-center
          local extent=math.abs(bf.u:Dot(direction))*bf.hu+math.abs(bf.v:Dot(direction))*bf.hv
          table.insert(intervals,{middle-extent-half-GAP,middle+extent+half+GAP})
         end
        end
       end
       table.sort(intervals,function(a,b)return a[1]<b[1] end)
       local merged={}
       for _,interval in intervals do
        local last=merged[#merged]
        if last and interval[1]<=last[2] then last[2]=math.max(last[2],interval[2])
        else table.insert(merged,{interval[1],interval[2]}) end
       end
       for _,interval in merged do
        if interval[1]<=0 and interval[2]>=0 then
         local shift=math.abs(interval[1])<=math.abs(interval[2]) and interval[1]-0.001 or interval[2]+0.001
         table.insert(choices,{direction=direction,shift=shift})
         break
        end
       end
      end
      table.sort(choices,function(a,b)return math.abs(a.shift)<math.abs(b.shift) end)
      if choices[1] then p.CFrame+=choices[1].direction*choices[1].shift
      else p.CFrame+=best.direction*best.sign*best.amount end
     end
     adjustments+=1
     if iteration==24 then table.insert(report.unresolved,{name=r.name,hole=r.hole,category="lateral-iteration-limit",change="Protected felt needs explicit source trim"}) end
     continue
    end
    local axes={p.CFrame.RightVector,p.CFrame.UpVector,p.CFrame.ZVector}
    local direction=axes[axis]
    -- Solve the entire forbidden-plane interval union for BOTH faces on this
    -- axis. Repeated per-face nudges can oscillate between the top and bottom
    -- of a minimum-thickness plate; a global interval solve cannot do that.
    local intervals={}
    for _,a in faces(p) do
     if a.axis~=axis then continue end
     for j=1,i-1 do
      local other=records[j]
      if not other.box then continue end
      for _,b in other.finalFaces do
       if a.n:Dot(b.n)>0.999999 and projectedOverlap(a,b) then
        local center=(b.c-a.c):Dot(direction)
        table.insert(intervals,{center-GAP-0.001,center+GAP+0.001})
       end
      end
     end
    end
    table.sort(intervals,function(a,b)return a[1]<b[1] end)
    local merged={}
    for _,interval in intervals do
     local last=merged[#merged]
     if last and interval[1]<=last[2] then last[2]=math.max(last[2],interval[2])
     else table.insert(merged,{interval[1],interval[2]}) end
    end
    local translation=0
    for _,interval in merged do
     if interval[1]<=0 and interval[2]>=0 then
      if r.protectedCarrier and axis==2 then translation=interval[2]+0.001
      else translation=math.abs(interval[1])<=math.abs(interval[2]) and interval[1]-0.001 or interval[2]+0.001 end
      break
     end
    end
    p.CFrame+=direction*translation

    adjustments+=1
    if iteration==24 then table.insert(report.unresolved,{name=r.name,hole=r.hole,category="iteration-limit",change="Needs exposed-face review; stopped after 24 local visual adjustments"}) end
   end
  else
   table.insert(report.exclusions,{name=r.name,hole=r.hole,category="non-box-geometry",change="Mesh/CSG/sphere bounds are not rendered faces; retained art geometry, separately audited by zscan"})
  end
  if adjustments>0 then
   local delta=p.Position-startCF.Position
   table.insert(report.fixes,{name=r.name,hole=r.hole,category="parallel-exterior-faces",change="Offset visual faces >=0.08 using a union of forbidden plane intervals; no minimum-thickness oscillation",adjustments=adjustments,translation={delta.X,delta.Y,delta.Z},sizeBefore={startSize.X,startSize.Y,startSize.Z},sizeAfter={p.Size.X,p.Size.Y,p.Size.Z}})
  end
  if math.min(p.Size.X,p.Size.Y,p.Size.Z)<MINIMUM-0.00001 then table.insert(report.thinAfter,r.name) end
  if r.protectedFelt then
   local top=p.Position+p.CFrame.UpVector*p.Size.Y/2
   if math.abs((top-r.protectedTop):Dot(r.protectedUp))>=0.002 then table.insert(report.invariantFailures,"ZF1 lowered/raised protected felt plane: "..r.name) end
  end
  if r.protectedCarrier then
   local top=p.Position+p.CFrame.UpVector*p.Size.Y/2
   if (top-r.carrierMinimumTop):Dot(r.carrierUp)<=-0.002 then table.insert(report.invariantFailures,"ZF1 lowered decal carrier below felt: "..r.name) end
  end
  r.finalFaces=r.disabled and {} or faces(p)
  if i%100==0 then task.wait() end
 end
 -- WeldConstraint caches its relative pose when endpoints are assigned. Legacy
 -- Weld/Motor6D store that pose explicitly; adjust C0 only for edited endpoints.
 for _,entry in detachedJoints do
  local j=entry.joint
  if j.Parent and entry.p0.Parent and entry.p1.Parent then
   if j:IsA("JointInstance") and (entry.p0.CFrame~=entry.cf0 or entry.p1.CFrame~=entry.cf1) then
    local offset=entry.p0.CFrame:ToObjectSpace(entry.p1.CFrame*entry.c1)
    if j:IsA("Motor6D") then offset=offset*j.Transform:Inverse() end
    j.C0=offset
   end
   j.Part0=entry.p0;j.Part1=entry.p1
  end
 end
 for _,entry in cloneJoints do
  local weld=Instance.new("WeldConstraint")
  weld.Name="ZF1VisualFollow";weld.Part0=entry.original;weld.Part1=entry.visual;weld.Parent=entry.visual
 end
 report.reconnectedJointCount=#detachedJoints+#cloneJoints
 assert(#report.invariantFailures==0,table.concat(report.invariantFailures,"; "))
 for _,o in originals do
  local p=o.p
  assert(p.CFrame==o.cf and p.Size==o.size and p.CanCollide==o.collide and p.CanQuery==o.query and p.CanTouch==o.touch and p.CollisionGroup==o.group and p.CustomPhysicalProperties==o.physical,"ZF1 changed collider: "..name(p))
 end
 report.colliderInvariantCount=#originals
 report.changedCount=#report.fixes
 report.visibleParts=#records
 course:SetAttribute("ZF1VisualGap",GAP)
 course:SetAttribute("ZF1MinimumVisualThickness",MINIMUM)
 return report
end
return Separation
