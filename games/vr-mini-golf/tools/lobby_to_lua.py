#!/usr/bin/env python3
"""Lobby data for Studio: assets/vr-mini-golf/lobby/boardwalk (lobby.json + models/manifest.json, both from
RobloxDevBot / 3D Model Bot) + tools/lobby_overrides.json -> src/ServerStorage/CourseData/LobbyLayout.luau.

    python3 tools/lobby_to_lua.py              # regenerate (then push it and run LobbyBuilder.Build())
    python3 tools/lobby_to_lua.py --check-board  # spawn-eye sight lines to the arch openings vs the course board

A revised manifest/lobby.json re-imports with this one step; fixes live in lobby_overrides.json.
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.dirname(HERE)
ASSETS = os.path.expanduser("~/src/RobloxDev/assets/vr-mini-golf/lobby/boardwalk")
OUT = os.path.join(GAME, "src", "ServerStorage", "CourseData", "LobbyLayout.luau")


LUA_KEYWORDS = {"and", "break", "do", "else", "elseif", "end", "false", "for", "function", "if", "in", "local", "nil",
                "not", "or", "repeat", "return", "then", "true", "until", "while", "continue"}


def lua(v, ind=0):
    pad = "\t" * ind
    if v is None:
        return "nil"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        r = round(float(v), 4)
        return str(int(r)) if r == int(r) else repr(r)
    if isinstance(v, str):
        return json.dumps(v)
    if isinstance(v, list):
        if all(not isinstance(x, (dict, list)) for x in v):
            return "{ " + ", ".join(lua(x) for x in v) + " }"
        return "{\n" + "".join(pad + "\t" + lua(x, ind + 1) + ",\n" for x in v) + pad + "}"
    if isinstance(v, dict):
        items = []
        for k, x in v.items():
            key = k if k.isidentifier() and k not in LUA_KEYWORDS else "[%s]" % json.dumps(k)
            items.append(pad + "\t" + key + " = " + lua(x, ind + 1) + ",\n")
        return "{\n" + "".join(items) + pad + "}"
    raise TypeError(v)


def board_sightlines(lobby, board_pos, yaw_deg, size=(26, 10.75, 2)):
    """Fraction of sample points across each portal opening visible from the spawn eye past the board box."""
    eye = (lobby["spawn"]["position"][0], 5.0, lobby["spawn"]["position"][2])
    yaw = math.radians(yaw_deg)
    s, c = math.sin(yaw), math.cos(yaw)
    axes = (((c, 0, -s), size[0] / 2), ((0, 1, 0), size[1] / 2), ((s, 0, c), size[2] / 2))
    o = (board_pos[0], size[1] / 2, board_pos[2])

    def hits(p):
        d = [p[i] - eye[i] for i in range(3)]
        t0, t1 = 0.0, 1.0
        for a, h in axes:
            rel = sum((eye[i] - o[i]) * a[i] for i in range(3))
            dd = sum(d[i] * a[i] for i in range(3))
            if abs(dd) < 1e-9:
                if abs(rel) > h:
                    return False
                continue
            u, v = sorted(((-h - rel) / dd, (h - rel) / dd))
            t0, t1 = max(t0, u), min(t1, v)
            if t0 > t1:
                return False
        return True

    out = {}
    for p in lobby["portals"]:
        x, _, z = p["position"]
        pts = [(x + dx, y, z) for dx in (-5, -2.5, 0, 2.5, 5) for y in (0.5, 3, 6, 9, 12)]
        out[p["id"]] = sum(not hits(q) for q in pts) / len(pts)
    return out


def main():
    lobby = json.load(open(os.path.join(ASSETS, "lobby.json")))
    man = json.load(open(os.path.join(ASSETS, "models", "manifest.json")))
    ov = json.load(open(os.path.join(HERE, "lobby_overrides.json")))
    props = {p["name"]: p for p in man["props"]}
    spawn = lobby["spawn"]["position"]

    insts, applied = [], []
    for i in man["instances"]:
        i = dict(i)
        o = ov["instances"].get(i["id"], {})
        for k in ("position", "yaw", "scale"):
            if k in o:
                i[k] = o[k]
        if o.get("faceSpawn"):
            i["yaw"] = round(math.degrees(math.atan2(spawn[0] - i["position"][0], spawn[2] - i["position"][2])), 2)
        if o:
            applied.append(i["id"])
        info = props[i["asset"]]
        scal = info.get("scalable") or ""
        sc = i.get("scale")
        if sc and i["asset"] not in ov.get("noScale", {}):
            sc = [sc[0] if "x" in scal else 1, sc[1] if "y" in scal else 1, sc[2] if "z" in scal else 1]
            sc = None if all(abs(v - 1) < 1e-4 for v in sc) else sc
        else:
            sc = None
        insts.append({"id": i["id"], "asset": i["asset"], "position": i["position"], "yaw": i.get("yaw", 0),
                      "scale": sc, "solid": bool(i.get("solid"))})
    missing = set(ov["instances"]) - set(applied)
    if missing:
        sys.exit("override ids not in the manifest: %s" % sorted(missing))

    assets = {}
    for name, p in props.items():
        assets[name] = {
            "bbox": p["bbox_size_studs"],
            "center": p["bbox_center_from_pivot"],
            "parts": [{"mesh": q["mesh"], "center": q["center_from_pivot"], "color": q["color"],
                       "material": q["roblox_material"]} for q in p["parts"]],
            "collision": [{"center": c["center"], "size": c["size"]} for c in (p.get("collision") or [])],
            "motion": ({"axis": p["motion"]["axis_roblox"], "rpm": p["motion"]["rpm"]} if p.get("motion") else None),
        }

    board = next(i for i in insts if i["id"] == "course_board")
    sight = board_sightlines(lobby, board["position"], board["yaw"])
    if "--check-board" in sys.argv:
        print(json.dumps({"board": board, "visible": sight}))
        return

    data = {
        "name": lobby["name"],
        "origin": ov["origin"],
        "spawn": lobby["spawn"],
        "bounds": lobby["bounds"],
        "walkways": lobby["walkwayColliders"],
        "railings": lobby["railings"],
        "lighting": lobby["lighting"],
        "portals": [{"id": p["id"], "position": p["position"], "courseId": p["courseId"], "state": p["state"]} for p in lobby["portals"]],
        "boardSightlines": sight,
        "instances": insts,
        "assets": assets,
    }
    head = ("-- GENERATED by tools/lobby_to_lua.py from assets/vr-mini-golf/lobby/boardwalk/{lobby.json, models/manifest.json}\n"
            "-- + tools/lobby_overrides.json (stage t fixes: %s). Do not edit by hand.\n" % ", ".join(applied))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write(head + "return " + lua(data) + "\n")
    print("wrote", OUT, len(insts), "instances,", len(assets), "assets; board sight lines", sight)


if __name__ == "__main__":
    main()
