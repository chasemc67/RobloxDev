-- v19 step 3b: set every pad felt Part (Blockout.Pads.PadNN.Felt) to FELT19 (plain colour, Material unchanged)
local c = FELT19
local n, mats = 0, {}
for _, pad in ipairs(workspace.World.Blockout.Pads:GetChildren()) do
  local f = pad:FindFirstChild("Felt")
  if f and f:IsA("BasePart") then f.Color = c; n += 1; mats[f.Material.Name] = true end
end
local m = {}; for k in pairs(mats) do table.insert(m, k) end
return string.format("FELT19 set %d parts to (%d,%d,%d) materials=%s", n, math.round(c.R*255), math.round(c.G*255), math.round(c.B*255), table.concat(m, ","))
