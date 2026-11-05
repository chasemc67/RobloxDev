-- v14 start values: thinner Atmosphere so the overview is not pink/hazy (Bloom Threshold stays 1.1, nothing else touched)
local L = game.Lighting; local a = L:FindFirstChildOfClass("Atmosphere")
a.Density = 0.04; a.Haze = 0.15; a.Offset = 0.05; a.Decay = Color3.fromRGB(200,215,235)   -- v14 step 8 tuned (was Haze 0.35 Offset 0.2, Decay 255,220,180): horizon was pink
local bl = L:FindFirstChildOfClass("BloomEffect"); if bl then bl.Threshold = 1.1 end
print(string.format("LIGHT14 dens=%.3f offset=%.2f haze=%.2f glare=%.2f decay=%s color=%s bloomThr=%s", a.Density, a.Offset, a.Haze, a.Glare, tostring(a.Decay), tostring(a.Color), tostring(bl and bl.Threshold)))
