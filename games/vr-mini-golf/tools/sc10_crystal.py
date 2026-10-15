"""Stage sc10: H16 slow-drop crystal test. Do balls falling through the 1.9 sinkhole opening visually pass through the
(non-colliding) rim crystals?
Play (Server): ball-sized physics spheres (r 0.08, as tools/sc8_h16_edge.py) on the deck around the opening:
  * rest drops: at rest on the square of Chebyshev half-width d (0.80, 0.85, 0.90, 0.925), 16 spots per d
  * slow putts: from 1.8 out along each axis, toward the opening, lateral offset 0 / 0.4 / 0.75 (both sides), speed 0.4/0.7/1.0
Every Heartbeat the ball centre is recorded in the rim frame (rim model pivot) while it is between felt + 0.2 and felt - 1.0.
Offline: each crystal is one connected component of the CrystalPink / CrystalAmber mesh (FBX vertices, rim-pivot frame,
Roblox axes; /tmp/sc10/rimverts_<b|d>.json from tools/sc10_rimverts.py). A crystal is convex, so the ball-centre distance is
0 inside (behind every face plane) or the min distance to its triangles. A HIT is a sample with distance < 0.08 (ball radius).
  PYTHONPATH=tools python3 tools/sc10_crystal.py run OUT.json
  python3 tools/sc10_crystal.py score OUT.json RIMVERTS.json
"""
import json, math, sys, time, os
os.environ.setdefault('GOLF_STUDIO', '124440050576723')
R_BALL = 0.08

LUA = r'''
local course=workspace.CourseSugarloaf
local rim=course.Hole16.StageAFVisuals.h16_sinkhole_rim
local root=rim:GetPivot()
local frame for _,p in rim:GetDescendants() do if p.Name:match('GeodeRim') then frame=p end end
local c=frame.Position
local F=CFrame.new(c)*frame.CFrame.Rotation
local balls=Instance.new('Folder') balls.Name='SC10CrystalBalls' balls.Parent=workspace
local rp=RaycastParams.new() rp.FilterType=Enum.RaycastFilterType.Exclude rp.FilterDescendantsInstances={rim,balls}
local feltY=workspace:Raycast(Vector3.new(c.X+1.6,c.Y+3,c.Z),Vector3.new(0,-6,0),rp).Position.Y
local up=Vector3.new(0,0.08+0.01,0)
local tests={}
local function at(x,z) local w=(F*CFrame.new(x,0,z)).Position return Vector3.new(w.X,feltY,w.Z)+up end
local function dirW(x,z) return F.Rotation*Vector3.new(x,0,z) end
local function ball(pos,vel,name,extra)
 local b=Instance.new('Part') b.Shape=Enum.PartType.Ball b.Size=Vector3.new(0.16,0.16,0.16) b.Name='SC10Ball_'..name
 b.CustomPhysicalProperties=PhysicalProperties.new(1,0.35,0.3) b.Anchored=false b.CanCollide=true b.CFrame=CFrame.new(pos)
 b.Parent=balls b.AssemblyLinearVelocity=vel
 local t={name=name,part=b,extra=extra,samples={}} table.insert(tests,t) return t
end
local hb=game:GetService('RunService').Heartbeat:Connect(function()
 for _,t in tests do if t.part.Parent then local p=t.part.Position
  if p.Y>feltY-1.0 and p.Y<feltY+0.085 then local l=root:PointToObjectSpace(p) table.insert(t.samples,{math.round(l.X*1e4)/1e4,math.round(l.Y*1e4)/1e4,math.round(l.Z*1e4)/1e4}) end
  if p.Y<feltY-0.3 then t.fell=true end end end end)
local function clear() for _,t in tests do if t.part.Parent then t.endPos=t.part.Position t.part.Parent=nil end end end
-- rest drops: 16 spots on the square of half-width d, 4 at a time (one per side)
for _,d in {0.80,0.85,0.90,0.925} do
 for _,s in {-0.75,-0.25,0.25,0.75} do
  ball(at(d,s*d),Vector3.zero,string.format('rest_%.3f_E_%.2f',d,s),{set='rest',d=d})
  ball(at(-d,-s*d),Vector3.zero,string.format('rest_%.3f_W_%.2f',d,s),{set='rest',d=d})
  ball(at(s*d,-d),Vector3.zero,string.format('rest_%.3f_N_%.2f',d,s),{set='rest',d=d})
  ball(at(-s*d,d),Vector3.zero,string.format('rest_%.3f_S_%.2f',d,s),{set='rest',d=d})
  task.wait(2.5) clear()
 end
end
-- corners
for _,d in {0.80,0.85,0.90,0.925} do
 for _,q in {{1,1},{-1,-1},{1,-1},{-1,1}} do ball(at(q[1]*d,q[2]*d),Vector3.zero,string.format('rest_%.3f_C_%d_%d',d,q[1],q[2]),{set='rest',d=d}) end
 task.wait(2.5) clear()
end
-- slow putts toward the opening (one direction per batch, laterals far apart)
for _,v in {0.4,0.7,1.0} do for _,ax in {{1,0},{-1,0},{0,1},{0,-1}} do
 for _,lat in {0,0.4,0.75,-0.4,-0.75} do
  local px,pz=ax[2]*lat,ax[1]*lat -- perpendicular offset
  ball(at(ax[1]*1.8+px,ax[2]*1.8+pz),-dirW(ax[1],ax[2])*v,string.format('putt_v%.1f_%d_%d_l%.2f',v,ax[1],ax[2],lat),{set='putt',v=v,lat=lat})
  task.wait(0.05)
 end
 task.wait(5) clear()
end end
task.wait(0.5)
hb:Disconnect()
local out={feltY=feltY,root={root:GetComponents()},results={}}
for _,t in tests do
 table.insert(out.results,{name=t.name,set=t.extra.set,d=t.extra.d,v=t.extra.v,lat=t.extra.lat,dropped=t.fell==true,samples=t.samples})
 t.part:Destroy() end
balls:Destroy()
_G.SC10Crys=game.HttpService:JSONEncode(out) return #_G.SC10Crys
'''


def tri_dist(p, a, b, c):
    # Ericson, closest point on triangle
    sub = lambda u, v: (u[0]-v[0], u[1]-v[1], u[2]-v[2]); dot = lambda u, v: u[0]*v[0]+u[1]*v[1]+u[2]*v[2]
    ab, ac, ap = sub(b, a), sub(c, a), sub(p, a)
    d1, d2 = dot(ab, ap), dot(ac, ap)
    if d1 <= 0 and d2 <= 0: q = a
    else:
        bp = sub(p, b); d3, d4 = dot(ab, bp), dot(ac, bp)
        cp = sub(p, c); d5, d6 = dot(ab, cp), dot(ac, cp)
        vc = d1*d4 - d3*d2; vb = d5*d2 - d1*d6; va = d3*d6 - d5*d4
        if d3 >= 0 and d4 <= d3: q = b
        elif vc <= 0 and d1 >= 0 and d3 <= 0: v = d1/(d1-d3); q = (a[0]+v*ab[0], a[1]+v*ab[1], a[2]+v*ab[2])
        elif d6 >= 0 and d5 <= d6: q = c
        elif vb <= 0 and d2 >= 0 and d6 <= 0: w = d2/(d2-d6); q = (a[0]+w*ac[0], a[1]+w*ac[1], a[2]+w*ac[2])
        elif va <= 0 and (d4-d3) >= 0 and (d5-d6) >= 0:
            w = (d4-d3)/((d4-d3)+(d5-d6)); q = (b[0]+w*(c[0]-b[0]), b[1]+w*(c[1]-b[1]), b[2]+w*(c[2]-b[2]))
        else:
            den = 1/(va+vb+vc); v = vb*den; w = vc*den
            q = (a[0]+ab[0]*v+ac[0]*w, a[1]+ab[1]*v+ac[1]*w, a[2]+ab[2]*v+ac[2]*w)
    return math.dist(p, q)


def crystals(rv):
    out = []
    for name, o in rv.items():
        if 'Crystal' not in name: continue
        V = o['verts']
        for comp in o['comps']:
            cs = set(comp); T = [t for t in o['tris'] if t[0] in cs]
            P = [V[i] for i in comp]; ctr = [sum(p[k] for p in P)/len(P) for k in range(3)]
            planes = []
            for t in T:
                a, b, c = V[t[0]], V[t[1]], V[t[2]]
                n = ((b[1]-a[1])*(c[2]-a[2])-(b[2]-a[2])*(c[1]-a[1]), (b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2]),
                     (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))
                k = n[0]*a[0]+n[1]*a[1]+n[2]*a[2]
                if n[0]*ctr[0]+n[1]*ctr[1]+n[2]*ctr[2] > k: n, k = (-n[0], -n[1], -n[2]), -k  # outward
                planes.append((n, k))
            out.append({'slot': name.split('__')[-1].split('.')[0], 'ctr': ctr, 'tris': [[V[i] for i in t] for t in T], 'planes': planes,
                        'lo': [min(p[k] for p in P) for k in range(3)], 'hi': [max(p[k] for p in P) for k in range(3)]})
    return out


def cdist(p, C):
    for k in range(3):
        if p[k] < C['lo'][k] - 0.5 or p[k] > C['hi'][k] + 0.5: return 9.0
    if all(n[0]*p[0]+n[1]*p[1]+n[2]*p[2] <= k + 1e-9 for n, k in C['planes']): return 0.0
    return min(tri_dist(p, *t) for t in C['tris'])


def score(run, rv):
    C = crystals(rv); res = []
    for r in run['results']:
        best = (9.0, None, None)
        for s in r['samples']:
            for k, c in enumerate(C):
                d = cdist(s, c)
                if d < best[0]: best = (d, k, s)
        res.append({'name': r['name'], 'set': r['set'], 'dropped': r['dropped'], 'samples': len(r['samples']),
                    'minDist': round(best[0], 4), 'crystal': best[1], 'slot': C[best[1]]['slot'] if best[1] is not None else None,
                    'at': [round(x, 3) for x in best[2]] if best[2] else None, 'hit': best[0] < R_BALL})
    drops = [x for x in res if x['dropped']]
    return {'crystals': len(C), 'balls': len(res), 'drops': len(drops), 'hits': sum(x['hit'] for x in res),
            'hitsBySet': {st: sum(x['hit'] for x in res if x['set'] == st) for st in ('rest', 'putt')},
            'dropsBySet': {st: '%d/%d' % (sum(x['dropped'] for x in res if x['set'] == st), sum(1 for x in res if x['set'] == st)) for st in ('rest', 'putt')},
            'minDist': min(x['minDist'] for x in res), 'rows': res}


if __name__ == '__main__':
    if sys.argv[1] == 'run':
        from run_playtests import Studio
        s = Studio(); s.start_play(); time.sleep(5)
        try:
            n = int(s.luau(LUA, 'Server', timeout=900))
            raw = ''.join(json.loads(s.luau('return game.HttpService:JSONEncode(_G.SC10Crys:sub(%d,%d))' % (i + 1, i + 40000), 'Server'))
                          for i in range(0, n, 40000))
        finally:
            s.stop_play()
        open(sys.argv[2], 'w').write(raw + '\n'); r = json.loads(raw)
        print('balls', len(r['results']), 'dropped', sum(x['dropped'] for x in r['results']))
    else:
        run = json.load(open(sys.argv[2])); rv = json.load(open(sys.argv[3]))
        out = score(run, rv); json.dump(out, open(sys.argv[2].replace('.json', '-score-' + sys.argv[3].split('_')[-1]), 'w'), indent=0)
        print({k: v for k, v in out.items() if k != 'rows'})
        for x in sorted(out['rows'], key=lambda x: x['minDist'])[:12]: print(' ', x)
