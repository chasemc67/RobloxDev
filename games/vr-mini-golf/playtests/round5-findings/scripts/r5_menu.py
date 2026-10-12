#!/usr/bin/env python3
"""Round 5 check 1: VR menus with the simulated laser pointer, every button, both hands.

  python3 playtests/round5/scripts/r5_menu.py --out playtests/round5/vr-menu

SimulateVR, normal play (test mode off). The head is levelled. For each step the simulated controller (VRDebug
CFrameValue, through GolfPointerDebug "aim") is pointed at a button; VRPointer.update's own raycast must hover it
and show the HoverGlow round it; then the trigger (VRControls onButtonDown/Up with ButtonR2 / ButtonL2) must do the
button's job. GolfMenuDebug is only used to open the results page (it needs a finished round). The panel CFrame is
logged on every step (must not move between pages), and every visible text is scanned for a thumbstick hint.
"""
import argparse
import json
import os
import sys
import time

TOOLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools")
sys.path.insert(0, os.path.abspath(TOOLS))
from run_playtests import Studio, set_edit_attrs  # noqa: E402
from ui_shots import capture  # noqa: E402
from menu_shots import menu, pointer, RESULT  # noqa: E402

LEVEL = """local h = game.ReplicatedStorage:WaitForChild('VRDebug'):WaitForChild('Head')
local before = h.Value
local look = Vector3.new(before.LookVector.X, 0, before.LookVector.Z)
look = look.Magnitude > 0.01 and look.Unit or Vector3.new(0, 0, -1)
h.Value = CFrame.lookAt(before.Position, before.Position + look)
return 'ok'"""

# panel pose + head pose, hover glow vs hovered button, visible menu texts, settings values, hint scan
PROBE = r"""
local HS = game:GetService('HttpService')
local cam = workspace.CurrentCamera
local pg = game.Players.LocalPlayer.PlayerGui
local out = {}
local p = cam:FindFirstChild('GolfMenuPanel')
local head = cam.CFrame
out.head = {head.X, head.Y, head.Z}
if p then
  local cf = p.CFrame
  out.panel = {pos = {cf.X, cf.Y, cf.Z}, look = {cf.LookVector.X, cf.LookVector.Y, cf.LookVector.Z}}
  local rel = head:PointToObjectSpace(cf.Position)
  out.panelRelHead = {rel.X, rel.Y, rel.Z}
  out.panelDist = (cf.Position - head.Position).Magnitude
  local flatLook = Vector3.new(head.LookVector.X, 0, head.LookVector.Z).Unit
  local to = Vector3.new(cf.X - head.X, 0, cf.Z - head.Z).Unit
  out.panelYawOffDeg = math.deg(math.acos(math.clamp(flatLook:Dot(to), -1, 1)))
  -- does the panel face the head? (Front face normal toward the head)
  local toHead = (head.Position - cf.Position).Unit
  out.panelFacesHeadDeg = math.deg(math.acos(math.clamp(cf.LookVector:Dot(toHead), -1, 1)))
end
-- glow: every visible HoverGlow and the button it wraps
out.glows = {}
for _, g in pg:GetDescendants() do
  if g:IsA('ImageLabel') and g.Name == 'HoverGlow' and g.Visible then
    local gp, gs = g.AbsolutePosition, g.AbsoluteSize
    local inside = {}
    for _, b in g.Parent:GetDescendants() do
      if b:IsA('GuiButton') and b.Visible then
        local bp, bs = b.AbsolutePosition, b.AbsoluteSize
        if bs.X > 1 and bp.X >= gp.X - 1 and bp.Y >= gp.Y - 1 and bp.X + bs.X <= gp.X + gs.X + 1 and bp.Y + bs.Y <= gp.Y + gs.Y + 1 then
          table.insert(inside, b.Name)
        end
      end
    end
    table.insert(out.glows, {gui = g.Parent:GetFullName(), wraps = inside})
  end
end
-- texts on the VR menu + any VR SurfaceGui / ScreenGui, scanned for a thumbstick hint
local texts, hints, sticks = {}, {}, {}
for _, d in pg:GetDescendants() do
  if (d:IsA('TextLabel') or d:IsA('TextButton')) and d.Text ~= '' then
    local vis = d.Visible
    local a = d.Parent
    while vis and a and a ~= pg do
      if a:IsA('GuiObject') and not a.Visible then vis = false end
      if a:IsA('LayerCollector') and not a.Enabled then vis = false end
      a = a.Parent
    end
    if vis then
      local low = string.lower(d.Text)
      if d:FindFirstAncestor('GolfMenu') then table.insert(texts, d.Text) end
      if string.find(low, 'stick') and (string.find(low, 'menu') or string.find(low, 'click') or string.find(low, 'press')) then
        table.insert(hints, d:GetFullName() .. ': ' .. d.Text)
      end
      if string.find(low, 'stick') then table.insert(sticks, d:GetFullName() .. ': ' .. d.Text) end
    end
  end
end
out.texts = texts
out.hints = hints
out.sticks = sticks
out.settings = {}
for _, k in {'MusicVolume', 'SFXVolume', 'CameraSensitivity', 'Handedness'} do out.settings[k] = game.Players.LocalPlayer:GetAttribute(k) end
local sc = pg:FindFirstChild('VRScorecard')
out.scorecard = sc and sc.Enabled or false
local b = workspace:FindFirstChild('Balls')
out.attrs = {}
for k, v in game.Players.LocalPlayer:GetAttributes() do out.attrs[k] = typeof(v) == 'number' and v or tostring(v) end
return HS:JSONEncode(out)
"""

# (button, hand, expected page after the trigger)  page None = menu closed; "scorecard" = VR scorecard up;
# "@results" = open the results page (GolfMenuDebug); "@wrist" step names use the wrist card
STEPS = [
    ("Settings", "LeftHand", "settings"),
    ("Back", "RightHand", "title"),
    ("Settings", "RightHand", "settings"),
    ("MusicVolumeDown", "LeftHand", "settings"),
    ("MusicVolumeUp", "RightHand", "settings"),
    ("SFXVolumeDown", "RightHand", "settings"),
    ("SFXVolumeUp", "LeftHand", "settings"),
    ("CameraSensitivityDown", "LeftHand", "settings"),
    ("CameraSensitivityUp", "RightHand", "settings"),
    ("HandLeft", "LeftHand", "settings"),
    ("HandRight", "RightHand", "settings"),
    ("Back", "LeftHand", "title"),
    ("HowToPlay", "LeftHand", "howto"),
    ("TabVR", "RightHand", "howto"),
    ("TabPhone", "LeftHand", "howto"),
    ("TabDesktop", "RightHand", "howto"),
    ("Back", "RightHand", "title"),
    ("HowToPlay", "RightHand", "howto"),
    ("Back", "LeftHand", "title"),
    ("Play", "LeftHand", "courses"),
    ("Back", "LeftHand", "title"),
    ("Play", "RightHand", "courses"),
    ("@image2", "RightHand", "courses"),   # coming-soon card 2: toast only
    ("@image3", "LeftHand", "courses"),    # coming-soon card 3
    ("PlayCourse", "LeftHand", None),
    ("WristMenu", "RightHand", "title"),   # wrist card MENU (wrist raised first)
    ("Resume", "RightHand", None),
    ("WristMenu", "RightHand", "title"),
    ("Play", "RightHand", "courses"),
    ("PlayCourse", "RightHand", None),     # "Restart round"
    ("WristScores", "RightHand", "scorecard"),
    ("Close", "LeftHand", None),
    ("@results", None, "results"),
    ("PlayAgain", "RightHand", None),
    ("@results", None, "results"),
    ("BackToMenu", "LeftHand", "title"),
    ("Play", "LeftHand", "courses"),
    ("PlayCourse", "RightHand", None),
]


def probe(st):
    try:
        return json.loads(st.luau(PROBE, "Client"))
    except ValueError as e:
        return {"error": str(e)}


def page_of(st, pr):
    m = menu(st, "state")
    m = json.loads(m) if isinstance(m, str) else m
    if pr.get("scorecard"):
        return "scorecard"
    return m.get("page")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    st = Studio()
    st.stop_play()
    set_edit_attrs(st, {"GolfTestMode": False, "SimulateVR": True})
    rows, panels, ok = [], [], True
    try:
        st.start_play()
        time.sleep(12)
        first = probe(st)
        first["page"] = page_of(st, first)
        print("initial", json.dumps({k: first.get(k) for k in ("page", "panel", "panelDist", "panelYawOffDeg", "hints")}))
        st.luau(LEVEL, "Client")
        time.sleep(0.6)
        lv = probe(st)
        capture(st, os.path.join(args.out, "c1_00_title_initial_level.png"))
        session = 1
        panels.append((session, "title_initial", lv.get("panel")))
        all_hints = set(first.get("hints", [])) | set(lv.get("hints", []))
        texts_by_page = {"title": lv.get("texts")}
        for i, (name, hand, expect) in enumerate(STEPS, start=1):
            if name == "@results":
                menu(st, "results", RESULT)
                time.sleep(1.2)
                pr = probe(st)
                session += 1
                panels.append((session, "results", pr.get("panel")))
                texts_by_page["results"] = pr.get("texts")
                capture(st, os.path.join(args.out, "c1_%02d_results_open.png" % i))
                continue
            wrist = name.startswith("Wrist")
            if wrist:
                pointer(st, "wrist", True)
                time.sleep(1.0)
            targets = pointer(st, "targets") or []
            if name.startswith("@image"):
                imgs = [t for t in targets if t["name"] == "Image"]
                idx = int(name[-1]) - 1
                t = imgs[idx] if idx < len(imgs) else None
                bname = "Image"
            else:
                t = next((t for t in targets if t["name"] == name), None)
                bname = name
            before = probe(st)
            page_before = page_of(st, before)
            if not t:
                rows.append({"step": i, "button": name, "hand": hand, "error": "not on any open panel", "targets": [x["name"] for x in targets]})
                print("MISSING", rows[-1])
                ok = False
                continue
            pointer(st, "aim", {"hand": hand, "point": t["world"]})
            time.sleep(0.4)
            stt = pointer(st, "state")
            hov = stt["pointer"]
            pr = probe(st)
            glow_ok = any(bname in g["wraps"] for g in pr.get("glows", []))
            shot = "c1_%02d_%s_%s_%s.png" % (i, page_before or "play", name.strip("@"), hand)
            capture(st, os.path.join(args.out, shot))
            pointer(st, "trigger", hand)
            time.sleep(0.9)
            if wrist:
                pointer(st, "wrist", False)
                time.sleep(0.6)
            after = probe(st)
            page_after = page_of(st, after)
            beam_after = pointer(st, "state")["pointer"]["beam"]
            if page_after in (None, "scorecard"):
                session += 1
            elif after.get("panel"):
                panels.append((session, page_after, after.get("panel")))
                texts_by_page.setdefault(page_after + ("_" + name if name.startswith("Tab") else ""), after.get("texts"))
            all_hints |= set(after.get("hints", []))
            good = (hov.get("button") == bname and hov.get("hand") == hand and glow_ok and page_after == expect
                    and (expect is not None or not beam_after))
            extra = {}
            if bname.endswith("Up") or bname.endswith("Down") or bname.startswith("Hand"):
                extra = {"settings_before": before.get("settings"), "settings_after": after.get("settings")}
                key = bname.replace("Up", "").replace("Down", "").replace("Hand", "Handedness" if bname.startswith("Hand") else "")
                if bname.startswith("Hand"):
                    key = "Handedness"
                b0, b1 = (before.get("settings") or {}).get(key), (after.get("settings") or {}).get(key)
                changed = (b1 == bname[4:]) if bname.startswith("Hand") else (b0 is not None and b1 is not None and b0 != b1)
                extra["attr_changed"] = changed
                extra["text_changed"] = before.get("texts") != after.get("texts")
                changed = changed or extra["text_changed"]
                extra["changed"] = changed
                good = good and changed
            ok = ok and good
            rows.append({"step": i, "button": name, "text": t.get("text"), "panel": t.get("panel"), "hand": hand,
                         "hovered": hov.get("button"), "hover_hand": hov.get("hand"), "glow_wraps_button": glow_ok,
                         "beam_on_hover": hov.get("beam"), "page_before": page_before, "page_after": page_after,
                         "expected": expect, "beam_after": beam_after, "pass": good, "shot": shot, **extra})
            print("step", json.dumps(rows[-1]))
        # panel jumps: compare every logged panel CFrame with the first levelled one, within one menu session
        jumps, refs = [], {}
        for ses, pg, p in panels:
            if not p:
                continue
            ref = refs.setdefault(ses, p)
            d = max(abs(p["pos"][k] - ref["pos"][k]) for k in range(3))
            dl = max(abs(p["look"][k] - ref["look"][k]) for k in range(3))
            jumps.append({"session": ses, "page": pg, "pos": p["pos"], "look": p["look"], "maxDeltaFromSessionStart": round(d, 4), "lookDelta": round(dl, 4)})
        res = {"pass": ok, "steps": rows, "panels": jumps, "initial": first, "level": {k: lv.get(k) for k in ("panel", "panelRelHead", "panelDist", "panelYawOffDeg", "panelFacesHeadDeg")},
               "thumbstick_hints": sorted(all_hints), "texts_by_page": texts_by_page,
               "console": {"server": st.problems("Server"), "client": st.problems("Client")}}
        with open(os.path.join(args.out, "vr_menu.json"), "w") as fh:
            json.dump(res, fh, indent=1)
        print("RESULT", "PASS" if ok else "FAIL", "steps", sum(r.get("pass", False) for r in rows), "/", len(rows))
        print("panels", json.dumps(jumps))
        print("hints", sorted(all_hints))
        print("console", json.dumps(res["console"]))
    finally:
        st.stop_play()
        set_edit_attrs(st, {"SimulateVR": False})


if __name__ == "__main__":
    main()
