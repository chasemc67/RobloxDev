"""Pass 6 finalize extension: new kit pieces, per-hole dressing (props / plants / ground), trading post and the reworked
cliff kit merged into manifest + layout (called by finalize_pass6.py after the gondola section)."""
import json
from pathlib import Path

SRC = Path(__file__).resolve().parent
CACHE = SRC / "_cache"
KIT = ["trading_post_deck", "barrel_a", "barrel_b", "lantern_post", "lantern_hanging", "lollipop_cactus_cluster",
       "rock_candy_cluster", "gumdrop_shrub_a", "gumdrop_shrub_b", "gumdrop_shrub_c", "boulder_scatter",
       "fallen_rock_scatter", "red_dirt_patch_a", "red_dirt_patch_b", "pebble_scatter", "clay_brick_edging"]


def apply(man, lay, recs):
    info = {}
    old = {p["id"]: i for i, p in enumerate(man["pieces"])}

    def put(rec):
        rec = dict(rec)
        rec.setdefault("world_json_size", None)
        rec.setdefault("world_json_ids", [])
        rec["instances"] = []
        if rec["id"] in old:
            man["pieces"][old[rec["id"]]] = rec
        else:
            old[rec["id"]] = len(man["pieces"])
            man["pieces"].append(rec)

    for k in KIT:
        if k in recs:
            put(recs[k])
    lp = CACHE / "pass6_layout.json"
    if lp.exists():
        d = json.loads(lp.read_text())
        tp = d.get("trading_post")
        if tp:
            lay["instances"].append(dict(piece="trading_post_deck", pos=tp["pos"], yaw=tp["yaw"], src="pass6:h01 tee",
                                         note="trading-post boardwalk beside the H1 tee (west of the lane, front faces "
                                              "the lane); >= 3 studs from rail1 for everything taller than 2"))
        dress = {}
        for hid, h in d["holes"].items():
            pieces = []
            for part in ("props", "plants", "ground"):
                name = f"{hid}_dress_{part}" if part != "ground" else f"{hid}_ground"
                if name not in recs or not h["counts"].get(part):
                    continue
                put(recs[name])
                lay["instances"].append(dict(piece=name, pos=h["pivot"], yaw=0.0, src=f"pass6:{hid}",
                                             note=f"H{h['number']} merged {part} dressing; geometry baked at world "
                                                  "offsets from the tee pivot, so yaw stays 0"))
                pieces.append(name)
            kinds = {}
            for m in h["members"]:
                kinds[m["kind"]] = kinds.get(m["kind"], 0) + 1
            dress[hid] = dict(hole=h["number"], name=h["name"], pieces=pieces, pivot=h["pivot"],
                              tris={p: recs[p]["tris"] for p in pieces},
                              clusters=[dict(anchor=c["anchor"], centre=c.get("centre"), members=c["members"])
                                        for c in h["clusters"]],
                              members=[dict(kind=m["kind"], pos=m["pos"], yaw=m["yaw"], scale=m["scale"],
                                            anchor=m["anchor"]) for m in h["members"]],
                              member_kinds=kinds, ground=dict(h["ground"]["stats"], pebbles=len(h["ground"]["pebbles"]),
                                                              bricks=len(h["ground"]["bricks"]),
                                                              brick_skips=h["ground"]["brick_skips"]))
        info["dressing"] = dict(rules=d["rules"], layout="_cache/pass6_layout.json (sc_dress_pass6.py)",
                                trading_post=tp, holes=dress)
    cp = CACHE / "pass6_cliffs.json"
    if cp.exists():
        c = json.loads(cp.read_text())
        for pid in c["pieces"]:
            if pid in recs:
                put(recs[pid])
        swap = c.get("swap", {})          # "piece|x|y|z|yaw" -> new piece id (top-of-stack tower variants)
        for inst in lay["instances"]:
            key = "|".join([inst["piece"]] + [str(v) for v in inst["pos"]] + [str(inst["yaw"])])
            if key in swap:
                inst["note"] = (inst.get("note", "") + f"; pass 6: top of stack -> {swap[key]}").lstrip("; ")
                inst["piece"] = swap[key]
        info["cliffs"] = {k: v for k, v in c.items() if k not in ("swap",)}
    info["renders"] = dict(
        script="_src/render_hero_pass6.py", final="previews/hero/V1-hub-tee1_pass6.png",
        compare="previews/hero/V1-hub-tee1_pass6_vs_concept.png", report="previews/hero/pass6_render_report.json",
        light="key sun 277/4 (orange, shadowed), no-shadow orange rim sun 285/3, peach-to-gold camera sky, AgX Punchy",
        staging="render-only: holes.json felt + rounded clay-brick curbs (replace the pass-5 candy rails), cups/flags")
    info["slab_finding"] = ("The dark slab right of the H1 lane near the H2 green in V1-hub-tee1_staged.png is KIT geometry: "
                            "three walk_boardwalk_6x12 instances (layout src paths:p_h1_h2, pos (76.36,18,432.49), "
                            "(77.64,18,429.51), (85.82,18,422.54)) - the Junction boardwalk planks on p_h1_h2 segs 1-2, "
                            "dark Timber with plank gaps at a grazing angle. Not a shadow, hazard/drop volume or staging "
                            "artefact; left unchanged (floor kit).")
    return info
