-- Stage al, LOCAL friction-test build: deterministic visual rail-top separation.
-- CourseBuilder creates Rail_/RailCap_ with vis(); Wall colliders remain untouched.
-- Coplanarity and polygon clipping below deliberately match al-inputs/scan-all-rail-tops.luau.
local RailTops = {}
local STEP = 0.02
local function name(p)
 return p:GetFullName() .. (p:GetAttribute("WallId") and "["..p:GetAttribute("WallId").."]" or p:GetAttribute("PieceId") and "["..p:GetAttribute("PieceId").."]" or "")
end
local function faces(p)
 local axes={p.CFrame.RightVector,p.CFrame.UpVector,p.CFrame.ZVector}
 local half={p.Size.X/2,p.Size.Y/2,p.Size.Z/2} local out={}
 for k=1,3 do local u=k%3+1 local v=(k+1)%3+1
  for _,sign in {-1,1} do table.insert(out,{n=axes[k]*sign,c=p.Position+axes[k]*half[k]*sign,u=axes[u],v=axes[v],w=half[u],h=half[v]}) end
 end return out
end
local function area(a,b)
 local poly={}
 for _,q in {{-1,-1},{1,-1},{1,1},{-1,1}} do local d=b.c+b.u*b.w*q[1]+b.v*b.h*q[2]-a.c table.insert(poly,Vector2.new(d:Dot(a.u),d:Dot(a.v))) end
 for _,edge in {{1,a.w,1},{1,-a.w,-1},{2,a.h,1},{2,-a.h,-1}} do
  local clipped={} local function value(p)return edge[1]==1 and p.X or p.Y end
  for i,p in poly do local q=poly[i%#poly+1] local pv,qv=value(p),value(q) local pin=(pv-edge[2])*edge[3]<=0 local qin=(qv-edge[2])*edge[3]<=0
   if pin then table.insert(clipped,p) end
   if pin~=qin then local t=(edge[2]-pv)/(qv-pv) table.insert(clipped,p:Lerp(q,t)) end
  end poly=clipped if #poly<3 then return 0 end
 end
 local sum=0 for i,p in poly do local q=poly[i%#poly+1] sum+=p.X*q.Y-p.Y*q.X end return math.abs(sum)/2
end
local function overlap(a,b)
 if (a.Position-b.Position).Magnitude >= (a.Size.Magnitude+b.Size.Magnitude)/2+0.02 then return nil end
 for _,f in faces(a) do for _,g in faces(b) do
  local gap=math.abs((g.c-f.c):Dot(f.n))
  if f.n:Dot(g.n)>0.99999 and gap<0.005 and f.n.Y>0.5 then
   local ar=area(f,g)
   if ar>0.0001 then return {area=ar,gap=gap,normal={f.n.X,f.n.Y,f.n.Z},position={f.c.X,f.c.Y,f.c.Z}} end
  end
 end end
 return nil
end
local function partsFor(hole)
 local parts={} local rails=hole and hole:FindFirstChild("Rails")
 for _,p in rails and rails:GetChildren() or {} do
  if p:IsA("Part") and p.Shape==Enum.PartType.Block and p.Transparency<0.99 and (p.Name:match("^Rail_") or p.Name:match("^RailCap_")) then table.insert(parts,p) end
 end
 return parts
end
function RailTops.Scan(course)
 local rows={}
 for n=1,18 do
  local parts=partsFor(course:FindFirstChild("Hole"..n))
  for i,a in parts do for j=i+1,#parts do
   local b=parts[j] local hit=overlap(a,b)
   if hit then hit.hole=n;hit.a=name(a);hit.b=name(b);table.insert(rows,hit) end
  end end
 end
 table.sort(rows,function(a,b)return a.area>b.area end)
 return rows
end
local function stableKey(p)
 local cf=p:GetAttribute("StageAlRailBaseCF") or p.CFrame
 local size=p:GetAttribute("StageAlRailBaseSize") or p.Size
 local values={cf:GetComponents()}
 table.insert(values,size.X);table.insert(values,size.Y);table.insert(values,size.Z)
 local key=name(p)
 for _,v in values do key..=string.format("|%.9f",v) end
 return key
end
local function setLevel(p,level)
 local cf=p:GetAttribute("StageAlRailBaseCF") local size=p:GetAttribute("StageAlRailBaseSize")
 local lift=level*STEP
 if p.Name:match("^RailCap_") then
  p.Size=size;p.CFrame=cf*CFrame.new(0,lift,0)
 else
  -- Extend only the visual body's top; its lower face remains at its original pose.
  -- Local up preserves sloping top orientation and provides exact .02 normal spacing.
  p.Size=size+Vector3.new(0,lift,0);p.CFrame=cf*CFrame.new(0,lift/2,0)
 end
 p:SetAttribute("StageAlRailTopLevel",level)
 p:SetAttribute("StageAlRailTopLift",lift)
end
function RailTops.Apply(course)
 assert(course,"CourseSugarloaf required")
 local report={step=STEP,changed={},physicalVisualCopies={},maxLevel=0,remaining={}}
 for n=1,18 do
  local parts=partsFor(course:FindFirstChild("Hole"..n))
  for i,p in parts do
   if p.CanCollide then
    -- Defensive legacy fallback: duplicate appearance, hide original collider, retain
    -- all original physical dimensions/pose/properties and collision/query flags.
    local visual=p:Clone()
    for _,child in visual:GetChildren() do child:Destroy() end
    visual.CanCollide=false;visual.CanQuery=false;visual.CanTouch=false
    visual:SetAttribute("StageAlRailVisualCopy",true);visual.Parent=p.Parent
    p.Transparency=1;p:SetAttribute("StageAlRailColliderHidden",true)
    table.insert(report.physicalVisualCopies,name(p));parts[i]=visual;p=visual
   end
   if not p:GetAttribute("StageAlRailBaseCF") then
    p:SetAttribute("StageAlRailBaseCF",p.CFrame);p:SetAttribute("StageAlRailBaseSize",p.Size)
   end
   p.CanQuery=false;p.CanTouch=false;p:SetAttribute("VisualQueryDisabled",true)
   setLevel(p,0)
  end
  table.sort(parts,function(a,b)return stableKey(a)<stableKey(b) end)
  for i,p in parts do
   -- Greedy graph coloring with actual transformed planes: unlike a fixed 2-color
   -- graph this also handles triangles and conflicts newly created across cap heights.
   local level=0
   while true do
    setLevel(p,level)
    local conflict=false
    for j=1,i-1 do if overlap(p,parts[j]) then conflict=true;break end end
    if not conflict then break end
    level+=1
    assert(level<=#parts*3,"Rail top separation did not converge: "..name(p))
   end
   report.maxLevel=math.max(report.maxLevel,level)
   if level>0 then table.insert(report.changed,{hole=n,part=name(p),level=level,lift=level*STEP,operation=p.Name:match("^RailCap_") and "lift visual cap" or "extend visual top; bottom fixed"}) end
  end
 end
 report.remaining=RailTops.Scan(course)
 report.remainingCount=#report.remaining
 report.changedCount=#report.changed
 course:SetAttribute("StageAlRailTopPairs",report.remainingCount)
 course:SetAttribute("StageAlRailTopMaxLift",report.maxLevel*STEP)
 return report
end
return RailTops
