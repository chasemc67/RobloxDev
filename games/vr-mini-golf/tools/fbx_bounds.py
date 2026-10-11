#!/usr/bin/env python3
"""Per-mesh bounding boxes of a binary FBX (3D Model Bot's Blender exports), in Roblox axes, relative to the FBX
origin (= the prop's pivot). Used by props_to_lua.py when an FBX is newer than models/manifest.json (props_overrides
"fbx_refresh"), so PropsBuilder.PrepareLibrary can fit the import from the real mesh centres.

  python3 -I tools/fbx_bounds.py path/to/prop.fbx

Blender writes the vertices Z-up (the -90 deg X turn lives on the Model node), so Roblox = (x, z, -y).
"""
import json
import struct
import sys
import zlib


def _nodes(b):
    big = struct.unpack_from("<I", b, 23)[0] >= 7500
    hdr = 25 if big else 13

    def node(o):
        end, nprops, _ = struct.unpack_from("<QQQ" if big else "<III", b, o)
        o += 24 if big else 12
        nl = b[o]
        o += 1
        if end == 0:
            return None, o
        name = b[o:o + nl].decode("latin1")
        o += nl
        props = []
        for _ in range(nprops):
            t = chr(b[o])
            o += 1
            if t in "YCIFDL":
                fmt = {"Y": "<h", "C": "<?", "I": "<i", "F": "<f", "D": "<d", "L": "<q"}[t]
                props.append(struct.unpack_from(fmt, b, o)[0])
                o += struct.calcsize(fmt)
            elif t in "fdlib":
                n, enc, cl = struct.unpack_from("<III", b, o)
                o += 12
                raw = b[o:o + cl]
                o += cl
                if enc:
                    raw = zlib.decompress(raw)
                props.append(struct.unpack("<%d%s" % (n, {"f": "f", "d": "d", "l": "q", "i": "i", "b": "?"}[t]), raw))
            elif t in "SR":
                n = struct.unpack_from("<I", b, o)[0]
                o += 4
                props.append(b[o:o + n])
                o += n
        kids = []
        while o < end - hdr:
            c, o = node(o)
            if c is None:
                break
            kids.append(c)
        return {"name": name, "props": props, "kids": kids}, end

    o, top = 27, []
    while o < len(b) - hdr:
        n, o = node(o)
        if n is None:
            break
        top.append(n)
    return top


def mesh_bounds(path):
    """{mesh name: {"center": [x, y, z], "size": [x, y, z]}} in Roblox studs/axes."""
    top = {n["name"]: n for n in _nodes(open(path, "rb").read())}
    geo, models = {}, {}
    for k in top["Objects"]["kids"]:
        if k["name"] == "Geometry":
            geo[k["props"][0]] = next(c for c in k["kids"] if c["name"] == "Vertices")["props"][0]
        elif k["name"] == "Model":
            models[k["props"][0]] = k["props"][1].split(b"\x00")[0].decode()
    out = {}
    for c in top["Connections"]["kids"]:
        g, m = c["props"][1], c["props"][2]
        if g in geo and m in models:
            v = geo[g]
            lo = [min(v[0::3]), min(v[2::3]), -max(v[1::3])]
            hi = [max(v[0::3]), max(v[2::3]), -min(v[1::3])]
            out[models[m]] = {"center": [round((a + b) / 2, 3) + 0.0 for a, b in zip(lo, hi)],
                              "size": [round(b - a, 3) for a, b in zip(lo, hi)]}
    return out


def prop_bounds(parts):
    lo = [min(p["center"][i] - p["size"][i] / 2 for p in parts.values()) for i in range(3)]
    hi = [max(p["center"][i] + p["size"][i] / 2 for p in parts.values()) for i in range(3)]
    return {"center": [round((a + b) / 2, 3) + 0.0 for a, b in zip(lo, hi)], "size": [round(b - a, 3) for a, b in zip(lo, hi)]}


if __name__ == "__main__":
    parts = mesh_bounds(sys.argv[1])
    print(json.dumps({"parts": parts, "prop": prop_bounds(parts)}, indent=1))
