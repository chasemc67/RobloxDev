-- LobbySpin: turns the lobby's moving decor (LobbyBuilder tags it LobbySpinner: SpinPivot, SpinAxis, SpinRPM) on
-- each client, phase-locked to server time so everyone sees the same angle. Anchored decor, local CFrame only.
local CollectionService = game:GetService("CollectionService")
local RunService = game:GetService("RunService")

local TAG = "LobbySpinner"
local spinners = {}

local function add(m)
	if m:IsA("Model") then
		spinners[m] = true
	end
end
for _, m in CollectionService:GetTagged(TAG) do
	add(m)
end
CollectionService:GetInstanceAddedSignal(TAG):Connect(add)
CollectionService:GetInstanceRemovedSignal(TAG):Connect(function(m)
	spinners[m] = nil
end)

RunService.RenderStepped:Connect(function()
	local t = workspace:GetServerTimeNow()
	local cam = workspace.CurrentCamera
	for m in spinners do
		local pivot, axis, rpm = m:GetAttribute("SpinPivot"), m:GetAttribute("SpinAxis"), m:GetAttribute("SpinRPM")
		-- only while someone could see it (the lobby is far from the course)
		if pivot and axis and rpm and m.Parent and (cam.CFrame.Position - pivot.Position).Magnitude < 400 then
			m:PivotTo(pivot * CFrame.fromAxisAngle(axis, (t * rpm / 60 % 1) * 2 * math.pi))
		end
	end
end)
