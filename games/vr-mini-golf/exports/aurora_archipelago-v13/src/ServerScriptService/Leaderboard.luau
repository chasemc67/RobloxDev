-- Leaderboard (stage z): best round totals per course in OrderedDataStores "VRMiniGolf_Best_v1_<courseId>"
-- (key = tostring(UserId), value = the lowest full-round total). Universe-wide, so the course places write and the
-- lobby reads.
--   * Leaderboard.submit(userId, courseId, total): UpdateAsync, keeps the lower total (GolfServer, on a counted round;
--     LobbyServer also back-fills a player's saved personal bests when they join the lobby).
--   * Leaderboard.top(courseId, n): { { userId, total } } lowest first, or nil + error.
--   * Studio playtests stay offline like PersonalBest (this universe has Studio API access off) unless workspace
--     PBInStudio is set. Offline, top() reads workspace attribute LeaderboardMock (JSON { [courseId] = { {userId,
--     total, name}, ... } }) so the board can be tested in Studio; submit() is a no-op.
local DataStoreService = game:GetService("DataStoreService")
local RunService = game:GetService("RunService")
local HttpService = game:GetService("HttpService")

local Leaderboard = {}

local PREFIX = "VRMiniGolf_Best_v1_"
local TRIES = 3

local offline = RunService:IsStudio() and workspace:GetAttribute("PBInStudio") ~= true
local stores = {}

local function storeOf(courseId)
	if offline then
		return nil
	end
	if stores[courseId] == nil then
		local ok, s = pcall(function()
			return DataStoreService:GetOrderedDataStore(PREFIX .. courseId)
		end)
		stores[courseId] = ok and s or false
	end
	return stores[courseId] or nil
end

function Leaderboard.isOffline()
	return offline
end

function Leaderboard.submit(userId: number, courseId: string, total: number)
	if type(userId) ~= "number" or userId <= 0 or type(total) ~= "number" or total <= 0 then
		return
	end
	local store = storeOf(courseId)
	if not store then
		return
	end
	total = math.floor(total)
	task.spawn(function()
		for i = 1, TRIES do
			local ok, err = pcall(function()
				store:UpdateAsync(tostring(userId), function(old)
					if type(old) == "number" and old <= total then
						return nil -- keep the better one (no write)
					end
					return total
				end)
			end)
			if ok then
				return
			end
			if i == TRIES then
				warn("[Leaderboard] submit failed: " .. tostring(err))
			else
				task.wait(2 * i)
			end
		end
	end)
end

function Leaderboard.top(courseId: string, n: number?)
	n = math.clamp(n or 8, 1, 100)
	if offline then
		local ok, mock = pcall(HttpService.JSONDecode, HttpService, workspace:GetAttribute("LeaderboardMock") or "{}")
		local list = {}
		for _, e in ok and type(mock) == "table" and mock[courseId] or {} do
			table.insert(list, { userId = e[1], total = e[2], name = e[3] })
		end
		table.sort(list, function(a, b)
			return a.total < b.total
		end)
		while #list > n do
			table.remove(list)
		end
		return list
	end
	local store = storeOf(courseId)
	if not store then
		return nil, "no store"
	end
	local ok, pages = pcall(function()
		return store:GetSortedAsync(true, n, 1)
	end)
	if not ok then
		return nil, pages
	end
	local list = {}
	for _, e in pages:GetCurrentPage() do
		local uid = tonumber(e.key)
		if uid then
			table.insert(list, { userId = uid, total = e.value })
		end
	end
	return list
end

return Leaderboard
