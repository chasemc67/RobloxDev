"""Find / raise the Roblox Studio window for a place (macOS).

Run with:  uv run --with pyobjc-framework-Quartz --with pyobjc-framework-Cocoa python studio_window.py <cmd> [title-prefix]
  list            all on-screen Roblox Studio windows as JSON
  rect  [prefix]  {"x","y","w","h","pid","id","title"} of the first window whose title starts with prefix
  front [prefix]  bring that window's app to the front, then print its rect
"""
import json
import sys

import Quartz

OWNER = "Roblox Studio"


def windows():
    opts = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    out = []
    for w in Quartz.CGWindowListCopyWindowInfo(opts, Quartz.kCGNullWindowID) or []:
        owner = w.get("kCGWindowOwnerName", "")
        if "Roblox" not in owner:
            continue
        b = w.get("kCGWindowBounds", {})
        out.append({
            "owner": owner,
            "title": w.get("kCGWindowName", "") or "",
            "pid": int(w.get("kCGWindowOwnerPID", 0)),
            "id": int(w.get("kCGWindowNumber", 0)),
            "layer": int(w.get("kCGWindowLayer", 0)),
            "x": int(b.get("X", 0)), "y": int(b.get("Y", 0)),
            "w": int(b.get("Width", 0)), "h": int(b.get("Height", 0)),
        })
    return out


def find(prefix):
    cands = [w for w in windows() if w["layer"] == 0 and w["title"].startswith(prefix) and w["w"] > 400]
    cands.sort(key=lambda w: -w["w"] * w["h"])
    return cands[0] if cands else None


def front(pid):
    from AppKit import NSRunningApplication
    app = NSRunningApplication.runningApplicationWithProcessIdentifier_(pid)
    if app is not None:
        app.activateWithOptions_(3)  # NSApplicationActivateAllWindows | IgnoringOtherApps


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    prefix = sys.argv[2] if len(sys.argv) > 2 else "VR Mini Golf"
    if cmd == "list":
        print(json.dumps(windows(), indent=1))
    else:
        w = find(prefix)
        if w is None:
            print(json.dumps({"error": "no window titled %r" % prefix}))
            sys.exit(1)
        if cmd == "front":
            front(w["pid"])
            import time
            time.sleep(0.8)
            w = find(prefix) or w
        print(json.dumps(w))
