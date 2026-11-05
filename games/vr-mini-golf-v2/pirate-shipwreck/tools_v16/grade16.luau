-- v16: Game Art Bot atmosphere (Color 255,235,210; Decay 190,150,110). v15 grade is NOT touched.
local L = game.Lighting; local a = L:FindFirstChildOfClass("Atmosphere")
a.Color = Color3.fromRGB(255, 235, 210); a.Decay = Color3.fromRGB(190, 150, 110)
print(string.format("GRADE16 atmosphere color=%s decay=%s dens=%.3f haze=%.2f offset=%.2f | bright=%.2f exp=%.2f", tostring(a.Color), tostring(a.Decay), a.Density, a.Haze, a.Offset, L.Brightness, L.ExposureCompensation))
