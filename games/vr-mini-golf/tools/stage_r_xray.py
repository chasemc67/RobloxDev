#!/usr/bin/env python3
"""Frame-synchronous H6 VR wheel regression; run only with exclusive Studio ownership.

python3 tools/stage_r_xray.py --out playtests/stage-r/xray
Truth uses independent rays to LIVE ball/putter positions after GolfXRay rendered.
No transition allowance: both logical state and Highlight.Enabled must match.
Stage t (round 7): the ball outline also needs the fade gate (ball at rest + aiming/lining up, XRay.state().gate),
so expected = occluded AND gate; a second phase putts the ball and requires 0 ball-outline frames while it rolls.
"""
import argparse
import json
import os
import time

from run_playtests import Studio, set_edit_attrs
from xray_shots import FIND_HEAD, place
from ui_shots import capture

SAMPLE = r'''
local RS = game:GetService("RunService")
local HS = game:GetService("HttpService")
local me = game.Players.LocalPlayer
local hook = me.PlayerScripts:WaitForChild("GolfXRayDebug")
local CO = require(game.ReplicatedStorage.Golf.CameraOcclusion)
local rp = RaycastParams.new()
rp.FilterType = Enum.RaycastFilterType.Exclude
rp.CollisionGroup = CO.CAMERA_GROUP
rp.IgnoreWater = true
local function vec(p) return {p.X, p.Y, p.Z} end
-- Independent query, not XRay.blocked or cached test-fixture coordinates.
local function truth(eye, p, margin)
    local d = p - eye
    if d.Magnitude - margin <= 0.05 then return false, nil end
    local ignore = {workspace.CurrentCamera, workspace.Balls, me.Character}
    for _ = 1, 32 do
        rp.FilterDescendantsInstances = ignore
        local hit = workspace:Raycast(eye, d.Unit * (d.Magnitude - margin), rp)
        if not hit then return false, nil end
        if hit.Instance:IsA("Terrain") or hit.Instance.Transparency < 0.95 then
            return true, hit.Instance:GetFullName()
        end
        table.insert(ignore, hit.Instance)
    end
    error("truth ray transparent-surface limit exceeded")
end
local rows, failure = {}, nil
local start = os.clock()
local bind = "StageRXRayTruth"
RS:BindToRenderStep(bind, Enum.RenderPriority.Last.Value + 1, function()
    local ok, err = pcall(function()
        local camera = workspace.CurrentCamera
        local eye = camera.CFrame.Position -- SimulateVR writes the live head here.
        local state = hook:Invoke()
        local row = {}
        for _, name in {"ball", "club"} do
            local hl = camera:FindFirstChild(name == "ball" and "BallXRay" or "ClubXRay")
            local target = name == "ball" and workspace.Balls:FindFirstChildWhichIsA("BasePart")
                or (camera:FindFirstChild("VRPutter") and camera.VRPutter:FindFirstChild("Head"))
            assert(hl and target and hl.Adornee == target, name .. " highlight/target missing or misbound")
            local p = target.Position
            local blocked, blocker = truth(eye, p, name == "ball" and 0.12 or 0.1)
            local gate = state[name].gate
            -- short keys (the MCP result is capped at 100 kB): t truth, o occluded, g gate, n on, e enabled, s speed
            row[name] = {t = blocked and gate, o = blocked, g = gate, n = state[name].on, e = hl.Enabled,
                s = name == "ball" and math.floor(target.AssemblyLinearVelocity.Magnitude * 100) / 100 or nil}
        end
        table.insert(rows, row)
    end)
    if not ok then failure = tostring(err) end
end)
local PHASE = PHASE_ARG
if PHASE == "rolling" then
    me.PlayerScripts:WaitForChild("GolfPointerDebug"):Invoke("randomStroke", 617)
end
while not failure and (#rows < 600 or os.clock() - start < 10) and os.clock() - start < 75 do
    task.wait(0.1)
    if PHASE == "rolling" and os.clock() - start > 8 then break end
    if PHASE == "rolling" and os.clock() - start > 2 and #rows > 120 then
        local last = rows[#rows].ball
        if last and last.s and last.s < 0.05 then break end
    end
end
RS:UnbindFromRenderStep(bind)
return HS:JSONEncode({rows = rows, error = failure, seconds = os.clock() - start})
'''


KEYS = {"t": "truth", "o": "occluded", "g": "gate", "n": "on", "e": "enabled", "s": "speed"}


def expand(result):
    result["rows"] = [{k: {KEYS[a]: b for a, b in v.items()} for k, v in r.items()} for r in result["rows"]]
    return result


def summarize(rows, name):
    values = [r[name] for r in rows]
    result = {"blocked": sum(v["truth"] for v in values), "clear": sum(not v["truth"] for v in values)}
    for field in ("on", "enabled"):
        result[field] = {
            "misses": sum(v["truth"] and not v[field] for v in values),
            "falseShows": sum(not v["truth"] and v[field] for v in values),
        }
    result["occludedFrames"] = sum(v.get("occluded", v["truth"]) for v in values)
    result["shownFrames"] = sum(v["enabled"] for v in values)
    result["pass"] = result["blocked"] > 0 and result["clear"] > 0 and all(
        counts == {"misses": 0, "falseShows": 0} for counts in (result["on"], result["enabled"]))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="playtests/stage-r/xray")
    args = parser.parse_args()
    os.makedirs(args.out, exist_ok=True)
    st = Studio()
    st.stop_play()
    set_edit_attrs(st, {"GolfTestMode": True, "SimulateVR": True})
    try:
        st.start_play()
        time.sleep(12)
        place(st, 6, (37.5, 30.0, -63.2))
        found = json.loads(st.luau(FIND_HEAD % json.dumps("mill"), "Client"))
        if "head" not in found:
            raise RuntimeError("No wheel-blocked viewpoint: " + json.dumps(found))
        head, ball, club = found["head"], found["ball"], found["club"]
        pose = {"head": head, "look": ball, "club": [club[0], ball[1] - 0.015, club[2]],
                "face": [club[0] - ball[0], 0, club[2] - ball[2]]}
        st.luau("local p = game.Players.LocalPlayer.PlayerScripts:WaitForChild('GolfPointerDebug'); "
                "return p:Invoke('pose', game:GetService('HttpService'):JSONDecode(%s))" % json.dumps(json.dumps(pose)), "Client")
        time.sleep(0.5)
        capture(st, os.path.join(args.out, "h6_before.png"))
        result = expand(json.loads(st.luau(SAMPLE.replace("PHASE_ARG", '"rest"'), "Client", timeout=90)))
        result["fixture"] = found
        result["samples"] = len(result["rows"])
        result["ball"] = summarize(result["rows"], "ball")
        result["club"] = summarize(result["rows"], "club")
        result["console"] = {"server": st.problems("Server"), "client": st.problems("Client")}
        result["pass"] = (not result.get("error") and result["samples"] >= 600 and result["seconds"] >= 10
                          and result["ball"]["pass"] and result["club"]["pass"]
                          and not any(result["console"].values()))
        with open(os.path.join(args.out, "h6_wheel_live.json"), "w") as f:
            json.dump(result, f, indent=1)
        capture(st, os.path.join(args.out, "h6_after.png"))
        # round 7: putt from the wheel-blocked spot; the ball outline must never show while it rolls
        roll = expand(json.loads(st.luau(SAMPLE.replace("PHASE_ARG", '"rolling"'), "Client", timeout=90)))
        moving = [r for r in roll["rows"] if r["ball"]["speed"] > 0.2]
        result["rolling"] = {"frames": len(moving), "occludedFrames": sum(r["ball"]["occluded"] for r in moving),
                             "outlineShown": sum(r["ball"]["enabled"] or r["ball"]["on"] for r in moving),
                             "error": roll.get("error")}
        result["pass"] = result["pass"] and not roll.get("error") and len(moving) > 0 and result["rolling"]["outlineShown"] == 0
        with open(os.path.join(args.out, "h6_wheel_live.json"), "w") as f:
            json.dump(result, f, indent=1)
        print(json.dumps({k: v for k, v in result.items() if k != "rows"}), flush=True)
        if not result["pass"]:
            raise SystemExit(1)
    finally:
        st.stop_play()
        set_edit_attrs(st, {"GolfTestMode": False, "SimulateVR": False, "GolfTestCamera": None,
                            "GolfTestCamPos": None, "GolfTestFocus": None, "GolfTestFOV": None})


if __name__ == "__main__":
    main()
