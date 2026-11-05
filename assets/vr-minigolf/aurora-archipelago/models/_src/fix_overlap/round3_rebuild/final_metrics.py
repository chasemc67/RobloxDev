import json,sys;sys.path.insert(0,'/workspace/aa3');from metrics import *
B=json.load(open('dump_before.json'));A=json.load(open('dump_after.json'));G=json.load(open('build_geom.json'))
res={}
for id in A:
    a=A[id]['objects'];src='r2' if f'r2_{id}' in B else 'appr'
    built={n:len(o['tris']) for n,o in G[id]['objects'].items()};imp={o['name']:len(o['tris']) for o in a}
    r=dict(before_approved=report(id,B[f'appr_{id}']['objects']),
           before_round2=report(id,B[f'r2_{id}']['objects']) if f'r2_{id}' in B else None,
           after=report(id,a))
    r['after']['silhouette_vs_approved']=silhouette(B[f'appr_{id}']['objects'],a)
    r['after']['ray_thickness_min']=local_thickness(a)
    r['after']['import_matches_build']=built==imp
    r['after']['roots']=A[id]['roots']
    res[id]=r;print(id,'match',built==imp,r['after'],flush=True)
json.dump(res,open('final_metrics.json','w'),indent=1)
