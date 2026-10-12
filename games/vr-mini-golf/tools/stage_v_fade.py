#!/usr/bin/env python3
"""Stage v (Playtest Bot round 7 #5/#6): flat-screen XRay outline fade timing.

  python3 tools/stage_v_fade.py --out playtests/stage-v/fade

One desktop play session (GolfTestMode, no SimulateVR, normal golf camera). A client-only opaque card is kept
between the camera and the ball so the ball is always occluded; the ball outline then follows only the aim gate
(Ball.seeThrough). Samples GolfXRayDebug every rendered frame (after GolfXRay) while GolfTestAPI "hitat" re-places
the ball (gate on -> fade in) and putts it (gate off -> fade out). Pass: every fade-in (gate on -> alpha 1) and
fade-out (gate off -> alpha 0) takes <= 0.1 s, and no outline frame shows while the ball rolls.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_playtests import Studio, set_edit_attrs, GAME_DIR, wait_api  # noqa: E402

SAMPLE = r'''
local RS = game:GetService("RunService")
local HS = game:GetService("HttpService")
local me = game.Players.LocalPlayer
local hook = me.PlayerScripts:WaitForChild("GolfXRayDebug")
local api = game.ReplicatedStorage:WaitForChild("GolfTestAPI")
local camera = workspace.CurrentCamera
local ball = workspace.Balls:FindFirstChildWhichIsA("BasePart")
local card = Instance.new("Part")
card.Name = "StageVFadeCard"
card.Anchored, card.CanCollide, card.CanTouch, card.CanQuery = true, false, false, true
card.Size = Vector3.new(3, 3, 0.2)
card.Color = Color3.new(0.2, 0.2, 0.2)
card.Parent = workspace
RS:BindToRenderStep("StageVCard", Enum.RenderPriority.Last.Value - 1, function()
    local b = workspace.Balls:FindFirstChildWhichIsA("BasePart")
    if not b then return end
    local eye = camera.CFrame.Position
    card.CFrame = CFrame.lookAt(eye:Lerp(b.Position, 0.5), b.Position)
end)
local rows, t0 = {}, os.clock()
RS:BindToRenderStep("StageVFade", Enum.RenderPriority.Last.Value + 1, function()
    local s = hook:Invoke()
    local hl = camera:FindFirstChild("BallXRay")
    local b = workspace.Balls:FindFirstChildWhichIsA("BasePart")
    table.insert(rows, { os.clock() - t0, s.ball.gate and 1 or 0, s.ball.on and 1 or 0, math.floor(s.ball.alpha * 1000) / 1000,
        hl and hl.Enabled and 1 or 0, b and math.floor(b.AssemblyLinearVelocity.Magnitude * 100) / 100 or 0 })
end)
task.wait(1.5)
local hole = me:GetAttribute("Hole") or 1
for i, v in { "2.5,0", "0,2.5", "-2.5,0" } do
    local b = workspace.Balls:FindFirstChildWhichIsA("BasePart")
    local p = b.Position
    api:Invoke("hitat", hole, string.format("%.3f,%.3f,%.3f", p.X, p.Y - 0.08, p.Z), v)
    task.wait(1.2)
end
RS:UnbindFromRenderStep("StageVFade")
RS:UnbindFromRenderStep("StageVCard")
card:Destroy()
return HS:JSONEncode({ rows = rows })
'''


def analyse(rows):
    """Durations from each gate edge to the alpha reaching its target."""
    fades = []
    prev_gate = rows[0][1]
    for i, r in enumerate(rows):
        t, gate = r[0], r[1]
        if gate != prev_gate:
            target = 1.0 if gate else 0.0
            done = None
            for r2 in rows[i:]:
                if r2[1] != gate:
                    break
                if abs(r2[3] - target) < 1e-3:
                    done = r2[0]
                    break
            fades.append({"kind": "in" if gate else "out", "t": round(t, 3),
                          "seconds": None if done is None else round(done - t, 3)})
        prev_gate = gate
    rolling = [r for r in rows if r[5] > 0.2]
    return fades, {"frames": len(rolling), "outlineShown": sum(1 for r in rolling if r[4] or r[2])}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=os.path.join(GAME_DIR, "playtests", "stage-v", "fade"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    st = Studio()
    st.stop_play()
    set_edit_attrs(st, {"GolfTestMode": True, "SimulateVR": False, "GolfTestCamera": ""})
    try:
        st.start_play()
        wait_api(st)
        time.sleep(3)
        res = json.loads(st.luau(SAMPLE, "Client", timeout=120))
        fades, rolling = analyse(res["rows"])
        ins = [f for f in fades if f["kind"] == "in"]
        outs = [f for f in fades if f["kind"] == "out"]
        out = {
            "frames": len(res["rows"]),
            "fades": fades,
            "maxFadeIn": max((f["seconds"] for f in ins if f["seconds"] is not None), default=None),
            "maxFadeOut": max((f["seconds"] for f in outs if f["seconds"] is not None), default=None),
            "rolling": rolling,
            "console": {"server": st.problems("Server"), "client": st.problems("Client")},
        }
        out["pass"] = (len(ins) > 0 and len(outs) > 0 and all(f["seconds"] is not None and f["seconds"] <= 0.1 for f in fades)
                       and rolling["frames"] > 0 and rolling["outlineShown"] == 0 and not any(out["console"].values()))
        with open(os.path.join(args.out, "fade.json"), "w") as f:
            json.dump(dict(out, rows=res["rows"]), f)
        print(json.dumps(out, indent=1), flush=True)
        if not out["pass"]:
            raise SystemExit(1)
    finally:
        st.stop_play()
        set_edit_attrs(st, {"GolfTestMode": False, "SimulateVR": False, "GolfTestCamera": None})


if __name__ == "__main__":
    main()
