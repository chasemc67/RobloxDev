-- Run in Edit after File > Import of vr_wrist_bracer.fbx with LG Stud Scene Anchored.
-- Refreshed October 11 file has .37 x .28 face; fit exact canvas aspect without changing straps.
local golf = game.ReplicatedStorage.Golf
local old = golf:WaitForChild("WristBracer")
local model = workspace:WaitForChild("vr_wrist_bracer")
for _, part in model:GetDescendants() do
    if part:IsA("BasePart") then
        part.Name = part.Name:gsub("vr_wrist_bracer__", "")
        local previous = old:FindFirstChild(part.Name, true)
        if previous then part.Color, part.Material = previous.Color, previous.Material end
        part.CFrame = CFrame.Angles(0, math.pi, 0) * part.CFrame
        part.Anchored, part.Massless = true, true
        part.CanCollide, part.CanTouch, part.CanQuery = false, false, false
        if part.Name == "WristFace" then part.Size = Vector3.new(.37, .001, .37 * 784 / 1024) end
    end
end
model.WorldPivot = CFrame.identity
old:Destroy()
model.Name, model.Parent = "WristBracer", golf
return "prepared"
