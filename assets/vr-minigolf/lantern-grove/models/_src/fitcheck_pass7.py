# Pass 7 fit checks (flags enlarged, H8 Firefly Hollow dressing, darker felt with a stronger nap). exec()'d by fitcheck.py
# after fitcheck_pass6.py (the flag size / pennant LOS checks live there). Generic dressing checks (keep-outs, tall
# props >= 3 studs from rails, near field <= 34k, spots clear of keep-outs) already cover every new instance.
lines.append("")
lines.append("# pass 7: Firefly Hollow (H8), cup flags, felt")
d8 = DH.get("H8", {})
hol = [it for it in d8.get("instances", []) if it["role"] == "hollow"]
alc = [it for it in hol if math.hypot(it["pos"][0] - 8.5, it["pos"][2] + 11.5) <= 9.0]
kinds = {it["prop"] for it in hol}
check("H8 Firefly Hollow: >= 10 hollow props (fireflies + glow shrooms + roots), >= 5 around the alcove, all 4 kinds",
      len(hol) >= 10 and len(alc) >= 5 and kinds >= {"firefly_cluster_low", "firefly_swarm", "glow_shroom_patch",
                                                      "glow_root_arch"},
      f"{len(hol)} hollow, {len(alc)} by the alcove, kinds {sorted(kinds)}")
glow = {p["name"]: {q["material"] for q in p["parts"]} for p in man["props"] if p["name"] in kinds}
check("hollow props glow (Firefly / ShroomGlow Neon parts) and stay cheap (<= 300 tris each)",
      all(m_ & {"Firefly", "ShroomGlow"} for m_ in glow.values()) and
      all(p["triangles"] <= 300 for p in man["props"] if p["name"] in kinds),
      ", ".join(f"{p['name']} {p['triangles']}" for p in man["props"] if p["name"] in kinds))
st8 = d8.get("stats", {})
p7 = st8.get("pass7_vs_pass6", {})
check("H8 richer than pass 6 and its near field still <= 34k",
      p7.get("instances_after", 0) > p7.get("pass6_instances", 99) and st8.get("near_field_tris_after", 1e9) <= 34000,
      f"{p7.get('pass6_instances')} -> {p7.get('instances_after')} instances, near field "
      f"{st8.get('near_field_tris_after')}")
ffs = [q for q in d8.get("spot_lights", []) if q.get("kind") == "firefly_glow"]
check("H8 firefly_glow spot lights present (checked clear of keep-outs above)", len(ffs) >= 1, f"{len(ffs)} spots")


def _img_stats(path):
    im = bpy.data.images.load(path, check_existing=False)
    px = np.array(im.pixels[:], float).reshape(-1, 4)[:, :3]
    bpy.data.images.remove(im)
    return px.mean(0), px.std(0)


tx = os.path.join(OUTD, "textures")
fm, fs = _img_stats(os.path.join(tx, "felt.png"))
bm_, _bs = _img_stats(os.path.join(tx, "felt_bright.png"))
nm_, ns = _img_stats(os.path.join(tx, "felt_normal.png"))
# pass 6 values (felt.png mean G 135/255, felt_normal x/y std 37/22 in 0..255): darker felt, >= 1.5x nap normal
check("felt darker than pass 6 (mean G < 0.5), felt_bright >= 1.3x brighter, nap normal >= 1.5x pass 6 strength",
      fm[1] < 0.5 and bm_[1] >= 1.3 * fm[1] and ns[0] >= 1.5 * 37 / 255,
      f"felt G {fm[1]:.3f}, bright G {bm_[1]:.3f}, normal std x {ns[0] * 255:.1f}")
# the cup-pool spots hang >= 1.5 from the (bigger) pennant, so it is not blown out in the tee view
sp_bad, sp_info = [], []
for n in (8, 9):
    for q in DH.get(f"H{n}", {}).get("spot_lights", []):
        if q["over"] != "cup":
            continue
        fp = MP[f"cup_flag_h{n:02d}"]
        T, mats = placed_local(fp["name"], fp["placements"][0])
        V = T[mats == "FlagRed"].reshape(-1, 3)
        dmin = float(np.linalg.norm(V - np.array(q["pos"]), axis=1).min())
        sp_info.append(f"H{n} {dmin:.2f}")
        if dmin < 1.5:
            sp_bad.append(f"H{n} cup spot {dmin:.2f} from the pennant")
check("H8/H9 cup-pool spot lights >= 1.5 studs from the cup-flag pennant", not sp_bad,
      "; ".join(sp_bad) if sp_bad else ", ".join(sp_info))
