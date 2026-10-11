#!/usr/bin/env python3
"""Convert 3D Model Bot's prop manifest (models/manifest.json + models/library/library.json) into the PropPlacements
ModuleScript that ServerStorage.PropsBuilder reads.

  python3 tools/props_to_lua.py             # write src/ServerStorage/CourseData/PropPlacements.luau
  python3 tools/props_to_lua.py --push      # ...and copy it into Studio

Contents: per-mesh materials (Color/Material/Transparency), the library grid offsets (how the bundled FBXs were laid
out), hero/structure/moving placements (props[].placements) and the per-hole set dressing (dressing.holes[].instances,
.lights). All positions are hole-local (holes.json frame); PropsBuilder applies each hole's world frame.
Library FBXs: assets/vr-mini-golf/lantern-grove/models/library/make_library.py (Blender), imported with Studio's
3D Importer (tools/codex_ui.sh).
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from holes_to_lua import GAME_DIR, REPO, to_lua  # noqa: E402

MODELS = os.path.join(REPO, "assets", "vr-mini-golf", "lantern-grove", "models")
OVERRIDES = os.path.join(HERE, "props_overrides.json")  # spec changes newer than the manifest (see its note)
DEFAULT_OUT = os.path.join(GAME_DIR, "src", "ServerStorage", "CourseData", "PropPlacements.luau")


def r3(v):
    return [round(float(x), 3) for x in v]


def apply_overrides(placements):
    """Patch hero placements from tools/props_overrides.json; returns what was applied (also kept in the module)."""
    if not os.path.exists(OVERRIDES):
        return []
    ov = json.load(open(OVERRIDES))
    applied = []
    for o in ov.get("placements", []):
        prop, hole, pos = o["match"]
        hit = [e for e in placements if e["prop"] == prop and e["hole"] == hole
               and max(abs(a - b) for a, b in zip(e["pos"], pos)) < 0.05]
        if not hit:
            print("override did not match (manifest updated?):", o["match"])
            continue
        for e in hit:
            if o.get("remove"):
                placements.remove(e)
            else:
                e.update({k: (r3(v) if isinstance(v, list) and k == "pos" else v) for k, v in o["set"].items()})
        applied.append(o.get("why", prop))
    for a in ov.get("add", []):
        e = {k: a[k] for k in ("prop", "hole", "pos", "yaw") if k in a}
        for k in ("scale", "motion", "light", "chain_top", "light_id"):
            if k in a:
                e[k] = a[k]
        placements.append(e)
        applied.append(a.get("why", a["prop"]))
    return applied


def convert():
    raw = open(os.path.join(MODELS, "manifest.json"), "rb").read()
    man = json.loads(raw)
    lib = json.load(open(os.path.join(MODELS, "library", "library.json")))
    out = {"source": {"file": os.path.relpath(os.path.join(MODELS, "manifest.json"), REPO), "sha1": hashlib.sha1(raw).hexdigest()},
           "library": {}, "parts": {}, "props": {}, "placements": [], "dressing": {}, "lights": {}}
    for b, v in lib["bundles"].items():
        out["library"][b] = {k: r3(e["offset"]) for k, e in v["props"].items()}
    for p in man["props"]:
        info = {"kind": p["kind"], "group": p["group"], "bbox": r3(p["bbox_size_studs"]),
                "center": r3(p["bbox_center_from_origin"]), "tris": p["triangles"]}
        if p.get("motion"):
            m = p["motion"]
            info["motion"] = {"id": m.get("holes_json_id"), "type": m.get("type")}
        out["props"][p["name"]] = info
        for part in p["parts"]:
            out["parts"][part["mesh"]] = {"color": part["color"], "material": part["roblox_material"],
                                          "transparency": part.get("transparency", 0)}
            if "bbox_center_from_origin" in part:
                # per-mesh centre relative to the prop origin: PrepareLibrary fits single-file imports with it
                out["parts"][part["mesh"]]["center"] = r3(part["bbox_center_from_origin"])
        for pl in p["placements"]:
            e = {"prop": p["name"], "hole": int(pl["hole"][1:]), "pos": r3(pl["pos"]), "yaw": pl.get("yaw", 0)}
            if "scale" in pl:
                e["scale"] = pl["scale"] if isinstance(pl["scale"], (int, float)) else r3(pl["scale"])
            if "scale_z_to" in pl:
                e["scale_z_to"] = pl["scale_z_to"]
            out["placements"].append(e)
    applied = apply_overrides(out["placements"])
    for hk, h in man["dressing"]["holes"].items():
        n = int(hk[1:])
        out["dressing"][str(n)] = [{"prop": i["prop"], "pos": r3(i["pos"]), "yaw": round(i.get("yaw", 0), 1),
                                    "scale": round(i.get("scale", 1), 3), "role": i.get("role")} for i in h["instances"]]
        out["lights"][str(n)] = [r3(l if isinstance(l, list) else l.get("pos")) for l in h.get("lights", [])]
    # pass-8 PointLights (manifest lights[]). The 3 H9 hanging lanterns carry their light on the lantern's own Neon
    # part (props_overrides.json adds with light_id take range/brightness/colour from here), so only the rail/glow
    # lights become stand-alone lights. Rail lights also get their post's base + yaw (dressing instance with the same
    # light_id) so PropsBuilder can stand a post on the ground until the rail_lantern_* meshes are imported.
    base = {}
    for hk, h in man["dressing"]["holes"].items():
        for i in h["instances"]:
            if i.get("light_id"):
                base[i["light_id"]] = {"base": r3(i["pos"]), "yaw": round(i.get("yaw", 0), 1), "prop": i["prop"]}
    by_id = {l["id"]: l for l in man.get("lights", [])}
    for e in out["placements"]:
        lid = e.pop("light_id", None)
        if lid:
            l = by_id[lid]
            e["light"] = {"range": l["range"], "brightness": l["brightness"], "color3": l["color3"], "id": lid}
    out["pointLights"] = []
    for l in man.get("lights", []):
        if l["kind"] == "hanging_lantern":
            continue
        e = {"id": l["id"], "hole": int(l["hole"][1:]), "kind": l["kind"], "pos": r3(l["pos"]),
             "color3": l["color3"], "range": l["range"], "brightness": l["brightness"], "prop": l.get("prop")}
        e.update(base.get(l["id"], {}))
        out["pointLights"].append(e)
    # the H8 firefly-swarm glow spots (dressing.holes.H8.spot_lights kind firefly_glow; pass 8: Brightness 3.5, Range 14)
    for hk, h in man["dressing"]["holes"].items():
        for l in h.get("spot_lights", []):
            if l.get("kind") == "firefly_glow":
                out["pointLights"].append({"id": l["id"], "hole": int(hk[1:]), "kind": l["kind"], "pos": r3(l["pos"]),
                                           "color3": [int(l["color"][i:i + 2], 16) for i in (1, 3, 5)],
                                           "range": l["range"], "brightness": l["brightness"]})
    out["overrides"] = applied
    src = to_lua(out)
    for n in range(1, 10):
        src = src.replace('["%d"] = ' % n, "[%d] = " % n)
    head = ("-- GENERATED by games/vr-mini-golf/tools/props_to_lua.py from the 3D Model Bot manifest (sha1 %s).\n"
            "-- Read by ServerStorage.PropsBuilder. Positions are hole-local (holes.json frame).\n" % out["source"]["sha1"][:12])
    return head + "return " + src + "\n", out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--push", action="store_true")
    args = ap.parse_args()
    src, data = convert()
    with open(args.out, "w") as fh:
        fh.write(src)
    print("wrote %s (%d bytes, %d props, %d placements, %d dressing instances)" % (
        os.path.relpath(args.out, GAME_DIR), len(src), len(data["props"]), len(data["placements"]),
        sum(len(v) for v in data["dressing"].values())))
    if args.push:
        import run_playtests as rp  # noqa: E402
        st = rp.Studio()
        if st.mode()[0] != "Edit":
            raise SystemExit("stop play first")
        rp.cmd_push(argparse.Namespace(files=[args.out]), st)


if __name__ == "__main__":
    main()
