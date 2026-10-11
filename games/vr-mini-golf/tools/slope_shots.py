"""Top-down check of every sloped felt piece (SlopeFelt Texture): an Edit-mode MCP screen_capture from above the
piece (world up, offset uphill), so downhill runs up the image. The bright arrow tips must point up
(away from the camera). Writes <out>/h<N>_<i>_<deg>deg_<key>.png, slopes.json and contact.png.

usage: python3 tools/slope_shots.py [--out playtests/stage-n/slopes] [--height 7]
"""
import argparse, base64, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_playtests as rp  # noqa: E402

# Hide (LocalTransparencyModifier 1, not saved) every part between the camera and a 7x7 grid on the slope's top face.
HIDE = """local cam, part = Vector3.new(%s), nil
for _, t in workspace.Course:GetDescendants() do
  if t:IsA('Texture') and t.Name == 'SlopeFelt' and (t.Parent.Position - Vector3.new(%s)).Magnitude < 0.01 then part = t.Parent end
end
local hidden = {}
_G.SlopeShotHidden = hidden
local top = part.CFrame * CFrame.new(0, part.Size.Y / 2, 0)
local targets = {}
for i = -3, 3 do for j = -3, 3 do
  table.insert(targets, (top * CFrame.new(part.Size.X * i / 7.5, 0.02, part.Size.Z * j / 7.5)).Position)
end end
local reach = (top.Position - cam).Magnitude + part.Size.Magnitude
-- segment vs oriented box (slab test in the part's space; CanQuery is off on Edit-mode decor, so no raycasts)
local function hits(p, a, b)
  local h = p.Size / 2
  local la, lb = p.CFrame:PointToObjectSpace(a), p.CFrame:PointToObjectSpace(b)
  local d = lb - la
  local t0, t1 = 0, 0.98
  for _, ax in {'X', 'Y', 'Z'} do
    local o, v, e = la[ax], d[ax], h[ax]
    if math.abs(v) < 1e-9 then
      if o < -e or o > e then return false end
    else
      local u0, u1 = (-e - o) / v, (e - o) / v
      if u0 > u1 then u0, u1 = u1, u0 end
      t0, t1 = math.max(t0, u0), math.min(t1, u1)
      if t0 > t1 then return false end
    end
  end
  return true
end
for _, p in workspace:GetDescendants() do
  if p:IsA('BasePart') and p ~= part and p.Transparency < 1 and not p:IsA('Terrain')
     and (p.Position - cam).Magnitude < reach + p.Size.Magnitude then
    for _, tgt in targets do
      if hits(p, cam, tgt) then p.LocalTransparencyModifier = 1; table.insert(hidden, p); break end
    end
  end
end
return #hidden"""
UNHIDE = """for _, p in _G.SlopeShotHidden or {} do p.LocalTransparencyModifier = 0 end
_G.SlopeShotHidden = nil return 'ok'"""

LIST = """local HttpService = game:GetService('HttpService')
local out = {}
for _, t in workspace.Course:GetDescendants() do
  if t:IsA('Texture') and t.Name == 'SlopeFelt' then
    local p = t.Parent
    local n = p.CFrame.UpVector
    local down = (Vector3.new(0, -1, 0) + n * n.Y).Unit
    local c = p.Position + n * (p.Size.Y / 2)
    local hole = p:FindFirstAncestorWhichIsA('Model')
    while hole and not string.match(hole.Name, '^Hole%d+$') do hole = hole.Parent end
    local ld = p.CFrame:VectorToObjectSpace(down)
    -- which way the texture's +V (image down) runs on this part: Top face, +V = part -Z, turned per rotation suffix
    table.insert(out, {hole = hole and hole.Name or '?', name = p.Name, deg = p:GetAttribute('SlopeDeg'), tex = t.Texture,
      c = {c.X, c.Y, c.Z}, pos = {p.Position.X, p.Position.Y, p.Position.Z}, n = {n.X, n.Y, n.Z}, down = {down.X, down.Y, down.Z}, localDown = {ld.X, ld.Y, ld.Z},
      size = {p.Size.X, p.Size.Y, p.Size.Z}})
  end
end
return HttpService:JSONEncode(out)"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(rp.GAME_DIR, "playtests", "stage-n", "slopes"))
    ap.add_argument("--height", type=float, default=7.0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    st = rp.Studio()
    items = json.loads(st.luau(LIST, "Edit"))
    items.sort(key=lambda it: (int(it["hole"][4:]) if it["hole"][4:].isdigit() else 99, it["c"][0]))
    names = []
    for i, it in enumerate(items):
        c, n, d = it["c"], it["n"], it["down"]
        # world-up camera, offset uphill along the horizontal fall line (so steep banks are seen from their top edge)
        h = min(a.height, max(4.0, 0.7 * max(it["size"][0], it["size"][2])))
        dl = (d[0] ** 2 + d[2] ** 2) ** 0.5 or 1.0
        dh = [d[0] / dl, 0.0, d[2] / dl]
        cam = [c[0] - dh[0] * h * 0.35, c[1] + h, c[2] - dh[2] * h * 0.35]
        look = [c[k] + dh[k] * 0.3 for k in range(3)]
        it["hidden"] = st.luau(HIDE % (",".join("%.4f" % v for v in cam), ",".join("%.4f" % v for v in it["pos"])), "Edit")
        name = "h%s_%02d_%sdeg.png" % (it["hole"][4:], i, it["deg"])
        r = st.m.req("tools/call", {"name": "screen_capture", "arguments": {
            "studio_id": st.id, "capture_id": "slope_%d" % i, "camera_position": cam, "look_at_position": look}})
        img = [x for x in r["result"]["content"] if x.get("type") == "image"][0]
        tmp = os.path.join(a.out, name + ".jpg")
        with open(tmp, "wb") as fh:
            fh.write(base64.b64decode(img["data"]))
        subprocess.run(["uv", "run", "-q", "--with", "pillow", "python", "-c",
                        "import sys; from PIL import Image; Image.open(sys.argv[1]).save(sys.argv[2])", tmp,
                        os.path.join(a.out, name)], check=True, timeout=120)
        os.remove(tmp)
        st.luau(UNHIDE, "Edit")
        it["shot"], it["cam"], it["look"] = name, cam, look
        names.append(name)
        rp.log("shot", name)
    with open(os.path.join(a.out, "slopes.json"), "w") as fh:
        json.dump(items, fh, indent=1)
    # labelled contact sheet
    subprocess.run(["uv", "run", "-q", "--with", "pillow", "python", "-c", """
import sys, os
from PIL import Image, ImageDraw
d, names = sys.argv[1], sys.argv[2:]
W, H, cols = 480, 300, 4
rows = (len(names) + cols - 1) // cols
sheet = Image.new('RGB', (W * cols, H * rows), 'black')
for i, nm in enumerate(names):
    im = Image.open(os.path.join(d, nm)).convert('RGB'); im.thumbnail((W, H))
    x, y = (i % cols) * W, (i // cols) * H
    sheet.paste(im, (x, y)); ImageDraw.Draw(sheet).text((x + 6, y + 6), nm, fill='yellow')
sheet.save(os.path.join(d, 'contact.png'))
""", a.out] + names, check=True, timeout=120)
    rp.log("wrote", len(names), "shots + contact.png")


if __name__ == "__main__":
    main()
