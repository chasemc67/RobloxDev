"""Pass 8 (playtest round 2 + Game Art Bot lighting direction): lantern-lit H9, rail lanterns on H7 / H8.

  lantern_large_hanging  the existing lantern_large paper lantern (same mesh) on a CORD_L-stud iron cord. Placed at
                         scale 0.85 (1.2 x 1.8 x 1.2 lantern, props.md) on holes.json Round-7 anchors amber_lantern_1..3
                         over the H9 heart green, bottom 8 above the felt, cord top at y ~16
  rail_lantern_stake     H7 lower tiers: small paper lantern on a short oak stake, 1.9 tall (< the 2-stud tall-prop
                         line, so it may stand right outside a rail)
  rail_lantern_crook     H8: the H8 walls are 3.9 tall, so a stake lantern would hide behind them. Oak post with a
                         crook arm (+X) and the lantern hanging from it ABOVE eye band (bottom 5.25 above the base):
                         the post stands >= 3 back from the rail, the lantern reaches to ~1.3 off the rail face.
All: decoration only (no collision). Glow core = Neon 'Glow'; PointLight per lantern in manifest.lights[] (amber
Color3(255, 169, 87), ~2700K).
"""
from registry import prop

CORD_L = 8.35             # cord above the hang point: at the placed scale 0.85 the ring tops out at y ~16 (props.md)
CROOK_REACH = 2.0          # crook arm: lantern centre this far along +X from the post axis
CROOK_LANT_Z = 5.25        # crook lantern bottom above the origin (>= tall-prop eye band 5.0)
CROOK_LANT_H = 0.85


@prop("lantern_large_hanging", ["H9"], "P1", target=[1.44, 2.0 + CORD_L, 1.44], group="lanterns",
      notes=f"Pass 8: lantern_large (same paper lantern mesh, 2.0 tall) on a {CORD_L:g}-stud iron cord with a ring at "
            "the top; origin = lantern bottom centre. Placed at scale 0.85 on the holes.json amber_lantern_1..3 anchors "
            "over the H9 heart green (bottom 8 above the felt, cord top y ~16). Neon core: PointLight Range 16, "
            "Color3(255,169,87) (manifest.lights[]).")
def lantern_large_hanging(pb):
    h = 2.0
    tass = h * 0.12
    pb.lantern(h - tass * 0.5, loc=(0, 0, tass * 0.5))          # == lantern_large
    pb.cyl("Iron", 0.035, 0.035, CORD_L, 4, loc=(0, 0, h + CORD_L / 2), smooth=False)
    pb.torus("Iron", 0.12, 0.03, 6, 3, loc=(0, 0, h + CORD_L + 0.1), rot=(90, 0, 0))


@prop("rail_lantern_stake", ["H7"], "P1", target=[0.45, 1.9, 0.45], group="lanterns",
      notes="Pass 8: small paper lantern on a short oak stake, 1.9 tall (under the 2-stud tall-prop line), placed "
            "~every 10 studs outside both rails of the H7 lower tiers. Neon core: PointLight Range 10, "
            "Color3(255,169,87) (manifest.lights[]).")
def rail_lantern_stake(pb):
    pb.cyl("Oak", 0.09, 0.07, 1.12, 5, loc=(0, 0, 0.56), smooth=False)
    pb.cyl("Iron", 0.17, 0.17, 0.05, 6, loc=(0, 0, 1.125), smooth=False)
    pb.lantern(0.75, loc=(0, 0, 1.15), hook=False, lod=1)


@prop("rail_lantern_crook", ["H8"], "P1", target=[2.4, 6.2, 0.5], group="lanterns",
      notes=f"Pass 8: oak post with a crook arm along local +X; a small paper lantern hangs {CROOK_REACH:g} out at "
            f"{CROOK_LANT_Z:g}..{CROOK_LANT_Z + CROOK_LANT_H:g} above the base, visible over H8's 3.9-tall walls. "
            "Yaw so +X points at the rail. Neon core: PointLight Range 10, Color3(255,169,87) (manifest.lights[]).")
def rail_lantern_crook(pb):
    top = CROOK_LANT_Z + CROOK_LANT_H + 0.3
    pb.cyl("Oak", 0.12, 0.09, top + 0.1, 5, loc=(0, 0, (top + 0.1) / 2), smooth=False)
    pb.box("Oak", (CROOK_REACH + 0.15, 0.12, 0.12), loc=(CROOK_REACH / 2, 0, top))
    pb.box("Oak", (0.1, 0.1, 0.7), loc=(0.3, 0, top - 0.3), rot=(0, 45, 0))          # brace
    pb.cyl("Iron", 0.02, 0.02, 0.3, 3, loc=(CROOK_REACH, 0, top - 0.15), smooth=False)
    pb.lantern(CROOK_LANT_H, loc=(CROOK_REACH, 0, CROOK_LANT_Z), lod=1)
