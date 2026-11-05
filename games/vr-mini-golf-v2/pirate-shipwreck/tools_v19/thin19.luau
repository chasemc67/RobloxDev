-- v19 step 4b: thin the pad 10 back-view dark canopy by HIDING (never deleting) the two first-layer BackdropPersistent.canopy_wall pieces in the pad 10 back cone
local TARGETS = { Vector3.new(521.6, 52.5, 159.1), Vector3.new(557.3, 49.1, 45.7) }
local out = {}
for _, d in ipairs(workspace.World.Dressing.BackdropPersistent:GetChildren()) do
  if d:IsA("BasePart") and d.Name == "canopy_wall" then
    for _, t in ipairs(TARGETS) do
      if (d.Position - t).Magnitude < 0.5 then
        d.Transparency = 1; d.CanCollide = false; d.CanQuery = false; d.CastShadow = false
        table.insert(out, string.format("THIN19 hid %s pos=(%.1f,%.1f,%.1f) size=(%.1f,%.1f,%.1f) scale(x/293.5)=%.3f mesh=%s trans=%.0f cc=%s cq=%s cs=%s", d:GetFullName(), d.Position.X, d.Position.Y, d.Position.Z, d.Size.X, d.Size.Y, d.Size.Z, d.Size.X / 293.5, d.MeshId, d.Transparency, tostring(d.CanCollide), tostring(d.CanQuery), tostring(d.CastShadow)))
      end
    end
  end
end
table.insert(out, "THIN19 count " .. #out)
return table.concat(out, "\n")
