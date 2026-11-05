"""Pass 5: merge the gondola_cable / gondola_cabin build records (_cache/pass5_build.json) into manifest.json and
layout.json, recompute totals and regenerate _src/pieces_table.md. Idempotent (replaces earlier gondola_* entries).
Backups of the pre-pass-5 files are in _src/backup_pass5/.   python _src/finalize_pass5.py
"""
import json, math, time
from pathlib import Path
import gondola_geom as G

SRC = Path(__file__).resolve().parent
MODELS = SRC.parent
NEW = ("gondola_cable", "gondola_cabin")


def r3(p):
    return [round(float(v), 3) for v in p]


def motion():
    ropes = G.ropes()
    out = {}
    for name, rope in ropes.items():
        A, Tw, B = rope
        L1, L2 = G.span_lengths(rope)
        # error of the linear-in-arc-length approximation w = s / L_span
        err = 0.0
        for k in range(0, 101):
            for (P, Q, sg, Ls, s0) in ((A, Tw, G.SAG[0], L1, 0.0), (Tw, B, G.SAG[1], L2, L1)):
                s = Ls * k / 100
                f = G.f_at_time(rope, (s0 + s) / G.SPEED)
                exact = G.rope_point(rope, f)
                approx = G.span_point(P, Q, s / Ls, sg)
                err = max(err, math.dist(exact, approx))
        table = []
        for t in range(0, int((L1 + L2) / G.SPEED) + 1, 10):
            table.append([t, r3(G.rope_point(rope, G.f_at_time(rope, t)))])
        table.append([round((L1 + L2) / G.SPEED, 2), r3(B)])
        out[name] = dict(A_bottom_attach=r3(A), T_tower_crest=r3(Tw), B_top_attach=r3(B),
                         span_arc_lengths=[round(L1, 2), round(L2, 2)], total_arc_length=round(L1 + L2, 2),
                         ride_seconds=round((L1 + L2) / G.SPEED, 2), linear_w_max_error_studs=round(err, 3),
                         samples_every_10s=table)
    return out


def main():
    recs = {r["id"]: r for r in json.loads((SRC / "_cache" / "pass5_build.json").read_text())}
    man = json.loads((MODELS / "manifest.json").read_text())
    lay = json.loads((MODELS / "layout.json").read_text())
    mo = motion()
    up, dn = mo["up_line"], mo["down_line"]
    cable_inst = dict(pos=r3(G.ORIGIN), yaw=0.0, src="lifts:Sunset Gondola",
                      note="world-placed static: pivot = bottom bull-wheel centre (line start); geometry already at world "
                           "offsets, so yaw stays 0")
    cabin_inst = dict(pos=r3(up["A_bottom_attach"]), yaw=G.CABIN_YAW_UP, src="lifts:Sunset Gondola",
                      note="moving cabin parked at the bottom-station boarding point (grip on the up-line rope where it "
                           "leaves the bull wheel; floor 0.4 above the platform). Travels the up line to the top at 6 "
                           "studs/s, see manifest gondola_cabin.motion")
    formula = (
        "Pivot (grip) path along a rope = two parabolic spans A->T (sag 10) and T->B (sag 2.5) in WORLD coords: "
        "P_span(w) = P + (Q - P)*w - (0, 4*sag*w*(1-w), 0), w in [0,1]. Travel: s(t) = 6*t studs of rope arc length; "
        "on span 1 (0 <= s <= L1) w solves arclen_AT(w) = s, on span 2 w solves arclen_TB(w) = s - L1. "
        "Numerically w ~= s/L1 (span 1) and (s-L1)/L2 (span 2) is within linear_w_max_error_studs of the exact "
        "arc-length position (sags are 1.8% / 1.5% of the spans). Cabin stays level (hanger pivots), yaw constant: up "
        f"line yaw {G.CABIN_YAW_UP} (front local -Z toward the top station), down line yaw {G.CABIN_YAW_UP + 180:.2f} "
        "from B to A. Roblox: cabin:PivotTo(CFrame.new(P(t)) * CFrame.Angles(0, math.rad(yaw), 0)) each Heartbeat. "
        "At the tower crest T the path has a 28 deg slope break (20.4 deg up -> 7.6 deg down).")
    entries = {}
    for pid in NEW:
        r = dict(recs[pid])
        r["world_json_size"] = None
        r["world_json_ids"] = ["lifts:Sunset Gondola"]
        r["instances"] = [cable_inst] if pid == "gondola_cable" else [cabin_inst]
        if pid == "gondola_cable":
            r["cast_shadow_note"] = "CastShadow OFF on gondola_cable__Licorice (haul ropes); tower meshes keep shadows"
            r["line"] = dict(
                straight_in_plan=True, plan_length=round(G.PLAN_D, 2), rope_spacing=2 * G.WHEEL_R,
                sag_studs=dict(span1_bottom_to_tower=G.SAG[0], span2_tower_to_top=G.SAG[1]),
                tower=dict(plan_distance_from_bottom_wheel=G.TOWER_D, centre_world=r3(G.tower_centre()),
                           ground_y=190.0, rope_crest_y=G.TOWER_ROPE_Y,
                           why="the straight chord between the station wheels passes ~37 studs inside the Crown cliff "
                               "(terrain 70 -> 190 at plan d 506-510) and Hole 17 sits directly under the line; one "
                               "portal tower on the Crown lip, 25+ studs from H17's footprint, carries the ropes over"),
                bull_wheels=dict(bottom_centre=r3(G.wheel_centre("bottom")), top_centre=r3(G.wheel_centre("top")),
                                 source="exported gondola_station torus (groove r 3.8 at station-local (0, 7.6, -2)) "
                                        "x layout.json station placements"),
                ropes={k: {kk: v[kk] for kk in ("A_bottom_attach", "T_tower_crest", "B_top_attach",
                                                  "span_arc_lengths", "total_arc_length")} for k, v in mo.items()},
                old_ore_cableway="the 3 cableway_trestle instances at (-330, ~150, -260/-200/-140) lie 283-399 studs "
                                 "from the gondola line segment (nearest point = the top wheel; the line only reaches "
                                 "x=-418 at z=129); they belong to the old ore cableway and are not used as supports")
        else:
            r["motion"] = dict(type="travel along cable", speed_studs_s=G.SPEED, path="gondola_cable up_line A->T->B",
                               formula=formula, up_line=up, down_line=dn, hang_grip_to_floor=G.HANG,
                               boarding_point=cabin_inst["pos"],
                               fitcheck="swept along both lines every 1 stud in sc_fitcheck_holes.py")
        entries[pid] = r
    man["pieces"] = [p for p in man["pieces"] if p["id"] not in NEW] + [entries[p] for p in NEW]
    lay["instances"] = [i for i in lay["instances"] if i["piece"] not in NEW]
    lay["instances"] += [dict(piece="gondola_cable", **cable_inst), dict(piece="gondola_cabin", **cabin_inst)]
    lay["counts"]["gondola_cable"] = 1
    lay["counts"]["gondola_cabin"] = 1
    lay["pass5"] = dict(gondola=dict(cable=cable_inst, cabin=cabin_inst, travel_path=dict(
        up_line=[up["A_bottom_attach"], up["T_tower_crest"], up["B_top_attach"]],
        down_line=[dn["B_top_attach"], dn["T_tower_crest"], dn["A_bottom_attach"]], sags=list(G.SAG),
        speed_studs_s=G.SPEED, ride_seconds=up["ride_seconds"], formula="see manifest gondola_cabin.motion")))
    P = {p["id"]: p for p in man["pieces"]}
    placed = sum(P[i["piece"]]["tris"] for i in lay["instances"])
    man["totals"].update(pieces=len(man["pieces"]), files=sum(len(p["files"]) for p in man["pieces"]),
                         placed_instances=len(lay["instances"]), placed_triangles=placed,
                         library_triangles=sum(p["tris"] for p in man["pieces"]),
                         max_mesh_triangles=max(p["max_mesh_tris"] for p in man["pieces"]))
    man["pass5"] = dict(generated=time.strftime("%Y-%m-%d %H:%M"), added=list(NEW),
                        summary="_src/pass5_summary.md", reimport="_src/reimport_pass5.txt",
                        fitcheck="fitcheck_pass5.txt")
    (MODELS / "manifest.json").write_text(json.dumps(man, indent=1))
    (MODELS / "layout.json").write_text(json.dumps(lay, indent=1))
    rows = ["| id | group | tris | MeshParts | materials | instances |", "|---|---|---|---|---|---|"]
    for p in man["pieces"]:
        rows.append(f"| {p['id']} | {p['group']} | {p['tris']} | {p['meshparts']} | {', '.join(p['materials'])} | "
                    f"{len(p['instances'])} |")
    (SRC / "pieces_table.md").write_text("\n".join(rows) + "\n")
    print(json.dumps(man["totals"]), json.dumps({k: (v["ride_seconds"], v["linear_w_max_error_studs"]) for k, v in mo.items()}))


if __name__ == "__main__":
    main()
