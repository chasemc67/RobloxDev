#!/usr/bin/env python3
"""Round 5 check 3: camera wall probe over the round-3 spots (483 x 12 yaws), flat golf camera AND VR head.
Flat: same as tools/camprobe.py (dist 6, pitch 30, CameraOcclusion.passThrough + occluders), plus per-pose camera
distance and fill stats. VR: the eye 5.0 studs over the felt beside the ball (1.8 studs = addressing it, 4.0 = standing
back) at the same 12 yaws, no pass-through (a head can be anywhere), faded set = CameraOcclusion.occluders(eye, ball)
(what VRControls' updateSeeThrough fades via CameraOcclusion.fade). Bad = ball hidden by an opaque unfaded part or
fill > 0.4 over the +-12 x +-9 deg grid.
  python3 playtests/round5/scripts/r5_camprobe.py --out playtests/round5/camprobe
"""
import argparse, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "tools")))
from run_playtests import Studio, set_edit_attrs, GAME_DIR, log  # noqa: E402

PROBE = r"""
local spots = game:GetService('HttpService'):JSONDecode(%s)
local RS = game:GetService('ReplicatedStorage')
local CO = require(RS.Golf.CameraOcclusion)
local CS = game:GetService('CollectionService')
local me = game:GetService('Players').LocalPlayer
local char = me.Character
local felt = {}
for _, p in CS:GetTagged('GolfSurface') do felt[p] = true end
local rp = RaycastParams.new()
rp.FilterType = Enum.RaycastFilterType.Exclude
rp.CollisionGroup = CO.CAMERA_GROUP
rp.IgnoreWater = true
local base = { workspace.CurrentCamera, char, workspace:FindFirstChild('Balls') }
local function opaqueHit(from, dir, skip)
  local f = table.clone(base)
  for _ = 1, 24 do
    rp.FilterDescendantsInstances = f
    local h = workspace:Raycast(from, dir, rp)
    if not h then return nil end
    local p = h.Instance
    if p:IsA('Terrain') then return h end
    if skip[p] or p.Transparency >= 0.5 then table.insert(f, p) else return h end
  end
  return nil
end
local function evalPose(cam, focus)
  local occ = CO.occluders(cam, focus, { char })
  local nOcc = 0
  for _ in occ do nOcc += 1 end
  local toF = focus - cam
  local d = toF.Magnitude
  local hid = opaqueHit(cam, toF.Unit * math.max(d - 0.15, 0.05), occ)
  local look = CFrame.lookAt(cam, focus)
  local hitN, n, names = 0, 0, {}
  for i = -3, 3 do for j = -3, 3 do
    local dir = (look * CFrame.Angles(math.rad(j * 3), math.rad(-i * 4), 0)).LookVector
    n += 1
    local h = opaqueHit(cam, dir * d, occ)
    if h and not felt[h.Instance] and not h.Instance:IsA('Terrain') then
      hitN += 1
      local nm = h.Instance.Parent.Name .. '/' .. h.Instance.Name
      names[nm] = (names[nm] or 0) + 1
    end
  end end
  local fill = hitN / n
  return { d = d, fill = fill, hid = hid and hid.Instance:GetFullName() or nil, faded = nOcc, bad = (hid ~= nil) or fill > 0.4, names = names }
end
local out = {}
local pitch = math.rad(30)
for _, s in spots do
  local focus = Vector3.new(s.pos[1], s.pos[2], s.pos[3]) + Vector3.new(0, 0.25, 0)
  local flat = { bad = 0, minD = 99, maxFill = 0, sumFill = 0, maxFaded = 0, sumFaded = 0, worst = nil }
  local vr = { bad = 0, maxFill = 0, sumFill = 0, maxFaded = 0, sumFaded = 0, worst = nil, n = 0 }
  for k = 0, 11 do
    local yaw = math.rad(k * 30)
    local rot = CFrame.fromEulerAnglesYXZ(-pitch, yaw, 0)
    local desired = focus - rot.LookVector * 6
    local cam = CO.passThrough(focus, desired)
    local r = evalPose(cam, focus)
    flat.minD = math.min(flat.minD, r.d)
    flat.maxFill = math.max(flat.maxFill, r.fill); flat.sumFill += r.fill
    flat.maxFaded = math.max(flat.maxFaded, r.faded); flat.sumFaded += r.faded
    if r.bad then flat.bad += 1 end
    if not flat.worst or (r.hid and 1 or 0) + r.fill > flat.worst.score then
      flat.worst = { score = (r.hid and 1 or 0) + r.fill, yaw = k * 30, fill = math.floor(r.fill * 100) / 100, hid = r.hid, faded = r.faded, d = math.floor(r.d * 100) / 100, names = r.names }
    end
    for _, back in { 1.8, 4.0 } do
      local horiz = Vector3.new(-math.sin(yaw), 0, -math.cos(yaw)) * back
      local eye = Vector3.new(focus.X, s.pos[2] - 0.15 + 5.0, focus.Z) + horiz
      local v = evalPose(eye, focus)
      vr.n += 1
      vr.maxFill = math.max(vr.maxFill, v.fill); vr.sumFill += v.fill
      vr.maxFaded = math.max(vr.maxFaded, v.faded); vr.sumFaded += v.faded
      if v.bad then vr.bad += 1 end
      if not vr.worst or (v.hid and 1 or 0) + v.fill > vr.worst.score then
        vr.worst = { score = (v.hid and 1 or 0) + v.fill, yaw = k * 30, back = back, fill = math.floor(v.fill * 100) / 100, hid = v.hid, faded = v.faded, names = v.names, eye = { eye.X, eye.Y, eye.Z } }
      end
    end
  end
  flat.meanFill = flat.sumFill / 12; flat.meanFaded = flat.sumFaded / 12
  vr.meanFill = vr.sumFill / vr.n; vr.meanFaded = vr.sumFaded / vr.n
  table.insert(out, { hole = s.hole, pos = s.pos, flat = flat, vr = vr })
  task.wait()
end
return game:GetService('HttpService'):JSONEncode(out)
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spots", default=os.path.join(GAME_DIR, "playtests", "round3", "camprobe.json"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--holes", default="1,2,3,4,5,6,7,8,9")
    a = ap.parse_args()
    spots = json.load(open(a.spots))["spots"]
    os.makedirs(a.out, exist_ok=True)
    st = Studio()
    st.stop_play()
    set_edit_attrs(st, {"GolfTestMode": False, "SimulateVR": False, "SkipMenu": True})
    results = []
    try:
        st.start_play()
        time.sleep(8)
        for hole in [int(x) for x in a.holes.split(",")]:
            hs = [{"hole": s["hole"], "pos": s["pos"]} for s in spots if s["hole"] == hole]
            for i in range(0, len(hs), 30):
                r = st.luau(PROBE % json.dumps(json.dumps(hs[i:i + 30])), "Client", timeout=600)
                try:
                    results.extend(json.loads(r))
                except ValueError:
                    log("hole", hole, "probe failed:", r[:400])
            rows = [x for x in results if x["hole"] == hole]
            log("hole %d: %d spots, flat bad poses %d, vr bad poses %d" % (hole, len(rows), sum(x["flat"]["bad"] for x in rows), sum(x["vr"]["bad"] for x in rows)))
        problems = {"server": st.problems("Server"), "client": st.problems("Client")}
    finally:
        st.stop_play()
        set_edit_attrs(st, {"SkipMenu": None})
    json.dump({"spots": results, "console": problems}, open(os.path.join(a.out, "camprobe_r5.json"), "w"), indent=1)
    L = ["# Round 5 camera probe (round-3 spots), flat golf camera + VR head", "",
         "| Hole | Spots | Flat bad poses / all | Flat min cam dist | Flat max fill | Flat mean fill | Flat faded mean / max | VR bad poses / all | VR max fill | VR mean fill | VR faded mean / max |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    def row(name, rows):
        n = len(rows)
        return "| %s | %d | %d / %d | %.2f | %.2f | %.3f | %.1f / %d | %d / %d | %.2f | %.3f | %.1f / %d |" % (
            name, n, sum(x["flat"]["bad"] for x in rows), 12 * n, min(x["flat"]["minD"] for x in rows), max(x["flat"]["maxFill"] for x in rows),
            sum(x["flat"]["meanFill"] for x in rows) / n, sum(x["flat"]["meanFaded"] for x in rows) / n, max(x["flat"]["maxFaded"] for x in rows),
            sum(x["vr"]["bad"] for x in rows), 24 * n, max(x["vr"]["maxFill"] for x in rows), sum(x["vr"]["meanFill"] for x in rows) / n,
            sum(x["vr"]["meanFaded"] for x in rows) / n, max(x["vr"]["maxFaded"] for x in rows))
    for hole in sorted({x["hole"] for x in results}):
        L.append(row(str(hole), [x for x in results if x["hole"] == hole]))
    L.append(row("all", results))
    L += ["", "Worst flat:", ""] + ["- H%d %s %s" % (x["hole"], x["pos"], json.dumps(x["flat"]["worst"])) for x in sorted(results, key=lambda x: -x["flat"]["worst"]["score"])[:10]]
    L += ["", "Worst VR:", ""] + ["- H%d %s %s" % (x["hole"], x["pos"], json.dumps(x["vr"]["worst"])) for x in sorted(results, key=lambda x: -x["vr"]["worst"]["score"])[:15]]
    L += ["", "Console: " + json.dumps(problems)]
    open(os.path.join(a.out, "summary.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
