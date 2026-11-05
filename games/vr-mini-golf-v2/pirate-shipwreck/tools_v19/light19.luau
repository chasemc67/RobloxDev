-- v19: Game Art Bot lighting. Sky, Atmosphere (haze), torches, ColorCorrection, Bloom, ExposureCompensation (-0.3) are NOT touched.
local L = game.Lighting
local function p(tag) print(string.format("LIGHT19 %s bright=%.2f top=%s bottom=%s amb=%s out=%s exp=%.2f", tag, L.Brightness, tostring(L.ColorShift_Top), tostring(L.ColorShift_Bottom), tostring(L.Ambient), tostring(L.OutdoorAmbient), L.ExposureCompensation)) end
p("before")
L.Brightness = 1.6
L.ColorShift_Top = Color3.fromRGB(255, 245, 230)
L.ColorShift_Bottom = Color3.fromRGB(0, 0, 0)
L.Ambient = Color3.fromRGB(110, 110, 115)
L.OutdoorAmbient = Color3.fromRGB(135, 135, 140)
p("after")
