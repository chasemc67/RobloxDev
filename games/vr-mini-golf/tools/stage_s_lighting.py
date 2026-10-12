#!/usr/bin/env python3
"""H9 runtime zone entry/exit regression. Exclusive Studio ownership required.

No shots. One desktop play session; a cloned production H9Lighting module reads
injected positions against the actual generated Hole9.Bounds. Always returns to Edit.
"""
import argparse
import json
import os
import time

from run_playtests import Studio, set_edit_attrs

SAMPLE = r'''
local Lighting = game:GetService("Lighting")
local RS = game:GetService("RunService")
local HS = game:GetService("HttpService")
local modules = game.Players.LocalPlayer.PlayerScripts:WaitForChild("GolfClient")
local source = modules:WaitForChild("H9Lighting")
local live = require(source)
live.stop() -- Prevent the regular playing-position callback from racing the fixture.
local clone = source:Clone()
clone.Name = "StageSH9LightingTest"
clone.Parent = modules
local zone = require(clone)
local bounds = workspace.Course:WaitForChild("Hole9"):WaitForChild("Bounds")
local originalExposure = Lighting.ExposureCompensation
local originalBlooms = {}
for _, effect in Lighting:GetChildren() do
    if effect:IsA("BloomEffect") then originalBlooms[effect] = effect.Intensity end
end
local sentinel = Instance.new("BloomEffect")
sentinel.Name = "StageSLightingSentinel"
sentinel.Intensity = 0.374
sentinel.Enabled = false -- Exercise data preservation without changing the screenshot.
sentinel.Parent = Lighting
local result = {cases = {}, fixture = {boundsSize = {bounds.Size.X, bounds.Size.Y, bounds.Size.Z}}}
local position = bounds.CFrame:PointToWorldSpace(Vector3.new(bounds.Size.X / 2 + 8, 0, 0))
local baselineExposure, baselineBlooms
local function baseline()
    baselineExposure = Lighting.ExposureCompensation
    baselineBlooms = {}
    for _, effect in Lighting:GetChildren() do
        if effect:IsA("BloomEffect") then baselineBlooms[effect] = effect.Intensity end
    end
end
local function settle()
    local start = os.clock()
    repeat RS.RenderStepped:Wait() until os.clock() - start >= 0.35
end
local function check(name, inside, exact)
    local expectedExposure = baselineExposure - (inside and 0.3 or 0)
    local currentExposure = Lighting.ExposureCompensation
    local pass = workspace:GetAttribute("H9LightingActive") == inside
        and (exact and currentExposure == expectedExposure
            or not exact and math.abs(currentExposure - expectedExposure) < 1e-6)
    local row = {name = name, inside = inside, exposure = currentExposure,
        expectedExposure = expectedExposure, exactRestore = exact, blooms = {}, pass = pass}
    for effect, value in baselineBlooms do
        local expected = value * (inside and 0.5 or 1)
        local actual = effect.Intensity
        local matches = exact and actual == expected or not exact and math.abs(actual - expected) < 1e-6
        table.insert(row.blooms, {name = effect.Name, actual = actual, expected = expected, pass = matches})
        row.pass = row.pass and matches
    end
    table.insert(result.cases, row)
    assert(row.pass, "H9 lighting mismatch: " .. name)
end
local ok, err = xpcall(function()
    baseline()
    zone.start(function() return position end)
    settle()
    check("outside initial", false, true)
    position = bounds.Position
    settle()
    check("enter", true, false)
    settle()
    check("remain inside no compounding", true, false)
    position = bounds.CFrame:PointToWorldSpace(Vector3.new(bounds.Size.X / 2 + 8, 0, 0))
    settle()
    check("leave exact restore", false, true)
    -- A different environment baseline between visits must be captured afresh.
    Lighting.ExposureCompensation = originalExposure + 0.173
    for effect, value in baselineBlooms do effect.Intensity = value + 0.117 end
    baseline()
    position = bounds.Position
    settle()
    check("reenter changed baseline", true, false)
    zone.stop()
    check("stop while inside exact restore", false, true)
    -- Missing playing position is an exit too (ball removed/scene transition).
    zone.start(function() return position end)
    settle()
    check("restart entry", true, false)
    position = nil
    settle()
    check("nil position exact restore", false, true)
end, debug.traceback)
zone.stop()
clone:Destroy()
Lighting.ExposureCompensation = originalExposure
for effect, value in originalBlooms do if effect.Parent then effect.Intensity = value end end
sentinel:Destroy()
result.pass = ok
result.error = not ok and tostring(err) or nil
result.finalExposure = Lighting.ExposureCompensation
result.originalExposure = originalExposure
result.finalRestoreExact = result.finalExposure == originalExposure
return HS:JSONEncode(result)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="playtests/stage-s/h9-lighting.json")
    args = parser.parse_args()
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    st = Studio()
    result = {"pass": False}
    try:
        st.stop_play()
        set_edit_attrs(st, {"GolfTestMode": True, "SimulateVR": False, "SkipMenu": True})
        st.start_play()
        time.sleep(10)
        result = json.loads(st.luau(SAMPLE, "Client", timeout=60))
        result["console"] = {"server": st.problems("Server"), "client": st.problems("Client")}
        result["pass"] = (result.get("pass", False) and result.get("finalRestoreExact", False)
                          and len(result.get("cases", [])) == 8 and not any(result["console"].values()))
    except Exception as exc:
        result["pass"] = False
        result["runnerError"] = str(exc)
    finally:
        try:
            st.stop_play()
            set_edit_attrs(st, {"GolfTestMode": False, "SimulateVR": False, "SkipMenu": None})
            result["finalMode"] = st.mode()[0]
            result["pass"] = result.get("pass", False) and result["finalMode"] == "Edit"
        except Exception as exc:
            result["pass"] = False
            result["cleanupError"] = str(exc)
        with open(args.out, "w") as stream:
            json.dump(result, stream, indent=2)
        print(json.dumps(result), flush=True)
    if not result["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
