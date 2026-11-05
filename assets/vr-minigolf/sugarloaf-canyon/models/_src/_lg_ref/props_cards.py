"""Pass 4 card-style treeline clumps (Quest performance): 3 crossed, double-sided vertical quads (12 tris) with an
alpha-cut painted clump texture (textures/card_red.png, card_gold.png). They replace 3D dressing beyond ~40-60
studs from a hole's felt (a 3D tree_backdrop_cluster is 834 tris). In Roblox: one MeshPart, SurfaceAppearance
ColorMap = the PNG with AlphaMode = Transparency (or MeshPart.TextureID; the alpha is a hard 0/255 cut), CastShadow
off, DoubleSided not needed (back faces are real geometry)."""
import math
import bmesh
from mathutils import Vector
import lglib
from registry import prop

lglib.MATS.update({
    "CardRed": ("#C8452A", "SmoothPlastic", 0, 0, "treeline card, red/orange clump (alpha-cut texture)"),
    "CardGold": ("#E8A42A", "SmoothPlastic", 0, 0, "treeline card, gold clump (alpha-cut texture)"),
})
lglib.TEX["CardRed"] = ("card_red", 24.0)
lglib.TEX["CardGold"] = ("card_gold", 24.0)
lglib.CARD_MATS |= {"CardRed", "CardGold"}
CARD_W, CARD_H = 24.0, 12.0


def crossed_cards(pb, mat, w=CARD_W, h=CARD_H, n=3, sink=0.6):
    for k in range(n):
        a = math.pi * k / n + 0.2
        d = Vector((math.cos(a), math.sin(a), 0)) * (w / 2)
        nrm = Vector((-math.sin(a), math.cos(a), 0)) * 0.03
        for flip in (False, True):
            b = bmesh.new()
            off = -nrm if flip else nrm
            vs = [b.verts.new(p + off) for p in (-d + Vector((0, 0, -sink)), d + Vector((0, 0, -sink)),
                                           d + Vector((0, 0, h - sink)), -d + Vector((0, 0, h - sink)))]
            b.faces.new(vs[::-1] if flip else vs)
            pb.add(mat, b)


for _nm, _mat in (("treeline_card_red", "CardRed"), ("treeline_card_gold", "CardGold")):
    def _mk(mat):
        def fn(pb):
            crossed_cards(pb, mat)
        return fn
    prop(_nm, ["all"], "P2", target=[CARD_W, CARD_H - 0.6, CARD_W], group="dressing",
         notes=f"Card treeline clump ({_mat}): 3 crossed double-sided quads, 12 tris, alpha-cut texture. Far-field "
               "(beyond ~40-60 studs from felt) replacement for 3D tree clumps.")(_mk(_mat))
