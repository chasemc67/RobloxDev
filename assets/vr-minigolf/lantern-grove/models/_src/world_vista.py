"""Pass 3: world-scale vista checks (PREVIEW ONLY: the terrain mesh here is never exported; Studio uses Terrain).

  blender -b -P models/_src/world_vista.py [-- --views v1,v2] [-- --samples 24] [-- --res 1280]
Writes models/world/previews/vista_<name>.png from the camera points in world/README.md (vista_prompts).
Scene: terrain-4stud.json heightfield (material colours from the legend) + water cells, a far apron plane,
holes.json felt/walls placed with world.json placements, the hole hero props and lantern posts (models/fbx),
and every world piece instance from models/world/layout.json (models/world/fbx).
"""
import sys, os, math
from mathutils import Vector
SRC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC)
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
VIEWS = argv[argv.index("--views") + 1].split(",") if "--views" in argv else None
SCENE_OPTS = dict(samples=int(argv[argv.index("--samples") + 1]) if "--samples" in argv else 24,
                  res=int(argv[argv.index("--res") + 1]) if "--res" in argv else 1280, dressing=True, lights=True)
import world_scene as S
import bpy

CAMS = {
    "h1_tee_to_tree": dict(pos=(190.0, 29.5, 170.0), bearing=302, pitch=7, fov=70),
    "lookout_rock": dict(pos=(166.0, 53.0, -80.0), bearing=293, pitch=-7, fov=100),
    "root_stair": dict(pos=(22.0, 28.7, -10.0), bearing=326, pitch=6, fov=75),
    "aerial": dict(pos=(200.0, 320.0, 330.0), bearing=315, pitch=-38, fov=60),
}
def render(name, c):
    S.cam.location = S.BL(c["pos"])
    b_ = math.radians(c["bearing"])
    p_ = math.radians(c["pitch"])
    d = Vector((math.sin(b_) * math.cos(p_), math.cos(b_) * math.cos(p_), math.sin(p_)))
    S.cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    S.cam.data.angle = math.radians(c["fov"])
    S.sc.render.filepath = os.path.join(S.OUTD, "previews", f"vista_{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"[vista] {name}")


for name, c in CAMS.items():
    if VIEWS and name not in VIEWS:
        continue
    render(name, c)
