-- Real-headset-only diagnostic samples, 10s/client, bounded rolling history persisted at most once/minute.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local DataStoreService = game:GetService("DataStoreService")
local golf = game:GetService("ReplicatedStorage"):WaitForChild("Golf")
local remotes = golf:WaitForChild("Remotes")
local remote = remotes:FindFirstChild("WristPose") or Instance.new("RemoteEvent")
remote.Name = "WristPose"; remote.Parent = remotes
local store = DataStoreService:GetDataStore("WristPoseLog")
local records = {}
local function finite(v, low, high)
	return type(v) == "number" and v == v and v >= low and v <= high
end
local function flush(player)
	local r = records[player]
	if not r or r.busy or #r.samples == 0 then return end
	r.busy = true
	local batch = r.samples; r.samples = {}
	local ok = pcall(function()
		store:UpdateAsync("u_" .. player.UserId, function(old)
			old = type(old) == "table" and old or {}
			local rows = type(old.samples) == "table" and old.samples or {}
			for _, row in batch do table.insert(rows, row) end
			while #rows > 120 do table.remove(rows, 1) end
			return { version = 1, updated = os.time(), samples = rows }
		end)
	end)
	if not ok then for _, row in batch do table.insert(r.samples, row) end end
	while #r.samples > 120 do table.remove(r.samples, 1) end
	r.busy = false
	player:SetAttribute("WristPoseLogStatus", ok and "saved" or "retry")
end
remote.OnServerEvent:Connect(function(player, data)
	if RunService:IsStudio() or type(data) ~= "table" then return end
	local r = records[player] or { samples = {}, last = -math.huge }; records[player] = r
	local now = os.clock()
	if now - r.last < 9 or not finite(data.faceDeg, 0, 180) or not finite(data.gazeDeg, 0, 180)
		or not finite(data.backDeg, 0, 180) or not finite(data.distance, 0, 20) or not finite(data.speed, 0, 1000) then return end
	r.last = now
	table.insert(r.samples, { t = os.time(), face = data.faceDeg, back = data.backDeg, gaze = data.gazeDeg,
		distance = data.distance, speed = data.speed, shown = data.shown == true, manual = data.manual == true,
		hand = data.hand == "left" and "left" or "right", hole = player:GetAttribute("Hole"), job = game.JobId })
	while #r.samples > 120 do table.remove(r.samples, 1) end
end)
Players.PlayerRemoving:Connect(function(player) flush(player); records[player] = nil end)
task.spawn(function()
	while task.wait(60) do for player in records do flush(player) end end
end)
game:BindToClose(function() for player in records do flush(player) end end)
