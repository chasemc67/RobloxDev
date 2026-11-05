#!/usr/bin/env python3
"""Sanity tests for tools/sim.py physics on synthetic holes.  python3 tools/test_physics.py"""
import math, os, sys
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
# 14. Sugarloaf Canyon: rectangular teleport trigger (H11 lift chamber). A ball rolling into the 3 x 3 rectangle anywhere (here 1.2 off
#     its centre line, outside a 0.5 circle) is moved to the upper exit with clamp(v * 0.5, 1.5, 3.0) along the exit dir.
hl = hole([flat("low", -5, 5, 5, -12), flat("up", -5, 5, -14, -40, y=4.0)])
hl["teleports"] = [dict(id="lift", entry={"center": [0, 0, -10], "radius": 0.5, "half_size": [1.5, 1.5]}, exit={"center": [0, 4.0, -16], "dir": [0, -1]},
                        speed_factor=0.5, min_speed=1.5, max_speed=3.0)]
_, r_tp = shoot(hl, 6.0, start=(1.2, 0, 0))
check("rect teleport trigger", abs(r_tp[2] - 4.0) < 1e-6 and r_tp[1] < -16.5, f"ended y={r_tp[2]:.2f} z={r_tp[1]:.2f} (lifted onto the upper deck)")
# 15. Sugarloaf Canyon pinned rule: a ball on a 1-in-2 slope rolling into a solid higher piece (a cliff) comes to rest instead of timing out
hp = hole([flat("slope", -5, 5, 5, -10, slope={"axis": "x", "rise": -5.0}), flat("cliff", 5, 8, 5, -10, y=3.0)])
_, r_pin = shoot(hp, 4.0, aim_deg=20.0, start=(3.0, -1.0, -3.0))
check("pinned ball rests", r_pin[3] == 0 and r_pin[4] < 29.0, f"outcome {r_pin[3]} after {r_pin[4]:.1f} s")
# 16-18. H11 interlock and actual moving deck ownership/schedule.
import json, os
h11 = next(h for h in json.load(open(os.path.join(os.path.dirname(__file__), "..", "holes.json")))["holes"] if h["number"] == 11)
ha11 = S.HoleArrays(h11)
ids = [m["id"] for m in h11["moving_parts"]]
jd, jl = ids.index("lock_lift_deck"), ids.index("quay_lip")
check("lift carries felt", not any(p["id"] == "lock" for p in h11["felt"]) and any(ha11.P[:,13] == jd+1), "no static lock floor; deck owns its felt")
schedule=h11["moving_parts"][jd]["schedule"]
flush=h11["moving_parts"][jl]["schedule"]["flush"]
rise, top, descend = schedule["rise"], schedule["release"], schedule["return_"]
period=S.cycle_period(h11["moving_parts"][0])
height=schedule["height"]
heights=[S.part_state(ha11.MP,jd,t)[0] for t in (0,rise[0],sum(rise)/2,rise[1],descend[0],sum(descend)/2,descend[1])]
check("lift real cycle", np.allclose(heights,[0,0,height/2,height,height,height/2,0]), str(heights))
lip=[S.part_state(ha11.MP,jl,t)[0] for t in (0,sum(rise)/2,flush[0]-.001,flush[0],flush[1]-.001,flush[1],descend[1])]
check("lip interlock", lip==[0,0,0,-1,-1,0,0], f"flush {flush}; top dwell {top}")
gate=h11["moving_parts"][ids.index("lock_gate")]
gate_travel=(max(gate["range"])-min(gate["range"]))/gate["speed"]
gate_closed_start=gate["dwell"][0]["s"]+gate_travel
gate_closed_end=gate_closed_start+gate["dwell"][1]["s"]
margins=(rise[0]-gate_closed_start,gate_closed_end-descend[1])
check("lift level dwell and margins", top[1]-top[0]>=2.-1e-9 and np.allclose(top,[rise[1],descend[0]]) and np.allclose(flush,[rise[1]-.1,descend[0]+.1]) and min(margins)>=.3-1e-9 and all(S.lift_tilt(t,period)==0 for t in np.linspace(0,period,120)) and all(abs(S.part_state(ha11.MP,ids.index("lock_gate"),t)[0])<1e-8 for t in np.linspace(rise[0]-.3,descend[1]+.3,120)), f"top dwell {top[1]-top[0]:g}s; gate margins {margins}; cycle {period:g}s")
# An uphill reversal on one continuous incline is not a settled ball.
hs=hole([flat("incline",-5,5,40,-40,slope={"axis":"z","rise":-2.8})])
_,r_turn=shoot(hs,6.0)
check("incline turnaround continues",r_turn[3]!=0,f"outcome {r_turn[3]} at z={r_turn[1]:.2f}")
# H8 regression: tiny V-bottom oscillations can revisit the same support piece
# at every stationarity checkpoint even though they cross the seam in between.
h8 = next(h for h in json.load(open(os.path.join(os.path.dirname(__file__), "..", "holes.json")))["holes"] if h["number"] == 8)
_, r_h8 = shoot(h8, 11.463299520450917, aim_deg=147.22715114685977,
                start=(-0.4433840829950553, 0.18150739325463744, -34.407536966273184), t0=211.99572333011537)
# Hollow bottom near z=-32: a sharp V seam (old) or a flat crease floor (Oct 12 2026, h8_flat). Rest must be in it.
# 2026-10-12: hollows are now 4.5-stud level floors (no V); the ball may roll on to the next floor. Rest must be on a floor.
_cr = [f for f in h8["felt"] if f["id"].startswith("crease")]
_on = any(f["center"][2] - f["size"][1] / 2 - .05 < r_h8[1] < f["center"][2] + f["size"][1] / 2 + .05 for f in _cr) if _cr else abs(r_h8[1] + 32) < .05
check("H8 repeated seam crossing settles", r_h8[3] == 0 and r_h8[4] < 29 and _on,
      f"outcome {r_h8[3]} after {r_h8[4]:.1f}s at z={r_h8[1]:.6f}")
# Game stop rule (BallController.luau, 2026-10-12): rest after 0.5 s under 0.2 studs/s only where |slope| < 0.015;
# steeper ground uses the 2 s wedge rule after up to 3 downhill seam hops. The H8 rest above must be on gentle ground,
# and every H8 felt piece must be either level-ish (< 0.015) or clearly a ramp, so no piece sits in between.
GAME_GENTLE = 0.015
_ha8 = S.HoleArrays(h8)
_ci = S.support(_ha8.P, r_h8[0], r_h8[1], 5.0, 0.15, 0.08)[0]
_g = float(np.hypot(*S.piece_grad(_ha8.P, _ci))) if _ci >= 0 else 0.0
check("H8 rest on gentle ground (game rule)", _g < GAME_GENTLE, f"slope at rest {_g:.4f}")
_mid = [float(np.hypot(*S.piece_grad(_ha8.P, i))) for i in range(len(_ha8.P)) if S.piece_grad(_ha8.P, i) != (0.0, 0.0)]
check("H8 no near-threshold slopes", all(g > 4 * GAME_GENTLE for g in _mid), f"ramp slopes {sorted(set(round(g, 3) for g in _mid))}")
print("ALL PASS" if ok else "SOME FAILED")
sys.exit(0 if ok else 1)
