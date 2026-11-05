-- Applied once in Studio after the bulk import (2026-10-31). NOT idempotent: it reads the importer PivotOffset then zeroes it. See README 'How it was imported'.
local W = workspace
local meshes = W.World.Meshes
local wreckCF = CFrame.new(-617.64, 0, 217.01) * CFrame.Angles(0, math.rad(-105.2), 0)
local caveCF = CFrame.new(563.5, 66, -606.5)
local duckPivot = CFrame.new(0.69, 13.622, 162.182, -0.965926, -0.258819, 0, -0.258819, 0.965926, 0, 0, 0, -1)
for _, mp in meshes:GetDescendants() do
  if mp:IsA("MeshPart") then
    local o = mp.PivotOffset.Position
    local c = Vector3.new(o.X, -o.Y, o.Z) -- centre relative to FBX origin, in part axes
    local base = mp.Parent.Name == "WreckV2" and wreckCF or caveCF
    local cf
    if mp.Name == "wreck_duck" then cf = base * duckPivot * CFrame.new(c) else cf = base * CFrame.new(c) end
    mp.PivotOffset = CFrame.new() -- plain centre pivot so later PivotTo is safe
    mp.CFrame = cf
    local rel = base:ToObjectSpace(mp.CFrame)
    local lo, hi = Vector3.new(1e9,1e9,1e9), Vector3.new(-1e9,-1e9,-1e9)
    for sx = -1, 1, 2 do for sy = -1, 1, 2 do for sz = -1, 1, 2 do
      local p = rel:PointToWorldSpace(mp.Size / 2 * Vector3.new(sx, sy, sz))
      lo = Vector3.new(math.min(lo.X, p.X), math.min(lo.Y, p.Y), math.min(lo.Z, p.Z)); hi = Vector3.new(math.max(hi.X, p.X), math.max(hi.Y, p.Y), math.max(hi.Z, p.Z))
    end end end
    print(("MESH %s min(%.1f,%.1f,%.1f) max(%.1f,%.1f,%.1f) pos(%.1f,%.1f,%.1f) anch=%s"):format(mp.Name, lo.X, lo.Y, lo.Z, hi.X, hi.Y, hi.Z, mp.Position.X, mp.Position.Y, mp.Position.Z, tostring(mp.Anchored)))
  end
end
