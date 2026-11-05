# Edge layout v3 = edge_layout_v2.json + two staggered, uneven tree rows behind the WEST fence (approved v1 kit pieces only).
# No-overlap rule: footprint radius = max(size X,Z)/2 * scale (same as v11 World.buildEdge); new pieces must clear every
# existing piece by the sum of radii + 0.5. West plateau edge x -94 (v11 World PLATEAU), fence x -91.5, ring top -3.7.
import json, numpy as np, os
HERE=os.path.dirname(os.path.abspath(__file__));M=os.path.dirname(HERE)
v2=json.load(open(os.path.join(M,'edge_layout_v2.json')));R=json.load(open(os.path.join(HERE,'edge_box_report.json')))
rad={k:max(v['size_xyz'][0],v['size_xyz'][2])/2 for k,v in R.items()}
spots=[(i['pos'][0],i['pos'][2],rad[i['piece']]*i['scale']) for i in v2['instances'] if i['piece'] not in('ground_ring','river_ext')]
rng=np.random.default_rng(2027);RY=v2['rim_top_y'] if 'rim_top_y' in v2 else v2['rim_ring_top_y'];new=[]
def free(x,z,r): return all((x-a)**2+(z-b)**2>=(r+c+0.5)**2 for a,b,c in spots)
for row,(x0,step,pool) in enumerate(((-114,13,['tree_round_b','tree_round_c','tree_round_b']),(-128,15,['tree_backdrop','tree_round_c','tree_backdrop']))):
    z=-112+row*7
    while z<114:
        p=pool[int(rng.integers(len(pool)))];s=float(rng.uniform(0.85,1.2));r=rad[p]*s;zz=z+rng.uniform(-3,3)
        for dx in(0,-3,-6,-9,-12,-15,-18):
            x=x0+rng.uniform(-4,4)+dx
            if free(x,zz,r):
                new.append(dict(piece=p,path=f'fbx_edge/{p}/{p}.fbx',pos=[round(x,2),RY,round(float(zz),2)],rotY=round(float(rng.uniform(0,360)),1),scale=round(s,3),group='west_rows'));spots.append((x,zz,r));break
        z+=step*rng.uniform(0.75,1.3)
# a few bushes in remaining gaps between the fence-foot and the rows (seam cover)
for _ in range(400):
    if sum(1 for n in new if n['group']=='west_seam')>=12: break
    p=['bush_a','bush_b'][int(rng.integers(2))];s=float(rng.uniform(0.85,1.2));r=rad[p]*s;x=-94-rng.uniform(2,12);z=rng.uniform(-108,110)
    if free(x,z,r): new.append(dict(piece=p,path=f'fbx_edge/{p}/{p}.fbx',pos=[round(x,2),RY,round(z,2)],rotY=round(float(rng.uniform(0,360)),1),scale=round(s,3),group='west_seam'));spots.append((x,z,r))
L=v2['instances']+new;cnt={}
for i in L: cnt[i['piece']]=cnt.get(i['piece'],0)+1
xs=[n['pos'][0] for n in new];zs=[n['pos'][2] for n in new]
out=dict(v2);out.update(version=3,seed_v3=2027,added_v3=dict(count=len(new),x_range=[min(xs),max(xs)],z_range=[min(zs),max(zs)],
  by_piece={p:sum(1 for n in new if n['piece']==p) for p in sorted({n['piece'] for n in new})},rule='clears every v2 piece by sum of footprint radii + 0.5'),counts=cnt,total=len(L),instances=L)
json.dump(out,open(os.path.join(M,'edge_layout_v3.json'),'w'),indent=1)
print(out['added_v3'],len(L))
