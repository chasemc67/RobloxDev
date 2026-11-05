--!nocheck
-- Minimal Roblox mocks so import_world.luau logic can run in the plain Luau CLI. TEST ONLY (not shipped).
local created = {}
local function mkEnum() return setmetatable({}, { __index = function(t, k) local v = setmetatable({ Name = k }, { __tostring = function() return k end }); rawset(t, k, v); return v end }) end
local Enum = setmetatable({}, { __index = function(t, k) local v = mkEnum(); rawset(t, k, v); return v end })
local V3 = {}
V3.__index = V3
local Vector3 = { new = function(x, y, z) return setmetatable({ X = x or 0, Y = y or 0, Z = z or 0 }, V3) end }
V3.__tostring = function(v) return ("%.2f,%.2f,%.2f"):format(v.X, v.Y, v.Z) end
local Color3 = { fromRGB = function(r, g, b) return { r = r, g = g, b = b } end, new = function(r, g, b) return { r = r, g = g, b = b } end }
local Region3 = { new = function(a, b) return { Min = a, Max = b } end }
local CFrame = {}
local CF = {}
CF.__index = CF
CF.__mul = function(a, b) return setmetatable({}, CF) end
CFrame.new = function(...) return setmetatable({}, CF) end
CFrame.Angles = function(...) return setmetatable({}, CF) end
local base = {}
base.__index = function(t, k)
	local m = rawget(base, k); if m then return m end
	return rawget(t, "_p")[k]
end
base.__newindex = function(t, k, v)
	if k == "Parent" then
		rawget(t, "_p").Parent = v
		if v then table.insert(rawget(v, "_kids"), t) end
		return
	end
	rawget(t, "_p")[k] = v
end
function base.IsA(self, c) return c == self._class end
function base.Destroy(self) end
function base.SetAttribute(self, k, v) self._attrs[k] = v end
function base.GetAttribute(self, k) return self._attrs[k] end
function base.FindFirstChild(self, n) for _, c in self._kids do if c.Name == n then return c end end return nil end
function base.FindFirstChildOfClass(self, cl) for _, c in self._kids do if c._class == cl then return c end end return nil end
local function newInst(class)
	local o = { _class = class, _kids = {}, _attrs = {}, _p = { Name = class } }
	if class == "Script" or class == "LocalScript" or class == "ModuleScript" then o._lsc = true end
	return setmetatable(o, base)
end
function base.IsA(self, c) if c == "LuaSourceContainer" then return self._lsc == true end return c == self._class end
local Instance = { new = function(class) local i = newInst(class); table.insert(created, class); return i end }
local writes, cellsChecked = 0, 0
local Terrain = newInst("Terrain")
function Terrain.SetMaterialColor() end
function Terrain.FillCylinder() end
function Terrain.WriteVoxelChannels(self, region, res, ch)
	assert(res == 4)
	local sm, so, lo = ch.SolidMaterial, ch.SolidOccupancy, ch.LiquidOccupancy
	local nx = #sm; assert(nx == 64 and #so == 64 and #lo == 64)
	assert(#sm[1] == 42 and #sm[1][1] == 64)
	for x = 1, nx do for y = 1, 42 do for z = 1, 64 do
		local o, w = so[x][y][z], lo[x][y][z]
		assert(o >= 0 and o <= 1 and w >= 0 and w <= 1)
		assert(o == 0 or w == 0, "solid cell contains water")
		assert((o > 0) == (sm[x][y][z] ~= Enum.Material.Air), "material/occupancy mismatch")
		cellsChecked += 1
	end end end
	writes += 1
end
local Workspace = newInst("Workspace"); Workspace._p.Terrain = Terrain
local Lighting = newInst("Lighting"); Lighting._p.GetSunDirection = function() return Vector3.new(0, 1, 0) end
function Lighting.GetSunDirection() return Vector3.new(0, 1, 0) end
local function b64decode(buf)
	local s = buffer.tostring(buf)
	local chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
	local map = {}
	for i = 1, #chars do map[string.byte(chars, i)] = i - 1 end
	local n = #s
	local pad = (string.sub(s, -2) == "==") and 2 or (string.sub(s, -1) == "=") and 1 or 0
	local outLen = n // 4 * 3 - pad
	local out = buffer.create(outLen)
	local o = 0
	for i = 1, n, 4 do
		local a, b, c, d = string.byte(s, i, i + 3)
		local v = map[a] * 262144 + map[b] * 4096 + (map[c] or 0) * 64 + (map[d] or 0)
		if o < outLen then buffer.writeu8(out, o, bit32.rshift(v, 16) % 256); o += 1 end
		if o < outLen then buffer.writeu8(out, o, bit32.rshift(v, 8) % 256); o += 1 end
		if o < outLen then buffer.writeu8(out, o, v % 256); o += 1 end
	end
	return out
end
local services = { Workspace = Workspace, Lighting = Lighting, EncodingService = { Base64Decode = function(_, b) return b64decode(b) end, DecompressBuffer = function(_, b) return b end } }
local game = { GetService = function(_, n) return services[n] end }
local workspace = Workspace
local task = { wait = function() end }
local function typeof(v) return type(v) end
local MOCK = { created = created, report = function()
	local scripts = 0
	for _, c in created do if c == "Script" or c == "LocalScript" or c == "ModuleScript" then scripts += 1 end end
	local blockout = Workspace:FindFirstChild("World") and Workspace:FindFirstChild("World"):FindFirstChild("Blockout")
	print(("MOCK: instances=%d scripts=%d chunkWrites=%d cellsChecked=%d blockoutChildren=%d"):format(#created, scripts, writes, cellsChecked, blockout and #blockout._kids or -1))
end }
