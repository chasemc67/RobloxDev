import bpy, json, sys, os, numpy as np
argv = sys.argv[sys.argv.index("--")+1:]
root, outp = argv[0], argv[1]
cups = json.load(open(os.path.join(root, "_src", "cups_world.json")))
C = np.array([c["cup_world"] for c in cups])
def d2tri(P, T):
    # 2D distance from points P (n,2) to triangles T (m,3,2); returns (n,) min and inside flags
    best = np.full(len(P), 1e9)
    a, b, c = T[:,0], T[:,1], T[:,2]
    for i,p in enumerate(P):
        def seg(u, v):
            d = v-u; t = np.clip(((p-u)*d).sum(1)/np.maximum((d*d).sum(1),1e-12),0,1)
            q = u+d*t[:,None]; return np.hypot(*(p-q).T)
        dist = np.minimum(np.minimum(seg(a,b),seg(b,c)),seg(c,a))
        cr = lambda u,v: (v[:,0]-u[:,0])*(p[1]-u[:,1])-(v[:,1]-u[:,1])*(p[0]-u[:,0])
        s1,s2,s3 = cr(a,b),cr(b,c),cr(c,a)
        inside = ((s1>=0)&(s2>=0)&(s3>=0))|((s1<=0)&(s2<=0)&(s3<=0))
        dist[inside] = 0
        best[i] = dist.min() if len(dist) else 1e9
    return best
res = {}
for c in cups:
    hid = c["hid"]; piv = np.array(c["pivot"])
    for kind in ("ground", "dress_props", "dress_plants"):
        f = os.path.join(root, "fbx", f"{hid}_{kind}.fbx")
        if not os.path.exists(f): continue
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=f)
        tris, per = [], {}
        for o in bpy.context.scene.objects:
            if o.type != "MESH": continue
            me = o.data; me.calc_loop_triangles()
            V = np.array([o.matrix_world @ v.co for v in me.vertices])
            R = np.stack([V[:,0], V[:,2], -V[:,1]], 1) + piv
            T = np.array([[R[i] for i in lt.vertices] for lt in me.loop_triangles])
            per[o.name] = T
        allT = np.concatenate(list(per.values()))
        lo, hi = allT.reshape(-1,3).min(0)-piv, allT.reshape(-1,3).max(0)-piv
        entry = dict(bbox_from_pivot=[lo.round(2).tolist(), hi.round(2).tolist()], tris=int(len(allT)), cups={})
        for j, cc in enumerate(cups):
            # only geometry within +-6 studs of the cup height matters
            band = (allT[:,:,1].max(1) > cc["cup_world"][1]-6) & (allT[:,:,1].min(1) < cc["cup_world"][1]+6)
            if not band.any(): continue
            d = d2tri(np.array([[cc["cup_world"][0], cc["cup_world"][2]]]), allT[band][:,:,[0,2]])[0]
            if d < 10:
                byobj = {n: float(d2tri(np.array([[cc["cup_world"][0], cc["cup_world"][2]]]), T[:,:,[0,2]])[0]) for n,T in per.items()}
                entry["cups"][cc["hid"]] = dict(clear=round(float(d),3), by_mesh={k: round(v,3) for k,v in byobj.items() if v < 10})
        res[f"{hid}_{kind}"] = entry
        print(hid, kind, entry["tris"], {k:v["clear"] for k,v in entry["cups"].items()}, flush=True)
json.dump(res, open(outp, "w"), indent=1)
print("DONE")
