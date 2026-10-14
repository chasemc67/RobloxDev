-- Stage zf1: read-only geometry audit. Run in Studio edit mode with run_code.
-- Retrieval: return _G.ZF1ScanJSON:sub(first, last); JSON is intentionally not printed.
-- Bounding-box faces are conservative for meshes, unions, wedges and curved parts.
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local EPS, PARALLEL, AREA_EPS = 0.02, 0.999999, 0.00001
local report = {
    schema = 1, placeId = game.PlaceId, placeVersion = game.PlaceVersion,
    role = workspace:GetAttribute("PlaceRole"), timestamp = DateTime.now():ToIsoDate(),
    toleranceStuds = EPS, counts = {}, hits = {}, modelBotMeshHits = {},
    placeholders = {}, animationSources = {}, terrainHits = {},
    limitations = {
        "MeshPart/UnionOperation/wedge/sphere/cylinder faces use OBBs; mesh-bbox and shape-bbox hits require visual review.",
        "Transparency animation source matches are conservative source candidates; arbitrary dynamic aliases cannot be resolved statically.",
        "Visible means Transparency < 1; no camera-occlusion or interior-face rejection is applied.",
        "Terrain sampled by downward terrain-only rays at face center and corners, not exact voxel boundary reconstruction.",
        "Category counts overlap: a placeholder or decorated face pair also appears in category 1. Total is the sum of category hit counts.",
    },
}
local function vec(v) return {v.X, v.Y, v.Z} end
local function holeOf(p)
    local n = p
    while n and n ~= workspace do
        local h = n:GetAttribute("HoleIndex") or n:GetAttribute("HoleId") or n:GetAttribute("Hole")
        if h ~= nil then return tostring(h) end
        local found = n.Name:match("^[Hh]ole[_ ]?(%d+)") or n.Name:match("^[Hh](%d+)[_ %-]") or n.Name:match("^[Hh](%d+)$")
        if found then return found end
        n = n.Parent
    end
    return "unknown"
end
local function placeholderOf(p)
    local n = p
    while n and n ~= workspace do
        local low = string.lower(n.Name)
        if low:find("placeholder", 1, true) or n:GetAttribute("Placeholder") == true
            or n:GetAttribute("IsPlaceholder") == true then return n:GetFullName() end
        n = n.Parent
    end
    return nil
end
local function isCharacter(p)
    local n = p.Parent
    while n and n ~= workspace do
        if n:IsA("Model") and (Players:GetPlayerFromCharacter(n) or n:FindFirstChildOfClass("Humanoid")) then return true end
        n = n.Parent
    end
    return false
end
local placeholderSet = {}
local placeholderParts, hiddenPlaceholderParts = {}, {}
local function describe(p)
    local ph = placeholderOf(p)
    local mesh = p:IsA("MeshPart") or p:FindFirstChildOfClass("SpecialMesh") ~= nil
    local desc = {
        name = p:GetFullName(), hole = holeOf(p), class = p.ClassName,
        position = vec(p.Position), size = vec(p.Size), cframe = {p.CFrame:GetComponents()},
        transparency = p.Transparency, localTransparencyModifier = p.LocalTransparencyModifier,
        material = p.Material.Name, canCollide = p.CanCollide,
        exactBox = p:IsA("Part") and p.Shape == Enum.PartType.Block and not mesh,
        shape = p:IsA("Part") and p.Shape.Name or nil,
        placeholder = ph, mesh = mesh,
        faceGeometry = mesh and "mesh-bbox" or (p:IsA("UnionOperation") and "union-bbox" or "part-bbox"),
    }
    if p:IsA("MeshPart") then desc.meshId = p.MeshId end
    return desc
end
local normals = {Enum.NormalId.Right, Enum.NormalId.Left, Enum.NormalId.Top, Enum.NormalId.Bottom, Enum.NormalId.Back, Enum.NormalId.Front}
local function makeRecord(p)
    local axes = {p.CFrame.RightVector, p.CFrame.UpVector, -p.CFrame.LookVector}
    local half = {p.Size.X / 2, p.Size.Y / 2, p.Size.Z / 2}
    local extent = Vector3.new(0,0,0)
    for i = 1,3 do extent += Vector3.new(math.abs(axes[i].X), math.abs(axes[i].Y), math.abs(axes[i].Z)) * half[i] end
    local r = {part = p, desc = describe(p), axes = axes, half = half, center = p.Position,
        min = p.Position - extent, max = p.Position + extent, faces = {}, visible = p.Transparency < 1}
    for i = 1,3 do
        local u, v = i % 3 + 1, (i + 1) % 3 + 1
        for _, sign in ipairs({1, -1}) do
            local f = {normal = axes[i] * sign, center = p.Position + axes[i] * half[i] * sign,
                u = axes[u], v = axes[v], hu = half[u], hv = half[v], id = normals[(i-1)*2 + (sign == 1 and 1 or 2)]}
            f.corners = {}
            for _, su in ipairs({-1,1}) do for _, sv in ipairs({-1,1}) do
                table.insert(f.corners, f.center + f.u * f.hu * su + f.v * f.hv * sv)
            end end
            table.insert(r.faces, f)
        end
    end
    return r
end
local function faceOverlap(a,b)
    if math.abs(a.normal:Dot(b.normal)) < PARALLEL then return false end
    local distance = math.abs((b.center-a.center):Dot(a.normal))
    if distance > EPS then return false end
    local minOverlap = math.huge
    for _, axis in ipairs({a.u, a.v, b.u, b.v}) do
        local ac, bc = a.center:Dot(axis), b.center:Dot(axis)
        local ar = math.abs(a.u:Dot(axis))*a.hu + math.abs(a.v:Dot(axis))*a.hv
        local br = math.abs(b.u:Dot(axis))*b.hu + math.abs(b.v:Dot(axis))*b.hv
        local overlap = math.min(ac+ar,bc+br) - math.max(ac-ar,bc-br)
        if overlap <= AREA_EPS then return false end
        minOverlap = math.min(minOverlap, overlap)
    end
    return true, distance, minOverlap
end
local function obbOverlap(a,b)
    local axes = {a.axes[1],a.axes[2],a.axes[3],b.axes[1],b.axes[2],b.axes[3]}
    for _, x in ipairs(a.axes) do for _, y in ipairs(b.axes) do
        local z = x:Cross(y)
        if z.Magnitude > 0.000001 then table.insert(axes,z.Unit) end
    end end
    for _, axis in ipairs(axes) do
        local ar, br = 0,0
        for i = 1,3 do ar += math.abs(a.axes[i]:Dot(axis))*a.half[i]; br += math.abs(b.axes[i]:Dot(axis))*b.half[i] end
        if ar+br-math.abs((a.center-b.center):Dot(axis)) <= AREA_EPS then return false end
    end
    return true
end
local categoryNames = {"coplanarFaces", "decoratedCoincidentFaces", "placeholderCoplanarFaces", "transparencyFlicker"}
for _, name in ipairs(categoryNames) do report.hits[name] = {}; report.counts[name] = 0 end
local function planar(d, face)
    return d.exactBox or (d.shape == "Cylinder" and (face == "Left" or face == "Right"))
end
local function add(category, hit)
    if hit.faceA then
        if not planar(hit.a,hit.faceA) or not planar(hit.b,hit.faceB) then
            hit.reviewClass = "non-planar-or-mesh-bbox-candidate"
        elseif hit.opposingNormals then
            hit.reviewClass = "opposing-interface-review"
        else hit.reviewClass = "exposed-planar-candidate" end
    end
    local bucket = report.hits[category]
    table.insert(bucket,hit)
    report.counts[category] += 1
    if (hit.a and hit.a.mesh) or (hit.b and hit.b.mesh) then
        table.insert(report.modelBotMeshHits, {category = category, hitIndex = #bucket, hit = hit,
            attribution = "Imported mesh candidate; mesh asset ID/name retained for 3D Model Bot source attribution."})
    end
end
local records, byPart = {}, {}
local all = workspace:GetDescendants()
for index, p in ipairs(all) do
    if p:IsA("BasePart") and not p:IsA("Terrain") and not isCharacter(p) then
        local ph = placeholderOf(p)
        if ph then
            placeholderSet[ph] = true
            if p.Transparency < 1 then table.insert(placeholderParts, p:GetFullName())
            else table.insert(hiddenPlaceholderParts, p:GetFullName()) end
        end
        if p.Transparency < 1 or p:FindFirstChildWhichIsA("Decal") or p:FindFirstChildWhichIsA("Texture") or p:FindFirstChildWhichIsA("SurfaceGui") then
            local r = makeRecord(p)
            table.insert(records,r); byPart[p] = r
        end
    end
    if index % 500 == 0 then task.wait() end
end
-- SurfaceGuis may live outside their Adornee. Index active decorated faces globally.
local decorated = {}
for _, obj in ipairs(game:GetDescendants()) do
    local p, active, face
    if obj:IsA("Decal") or obj:IsA("Texture") then p = obj.Parent; active = obj.Transparency < 1; face = obj.Face
    elseif obj:IsA("SurfaceGui") then p = obj.Adornee or obj.Parent; active = obj.Enabled; face = obj.Face end
    if p and p:IsA("BasePart") and p:IsDescendantOf(workspace) and active and not isCharacter(p) then
        if not byPart[p] then local r = makeRecord(p); byPart[p] = r; table.insert(records,r) end
        decorated[p] = decorated[p] or {}
        decorated[p][face] = decorated[p][face] or {}
        table.insert(decorated[p][face], {name=obj:GetFullName(),class=obj.ClassName,face=face.Name,
            alwaysOnTop=obj:IsA("SurfaceGui") and obj.AlwaysOnTop or nil})
    end
end
for ph in pairs(placeholderSet) do table.insert(report.placeholders,ph) end
table.sort(report.placeholders)
report.placeholderContainers = report.placeholders
report.placeholderContainerCount = #report.placeholderContainers
report.placeholders = placeholderParts
report.hiddenPlaceholders = hiddenPlaceholderParts
report.placeholderCount = #placeholderParts
report.hiddenPlaceholderCount = #hiddenPlaceholderParts
report.allPlaceholderPartCount = #placeholderParts + #hiddenPlaceholderParts
table.sort(report.placeholders)
table.sort(report.hiddenPlaceholders)
report.partCount = #records
report.visiblePartCount = 0
for _,r in ipairs(records) do if r.visible then report.visiblePartCount += 1 end end
table.sort(records,function(a,b) return a.min.X < b.min.X end)
local tested = 0
local layerMaterial = {Glass=true, ForceField=true, Neon=true}
for i,a in ipairs(records) do
    for j = i+1,#records do
        local b = records[j]
        if b.min.X > a.max.X+EPS then break end
        if b.min.Y <= a.max.Y+EPS and b.max.Y >= a.min.Y-EPS and b.min.Z <= a.max.Z+EPS and b.max.Z >= a.min.Z-EPS then
            tested += 1
            for _,af in ipairs(a.faces) do for _,bf in ipairs(b.faces) do
                local overlap, distance, minOverlap = faceOverlap(af,bf)
                if overlap then
                    local hit = {a=a.desc,b=b.desc,faceA=af.id.Name,faceB=bf.id.Name,
                        centerA=vec(af.center),centerB=vec(bf.center),normalA=vec(af.normal),normalB=vec(bf.normal),
                        planeDistance=distance,minOverlap=minOverlap,
                        opposingNormals=af.normal:Dot(bf.normal)<0,
                        facingAcrossGap=(bf.center-af.center):Dot(af.normal)>=0}
                    if a.visible and b.visible then
                        add("coplanarFaces",hit)
                        if a.desc.placeholder or b.desc.placeholder then add("placeholderCoplanarFaces",hit) end
                    end
                    local da = decorated[a.part] and decorated[a.part][af.id]
                    local db = decorated[b.part] and decorated[b.part][bf.id]
                    if (da and b.visible) or (db and a.visible) or (da and db) then
                        local dh = table.clone(hit); dh.decorationsA=da; dh.decorationsB=db
                        add("decoratedCoincidentFaces",dh)
                    end
                end
            end end
            if a.visible and b.visible and obbOverlap(a,b) then
                local reasons = {}
                if a.desc.transparency>0 and b.desc.transparency>0 then table.insert(reasons,"overlapping-semitransparent") end
                if layerMaterial[a.desc.material] and layerMaterial[b.desc.material] then table.insert(reasons,"layered-glass-forcefield-neon") end
                if a.part.CFrame == b.part.CFrame and a.part.Size == b.part.Size then
                    table.insert(reasons,"identical-transform-size")
                end
                if #reasons>0 then add("transparencyFlicker",{a=a.desc,b=b.desc,reasons=reasons}) end
            end
            if tested % 300 == 0 then task.wait() end
        end
    end
    if i % 100 == 0 then task.wait() end
end
report.broadphasePairs = tested
-- Script inspection does not execute code or mutate scripts.
for i,obj in ipairs(game:GetDescendants()) do
    if obj:IsA("LuaSourceContainer") then
        local ok,source = pcall(function() return obj.Source end)
        if ok then
            local lines = {}; local lineNo = 0
            for line in (source.."\n"):gmatch("(.-)\n") do
                lineNo += 1
                if line:find("LocalTransparencyModifier",1,true) or line:find("Transparency",1,true) then
                    if not line:match("^%s*%-%-") then table.insert(lines,{line=lineNo,text=line:sub(1,400)}) end
                end
            end
            if #lines>0 then table.insert(report.animationSources,{name=obj:GetFullName(),lines=lines,
                hasTween=source:find("TweenService",1,true)~=nil or source:find(":Tween",1,true)~=nil,
                hasFrameLoop=source:find("RenderStepped",1,true)~=nil or source:find("Heartbeat",1,true)~=nil}) end
        end
    end
    if i % 250 == 0 then task.wait() end
end
for _,r in ipairs(records) do
    if r.visible and r.part.LocalTransparencyModifier ~= 0 then
        add("transparencyFlicker",{a=r.desc,reasons={"nonzero-local-transparency-modifier"}})
    end
end
local terrain = workspace:FindFirstChildOfClass("Terrain")
local terrainSamples = 0
if terrain then
    local params = RaycastParams.new(); params.FilterType=Enum.RaycastFilterType.Include
    params.FilterDescendantsInstances={terrain}; params.IgnoreWater=false
    for i,r in ipairs(records) do
        if r.visible then for _,f in ipairs(r.faces) do
            if f.normal.Y > 0.7 then
                local samples = {f.center}
                for _,c in ipairs(f.corners) do table.insert(samples,c) end
                for _,s in ipairs(samples) do
                    terrainSamples += 1
                    local hit=workspace:Raycast(s+Vector3.new(0,4.05,0),Vector3.new(0,-8.1,0),params)
                    if hit then
                        local d=math.abs((hit.Position-f.center):Dot(f.normal))
                        if d<=EPS and math.abs(hit.Normal:Dot(f.normal))>0.98 then
                            table.insert(report.terrainHits,{part=r.desc,face=f.id.Name,position=vec(hit.Position),
                                material=hit.Material.Name,distance=d,category="terrain-surface-coplanar"})
                        end
                    end
                end
            end
        end end
        if i % 100 == 0 then task.wait() end
    end
end
report.terrainSamples=terrainSamples
report.counts.terrainCoplanar=#report.terrainHits
report.counts.animationSourceCandidates=#report.animationSources
report.counts.modelBotMeshHits=#report.modelBotMeshHits
report.counts.total=0
for _,category in ipairs(categoryNames) do report.counts.total+=report.counts[category] end
report.reviewCounts = {}
for _,category in ipairs(categoryNames) do
    local counts = {}
    for _,hit in ipairs(report.hits[category]) do
        local kind = hit.reviewClass or "transparency-review"
        counts[kind] = (counts[kind] or 0) + 1
    end
    report.reviewCounts[category] = counts
end
report.counts.geometryCategories123=report.counts.coplanarFaces+report.counts.decoratedCoincidentFaces+report.counts.placeholderCoplanarFaces
_G.ZF1ScanJSON=HttpService:JSONEncode(report)
_G.ZF1ScanReport=report
return #_G.ZF1ScanJSON
