"""Minimal local stand-in for the subset of `trimesh` used by the kit_v1/kit_v22 generators.
Written for this thumbnail job because trimesh is not installed on the render PC. Pure numpy.
Implements: Trimesh(vertices, faces, process) with vertices/faces/copy/apply_transform/apply_translation/
apply_scale/fix_normals/face_normals/triangles_center/submesh; creation.box/icosphere; transformations.
rotation_matrix/translation_matrix/transform_points; geometry.align_vectors."""
import numpy as np
from . import creation, transformations, geometry  # noqa


class Trimesh:
    def __init__(self, vertices=None, faces=None, process=False, **kw):
        self.vertices = np.array(vertices, dtype=float).reshape(-1, 3)
        self.faces = np.array(faces, dtype=np.int64).reshape(-1, 3)

    def copy(self):
        return Trimesh(self.vertices.copy(), self.faces.copy())

    def apply_transform(self, M):
        M = np.asarray(M, float)
        v = np.c_[self.vertices, np.ones(len(self.vertices))] @ M.T
        self.vertices = v[:, :3]
        if np.linalg.det(M[:3, :3]) < 0:
            self.faces = self.faces[:, ::-1].copy()
        return self

    def apply_translation(self, t):
        self.vertices = self.vertices + np.asarray(t, float)
        return self

    def apply_scale(self, s):
        self.vertices = self.vertices * np.asarray(s, float)
        if np.ndim(s) and np.prod(s) < 0:
            self.faces = self.faces[:, ::-1].copy()
        return self

    @property
    def triangles(self):
        return self.vertices[self.faces]

    @property
    def triangles_center(self):
        return self.triangles.mean(axis=1)

    @property
    def face_normals(self):
        t = self.triangles
        n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
        l = np.linalg.norm(n, axis=1, keepdims=True)
        return n / np.where(l == 0, 1, l)

    def _signed_volume(self):
        t = self.triangles
        return np.einsum('ij,ij->i', t[:, 0], np.cross(t[:, 1], t[:, 2])).sum() / 6.0

    def fix_normals(self, **kw):
        # Generators build consistently-wound ring solids; only the global orientation can be inverted.
        # (Blender build additionally recalculates normals per island.)
        if len(self.faces) and self._signed_volume() < 0:
            self.faces = self.faces[:, ::-1].copy()
        return self

    def submesh(self, faces_sequence, append=True, **kw):
        sel = np.concatenate([np.asarray(f, np.int64).ravel() for f in faces_sequence])
        F = self.faces[sel]
        used, inv = np.unique(F.ravel(), return_inverse=True)
        return Trimesh(self.vertices[used], inv.reshape(-1, 3))
