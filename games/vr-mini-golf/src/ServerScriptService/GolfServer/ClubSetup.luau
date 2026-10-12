-- Per-player, per-hand grip calibration. Studio tests use memory unless ClubSetupInStudio=true.
-- Like PersonalBest: every DataStore call is pcall'd; if DataStores are unavailable (unpublished place, API
-- access off) it warns once and keeps fits in memory for the session.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local DataStoreService = game:GetService("DataStoreService")
local ClubSetup = {}
local cache, busy, lastSave = {}, {}, {}
local offline = RunService:IsStudio() and workspace:GetAttribute("ClubSetupInStudio") ~= true
local store, warned = nil, false
local function goOffline(err)
	offline = true
	if not warned then
		warned = true
		warn("[ClubSetup] DataStores unavailable (" .. tostring(err) .. "); club fits are kept for this session only")
	end
end
local function isFatal(err)
	local s = string.lower(tostring(err))
	for _, w in { "studio", "publish", "403", "not allowed", "forbidden" } do
		if string.find(s, w, 1, true) then return true end
	end
	return false
end
if not offline then
	local ok, result = pcall(function() return DataStoreService:GetDataStore("VRMiniGolf_ClubSetup_v1") end)
	if ok and result then store = result else goOffline(result) end
end
local function valid(raw)
	if type(raw) ~= "table" or type(raw.angles) ~= "table" then return nil end
	local out = { angles = {}, length = raw.length }
	if type(out.length) ~= "number" or out.length ~= out.length or out.length < 1.2 or out.length > 4 then return nil end
	for i = 1, 3 do
		local v = raw.angles[i]
		if type(v) ~= "number" or v ~= v or math.abs(v) > math.pi * 2 then return nil end
		out.angles[i] = v
	end
	return out
end
local function request(fn)
	if offline or not store then return false, nil end
	for attempt = 1, 3 do
		local ok, value = pcall(fn)
		if ok then return true, value end
		if isFatal(value) then goOffline(value); return false, nil end
		if attempt < 3 then task.wait(0.5 * attempt) end
	end
	return false, nil
end
function ClubSetup.init(remotes)
	local remote = remotes:FindFirstChild("ClubSetup") or Instance.new("RemoteFunction")
	remote.Name = "ClubSetup"
	remote.Parent = remotes
	remote.OnServerInvoke = function(player, action, hand, raw)
		local id = player.UserId
		if busy[id] then return { ok = false, message = "Please wait, then try again" } end
		if action ~= "load" and action ~= "save" and action ~= "reset" then return { ok = false } end
		if action ~= "load" and hand ~= "LeftHand" and hand ~= "RightHand" then return { ok = false } end
		local value = action == "save" and valid(raw) or nil
		if action == "save" and not value then return { ok = false } end
		if action ~= "load" and os.clock() - (lastSave[id] or -10) < 1 then return { ok = false, message = "Please wait a moment" } end
		busy[id] = true
		if not cache[id] then
			local ok, data = true, {}
			if not offline then ok, data = request(function() return store:GetAsync("u_" .. id) end) end
			if not ok and offline then ok, data = true, {} end -- DataStores just went away: session-only
			if not ok then busy[id] = nil; return { ok = false, message = "Could not load saved fit; try again" } end
			local rec = {}
			if type(data) == "table" then
				for _, h in { "LeftHand", "RightHand" } do rec[h] = valid(data[h]) end
			end
			cache[id] = rec
		end
		if action == "load" then busy[id] = nil; return { ok = true, fits = cache[id], sessionOnly = offline } end
		lastSave[id] = os.clock()
		local ok = true
		if not offline then
			ok = request(function()
				return store:UpdateAsync("u_" .. id, function(old)
					local rec = type(old) == "table" and old or {}
					rec[hand] = value
					return rec
				end)
			end)
			if not ok and offline then ok = true end -- DataStores just went away: keep it for the session
		end
		if ok then cache[id][hand] = value end
		busy[id] = nil
		return { ok = ok, sessionOnly = offline, message = not ok and "Save failed; pull trigger to retry" or nil }
	end
	Players.PlayerRemoving:Connect(function(player)
		cache[player.UserId], lastSave[player.UserId], busy[player.UserId] = nil, nil, nil
	end)
end
return ClubSetup
