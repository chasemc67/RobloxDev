import math
import numpy as np


def rotation_matrix(angle, direction, point=None):
    d = np.asarray(direction, float)[:3]
    d = d / np.linalg.norm(d)
    s, c = math.sin(angle), math.cos(angle)
    R = np.diag([c, c, c]) + np.outer(d, d) * (1 - c)
    R += np.array([[0, -d[2], d[1]], [d[2], 0, -d[0]], [-d[1], d[0], 0]]) * s
    M = np.eye(4)
    M[:3, :3] = R
    if point is not None:
        p = np.asarray(point, float)[:3]
        M[:3, 3] = p - R @ p
    return M


def translation_matrix(direction):
    M = np.eye(4)
    M[:3, 3] = np.asarray(direction, float)[:3]
    return M


def transform_points(points, matrix):
    P = np.asarray(points, float)
    return (np.c_[P, np.ones(len(P))] @ np.asarray(matrix, float).T)[:, :3]
