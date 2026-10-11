#!/usr/bin/env python3
"""Golf camera near walls: replay Playtest Bot's round-3 camera probe spots through the real camera code.

  python3 tools/camprobe.py [--spots playtests/round3/camprobe.json] [--out playtests/stage-m/camprobe]

For every spot (ball 0.6 off a wall) the putting camera orbits the ball in 12 yaw steps (dist 6, pitch 30, as
TouchControls). Each pose goes through CameraOcclusion.passThrough (only Terrain moves the camera) and
CameraOcclusion.occluders (what the client fades to LocalTransparencyModifier 0.7). Then ray grids check what's
left in front of the ball:
  ballHidden  the sight line to the ball is blocked by an opaque, unfaded part (felt included)
  fill        share of a 7x7 ray grid over +-12 x +-9 degrees around the ball that hits an opaque, unfaded, non-felt
              part closer than the ball (wideShare: the same over +-35 x +-21 degrees, info only)
A pose is bad ("a wall fills the view") if ballHidden or fill > 0.4. Runs in a normal Play session (test mode off).
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_playtests import Studio, GAME_DIR, log, set_edit_attrs  # noqa: E402

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
    if skip[p] or p.Transparency >= 0.5 then
      table.insert(f, p)
    else
      return h
    end
  end
  return nil
end
local out = {}
local pitch = math.rad(30)
for _, s in spots do
  local focus = Vector3.new(s.pos[1], s.pos[2], s.pos[3]) + Vector3.new(0, 0.25, 0)
  local worst = { fill = -1 }
  local bad = 0
  for k = 0, 11 do
    local yaw = math.rad(k * 30)
    local rot = CFrame.fromEulerAnglesYXZ(-pitch, yaw, 0)
    local desired = focus - rot.LookVector * 6
    local cam = CO.passThrough(focus, desired)
    local occ = CO.occluders(cam, focus, { char })
    local nOcc = 0
    for _ in occ do nOcc += 1 end
    local toF = focus - cam
    local d = toF.Magnitude
    local hid = opaqueHit(cam, toF.Unit * math.max(d - 0.15, 0.05), occ)
    local look = CFrame.lookAt(cam, focus)
    local function grid(ni, nj, hStep, vStep, names)
      local hitN, n = 0, 0
      for i = -ni, ni do
        for j = -nj, nj do
          local dir = (look * CFrame.Angles(math.rad(j * vStep), math.rad(-i * hStep), 0)).LookVector
          n += 1
          local h = opaqueHit(cam, dir * d, occ)
          if h and not felt[h.Instance] and not h.Instance:IsA('Terrain') then
            hitN += 1
            if names then
              local nm = h.Instance.Parent.Name .. '/' .. h.Instance.Name
              names[nm] = (names[nm] or 0) + 1
            end
          end
        end
      end
      return hitN / n
    end
    local names = {}
    local fill = grid(3, 3, 4, 3, names) -- the ball's surroundings: +-12 x +-9 degrees
    local wide = grid(4, 4, 35 / 4, 21 / 4) -- most of the view (info only)
    local isBad = (hid ~= nil) or fill > 0.4
    if isBad then bad += 1 end
    local score = (hid and 1 or 0) + fill
    if score > worst.fill then
      worst = { fill = score, yaw = k * 30, ballHidden = hid and hid.Instance:GetFullName() or nil, fillShare = math.floor(fill * 100) / 100, wideShare = math.floor(wide * 100) / 100,
        camMoved = math.floor((cam - desired).Magnitude * 100) / 100, faded = nOcc, hits = names }
    end
  end
  table.insert(out, { hole = s.hole, pos = s.pos, bad = bad, worst = worst })
  task.wait()
end
return game:GetService('HttpService'):JSONEncode(out)
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spots", default=os.path.join(GAME_DIR, "playtests", "round3", "camprobe.json"))
    ap.add_argument("--out", default=os.path.join(GAME_DIR, "playtests", "stage-m", "camprobe"))
    ap.add_argument("--holes", default="1,2,3,4,5,6,7,8,9")
    a = ap.parse_args()
    spots = json.load(open(a.spots))["spots"]
    os.makedirs(a.out, exist_ok=True)
    st = Studio()
    st.stop_play()
    set_edit_attrs(st, {"GolfTestMode": False, "SimulateVR": False, "SkipMenu": True})
    st.start_play()
    import time
    time.sleep(8)
    results = []
    try:
        for hole in [int(x) for x in a.holes.split(",")]:
            hs = [{"hole": s["hole"], "pos": s["pos"]} for s in spots if s["hole"] == hole]
            r = st.luau(PROBE % json.dumps(json.dumps(hs)), "Client", timeout=600)
            try:
                rows = json.loads(r)
            except ValueError:
                log("hole", hole, "probe failed:", r[:400])
                continue
            bad = sum(1 for x in rows if x["bad"] > 0)
            poses = sum(x["bad"] for x in rows)
            log("hole %d: %d spots, %d with a bad pose (%d of %d poses)" % (hole, len(rows), bad, poses, 12 * len(rows)))
            results.extend(rows)
    finally:
        st.stop_play()
        set_edit_attrs(st, {"SkipMenu": None})
    json.dump(results, open(os.path.join(a.out, "camprobe_after.json"), "w"), indent=1)
    lines = ["# Camera probe (round-3 spots, pass-through + see-through camera)", "",
             "| Hole | Spots | Spots with a bad pose | Bad poses / all |", "|---|---|---|---|"]
    for hole in sorted({x["hole"] for x in results}):
        rows = [x for x in results if x["hole"] == hole]
        lines.append("| %d | %d | %d | %d / %d |" % (hole, len(rows), sum(1 for x in rows if x["bad"]), sum(x["bad"] for x in rows), 12 * len(rows)))
    tot = len(results)
    lines.append("| all | %d | %d | %d / %d |" % (tot, sum(1 for x in results if x["bad"]), sum(x["bad"] for x in results), 12 * tot))
    worst = sorted(results, key=lambda x: -x["worst"]["fill"])[:15]
    lines += ["", "Worst spots:", ""] + ["- H%d %s yaw %s: %s" % (x["hole"], x["pos"], x["worst"]["yaw"], json.dumps(x["worst"])) for x in worst]
    open(os.path.join(a.out, "summary.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
