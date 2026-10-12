-- PersonalBest: per-player best round totals + settings, saved in DataStore "VRMiniGolf_PB_v1".
-- Key "u_<UserId>", value { best = { lantern_grove = total, ... }, settings = { MusicVolume, SFXVolume,
-- Handedness, CameraSensitivity } }. Every call is pcall'd with retries; writes use UpdateAsync and keep the lower
-- total. If DataStores are unavailable (Studio without API access, unpublished place) it warns once and keeps
-- records in memory for the session (always in Studio unless workspace PBInStudio is set).
-- Published to the client as player attributes: Best_<courseId>, MusicVolume, SFXVolume, Handedness,
-- CameraSensitivity, and SettingsLoaded = true once the record has been read.
local DataStoreService = game:GetService("DataStoreService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = require(ReplicatedStorage:WaitForChild("Golf"):WaitForChild("Config"))

local PB = {}

local STORE_NAME = "VRMiniGolf_PB_v1"
local TRIES = 4
local SETTINGS_SAVE_DELAY = 6 -- seconds: settings changes are batched into one write

local store = nil
local offline = false -- true once DataStores are known to be unavailable: in-memory only from then on
local warned = false
local transientWarnings = 0

local records = {} -- [userId] = { best = {}, settings = {} }
local settingsDirty = {} -- [userId] = true
local saveScheduled = {} -- [userId] = true
local pendingWrites = 0

local function warnOffline(err)
	offline = true
	if not warned then
		warned = true
		warn("[PersonalBest] DataStores unavailable (" .. tostring(err) .. "); personal bests are kept for this session only")
	end
end

-- errors that retrying won't fix (Studio API access off, unpublished place)
local function isFatal(err)
	local s = string.lower(tostring(err))
	return string.find(s, "studio", 1, true) ~= nil
		or string.find(s, "publish", 1, true) ~= nil
		or string.find(s, "403", 1, true) ~= nil
		or string.find(s, "not allowed", 1, true) ~= nil
		or string.find(s, "forbidden", 1, true) ~= nil
end

do
	-- Studio playtests (this place has Studio API access off) stay in memory, so test runs log no DataStore errors;
	-- set workspace attribute PBInStudio = true to exercise the real store from Studio
	if game:GetService("RunService"):IsStudio() and workspace:GetAttribute("PBInStudio") ~= true then
		offline, warned = true, true
	end
	local ok, result = pcall(function()
		return DataStoreService:GetDataStore(STORE_NAME)
	end)
	if ok then
		store = result
	else
		warnOffline(result)
	end
end

-- Runs fn with retries and exponential backoff. Returns ok, result.
local function withRetries(fn)
	if offline or not store then
		return false, nil
	end
	for i = 1, TRIES do
		local ok, result = pcall(fn)
		if ok then
			return true, result
		end
		if isFatal(result) then
			warnOffline(result)
			return false, nil
		end
		if i < TRIES then
			task.wait(0.5 * 2 ^ (i - 1)) -- 0.5, 1, 2 s
		elseif transientWarnings < 3 then
			transientWarnings += 1
			warn("[PersonalBest] DataStore request failed after " .. TRIES .. " tries: " .. tostring(result))
		end
	end
	return false, nil
end

local function keyFor(userId)
	return "u_" .. tostring(userId)
end

local function clampSettings(raw)
	local d = Config.DefaultSettings
	local out = {}
	raw = type(raw) == "table" and raw or {}
	local function vol(v, default)
		return type(v) == "number" and v == v and math.clamp(v, 0, 1) or default
	end
	out.MusicVolume = vol(raw.MusicVolume, d.MusicVolume)
	out.SFXVolume = vol(raw.SFXVolume, d.SFXVolume)
	out.Handedness = (raw.Handedness == "Left" or raw.Handedness == "Right") and raw.Handedness or d.Handedness
	local lo, hi = Config.CameraSensitivityRange[1], Config.CameraSensitivityRange[2]
	local cs = raw.CameraSensitivity
	out.CameraSensitivity = type(cs) == "number" and cs == cs and math.clamp(cs, lo, hi) or d.CameraSensitivity
	out.CourseMode = (raw.CourseMode == "PVP" or raw.CourseMode == "Peaceful") and raw.CourseMode or d.CourseMode
	return out
end

local function normalize(data)
	data = type(data) == "table" and data or {}
	local best = {}
	if type(data.best) == "table" then
		for k, v in data.best do
			if type(k) == "string" and type(v) == "number" and v > 0 then
				best[k] = math.floor(v)
			end
		end
	end
	return { best = best, settings = clampSettings(data.settings), hasSettings = type(data.settings) == "table" }
end

local function publish(player, rec)
	if not player.Parent then
		return
	end
	for _, course in Config.Courses do
		if course.playable then
			player:SetAttribute("Best_" .. course.id, rec.best[course.id])
		end
	end
	for k, v in rec.settings do
		player:SetAttribute(k, v)
	end
end

-- Writes the record (best totals merged keeping the lower, settings if dirty).
local function save(userId)
	local rec = records[userId]
	if not rec or offline or not store then
		return
	end
	local writeSettings = settingsDirty[userId] == true
	settingsDirty[userId] = nil
	local best = table.clone(rec.best)
	local settings = table.clone(rec.settings)
	pendingWrites += 1
	local ok = withRetries(function()
		return store:UpdateAsync(keyFor(userId), function(old)
			local cur = normalize(old)
			for k, v in best do
				if not cur.best[k] or v < cur.best[k] then
					cur.best[k] = v
				end
			end
			local out = { best = cur.best }
			if writeSettings then
				out.settings = settings
			elseif cur.hasSettings then
				out.settings = cur.settings
			end
			return out
		end)
	end)
	pendingWrites -= 1
	if not ok and writeSettings and not offline then
		settingsDirty[userId] = true -- try again on the next save
	end
end

function PB.load(player)
	local userId = player.UserId
	local rec = { best = {}, settings = clampSettings(nil) }
	records[userId] = rec
	task.spawn(function()
		local ok, data = withRetries(function()
			return store:GetAsync(keyFor(userId))
		end)
		if records[userId] ~= rec then
			return -- left while loading
		end
		if ok then
			local loaded = normalize(data)
			-- keep anything that happened during the load (a round finished, a setting changed)
			for k, v in loaded.best do
				if not rec.best[k] or v < rec.best[k] then
					rec.best[k] = v
				end
			end
			if not settingsDirty[userId] then
				rec.settings = loaded.settings
			end
		end
		publish(player, rec)
		if player.Parent then
			player:SetAttribute("SettingsLoaded", true)
		end
	end)
end

function PB.get(player, courseId)
	local rec = records[player.UserId]
	return rec and rec.best[courseId]
end

-- A finished full round: returns best, isNewBest, previousBest.
function PB.recordRound(player, courseId, total)
	local userId = player.UserId
	local rec = records[userId]
	if not rec then
		return nil, false, nil
	end
	local prev = rec.best[courseId]
	local isNew = prev == nil or total < prev
	if isNew then
		rec.best[courseId] = total
		player:SetAttribute("Best_" .. courseId, total)
		task.spawn(save, userId)
	end
	return rec.best[courseId], isNew, prev
end

function PB.setSettings(player, raw)
	local userId = player.UserId
	local rec = records[userId]
	if not rec or type(raw) ~= "table" then
		return
	end
	-- merge onto the current settings so a partial table only changes what it names
	local merged = table.clone(rec.settings)
	for k, v in raw do
		if Config.DefaultSettings[k] ~= nil then
			merged[k] = v
		end
	end
	rec.settings = clampSettings(merged)
	publish(player, rec)
	settingsDirty[userId] = true
	if not saveScheduled[userId] then
		saveScheduled[userId] = true
		task.delay(SETTINGS_SAVE_DELAY, function()
			saveScheduled[userId] = nil
			if settingsDirty[userId] and records[userId] == rec then
				save(userId)
			end
		end)
	end
end

function PB.unload(player)
	local userId = player.UserId
	if records[userId] and settingsDirty[userId] then
		save(userId)
	end
	records[userId] = nil
	settingsDirty[userId] = nil
end

-- Server shutdown: flush every dirty record, then wait (up to ~25 s) for writes in flight.
function PB.flushAll()
	for userId in records do
		if settingsDirty[userId] then
			task.spawn(save, userId)
		end
	end
	local t0 = os.clock()
	task.wait()
	while pendingWrites > 0 and os.clock() - t0 < 25 do
		task.wait(0.2)
	end
end

return PB
