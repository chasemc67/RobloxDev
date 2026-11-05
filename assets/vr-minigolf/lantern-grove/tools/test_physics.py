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
print("ALL PASS" if ok else "SOME FAILED")
sys.exit(0 if ok else 1)
