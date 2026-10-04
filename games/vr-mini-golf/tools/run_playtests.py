#!/usr/bin/env python3
"""VR Mini Golf playtest runner (stdlib + studio_mcp.py). See games/vr-mini-golf/playtesting.md.

  python3 run_playtests.py list
  python3 run_playtests.py run [scenario ...] [--cams fixed,topdown,follow] [--record] [--out DIR] [--no-vr]
  python3 run_playtests.py smoke                  normal (non-test) solo playtest: errors/warnings + HUD check
  python3 run_playtests.py export                 mirror every Studio script into games/vr-mini-golf/src/
  python3 run_playtests.py push FILE [FILE ...]   copy local src/ files into Studio (Edit) - dev convenience
  python3 run_playtests.py compare BEFORE_DIR AFTER_DIR   before/after table of the key numbers

Only ever talks to the Studio whose name contains PLACE_ID.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from studio_mcp import StudioMCP  # noqa: E402

GAME_DIR = os.path.dirname(HERE)
SRC_DIR = os.path.join(GAME_DIR, "src")
PLACE_ID = "87725688219952"
WINDOW_PREFIX = "VR Mini Golf"
STUD = 0.3
EXPORT_SERVICES = ["Workspace", "ReplicatedFirst", "ReplicatedStorage", "ServerScriptService", "ServerStorage",
                   "StarterGui", "StarterPack", "StarterPlayer", "Lighting", "SoundService", "Teams", "Chat"]


def log(*a):
    print("[runner]", *a, flush=True)


class Studio:
    def __init__(self):
        self.m = StudioMCP()
        studios = json.loads(self.m.call("list_roblox_studios")).get("studios", [])
        match = [s for s in studios if "placeId: %s" % PLACE_ID in s["name"]]
        if not match:
            raise SystemExit("VR Mini Golf (placeId %s) is not open in Studio. Open: %s" % (PLACE_ID, [s["name"] for s in studios]))
        self.id = match[0]["id"]
        log("studio", match[0]["name"], self.id)

    def call(self, tool, args=None, timeout=300):
        a = dict(args or {})
        a["studio_id"] = self.id
        return self.m.call(tool, a, timeout)

    def luau(self, code, dm="Edit", timeout=120):
        return self.call("execute_luau", {"code": code, "datamodel_type": dm}, timeout)

    def mode(self):
        s = self.call("get_studio_state")
        m = re.search(r"Current Studio Mode:\s*(\w+)", s)
        return (m.group(1) if m else "?"), s

    def stop_play(self):
        mode, _ = self.mode()
        if mode != "Edit":
            self.call("start_stop_play", {"is_start": False})
            for _ in range(60):
                time.sleep(1)
                if self.mode()[0] == "Edit":
                    break
        log("mode", self.mode()[0])

    def start_play(self):
        self.call("start_stop_play", {"is_start": True})
        for _ in range(90):
            time.sleep(1)
            mode, s = self.mode()
            if "Client" in s and "Server" in s:
                return
        raise RuntimeError("play did not start: " + s)

    def api(self, *args, timeout=60):
        code = "local f = game:GetService('ReplicatedStorage'):FindFirstChild('GolfTestAPI')\n" \
               "if not f then return 'NOAPI' end\nreturn f:Invoke(%s)" % ", ".join(lua_lit(a) for a in args)
        return self.luau(code, "Client", timeout)

    def problems(self, dm):
        code = """local HttpService = game:GetService('HttpService')
local out = {}
for _, m in game:GetService('LogService'):GetLogHistory() do
  if m.messageType == Enum.MessageType.MessageError or m.messageType == Enum.MessageType.MessageWarning then
    table.insert(out, (m.messageType == Enum.MessageType.MessageError and 'ERROR ' or 'WARN ') .. m.message)
  end
end
return HttpService:JSONEncode(out)"""
        r = self.luau(code, dm)
        try:
            return json.loads(r)
        except ValueError:
            return ["(could not read log: %s)" % r[:200]]


def lua_lit(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if v is None:
        return "nil"
    return json.dumps(str(v))


def long_string(s):
    n = 1
    while ("]" + "=" * n + "]") in s:
        n += 1
    return "[" + "=" * n + "[\n" + s + "]" + "=" * n + "]"


def set_edit_attrs(st, attrs):
    lines = ["local ok = pcall(function() game:GetService('StudioDeviceSimulatorService'):StopSimulationAsync() end)"]
    for k, v in attrs.items():
        lines.append("workspace:SetAttribute(%s, %s)" % (lua_lit(k), lua_lit(v)))
    lines.append("return 'ok'")
    return st.luau("\n".join(lines), "Edit")


# ----------------------------------------------------------------------------------------- window / recording
def window(cmd):
    try:
        r = subprocess.run(["uv", "run", "-q", "--with", "pyobjc-framework-Quartz", "--with", "pyobjc-framework-Cocoa",
                            "python", os.path.join(HERE, "studio_window.py"), cmd, WINDOW_PREFIX],
                           capture_output=True, text=True, timeout=120)
        return json.loads(r.stdout.strip().splitlines()[-1])
    except Exception as e:  # noqa: BLE001
        log("window lookup failed:", e)
        return None


def start_recording(rect, seconds, path):
    x, y, w, h = rect
    cmd = ["screencapture", "-x", "-v", "-V", str(int(seconds)), "-R", "%d,%d,%d,%d" % (x, y, w, h), path]
    log("recording", seconds, "s ->", os.path.relpath(path, GAME_DIR))
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ----------------------------------------------------------------------------------------- run
def wait_api(st, timeout=90):
    t = time.time()
    while time.time() - t < timeout:
        r = st.api("status")
        if r.startswith("{"):
            return json.loads(r)
        time.sleep(1)
    raise RuntimeError("GolfTestAPI never appeared (last: %s)" % r[:300])


def fetch_log(st):
    lines, i = [], 1
    while True:
        r = st.api("log", i, 60000)
        head, _, body = r.partition("\n")
        try:
            nxt = int(head)
        except ValueError:
            raise RuntimeError("bad log chunk: " + r[:200])
        if body:
            lines.extend(body.split("\n"))
        if nxt <= i:
            break
        i = nxt
    return lines


def run_one(st, name, cam, out_dir, record, seconds, rect):
    tag = name + ("-" + cam if cam else "")
    rec = None
    clip = None
    if record and rect:
        clip = os.path.join(out_dir, tag + ".mov")
        rec = start_recording(rect, seconds, clip)
        time.sleep(1.0)
    r = st.api("start", name, cam or "")
    if r != "started":
        raise RuntimeError("start %s: %s" % (name, r))
    t0 = time.time()
    status = {}
    while time.time() - t0 < 180:
        time.sleep(1)
        s = st.api("status")
        if s.startswith("{"):
            status = json.loads(s)
            if not status.get("running"):
                break
    lines = fetch_log(st)
    with open(os.path.join(out_dir, tag + ".jsonl"), "w") as f:
        f.write("\n".join(lines) + "\n")
    result = json.loads(st.api("result", name) or "{}")
    if rec:
        rec.wait(timeout=seconds + 30)
    log("%-10s cam=%-8s %5.1fs  lines=%d  %s" % (name, cam or "-", time.time() - t0, len(lines),
                                                   "ERROR " + result.get("error", "")[:200] if result.get("error") else ""))
    return result, clip


def cmd_run(args):
    st = Studio()
    st.stop_play()
    out_dir = args.out or os.path.join(GAME_DIR, "playtests", datetime.date.today().isoformat())
    os.makedirs(out_dir, exist_ok=True)
    set_edit_attrs(st, {"GolfTestMode": True, "SimulateVR": not args.no_vr, "GolfTestCamera": ""})
    results, clips = {}, []
    try:
        st.start_play()
        status = wait_api(st)
        log("harness ready", status)
        scen = json.loads(st.api("list"))
        names = args.scenarios or [s["name"] for s in scen]
        secs = {s["name"]: s["seconds"] for s in scen}
        unknown = [n for n in names if n not in secs]
        if unknown:
            raise SystemExit("unknown scenarios %s (have %s)" % (unknown, list(secs)))
        cams = [c for c in (args.cams or "").split(",") if c] or [""]
        rect = None
        if args.record:
            w = window("front")
            if not w or "error" in w:
                raise SystemExit("Studio window not found for recording: %s" % w)
            rect = args.rect and [int(v) for v in args.rect.split(",")] or [w["x"], w["y"], w["w"], w["h"]]
            log("window", w)
        for name in names:
            for cam in cams:
                res, clip = run_one(st, name, cam, out_dir, args.record, secs[name] + 2, rect)
                results.setdefault(name, {})[cam or "default"] = res
                if clip:
                    clips.append(clip)
        problems = {"server": st.problems("Server"), "client": st.problems("Client")}
    finally:
        st.stop_play()
        set_edit_attrs(st, {"GolfTestMode": False, "SimulateVR": False, "GolfTestCamera": None,
                            "GolfTestFocus": None, "GolfTestFrameSize": None, "GolfTestViewDir": None})
    with open(os.path.join(out_dir, "results.json"), "w") as f:
        json.dump(results, f, indent=1)
    md = summary_md(results, problems, clips, out_dir, args)
    with open(os.path.join(out_dir, "summary.md"), "w") as f:
        f.write(md)
    print(md)


# ----------------------------------------------------------------------------------------- summary
def first(res_by_cam):
    for k in ("default", "fixed", "topdown", "follow"):
        if k in res_by_cam:
            return res_by_cam[k]
    return next(iter(res_by_cam.values()))


def f(v, nd=2):
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        return ("%." + str(nd) + "f") % v
    return str(v)


def first_contact(shot, prefix=None):
    for c in shot.get("contacts", []):
        if prefix is None or c.get("part", "").split("/")[-1].startswith(prefix):
            return c
    return None


def summary_md(results, problems, clips, out_dir, args):
    L = ["# VR Mini Golf playtest summary", "",
         "- Run: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
         "- Scenarios: %s" % ", ".join(results), "- Cameras: %s" % (args.cams or "default"),
         "- SimulateVR: %s" % (not args.no_vr), ""]
    any_res = first(next(iter(results.values()))) if results else {}
    r = results.get("rollout")
    if r:
        r = first(r)
        L += ["## Rollout (flat felt test lane)", "",
              "| Speed | Distance | Time to stop | Time to rest | Ideal v²/2a |", "|---|---|---|---|---|"]
        for s in r.get("shots", []):
            ideal = (s["v0"] ** 2) / (2 * 3.6) * STUD
            L.append("| %s m/s | %s m | %s s | %s s | %.2f m |" % (s["speedMps"], f(s["distM"]), f(s.get("tStop")), f(s["tEnd"]), ideal))
        L.append("")
    for key, title in (("bank", "45° bank wall (Hole 2 Dogleg)"), ("walls", "Walls and bumper posts")):
        r = results.get(key)
        if not r:
            continue
        r = first(r)
        L += ["## " + title, "",
              "| Shot | Part | Speed in | Speed out | Angle in | Angle out | Normal restitution | Tangential retention | Speed kept |",
              "|---|---|---|---|---|---|---|---|---|"]
        for s in r.get("shots", []):
            c = first_contact(s)
            if not c:
                L.append("| %s | (no contact) | | | | | | | |" % s["label"])
                continue
            L.append("| %s | %s | %.2f m/s | %.2f m/s | %s° | %s° | %s | %s | %s |" % (
                s["label"], c["part"], c["speedIn"] * STUD, c["speedOut"] * STUD, c["angleIn"], c["angleOut"],
                f(c.get("restitution")), f(c.get("tangentialRetention")), f(c.get("speedRetention"))))
        L.append("")
    r = results.get("windmill")
    if r:
        r = first(r)
        L += ["## Windmill (Hole 4)", "", "| Shot | Outcome | Contacts | Distance | Speed at cup |", "|---|---|---|---|---|"]
        for s in r.get("shots", []):
            parts = ", ".join("%s (%.2f m/s in)" % (c["part"], c["speedIn"] * STUD) for c in s.get("contacts", [])) or "none"
            L.append("| %s | %s | %s | %s m | %s |" % (s["label"], s["outcome"], parts, f(s["distM"]), f(s.get("rimSpeedMps"))))
        L.append("")
    r = results.get("hill")
    if r:
        r = first(r)
        L += ["## The Hill (Hole 3)", "", "| Shot | Outcome | Reached green | Ended on green | Rolled back | Max height | Final position |",
              "|---|---|---|---|---|---|---|"]
        for s in r.get("shots", []):
            L.append("| %s | %s | %s | %s | %s | %s | %s |" % (s["label"], s["outcome"], f(s.get("madeGreen")), f(s.get("endedOnGreen")),
                                                            f(s.get("rolledBack")), f(s["maxY"]), s["finish"]))
        L.append("")
    r = results.get("cup")
    if r:
        r = first(r)
        L += ["## Cup drop (Hole 1, from 60 cm)", "", "| Putt speed | Speed at rim | Outcome | Holed on first pass |", "|---|---|---|---|"]
        for s in r.get("shots", []):
            L.append("| %s m/s | %s m/s | %s | %s |" % (s["speedMps"], f(s.get("rimSpeedMps")), s["outcome"], f(s.get("holedFirstPass"))))
        L.append("")
    r = results.get("ledge")
    if r:
        r = first(r)
        L += ["## Ledge plane snap (SimulateVR)", ""]
        if r.get("skipped") or r.get("error"):
            L += ["Skipped/error: %s" % (r.get("skipped") or r.get("error")), ""]
        else:
            L += ["Heights are relative to the plane the ball rests on (studs; 1 stud = 30 cm).", "",
                  "| Case | Ball plane Y | VR rig floor Δ | Character feet Δ | Putter head bottom Δ | Pass |", "|---|---|---|---|---|---|"]
            for c in r.get("cases", []):
                L.append("| %s | %s | %s | %s | %s | %s |" % (c["label"], f(c["ballPlaneY"], 3), f(c["rigDelta"], 3),
                                                           f(c.get("charDelta"), 3), f(c["headDelta"], 3), f(c["ok"])))
            L.append("")
    r = results.get("ghost")
    if r:
        r = first(r)
        L += ["## Club ghosting (SimulateVR)", ""]
        if r.get("skipped") or r.get("error"):
            L += ["Skipped/error: %s" % (r.get("skipped") or r.get("error")), ""]
        else:
            L += ["| Sweep | Max follow error | Max lift | Ball moved | Hits | Club parts non-colliding | Pass |", "|---|---|---|---|---|---|---|"]
            for k in ("wall", "post"):
                s = r.get(k) or {}
                L.append("| %s | %s | %s | %s | %s | %s | %s |" % (s.get("label"), f(s.get("maxFollowError"), 3), f(s.get("maxLift"), 3),
                                                                  f(s.get("ballMoved"), 3), s.get("hits"), f(s.get("clubPartsGhost")), f(s.get("ok"))))
            sw = r.get("swing") or {}
            L += ["", "VR swing through the ball (putter face 1.2 m/s): hit=%s source=%s ball speed %s studs/s (expected %s), outcome %s, %s m. Pass: %s" % (
                f(sw.get("hit")), sw.get("source"), f(sw.get("ballSpeed")), f(sw.get("expectedSpeed")), sw.get("outcome"), f(sw.get("distM")), f(sw.get("ok"))), ""]
    errs = [k for k, v in results.items() for c, rr in v.items() if rr.get("error")]
    if errs:
        L += ["## Scenario errors", ""] + ["- %s: %s" % (k, first(results[k]).get("error", "")[:500]) for k in errs] + [""]
    L += ["## Console", "", "- Server warnings/errors: %d" % len(problems["server"]), "- Client warnings/errors: %d" % len(problems["client"])]
    for side in ("server", "client"):
        for p in problems[side][:20]:
            L.append("  - %s: `%s`" % (side, p[:300]))
    if clips:
        L += ["", "## Clips", ""] + ["- `%s`" % os.path.relpath(c, GAME_DIR) for c in clips]
    if any_res:
        L += ["", "Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder."]
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------------------------------- compare
def key_metrics(results):
    out = {}
    def g(name):
        return first(results[name]) if name in results else {}
    for s in g("rollout").get("shots", []):
        out["rollout %s m/s distance (m)" % s["speedMps"]] = s["distM"]
        out["rollout %s m/s time to stop (s)" % s["speedMps"]] = s.get("tStop")
    for key in ("bank", "walls"):
        for s in g(key).get("shots", []):
            c = first_contact(s)
            if c:
                out["%s restitution (normal)" % s["label"]] = c.get("restitution")
                if c.get("tangentialRetention") is not None:
                    out["%s tangential retention" % s["label"]] = c.get("tangentialRetention")
                out["%s speed kept" % s["label"]] = c.get("speedRetention")
                if key == "bank":
                    out["%s angle out (deg)" % s["label"]] = c.get("angleOut")
    for s in g("cup").get("shots", []):
        out["cup %s m/s" % s["speedMps"]] = s["outcome"] + ("" if s.get("holedFirstPass") or s["outcome"] != "cup" else " (after rebound)")
    for s in g("hill").get("shots", []):
        out["%s" % s["label"]] = "%s, green=%s, rolled back=%s" % (s["outcome"], f(s.get("madeGreen")), f(s.get("rolledBack")))
    for s in g("windmill").get("shots", []):
        out["%s" % s["label"]] = "%s (%d contacts)" % (s["outcome"], len(s.get("contacts", [])))
    for c in g("ledge").get("cases", []):
        out["ledge %s head Δ (studs)" % c["label"]] = c["headDelta"]
        out["ledge %s rig floor Δ (studs)" % c["label"]] = c["rigDelta"]
        out["ledge %s character Δ (studs)" % c["label"]] = c.get("charDelta")
    gh = g("ghost")
    for k in ("wall", "post"):
        if gh.get(k):
            out["ghost %s: max lift / follow err / ball moved / pass" % k] = "%s / %s / %s / %s" % (
                f(gh[k]["maxLift"], 3), f(gh[k]["maxFollowError"], 3), f(gh[k]["ballMoved"], 3), f(gh[k]["ok"]))
    if gh.get("swing"):
        out["ghost VR swing ball speed (studs/s)"] = gh["swing"].get("ballSpeed")
    return out


def cmd_compare(args):
    a = json.load(open(os.path.join(args.before, "results.json")))
    b = json.load(open(os.path.join(args.after, "results.json")))
    ka, kb = key_metrics(a), key_metrics(b)
    keys = list(ka) + [k for k in kb if k not in ka]
    print("| Metric | Before | After |\n|---|---|---|")
    for k in keys:
        print("| %s | %s | %s |" % (k, f(ka.get(k), 3), f(kb.get(k), 3)))


# ----------------------------------------------------------------------------------------- smoke
def cmd_smoke(args):
    st = Studio()
    st.stop_play()
    set_edit_attrs(st, {"GolfTestMode": False, "SimulateVR": False})
    try:
        st.start_play()
        time.sleep(args.wait)
        hud = st.luau("""local pg = game:GetService('Players').LocalPlayer:FindFirstChild('PlayerGui')
local gui = pg and pg:FindFirstChild('GolfHUD')
local texts = {}
if gui then for _, d in gui:GetDescendants() do if d:IsA('TextLabel') and d.Visible and d.Text ~= '' then table.insert(texts, d.Text) end end end
local api = game:GetService('ReplicatedStorage'):FindFirstChild('GolfTestAPI')
local lane = workspace:FindFirstChild('GolfTestLane')
return game:GetService('HttpService'):JSONEncode({hud = gui ~= nil, texts = texts, testApi = api ~= nil, testLane = lane ~= nil})""", "Client")
        problems = {"server": st.problems("Server"), "client": st.problems("Client")}
    finally:
        st.stop_play()
    print(json.dumps({"hud": json.loads(hud), "problems": problems}, indent=1))


# ----------------------------------------------------------------------------------------- export / push
def studio_to_rel(full, cls):
    parts = full.split(".")
    ext = {"Script": ".server.luau", "LocalScript": ".client.luau"}.get(cls, ".luau")
    return os.path.join(*parts[:-1], parts[-1] + ext) if len(parts) > 1 else parts[0] + ext


def cmd_export(args):
    st = Studio()
    listing = st.luau("""local HttpService = game:GetService('HttpService')
local out = {}
for _, svc in %s do
  local s = game:FindService(svc)
  if s then
    for _, d in s:GetDescendants() do
      if d:IsA('LuaSourceContainer') then table.insert(out, {path = d:GetFullName(), class = d.ClassName, len = #d.Source}) end
    end
  end
end
return HttpService:JSONEncode(out)""" % ("{" + ",".join(json.dumps(s) for s in EXPORT_SERVICES) + "}"), "Edit")
    items = json.loads(listing)
    written = set()
    for it in items:
        src = ""
        off = 1
        while off <= it["len"] or (off == 1 and it["len"] == 0):
            chunk = st.luau("""local inst = game
for name in string.gmatch(%s, '[^.]+') do inst = inst:FindFirstChild(name) end
return string.sub(inst.Source, %d, %d)""" % (json.dumps(it["path"]), off, off + 59999), "Edit")
            src += chunk
            off += 60000
            if it["len"] == 0:
                break
        rel = studio_to_rel(it["path"], it["class"])
        path = os.path.join(SRC_DIR, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(src if src.endswith("\n") else src + "\n")
        written.add(os.path.normpath(path))
        log("exported", rel, len(src))
    for root, _, files in os.walk(SRC_DIR):
        for fn in files:
            p = os.path.normpath(os.path.join(root, fn))
            if fn.endswith(".luau") and p not in written:
                os.remove(p)
                log("removed stale", os.path.relpath(p, SRC_DIR))
    for root, dirs, files in os.walk(SRC_DIR, topdown=False):
        if not os.listdir(root) and root != SRC_DIR:
            os.rmdir(root)


def cmd_push(args):
    st = Studio()
    if st.mode()[0] != "Edit":
        raise SystemExit("stop play first")
    for file in args.files:
        path = os.path.abspath(file)
        rel = os.path.relpath(path, SRC_DIR)
        if rel.startswith(".."):
            raise SystemExit("%s is not under %s" % (file, SRC_DIR))
        parts = rel.split(os.sep)
        name = parts[-1]
        cls = "ModuleScript"
        for suf, c in ((".server.luau", "Script"), (".client.luau", "LocalScript"), (".luau", "ModuleScript")):
            if name.endswith(suf):
                name, cls = name[: -len(suf)], c
                break
        src = open(path).read()
        code = """local path = %s
local parent = game:GetService(path[1])
for i = 2, #path do parent = parent:FindFirstChild(path[i]) or error('missing ' .. path[i]) end
local s = parent:FindFirstChild(%s)
if s and s.ClassName ~= %s then error('class mismatch: ' .. s.ClassName) end
local created = false
if not s then s = Instance.new(%s); s.Name = %s; s.Parent = parent; created = true end
s.Source = %s
return (created and 'created ' or 'updated ') .. s:GetFullName() .. ' ' .. #s.Source""" % (
            "{" + ",".join(json.dumps(p) for p in parts[:-1]) + "}", json.dumps(name), json.dumps(cls), json.dumps(cls),
            json.dumps(name), long_string(src))
        log(st.luau(code, "Edit"))


def cmd_list(args):
    # read from the src/ mirror of GolfClient.GolfTest so this works without a playtest running
    names = []
    for line in open(os.path.join(SRC_DIR, "StarterPlayer", "StarterPlayerScripts", "GolfClient", "GolfTest.luau")):
        m = re.match(r'\s*name = "([\w-]+)",', line)
        d = re.match(r'\s*desc = "(.*)",', line)
        if m:
            names.append([m.group(1), ""])
        elif d and names:
            names[-1][1] = d.group(1)
    for n, d in names:
        print("%-10s %s" % (n, d))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    r = sub.add_parser("run")
    r.add_argument("scenarios", nargs="*")
    r.add_argument("--cams", default="")
    r.add_argument("--record", action="store_true")
    r.add_argument("--out")
    r.add_argument("--rect", help="x,y,w,h screen rect to record instead of the Studio window")
    r.add_argument("--no-vr", action="store_true", help="don't set SimulateVR (ledge/ghost are skipped)")
    s = sub.add_parser("smoke")
    s.add_argument("--wait", type=float, default=10)
    sub.add_parser("export")
    p = sub.add_parser("push")
    p.add_argument("files", nargs="+")
    c = sub.add_parser("compare")
    c.add_argument("before")
    c.add_argument("after")
    args = ap.parse_args()
    {"list": cmd_list, "run": cmd_run, "smoke": cmd_smoke, "export": cmd_export, "push": cmd_push, "compare": cmd_compare}[args.cmd](args)


if __name__ == "__main__":
    main()
