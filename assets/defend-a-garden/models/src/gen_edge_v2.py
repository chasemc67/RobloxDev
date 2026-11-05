# Edge dressing pass 2 (box): v2 palette (hedges +10% lighter, ring just darker than play grass), v2 geometry subset, edge_layout_v2.json.
import json, numpy as np, os, sys
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__));M=os.path.dirname(HERE)
G=json.load(open(os.path.join(HERE,'edge_geom.json')));V1=json.load(open(os.path.join(M,'edge_layout.json')))
NAMES=['G1','G2','G3','Back1','Back2','Trunk','Hedge','HedgeLt','Wood','WoodLt','Rock','RockDk','Reed','Cattail','Water','Bed','Ring','Bush1','Bush2']
pal=Image.open(os.path.join(HERE,'edge_palette.png')).convert('RGB')
NEW={'Hedge':(68,165,68),'HedgeLt':(88,185,73),'Ring':(108,184,72)}  # play grass is (120,200,80)
for n,c in NEW.items():
    i=NAMES.index(n);x,y=i%8,i//8;assert pal.getpixel((x*32+16,y*32+16))!=c;pal.paste(c,(x*32,y*32,x*32+32,y*32+32))
pal.save(os.path.join(HERE,'edge_palette_v2.png'))
V2P=['hedge_tall','hedge_tall_cap','hedge_low','hedge_low_cap','ground_ring']
json.dump({k:G[k] for k in V2P},open(os.path.join(HERE,'edge_geom_v2.json'),'w'))
def path(p): return f'fbx_edge_v2/{p}/{p}.fbx' if p in V2P else f'fbx_edge/{p}/{p}.fbx'
rng=np.random.default_rng(2026);RY=-3.7;L=[]
def put(p,x,y,z,r=None,s=None,tag=''):
    r=rng.uniform(0,360) if r is None else r;s=rng.uniform(0.85,1.2) if s is None else s
    L.append(dict(piece=p,path=path(p),pos=[round(float(x),2),round(float(y),2),round(float(z),2)],rotY=round(float(r),1),scale=round(float(s),3),group=tag))
keep={'fence_section','fence_post','hedge_tall','hedge_tall_cap','hedge_low','hedge_low_cap','river_ext','ground_ring','rock_s','rock_m','rock_l','reeds_a','reeds_b'}
for i in V1['instances']:
    p=i['piece']
    if p not in keep: continue
    if p.startswith('hedge') or p.startswith('fence') or p in('river_ext','ground_ring'):
        r=i['rotY']+(180*int(rng.integers(2)) if p in('hedge_tall','hedge_low') else 0);put(p,*i['pos'],r,i['scale'],'structure')
    else: put(p,*i['pos'],None,None,'bank')
pts=[]
def free(x,z,d):
    return all((x-a)**2+(z-b)**2>=d*d for a,b in pts)
def river(x,z): return 84<x<110 and (z>74 or z<-71)
# North: two staggered, uneven tree rows on the slope behind the hedges
for row,(z0,step,pool) in enumerate(((-80,13,['tree_round_b','tree_round_c']),(-92,15,['tree_backdrop','tree_backdrop','tree_round_c']))):
    x=-125+row*7
    while x<128:
        xx=x+rng.uniform(-3,3);zz=z0+rng.uniform(-4,4)
        if not river(xx,zz): put(pool[int(rng.integers(len(pool)))],xx,RY,zz,tag='north_rows');pts.append((xx,zz))
        x+=step*rng.uniform(0.75,1.3)
# Slope fill: 0-38 studs outside the plateau edges (lawn x-94..90 / far bank to 160, z-73..77). Near the edge: bushes +
# small trees whose tops sit about at plateau height (y0); further out: bigger trees.
def band_sample(n,fn,mind):
    t=0;c=0
    while c<n and t<n*60:
        t+=1;x,z,dist=fn()
        if river(x,z) or not free(x,z,mind): continue
        if dist<5: p=['bush_a','bush_b'][int(rng.integers(2))];s=rng.uniform(1.0,1.2)
        elif dist<16: p=['tree_round_a','bush_a','bush_b','tree_round_a'][int(rng.integers(4))];s=rng.uniform(0.85,1.0)
        else: p=['tree_round_a','tree_round_b','tree_round_c'][int(rng.integers(3))];s=None
        put(p,x,RY,z,None,s,'slope');pts.append((x,z));c+=1
def west():  d=rng.uniform(1.5,38);return -94-d,rng.uniform(-110,112),d
def south(): d=rng.uniform(1.5,38);return rng.uniform(-130,195),77+d,d
def northfoot(): d=rng.uniform(1.5,6);return rng.uniform(-130,195),-73-d,d
def east():  d=rng.uniform(1.5,38);return 160+d,rng.uniform(-110,112),d
band_sample(45,west,7.5);band_sample(55,south,7.5);band_sample(30,northfoot,6);band_sample(40,east,7.5)
# Far bank trees (on the bank, y0), uneven
for z in np.arange(-66,72,15):
    x=116+rng.uniform(-4,30);zz=z+rng.uniform(-5,5)
    if free(x,zz,7): put(['tree_round_a','tree_round_b','tree_round_c','tree_backdrop'][int(rng.integers(4))],x,0,zz,tag='far_bank');pts.append((x,zz))
# A few bushes overlapping the front of the north hedges (lawn), clear of the patch fence (z-60) and barn
for x in rng.choice(np.arange(-80,82,9),7,replace=False): put(['bush_a','bush_b'][int(rng.integers(2))],x+rng.uniform(-2,2),0,-64.8+rng.uniform(-0.6,0.6),tag='hedge_overlap')
# Lawn-side scatter along west fence and south hedge inside the bounds margin? no: keep gameplay area clear.
GAP=dict(x=[-38,-22],z=72.5,path_x=-30,gate_z=50,note='hedge_low caps at x -38 and -22 (cap half-width 1.25 at scale 1) -> clear opening x -36.75..-23.25 (13.5 studs) on the line z 72.5; path is 12 wide (x -36..-24)')
cnt={}
for i in L: cnt[i['piece']]=cnt.get(i['piece'],0)+1
# gap check: nothing in the south hedge line opening
bad=[i for i in L if abs(i['pos'][2]-72.5)<4 and -37<i['pos'][0]<-23 and i['piece']!='hedge_low_cap']
assert not bad,bad
json.dump(dict(version=2,coordinate_frame=V1['coordinate_frame'],source=V1['source'],rim_ring_top_y=RY,rotY_units='degrees about +Y',
  seed=2026,scale_range=[0.85,1.2],south_gate_gap=GAP,counts=cnt,total=len(L),instances=L),open(os.path.join(M,'edge_layout_v2.json'),'w'),indent=1)
print(cnt,len(L))
