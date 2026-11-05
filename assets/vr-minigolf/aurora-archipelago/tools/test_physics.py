#!/usr/bin/env python3
"""Sanity tests for tools/sim.py physics on synthetic holes.  python3 tools/test_physics.py"""
import json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim as S


def hole(felt, walls=(), moving=(), cup=(0, 0, -500)):
    return dict(id="t", felt=list(felt), walls=list(walls), moving_parts=list(moving), teleports=[], hazards=[],
                cup={"position": list(cup), "radius": 0.5}, tee={"position": [0, 0, 0]}, ai_waypoints={}, par=2)


def flat(fid, x0, x1, z0, z1, y=0.0, slope=None):
    p = dict(id=fid, zone=fid, center=[(x0 + x1) / 2, y, (z0 + z1) / 2], size=[abs(x1 - x0), abs(z1 - z0)], yaw=0.0,
             slope=slope)
    return p


def shoot(h, v, aim_deg=-90.0, start=(0, 0, 0), t0=0.0):
    ha = S.HoleArrays(h)
    path, r = S.trace_shot(ha, math.radians(aim_deg), v, t0, start=start)
    return path, r


ok = True


def check(name, cond, info):
    global ok
    print(("PASS " if cond else "FAIL ") + name + ": " + info)
    ok &= bool(cond)


# 1. max putt on flat felt
h = hole([flat("f", -5, 5, 5, -300)])
path, r = shoot(h, S.V_MAX)
check("max putt distance", 57 <= -r[1] <= 63, f"{-r[1]:.1f} studs ({-r[1] * S.STUD_M:.1f} m) at V_MAX={S.V_MAX}, analytic {S.flat_dist(S.V_MAX, S.ROLL_DECEL_CONST, S.ROLL_DECEL_PER_SPEED):.1f}")

# 2. wall restitution head-on
wall = dict(id="w", center=[0, 0.5, -10.25], size=[10, 2, 0.5], yaw=0.0)
h = hole([flat("f", -5, 5, 5, -10)], [wall])
ha = S.HoleArrays(h)
PH = S.ph_array()
path, r = shoot(h, 8.0)
# speed just before/after impact from path samples
zs = path[:, 2]
imp = int(np.argmin(zs))
vin = (zs[imp - 2] - zs[imp - 1]) / (6 * PH[12])
vout = abs(zs[imp + 2] - zs[imp + 1]) / (6 * PH[12])
check("wall restitution", abs(vout / vin - S.WALL_RESTITUTION) < 0.05, f"in {vin:.2f} out {vout:.2f} ratio {vout / vin:.3f}")

# 3. ramp: rise 1 over 8 needs ~sqrt(v_flat^2 + 2 g h)
ramp = flat("r", -5, 5, -10, -18, y=0.5, slope={"axis": "z", "rise": -1.0})  # higher at -z
top = flat("t", -5, 5, -18, -60, y=1.0)
h = hole([flat("f", -5, 5, 5, -10), ramp, top])
_, r_lo = shoot(h, 7.5)
_, r_hi = shoot(h, 15.0)
# energy: v^2 must cover 2*g*1.0 = 65 plus rolling losses on 10 flat + 8 ramp studs; 7.5 is clearly short
check("ramp climb", r_lo[2] < 0.5 and r_hi[2] > 0.99, f"v7.5 ends y={r_lo[2]:.2f} z={r_lo[1]:.1f}; v15 ends y={r_hi[2]:.2f} z={r_hi[1]:.1f}")

# 4. drop keeps ~80% speed and lands on lower level
h = hole([flat("u", -5, 5, 5, -10, y=0.0), flat("l", -5, 5, -10, -80, y=-1.5)])
_, r = shoot(h, 10.0)
check("drop", abs(r[2] + 1.5) < 1e-6 and r[3] == 0, f"ends y={r[2]:.2f} z={r[1]:.1f}")

# 5. cliff face from the lower level reflects
h = hole([flat("l", -5, 5, 5, -20, y=-1.5), flat("u", -5, 5, -20, -40, y=0.0)])
_, r = shoot(h, 8.0, start=(0, -1.5, 0))
check("cliff blocks", r[1] > -20 and abs(r[2] + 1.5) < 1e-6, f"ends z={r[1]:.2f} y={r[2]:.2f}")

# 6. cup capture slow vs fast
h = hole([flat("f", -5, 5, 5, -40)], cup=(0, 0, -10))
_, r1 = shoot(h, S.speed_for(10.8, S.ROLL_DECEL_CONST, S.ROLL_DECEL_PER_SPEED, S.V_MAX))
_, r2 = shoot(h, 18.0)
check("cup capture", r1[3] == 1 and r2[3] != 1, f"gentle putt outcome {r1[3]}, blast outcome {r2[3]}")

# 7. side slope curls the ball downhill
h = hole([flat("s", -5, 5, 5, -40, y=0.0, slope={"axis": "x", "rise": 0.6})])  # higher at +x
_, r = shoot(h, 9.0)
check("side slope break", r[0] < -0.5, f"ball drifted to x={r[0]:.2f} (downhill = -x)")

# 8. rotating arm deflects
arm = dict(id="m", type="rotate", pivot=[0, 0, -10], axis=[0, 1, 0], speed=0.0, range=None, phase=0.0,
           blockers=[dict(center=[0, 0.5, 0], size=[8, 1, 0.6], yaw=0.0)])
h = hole([flat("f", -5, 5, 5, -40)], moving=[arm])
_, r = shoot(h, 9.0)
check("static arm blocks", r[1] > -10, f"ball stopped at z={r[1]:.2f}")
# 9. hazard respawn point: ball rolling off the felt over water reappears at the respawn point (outcome 5)
h = hole([flat("f", -1, 1, 5, -10)])
h["hazards"] = [dict(id="w", type="water", center=[0, -1, -20], size=[20, 20], yaw=0.0, reset="respawn", respawn=[0.0, 0.0, -2.0])]
_, r = shoot(h, 10.0)
check("hazard respawn", r[3] == 5 and abs(r[1] + 2.0) < 1e-6 and abs(r[0]) < 1e-6, f"outcome {r[3]}, placed at ({r[0]:.2f},{r[1]:.2f})")

# 10. pendulum: bob hanging at rest (amplitude 0) blocks the lane; swung out (phase 90 deg, period long) it lifts clear
def pend(phase, amp=30.0):
    return dict(id="p", type="swing", pivot=[0, 7.96, -10], axis=[0, 0, 1], amplitude_deg=amp, period_s=1000.0, phase=phase,
                blockers=[dict(center=[0, -7.0, 0], size=[1.6, 1.8, 1.0], yaw=0.0)])
h = hole([flat("f", -5, 5, 5, -40)], moving=[pend(0.0, amp=0.0001)])
_, r_rest = shoot(h, 9.0)
h = hole([flat("f", -5, 5, 5, -40)], moving=[pend(90.0)])
_, r_out = shoot(h, 9.0)
check("pendulum", r_rest[1] > -10 and r_out[1] < -12, f"bob at rest: ball stops z={r_rest[1]:.2f}; bob swung out 30 deg: z={r_out[1]:.2f}")

# 11. V-shaped dip: a ball dropped near the crease settles (no 30 s timeout)
h = hole([flat("a", -5, 5, 5, -3, y=0.2, slope={"axis": "z", "rise": 0.4}), flat("b", -5, 5, -3, -11, y=0.2, slope={"axis": "z", "rise": -0.4})])
_, r = shoot(h, 2.0, start=(0, 0.0, -3.0))
check("dip settles", r[3] == 0 and r[4] < 29.0, f"outcome {r[3]} after {r[4]:.1f} s at z={r[1]:.2f}")
# 12. slider dwell: positions over one cycle follow lo -> (pause) -> hi (pause) -> lo; period includes the pauses
m = dict(id="d", type="slide", pivot=[0, 0, 0], axis=[1, 0, 0], speed=2.0, range=[0.0, 4.0], phase=0.0,
         dwell=[dict(at=0.0, s=1.0), dict(at=2.0, s=0.5), dict(at=4.0, s=1.5)], blockers=[dict(center=[0, 0.5, 0], size=[1, 1, 1], yaw=0.0)])
ha = S.HoleArrays(hole([flat("f", -5, 5, 5, -40)], moving=[m]))
T = S.cycle_period(m)
pts = {t: S.part_state(ha.MP, 0, t)[0] for t in (0.5, 1.5, 2.25, 3.0, 4.0, 5.5, 6.25, 7.0, 7.9, T + 0.5)}
exp = {0.5: 0.0, 1.5: 1.0, 2.25: 2.0, 3.0: 3.0, 4.0: 4.0, 5.5: 3.0, 6.25: 2.0, 7.0: 1.0, 7.9: 0.0, T + 0.5: 0.0}
check("slider dwell", abs(T - 7.5) < 1e-9 and all(abs(pts[t] - exp[t]) < 1e-6 for t in exp), f"period {T} s, offsets {[round(v, 2) for v in pts.values()]}")
# 13. pendulum height rule (Round 8): a bob hanging at rest whose bottom is 0.10 above the felt (above the ball centre 0.08,
#     below its top 0.16) only meets the top of the ball: the ball rolls under. At 0.06 (test 10) it is stopped.
def pend_at(pivot_y):
    return dict(id="p", type="swing", pivot=[0, pivot_y, -10], axis=[0, 0, 1], amplitude_deg=0.0001, period_s=1000.0, phase=0.0,
                blockers=[dict(center=[0, -7.0, 0], size=[1.6, 1.8, 1.0], yaw=0.0)])
_, r_hi = shoot(hole([flat("f", -5, 5, 5, -40)], moving=[pend_at(8.0)]), 9.0)
_, r_lo = shoot(hole([flat("f", -5, 5, 5, -40)], moving=[pend_at(7.96)]), 9.0)
check("pendulum height rule", r_hi[1] < -12 and r_lo[1] > -10, f"bob bottom 0.10: ball z={r_hi[1]:.2f} (rolled under); bottom 0.06: z={r_lo[1]:.2f}")
# 14. rectangular teleport trigger: a ball rolling into the 3 x 3 rectangle anywhere (here 1.2 off its centre line, outside a 0.5
#     circle) is moved to the upper exit with clamp(v * 0.5, 1.5, 3.0) along the exit dir.
hl = hole([flat("low", -5, 5, 5, -12), flat("up", -5, 5, -14, -40, y=4.0)])
hl["teleports"] = [dict(id="tp", entry={"center": [0, 0, -10], "radius": 0.5, "half_size": [1.5, 1.5]}, exit={"center": [0, 4.0, -16], "dir": [0, -1]},
                        speed_factor=0.5, min_speed=1.5, max_speed=3.0)]
_, r_tp = shoot(hl, 6.0, start=(1.2, 0, 0))
check("rect teleport trigger", abs(r_tp[2] - 4.0) < 1e-6 and r_tp[1] < -16.5, f"ended y={r_tp[2]:.2f} z={r_tp[1]:.2f} (lifted onto the upper deck)")
# 15. pinned rule: a ball on a 1-in-2 slope rolling into a solid higher piece (a cliff) comes to rest instead of timing out
hp = hole([flat("slope", -5, 5, 5, -10, slope={"axis": "x", "rise": -5.0}), flat("cliff", 5, 8, 5, -10, y=3.0)])
_, r_pin = shoot(hp, 4.0, aim_deg=20.0, start=(3.0, -1.0, -3.0))
check("pinned ball rests", r_pin[3] == 0 and r_pin[4] < 29.0, f"outcome {r_pin[3]} after {r_pin[4]:.1f} s")
# 16. Aurora: ice felt (decel_scale 0.35) rolls a putt much further; the analytic flat distance with a, k scaled by 0.35 matches
hi_ = hole([dict(flat("ice", -5, 5, 5, -400), surface="ice", decel_scale=0.35)])
_, r_ice = shoot(hi_, 5.0)
_, r_felt = shoot(hole([flat("f", -5, 5, 5, -400)]), 5.0)
d_an = S.flat_dist(5.0, 0.5 * 0.35, 0.25 * 0.35)
check("ice felt roll", abs(-r_ice[1] - d_an) < 0.6 and -r_ice[1] > 2.5 * -r_felt[1], f"v=5: ice {-r_ice[1]:.1f} studs (analytic {d_an:.1f}), felt {-r_felt[1]:.1f}")
# 17. Aurora: the planner's surface-aware speed rolls the requested distance over felt -> ice -> felt
hm = hole([flat("a", -5, 5, 5, -10), dict(flat("ice", -5, 5, -10, -30), surface="ice", decel_scale=0.35), flat("b", -5, 5, -30, -80)])
ham = S.HoleArrays(hm)
v_pl = S.speed_for_line(ham.P, 0.0, 0.0, 0.0, 0.0, -40.0, 40.0, S.ROLL_DECEL_CONST, S.ROLL_DECEL_PER_SPEED, S.V_MAX)
_, r_pl = shoot(hm, v_pl)
check("surface-aware planner", abs(-r_pl[1] - 40.0) < 0.8, f"v={v_pl:.2f} rolls to z={r_pl[1]:.2f} (target -40; felt-only speed would be {S.speed_for(40, 0.5, 0.25, S.V_MAX):.2f})")
# 18. Aurora: timed surface (light bridge). Solid for t in [0, 4) of an 8 s cycle; a ball crossing while solid gets over the pit,
#     a ball arriving while it is gone falls and respawns (outcome 5)
def bridge(phase):
    return hole([flat("a", -2, 2, 5, -10), dict(flat("span", -2, 2, -10, -16), timed=dict(part="t", period_s=8.0, solid=[0.0, 4.0], phase_s=phase)),
                 flat("b", -2, 2, -16, -60)])
hb = bridge(0.0)
hb["hazards"] = [dict(id="gap", type="pit", center=[0, -30, -13], size=[10, 6], yaw=0.0, reset="respawn", respawn=[0.0, 0.0, -8.0])]
_, r_on = shoot(hb, 9.0)
hb2 = bridge(4.0)
hb2["hazards"] = hb["hazards"]
_, r_off = shoot(hb2, 9.0)
check("timed bridge", r_on[3] == 0 and r_on[1] < -16 and r_off[3] == 5 and abs(r_off[1] + 8.0) < 1e-6,
      f"solid: outcome {r_on[3]} z={r_on[1]:.1f}; vanished: outcome {r_off[3]} placed at z={r_off[1]:.1f}")
# 19. Aurora: lift (H5 geyser). Column = vertical slide 0..4 with dwell; boarding window = the bottom dwell. A ball arriving while the
#     column is up bounces off its face (stays on the lower tier); arriving in the window it is held and released on the upper tier
col = dict(id="col", type="slide", pivot=[0, 0, -11.5], axis=[0, 1, 0], speed=2.0, range=[0.0, 4.0], phase=0.0,
           dwell=[dict(at=0.0, s=3.0), dict(at=4.0, s=1.0)], blockers=[dict(center=[0, -2.0, 0], size=[3, 4, 3], yaw=0.0)])
def lift_hole():
    h = hole([flat("low", -5, 5, 5, -13), flat("up", -5, 5, -13, -40, y=4.0)], moving=[col])
    h["teleports"] = [dict(id="geyser", kind="lift", entry={"center": [0, 0, -11.5], "radius": 1.5, "half_size": [1.5, 1.5]},
                           exit={"center": [0, 4.0, -14.5], "dir": [0, -1]}, speed_factor=0.6, min_speed=2.0, max_speed=6.0,
                           lift=dict(cycle_s=S.cycle_period(col), board=[0.0, 3.0], release_s=5.0))]
    return h
_, r_in = shoot(lift_hole(), 6.0, t0=0.0)
_, r_up = shoot(lift_hole(), 6.0, t0=4.0)
check("geyser lift", abs(r_in[2] - 4.0) < 1e-6 and r_in[1] < -14.5 and abs(r_up[2]) < 1e-6 and r_up[1] > -10,
      f"window: ended y={r_in[2]:.1f} z={r_in[1]:.1f}; column up: ended y={r_up[2]:.1f} z={r_up[1]:.1f}")
# An uphill reversal on one continuous incline is not a settled ball.
hs=hole([flat("incline",-5,5,40,-40,slope={"axis":"z","rise":-2.8})])
_,r_turn=shoot(hs,6.0)
check("incline turnaround continues",r_turn[3]!=0,f"outcome {r_turn[3]} at z={r_turn[1]:.2f}")
# Game stop rule (BallController.luau, 2026-10-12): rest after 0.5 s under 0.2 studs/s only where |slope| < 0.015;
# steeper ground: 2 s wedge rule after up to 3 downhill seam hops. tools/rest_timing.py applies it to recorded paths.
GAME_GENTLE = 0.015
_holes = {h["number"]: h for h in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "holes.json")))["holes"]}
def _edge_y(f, side):
    """felt top height along its x edge side (-1 west, +1 east) for x-sloped or level pieces"""
    sl = f.get("slope") or {}
    r = sl.get("rise", 0.0) if sl.get("axis") == "x" else 0.0
    return f["center"][1] + side * r / 2
_h6 = {f["id"]: f for f in _holes[6]["felt"]}
_seams = [("shelf", "cup_pad"), ("cup_pad", "shelf_e")]
_lips = [abs(_edge_y(_h6[a], 1) - _edge_y(_h6[b], -1)) for a, b in _seams]
check("H6 cup stripe has no lip", max(_lips) < 1e-3, f"seam steps {[round(v, 4) for v in _lips]}")
_sl6 = [abs((f.get("slope") or {}).get("rise", 0.0)) / f["size"][0] for f in _holes[6]["felt"] if f["zone"] == "shelf"]
_cp = _h6["cup_pad"]; _cx, _cz = _holes[6]["cup"]["position"][0], _holes[6]["cup"]["position"][2]
check("H6 shelf gentle + level within 1.5 of cup", max(_sl6) < GAME_GENTLE and _cp.get("slope") is None and
      _cp["center"][0] - _cp["size"][0] / 2 <= _cx - 1.5 + 1e-6 and _cp["center"][0] + _cp["size"][0] / 2 >= _cx + 1.5 - 1e-6,
      f"max shelf slope {max(_sl6):.4f}; cup_pad x {_cp['center'][0] - _cp['size'][0] / 2:g}..{_cp['center'][0] + _cp['size'][0] / 2:g}")
_pool = _holes[6]["hazards"][0]
check("H6 pool covers the north escape point", _pool["center"][2] - _pool["size"][1] / 2 <= -47.97 and
      _pool["center"][0] - _pool["size"][0] / 2 <= 10.27, f"pool z {_pool['center'][2] + _pool['size'][1] / 2:g}..{_pool['center'][2] - _pool['size'][1] / 2:g}")
print("ALL PASS" if ok else "SOME FAILED")
sys.exit(0 if ok else 1)
