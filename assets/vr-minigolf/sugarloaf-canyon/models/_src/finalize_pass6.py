"""Pass 6: rebuild models/manifest.json + models/layout.json from the PRE-pass-6 snapshot (_src/backup_pass6/) plus the
pass-6 build records (_cache/pass6_build.json), the dressing layout (_cache/pass6_layout.json, sc_dress_pass6.py) and
the cliff-variant swap (_cache/pass6_cliffs.json). Idempotent: always starts from the snapshot.
Also regenerates _src/pieces_table.md and collates _src/reimport_pass6.txt.      python _src/finalize_pass6.py
"""
import json, math, time
from pathlib import Path
import gondola_geom as G

SRC = Path(__file__).resolve().parent
MODELS = SRC.parent
CACHE = SRC / "_cache"


def r3(p):
    return [round(float(v), 3) for v in p]


def motion():
    out = {}
    for name, rope in G.ropes().items():
        A, Tw, B = rope
        L1, L2 = G.span_lengths(rope)
        err = 0.0
        for k in range(0, 101):
            for (P, Q, sg, Ls, s0) in ((A, Tw, G.SAG[0], L1, 0.0), (Tw, B, G.SAG[1], L2, L1)):
                s = Ls * k / 100
                f = G.f_at_time(rope, (s0 + s) / G.SPEED)
                err = max(err, math.dist(G.rope_point(rope, f), G.span_point(P, Q, s / Ls, sg)))
        table = [[t, r3(G.rope_point(rope, G.f_at_time(rope, t)))] for t in range(0, int((L1 + L2) / G.SPEED) + 1, 10)]
        table.append([round((L1 + L2) / G.SPEED, 2), r3(B)])
        out[name] = dict(A_bottom_attach=r3(A), T_tower_crest=r3(Tw), B_top_attach=r3(B),
                         span_arc_lengths=[round(L1, 2), round(L2, 2)], total_arc_length=round(L1 + L2, 2),
                         ride_seconds=round((L1 + L2) / G.SPEED, 2), linear_w_max_error_studs=round(err, 3),
                         samples_every_10s=table)
    return out


def slope_deg(P, Q, sag, w):
    """Path slope (deg) of span P->Q at chord fraction w."""
    dy = (Q[1] - P[1]) - 4 * sag * (1 - 2 * w)
    dh = math.hypot(Q[0] - P[0], Q[2] - P[2])
    return math.degrees(math.atan2(dy, dh))


def gondola(man, lay, recs):
    mo = motion()
    up, dn = mo["up_line"], mo["down_line"]
    A, Tw, B = G.ropes()["up_line"]
    s1_end, s2_start = slope_deg(A, Tw, G.SAG[0], 1.0), slope_deg(Tw, B, G.SAG[1], 0.0)
    cable_inst = dict(pos=r3(G.ORIGIN), yaw=0.0, src="lifts:Sunset Gondola",
                      note="world-placed static: pivot = bottom bull-wheel centre (line start); geometry already at world "
                           "offsets, so yaw stays 0. Pass 6: bottom wheel raised 7.2 with the station (y 25.6 -> 32.8)")
    cabin_inst = dict(pos=r3(up["A_bottom_attach"]), yaw=G.CABIN_YAW_UP, src="lifts:Sunset Gondola",
                      note="moving cabin parked at the bottom-station boarding position (grip on the up-line rope where "
                           "it leaves the bull wheel; floor 0.4 above the RAISED deck, deck top world y 26.0). Travels "
                           "the up line to the top at 6 studs/s, see manifest gondola_cabin.motion")
    formula = (
        f"Pivot (grip) path along a rope = two parabolic spans A->T (sag {G.SAG[0]}) and T->B (sag {G.SAG[1]}) in WORLD "
        "coords: P_span(w) = P + (Q - P)*w - (0, 4*sag*w*(1-w), 0), w in [0,1]. Pass 6: A (bottom attach) is 7.2 "
        f"higher than pass 5 (world y {up['A_bottom_attach'][1]}); T and B unchanged. Travel: s(t) = 6*t studs of "
        "rope arc length; on span 1 (0 <= s <= L1) w solves arclen_AT(w) = s, on span 2 w solves arclen_TB(w) = s - L1. "
        "Numerically w ~= s/L1 (span 1) and (s-L1)/L2 (span 2) is within linear_w_max_error_studs of the exact "
        "arc-length position. Cabin stays level (hanger pivots), yaw constant: up line yaw "
        f"{G.CABIN_YAW_UP} (front local -Z toward the top station), down line yaw {G.CABIN_YAW_UP + 180:.2f} from B to "
        "A. Roblox: cabin:PivotTo(CFrame.new(P(t)) * CFrame.Angles(0, math.rad(yaw), 0)) each Heartbeat. At the tower "
        f"crest T the path breaks from {s1_end:.1f} deg up to {s2_start:.1f} deg.")
    old = {p["id"]: p for p in man["pieces"]}
    # gondola_cable: new record; gondola_station_bottom: new piece; gondola_cabin: FBX unchanged, motion recomputed
    cable = dict(recs["gondola_cable"])
    prev = old["gondola_cable"]
    cable["instances"] = [cable_inst]
    cable["cast_shadow_note"] = "CastShadow OFF on gondola_cable__Licorice (haul ropes); tower meshes keep shadows"
    line = dict(prev["line"])
    line["bull_wheels"] = dict(bottom_centre=r3(G.wheel_centre("bottom")), top_centre=r3(G.wheel_centre("top")),
                               source="exported station tori: gondola_station_bottom groove r 3.8 at station-local "
                                      "(0, 14.8, -2) (raised 7.2), gondola_station (top) at (0, 7.6, -2)")
    line["ropes"] = {k: {kk: v[kk] for kk in ("A_bottom_attach", "T_tower_crest", "B_top_attach", "span_arc_lengths",
                                              "total_arc_length")} for k, v in mo.items()}
    line["pass6_raise"] = dict(bottom_attach_raise=G.BOTTOM_RAISE, why=(
        "RobloxDevBot clearance request: the cabin swept path over the Junction walkway p_h18_hub seg 3 (walk y 18) was "
        "2.92 above the walk in pass 5; the bottom station is now the raised gondola_station_bottom (deck +7.2), so "
        "the bottom attach / wheel moved 25.6 -> 32.8 and the cabin clears the walk by >= 8 (see fitcheck_pass6.txt)"),
        tower_position_unchanged=True, sags_unchanged=list(G.SAG))
    line["tower"] = dict(line["tower"], recolour="pass 6: sun-weathered timber (TimberWeathered + Timber baulks), dark "
                                                 "Iron fittings, Brass bolt plates; sheaves PepRed/MintWhite")
    cable["line"] = line
    cable["world_json_size"] = None
    st = dict(recs["gondola_station_bottom"])
    st["instances"] = [dict(pos=[132.0, 18.0, 544.0], yaw=53.53, src="gondola_bottom_station",
                            note="pass 6 raised bottom station (replaces the gondola_station instance here); same "
                                 "footprint centre/yaw; ground boarding point (130, 18, 540) under the open end, side "
                                 "stair up to the deck")]
    st["world_json_size"] = [16, 14, 12]
    st["boarding"] = dict(world_boarding_point=[130.0, 18.0, 540.0], station_local=[2.0, 0.0, -4.0],
                          deck_top_world_y=26.0, stair="10 risers x 0.8, treads 1.5, 5.8 wide, local +X side, foot at "
                          "the open (-Z) end, top at the back of the deck (cabin loop only uses the front 7 studs)",
                          headroom_under_joists=4.9)
    cabin = dict(old["gondola_cabin"])
    cabin["instances"] = [cabin_inst]
    cabin["motion"] = dict(cabin["motion"], formula=formula, up_line=up, down_line=dn, boarding_point=cabin_inst["pos"],
                           pass6="bottom attach raised 7.2 (tower and top unchanged); FBX unchanged (hanger unchanged)")
    top_station = dict(old["gondola_station"])
    top_station["instances"] = [i for i in top_station["instances"] if i.get("src") != "gondola_bottom_station"]
    top_station["notes"] = top_station["notes"] + " Pass 6: used for the TOP station only; the bottom is gondola_station_bottom."
    for p in (cable, st, cabin, top_station):
        old[p["id"]] = p
    lay["instances"] = [i for i in lay["instances"] if not (i["piece"] == "gondola_station" and i.get("src") ==
                                                              "gondola_bottom_station")
                        and i["piece"] not in ("gondola_cable", "gondola_cabin")]
    lay["instances"] += [dict(piece="gondola_station_bottom", **st["instances"][0]),
                         dict(piece="gondola_cable", **cable_inst), dict(piece="gondola_cabin", **cabin_inst)]
    lay.setdefault("pass6", {})["gondola"] = dict(
        cable=cable_inst, cabin=cabin_inst, bottom_station="gondola_station_bottom", raise_studs=G.BOTTOM_RAISE,
        travel_path=dict(up_line=[up["A_bottom_attach"], up["T_tower_crest"], up["B_top_attach"]],
                         down_line=[dn["B_top_attach"], dn["T_tower_crest"], dn["A_bottom_attach"]], sags=list(G.SAG),
                         speed_studs_s=G.SPEED, ride_seconds=up["ride_seconds"],
                         formula="see manifest gondola_cabin.motion"))
    man["pieces"] = [old[p["id"]] for p in man["pieces"]] + [st]
    return mo


def totals(man, lay):
    P = {p["id"]: p for p in man["pieces"]}
    placed = sum(P[i["piece"]]["tris"] for i in lay["instances"])
    lay["counts"] = {}
    for i in lay["instances"]:
        lay["counts"][i["piece"]] = lay["counts"].get(i["piece"], 0) + 1
    for p in man["pieces"]:
        p["instances"] = [{k: v for k, v in i.items() if k != "piece"} for i in lay["instances"] if i["piece"] == p["id"]]
    man["totals"].update(pieces=len(man["pieces"]), files=sum(len(p["files"]) for p in man["pieces"]),
                         placed_instances=len(lay["instances"]), placed_triangles=placed,
                         library_triangles=sum(p["tris"] for p in man["pieces"]),
                         max_mesh_triangles=max(p["max_mesh_tris"] for p in man["pieces"]))
    return placed


def pieces_table(man):
    rows = ["| id | group | tris | max mesh | MeshParts | materials | instances |", "|---|---|---|---|---|---|---|"]
    for p in man["pieces"]:
        rows.append(f"| {p['id']} | {p['group']} | {p['tris']} | {p['max_mesh_tris']} | {p['meshparts']} | "
                    f"{', '.join(p['materials'])} | {len(p['instances'])} |")
    (SRC / "pieces_table.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main():
    recs = json.loads((CACHE / "pass6_build.json").read_text())
    man = json.loads((SRC / "backup_pass6" / "manifest.json").read_text())
    lay = json.loads((SRC / "backup_pass6" / "layout.json").read_text())
    before = totals(man, lay)
    gondola(man, lay, recs)
    import finalize_pass6_ext as X          # props, dressing, cliffs (filled in as those steps land)
    info = X.apply(man, lay, recs)
    after = totals(man, lay)
    man["pass6"] = dict(generated=time.strftime("%Y-%m-%d %H:%M"), placed_triangles_before=before,
                        placed_triangles_after=after, summary="_src/pass6_summary.md", reimport="_src/reimport_pass6.txt",
                        fitcheck="fitcheck_pass6.txt", **info)
    (MODELS / "manifest.json").write_text(json.dumps(man, indent=1))
    (MODELS / "layout.json").write_text(json.dumps(lay, indent=1))
    pieces_table(man)
    print(json.dumps(man["totals"]), "placed before", before, "after", after)


if __name__ == "__main__":
    main()
