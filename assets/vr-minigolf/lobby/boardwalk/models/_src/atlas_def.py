"""bw_atlas_1024.png layout (pure python, shared by make_atlas.py and bwlib.py).

Regions are pixel rects (x0, y0, x1, y1) with y measured from the TOP of the image (as in atlas_layout.md).
bwlib converts them to UV (v = 1 - y/1024). Rows follow atlas_layout.md exactly.
"""
SIZE = 1024

PAL = {
    "plank": "#B5835A", "plank_dark": "#7A4E2D", "post": "#8A5A34",
    "brass": "#C9A04A", "brass_hi": "#E8C979", "brass_lo": "#8C6A2A",
    "parch": "#F1E2BE", "ink": "#4A2F1A", "glow": "#FFC867", "rope": "#CDB38A",
    "turf": "#6FBF5A", "fringe": "#4F9A43", "awn_red": "#E2574C", "awn_cream": "#F6EBD8",
    "sand_red": "#D9714A", "sand_light": "#F0C9A0", "crystal": "#7B5BD6", "crystal_tip": "#9FE6F2",
    "bark": "#6B4429", "leaf_orange": "#E58A3A", "leaf_red": "#C9473A", "leaf_yellow": "#E8C24C",
    "stone": "#8D8A86", "ocean": "#3E8FB0", "shallows": "#6FC2D1", "fog": "#F2A57E",
}

# trim strips (full width, tile in U)
R = {
    "deck":      (0, 0, 1024, 128),      # row0: 8 planks of 16 px (14 plank + 2 gap) running along U
    "beam":      (0, 128, 1024, 256),    # row1: post/beam grain along U
    "brass":     (0, 256, 1024, 320),    # bevel gradient lo -> base -> hi -> base -> lo (across V)
    "rope":      (0, 320, 1024, 384),    # twisted rope strip
    "parch_panel": (0, 384, 512, 512),   # parchment with ink border (fit 0-1: panels, plates)
    "parch":     (512, 384, 1024, 512),  # plain parchment (no border)
    "awning":    (0, 512, 1024, 576),    # 8 stripes across 1024 (stripe changes along U)
    "stone":     (0, 576, 1024, 640),    # stone footing blocks
    "turf":      (0, 640, 1024, 704),    # turf with fringe edge rows at the band edges
    "sandstone": (0, 704, 1024, 768),    # horizontal bands, alternating along U (map U = height)
    "bark":      (0, 768, 1024, 832),    # bark grain along U
    "leaf_orange": (0, 832, 256, 896),
    "leaf_red":    (256, 832, 512, 896),
    "leaf_yellow": (512, 832, 768, 896),
    "crystal":     (768, 832, 1024, 896),
}

# flat swatch cells: 16 x 64 px wide, 2 rows of 64 px (rows 896-959, 960-1023)
SWATCH_ORDER = [
    "plank", "plank_dark", "post", "brass", "brass_hi", "brass_lo", "parch", "ink",
    "glow", "rope", "turf", "fringe", "awn_red", "awn_cream", "sand_red", "sand_light",
    "crystal", "crystal_tip", "bark", "leaf_orange", "leaf_red", "leaf_yellow", "stone", "ocean",
    "shallows", "fog",
]
SW = {}
for _i, _n in enumerate(SWATCH_ORDER):
    _x = (_i % 16) * 64
    _y = 896 + (_i // 16) * 64
    SW[_n] = (_x, _y, _x + 64, _y + 64)

# deck tile variants: U offset (fraction of strip) where the 10-stud tile starts; tile spans 0.5 of the strip
DECK_U0 = {"a": 0.0, "b": 0.5}
DECK_STRIP_STUDS = 20.0     # the full 1024 px strip = 20 studs of plank length
DECK_PLANKS = 8             # planks across one 10-stud tile (1.25 studs each)


def hex_rgb255(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
