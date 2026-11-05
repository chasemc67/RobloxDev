"""Prop registry for the Golden Hour Boardwalk lobby. Every generator registers itself here.

target: spec size [x, y, z] in Roblox studs (Y up) from props.md / builder_Lobby.luau; None = unchecked axis.
tris_max: per-mesh budget from brief_pass1.md (+ OVERRIDE limits for deck / railing).
front: which side of the prop's own (yaw 0) frame is the viewer side.
"""
PROPS = []
GROUPS = ("structure", "board", "arches", "green", "social", "backdrop")
FRONT_SOUTH = "+Z (Roblox, south, toward spawn) = Blender -Y"
FRONT_NORTH = "-Z (Roblox, north) = Blender +Y"
FRONT_NONE = "none (symmetric / tiling)"


def prop(name, group, *, target, tris_max, front=FRONT_NONE, pivot="base", collision=None, motion=None,
         notes="", scalable=None, tol=0.10, view=None):
    def deco(fn):
        PROPS.append(dict(name=name, group=group, target=target, tris_max=tris_max, front=front, pivot=pivot,
                          collision=collision, motion=motion, notes=notes, scalable=scalable, tol=tol, view=view,
                          fn=fn))
        return fn
    return deco


def by_name(n):
    return next(p for p in PROPS if p["name"] == n)


def load_all():
    import importlib, os
    here = os.path.dirname(os.path.abspath(__file__))
    for m in ("props_structure", "props_board", "props_arches", "props_green", "props_social", "props_backdrop"):
        if os.path.exists(os.path.join(here, m + ".py")):
            importlib.import_module(m)
    return PROPS
