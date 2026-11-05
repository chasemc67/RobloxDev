# Pass 10 fit checks. exec()'d by fitcheck.py after fitcheck_pass9.py (uses its namespace: _pd, _foot_bl, _body_bl,
# _plinth_T, _bodyT, _piv9, plinth_problem, swing_clearance, _surface_samples, P9_*, MP, HM, OUTD, check, lines, np).
# Job 1: H9 plinth = Round 10 collider foot 1.0 x 0.4 x 1.6, swing +-11 deg / 4 s. The brief's numbers are written out
# here as the spec; each is also compared with holes.json, so drift in either one is flagged.
lines.append("")
lines.append("# pass 10: H9 pendulum plinth Round 10 (1.0 x 0.4 x 1.6, yaw 0, bottom 0.059 below the body), swing +-11 deg / 4 s")
P10_FOOT = dict(size=(1.0, 0.4, 1.6), yaw=0.0, drop=0.059)            # brief_pass10 / props.md Round 10
P10_HINGE = (21.2, 8.996, -38.5)
P10_SWING = dict(amplitude_deg=11.0, period_s=4.0)

_hf = np.array(_foot_bl["size"], float)
check("H9 holes.json collider foot == the Round 10 spec 1.0x0.4x1.6 yaw 0, hinge (21.2, 8.996, -38.5), +-11 deg / 4 s",
      np.allclose(_hf, P10_FOOT["size"], atol=1e-6) and abs(_foot_bl.get("yaw", 0.0) - P10_FOOT["yaw"]) < 1e-6 and
      np.allclose(_piv9, P10_HINGE, atol=1e-6) and abs(_pd["amplitude_deg"] - P10_SWING["amplitude_deg"]) < 1e-6 and
      abs(_pd["period_s"] - P10_SWING["period_s"]) < 1e-6,
      f"foot {list(_hf)} yaw {_foot_bl.get('yaw', 0)} centre {_foot_bl['center']}, hinge {list(_piv9)}, "
      f"amp {_pd['amplitude_deg']} T {_pd['period_s']} range {_pd.get('range')}")


def p10_plinth_dims(T):
    """(size along course x, y, z) of plinth tris T (pivot frame, yaw-0 box) and the drop below the body bottom."""
    P = T.reshape(-1, 3)
    return P.max(0) - P.min(0), float(_bodyT.reshape(-1, 3)[:, 1].min() - P[:, 1].min())


_dims, _drop = p10_plinth_dims(_plinth_T)
check("H9 plinth measured on the FBX: 1.0 (x, along the swing) x 0.4 x 1.6, bottom 0.059 below the body bottom",
      np.allclose(_dims, P10_FOOT["size"], atol=1e-3) and abs(_drop - P10_FOOT["drop"]) < 1e-3,
      f"{_dims[0]:.4f} x {_dims[1]:.4f} x {_dims[2]:.4f}, drop {_drop:.4f}")
_mm = MP["h9_lantern_pendulum"].get("motion", {})


def p10_motion_problem(mm):
    bad = [k for k in ("amplitude_deg", "period_s") if abs(float(mm.get(k, -1)) - float(_pd[k])) > 1e-6]
    if list(mm.get("range", [])) != list(_pd["range"]):
        bad.append("range")
    if not np.allclose(mm.get("course_local_pivot", [0, 0, 0]), _piv9, atol=1e-6):
        bad.append("pivot")
    return ", ".join(bad) or None


check("H9 pendulum manifest motion == holes.json (amplitude, period, range, hinge)", p10_motion_problem(_mm) is None,
      p10_motion_problem(_mm) or f"{_mm.get('formula')}")
check("H9 plinth clearance >= 0.02 sampled over the whole Round 10 range [-11, 11] at 0.001 deg (pass 9 rule)",
      P9_ANGLES.min() <= -P10_SWING["amplitude_deg"] + 1e-9 and P9_ANGLES.max() >= P10_SWING["amplitude_deg"] - 1e-9
      and P9_CLR >= P9_MIN_CLR, f"{len(P9_ANGLES)} angles {P9_ANGLES.min():g}..{P9_ANGLES.max():g}: min {P9_CLR:.4f} "
      f"at {P9_CLR_ANG:+.3f} deg")
# negative tests (Round 10)
_c9 = (_plinth_T - _foot_bl["center"]) * np.array([0.9, 1, 1]) + _foot_bl["center"]
check("negative test flagged: the Round 9 plinth (0.9 along the swing) no longer matches the foot",
      plinth_problem(_c9, _bodyT) is not None, plinth_problem(_c9, _bodyT) or "")
_lo5 = _plinth_T + np.array([0, -0.005, 0])
_c5, _a5, _ = swing_clearance(_surface_samples(_lo5), P9_ANGLES[::10])
check("negative test flagged: plinth 0.005 lower (clearance < 0.02 in the swing)", _c5 < P9_MIN_CLR,
      f"min {_c5:.4f} at {_a5:+.2f} deg")
check("negative test flagged: manifest swing left at the Round 9 +-13 deg",
      p10_motion_problem(dict(_mm, amplitude_deg=13.0, range=[-13.0, 13.0])) is not None)
_sh = _plinth_T + np.array([0.05, 0, 0])
check("negative test flagged: plinth 0.05 off-centre along the swing", plinth_problem(_sh, _bodyT) is not None,
      plinth_problem(_sh, _bodyT) or "")

# Job 2: vr_wrist_bracer, verified on the re-imported FBX (Roblox axes: x, y, z = Blender x, z, -y)
lines.append("")
lines.append("# pass 10: vr_wrist_bracer (re-imported FBX): WristFace 0.37 x 0.28 (~1.31, 1024x784 card; pass 10b), normal +Y, UVs 0-1, < 2k tris")
P10_FACE = dict(w=0.37, h=0.28, center=(0.0, 0.238, 0.0))


def p10_import_bracer(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path, axis_forward="-Z", axis_up="Y")
    new = [o for o in bpy.data.objects if o not in before]
    bpy.context.view_layer.update()
    out = {}
    for o in new:
        if o.type == "EMPTY":
            out["__root__"] = dict(mw=np.array(o.matrix_world), name=o.name)
        if o.type != "MESH":
            continue
        me = o.data
        me.calc_loop_triangles()
        mw = np.array(o.matrix_world)
        V = np.array([v.co[:] for v in me.vertices], float) @ mw[:3, :3].T + mw[:3, 3]
        V = np.stack([V[:, 0], V[:, 2], -V[:, 1]], -1)
        tris = np.array([t.vertices[:] for t in me.loop_triangles], int)
        uvl = me.uv_layers[0].data if me.uv_layers else None
        uvs = [(V[me.loops[li].vertex_index], tuple(uvl[li].uv)) for li in range(len(me.loops))] if uvl else []
        out[o.name.split(".")[0]] = dict(V=V, tris=tris, uvs=uvs, origin=mw[:3, 3].copy())
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    return out


def p10_face_problem(f):
    """None if face dict f (V, tris, uvs) is the exact flat 0.37 x 0.28 quad at the spec centre, normal +Y, UVs 0-1."""
    V, T = f["V"], f["tris"]
    if len(T) != 2:
        return f"{len(T)} tris (want 2)"
    ext = V.max(0) - V.min(0)
    if abs(ext[1]) > 1e-4:
        return f"not flat (y extent {ext[1]:.4f})"
    if abs(ext[0] - P10_FACE["w"]) > 1e-4 or abs(ext[2] - P10_FACE["h"]) > 1e-4:
        return f"size {ext[0]:.4f} x {ext[2]:.4f} (want 0.37 x 0.28)"
    if abs(ext[0] / ext[2] - 0.37 / 0.28) > 1e-3 or abs(ext[0] / ext[2] - 1024 / 784) > 0.02:
        return f"aspect {ext[0] / ext[2]:.4f}"
    c = (V.max(0) + V.min(0)) / 2
    if np.abs(c - P10_FACE["center"]).max() > 1e-4:
        return f"centre {np.round(c, 4).tolist()} (want {list(P10_FACE['center'])})"
    for t in T:
        n = np.cross(V[t[1]] - V[t[0]], V[t[2]] - V[t[0]])
        n = n / np.linalg.norm(n)
        if n[1] < 0.9999:
            return f"normal {np.round(n, 4).tolist()} (want +Y)"
    if not f["uvs"]:
        return "no UVs"
    mn = V.min(0)
    for p, (u, v) in f["uvs"]:
        eu, ev = (p[0] - mn[0]) / P10_FACE["w"], (V.max(0)[2] - p[2]) / P10_FACE["h"]
        if abs(u - eu) > 1e-4 or abs(v - ev) > 1e-4:
            return f"UV ({u:.3f}, {v:.3f}) at x {p[0]:.3f} z {p[2]:.3f} (want ({eu:.3f}, {ev:.3f}))"
    U = np.array([uv for _, uv in f["uvs"]])
    if abs(U.min()) > 1e-4 or abs(U.max() - 1) > 1e-4:
        return f"UV range {U.min():.4f}..{U.max():.4f}"
    return None


_br = p10_import_bracer(os.path.join(OUTD, "fbx", "vr_wrist_bracer.fbx"))
_face = _br.get("WristFace")
_fp = p10_face_problem(_face) if _face else "no MeshPart named WristFace"
if _face:
    _fe = _face["V"].max(0) - _face["V"].min(0)
    _fd = (f"{_fe[0]:.4f} x {_fe[2]:.4f} (aspect {_fe[0] / _fe[2]:.4f}), centre "
           f"{np.round((_face['V'].max(0) + _face['V'].min(0)) / 2, 4).tolist()}, {len(_face['uvs'])} UV loops")
check("vr_wrist_bracer FBX: separate MeshPart `WristFace` = flat 2-tri quad 0.37 (X) x 0.28 (Z), ratio 1.3214 (card 1.306), centre "
      "(0, 0.238, 0) from the pivot, normal +Y, UVs 0-1 filling it (U +X, V -Z)", _fp is None, _fp or _fd)
_ntb = sum(len(d["tris"]) for k, d in _br.items() if k != "__root__")
_mb = MP.get("vr_wrist_bracer", {})
check("vr_wrist_bracer FBX < 2000 tris and manifest triangles == FBX", _ntb < 2000 and _mb.get("triangles") == _ntb,
      f"{_ntb} tris, parts {sorted(k for k in _br if k != '__root__')}")
_orgb = max(float(np.abs(d["origin"]).max()) for k, d in _br.items() if k != "__root__")
_rootb = _br.get("__root__")
check("vr_wrist_bracer pivot = wrist centre: root + every part origin at (0,0,0); sleeve centred on the X axis",
      _orgb < 1e-5 and _rootb is not None and float(np.abs(_rootb["mw"][:3, 3]).max()) < 1e-5,
      f"part origin offset {_orgb:.1e}")
_lv = _br.get("vr_wrist_bracer__Leather", {}).get("V")
if _lv is not None:
    _sl = _lv[(np.abs(_lv[:, 1]) < 0.12)]                     # sleeve verts off the top pad
    _rin = float(np.hypot(_sl[:, 1], _sl[:, 2]).min())
else:
    _rin = 0
check("vr_wrist_bracer fits a 0.35-diameter forearm (sleeve inner radius >= 0.175, outer <= 0.25)",
      _rin >= 0.175 and _lv is not None and float(np.hypot(_sl[:, 1], _sl[:, 2]).max()) <= 0.25,
      f"sleeve inner radius {_rin:.4f}, outer {float(np.hypot(_sl[:, 1], _sl[:, 2]).max()) if _lv is not None else 0:.4f}")
_va = _mb.get("vr_attach", {})
check("vr_wrist_bracer manifest documents axes, face size, face centre offset and normal",
      all(k in _va.get("axes", {}) for k in "xyz") and _va.get("wrist_face", {}).get("size_studs") == [0.37, 0.28] and
      _va.get("wrist_face", {}).get("center_offset_from_pivot") == list(P10_FACE["center"]) and
      _va.get("wrist_face", {}).get("normal") == "+Y", f"{_va.get('wrist_face', {}).get('center_offset_from_pivot')}")
# negative tests on the face checker
if _face:
    _nf = dict(_face, V=_face["V"] * np.array([1, 1, 1.05]))
    check("negative test flagged: face 0.294 deep (wrong ratio)", p10_face_problem(_nf) is not None, p10_face_problem(_nf) or "")
    _nf = dict(_face, tris=_face["tris"][:, ::-1])
    check("negative test flagged: face normal flipped (-Y)", p10_face_problem(_nf) is not None, p10_face_problem(_nf) or "")
    _nf = dict(_face, uvs=[(p, (u * 0.5, v)) for p, (u, v) in _face["uvs"]])
    check("negative test flagged: UVs only filling half the face", p10_face_problem(_nf) is not None, p10_face_problem(_nf) or "")

    _nf = dict(_face, V=(_face["V"] - _face["V"].mean(0)) * np.array([0.32 / 0.37, 1, 0.20 / 0.28]) + _face["V"].mean(0))
    check("negative test flagged: old pass-10 face 0.32 x 0.20", p10_face_problem(_nf) is not None, p10_face_problem(_nf) or "")
