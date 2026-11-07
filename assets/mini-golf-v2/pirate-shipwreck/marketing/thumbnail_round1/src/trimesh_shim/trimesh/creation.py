import numpy as np


def box(extents=(1, 1, 1), transform=None, **kw):
    from . import Trimesh
    e = np.asarray(extents, float) / 2.0
    V = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)], float) * e
    # outward-wound quads (index = 4*ix + 2*iy + iz)
    Q = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    F = []
    for a, b, c, d in Q:
        F += [[a, b, c], [a, c, d]]
    m = Trimesh(V, F)
    m.fix_normals()
    if transform is not None:
        m.apply_transform(transform)
    return m


def icosphere(subdivisions=1, radius=1.0, **kw):
    from . import Trimesh
    t = (1 + 5 ** 0.5) / 2
    V = np.array([[-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0], [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t],
                  [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1]], float)
    F = [[0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11], [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
         [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9], [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]]
    V = V / np.linalg.norm(V, axis=1, keepdims=True) * radius
    m = Trimesh(V, F)
    m.fix_normals()
    return m
