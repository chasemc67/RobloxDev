# Pass 9 fit checks (H9 pendulum base plinth = Round-9 collider foot). exec()'d by fitcheck.py after fitcheck_pass8.py
# (uses its namespace: man, MP, HM, OUTD, check, lines, np, DL, felt_plane_y, bpy, os, math).
# All numbers (hinge, blockers, swing) are read from holes.json; the plinth is measured on the exported FBX.
lines.append("")
lines.append("# pass 9 (updated pass 10): H9 pendulum base plinth = the holes.json collider foot (Round 10: 1.0x0.4x1.6, yaw 0)")
P9_MIN_CLR = 0.02                    # brief: plinth (and whole mesh) >= 0.02 above the felt at every swing angle
P9_STEP = 0.001                      # deg: swing sampling step
_h9 = HM[9]
_pd = [m for m in _h9["moving_parts"] if m["id"] == "lantern_pendulum"][0]
_piv9 = np.array(_pd["pivot"], float)
_body_bl, _foot_bl = _pd["blockers"][0], _pd["blockers"][1]


def _fbx_parts(path):
    """{object name: (matrix_world 4x4, tris (n,3,3) Roblox axes, pivot frame)} of an exported FBX."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path, axis_forward="-Z", axis_up="Y")
    new = [o for o in bpy.data.objects if o not in before]
    bpy.context.view_layer.update()
    out = {}
    for o in new:
        if o.type != "MESH":
            continue
        me = o.data
        me.calc_loop_triangles()
        mw = np.array(o.matrix_world)
        V = np.array([v.co[:] for v in me.vertices], float) @ mw[:3, :3].T + mw[:3, 3]
        idx = np.array([t.vertices[:] for t in me.loop_triangles], int)
        T = V[idx]
        out[o.name.split(".")[0]] = (mw, np.stack([T[..., 0], T[..., 2], -T[..., 1]], -1))
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    return out


def _felt_y_vec(h, X, Z):
    """Vectorised felt_plane_y: highest felt surface under hole-local (X, Z); NaN where there is no felt."""
    best = np.full(X.shape, -np.inf)
    for f in h["felt"]:
        c = f["center"]
        a = math.radians(f.get("yaw", 0))
        dx, dz = X - c[0], Z - c[2]
        lx, lz = dx * math.cos(a) - dz * math.sin(a), dx * math.sin(a) + dz * math.cos(a)
        inside = (np.abs(lx) <= f["size"][0] / 2 + 1e-6) & (np.abs(lz) <= f["size"][1] / 2 + 1e-6)
        sl = f.get("slope") or {}
        y = np.full(X.shape, float(c[1]))
        if sl.get("rise"):
            y = y + sl["rise"] * (lx / f["size"][0] if sl.get("axis") == "x" else lz / f["size"][1])
        best = np.where(inside, np.maximum(best, y), best)
    return np.where(np.isfinite(best), best, np.nan)


def _surface_samples(T, n=12):
    """Triangle vertices + a barycentric grid on every triangle (pivot frame)."""
    pts = [T.reshape(-1, 3)]
    for i in range(n + 1):
        for j in range(n + 1 - i):
            a, b = i / n, j / n
            pts.append(T[:, 0] * (1 - a - b) + T[:, 1] * a + T[:, 2] * b)
    return np.unique(np.round(np.concatenate(pts), 9), axis=0)


def swing_clearance(P, angles, h=_h9, piv=_piv9, axis=_pd["axis"]):
    """min over angles of (point y - felt y under it), hole-local. P: (n,3) pivot frame. -> (min, angle, n_no_felt)."""
    k = np.asarray(axis, float) / np.linalg.norm(axis)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    best, best_a, nofelt = np.inf, None, 0
    for chunk in np.array_split(angles, max(1, len(angles) // 500)):
        r = np.radians(chunk)[:, None, None]
        R = np.eye(3) + np.sin(r) * K + (1 - np.cos(r)) * (K @ K)                 # (m,3,3) Rodrigues
        Q = np.einsum("mij,nj->mni", R, P) + piv
        fy = _felt_y_vec(h, Q[..., 0], Q[..., 2])
        nofelt += int(np.isnan(fy).sum())
        g = np.where(np.isnan(fy), np.inf, Q[..., 1] - fy).min(1)
        i = int(np.argmin(g))
        if g[i] < best:
            best, best_a = float(g[i]), float(chunk[i])
    return best, best_a, nofelt


def _box_local(P, bl):
    return (P - np.array(bl["center"], float)) @ DL.yaw_mat(bl.get("yaw", 0.0))


def plinth_problem(Tp, Tbody):
    """None if the plinth tris Tp (pivot frame) are exactly the collider-foot box, centred under the body and (holes.json
    foot bottom - body bottom: Round 9 0.062, Round 10 0.059) below its bottom; else a reason."""
    if len(Tp) == 0:
        return "no plinth geometry"
    P = Tp.reshape(-1, 3)
    L = _box_local(P, _foot_bl)
    hf = np.array(_foot_bl["size"], float) / 2
    if np.any(np.abs(L) > hf + 1e-3):
        return f"outside the foot box by {float((np.abs(L) - hf).max()):.3f}"
    for ax in range(3):
        if L[:, ax].min() > -hf[ax] + 1e-3 or L[:, ax].max() < hf[ax] - 1e-3:
            return f"does not reach the foot faces on axis {'xyz'[ax]} ({L[:, ax].min():.3f}..{L[:, ax].max():.3f})"
    Pb = Tbody.reshape(-1, 3)
    drop = Pb[:, 1].min() - P[:, 1].min()
    want = (_body_bl["center"][1] - _body_bl["size"][1] / 2) - (_foot_bl["center"][1] - _foot_bl["size"][1] / 2)
    if abs(drop - want) > 1e-3:
        return f"bottom {drop:.4f} below the body bottom (want {want:.3f})"
    cb = (Pb.min(0) + Pb.max(0)) / 2
    cp = (P.min(0) + P.max(0)) / 2
    if np.abs(cb[[0, 2]] - cp[[0, 2]]).max() > 1e-3:
        return f"off-centre under the body by {np.abs(cb[[0, 2]] - cp[[0, 2]]).max():.3f}"
    return None


_fbx9 = os.path.join(OUTD, "fbx", "h9_lantern_pendulum.fbx")
_parts9 = _fbx_parts(_fbx9)
_iron = _parts9.get("h9_lantern_pendulum__Iron")
_body_bot = _body_bl["center"][1] - _body_bl["size"][1] / 2                     # -7.9 (lantern body bottom)
_plinth_T = _iron[1][(_iron[1][..., 1] < _body_bot + 0.4).all(1)] if _iron else np.zeros((0, 3, 3))
_bodyT = np.concatenate([T[(T[..., 1] < _body_bl["center"][1] + _body_bl["size"][1] / 2 + 1e-4).all(1)]
                         for nm, (mw, T) in _parts9.items() if nm != "h9_lantern_pendulum__Iron"])
_allT = np.concatenate([T for (mw, T) in _parts9.values()])
_pp = plinth_problem(_plinth_T, _bodyT)
_Pp = _plinth_T.reshape(-1, 3)
_Lb = _box_local(_Pp, _body_bl)
_poke = float((np.abs(_Lb[:, [0, 2]]) - np.array(_body_bl["size"], float)[[0, 2]] / 2).max())
check(f"H9 pendulum base plinth (FBX __Iron) == the holes.json collider foot {'x'.join(f'{v:g}' for v in _foot_bl['size'])} "
      f"yaw {_foot_bl.get('yaw', 0):g} (= {_foot_bl.get('yaw', 0) - _body_bl.get('yaw', 0):g} deg vs the body), centred "
      f"under the body, bottom {(_body_bot - (_foot_bl['center'][1] - _foot_bl['size'][1] / 2)):.3f} below it",
      _pp is None, _pp or f"{len(_plinth_T)} tris, x {_Pp[:, 0].min():.3f}..{_Pp[:, 0].max():.3f}, "
      f"y {_Pp[:, 1].min():.3f}..{_Pp[:, 1].max():.3f}, z {_Pp[:, 2].min():.3f}..{_Pp[:, 2].max():.3f}; corners poke "
      f"{_poke:.3f} past the body faces")
# rigid: the plinth is in the same MeshPart as the hinge pin and the bob's iron, every part's origin is the hinge, and at
# every swing angle the transformed plinth coincides with the transformed collider foot
_orig = max(float(np.abs(mw[:3, 3]).max()) for (mw, T) in _parts9.values())
_one = _iron is not None and (_iron[1][..., 1] > -0.3).any() and len(_plinth_T) > 0
_ang = np.arange(-_pd["amplitude_deg"], _pd["amplitude_deg"] + 1e-9, 0.25)
_FC = np.array([[sx, sy, sz] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)], float) * \
    np.array(_foot_bl["size"], float) / 2 @ DL.yaw_mat(_foot_bl.get("yaw", 0.0)).T + np.array(_foot_bl["center"], float)
_PC = np.array([_Pp[np.argmin(np.linalg.norm(_Pp - c, axis=1))] for c in _FC])
_dev = 0.0
for a_ in _ang:
    R_ = DL.axis_angle(_pd["axis"], a_)
    _dev = max(_dev, float(np.abs((_PC @ R_.T + _piv9) - (_FC @ R_.T + _piv9)).max()))
check("H9 pendulum plinth swings rigidly with the bob: one MeshPart with the hinge pin (__Iron), every part origin at "
      f"the hinge, plinth corners == collider-foot corners at every angle (+-{_pd['amplitude_deg']:g}, 0.25 deg steps)",
      _one and _orig < 1e-4 and _dev < 1e-3, f"origin offset {_orig:.1e}, max corner deviation {_dev:.1e}, "
      f"{len(_parts9)} parts")
# clearance over the swing: exact plinth geometry (verts + dense face samples) vs the actual felt under each point
_rng = _pd.get("range") or [-_pd["amplitude_deg"], _pd["amplitude_deg"]]
_lo, _hi = min(_rng[0], -_pd["amplitude_deg"]), max(_rng[1], _pd["amplitude_deg"])
P9_ANGLES = np.round(np.arange(_lo, _hi + 1e-9, P9_STEP), 6)
_Sp = _surface_samples(_plinth_T)
P9_CLR, P9_CLR_ANG, _nf = swing_clearance(_Sp, P9_ANGLES)
_rest, _, _ = swing_clearance(_Sp, np.array([0.0]))
_hc = math.hypot(_foot_bl["size"][0] / 2, -_foot_bl["center"][1] + _foot_bl["size"][1] / 2)
_an = math.degrees(math.atan2(_foot_bl["size"][0] / 2, -_foot_bl["center"][1] + _foot_bl["size"][1] / 2))
check(f"H9 pendulum plinth clears the felt by >= {P9_MIN_CLR:g} at every angle of the holes.json motion "
      f"(range {_rng}, amplitude {_pd['amplitude_deg']:g}; {len(P9_ANGLES)} angles at {P9_STEP:g} deg, "
      f"{len(_Sp)} exact surface points incl. corners)", P9_CLR >= P9_MIN_CLR and _nf == 0,
      f"min {P9_CLR:.4f} at {P9_CLR_ANG:+.3f} deg (analytic corner minimum {_piv9[1] - _hc - 1.0:.4f} at "
      f"+-{_an:.3f} deg over felt y 1.0), {_rest:.4f} at rest, {_nf} points off the felt")
_Sa = _allT.reshape(-1, 3)
P9_ALL, P9_ALL_ANG, _nfa = swing_clearance(_Sa, P9_ANGLES[::10])
check(f"H9 whole pendulum mesh clears the felt by >= {P9_MIN_CLR:g} over the swing (all FBX vertices, 0.01 deg)",
      P9_ALL >= P9_MIN_CLR, f"min {P9_ALL:.4f} at {P9_ALL_ANG:+.2f} deg")
_ntri = sum(len(T) for (mw, T) in _parts9.values())
check("H9 pendulum FBX < 20k tris and manifest triangles == FBX", _ntri < 20000 and
      MP["h9_lantern_pendulum"]["triangles"] == _ntri, f"{_ntri} tris")
# negative tests
_neg = _plinth_T + np.array([0, -0.01, 0])
_c, _a, _ = swing_clearance(_surface_samples(_neg), P9_ANGLES[::10])
check("negative test flagged: plinth 0.01 lower (clearance < 0.02 somewhere in the swing)",
      _c < P9_MIN_CLR, f"min {_c:.4f} at {_a:+.2f} deg")
_Rw = DL.yaw_mat(_body_bl.get("yaw", 0.0) - _foot_bl.get("yaw", 0.0))
_neg2 = (_plinth_T - _foot_bl["center"]) @ _Rw.T + _foot_bl["center"]
_r2 = plinth_problem(_neg2, _bodyT)
check("negative test flagged: plinth at the body's yaw (+30, not square to the swing)", _r2 is not None, _r2 or "")
check("negative test flagged: no plinth", plinth_problem(np.zeros((0, 3, 3)), _bodyT) is not None)
_neg4 = _plinth_T * np.array([1.2, 1, 1])
check("negative test flagged: plinth 20% wider than the foot", plinth_problem(_neg4, _bodyT) is not None,
      plinth_problem(_neg4, _bodyT) or "")
