local HS = game:GetService("HttpService")
HS.HttpEnabled = true
local ok, src = pcall(function() return HS:GetAsync("http://localhost:8765/dressing_v20.luau?v=20") end)
HS.HttpEnabled = false
if not ok then print("LT20D ERR " .. tostring(src)) return end
local f, err = loadstring(src)
if not f then print("LT20D COMPILE ERR " .. tostring(err)) return end
local ok2, e2 = pcall(f)
print("LT20D run ok=" .. tostring(ok2) .. " " .. tostring(e2) .. " http=" .. tostring(HS.HttpEnabled))
