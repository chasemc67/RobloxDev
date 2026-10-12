#!/usr/bin/env python3
"""Round 5 check 2: wrist bracer / card. One SimulateVR normal-play session:
  1. close the title with the pointer (Play -> Play course)
  2. card values at the tee, layout geometry (aspect, faces the eye, right way up on screen), zoomed screenshots
  3. real strokes: simulated VR swings through the ball (GolfPointerDebug "pose" club path), card values after each
     (hole, par, stroke, total, best) vs the player's attributes / Scores; best via a temp server attribute
  4. wrist MENU -> title (Resume mid-round) -> Resume; wrist SCORES -> scorecard -> Close
  5. labelled pose sequences (wrist_seq.luau), right-handed then left-handed: false shows / misses
  python3 playtests/round5/scripts/r5_wrist.py --out playtests/round5/wrist
"""
import argparse
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "tools")))
from run_playtests import Studio, set_edit_attrs  # noqa: E402
from ui_shots import capture  # noqa: E402
from menu_shots import menu, pointer  # noqa: E402
from wrist_sim import LEVEL_HEAD, LOOK_AT_CARD  # noqa: E402

GEOM = r"""
local HS = game:GetService('HttpService')
local cam = workspace.CurrentCamera
local p = cam:FindFirstChild('VRWrist')
local gui
for _, g in game.Players.LocalPlayer.PlayerGui:GetChildren() do if g:IsA('SurfaceGui') and g.Adornee == p then gui = g end end
local out = {partSize = {p.Size.X, p.Size.Y}, canvas = gui and {gui.CanvasSize.X, gui.CanvasSize.Y}, face = gui and gui.Face.Name}
out.partAspect = p.Size.X / p.Size.Y
out.canvasAspect = gui and gui.CanvasSize.X / gui.CanvasSize.Y
-- canvas point -> world on the Front face (same mapping as VRPointer.targets) -> viewport
local function w(cx, cy)
  local lx = p.Size.X / 2 - cx / gui.CanvasSize.X * p.Size.X
  local ly = p.Size.Y / 2 - cy / gui.CanvasSize.Y * p.Size.Y
  return p.CFrame:PointToWorldSpace(Vector3.new(lx, ly, -p.Size.Z / 2))
end
local function vp(cx, cy) local v = cam:WorldToViewportPoint(w(cx, cy)) return {v.X, v.Y, v.Z} end
out.tl, out.tr, out.bl, out.br = vp(0, 0), vp(1024, 0), vp(0, 640), vp(1024, 640)
out.centre = vp(512, 320)
local n = -p.CFrame.LookVector -- Front face normal is -Z... (Front = -Z in Roblox)
n = p.CFrame.LookVector
local toEye = (cam.CFrame.Position - w(512, 320)).Unit
out.frontFacesEyeDeg = math.deg(math.acos(math.clamp(n:Dot(toEye), -1, 1)))
-- on-screen: top edge above bottom edge, left of the text left of the right
out.upright = out.tl[2] < out.bl[2] and out.tr[2] < out.br[2]
out.notMirrored = out.tl[1] < out.tr[1] and out.bl[1] < out.br[1]
-- roll of the card's top edge on screen
out.topEdgeRollDeg = math.deg(math.atan2(out.tr[2] - out.tl[2], out.tr[1] - out.tl[1]))
local wpx = math.sqrt((out.tr[1]-out.tl[1])^2 + (out.tr[2]-out.tl[2])^2)
local hpx = math.sqrt((out.bl[1]-out.tl[1])^2 + (out.bl[2]-out.tl[2])^2)
out.screenAspect = hpx > 0 and wpx / hpx or 0
out.distToEye = (cam.CFrame.Position - w(512, 320)).Magnitude
-- element positions in canvas px (to compare with the art spec)
out.elements = {}
local card = gui:FindFirstChild('Card')
for _, d in card:GetDescendants() do
  if d:IsA('GuiObject') then
    local a = d.AbsolutePosition - gui.AbsolutePosition
    out.elements[d.Name] = {x = d.Position.X.Offset, y = d.Position.Y.Offset, w = d.Size.X.Offset, h = d.Size.Y.Offset,
      text = (d:IsA('TextLabel') or d:IsA('TextButton')) and d.Text or nil, textSize = (d:IsA('TextLabel') or d:IsA('TextButton')) and d.TextSize or nil,
      fits = (d:IsA('TextLabel') or d:IsA('TextButton')) and d.TextFits or nil, image = d:IsA('ImageLabel') and d.Image or nil}
  end
end
return HS:JSONEncode(out)
"""

VALUES = r"""
local HS = game:GetService('HttpService')
local pl = game.Players.LocalPlayer
local hook = pl.PlayerScripts:WaitForChild('GolfPointerDebug')
local w = hook:Invoke('state').wrist
local out = {card = {hole = w.hole, name = w.name, par = w.par, stroke = w.stroke, total = w.total, best = w.best}}
local a = {}
for k, v in pl:GetAttributes() do a[k] = typeof(v) == 'number' and v or tostring(v) end
out.attrs = a
local n = pl:GetAttribute('Hole') or 1
local hole = workspace.Course:FindFirstChild('Hole' .. n)
out.holeName = hole and hole:GetAttribute('HoleName')
out.holePar = hole and hole:GetAttribute('Par')
return HS:JSONEncode(out)
"""

# one real VR swing at the cup: club from behind the ball through it at `speed` studs/s along the aim
SWING = r"""
local HS = game:GetService('HttpService')
local RunService = game:GetService('RunService')
local pl = game.Players.LocalPlayer
local hook = pl.PlayerScripts:WaitForChild('GolfPointerDebug')
local speed, aimOff = %s, %s
local ball
for _, b in workspace:WaitForChild('Balls'):GetChildren() do if b:IsA('BasePart') then ball = b end end
local n = pl:GetAttribute('Hole') or 1
local hole = workspace.Course:FindFirstChild('Hole' .. n)
local cup
for _, d in hole:GetDescendants() do
  if d:IsA('BasePart') and (d.Name == 'Cup' or d.Name == 'CupPlate' or d.Name == 'CupLiner') then cup = cup or d end
end
local bp = ball.Position
local target = cup and cup.Position or (bp + Vector3.new(0, 0, -5))
local dir = Vector3.new(target.X - bp.X, 0, target.Z - bp.Z).Unit
dir = CFrame.fromAxisAngle(Vector3.yAxis, math.rad(aimOff)):VectorToWorldSpace(dir)
local right = dir:Cross(Vector3.yAxis)
local r = ball.Size.Y / 2
local y = bp.Y - r + 0.3
local head = Vector3.new(bp.X, bp.Y + 5.0, bp.Z) - right * 1.8 - dir * 0.3
local strokes0 = pl:GetAttribute('Strokes') or 0
local start = Vector3.new(bp.X, y, bp.Z) - dir * 1.6
hook:Invoke('pose', {head = {head.X, head.Y, head.Z}, look = {bp.X, bp.Y, bp.Z}, club = {start.X, start.Y, start.Z}, face = {dir.X, dir.Y, dir.Z}})
for _ = 1, 20 do RunService.RenderStepped:Wait() end
local t0 = os.clock()
while os.clock() - t0 < 1.6 / speed + 0.6 do
  local d = math.min((os.clock() - t0) * speed, 2.6)
  local p = start + dir * d
  hook:Invoke('pose', {head = {head.X, head.Y, head.Z}, look = {bp.X, bp.Y, bp.Z}, club = {p.X, p.Y, p.Z}, face = {dir.X, dir.Y, dir.Z}})
  RunService.RenderStepped:Wait()
end
-- park the club at the player's side, away from the ball
local park = Vector3.new(head.X, y, head.Z) - right * 1.0
hook:Invoke('pose', {club = {park.X, park.Y, park.Z}, face = {dir.X, dir.Y, dir.Z}})
local hit = false
local tw = os.clock()
while os.clock() - tw < 2 do
  if (ball.AssemblyLinearVelocity.Magnitude > 0.5) or (pl:GetAttribute('Strokes') or 0) ~= strokes0 then hit = true break end
  task.wait(0.05)
end
-- wait for the ball to stop (or the hole to change)
local t1 = os.clock()
while os.clock() - t1 < 25 do
  task.wait(0.25)
  local b2
  for _, b in workspace.Balls:GetChildren() do if b:IsA('BasePart') then b2 = b end end
  if (pl:GetAttribute('Hole') or 1) ~= n then break end
  if b2 and b2.AssemblyLinearVelocity.Magnitude < 0.05 and os.clock() - t1 > 1 then break end
end
task.wait(1.0)
return HS:JSONEncode({hit = hit, hole = n, holeAfter = pl:GetAttribute('Hole'), strokesBefore = strokes0, strokesAfter = pl:GetAttribute('Strokes'), ballFrom = {bp.X, bp.Y, bp.Z}, cup = cup and cup:GetFullName(), dist = (target - bp).Magnitude})
"""


def values(st):
    return json.loads(st.luau(VALUES, "Client"))


def segs_for(rng):
    D = lambda d=1.0: {"name": "down", "kind": "down", "dur": d, "expect": "none"}
    out = []
    for rep in range(3):
        for d in [0.08, 0.12, 0.15, 0.2, 0.22]:
            out += [{"name": "glance_%.2fs" % d, "kind": "watch", "dur": d, "expect": "none"}, D(0.8)]
        for d in [0.25, 0.28]:
            out += [{"name": "glance_%.2fs" % d, "kind": "watch", "dur": d, "expect": "either"}, D(0.8)]
        for d in [0.35, 0.5, 1.0, 2.0]:
            out += [{"name": "look_%.2fs" % d, "kind": "watch", "dur": d, "expect": "show"}, D(1.0)]
    for tilt in [0, 10, 20, -10, -20]:
        out += [{"name": "tilt_%d" % tilt, "kind": "watch", "tilt": tilt, "dur": 1.0, "expect": "show"}, D()]
    for tilt in [30, -30]:
        out += [{"name": "tilt_%d" % tilt, "kind": "watch", "tilt": tilt, "dur": 1.0, "expect": "either"}, D()]
    for tilt in [45, 60, 90, -45, -60, -90]:
        out += [{"name": "tilt_%d" % tilt, "kind": "watch", "tilt": tilt, "dur": 1.0, "expect": "none"}, D()]
    for g in [0, 10, 18]:
        out += [{"name": "gaze_off_%d" % g, "kind": "lookat", "gazeOff": g, "dur": 1.0, "expect": "show"}, D()]
    for g in [22, 27, -22]:
        out += [{"name": "gaze_off_%d" % g, "kind": "lookat", "gazeOff": g, "dur": 1.0, "expect": "either"}, D()]
    for g in [32, 45, 70, -35, -60]:
        out += [{"name": "gaze_off_%d" % g, "kind": "lookat", "gazeOff": g, "dur": 1.0, "expect": "none"}, D()]
    for y in [40, 60, -40, -60]:
        out += [{"name": "wrist_aside_%d" % y, "kind": "watch", "wristYaw": y, "dur": 1.0, "expect": "none"}, D()]
    for sp in [3.5, 5, 7, 9]:
        out += [{"name": "swing_%.1f" % sp, "kind": "swing", "speed": sp, "dur": 1.6, "expect": "none"}, D()]
    out += [{"name": "waggle_slow_2.0", "kind": "swing", "speed": 2.0, "amp": 0.4, "dur": 1.6, "expect": "either"}, D()]
    for bk in [0.6, 1.0, 1.4]:
        out += [{"name": "putt_lineup_look_wrist_back%.1f" % bk, "kind": "stance", "back": bk, "lookWrist": True, "dur": 1.5, "expect": "none"}, D()]
    # 30 s looking around: random head, off hand hanging / beside / tipped watch poses, with 6 real looks mixed in
    t, looks = 0, 0
    while t < 30:
        r = rng.random()
        d = rng.uniform(0.5, 1.6)
        if r < 0.15 and looks < 6:
            out += [{"name": "random_look", "kind": "watch", "dur": d + 0.4, "expect": "show"}]
            looks += 1
        elif r < 0.45:
            out += [{"name": "random_aside", "kind": "watch", "wristYaw": rng.choice([-1, 1]) * rng.uniform(38, 70), "yaw": rng.uniform(-60, 60), "pitch": rng.uniform(-50, 20), "dur": d, "expect": "none"}]
        elif r < 0.7:
            out += [{"name": "random_tipped", "kind": "watch", "tilt": rng.choice([-1, 1]) * rng.uniform(45, 80), "dur": d, "expect": "none"}]
        else:
            out += [{"name": "random_down", "kind": "down", "yaw": rng.uniform(-80, 80), "pitch": rng.uniform(-60, 25), "dur": d, "expect": "none"}]
        out += [D(0.7)]
        t += d + 0.7
    return out


def run_segs(st, segs, offhand):
    code = open(os.path.join(HERE, "wrist_seq.luau")).read()
    res = []
    # chunks of <= ~40 s
    chunk, dur = [], 0
    chunks = []
    for s in segs:
        chunk.append(s)
        dur += s["dur"]
        if dur > 35 and s["kind"] == "down":
            chunks.append(chunk)
            chunk, dur = [], 0
    if chunk:
        chunks.append(chunk)
    for c in chunks:
        st.luau(LEVEL_HEAD, "Client")
        lua = code.replace("SEGMENTS", json.dumps(json.dumps(c))).replace("OFFHAND", json.dumps(offhand))
        r = st.luau(lua, "Client", timeout=180)
        try:
            res += json.loads(r)
        except ValueError:
            print("SEQ ERROR", r[:500])
            res.append({"error": r[:500]})
    return res


def score(rows):
    fs = [r for r in rows if r.get("expect") == "none" and r.get("shows", 0) > 0]
    ms = [r for r in rows if r.get("expect") == "show" and r.get("shows", 0) == 0]
    lat = [r["firstShowMs"] for r in rows if r.get("expect") == "show" and r.get("firstShowMs") is not None]
    either = [(r["name"], r["shows"]) for r in rows if r.get("expect") == "either"]
    return {"segments": len(rows), "expect_none": sum(r.get("expect") == "none" for r in rows),
            "expect_show": sum(r.get("expect") == "show" for r in rows), "false_shows": len(fs), "misses": len(ms),
            "false_list": [(r["name"], r.get("minFaceDeg"), r.get("minGazeDeg"), r.get("blocked")) for r in fs],
            "miss_list": [(r["name"], r.get("minFaceDeg"), r.get("minGazeDeg"), r.get("blocked")) for r in ms],
            "latency_ms": {"min": min(lat) if lat else None, "max": max(lat) if lat else None, "mean": round(sum(lat) / len(lat)) if lat else None},
            "borderline": either}


def zoom_shot(st, path):
    st.luau(LOOK_AT_CARD, "Client")
    time.sleep(0.3)
    st.luau("workspace.CurrentCamera.FieldOfView = 22 return 'ok'", "Client")
    time.sleep(0.5)
    g = json.loads(st.luau(GEOM, "Client"))
    capture(st, path)
    st.luau("workspace.CurrentCamera.FieldOfView = 70 return 'ok'", "Client")
    return g


def click(st, name, hand="RightHand", wrist=False):
    if wrist:
        pointer(st, "wrist", True)
        time.sleep(1.0)
    t = next((t for t in pointer(st, "targets") or [] if t["name"] == name), None)
    if not t:
        return {"button": name, "error": "missing"}
    pointer(st, "aim", {"hand": hand, "point": t["world"]})
    time.sleep(0.4)
    hov = pointer(st, "state")["pointer"]
    pointer(st, "trigger", hand)
    time.sleep(0.9)
    if wrist:
        pointer(st, "wrist", False)
        time.sleep(0.6)
    m = menu(st, "state")
    m = json.loads(m) if isinstance(m, str) else m
    card = st.luau("local g = game.Players.LocalPlayer.PlayerGui:FindFirstChild('VRScorecard') return g and g.Enabled or false", "Client")
    return {"button": name, "text": t.get("text"), "hovered": hov.get("button"), "page": "scorecard" if card in (True, "true") else m.get("page")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--strokes", type=int, default=10)
    ap.add_argument("--skip-seq", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    st = Studio()
    st.stop_play()
    set_edit_attrs(st, {"GolfTestMode": False, "SimulateVR": True})
    res = {}
    try:
        st.start_play()
        time.sleep(12)
        st.luau(LEVEL_HEAD, "Client")
        time.sleep(0.5)
        res["close_title"] = [click(st, "Play"), click(st, "PlayCourse")]
        print("close", res["close_title"])
        time.sleep(2)
        # -- tee values + layout, right-handed (card on the left wrist)
        st.luau(LEVEL_HEAD, "Client")
        res["tee_down"] = pointer(st, "state")["wrist"]
        capture(st, os.path.join(args.out, "c2_h1_tee_normalplay_wristdown.png"))
        pointer(st, "wrist", True)
        time.sleep(1.2)
        res["tee_values"] = values(st)
        capture(st, os.path.join(args.out, "c2_h1_tee_leftwrist_up.png"))
        res["geom_left"] = zoom_shot(st, os.path.join(args.out, "c2_h1_tee_leftwrist_zoom_fov22.png"))
        print("geom", json.dumps({k: v for k, v in res["geom_left"].items() if k != "elements"}))
        pointer(st, "wrist", False)
        time.sleep(1.0)
        st.luau(LEVEL_HEAD, "Client")
        # -- real strokes
        res["strokes"] = []
        rng = random.Random(5)
        for i in range(args.strokes):
            sp = rng.uniform(3.0, 5.0)
            r = json.loads(st.luau(SWING % (repr(round(sp, 2)), repr(round(rng.uniform(-3, 3), 1))), "Client", timeout=90))
            st.luau(LEVEL_HEAD, "Client")
            pointer(st, "wrist", True)
            time.sleep(1.2)
            v = values(st)
            r["values"] = v
            a = v["attrs"]
            r["card_matches"] = (v["card"]["stroke"] == str(a.get("Strokes", 0)) and v["card"]["hole"] == "HOLE %s" % a.get("Hole", 1)
                                 and v["card"]["par"] == str(v["holePar"]) and v["card"]["name"] == (v["holeName"] or ""))
            shot = "c2_h%s_stroke%s_leftwrist_up.png" % (a.get("Hole", 1), a.get("Strokes", 0))
            capture(st, os.path.join(args.out, shot))
            r["shot"] = shot
            pointer(st, "wrist", False)
            time.sleep(0.8)
            res["strokes"].append(r)
            print("stroke", i, json.dumps({k: r[k] for k in ("hit", "hole", "holeAfter", "strokesBefore", "strokesAfter", "card_matches")}), v["card"])
            if (a.get("Hole") or 1) >= 3:
                break
        # -- best: the Studio PB store is offline (in memory); publish a best the way PersonalBest.publish does
        st.luau("for _, p in game.Players:GetPlayers() do p:SetAttribute('Best_lantern_grove', 25) end return 'ok'", "Server")
        time.sleep(1.0)
        pointer(st, "wrist", True)
        time.sleep(1.2)
        res["best_values"] = values(st)
        res["geom_best"] = zoom_shot(st, os.path.join(args.out, "c2_best25_leftwrist_zoom_fov22.png"))
        pointer(st, "wrist", False)
        time.sleep(0.8)
        st.luau("for _, p in game.Players:GetPlayers() do p:SetAttribute('Best_lantern_grove', nil) end return 'ok'", "Server")
        print("best", res["best_values"]["card"])
        # -- wrist buttons mid-round
        st.luau(LEVEL_HEAD, "Client")
        res["buttons"] = [click(st, "WristMenu", wrist=True)]
        res["buttons"].append(click(st, "Resume"))
        res["buttons"].append(click(st, "WristScores", wrist=True))
        capture(st, os.path.join(args.out, "c2_scorecard_from_wrist.png"))
        res["buttons"].append(click(st, "Close", "LeftHand"))
        res["strokes_after_buttons"] = values(st)["attrs"].get("Strokes")
        print("buttons", res["buttons"])
        # -- sequences, right-handed
        if not args.skip_seq:
            rows = run_segs(st, segs_for(random.Random(11)), "LeftHand")
            res["seq_right_handed"] = {"score": score(rows), "rows": rows}
            print("seq RH", json.dumps(res["seq_right_handed"]["score"]))
        # -- left-handed: Settings > Left through the pointer, then the card on the right wrist
        st.luau(LEVEL_HEAD, "Client")
        res["to_left"] = [click(st, "WristMenu", wrist=True), click(st, "Settings"), click(st, "HandLeft"), click(st, "Back"), click(st, "Resume")]
        print("to left", res["to_left"])
        st.luau(LEVEL_HEAD, "Client")
        pointer(st, "wrist", True)
        time.sleep(1.2)
        res["right_wrist_state"] = pointer(st, "state")["wrist"]
        capture(st, os.path.join(args.out, "c2_rightwrist_up_lefthanded.png"))
        res["geom_right"] = zoom_shot(st, os.path.join(args.out, "c2_rightwrist_zoom_fov22_lefthanded.png"))
        pointer(st, "wrist", False)
        time.sleep(1.0)
        if not args.skip_seq:
            rows = run_segs(st, segs_for(random.Random(12)), "RightHand")
            res["seq_left_handed"] = {"score": score(rows), "rows": rows}
            print("seq LH", json.dumps(res["seq_left_handed"]["score"]))
        st.luau(LEVEL_HEAD, "Client")
        res["to_right"] = [click(st, "WristMenu", wrist=True), click(st, "Settings"), click(st, "HandRight"), click(st, "Back"), click(st, "Resume")]
        res["console"] = {"server": st.problems("Server"), "client": st.problems("Client")}
        print("console", json.dumps(res["console"]))
    finally:
        with open(os.path.join(args.out, "wrist.json"), "w") as fh:
            json.dump(res, fh, indent=1)
        st.stop_play()
        set_edit_attrs(st, {"SimulateVR": False})


if __name__ == "__main__":
    main()
