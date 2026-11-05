-- v15 grade (Game Art Bot): Brightness 2.0, ExposureCompensation -0.3, ColorCorrection Saturation 0 / Contrast 0.05 / Tint white. Bloom untouched (Threshold 1.1).
local L = game.Lighting
L.Brightness = 2.0; L.ExposureCompensation = -0.3
local cc = L:FindFirstChildOfClass("ColorCorrectionEffect")
cc.Saturation = 0; cc.Contrast = 0.05; cc.TintColor = Color3.fromRGB(255, 255, 255)
local bl = L:FindFirstChildOfClass("BloomEffect")
print(string.format("GRADE15 bright=%.2f exp=%.2f sat=%.2f contrast=%.2f tint=%s bloomThr=%s", L.Brightness, L.ExposureCompensation, cc.Saturation, cc.Contrast, tostring(cc.TintColor), tostring(bl and bl.Threshold)))
