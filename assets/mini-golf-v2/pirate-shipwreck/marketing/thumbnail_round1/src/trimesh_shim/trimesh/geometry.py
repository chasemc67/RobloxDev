import numpy as np


def align_vectors(a, b, return_angle=False):
    """4x4 rotation taking unit direction a onto b (Rodrigues)."""
    a = np.asarray(a, float); a = a / np.linalg.norm(a)
    b = np.asarray(b, float); b = b / np.linalg.norm(b)
    v = np.cross(a, b); c = float(np.dot(a, b))
    M = np.eye(4)
    if c < -1 + 1e-9:
        p = np.cross(a, [1, 0, 0]) if abs(a[0]) < 0.9 else np.cross(a, [0, 1, 0])
        p /= np.linalg.norm(p)
        M[:3, :3] = 2 * np.outer(p, p) - np.eye(3)
    else:
        K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
        M[:3, :3] = np.eye(3) + K + K @ K / (1 + c)
    return M
