"""v210b: manifest bookkeeping that build_all does not do (plain python, idempotent).
  * dressing.holes.H3 / H8 fbx[0]: triangle counts after dedupe_v210b (4 duplicate oak quads = 8 tris removed each)
  * previews[] of the 6 rebuilt / new props -> previews/v210b/
  * top-level 'v210b' block: what changed + what RobloxDevBot has to do in Studio
python3 manifest_v210b.py <models dir>
"""
import json, os, sys

ROOT = sys.argv[1]
mp = os.path.join(ROOT, "manifest.json")
man = json.load(open(mp))
ded = json.load(open(os.path.join(ROOT, "_src", "dedupe_v210b.json")))

for H, name in (("H3", "dressing_h03_a"), ("H8", "dressing_h08_a")):
    e = [f for f in man["dressing"]["holes"][H]["fbx"] if f["fbx"] == f"fbx/{name}.fbx"][0]
    after = ded[name]["tris_after"]
    for p in e["parts"]:
        p["tris"] = after[p["mesh"]]
    e["triangles"] = sum(after.values())
    e["v210b"] = (f"{ded[name]['removed'][name + '__Oak']['polygons']} duplicate oak faces removed (lantern-pole post "
                  "bottoms coplanar with their slate footing bottoms); every other polygon unchanged. Hole-level "
                  "'triangles' / 'stats' are the dressing-pass instance budget and were not re-summed (-8 tris).")

# previews of the rebuilt / new props live in previews/v210b/ (build_all renders moved there)
for e in man["props"]:
    if e["name"] in ("bank_backing_stone", "h8_alcove_bank_cladding", "rail_straight_4_h9", "rail_straight_2_h9",
                     "rail_end_post_h9", "h9_bank_lip"):
        e["previews"] = [f"previews/v210b/{e['name']}_v210b_{v}.png" for v in ("eye", "34")]
        assert all(os.path.exists(os.path.join(ROOT, q)) for q in e["previews"]), e["previews"]

man["v210b"] = dict(
    note=("v210b (2026-10-12, playtest round 8 + H9 game-art review). Bank backings H3/H8/H9 render as stone #B8AFA0 "
          "wherever visible; duplicate oak faces removed; H9 rails oak, limestone only on H9 posts + bank backing; "
          "mint lip on the H9 bank top edge. holes.json (rails, rail16, banks) and mover speeds untouched. Supersedes "
          "v210.roblox['bank_backing_stone__OakDeep'] (that part no longer exists)."),
    changed_fbx=["fbx/bank_backing_stone.fbx", "fbx/h8_alcove_bank_cladding.fbx", "fbx/dressing_h03_a.fbx",
                 "fbx/dressing_h08_a.fbx"],
    new_fbx=["fbx/rail_straight_4_h9.fbx", "fbx/rail_straight_2_h9.fbx", "fbx/rail_end_post_h9.fbx",
             "fbx/h9_bank_lip.fbx"],
    exported_with="Blender 5.2.2 LTS (same FBX settings as fbx_export)",
    roblox={
        "bank_backing_stone": ("Re-import (all 5 placements). One MeshPart __Limestone: Color #B8AFA0, Material "
                               "Limestone, SurfaceAppearance limestone.png. Delete the old __OakDeep and __Moss "
                               "MeshParts. Move the H8 bank2_backing instance to hole-local (-17.7753, 1.5, -40.7753) "
                               "yaw 135 (was z -49.7753, 9 studs off its wall)."),
        "rail_kit_on_backing_walls": ("Delete any rail-kit piece / end post standing on a *_backing wall (H3 bank1/2, "
                                      "H8 bank1/2, H9 bank1): bank_backing_stone is their visual, a rail kit there "
                                      "is the duplicate cap / z-fights with the stone."),
        "h8_alcove_bank_cladding": ("Re-import. One MeshPart __Limestone (#B8AFA0, Limestone, limestone.png); delete "
                                    "the old __RootBark and __Moss MeshParts."),
        "H9_rails": ("Every H9 rail wall: rail_straight_*_trim -> rail_straight_*_h9 (one MeshPart __OakDeep: Color "
                     "#7A4E32, Material WoodPlanks, Reflectance 0, no SurfaceAppearance); end posts "
                     "rail_end_post_trim -> rail_end_post_h9 (__Limestone #B8AFA0). Same placement rule. H8 keeps the "
                     "trim kit."),
        "h9_bank_lip": ("New: one MeshPart h9_bank_lip__BankLip at the H9 bank1_backing pos/yaw. Color #6CC79F, "
                        "Material SmoothPlastic, Reflectance 0, CanCollide/CanQuery/CanTouch false, Anchored, no "
                        "PointLight / no Neon."),
        "dressing_h03_a, dressing_h08_a": "Re-import (4 duplicate oak faces removed in each, nothing else changed).",
        "movers": "No speed changes (Studio's job).",
    },
    checks="_src/fitcheck_v210b_validated.txt, _src/reimport_v210b.json, _src/coplanar_v210b.json, _src/dedupe_v210b.json",
)
json.dump(man, open(mp, "w"), indent=1)
print("manifest v210b block written;", {H: [f["triangles"] for f in man["dressing"]["holes"][H]["fbx"]] for H in ("H3", "H8")})
