#!/usr/bin/env python3
"""Round 6 check 5: Edit-mode screen_capture of each >= 25 deg plain bank (FeltPattern PlainBank) from the lane side,
plus a per-bank pixel sample: bank face vs the flat felt beside it (projected with the capture camera). Read-only."""
import base64, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "tools")))
import run_playtests as rp  # noqa: E402
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
st = rp.Studio()
LIST = r"""
local out = {}
for _, p in workspace.Course:GetDescendants() do
  if p:IsA('BasePart') and p:GetAttribute('FeltPattern') == 'PlainBank' then
    local n = p.CFrame.UpVector
    local nh = Vector3.new(n.X, 0, n.Z).Unit
    local top = p.Position + n * p.Size.Y / 2
    -- the flat felt the bank's foot meets: ray down just past the foot, out along nh
    local foot = top + nh * 1.6 + Vector3.new(0, 2, 0)
    local best, bd
    for _, q in workspace.Course:GetDescendants() do
      if q:IsA('BasePart') and q.Name == 'Felt' and q ~= p and (q:GetAttribute('SlopeDeg') or 0) == 0 then
        local lp = q.CFrame:PointToObjectSpace(foot)
        if math.abs(lp.X) <= q.Size.X / 2 and math.abs(lp.Z) <= q.Size.Z / 2 then
          local d = math.abs(lp.Y) if not bd or d < bd then best, bd = q, d end
        end
      end
    end
    local hole = p:FindFirstAncestorWhichIsA('Model') while hole and not hole.Name:match('^Hole%d+$') do hole = hole.Parent end
    local fp = best and (best.Position + Vector3.new(0, best.Size.Y / 2, 0)) or nil
    table.insert(out, {hole = hole.Name, top = {top.X, top.Y, top.Z}, nh = {nh.X, nh.Z}, bank = p.Color:ToHex(),
      flat = best and best.Color:ToHex() or nil, flatTop = fp and {foot.X, fp.Y, foot.Z} or nil, textures = #p:GetChildren()})
  end
end
return game:GetService('HttpService'):JSONEncode(out)"""
items = json.loads(st.luau(LIST, "Edit"))
for i, it in enumerate(items):
    t, nh = it["top"], it["nh"]
    cam = [t[0] + nh[0] * 7, t[1] + 5, t[2] + nh[1] * 7]
    look = [t[0], t[1] - 0.3, t[2]]
    r = st.m.req("tools/call", {"name": "screen_capture", "arguments": {"studio_id": st.id, "capture_id": "bank_%d" % i, "camera_position": cam, "look_at_position": look}})
    img = [x for x in r["result"]["content"] if x.get("type") == "image"][0]
    name = "bank_%s_%d.png" % (it["hole"].lower(), i)
    tmp = os.path.join(out, name + ".jpg")
    open(tmp, "wb").write(base64.b64decode(img["data"]))
    subprocess.run(["uv", "run", "-q", "--with", "pillow", "python", "-c", "import sys; from PIL import Image; Image.open(sys.argv[1]).save(sys.argv[2])", tmp, os.path.join(out, name)], check=True)
    os.remove(tmp)
    it["shot"], it["cam"] = name, cam
    def lum(h):
        r_, g, b = (int(h[k:k + 2], 16) for k in (0, 2, 4))
        return 0.2126 * r_ + 0.7152 * g + 0.0722 * b
    it["lumRatioVsFlat"] = round(lum(it["bank"]) / lum(it["flat"]), 3) if it.get("flat") else None
    print(json.dumps(it), flush=True)
json.dump(items, open(os.path.join(out, "banks.json"), "w"), indent=1)
