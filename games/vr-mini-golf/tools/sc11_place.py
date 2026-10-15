"""Stage sc11: Sugarloaf Canyon cliff caps snap, near-felt full detail (LOD -> source), placeholder inventory + decals, H15 seam.
  PYTHONPATH=tools python3 tools/sc11_place.py caps [--apply]      (item 1: true-ground snap of the 6 cliffT caps -> caps.json)
  PYTHONPATH=tools python3 tools/sc11_place.py lodplan              (item 2: LOD pieces whose true footprint is <= 15 from felt)
  PYTHONPATH=tools python3 tools/sc11_place.py lodswap              (item 2: swap them back to the SC7Kit source meshes)
  PYTHONPATH=tools python3 tools/sc11_place.py placeholders         (item 3: inventory -> placeholders-raw.json)
  PYTHONPATH=tools python3 tools/sc11_place.py dress NAME [INV]     (sc10 felt/rail/float rules on the live place -> NAME.json)
Geometry: sc9_mesh_geom.py hulls/contact rings (/tmp/sc9/geom.json), live Model pivots, plan scales (sc10_place / sc10_dress).
Ground for the snap = sc10_place.trueground (render mesh of Terrain + visible non-dressing parts, not collision boxes).
"""
import json, sys
from pathlib import Path
import sc10_place as P
import sc10_dress as D
import sc9_place
from sc5_util import studio, fetch, GAME
from holes_to_lua import to_lua

OUT = GAME / 'playtests/stage-sc11'
D.OUT = OUT
CAPS = [832, 823, 821, 1247, 830, 1279]
SINK = 0.05
NEAR = 15.0


def cap_rows(W, s, ids, tag):
    rows = {}
    q_true, q_coll = [], {}
    for i in ids:
        pc = W.live[str(i)]; hulls, lo, hi, ring = W.fp(pc, i)
        hv = [(x, z) for H in hulls for x, z in H]
        pts = [[x, lo + 5, z] for x, y, z in ring] + [[x, lo + 5, z] for x, z in hv]
        q_true.append({'id': str(i), 'pts': pts}); q_coll[str(i)] = pts
        rows[i] = {'i': i, 'name': pc['name'], 'stem': pc['stem'], 'pivot': pc['pivot'], 'lowY': lo, 'highY': hi, 'nRing': len(ring)}
    tg = P.trueground(s, q_true); cg = W.ground(q_coll)
    for i, r in rows.items():
        n = r['nRing']; t = tg[str(i)]; c = cg[str(i)]
        def gaps(h): return [round(r['lowY'] - x[0], 3) if x else None for x in h]
        r['trueRing'] = gaps(t[:n]); r['trueHull'] = gaps(t[n:]); r['collRing'] = gaps(c[:n]); r['collHull'] = gaps(c[n:])
        r['trueGround'] = sorted({x[1] for x in t if x}); r['collGround'] = sorted({x[1] for x in c if x})
        r['trueRingTop'] = max([x[0] for x in t[:n] if x], default=None)
        fin = [g for g in r['trueRing'] if g is not None]
        r['trueGapMin'] = min(fin) if fin else None; r['trueGapMax'] = max(fin) if fin else None
        cf = [g for g in r['collRing'] if g is not None]
        r['collGapMin'] = min(cf) if cf else None
        r['collGroundParts'] = sorted({x[1] for x in c[:n] if x})
    return rows


def caps(apply):
    s = studio(); W = D.World(s, 'inventory-before')
    before = cap_rows(W, s, CAPS, 'before')
    plan = []
    for i, r in before.items():
        if r['trueRingTop'] is None: r['plan'] = 'no true ground under the ring'; continue
        dy = (r['trueRingTop'] - SINK) - r['lowY']; r['dy'] = dy
        plan.append({'i': i, 'dx': 0, 'dy': dy, 'dz': 0, 'tag': 'SC11CapSnap'})
    res = {'before': {str(k): v for k, v in before.items()}, 'plan': plan}
    if apply and plan:
        raw = fetch(s, '_G.SC5Out', P.MOVE.replace('__PLAN__', to_lua(plan)), timeout=900); res['move'] = json.loads(raw)
        W = D.World(s, 'inventory-before')
        after = cap_rows(W, s, CAPS, 'after'); res['after'] = {str(k): v for k, v in after.items()}
        rules = {}
        for i in CAPS:
            pc = W.live[str(i)]; hulls, lo, hi, ring = W.fp(pc, i)
            felt = W.felt_hits(hulls); rm, rk, _ = W.rail_min(hulls)
            g = W.ground({str(i): [[x, lo + 5, z] for x, y, z in ring]})[str(i)]
            fin = [lo - h[0] for h in g if h]; gap = min(fin) if fin else None
            tg = after[i]['trueGapMin']
            rules[str(i)] = {'felt': felt, 'railMin': round(rm, 3), 'rail': W.rails[rk][0] if rk is not None else None, 'collFloatGap': gap,
                             'trueFloatGap': tg, 'failFelt': bool(felt), 'failRail': rm < 1.0,
                             'failFloat': gap is None or gap > 0.1 or tg is None or tg > 0.1}
        res['rules'] = rules
    (OUT / ('caps.json' if apply else 'caps-plan.json')).write_text(json.dumps(res, indent=1) + '\n')
    for i in CAPS:
        b = before[i]; a = res.get('after', {}).get(str(i))
        print(i, b['name'], 'low %.2f' % b['lowY'], 'true gap %s..%s' % (b['trueGapMin'], b['trueGapMax']), 'coll gap', b['collGapMin'],
              'coll ground', [g.split('.')[-1] for g in b['collGroundParts']][:3], 'true ground', [g.split('.')[-1] for g in b['trueGround']][:3],
              'dy %.3f' % b.get('dy', 0), '-> after true %s..%s' % (a['trueGapMin'], a['trueGapMax']) if a else '')
    if 'rules' in res:
        for k, v in res['rules'].items(): print('  rules', k, v)


LODINFO = r'''
local rep={}
for _,f in workspace.CourseSugarloaf.Look7Dressing:GetChildren() do for _,m in f:GetChildren() do
 local lod=false local parts={}
 for _,p in m:GetChildren() do if p:IsA('MeshPart') then
  local isLod=p.Name:find('_lod__')~=nil if isLod then lod=true end
  local a={} for k,v in p:GetAttributes() do a[k]=typeof(v)=='string' and v or tostring(v) end
  table.insert(parts,{name=p.Name,mesh=p.MeshId,rf=p.RenderFidelity.Name,attrs=a}) end end
 if lod or m:GetAttribute('SC9LOD') then rep[tostring(m:GetAttribute('SC9LayoutIndex'))]={name=m.Name,stem=m:GetAttribute('SC9Stem'),attrLOD=m:GetAttribute('SC9LOD'),parts=parts} end
end end
_G.SC5Out=game.HttpService:JSONEncode(rep) return #_G.SC5Out
'''

SWAP = r'''
local plan=__PLAN__
local pieces=__PIECES__
local dress=workspace.CourseSugarloaf.Look7Dressing
local kit=game.ServerStorage.SC7Kit
local RY=CFrame.Angles(0,math.pi,0)
local by={} for _,f in dress:GetChildren() do for _,m in f:GetChildren() do by[m:GetAttribute('SC9LayoutIndex')]=m end end
local rep={swapped={},partsBefore=0,partsAfter=0}
for _,e in plan do local m=assert(by[e.i],'piece '..e.i)
 assert(m:GetAttribute('SC9Stem')==e.lodStem,'stem '..e.i)
 local root=m.WorldPivot local s=Vector3.new(table.unpack(e.scale))
 local old={} for _,p in m:GetChildren() do if p:IsA('BasePart') then table.insert(old,p) end end
 local new={}
 for _,n in assert(pieces[e.stem],'stem '..e.stem) do
  local t=assert(kit:FindFirstChild(n.name),'template '..n.name)
  local p=t:Clone()
  p.Size=Vector3.new(table.unpack(n.size))*s
  p.CFrame=root*CFrame.new(Vector3.new(table.unpack(n.center))*s)*RY
  p.Anchored=true p.CanCollide=false p.CanQuery=false p.CanTouch=false p.Massless=true
  pcall(function() p.CollisionFidelity=Enum.CollisionFidelity.Box end)
  p.RenderFidelity=Enum.RenderFidelity.Automatic
  p:SetAttribute('VisualQueryDisabled',true)
  table.insert(new,p)
 end
 rep.partsBefore+=#old rep.partsAfter+=#new
 for _,p in old do p:Destroy() end
 for _,p in new do p.Parent=m end
 m.WorldPivot=root
 m:SetAttribute('SC9Stem',e.stem) m:SetAttribute('SC9LOD',false) m:SetAttribute('SC11FullDetail',e.lodStem)
 for _,p in m:GetChildren() do assert(not p.CanCollide and not p.CanQuery and not p.CanTouch,'flags') end
 table.insert(rep.swapped,{i=e.i,name=m.Name,from=e.lodStem,to=e.stem,old=#old,new=#new})
end
_G.SC5Out=game.HttpService:JSONEncode(rep) return #_G.SC5Out
'''


def lodplan(s=None):
    s = s or studio(); W = D.World(s, 'inventory-before')
    info = json.loads(fetch(s, '_G.SC5Out', LODINFO, timeout=600))
    rows = []
    for i, x in info.items():
        pc = W.live[i]; hulls, lo, hi, ring = W.fp(pc, i)
        best = (1e9, None)
        for H in hulls:
            cx, cz, r = D.circle(H)
            for f in W.felt:
                import math
                if math.hypot(cx - f[3][0], cz - f[3][1]) > r + f[3][2] + NEAR + 1: continue
                d, _ = D.dist(H, f[2])
                if d < best[0]: best = (d, f[0])
        rows.append({'i': int(i), 'name': x['name'], 'stem': x['stem'], 'feltDist': round(best[0], 3) if best[1] else None, 'felt': best[1],
                     'parts': [p['name'] for p in x['parts']], 'pivot': pc['pivot']})
    rows.sort(key=lambda r: (r['feltDist'] is None, r['feltDist'] or 0))
    near = [r for r in rows if r['feltDist'] is not None and r['feltDist'] <= NEAR]
    res = {'rule': 'Look7 piece using SC9LODKit meshes whose true XZ footprint (sc9 slot hulls, live pivot, plan scale) is within 15 '
                   'studs (plan distance) of any GolfSurface plan polygon', 'lodPieces': len(rows), 'near': len(near), 'rows': rows}
    (OUT / 'lod-plan.json').write_text(json.dumps(res, indent=1) + '\n')
    print('lod pieces', len(rows), 'near', len(near))
    for r in near: print(' ', r['i'], r['name'], r['feltDist'], r['felt'].split('.')[-3:] if r['felt'] else '')
    return near


def lodswap():
    s = studio(); near = lodplan(s)
    by = sc9_place.meshes_by_stem(); sc = P.scales()
    plan = [{'i': r['i'], 'lodStem': r['stem'], 'stem': r['stem'][:-4], 'scale': sc[r['i']]} for r in near]
    assert all(r['stem'].endswith('_lod') for r in near)
    pieces = {k: [dict(name=m['name'], center=m['center'], size=m['size']) for m in by[k]] for k in {p['stem'] for p in plan}}
    raw = fetch(s, '_G.SC5Out', SWAP.replace('__PLAN__', to_lua(plan)).replace('__PIECES__', to_lua(pieces)), timeout=900)
    (OUT / 'lod-swap.json').write_text(raw + '\n'); r = json.loads(raw)
    print('swapped', len(r['swapped']), 'parts', r['partsBefore'], '->', r['partsAfter'])


PLACEHOLDERS = r'''
local course=workspace.CourseSugarloaf
local rep={}
local function hole(p) local h=p:FindFirstAncestorWhichIsA('Model') while h and not h.Name:match('^Hole%d+$') do h=h.Parent and h.Parent:FindFirstAncestorWhichIsA('Model') end
 if h then return tonumber(h.Name:sub(5)) end local s=p:GetFullName():match('Hole(%d+)') return s and tonumber(s) end
local seen={}
for _,p in course:GetDescendants() do
 local why={}
 if p:FindFirstAncestor('Placeholder') then table.insert(why,'ancestor Placeholder') end
 if p.Name:lower():find('placeholder') then table.insert(why,'name') end
 for _,t in p:GetTags() do if t:lower():find('placeholder') then table.insert(why,'tag '..t) end end
 for k,v in p:GetAttributes() do if k:lower():find('placeholder') then table.insert(why,'attr '..k) end end
 if #why>0 and p:IsA('BasePart') then
  local a={} for k,v in p:GetAttributes() do a[k]=tostring(v) end
  local dec={} for _,c in p:GetChildren() do if c:IsA('Decal') or c:IsA('Texture') or c:IsA('SurfaceGui') then table.insert(dec,c.ClassName..':'..c.Name) end end
  table.insert(rep,{path=p:GetFullName(),name=p.Name,parent=p.Parent.Name,grand=p.Parent.Parent and p.Parent.Parent.Name,class=p.ClassName,hole=hole(p),
   visible=p.Transparency<1,transparency=p.Transparency,size={p.Size.X,p.Size.Y,p.Size.Z},cf={p.CFrame:GetComponents()},
   material=p.Material.Name,color=p.Color:ToHex(),collide=p.CanCollide,query=p.CanQuery,touch=p.CanTouch,tags=p:GetTags(),attrs=a,why=why,children=dec,
   shape=p:IsA('Part') and p.Shape.Name or ''})
 elseif #why>0 and not seen[p] then
  local a={} for k,v in p:GetAttributes() do a[k]=tostring(v) end
  table.insert(rep,{path=p:GetFullName(),name=p.Name,class=p.ClassName,container=true,why=why,attrs=a,tags=p:GetTags(),hole=hole(p)})
 end
end
_G.SC5Out=game.HttpService:JSONEncode(rep) return #_G.SC5Out
'''


if __name__ == '__main__':
    a = sys.argv[1]
    if a == 'caps': caps('--apply' in sys.argv)
    elif a == 'lodplan': lodplan()
    elif a == 'lodswap': lodswap()
    elif a == 'placeholders':
        s = studio(); raw = fetch(s, '_G.SC5Out', PLACEHOLDERS, timeout=600)
        (OUT / 'placeholders-raw.json').write_text(raw + '\n'); r = json.loads(raw)
        parts = [x for x in r if not x.get('container')]
        print('rows', len(r), 'parts', len(parts), 'visible', sum(x['visible'] for x in parts), 'containers', len(r) - len(parts))
    elif a == 'dress':
        s = studio(); W = D.World(s, sys.argv[3] if len(sys.argv) > 3 else 'inventory-before'); D.check(W, sys.argv[2])
