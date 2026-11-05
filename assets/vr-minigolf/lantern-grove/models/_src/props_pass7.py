"""Pass 7: Firefly Hollow (H8) dressing props. Cheap, decoration only (no collision), placed by dressing_world.py
(role 'hollow') around the H8 alcove, the junction and the climb.

  firefly_cluster_low   ~16 Neon firefly specks hovering 0.3..1.8 above the ground (low: may sit beside rails)
  firefly_swarm         ~26 specks in a loose rising column up to ~4.2 (tall: kept 3 studs back from rails)
  glow_shroom_patch     3 small bioluminescent mushrooms (ShroomGlow caps, Firefly spots) on a moss pad
  glow_root_arch        a gnarled surface root arching out of the ground and back in, moss + 3 glow shrooms
"""
import math, random
from registry import prop
from lglib import TAU
from lglib import M


def small_shroom(pb, h, r, loc=(0, 0, 0), tilt=(0, 0), spot=False):
    """Low-poly glow mushroom (~60 tris): Cream stem + ShroomGlow Neon cap (+ optional Firefly spot on top)."""
    m = M(loc, (tilt[0], tilt[1], 0))
    sr = max(0.05, r * 0.3)
    pb.cyl("Cream", sr * 1.15, sr * 0.85, h, 6, loc=(0, 0, h / 2), matrix=m, caps=False, smooth=False)
    pb.lathe("ShroomGlow", [(r * 0.35, h - 0.02), (r, h - 0.02 + r * 0.08), (r * 0.7, h + r * 0.5),
                            (0, h + r * 0.66)], 8, matrix=m)
    if spot:
        pb.sphere("Firefly", r * 0.18, loc=(0, 0, h + r * 0.66), matrix=m, segs=4, rings=2, smooth=False)


def _specks(pb, rnd, n, rmax, z0, z1, big=2):
    for k in range(n):
        a = rnd.uniform(0, TAU)
        rr = rmax * math.sqrt(rnd.uniform(0.02, 1.0))
        z = rnd.uniform(z0, z1)
        r = 0.22 if k < big else rnd.uniform(0.1, 0.16)          # iteration 2: bigger specks (read from the tee)
        pb.sphere("Firefly", r, loc=(math.cos(a) * rr, math.sin(a) * rr, z), segs=4, rings=2, smooth=False)


@prop("firefly_cluster_low", ["H8"], "P2", target=[2.8, 1.8, 2.8], group="nature",
      notes="Pass 7 Firefly Hollow: 16 hovering firefly specks (Neon #D8FF6A, 8 tris each), 0.3..1.8 above the "
            "ground. No ground contact: anchor the Model at its origin. Optional: one faint PointLight "
            "(range 6, Brightness 0.4, #D8FF6A) at the centre.")
def firefly_cluster_low(pb):
    _specks(pb, random.Random(701), 16, 1.4, 0.3, 1.8)


@prop("firefly_swarm", ["H8"], "P2", target=[3.2, 4.2, 3.2], group="nature",
      notes="Pass 7 Firefly Hollow: 26 firefly specks rising in a loose spiral column up to ~4.2 (Neon #D8FF6A). "
            "The brightest H8 swarms get a spot light (manifest dressing spot_lights, kind firefly_glow).")
def firefly_swarm(pb):
    rnd = random.Random(702)
    for k in range(26):
        u = k / 25
        a = u * TAU * 1.7 + rnd.uniform(-0.6, 0.6)
        rr = 0.5 + 1.0 * u + rnd.uniform(-0.3, 0.3)
        r = 0.24 if k % 7 == 0 else rnd.uniform(0.1, 0.16)
        pb.sphere("Firefly", r, loc=(math.cos(a) * rr, math.sin(a) * rr, 0.6 + 3.6 * u + rnd.uniform(-0.25, 0.25)),
                  segs=4, rings=2, smooth=False)


@prop("glow_shroom_patch", ["H8"], "P2", target=[2.2, 1.1, 2.2], group="nature",
      notes="Pass 7 Firefly Hollow: 3 small bioluminescent mushrooms (ShroomGlow Neon caps, Firefly spots) on a "
            "moss pad. Cheap version of glowing_mushrooms (214 vs 2,040 tris).")
def glow_shroom_patch(pb):
    for k, (x, y, h, r, tx, ty) in enumerate(((0, 0, 0.85, 0.42, 0, 0), (0.55, 0.3, 0.6, 0.32, -10, 12),
                                              (-0.45, 0.4, 0.48, 0.27, 12, -8))):
        small_shroom(pb, h, r, (x, y, 0), (tx, ty), spot=k < 2)
    pb.cyl("Moss", 0.8, 0.65, 0.16, 7, loc=(0, 0, 0.06), smooth=False)


@prop("glow_root_arch", ["H8"], "P2", target=[4.6, 1.4, 1.2], group="nature",
      notes="Pass 7 Firefly Hollow: gnarled surface root (RootBark) arching out of the leaf floor and back in, a "
            "smaller side root, moss tufts and 2 small glow shrooms. Low (< 1.5): may sit beside rails.")
def glow_root_arch(pb):
    pts = [(-2.3, 0.0, -0.15), (-1.7, 0.1, 0.55), (-0.8, -0.05, 1.05), (0.2, 0.1, 1.15), (1.1, 0.0, 0.8),
           (1.9, 0.05, 0.3), (2.3, 0.0, -0.15)]
    pb.tube("RootBark", pts, [0.34, 0.32, 0.28, 0.26, 0.24, 0.22, 0.2], 5, wobble=0.04, seed=3)
    pb.tube("RootBark", [(-0.6, 0.0, 0.95), (-0.4, 0.8, 0.4), (-0.2, 1.3, -0.1)], [0.17, 0.14, 0.11], 4, wobble=0.03,
            seed=4)
    for x, y, sx in ((-1.9, 0.0, 0.8), (2.0, 0.0, 0.6)):
        pb.rock("Moss", (sx, 0.6, 0.22), loc=(x, y, 0), seed=int(x * 10) + 30, amp=0.08, ico=0)
    for k, (x, y, z, h, r) in enumerate(((-1.2, -0.35, 0.0, 0.5, 0.24), (0.9, 0.4, 0.0, 0.42, 0.2))):
        small_shroom(pb, h, r, (x, y, z), (8 * (k - 1), 6), spot=k == 0)
