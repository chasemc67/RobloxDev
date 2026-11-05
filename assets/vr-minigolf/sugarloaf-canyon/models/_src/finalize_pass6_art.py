"""Pass 6 artifacts (system Python + Pillow): _src/reimport_pass6.txt (latest re-import record of every pass-6 FBX),
contact_sheet.png (hero block kept, piece grid rebuilt incl. pass-6 pieces), and with --compare the labelled
previews/hero/V1-hub-tee1_pass6_vs_concept.png.     python _src/finalize_pass6_art.py [--compare]
"""
import json, math, sys, time, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
SRC = Path(__file__).resolve().parent
MODELS = SRC.parent
COURSE = MODELS.parent
HERO = MODELS / "previews" / "hero"
fp = Path("C:/Windows/Fonts/segoeui.ttf")
font = ImageFont.truetype(str(fp), 20) if fp.exists() else ImageFont.load_default()
small = ImageFont.truetype(str(fp), 14) if fp.exists() else ImageFont.load_default()


def log(s):
    line = time.strftime("%Y-%m-%d %H:%M:%S") + " " + s
    print(line)
    with (SRC / "PROGRESS.md").open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def reimport():
    recs = json.loads((SRC / "_cache" / "pass6_build.json").read_text())
    runs = sorted((SRC / "_cache").glob("reimport_pass6_*.json"), key=lambda p: p.stat().st_mtime)
    latest = {}
    for r in runs:
        if r.stem.endswith("step1"):
            continue
        for e in json.loads(r.read_text()):
            latest[e["file"]] = (e, r)
    lines = [f"Pass 6 FBX re-import check ({time.strftime('%Y-%m-%d %H:%M')}): every new/changed pass-6 FBX re-imported "
             "into a clean factory Blender 5.2 scene with the default FBX importer (forward -Z, up Y); checks: single "
             "root Empty named after the file, MeshPart names <part>__<Material> match the build, material per mesh, "
             "world scale 1, tri count = built, Roblox bbox size + centre-from-pivot = built (0.02), every mesh < 20k tris; "
             "embedded textures listed. Source: _cache/reimport_pass6_<run>.json (latest run per file).", ""]
    s1 = json.loads((SRC / "_cache" / "pass6_step1.json").read_text())
    lines += ["STEP 1 (gondola tower recolour on the unchanged pass-5 line, before step 1b):",
              f"  pass 5: tris {s1['pass5']['tris']} bbox {s1['pass5']['bbox']} centre {s1['pass5']['centre']}",
              f"  recolour: tris {s1['pass6_recolour']['tris']} bbox {s1['pass6_recolour']['bbox']} centre "
              f"{s1['pass6_recolour']['centre']}; re-import tris {s1['pass6_recolour']['reimport_tris']} -> "
              f"{'IDENTICAL geometry' if s1['identical_geometry'] else 'DIFFERENT'}", ""]
    ok_all, n = True, 0
    for pid, rec in recs.items():
        for part in rec["parts"]:
            f = part["file"]
            e, run = latest.get(f, (None, None))
            fbx = MODELS / f
            stale = e is None or fbx.stat().st_mtime > run.stat().st_mtime
            ok = e is not None and e["ok"] and not stale and e["tris"] == part["tris"]
            ok_all &= ok
            n += 1
            if e is None:
                lines.append(f"FAIL {f}: no re-import record")
                continue
            lines.append(f"{'PASS' if ok else 'FAIL'} {f}  [{run.stem}]")
            lines.append(f"  root {e['root']} | meshes {len(e['meshes'])} (names ok {e['names_ok']}, materials ok {e['mat_ok']}) | "
                         f"tris {e['tris']} = built {e['built_tris']} | max mesh {e['max_mesh_tris']} | scale ok {e['scale_ok']}")
            lines.append(f"  bbox {e['bbox']} centre {e['centre']} vs built {e['built_bbox']} / {e['built_centre']} (ok {e['bbox_ok']})"
                         + (" | STALE (FBX newer than check)" if stale else ""))
            if e["images"]:
                lines.append(f"  images: {', '.join(e['images'])}")
    lines += ["", f"RESULT: {'ALL PASS' if ok_all else 'FAIL'} ({n} FBX files)"]
    (SRC / "reimport_pass6.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return ok_all, n


def contact():
    man = json.loads((MODELS / "manifest.json").read_text())
    bak = SRC / "backup_pass6" / "contact_sheet.png"
    if not bak.exists():
        Image.open(MODELS / "contact_sheet.png").save(bak)
    hero = Image.open(bak).convert("RGB").crop((0, 0, 1600, 1520))
    previews = []
    for p in man["pieces"]:
        c = [MODELS / s.replace("\\", "/") for s in p.get("previews", []) if (MODELS / s.replace("\\", "/")).exists()]
        if not c:
            c = sorted((MODELS / "previews").glob(p["id"] + "_eye.png")) + sorted((MODELS / "previews").glob(p["id"] + "_34.png"))
        if c:
            previews.append((p["id"], c[-1], p["tris"]))
    root = Image.new("RGB", (1600, 1520 + math.ceil(len(previews) / 5) * 218), "#211a21")
    root.paste(hero, (0, 0))
    d = ImageDraw.Draw(root)
    for k, (name, path, t) in enumerate(previews):
        x, y = (k % 5) * 320, 1520 + (k // 5) * 218
        th = ImageOps.contain(Image.open(path).convert("RGB"), (316, 188))
        root.paste(th, (x + (320 - th.width) // 2, y))
        d.text((x + 6, y + 191), f"{name} / {t:,} tris", font=small, fill="#ffe7cc")
    root.save(MODELS / "contact_sheet.png")
    return len(previews), root.size


def compare():
    r = Image.open(HERO / "V1-hub-tee1_pass6.png").convert("RGB").resize((960, 540))
    c = Image.open(COURSE / "world" / "vistas" / "V1-hub-tee1.png").convert("RGB").resize((960, 540))
    sh = Image.new("RGB", (1920, 580), "#211a21")
    d = ImageDraw.Draw(sh)
    sh.paste(r, (0, 0))
    sh.paste(c, (960, 0))
    d.text((14, 548), "V1-hub-tee1 pass 6 render (Cycles OptiX 1920x1080, 128 spp, denoised)", font=font, fill="#ffe7cc")
    d.text((974, 548), "V1-hub-tee1 concept (world/vistas/V1-hub-tee1.png)", font=font, fill="#ffe7cc")
    sh.save(HERO / "V1-hub-tee1_pass6_vs_concept.png")


if __name__ == "__main__":
    if "--compare" in sys.argv:
        compare()
        log("Pass6: previews/hero/V1-hub-tee1_pass6_vs_concept.png written")
    else:
        ok, n = reimport()
        k, size = contact()
        log(f"Pass6 art: reimport_pass6.txt {'ALL PASS' if ok else 'FAIL'} ({n} FBX); contact_sheet.png {size} with {k} thumbnails")
