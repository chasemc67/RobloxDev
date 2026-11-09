-- v17b: kit_v2_5 rock cliff palette (Image 104642093288682) on both CaveV2 cliffs; Color (115,100,92); plain Plastic, no SurfaceAppearance
local CH = game:GetService("ChangeHistoryService")
local rec = CH:TryBeginRecording("v17b cliff rock palette")
local M = workspace.World.Meshes.CaveV2
local out = {}
for _, n in ipairs({ "cave_cliff_lower", "cave_cliff_upper" }) do
  local p = M[n]
  local before = p.TextureID .. " " .. tostring(p.Color)
  p.TextureID = "rbxassetid://104642093288682"
  p.Color = Color3.fromRGB(115, 100, 92)
  p.Material = Enum.Material.Plastic
  table.insert(out, string.format("CLIFF17B %s before %s after %s %s %s SA=%s", n, before, p.TextureID, tostring(p.Color), p.Material.Name, tostring(p:FindFirstChildOfClass("SurfaceAppearance") ~= nil)))
end
if rec then CH:FinishRecording(rec, Enum.FinishRecordingOperation.Commit) end
return table.concat(out, "\n")
