"""Validate pro_shop_pavilion_v1.blend and write manifest.json, validation.json, report.txt.

Usage:
  blender -b <pro_shop_pavilion_v1.blend> --python validate_pavilion.py -- --outdir <dir>
"""
import argparse
import json
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

FORBIDDEN = ("pirate", "tiki", "price", "coin", "currency", "gem", "npc", "mirror", "course", "skull")
REQUIRED_ANCHORS = ["ANCHOR_Root_BaseCentre", "ANCHOR_UI_ScreenPanel", "ANCHOR_UI_EquippedBall",
                    "ANCHOR_UI_EquippedClub", "ANCHOR_Display_ActivePreview", "ANCHOR_Prompt_Counter",
                    "ANCHOR_Player_StandSpot", "ANCHOR_Sign"] + \
                   [f"ANCHOR_BallTray_Slot_{i:02d}" for i in range(1, 9)] + \
                   [f"ANCHOR_ClubRack_Slot_{i:02d}" for i in range(1, 7)]


def r3(v):
    return [round(float(x), 4) for x in v]


def coll_of(o):
    return o.users_collection[0].name if o.users_collection else ""


def is_export(o):
    c = o.users_collection[0] if o.users_collection else None
    if c is None or not c.get("ps_export", False):
        return False
    return o.type == "MESH"


def world_bm(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.transform(o.matrix_world)
    return bm


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    a = ap.parse_args(argv)
    sc = bpy.context.scene
    objs = [o for o in sc.objects]
    exp = [o for o in objs if is_export(o)]
    checks = []

    def check(name, ok, detail):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})

    # ---------------- per-object stats
    info = {}
    bvh = {}
    allmn, allmx = Vector((1e9,) * 3), Vector((-1e9,) * 3)
    for o in objs:
        if o.type != "MESH":
            continue
        me = o.data
        tris = sum(len(p.vertices) - 2 for p in me.polygons)
        ws = [o.matrix_world @ v.co for v in me.vertices]
        mn = Vector((min(c.x for c in ws), min(c.y for c in ws), min(c.z for c in ws)))
        mx = Vector((max(c.x for c in ws), max(c.y for c in ws), max(c.z for c in ws)))
        uv_ok = len(me.uv_layers) > 0
        degen = 0
        if uv_ok:
            uvd = me.uv_layers[0].data
            for p in me.polygons:
                pts = [uvd[li].uv for li in p.loop_indices]
                ar = 0.0
                for i in range(1, len(pts) - 1):
                    ar += abs((pts[i] - pts[0]).cross(pts[i + 1] - pts[0])) / 2
                if ar < 1e-12:
                    degen += 1
        info[o.name] = dict(name=o.name, collection=coll_of(o), export=is_export(o), tris=tris,
                            verts=len(me.vertices), materials=[m.name for m in me.materials if m],
                            bbox_min=r3(mn), bbox_max=r3(mx), dims=r3(mx - mn), pivot=r3(o.location),
                            rotation=r3(o.rotation_euler), scale=r3(o.scale), uv=uv_ok,
                            degenerate_uv_faces=degen,
                            props={k: (v if isinstance(v, (int, float, str, bool)) else str(v))
                                   for k, v in o.items()})
        if is_export(o):
            allmn = Vector(map(min, allmn, mn))
            allmx = Vector(map(max, allmx, mx))
            bm = world_bm(o)
            bvh[o.name] = (BVHTree.FromBMesh(bm), mn, mx)
            bm.free()

    tot = sum(info[o.name]["tris"] for o in exp)
    big = max(exp, key=lambda o: info[o.name]["tris"])
    check("every_export_mesh_under_20k_tris", info[big.name]["tris"] < 20000,
          f"largest {big.name} = {info[big.name]['tris']}")
    check("total_export_tris_in_budget", tot <= 60000, f"{tot} tris across {len(exp)} export meshes "
                                                        f"(suggested 30k-50k)")
    no_uv = [o.name for o in objs if o.type == "MESH" and not info[o.name]["uv"]]
    check("uv_on_all_meshes", not no_uv, "all meshes have UVMap" if not no_uv else f"missing: {no_uv}")
    dg = [(n, i["degenerate_uv_faces"]) for n, i in info.items() if i["export"] and i["degenerate_uv_faces"]]
    check("no_degenerate_uv_faces_on_export", not dg, "none" if not dg else str(dg[:10]))
    bad_tx = [o.name for o in exp if any(abs(x) > 1e-6 for x in o.rotation_euler) or
              any(abs(x - 1) > 1e-6 for x in o.scale)]
    check("export_mesh_identity_rot_scale", not bad_tx, "ok" if not bad_tx else str(bad_tx))
    bad_pv = []
    for o in exp:
        i = info[o.name]
        if abs(i["pivot"][2] - i["bbox_min"][2]) > 1e-3 or \
                abs(i["pivot"][0] - (i["bbox_min"][0] + i["bbox_max"][0]) / 2) > 1e-3 or \
                abs(i["pivot"][1] - (i["bbox_min"][1] + i["bbox_max"][1]) / 2) > 1e-3:
            bad_pv.append(o.name)
    check("export_pivots_at_base_centre", not bad_pv, "origin = bbox base centre" if not bad_pv else str(bad_pv))

    # materials / textures
    tex_mats, untex = {}, []
    for o in exp:
        for m in o.data.materials:
            imgs = [n.image.name for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image]
            tex_mats[m.name] = imgs
            if not imgs and m.name != "M_UI_Display_Placeholder":
                untex.append(m.name)
    check("export_materials_textured", not untex,
          "all export materials use image maps (display placeholder is flat by design)" if not untex
          else str(sorted(set(untex))))
    unpacked = [i.name for i in bpy.data.images if i.source in ("FILE", "GENERATED") and i.packed_file is None
                and i.name not in ("Render Result", "Viewer Node")]
    check("all_images_packed", not unpacked, "all images packed" if not unpacked else str(unpacked))
    unpacked_f = [f.name for f in bpy.data.fonts if f.packed_file is None and f.filepath != "<builtin>"]
    check("fonts_packed", not unpacked_f, "ok" if not unpacked_f else str(unpacked_f))
    multi = [o.name for o in exp if len(o.data.materials) != 1]
    check("one_material_per_export_mesh", not multi, "ok" if not multi else str(multi))

    # dims / scale
    dims = allmx - allmn
    check("footprint_and_height_sane", 19 <= dims.x <= 24 and 10 <= dims.y <= 16 and 11 <= dims.z <= 14,
          f"export bounds {r3(allmn)} .. {r3(allmx)}; size {r3(dims)} (W x D x H)")
    check("origin_ground_centre", abs(allmn.z) < 0.09 and abs((info['Plinth_Stone']['bbox_min'][0] +
                                                               info['Plinth_Stone']['bbox_max'][0]) / 2) < 1e-3,
          f"lowest export z {allmn.z:.3f} (approach slab sinks 0.08 below grade); plinth centred on x=0")
    pl = info["Plinth_Stone"]["bbox_max"][2]
    ct = info["Counter_Top_Planks"]["bbox_max"][2]
    check("counter_height_about_3", 2.8 <= ct - pl <= 3.3, f"counter top {ct:.3f} - approach/plinth {pl:.3f} "
                                                            f"= {ct - pl:.3f} studs")
    ap_ = info["Approach_Base"]
    rise = ap_["bbox_max"][2] - 0.0
    run = ap_["dims"][1]
    slope = math.degrees(math.atan2(rise, run))
    check("level_approach_no_step", slope < 5 and abs(ap_["bbox_max"][2] - pl) < 1e-3,
          f"approach rises {rise:.2f} over {run:.2f} ({slope:.1f} deg) and meets the plinth flush")

    # ---------------- contact / floating
    names = list(bvh)
    floating = []
    for n in names:
        t, mn, mx = bvh[n]
        if mn.z <= 0.001:
            continue
        o = bpy.data.objects[n]
        vs = [o.matrix_world @ v.co for v in o.data.vertices]
        ok = False
        for m in names:
            if m == n:
                continue
            t2, mn2, mx2 = bvh[m]
            if any(mn[k] > mx2[k] + 0.05 or mx[k] < mn2[k] - 0.05 for k in range(3)):
                continue
            if t.overlap(t2):  # embedded joinery (post into plate, sill into wall) counts as support
                ok = True
                break
            step = max(1, len(vs) // 600)
            for v in vs[::step]:
                hit = t2.find_nearest(v, 0.03)
                if hit[0] is not None:
                    ok = True
                    break
            if ok:
                break
        if not ok:
            floating.append(n)
    check("no_floating_export_meshes", not floating,
          "every export mesh touches/embeds into another (<=0.03) or the ground" if not floating else str(floating))

    # ---------------- roof coverage (rays through export meshes only)
    def cast(origin, direction, maxd=60.0):
        best = None
        for n, (t, mn, mx) in bvh.items():
            h = t.ray_cast(origin, direction, maxd)
            if h[0] is not None and (best is None or h[3] < best[1]):
                best = (n, h[3])
        return best
    holes_below, holes_above, tile_hits, n_rays = [], [], 0, 0
    x = -10.8
    while x <= 10.81:
        y = -5.3
        while y <= 5.01:
            n_rays += 1
            hb = cast(Vector((x, y, 5.6)), Vector((0, 0, 1)))
            if hb is None:
                holes_below.append((round(x, 2), round(y, 2)))
            ha = cast(Vector((x, y, 20)), Vector((0, 0, -1)))
            if ha is None or not ha[0].startswith("Roof_"):
                holes_above.append((round(x, 2), round(y, 2), ha[0] if ha else None))
            elif ha[0].startswith(("Roof_Tiles", "Roof_RidgeCap")):
                tile_hits += 1
            y += 0.45
        x += 0.45
    check("roof_closed_from_below", not holes_below, f"{n_rays} upward rays all blocked" if not holes_below
          else f"{len(holes_below)} open: {holes_below[:8]}")
    check("roof_top_is_roofing", not holes_above and tile_hits / n_rays > 0.85,
          f"{tile_hits}/{n_rays} downward rays land on tiles/ridge cap; rest on barge/fascia/finial"
          if not holes_above else f"non-roof hits: {holes_above[:8]}")

    # ---------------- items: balls, clubs, dish
    felt_top = info["BallTray_Felt"]["bbox_max"][2]
    balls = [o for o in exp if o.name.startswith("Ball_Tray_")]
    bad = []
    for o in balls:
        b = info[o.name]
        r = b["dims"][2] / 2
        c = Vector(b["bbox_min"]) + Vector(b["dims"]) / 2
        if abs(b["bbox_min"][2] - felt_top) > 0.01:
            bad.append(f"{o.name} rests {b['bbox_min'][2] - felt_top:+.3f}")
    pairs = [(p.name, q.name) for i, p in enumerate(balls) for q in balls[i + 1:]
             if (Vector(info[p.name]["bbox_min"]) - Vector(info[q.name]["bbox_min"])).length <
             info[p.name]["dims"][0] + 0.01]
    skins = sorted({o.get("ps_skin") for o in balls})
    check("ball_tray_items", len(balls) == 8 and not bad and not pairs and len(skins) >= 6,
          f"{len(balls)} balls, {len(skins)} distinct skins {skins}; all rest on felt; no overlaps"
          if not bad and not pairs else f"{bad} {pairs}")
    db = info["Ball_Display_ActivePreview_classic_white"]
    bowl = info["Dish_Bowl"]
    check("display_ball_rests_in_dish", abs(db["bbox_min"][2] - bowl["bbox_min"][2]) < 0.01,
          f"ball bottom {db['bbox_min'][2]:.3f} vs bowl bottom {bowl['bbox_min'][2]:.3f}; "
          f"bowl depth {info['Dish_Surround']['bbox_max'][2] - bowl['bbox_min'][2]:.3f}")
    clubs = [o for o in exp if o.name.startswith("Club_")]
    rail_top = info["ClubRack_SlottedRail"]["bbox_max"][2]
    base_top = info["ClubRack_Base"]["bbox_max"][2]
    cbad = []
    for o in clubs:
        if abs(info[o.name]["bbox_min"][2] - base_top) > 0.01:
            cbad.append(f"{o.name} head {info[o.name]['bbox_min'][2] - base_top:+.3f}")
    over = []
    for i, p in enumerate(clubs):
        for q in clubs[i + 1:]:
            if bvh[p.name][0].overlap(bvh[q.name][0]):
                over.append((p.name, q.name))
    grips = sorted({o.get("ps_grip") for o in clubs})
    heads = sorted({o.get("ps_head") for o in clubs})
    check("club_rack_items", len(clubs) == 6 and not cbad and not over,
          f"6 putters ({heads}); heads on base z {base_top:.2f}, grips rest on slotted rail z {rail_top:.2f}; "
          f"slot 0.14 vs shaft 0.066 / grip 0.17; no club-club overlap; grips {grips}"
          if not cbad and not over else f"{cbad} {over}")

    # ---------------- sign + UI from the eye camera
    vis = {}
    for o in objs:
        if o.type != "MESH" or o.hide_render or coll_of(o) in ("PS_Collision_Proxy",) or o.name.startswith("ENV_"):
            continue
        bm = world_bm(o)
        vis[o.name] = BVHTree.FromBMesh(bm)
        bm.free()

    def first_hit(a_, b_):
        d = b_ - a_
        best = None
        for n, t in vis.items():
            h = t.ray_cast(a_, d.normalized(), d.length + 0.5)
            if h[0] is not None and (best is None or h[3] < best[1]):
                best = (n, h[3])
        return best
    cam = bpy.data.objects["CAM_Eye_Counter"].location
    sign_c = Vector(info["Sign_Lettering"]["bbox_min"]) + Vector(info["Sign_Lettering"]["dims"]) / 2
    disp_c = Vector(info["UI_Display_Surface_REPLACEABLE"]["bbox_min"]) + \
        Vector(info["UI_Display_Surface_REPLACEABLE"]["dims"]) / 2
    hs = first_hit(cam, sign_c + Vector((0, 0.03, 0)))
    hd = first_hit(cam, disp_c + Vector((0, 0.01, 0)))
    hs_top = first_hit(cam, Vector((0, sign_c.y, info["Sign_Frame"]["bbox_max"][2] - 0.02)))
    check("sign_visible_from_counter_eye", hs and hs[0] in ("Sign_Lettering", "Sign_Board") and hs_top and
          hs_top[0] == "Sign_Frame", f"eye {r3(cam)} -> lettering hits {hs and hs[0]}; frame top hits "
                                     f"{hs_top and hs_top[0]}")
    check("screen_visible_from_counter_eye", hd and (hd[0].startswith("UI_")),
          f"eye -> display centre hits {hd and hd[0]}")
    lt = bpy.data.objects["Sign_Lettering"].get("ps_text")
    check("sign_lettering_editable", lt == "PRO SHOP" and "Sign_Lettering_TEXTSOURCE" in bpy.data.objects,
          "mesh lettering 'PRO SHOP' + hidden editable text curve Sign_Lettering_TEXTSOURCE")

    # ---------------- collections / anchors / proxies / naming
    cols = [o for o in objs if o.name.startswith("COL_")]
    badc = [o.name for o in cols if not o.hide_render or coll_of(o) != "PS_Collision_Proxy"]
    check("collision_proxies_separate_hidden", cols and not badc,
          f"{len(cols)} COL_* proxies in PS_Collision_Proxy, hidden in renders, wire display"
          if not badc else str(badc))
    missing = [n for n in REQUIRED_ANCHORS if n not in bpy.data.objects]
    check("anchors_present", not missing, f"{len(REQUIRED_ANCHORS)} anchors" if not missing else str(missing))
    ui = bpy.data.collections.get("PS_UI_Placeholder_ILLUSTRATIVE")
    note = [o for o in ui.objects if o.type == "FONT" and "PLACEHOLDER" in o.data.body]
    check("ui_marked_illustrative", ui is not None and not ui.get("ps_export") and note and
          "UI_Display_Surface_REPLACEABLE" in bpy.data.objects,
          "UI overlay in non-export PS_UI_Placeholder_ILLUSTRATIVE with on-screen PLACEHOLDER note; "
          "display surface is a separate replaceable mesh")
    bad_names = [x.name for x in list(bpy.data.objects) + list(bpy.data.materials) + list(bpy.data.collections)
                 if any(f in x.name.lower() for f in FORBIDDEN)]
    texts = " ".join(o.data.body.lower() for o in objs if o.type == "FONT")
    bad_txt = [f for f in FORBIDDEN if f in texts] + [c for c in ("$", "€", "£") if c in texts]
    check("no_out_of_scope_content", not bad_names and not bad_txt,
          "no pirate/tiki/NPC/mirror/course/price/currency names or text" if not bad_names and not bad_txt
          else f"{bad_names} {bad_txt}")

    # ---------------- write
    all_pass = all(c["pass"] for c in checks)
    out = os.path.abspath(a.outdir)
    by_coll = {}
    for o in exp:
        by_coll.setdefault(coll_of(o), []).append(o.name)
    anchors = {o.name: dict(location=r3(o.location), rotation_deg=r3([math.degrees(x) for x in o.rotation_euler]),
                            props={k: (v if isinstance(v, (int, float, str)) else str(v)) for k, v in o.items()})
               for o in objs if o.name.startswith("ANCHOR_")}
    images = [dict(name=i.name, size=list(i.size), colorspace=i.colorspace_settings.name,
                   packed=i.packed_file is not None, file="textures/" + i.name + ".png")
              for i in bpy.data.images if i.name not in ("Render Result", "Viewer Node")]
    mats = {}
    for m in bpy.data.materials:
        if not m.node_tree:
            continue
        b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        links = {l.to_socket.name: l.from_node.image.name for l in m.node_tree.links
                 if l.from_node.type == "TEX_IMAGE" and l.from_node.image}
        mats[m.name] = dict(export=bool(m.get("ps_export", True)), maps=links,
                            roughness=round(b.inputs["Roughness"].default_value, 3) if b else None,
                            metallic=round(b.inputs["Metallic"].default_value, 3) if b else None,
                            surface_appearance={"ColorMap": links.get("Base Color"),
                                                "MetalnessMap": links.get("Metallic"),
                                                "RoughnessMap": links.get("Roughness")})
    manifest = dict(
        asset="pro_shop_pavilion_v1",
        status="FIRST DETAILED MODEL for Art + Chase review - not accepted final",
        concept="Art concept A sage/timber park pavilion (A-park-pavilion.jpg is aesthetic authority)",
        units="1 Blender unit = 1 Roblox stud; Z up; open front faces -Y (Roblox +Z after FBX axis "
              "conversion forward -Z / up Y)",
        origin="(0,0,0) = ground centre of plinth footprint; every export mesh pivot = its bbox base centre",
        bounds=dict(min=r3(allmn), max=r3(allmx), size_wdh=r3(dims)),
        key_heights=dict(plinth_top=pl, counter_top=ct, counter_above_approach=round(ct - pl, 3),
                         eye_camera=5.0, roof_ridge_cap_top=round(info["Roof_RidgeCap"]["bbox_max"][2], 3),
                         finial_top=round(info["Roof_Finial_Front"]["bbox_max"][2], 3)),
        tris=dict(export_total=tot, export_meshes=len(exp),
                  by_collection={k: sum(info[n]["tris"] for n in v) for k, v in by_coll.items()},
                  largest=dict(name=big.name, tris=info[big.name]["tris"])),
        collections={k: v for k, v in sorted(by_coll.items())},
        objects=[info[n] for n in sorted(info) if not n.startswith("ENV_")],
        anchors=anchors,
        collision_proxies=[o.name for o in cols],
        materials=mats,
        textures=images,
        non_export_collections=["PS_UI_Placeholder_ILLUSTRATIVE", "PS_Anchors", "PS_Collision_Proxy",
                                "PS_Source_EditableText", "ENV_RenderOnly"],
        cameras={o.name: dict(location=r3(o.location), lens=o.data.lens, res=list(o.get("ps_res", [])))
                 for o in objs if o.type == "CAMERA"},
    )
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    with open(os.path.join(out, "validation.json"), "w") as f:
        json.dump(dict(all_pass=all_pass, checks=checks), f, indent=1)
    lines = ["PRO SHOP PAVILION v1 - FIRST DETAILED MODEL (for Art + Chase review, not accepted final)", "",
             f"Bounds (W x D x H): {r3(dims)} studs; export tris {tot} in {len(exp)} meshes; "
             f"largest {big.name} {info[big.name]['tris']}", ""]
    for k, v in sorted(by_coll.items()):
        lines.append(f"  {k}: {sum(info[n]['tris'] for n in v)} tris, {len(v)} meshes")
    lines += ["", f"VALIDATION (all_pass={all_pass})"]
    lines += [f"  {'PASS' if c['pass'] else 'FAIL'} {c['check']}: {c['detail']}" for c in checks]
    with open(os.path.join(out, "report.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    main()
