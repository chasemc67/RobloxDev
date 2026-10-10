#!/usr/bin/env python3
"""VR Mini Golf playtest runner (stdlib + studio_mcp.py). See games/vr-mini-golf/playtesting.md.

  python3 run_playtests.py list
  python3 run_playtests.py run [scenario ...] [--cams fixed,topdown,follow] [--record] [--out DIR] [--no-vr]
                                [--opts '{"fuzz":12,"sweep":6,"hioTries":9,"parts":"routes,hio,banks,sweep,fuzz"}']
  python3 run_playtests.py holes [N ...] [--opts ...] [--out DIR]   per-hole suites h1..h9 + h7pin, h8door, movers
  python3 run_playtests.py shots [--out DIR] [--holes 1,2,..]       overview.png, holeNN.png, topdown/follow per hole
  python3 run_playtests.py smoke                  normal (non-test) solo playtest: errors/warnings + HUD check
  python3 run_playtests.py export                 mirror every Studio script into games/vr-mini-golf/src/
  python3 run_playtests.py push FILE [FILE ...]   copy local src/ files into Studio (Edit) - dev convenience
  python3 run_playtests.py compare BEFORE_DIR AFTER_DIR   before/after table of the key numbers
  python3 run_playtests.py clubviz [--out DIR]    VR club mount screenshots (legacy vs grip; side/front/top)

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


TEST_ATTRS = ["GolfTestCamera", "GolfTestFocus", "GolfTestFrameSize", "GolfTestViewDir", "GolfTestCamPos", "GolfTestCamUp",
              "GolfTestFOV", "GolfTestClubDebug", "GolfTestOpts"]


def clear_test_attrs(st):
    attrs = {"GolfTestMode": False, "SimulateVR": False}
    attrs.update({k: None for k in TEST_ATTRS})
    set_edit_attrs(st, attrs)


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
    while time.time() - t0 < seconds + 180:
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
    attrs = {"GolfTestMode": True, "SimulateVR": not args.no_vr, "GolfTestCamera": ""}
    if getattr(args, "opts", None):
        json.loads(args.opts)  # validate
        attrs["GolfTestOpts"] = args.opts
    set_edit_attrs(st, attrs)
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
        clear_test_attrs(st)
    with open(os.path.join(out_dir, "results.json"), "w") as f:
        json.dump(results, f, indent=1)
    md = summary_md(results, problems, clips, out_dir, args)
    with open(os.path.join(out_dir, "summary.md"), "w") as f:
        f.write(md)
    print(md)


# ----------------------------------------------------------------------------------------- club screenshots
def capture_window(win_id, path):
    subprocess.run(["screencapture", "-x", "-o", "-l%d" % win_id, path], check=True, timeout=30)


def crop_viewport(path):
    """Crop a Studio window capture to the 3D viewport (the largest block of rows/cols that isn't Studio chrome).
    Uses Pillow through uv; leaves the file alone if that fails."""
    code = r"""
import sys
from PIL import Image
p = sys.argv[1]
im = Image.open(p).convert("RGB")
w, h = im.size
px = im.load()
# play-mode viewport border: a 2 px blue frame (~(51,95,255)) around the game view
def blue(c):
    return c[2] > 235 and c[0] < 90 and 70 < c[1] < 125
# the border is the only long straight run of that colour: rows/cols where it covers > 40% of the window
rows = [y for y in range(h) if sum(blue(px[x, y]) for x in range(0, w, 4)) > 0.4 * w / 4]
cols = [x for x in range(w) if sum(blue(px[x, y]) for y in range(0, h, 4)) > 0.4 * h / 4]
if rows and cols:
    x0, x1, y0, y1 = min(cols), max(cols), min(rows), max(rows)
    if x1 - x0 > w * 0.3 and y1 - y0 > h * 0.3:
        # also drop the Roblox top-bar buttons strip (CoreGui, ~58 pt; captures are Retina 2x)
        im.crop((x0 + 4, y0 + 4 + 2 * 58, x1 - 3, y1 - 3)).save(p)
        print("cropped", x0, y0, x1, y1)
        sys.exit(0)
print("no border; kept full window")
"""
    try:
        r = subprocess.run(["uv", "run", "-q", "--with", "pillow", "python", "-c", code, path],
                           capture_output=True, text=True, timeout=120)
        log("crop", os.path.basename(path), (r.stdout or r.stderr).strip()[-200:])
    except Exception as e:  # noqa: BLE001
        log("crop failed:", e)


def cmd_clubviz(args):
    st = Studio()
    st.stop_play()
    out_dir = args.out or os.path.join(GAME_DIR, "playtests", datetime.date.today().isoformat() + "-clubfix")
    os.makedirs(out_dir, exist_ok=True)
    set_edit_attrs(st, {"GolfTestMode": True, "SimulateVR": True, "GolfTestCamera": ""})
    metrics = {}
    try:
        st.start_play()
        wait_api(st)
        st.luau("game:GetService('StarterGui'):SetCoreGuiEnabled(Enum.CoreGuiType.All, false) return 'ok'", "Client")
        w = window("front")
        if not w or "error" in w:
            raise SystemExit("Studio window not found: %s" % w)
        for tag, legacy in (("before", True), ("after", False)):
            for view in args.views.split(","):
                r = st.api("clubpose", legacy, view, timeout=90)
                if not r.startswith("{"):
                    raise RuntimeError("clubpose %s %s: %s" % (tag, view, r[:300]))
                metrics["%s_%s" % (tag, view)] = json.loads(r)
                time.sleep(args.settle)  # the Studio viewport lags the game a little
                path = os.path.join(out_dir, "%s%s_%s.png" % (args.prefix, tag, view))
                capture_window(w["id"], path)
                if not args.no_crop:
                    crop_viewport(path)
                log(tag, view, os.path.relpath(path, GAME_DIR))
        metrics["problems"] = {"server": st.problems("Server"), "client": st.problems("Client")}
    finally:
        st.stop_play()
        clear_test_attrs(st)
    with open(os.path.join(out_dir, args.prefix + "clubpose.json"), "w") as fh:
        json.dump(metrics, fh, indent=1)
    keys = ["handHeightM", "handleLeanDeg", "shaftVsHandleDeg", "shaftVisualVsHandleDeg", "shaftStartGap", "shaftLeanDeg",
            "aimRayElevationDeg", "headBottomAbovePlane", "headToTarget", "headToBallFlat", "clubLength"]
    print("| metric | before | after |\n|---|---|---|")
    b, a = metrics.get("before_side", {}), metrics.get("after_side", {})
    for k in keys:
        print("| %s | %s | %s |" % (k, b.get(k), a.get(k)))
    print("problems:", json.dumps(metrics.get("problems")))


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


def holed_first_pass(s):
    """Holed without touching anything away from the cup. Recomputed from the logged contacts so older runs
    (whose Lua metric counted the ball's own drop against the rim as a contact) score the same way."""
    if s.get("outcome") != "cup":
        return False
    cx, _, cz = s.get("cupPos") or [0, 1, 27]  # hole 1 cup
    for c in s.get("contacts", []):
        x, _, z = c["pos"]
        if ((x - cx) ** 2 + (z - cz) ** 2) ** 0.5 > s.get("cupRadius", 0.21) + 2 * 0.08:
            return False
    return True


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
              "| Speed | Distance | Time to stop | Time to rest | Ideal distance / time (rolling model) |", "|---|---|---|---|---|"]
        for s in r.get("shots", []):
            if s.get("idealM") is not None:
                ideal = "%.2f m / %.2f s" % (s["idealM"], s["idealT"])
            else:  # runs before RollDrag existed: constant RollDecel 3.6
                ideal = "%.2f m (v²/2a)" % ((s["v0"] ** 2) / (2 * 3.6) * STUD)
            L.append("| %s m/s | %s m | %s s | %s s | %s |" % (s["speedMps"], f(s["distM"]), f(s.get("tStop")), f(s["tEnd"]), ideal))
        L.append("")
    for key, title in (("bank", "45° timber deflector (Hole 1 Lantern Gate)"), ("walls", "Rails and bumper blocks")):
        r = results.get(key)
        if not r:
            continue
        r = first(r)
        L += ["## " + title, "",
              "| Shot | Part | Speed in | Speed out | Angle in | Angle out | Normal restitution | Tangential retention | Speed kept | Kept after 0.3 s |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for s in r.get("shots", []):
            c = first_contact(s)
            if not c:
                L.append("| %s | (no contact) | | | | | | | |" % s["label"])
                continue
            L.append("| %s | %s | %.2f m/s | %.2f m/s | %s° | %s° | %s | %s | %s | %s |" % (
                s["label"], c["part"], c["speedIn"] * STUD, c["speedOut"] * STUD, c["angleIn"], c["angleOut"],
                f(c.get("restitution")), f(c.get("tangentialRetention")), f(c.get("speedRetention")), f(c.get("retentionAfter300ms"))))
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
        L += ["## Ramp (Hole 9, 1 stud rise)", "", "| Shot | Outcome | Reached green | Ended on green | Rolled back | Max height | Final position |",
              "|---|---|---|---|---|---|---|"]
        for s in r.get("shots", []):
            L.append("| %s | %s | %s | %s | %s | %s | %s |" % (s["label"], s["outcome"], f(s.get("madeGreen")), f(s.get("endedOnGreen")),
                                                            f(s.get("rolledBack")), f(s["maxY"]), s["finish"]))
        L.append("")
    r = results.get("cup")
    if r:
        r = first(r)
        L += ["## Cup drop (Hole 1, cup radius 0.5 stud, from 60 cm)", "", "| Putt speed | Speed at rim | Outcome | Holed on first pass |", "|---|---|---|---|"]
        for s in r.get("shots", []):
            L.append("| %s m/s | %s m/s | %s | %s |" % (s["speedMps"], f(s.get("rimSpeedMps")), s["outcome"], f(holed_first_pass(s))))
        L.append("")
    r = results.get("ledge")
    if r:
        r = first(r)
        L += ["## Ledge plane snap (SimulateVR)", ""]
        if r.get("skipped") or r.get("error"):
            L += ["Skipped/error: %s" % (r.get("skipped") or r.get("error")), ""]
        else:
            L += ["Heights are relative to the plane the ball rests on (studs; 1 stud = 30 cm).", "",
                  "| Case | Ball plane Y | VR rig floor Δ | Character feet Δ | Putter head bottom Δ | Wall group (player collides) | Pass |",
                  "|---|---|---|---|---|---|---|"]
            for c in r.get("cases", []):
                L.append("| %s | %s | %s | %s | %s | %s (%s) | %s |" % (c["label"], f(c["ballPlaneY"], 3), f(c["rigDelta"], 3),
                                                           f(c.get("charDelta"), 3), f(c["headDelta"], 3), c.get("wallGroup", "-"),
                                                           f(c.get("playerCollidesWithWall")), f(c["ok"])))
            L.append("")
    r = results.get("clubviz")
    if r:
        r = first(r)
        L += ["## VR club mount (SimulateVR, putting-grip hand pose)", ""]
        if r.get("skipped") or r.get("error"):
            L += ["Skipped/error: %s" % (r.get("skipped") or r.get("error")), ""]
        else:
            L += ["| Mount | Shaft vs handle | Shaft start gap (studs) | Shaft lean | Head bottom above plane | Head to target | Aim ray elevation |",
                  "|---|---|---|---|---|---|---|"]
            for k in ("legacy", "grip"):
                c = r.get(k) or {}
                L.append("| %s | %s° | %s | %s° | %s | %s | %s° |" % (k, c.get("shaftVsHandleDeg"), f(c.get("shaftStartGap"), 3), c.get("shaftLeanDeg"),
                                                                    f(c.get("headBottomAbovePlane"), 3), f(c.get("headToTarget"), 3), c.get("aimRayElevationDeg")))
            ft = r.get("fit") or {}
            L += ["", "A-button re-fit from that pose: shaft lean %s°, shaft start gap %s, head bottom above plane %s, length %s -> %s studs (pass %s)" % (
                ft.get("shaftLeanDeg"), f(ft.get("shaftStartGap"), 3), f(ft.get("headBottomAbovePlane"), 3), f(ft.get("clubLengthBefore"), 3),
                f(ft.get("clubLength"), 3), f(ft.get("ok"))), "", "Pass (grip mount + re-fit): %s" % f(r.get("ok")), ""]
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
    L += hole_summary_md(results)
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


def hole_summary_md(results):
    """Per-hole tables for the Lantern Grove suites (h1..h9), the H7 log-pin hunt, the H8 door test and movers."""
    L = []
    rows = []
    for n in range(1, 10):
        r = results.get("h%d" % n)
        if not r:
            continue
        r = first(r)
        if r.get("error"):
            rows.append("| %d | | ERROR: %s |||||||" % (n, r["error"][:120]))
            continue
        routes = {x["skill"]: x for x in r.get("routes", [])}
        def rt(k):
            x = routes.get(k)
            return "-" if not x else "%s%s" % (x["strokes"], "" if x["holed"] else " (not holed)")
        intended = {x["skill"]: x for x in r.get("intended", [])}
        def it(k):
            x = intended.get(k)
            return "-" if not x else "%s%s" % (x["strokes"], "" if x["holed"] else " (not holed)")
        hio = r.get("hio") or {}
        sw = r.get("sweep") or []
        swtxt = "; ".join("%s %d/%d clear" % (m["mover"], sum(1 for row in m["rows"] if not row["blocked"]), len(m["rows"])) for m in sw) or "-"
        fz = r.get("fuzz") or {}
        rows.append("| %d %s | %s | %s / %s | %s | %s | %s | %s | %s | %s/%s/%s/%s | %d / %d / %d |" % (
            n, r.get("name", ""), r.get("par"), it("good"), it("average"), rt("good"), rt("average"),
            ("yes (aim %.1f°, %.1f studs/s)" % (hio.get("aceAim"), hio.get("aceSpeed"))) if hio.get("ace") else ("no (%d tries)" % len(hio.get("attempts", [])) if hio.get("attempts") else "-"),
            ", ".join("%s: %s" % (b["bank"], f((b.get("firstContact") or {}).get("restitution"))) for b in r.get("banks", [])) or "-",
            swtxt, fz.get("shots", "-"), fz.get("hazards", "-"), fz.get("escapes", "-"), fz.get("stuck", "-"),
            r.get("escapes", 0), r.get("stuck", 0), r.get("nudges", 0)))
    if rows:
        L += ["## Lantern Grove per-hole suites", "",
              "Intended = the waypoint line played best-of-K per stroke (aim ±3/6°, speed ±10-25% from the same spot; every "
              "counted stroke is a real in-engine shot), good / safe. "
              "Routes = strokes to hole out with the spec's AI waypoints, one shot per stroke (good = aggressive/risk line, average = safe line). "
              "Banks = normal restitution of the first rail contact. Fuzz = shots / hazards / escapes / stuck.", "",
              "| Hole | Par | Intended (good / safe) | Good line | Safe line | Hole-in-one | Banks (restitution) | Mover timing sweep | Fuzz | Escapes / stuck / nudges |",
              "|---|---|---|---|---|---|---|---|---|---|"] + rows + [""]
        for n in range(1, 10):
            r = results.get("h%d" % n)
            if not r:
                continue
            r = first(r)
            iss = r.get("issues") or []
            if iss:
                L.append("- h%d issues: %s" % (n, "; ".join("%s %s at %s" % (i.get("kind"), i.get("label"), i.get("pos") or i.get("to") or i.get("from")) for i in iss[:12])))
        L.append("")
    r = results.get("progress")
    if r:
        r = first(r)
        L += ["## Hole-to-hole progression", "", "| Hole | Sunk | Next hole | Ball to next tee | VR rig to ball | HUD | Pass |", "|---|---|---|---|---|---|---|"]
        for row in r.get("rows", []):
            if row["hole"] < 9:
                L.append("| %d | %s | %s | %s | %s | %s | %s |" % (row["hole"], f(row["sunk"]), row.get("nextHole"), row.get("ballToTee"),
                                                             row.get("vrRigToBall"), row.get("hudTitle", "").split("\n")[0], f(row.get("ok"))))
            else:
                L.append("| 9 | %s | course complete: %s | | | final scorecard: %s | %s |" % (f(row["sunk"]), f(row.get("courseComplete")),
                                                                                       f(row.get("scorecard")), f(row.get("ok"))))
        L += ["", "Pass: %s" % f(r.get("ok")), ""]
    r = results.get("h7pin")
    if r:
        r = first(r)
        L += ["## Hole 7 sliding log pin hunt", "", "Cases: %d, pinned > 0.5 s or nudged: %s, longest pinned contact: %s s" % (
            len(r.get("cases", [])), r.get("pinCases"), r.get("maxPinnedS")), ""]
        L += ["| Case | Touched log | Max pinned (s) | Nudges | Finish zone |", "|---|---|---|---|---|"]
        for c in r.get("cases", []):
            L.append("| %s | %s | %s | %d | %s |" % (c["label"], f(c["touchedLog"]), c["maxPinnedS"], len(c.get("nudges", [])), c.get("zone")))
        L.append("")
    r = results.get("h8door")
    if r:
        r = first(r)
        L += ["## Hole 8 root door vs balls at the alcove rails", "", "Door range: %s" % r.get("range"), "",
              "| Start | Max speed | Max rise | Max pinned (s) | Flags | Finish zone |", "|---|---|---|---|---|---|"]
        for c in r.get("cases", []):
            L.append("| %s | %s | %s | %s | %s | %s |" % (c["start"], c["maxSpeed"], c["maxRise"], c["maxPinnedS"],
                                                     ", ".join(x.get("kind", "") for x in c.get("flags") or []) or "-", c.get("zone")))
        L.append("")
    r = results.get("movers")
    if r:
        r = first(r)
        L += ["## Moving parts vs spec", "", "| Mover | Hole | Value error | Blocker pose error (studs) | Server owned | Client lag (s) |", "|---|---|---|---|---|---|"]
        lag = {(c["hole"], c["id"]): c for c in r.get("client", [])}
        for m in r.get("server", []):
            n = int(str(m.get("hole", "Hole0")).replace("Hole", "") or 0)
            c = lag.get((n, m["id"]), {})
            L.append("| %s | %s | %.3f | %.3f | %s | %s |" % (m["id"], m.get("hole"), m["err"], m["blockerPosErr"], f(m["networkOwnerServer"]), c.get("lag")))
        L += ["", "Pass: %s" % f(r.get("ok")), ""]
    return L


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
                out["%s speed kept after 0.3 s" % s["label"]] = c.get("retentionAfter300ms")
                if key == "bank":
                    out["%s angle out (deg)" % s["label"]] = c.get("angleOut")
    for s in g("cup").get("shots", []):
        out["cup %s m/s putt" % s["speedMps"]] = "%s%s, rim %s m/s" % (
            s["outcome"], "" if holed_first_pass(s) or s["outcome"] != "cup" else " (after rebound)", f(s.get("rimSpeedMps")))
    for s in g("hill").get("shots", []):
        out["%s" % s["label"]] = "%s, green=%s, rolled back=%s" % (s["outcome"], f(s.get("madeGreen")), f(s.get("rolledBack")))
    for s in g("windmill").get("shots", []):
        out["%s" % s["label"]] = "%s (%d contacts)" % (s["outcome"], len(s.get("contacts", [])))
    for c in g("ledge").get("cases", []):
        out["ledge %s head Δ (studs)" % c["label"]] = c["headDelta"]
        out["ledge %s rig floor Δ (studs)" % c["label"]] = c["rigDelta"]
        out["ledge %s character Δ (studs)" % c["label"]] = c.get("charDelta")
    cv = g("clubviz")
    if cv.get("grip"):
        out["clubviz grip: shaft vs handle (deg) / head above plane / pass"] = "%s / %s / %s" % (
            cv["grip"]["shaftVsHandleDeg"], f(cv["grip"]["headBottomAbovePlane"], 3), f(cv.get("ok")))
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
    """Normal solo playtest (test mode off): loads, then plays real putts on hole 1 through the regular client code
    (BallController.hit, the function the touch/mouse and VR controls call), and collects errors/warnings and the HUD.
    --device iphone_17_pro runs it under Studio's device emulator (TouchEnabled, phone viewport)."""
    st = Studio()
    st.stop_play()
    set_edit_attrs(st, {"GolfTestMode": False, "SimulateVR": False})
    if args.device:
        log("device", st.luau("game:GetService('StudioDeviceSimulatorService'):SetDeviceAsync(%s) return 'ok'" % json.dumps(args.device), "Edit"))
    try:
        st.start_play()
        time.sleep(args.wait)
        # (a require() from the MCP command context gets its own copy of BallController, so this checks the real
        # ball instance; scripted putts through Ball.hit are covered by the test-mode harness)
        play = st.luau("""local Players = game:GetService('Players')
local UIS = game:GetService('UserInputService')
task.wait(%d)
local me = Players.LocalPlayer
local ball = workspace:FindFirstChild('Balls') and workspace.Balls:FindFirstChild(tostring(me.UserId))
local h1 = workspace.Course:FindFirstChild('Hole1')
local out = {touch = UIS.TouchEnabled, viewport = tostring(workspace.CurrentCamera.ViewportSize), ball = ball ~= nil,
  hole = me:GetAttribute('Hole'), strokes = me:GetAttribute('Strokes'), camType = tostring(workspace.CurrentCamera.CameraType)}
if ball and h1 then out.ballToTee = math.floor((ball.Position - h1.Tee.Position).Magnitude * 100) / 100; out.anchored = ball.Anchored end
-- perf: frames over 5 s at the hole 1 tee view (Mac GPU, so only a relative number), and what the client holds
local frames = 0
local conn = game:GetService('RunService').RenderStepped:Connect(function() frames += 1 end)
task.wait(5)
conn:Disconnect()
out.fps = frames / 5
local parts, meshes, lights = 0, 0, 0
for _, d in workspace:GetDescendants() do
  if d:IsA('BasePart') then parts += 1 end
  if d:IsA('MeshPart') then meshes += 1 end
  if d:IsA('Light') then lights += 1 end
end
out.parts, out.meshParts, out.lights = parts, meshes, lights
return game:GetService('HttpService'):JSONEncode(out)""" % args.shots, "Client", timeout=180)
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
        if args.device:
            st.luau("pcall(function() game:GetService('StudioDeviceSimulatorService'):StopSimulationAsync() end) return 'ok'", "Edit")
    try:
        play = json.loads(play)
    except ValueError:
        pass
    print(json.dumps({"device": args.device or "desktop", "play": play, "hud": json.loads(hud), "problems": problems}, indent=1))


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


def cmd_push(args, st=None):
    st = st or Studio()
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
for i = 2, #path do
  local nxt = parent:FindFirstChild(path[i])
  if not nxt then nxt = Instance.new('Folder'); nxt.Name = path[i]; nxt.Parent = parent end
  parent = nxt
end
local s = parent:FindFirstChild(%s)
if s and s.ClassName ~= %s then error('class mismatch: ' .. s.ClassName) end
local created = false
if not s then s = Instance.new(%s); s.Name = %s; s.Parent = parent; created = true end
s.Source = %s
return (created and 'created ' or 'updated ') .. s:GetFullName() .. ' ' .. #s.Source""" % (
            "{" + ",".join(json.dumps(p) for p in parts[:-1]) + "}", json.dumps(name), json.dumps(cls), json.dumps(cls),
            json.dumps(name), long_string(src))
        log(st.luau(code, "Edit"))


def engine_sim_lines(holes):
    """Candidate ace lines from tools/engine_sim.py (engine-calibrated copy of the designer's sim)."""
    cmd = ["uv", "run", "-q", "--with", "numpy", "--with", "numba", "python", os.path.join(HERE, "engine_sim.py"),
           "--top", "4", "--holes"] + [str(h) for h in holes]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    for line in r.stderr.splitlines():
        if line.startswith("hole "):
            log("engine-sim", line[:200])
    try:
        return json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        log("engine-sim failed:", r.stderr[-500:])
        return {}


def cmd_holes(args):
    names = ["h%d" % int(n) for n in (args.holes or range(1, 10))]
    if args.engine_sim:
        o = json.loads(args.opts or "{}")
        o["hioLines"] = engine_sim_lines([int(n) for n in (args.holes or range(1, 10))])
        args.opts = json.dumps(o)
    if not args.holes:
        names += ["h7pin", "h8door", "movers"]
    ns = argparse.Namespace(scenarios=names, cams="", record=False, out=args.out, rect=None, no_vr=True, opts=args.opts)
    cmd_run(ns)


def cmd_shots(args):
    """Screenshots for review: overview (whole course, top-down), and per hole: holeNN.png (3/4 view from behind the
    tee, HUD on), topdown_hNN.png and follow_hNN_a/b.png (chase cam during the intended first shot)."""
    st = Studio()
    st.stop_play()
    out_dir = args.out or os.path.join(GAME_DIR, "playtests", "lantern-v1")
    os.makedirs(out_dir, exist_ok=True)
    set_edit_attrs(st, {"GolfTestMode": True, "SimulateVR": False, "GolfTestCamera": ""})
    holes = [int(h) for h in args.holes.split(",")] if args.holes else list(range(1, 10))
    written = []
    def hud(on):
        st.luau("local g = game.Players.LocalPlayer.PlayerGui:FindFirstChild('GolfHUD') if g then g.Enabled = %s end "
                "local a = game.Players.LocalPlayer.PlayerGui:FindFirstChild('GolfAim') if a then a.Enabled = %s end return 'ok'" % (
                    "true" if on else "false", "true" if on else "false"), "Client")
    def snap(name):
        time.sleep(args.settle)
        path = os.path.join(out_dir, name)
        capture_window(w["id"], path)
        crop_viewport(path)
        written.append(path)
        log("shot", os.path.relpath(path, GAME_DIR))
    try:
        st.start_play()
        wait_api(st)
        st.luau("local SG = game:GetService('StarterGui') SG:SetCoreGuiEnabled(Enum.CoreGuiType.All, false) return 'ok'", "Client")
        w = window("front")
        if not w or "error" in w:
            raise SystemExit("Studio window not found: %s" % w)
        if not args.no_overview:
            hud(False)
            st.api("frame", "topdown", 0)
            snap("overview.png")
        for n in holes:
            r = st.api("place", n, "")
            if r != "ok":
                log("place", n, r)
            hud(False)
            st.api("frame", "topdown", n)
            snap("topdown_h%02d.png" % n)
            hud(True)
            st.api("frame", "hole", n)
            snap("hole%02d.png" % n)
            if not args.no_follow:
                hud(False)
                st.api("frame", "ball")
                time.sleep(1.0)
                st.api("putt", n, args.putt)
                time.sleep(args.follow_delay)
                capture_window(w["id"], os.path.join(out_dir, "follow_h%02d_a.png" % n))
                crop_viewport(os.path.join(out_dir, "follow_h%02d_a.png" % n))
                time.sleep(1.6)
                capture_window(w["id"], os.path.join(out_dir, "follow_h%02d_b.png" % n))
                crop_viewport(os.path.join(out_dir, "follow_h%02d_b.png" % n))
                written += [os.path.join(out_dir, "follow_h%02d_%s.png" % (n, k)) for k in "ab"]
        st.api("frame", "clear")
        problems = {"server": st.problems("Server"), "client": st.problems("Client")}
    finally:
        st.stop_play()
        clear_test_attrs(st)
    print(json.dumps({"written": [os.path.relpath(p, GAME_DIR) for p in written], "problems": problems}, indent=1))


def cmd_overview(args):
    """World overview stills from Edit mode (the play client stops drawing terrain/parts from ~1000 studs up):
    overview.png (top-down over the world map's terrain extent) and overview_aerial.png (world.json vista 4 view).
    Haze is switched off for the shot and restored."""
    import base64
    st = Studio()
    st.stop_play()
    out_dir = args.out or os.path.join(GAME_DIR, "playtests", "lantern-v1")
    os.makedirs(out_dir, exist_ok=True)
    saved = st.luau("local a = game.Lighting:FindFirstChildOfClass('Atmosphere') local d = a and a.Density or -1 "
                    "if a then a.Density = 0 end return tostring(d)", "Edit")
    views = [("overview.png", [40, 900, 1], [40, 0, 0]), ("overview_aerial.png", [230, 300, 340], [10, 20, -20])]
    try:
        for name, cam, look in views:
            r = st.m.req("tools/call", {"name": "screen_capture", "arguments": {
                "studio_id": st.id, "capture_id": name, "camera_position": cam, "look_at_position": look}})
            img = [c for c in r["result"]["content"] if c.get("type") == "image"][0]
            tmp = os.path.join(out_dir, name + ".jpg")
            with open(tmp, "wb") as fh:
                fh.write(base64.b64decode(img["data"]))
            subprocess.run(["uv", "run", "-q", "--with", "pillow", "python", "-c",
                            "import sys; from PIL import Image; Image.open(sys.argv[1]).save(sys.argv[2])", tmp,
                            os.path.join(out_dir, name)], check=True, timeout=120)
            os.remove(tmp)
            log("shot", name)
    finally:
        if float(saved) >= 0:
            st.luau("game.Lighting:FindFirstChildOfClass('Atmosphere').Density = %s return 'ok'" % saved, "Edit")


def cmd_list(args):
    # read from the src/ mirror of GolfClient.GolfTest so this works without a playtest running
    names = []
    for line in open(os.path.join(SRC_DIR, "StarterPlayer", "StarterPlayerScripts", "GolfClient", "GolfTest.luau")):
        m = re.match(r'\s*name = "([\w-]+)",', line)
        d = re.match(r'\s*desc = "(.*)",', line)
        if m:
            names.append([m.group(1), ""])
        elif d and names and '" ..' not in d.group(1):
            names[-1][1] = d.group(1)
        elif re.match(r'\s*name = "h" \.\. n,', line):
            names += [["h%d" % n, "hole %d suite: intended lines, HIO line + search, rail banks, mover timing sweep, fuzz" % n]
                      for n in range(1, 10)]
    for n, d in names:
        print("%-10s %s" % (n, d))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    ov = sub.add_parser("overview")
    ov.add_argument("--out")
    r = sub.add_parser("run")
    r.add_argument("scenarios", nargs="*")
    r.add_argument("--cams", default="")
    r.add_argument("--record", action="store_true")
    r.add_argument("--out")
    r.add_argument("--rect", help="x,y,w,h screen rect to record instead of the Studio window")
    r.add_argument("--no-vr", action="store_true", help="don't set SimulateVR (ledge/ghost are skipped)")
    r.add_argument("--opts", help="JSON options for the per-hole suites (workspace.GolfTestOpts)")
    hs = sub.add_parser("holes")
    hs.add_argument("holes", nargs="*")
    hs.add_argument("--opts")
    hs.add_argument("--out")
    hs.add_argument("--engine-sim", action="store_true", help="seed the HIO search with tools/engine_sim.py lines")
    sh = sub.add_parser("shots")
    sh.add_argument("--out")
    sh.add_argument("--holes")
    sh.add_argument("--settle", type=float, default=2.5)
    sh.add_argument("--follow-delay", type=float, default=1.0)
    sh.add_argument("--putt", default="hio")
    sh.add_argument("--no-follow", action="store_true")
    sh.add_argument("--no-overview", action="store_true")
    s = sub.add_parser("smoke")
    s.add_argument("--wait", type=float, default=10)
    s.add_argument("--device", help="Studio device emulation, e.g. iphone_17_pro")
    s.add_argument("--shots", type=int, default=15, help="seconds of normal play before checking")
    sub.add_parser("export")
    cv = sub.add_parser("clubviz")
    cv.add_argument("--out")
    cv.add_argument("--views", default="side,front,top,side_close,front_close")
    cv.add_argument("--prefix", default="")
    cv.add_argument("--settle", type=float, default=3.0)
    cv.add_argument("--no-crop", action="store_true")
    p = sub.add_parser("push")
    p.add_argument("files", nargs="+")
    c = sub.add_parser("compare")
    c.add_argument("before")
    c.add_argument("after")
    args = ap.parse_args()
    {"list": cmd_list, "run": cmd_run, "holes": cmd_holes, "shots": cmd_shots, "smoke": cmd_smoke, "export": cmd_export, "push": cmd_push, "compare": cmd_compare,
     "clubviz": cmd_clubviz, "overview": cmd_overview}[args.cmd](args)


if __name__ == "__main__":
    main()
