-- v19 step 7b: Atmosphere Haze 0.15 -> 0 (only value that removes the grey below-horizon band; 0.10/0.05/0.02/0.01 left it unchanged). Color/Decay/Density/Offset/Glare unchanged.
local A = game.Lighting:FindFirstChildOfClass("Atmosphere")
local before = A.Haze
A.Haze = 0
return string.format("HAZE19 haze %.2f -> %.2f dens=%.3f offset=%.2f glare=%.2f color=%s decay=%s", before, A.Haze, A.Density, A.Offset, A.Glare, tostring(A.Color), tostring(A.Decay))
