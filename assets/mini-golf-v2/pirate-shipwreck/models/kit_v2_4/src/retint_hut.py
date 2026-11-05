# kit_v2_3: palette-only change for kit_hut_leanto. No vertex/face changes, only per-vertex UVs are re-pointed at other palette cells.
# kit_v2_4: thatch keeps v2_2 UVs (3-tone); hut-only cells edited in kit_lib: Straw (200,165,90), StrawDk (166,134,74), StrawLt (222,190,130)
#   wood  : Wood1 (110,70,40) already at target (unchanged, shared cell untouched)
#   dark wood: WoodDk (86,54,32) is SHARED with crate_stack/rowboat_broken/lantern_post -> the hut gets its OWN new cell HutWoodDk (80,50,30)
import sys,os,json,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from kit_lib import *
src,dst=sys.argv[1:3]
g=json.load(open(src));spec=g['kit_hut_leanto']
def uvc(n): return list(uv_of(n))
remap={'WoodDk':'HutWoodDk'}
inv={tuple(np.round(uv_of(n),6)):n for n in PAL}
cnt={}
for o in spec['objects']:
    for i,uv in enumerate(o['uvs']):
        n=inv.get(tuple(np.round(uv,6)))
        assert n,uv
        if n in remap: o['uvs'][i]=list(uv_of(remap[n]));cnt[n]=cnt.get(n,0)+1
print('re-pointed vertices',cnt)
json.dump(g,open(dst,'w'))
palette_png(os.path.join(os.path.dirname(dst),'..','kit_palette.png'));json.dump(PAL,open(os.path.join(os.path.dirname(dst),'..','palette.json'),'w'))
