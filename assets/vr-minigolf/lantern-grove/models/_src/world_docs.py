"""Pass 3 docs: models/world/contact_sheet_world.png + _src/world_readme.md (appended to models/README.md by
make_docs.py). System python3 + Pillow.  python3 models/_src/world_docs.py"""
import json, os
from PIL import Image, ImageDraw, ImageFont

SRC = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.dirname(SRC)
OUTD = os.path.join(MODELS, "world")
man = json.load(open(os.path.join(OUTD, "manifest.json")))
P = man["pieces"]
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f1, f2 = ImageFont.truetype(FONT, 15), ImageFont.truetype(FONT_R, 12)

# ----------------------------------------------------------------------------- contact sheet
cells = []
for p in P:
    for pv in p["previews"]:
        if p["id"].startswith("treeline_clump") and not p["id"].endswith(("gold_orange", "red_orange")) \
                and not pv.endswith("_34.png"):
            continue
        cells.append((p, pv))
vistas = sorted(f for f in os.listdir(os.path.join(OUTD, "previews")) if f.startswith("vista_"))
CW = 230
cols = 6
rows = (len(cells) + cols - 1) // cols
VW = (cols * (CW + 8)) // 2 - 8
VH = VW * 9 // 16
vrows = (len(vistas) + 1) // 2
sheet = Image.new("RGB", (cols * (CW + 8) + 16, 64 + rows * (CW + 44) + vrows * (VH + 30) + 10), (24, 26, 30))
d = ImageDraw.Draw(sheet)
tot = sum(p["tris"] for p in P)
d.text((14, 14), f"Lantern Grove world pieces (pass 3): {len(P)} pieces, "
       f"{sum(len(p['files']) for p in P)} FBX, {tot:,} tris; vistas below", font=ImageFont.truetype(FONT, 22),
       fill=(242, 182, 50))
y = 56
for i, (p, pv) in enumerate(cells):
    x0 = 12 + (i % cols) * (CW + 8)
    y0 = y + (i // cols) * (CW + 44)
    fp = os.path.join(OUTD, pv)
    if os.path.exists(fp):
        sheet.paste(Image.open(fp).convert("RGB").resize((CW, CW)), (x0, y0))
    lab = os.path.basename(pv)[:-4].replace(p["id"] + "_", "")
    d.text((x0, y0 + CW + 2), p["id"][:28], font=f1 if len(p["id"]) < 24 else f2, fill=(240, 240, 240))
    sz = "x".join(f"{v:.0f}" for v in p["bbox_size_studs"])
    d.text((x0, y0 + CW + 22), f"{lab}  {sz}  {p['tris']}t  x{len(p['instances'])}", font=f2, fill=(255, 179, 71))
y += rows * (CW + 44)
for i, v in enumerate(vistas):
    x0 = 12 + (i % 2) * (VW + 8)
    y0 = y + (i // 2) * (VH + 30)
    sheet.paste(Image.open(os.path.join(OUTD, "previews", v)).convert("RGB").resize((VW, VH)), (x0, y0))
    d.text((x0, y0 + VH + 4), v[:-4], font=f1, fill=(240, 240, 240))
sheet.save(os.path.join(OUTD, "contact_sheet_world.png"))

# ----------------------------------------------------------------------------- README section
L = []
A = L.append
A("## World pieces")
A("")
A("Pass 3 adds world-scale background meshes for the continuous world in `../world/` (world.json, terrain, "
  "placements). They live in `models/world/`:")
A("")
A("| Path | What |")
A("|---|---|")
A("| `world/fbx/<id>.fbx`, `world/fbx/<id>_partN.fbx` | One FBX per piece, or several parts that share one origin (every file < 20k tris) |")
A("| `world/manifest.json` | Every piece: files, parts (role, tris, bbox, meshes/materials), origin, notes, **instances** (world pos / yaw / scale) |")
A("| `world/layout.json` | Just the instances (written by `_src/world_layout.py`) |")
A("| `world/previews/<id>_34.png` (+ `hollow_tree_world_shell_door/cutaway/top_fit.png`) | Piece previews |")
A("| `world/previews/vista_*.png` | World vistas over a preview-only terrain mesh (holes as felt boxes) |")
A("| `world/contact_sheet_world.png` | All previews + vistas |")
A("| `world/fitcheck_world.txt` | Hero tree vs H8/H9/walkways fit check (`_src/world_fitcheck.py`) |")
A("")
A("**Import (RobloxDevBot):**")
A("")
A("1. File > Import 3D each FBX with the **scale unit Stud** (same as the props), keep the hierarchy: one Model per "
  "file, one MeshPart per material `<part>__<Material>`. Set Color/Material/Transparency from the material table "
  "above (new world materials are listed below). Anchored, `CanCollide = CanQuery = CanTouch = false` (all decoration).")
A("2. **Positions are world studs** (+X east, +Y up, -Z north, the same frame as world.json and the placed holes), and "
  "they are the **base centre** of the piece (exceptions are in the `origin` column). Every part of a multi-part piece "
  "has the same origin, so put the parts in one Model and pivot the Model.")
A("3. Place each instance with `Model:PivotTo(CFrame.new(pos[1], pos[2], pos[3]) * CFrame.Angles(0, math.rad(yaw), 0))`. "
  "If the pivot did not survive import, set `Model.WorldPivot` to the FBX origin first (see Pivot above: "
  "`bbox_center_from_origin` per part is in world/manifest.json). `scale` [sx, sy, sz]: equal values -> "
  "`Model:ScaleTo(s)`; otherwise scale each MeshPart's Size and its offset from the pivot per axis (rock kits, tree "
  "line, hills and mountains are fine with this).")
A("4. Far pieces (mountains, far hills, clouds, tree line): `CastShadow = false`, `RenderFidelity = Performance`. "
  "Neon parts (Glow) get PointLights only on the hero tree and near pieces.")
A("5. Hero tree extras: SurfaceLight / Beam light shaft from the oculus (r 14, top of the hollow at y 117.6) down onto "
  "H9; PointLights in the lanterns of `hollow_tree_world_shell_part6/7` and `hollow_tree_crown_part1`.")
A("")
A("**Hero tree origin**: `hollow_tree_world_shell` origin = trunk base centre **[-74, 39.6, 6]** (yaw 0): local y 0 = "
  "the H9 floor (terrain 39.6). The skirt goes 4.6 below it so the shell meets uneven terrain. Door at map angle "
  "53.1 deg (atan2(dz, dx)). `hollow_tree_crown` origin = crown base centre **[-74, 139.6, 6]**; its limbs dip 3 "
  "below it into the trunk top. H9 needs no change: place the holes as in world/README.md.")
A("")
A("New materials (world pieces only):")
A("")
A("| Material | Colour | Roblox Material | Transparency | Texture |")
A("|---|---|---|---|---|")
import sys as _sys
_sys.path.insert(0, SRC) if "SRC" in globals() else None
_WM = ["Heartwood", "MountainFoot", "MountainPeach", "MountainMauve", "MountainSnow", "SkyPaper", "Cloud", "CloudShade", "Mist"]
_WMAT = {"Heartwood": ("#B9783F", "Wood", 0, "textures/heartwood.png (tile 12 on the shell)"),
         "MountainFoot": ("#EDC6A8", "SmoothPlastic", 0, "(flat) = horizon sky haze"),
         "MountainPeach": ("#D8A38E", "SmoothPlastic", 0, "(flat)"),
         "MountainMauve": ("#AE8890", "SmoothPlastic", 0, "(flat)"),
         "MountainSnow": ("#F8EDE6", "SmoothPlastic", 0, "(flat)"),
         "SkyPaper": ("#F6A04A", "SmoothPlastic", 0, "textures/paper_glow.png, self-lit (SurfaceAppearance ColorMap; Neon-like glow via PointLight)"),
         "Cloud": ("#FFE6BE", "SmoothPlastic", 0, "(flat)"), "CloudShade": ("#E9B7A4", "SmoothPlastic", 0, "(flat)"),
         "Mist": ("#F3F7F8", "SmoothPlastic", 0.45, "(flat)")}
for m in _WM:
    hx, rb, tr, tx = _WMAT[m]
    A(f"| `{m}` | `{hx}` | {rb} | {tr} | {tx} |")
A("")
A("Textures: world pieces reuse `textures/*.png` with bigger tiles (`texture_tile_scale` per part: x3 for the trunk "
  "shell, x4 for the crown, x2-8 for the rest), so bark and leaves keep a sensible size at world scale.")
A("")
A("| Piece | Kind | Files | Tris (max part) | Size [x,y,z] | Instances | Origin |")
A("|---|---|---|---|---|---|---|")
for p in P:
    fs = ", ".join(f"`{os.path.basename(f)}`" for f in p["files"]) if len(p["files"]) <= 2 else \
        f"`{os.path.basename(p['files'][0])}` .. `{os.path.basename(p['files'][-1])}` ({len(p['files'])})"
    sz = "[" + ", ".join(f"{v:g}" for v in p["bbox_size_studs"]) + "]"
    A(f"| **{p['id']}** | {p['kind']} | {fs} | {p['tris']} ({p['max_part_tris']}) | {sz} | {len(p['instances'])} | {p['origin']} |")
A("")
for p in P:
    if p["id"].startswith("treeline_clump") and not p["id"].endswith("gold_orange"):
        continue
    A(f"- **{p['id']}**: {p['notes']}")
A("")
fc = os.path.join(OUTD, "fitcheck_world.txt")
if os.path.exists(fc):
    A("### Hero tree fit check (`_src/world_fitcheck.py`)")
    A("")
    A("```")
    A(open(fc).read().rstrip())
    A("```")
    A("")
A("Rebuild: `python3 _src/world_layout.py && blender -b -P _src/world_build.py && blender -b -P _src/world_fitcheck.py "
  "&& blender -b -P _src/world_vista.py && python3 _src/world_docs.py && python3 _src/make_docs.py` "
  "(or `_src/build_world.sh`).")
A("")
open(os.path.join(SRC, "world_readme.md"), "w").write("\n".join(L) + "\n")
print("world docs:", len(P), "pieces,", len(cells), "cells,", len(vistas), "vistas")
