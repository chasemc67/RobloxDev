"""Read-only local Stage aj capture + offline OBB clearance evidence (no publish/save).
Run with --capture to fetch Studio. Default reanalyzes built-audit.json without Studio.
A mesh OBB envelope violation is a candidate, not proof that rendered mesh triangles intersect.
"""
import argparse
import collections
import csv
import json
import math
import re
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
OUT = GAME / 'playtests/stage-aj'


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def sub(a, b):
    return [x-y for x, y in zip(a, b)]


def cross(a, b):
    return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]


def radius(p, axis):
    return sum(abs(dot(v, axis))*s/2 for v, s in zip(p['axes'], p['size']))


def separation(a, b):
    """Max normalized SAT axis separation: positive gap, negative penetration."""
    delta = sub(a['center'], b['center'])
    axes = a['axes'] + b['axes'] + [cross(x, y) for x in a['axes'] for y in b['axes']]
    best = -math.inf
    for axis in axes:
        length = math.sqrt(dot(axis, axis))
        if length < 1e-8:
            continue
        n = [v/length for v in axis]
        best = max(best, abs(dot(delta, n))-radius(a, n)-radius(b, n))
    return best


def hole(p):
    m = re.search(r'\.Hole(\d+)\.', p['path'])
    return int(m[1]) if m else None


def capture():
    from run_playtests import Studio
    st = Studio()
    try:
        assert st.mode()[0] == 'Edit'
        size = int(st.luau(Path(__file__).with_suffix('.luau').read_text(), timeout=120))
        chunks = [st.luau(f'return string.sub(_G.StageAJAuditJSON,{i+1},{min(i+45000,size)})') for i in range(0, size, 45000)]
        st.luau('_G.StageAJAuditJSON=nil return true')
        OUT.joinpath('built-audit.json').write_text(''.join(chunks)+'\n')
    finally:
        st.m.p.terminate()


def top_faces(a,b):
    normal=b['axes'][1]
    ac=[v+n*a['size'][1]/2 for v,n in zip(a['center'],a['axes'][1])]
    bc=[v+n*b['size'][1]/2 for v,n in zip(b['center'],normal)]
    delta=sub(ac,bc)
    gap=dot(delta,normal)
    ndot=dot(a['axes'][1],normal)
    overlaps=True
    for axis in [a['axes'][0],a['axes'][2],b['axes'][0],b['axes'][2]]:
        ar=sum(abs(dot(a['axes'][i],axis))*a['size'][i]/2 for i in [0,2])
        br=sum(abs(dot(b['axes'][i],axis))*b['size'][i]/2 for i in [0,2])
        if abs(dot(delta,axis))>=ar+br-1e-5: overlaps=False
    return {'signed_plane_gap':gap,'normal_dot':ndot,'tangent_overlap':overlaps,
            'coplanar_overlap':ndot>.999999 and abs(gap)<.001 and overlaps}


def extra_trim_audit(parts):
    candidates=[p for p in parts if p['transparency']<.6 and not p['collide'] and not p['name'].startswith('RailCap_') and re.search(r'trim|lip',p['path'],re.I)]
    rails=[p for p in parts if '.Rails.' in p['path'] and p['transparency']<.6 and p['name'].startswith(('Rail_','Bumper_','RailCap_'))]
    rows=[]
    for p in candidates:
        for b in rails:
            if hole(p) and hole(p)!=hole(b): continue
            rel=top_faces(p,b)
            if rel['coplanar_overlap']:
                rows.append({'prop':p['path'],'rail':b['path'],'hole':hole(b),'kind':'remaining_visual_top_coplanar_candidate',**rel})
    baseline=[]
    for filename in ['coplanar-faces.csv','overlaps.csv']:
        with GAME.joinpath('logs/stages/aj-inputs',filename).open() as f:
            for row in csv.DictReader(f):
                paths=' '.join(row.get(k,'') for k in ['PartA','PartB','Prop','Target'])
                if re.search(r'trim|lip',paths,re.I) and 'RailCap_' not in paths:
                    baseline.append({'source':filename,**row,'classification':'physical_geometry_preserved' if '.Geometry.' in paths and '.Decor.' not in paths and '.Meshes.' not in paths else 'visual_envelope_candidate'})
    return {'built_candidates_examined':len(candidates),'remaining':rows,'baseline_named_trim_lip_rows':baseline}


def imports_against_manifest(data, parts):
    from fbx_bounds import mesh_bounds
    root=GAME.parents[1]/'assets/vr-mini-golf/sugarloaf-canyon/models'
    main=json.loads((root/'manifest.json').read_text())
    ground=next(p for p in main['pieces'] if p['id']=='h08_ground')
    tank=next(p for p in json.loads((root/'props_h09h14_manifest.json').read_text())['parts'] if p['id']=='h09_water_tank')
    checks=[]
    for stem, path, position, yaw in [('h08_ground',root/'fbx/h08_ground.fbx',ground['instances'][0]['pos'],ground['instances'][0]['yaw']),
                                     ('h09_water_tank',root/tank['fbx'],tank['pivot_world'],tank['yaw_deg'])]:
        # Stage's generated SugarloafLayout offset is [0,0,-5000]. Export it alongside the snapshot below.
        offset=data['layoutOffset']
        expected=[a+b for a,b in zip(position,offset)]
        models=[m for m in data['importModels'] if m['path'].endswith('.'+stem)]
        bounds=mesh_bounds(path)
        actual=[p for p in parts if '.'+stem+'.' in p['path']]
        missing=set(bounds)-{p['name'] for p in actual}
        errors=[]
        angle=math.radians(yaw)
        for p in actual:
            b=bounds.get(p['name'])
            if not b: errors.append({'name':p['name'],'unknown':True}); continue
            x,y,z=b['center']
            center=[expected[0]+math.cos(angle)*x+math.sin(angle)*z,expected[1]+y,expected[2]-math.sin(angle)*x+math.cos(angle)*z]
            distance=math.sqrt(dot(sub(p['center'],center),sub(p['center'],center)))
            size_error=max(abs(a-b) for a,b in zip(p['size'],b['size']))
            if distance>.001 or size_error>.001: errors.append({'name':p['name'],'center_error':distance,'size_error':size_error})
        pivot_errors=[math.sqrt(dot(sub(m['pivot'][:3],expected),sub(m['pivot'][:3],expected))) for m in models]
        checks.append({'id':stem,'models':len(models),'mesh_count':len(actual),'expected_mesh_count':len(bounds),'missing':sorted(missing),
                       'pivot_errors':pivot_errors,'mesh_errors':errors,'pass':len(models)==1 and len(actual)==len(bounds) and not missing and not errors and all(e<.001 for e in pivot_errors)})
    return checks


def analyze():
    data = json.loads(OUT.joinpath('built-audit.json').read_text())
    parts = data['parts']
    parts = list(parts.values()) if isinstance(parts, dict) else parts
    visual = [p for p in parts if p['transparency'] < .6 and not p['collide'] and (p['class']=='MeshPart' or '.Decor.' in p['path'] or '.Kit.' in p['path'])]
    targets = []
    for p in parts:
        if '.Movers.' in p['path']:
            continue
        if p.get('wall') and p['collide']:
            targets.append((p, 'rail'))
        if p.get('surface') and p['collide']:
            targets.append((p, 'felt'))
            q = dict(p)
            q['size'] = [p['size'][0], .16, p['size'][2]]
            q['center'] = [v + n*(p['size'][1]/2+.08) for v,n in zip(p['center'],p['axes'][1])]
            targets.append((q, 'ball_headroom'))
            # Match deco_clearance's horizontal footprint at the highest felt height,
            # with vertical headroom from felt-0.4 to felt+8.
            x=[p['axes'][0][0],0,p['axes'][0][2]]
            length=math.sqrt(dot(x,x))
            x=[v/length for v in x]
            z=[-x[2],0,x[0]]
            q=dict(p)
            q['axes']=[x,[0,1,0],z]
            q['size']=[2*radius(p,x),8.4,2*radius(p,z)]
            q['center']=[p['center'][0],p['center'][1]+radius(p,[0,1,0])+3.8,p['center'][2]]
            targets.append((q,'player_headroom_8'))
    envelopes = re.compile(r'ground|parapet|skirt|plinth|respawn|teleport|pad_|gap_floor|rail|felt_arrow|hour_stone', re.I)
    rows=[]
    for a in visual:
        ar=math.sqrt(dot(a['size'], a['size']))/2
        for b, kind in targets:
            ah,bh=hole(a),hole(b)
            if ah and ah != bh:
                continue
            delta=sub(a['center'],b['center'])
            if dot(delta,delta) > (ar+math.sqrt(dot(b['size'],b['size']))/2+.15)**2:
                continue
            sep=separation(a,b)
            if sep >= .15-1e-5:
                continue
            intended=bool(envelopes.search(a['path']))
            rows.append({'hole':bh,'prop':a['path'],'target':b['path'],'target_id':b.get('wall') or b.get('piece'),
                         'kind':kind,'separation':round(sep,6),'required_gap':.15,
                         'classification':'intended_dressing_envelope_candidate' if intended else 'clearance_candidate',
                         'mesh_bounds_only':a['class']=='MeshPart'})
    caps=[]
    for a in parts:
        if not a['name'].startswith('RailCap_'):
            continue
        bodies=[b for b in parts if hole(a)==hole(b) and b.get('wall')==a.get('wall') and b['name'].startswith(('Rail_', 'Bumper_'))]
        for b in bodies:
            relation=top_faces(a,b)
            gap=relation['signed_plane_gap']
            caps.append({'hole':hole(a),'cap':a['path'],'rail':b['path'],'wall':a.get('wall'),'raised':a.get('raised',False),
                         'top_plane_gap_after':round(gap,7),'top_plane_gap_before_reconstructed':round(gap-(.02*b['axes'][1][1] if a.get('raised') else 0),7),
                         'coplanar_after':relation['coplanar_overlap'],'normal_dot':relation['normal_dot'],'tangent_overlap':relation['tangent_overlap'],'collider_changed':False})
    before=collections.defaultdict(set)
    with GAME.joinpath('logs/stages/aj-inputs/coplanar-faces.csv').open() as f:
        for r in csv.DictReader(f):
            if float(r['NormalY'])>.99:
                for key in ['PartA','PartB']:
                    if 'RailCap_' in r[key]: before[int(r['Hole'])].add(r[key])
    perhole={str(n):{'baseline_unique_caps':len(before[n]),'built_caps':sum(r['hole']==n for r in caps),
                    'raised':sum(r['hole']==n and r['raised'] for r in caps),
                    'coplanar_after':sum(r['hole']==n and r['coplanar_after'] for r in caps)} for n in range(1,19)}
    camera=[p for p in parts if 'tradingpost' in re.sub(r'[^a-z0-9]','',p['path'].lower())]
    proxies=[p for p in parts if p.get('proxy')]
    authored=json.loads(OUT.joinpath('deco_clearance.json').read_text())
    checks={'camera_parts':len(camera),'camera_flags_pass':all(not p['collide'] and not p['query'] and not p['touch'] and p.get('skipQuery') for p in camera),
            'primitive_proxies':len(proxies),'proxy_pass':len(proxies)==7 and all(p['class']=='Part' and p['collide'] and p['group']=='GolfWall' and p['transparency']==1 for p in proxies),
            'placeholder_pass':not data['placeholders'],
            'import_visual_flags':[{'path':p['path'],'pass':not(p['collide'] or p['query'] or p['touch'])} for p in parts if 'h08_ground' in p['path'] or 'h09_water_tank' in p['path']]}
    extra=extra_trim_audit(parts)
    OUT.joinpath('trim-lip-audit.json').write_text(json.dumps(extra,indent=2)+'\n')
    summary={'remaining_trim_lip_top_candidates':len(extra['remaining']),'method':'Actual oriented part bounds, 15-axis SAT; .15 gap, .16 ball headroom and horizontal footprint player headroom felt-0.4 through felt+8. Mesh envelope candidates require visual/triangle refinement; intended labels are name-based, not waivers.',
             'built_visual_parts':len(visual),'targets':len(targets),'clearance_candidates':len(rows),
             'by_target_kind':dict(collections.Counter(r['kind'] for r in rows)),
             'by_classification':dict(collections.Counter(r['classification'] for r in rows)),
             'by_hole':dict(collections.Counter(r['hole'] for r in rows)),
             'authored_deco_rows':len(authored),'authored_by_hole':dict(collections.Counter(r['hole'] for r in authored)),
             'comparison_note':'Authored rows use anchor envelopes; built rows use individual actual MeshPart bounds, so counts are not equivalent. Full rows retained for review.',
             'import_transform_checks':imports_against_manifest(data,parts),'railcaps':perhole,'checks':checks,'import_models':data['importModels'],'geometry_equality':data.get('geometryEquality')}
    for name,obj in [('built-clearance',rows),('railcap-fixed-list',caps),('built-audit-summary',summary),('obstacle-proxies',proxies),('trading-post-flags',camera)]:
        OUT.joinpath(name+'.json').write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--capture',action='store_true')
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    if args.capture: capture()
    analyze()
