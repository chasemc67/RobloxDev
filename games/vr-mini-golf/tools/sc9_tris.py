"""Stage sc9: triangle count of the open place, exact per MeshId (AssetService:CreateEditableMeshAsync -> #GetFaces()).
  PYTHONPATH=tools python3 tools/sc9_tris.py cache            (count every MeshId used in Workspace/ServerStorage; cached in
                                                              playtests/stage-sc9/mesh-tris.json, only new ids are queried)
  PYTHONPATH=tools python3 tools/sc9_tris.py report TAG       (visible MeshParts around the H1 tee -> tris-TAG.json)
Visible = a Workspace MeshPart with Transparency < 1. Distance = 3D distance from the H1 tee camera (tee + 5 up) to the
nearest point of the part's bounding box. Non-mesh BaseParts are counted separately (12 tris per block, the rest by class).
"""
import json, sys, math
from sc5_util import studio, fetch, GAME

OUT = GAME / 'playtests/stage-sc9'
CACHE = OUT / 'mesh-tris.json'
H1_CAM = (60, 17.982 + 5, -4530)

IDS = r'''
local seen,ids={},{}
for _,root in {workspace,game.ServerStorage} do for _,p in root:GetDescendants() do
 if p:IsA('MeshPart') and p.MeshId~='' and not seen[p.MeshId] then seen[p.MeshId]=true table.insert(ids,p.MeshId) end end end
_G.SC5Out=game.HttpService:JSONEncode(ids) return #_G.SC5Out
'''

COUNT = r'''
local AS=game:GetService('AssetService')
local ids=__IDS__
local r={}
for _,id in ids do
 local ok,em=pcall(function() return AS:CreateEditableMeshAsync(Content.fromUri(id)) end)
 if ok then r[id]=#em:GetFaces() em:Destroy() else r[id]='ERR '..tostring(em) end
end
_G.SC5Out=game.HttpService:JSONEncode(r) return #_G.SC5Out
'''

PARTS = r'''
local r={}
for _,p in workspace:GetDescendants() do if p:IsA('BasePart') and p.Transparency<1 then
 local s=p.Size local c=p.CFrame
 local ext=Vector3.new(math.abs(c.RightVector.X)*s.X+math.abs(c.UpVector.X)*s.Y+math.abs(c.LookVector.X)*s.Z,
  math.abs(c.RightVector.Y)*s.X+math.abs(c.UpVector.Y)*s.Y+math.abs(c.LookVector.Y)*s.Z,
  math.abs(c.RightVector.Z)*s.X+math.abs(c.UpVector.Z)*s.Y+math.abs(c.LookVector.Z)*s.Z)/2
 local look=p:FindFirstAncestor('Look7Dressing')
 table.insert(r,{p.ClassName,p:IsA('MeshPart') and p.MeshId or (p:IsA('Part') and p.Shape.Name or ''),
  {c.X,c.Y,c.Z},{ext.X,ext.Y,ext.Z},look and 1 or 0,p:IsA('MeshPart') and p.RenderFidelity.Name or ''})
end end
_G.SC5Out=game.HttpService:JSONEncode(r) return #_G.SC5Out
'''

PRIM = {'Block': 12, 'Wedge': 8, 'CornerWedge': 6, 'Ball': 1200, 'Cylinder': 300}  # rough engine primitives


def dist(c, e):
    d = [max(abs(c[i] - H1_CAM[i]) - e[i], 0) for i in range(3)]
    return math.sqrt(sum(x * x for x in d))


if __name__ == '__main__':
    s = studio()
    if sys.argv[1] == 'cache':
        cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
        ids = [i for i in json.loads(fetch(s, '_G.SC5Out', IDS)) if not isinstance(cache.get(i), int)]
        print('to query', len(ids), 'cached', len(cache))
        for k in range(0, len(ids), 40):
            r = json.loads(fetch(s, '_G.SC5Out', COUNT.replace('__IDS__', json.dumps(ids[k:k + 40]).replace('[', '{').replace(']', '}')), timeout=600))
            cache.update(r); CACHE.write_text(json.dumps(cache) + '\n'); print(k + len(r), flush=True)
        print('errors', sum(not isinstance(v, int) for v in cache.values()))
    elif sys.argv[1] == 'report':
        cache = json.loads(CACHE.read_text())
        rows = json.loads(fetch(s, '_G.SC5Out', PARTS))
        miss = {r[1] for r in rows if r[0] == 'MeshPart' and not isinstance(cache.get(r[1]), int)}
        radii = [60, 120, 250, 500, 1000, 1e9]
        res = {'camera': H1_CAM, 'missingMeshIds': sorted(miss), 'byRadius': {}}
        for R in radii:
            t = {'meshTris': 0, 'meshParts': 0, 'look7Tris': 0, 'look7Parts': 0, 'otherMeshTris': 0, 'primitiveParts': 0, 'primitiveTrisApprox': 0}
            for cls, mid, c, e, look, fid in rows:
                if dist(c, e) > R: continue
                if cls == 'MeshPart':
                    n = cache.get(mid); n = n if isinstance(n, int) else 0
                    t['meshTris'] += n; t['meshParts'] += 1
                    if look: t['look7Tris'] += n; t['look7Parts'] += 1
                    else: t['otherMeshTris'] += n
                else:
                    t['primitiveParts'] += 1; t['primitiveTrisApprox'] += PRIM.get(mid, 12) if cls == 'Part' else 12
            res['byRadius']['all' if R == 1e9 else str(R)] = t
        res['maxDistance'] = max(dist(c, e) for _, _, c, e, _, _ in rows)
        res['renderFidelity'] = {}
        for cls, mid, c, e, look, fid in rows:
            if cls == 'MeshPart': k = ('look7:' if look else 'other:') + fid; res['renderFidelity'][k] = res['renderFidelity'].get(k, 0) + 1
        (OUT / ('tris-' + sys.argv[2] + '.json')).write_text(json.dumps(res, indent=1) + '\n')
        print(json.dumps({k: v for k, v in res.items() if k != 'missingMeshIds'}, indent=1), 'missing', len(miss))
