-- Real-headset-only diagnostic samples, 10s/client, bounded rolling history persisted at most once/minute.
-- Event samples (stage t: event = open | close | button | nearFace) have their own throttle (1.5 s, 20/min).
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local DataStoreService = game:GetService("DataStoreService")
local golf = game:GetService("ReplicatedStorage"):WaitForChild("Golf")
local remotes = golf:WaitForChild("Remotes")
local remote = remotes:FindFirstChild("WristPose") or Instance.new("RemoteEvent")
remote.Name = "WristPose"; remote.Parent = remotes
-- Like PersonalBest: DataStore calls are pcall'd and become a no-op (warned once) when DataStores are
-- unavailable (Studio, unpublished place, API access off).
local offline, warned = RunService:IsStudio(), true
local store = nil
if not offline then
	warned = false
	local ok, result = pcall(function() return DataStoreService:GetDataStore("WristPoseLog") end)
	if ok and result then store = result else offline = true end
	if not ok then warned = true; warn("[WristPoseLog] DataStores unavailable (" .. tostring(result) .. "); samples are dropped") end
end
local function isFatal(err)
	local s = string.lower(tostring(err))
	for _, w in { "studio", "publish", "403", "not allowed", "forbidden" } do
		if string.find(s, w, 1, true) then return true end
	end
	return false
end
local records = {}
local EVENTS = { open = true, close = true, button = true, nearFace = true }
local function finite(v, low, high)
	return type(v) == "number" and v == v and v >= low and v <= high
end
local function flush(player)
	local r = records[player]
	if not r or r.busy or #r.samples == 0 then return end
	if offline or not store then r.samples = {}; return end
	r.busy = true
	local batch = r.samples; r.samples = {}
	local ok, err = pcall(function()
		store:UpdateAsync("u_" .. player.UserId, function(old)
			old = type(old) == "table" and old or {}
			local rows = type(old.samples) == "table" and old.samples or {}
			for _, row in batch do table.insert(rows, row) end
			while #rows > 120 do table.remove(rows, 1) end
			return { version = 1, updated = os.time(), samples = rows }
		end)
	end)
	if not ok and isFatal(err) then
		offline = true
		if not warned then warned = true; warn("[WristPoseLog] DataStores unavailable (" .. tostring(err) .. "); samples are dropped") end
	elseif not ok then for _, row in batch do table.insert(r.samples, row) end end
	while #r.samples > 120 do table.remove(r.samples, 1) end
	r.busy = false
	player:SetAttribute("WristPoseLogStatus", ok and "saved" or "retry")
end
remote.OnServerEvent:Connect(function(player, data)
	if offline or type(data) ~= "table" then return end
	local r = records[player] or { samples = {}, last = -math.huge, lastEvent = -math.huge, minute = 0, perMinute = 0 }; records[player] = r
	local now = os.clock()
	local event = EVENTS[data.event] and data.event or nil
	if event then
		if math.floor(now / 60) ~= r.minute then r.minute, r.perMinute = math.floor(now / 60), 0 end
		if now - r.lastEvent < 1.5 or r.perMinute >= 20 then return end
	elseif now - r.last < 9 then return end
	if not finite(data.faceDeg, 0, 180) or not finite(data.gazeDeg, 0, 180)
		or not finite(data.backDeg, 0, 180) or not finite(data.distance, 0, 20) or not finite(data.speed, 0, 1000) then return end
	if event then r.lastEvent = now; r.perMinute += 1 else r.last = now end
	table.insert(r.samples, { t = os.time(), event = event, face = data.faceDeg, back = data.backDeg, gaze = data.gazeDeg,
		distance = data.distance, speed = data.speed, shown = data.shown == true, manual = data.manual == true,
		hand = data.hand == "left" and "left" or "right", hole = player:GetAttribute("Hole"), job = game.JobId })
	while #r.samples > 120 do table.remove(r.samples, 1) end
end)
Players.PlayerRemoving:Connect(function(player) flush(player); records[player] = nil end)
task.spawn(function()
	while task.wait(60) do for player in records do flush(player) end end
end)
game:BindToClose(function() for player in records do flush(player) end end)
