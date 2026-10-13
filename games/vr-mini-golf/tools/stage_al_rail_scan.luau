local function name(p) return p:GetFullName()..(p:GetAttribute("WallId") and "["..p:GetAttribute("WallId").."]" or p:GetAttribute("PieceId") and "["..p:GetAttribute("PieceId").."]" or "") end
_G.RailAllPairs={}
for n=1,18 do local parts={} for _,p in workspace.CourseSugarloaf["Hole"..n].Rails:GetChildren() do if p:IsA("Part") and (p.Name:match("^Rail_") or p.Name:match("^RailCap_")) then table.insert(parts,p) end end
for i,a in parts do for j=i+1,#parts do local b=parts[j] if (a.Position-b.Position).Magnitude<(a.Size.Magnitude+b.Size.Magnitude)/2+0.02 then table.insert(_G.RailAllPairs,{hole=n,a=name(a),b=name(b)}) end end end
end
local C=workspace.CourseSugarloaf
local lookup={}
local function name(p) return p:GetFullName()..(p:GetAttribute("WallId") and "["..p:GetAttribute("WallId").."]" or p:GetAttribute("PieceId") and "["..p:GetAttribute("PieceId").."]" or "") end
for _,p in C:GetDescendants() do if p:IsA("Part") and p.Shape==Enum.PartType.Block and p.Transparency<0.99 then lookup[name(p)]=p end end
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
_G.RailAllFaces={done=false,rows={}}
task.spawn(function()
 for i,r in _G.RailAllPairs do
  local a,b=lookup[r.a],lookup[r.b]
  if a and b then
   for _,f in faces(a) do for _,g in faces(b) do
    local gap=math.abs((g.c-f.c):Dot(f.n))
    if f.n:Dot(g.n)>0.99999 and gap<0.005 and f.n.Y>0.5 then local ar=area(f,g) if ar>0.0001 then table.insert(_G.RailAllFaces.rows,{hole=r.hole,a=r.a,b=r.b,area=ar,gap=gap,normal={f.n.X,f.n.Y,f.n.Z},position={f.c.X,f.c.Y,f.c.Z}}) end end
   end end
  end
  if i%50==0 then task.wait() end
 end
 table.sort(_G.RailAllFaces.rows,function(a,b)return a.area>b.area end)
 _G.RailAllFaces.done=true
end)
return "Checking same-facing coplanar surface areas"
