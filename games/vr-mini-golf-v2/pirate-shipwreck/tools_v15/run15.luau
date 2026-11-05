-- v15 runner: runs ~/stage/<file> from :8765 with print captured; optional shot via :8767 after a 3 s wait. Leaves HttpEnabled false.
local HS = game:GetService("HttpService")
local out = {}
local function cap(...) local t = {} for i = 1, select("#", ...) do t[i] = tostring((select(i, ...))) end table.insert(out, table.concat(t, " ")) end
local function get(url) HS.HttpEnabled = true local ok, r = pcall(function() return HS:GetAsync(url) end) HS.HttpEnabled = false return ok, r end
local function run(file)
  local ok, src = get("http://localhost:8765/" .. file .. "?t=" .. os.clock())
  if not ok then cap("RUN15 GET ERR", file, src) return end
  local f, err = loadstring(src) if not f then cap("RUN15 COMPILE ERR", file, err) return end
  setfenv(f, setmetatable({ print = cap }, { __index = getfenv() }))
  local ok2, e2 = pcall(f) if not ok2 then cap("RUN15 RUN ERR", file, e2) end
end
local function shot(name) task.wait(3) local ok, r = get("http://localhost:8767/shot?name=" .. name) cap("SHOT", name, ok, r) end
return run, shot, out
