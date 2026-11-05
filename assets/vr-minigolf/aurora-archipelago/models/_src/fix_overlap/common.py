"""Source selection, immutable-input guard, and FBX cache provenance."""
import hashlib
import json
from pathlib import Path
import numpy as np
S=Path(__file__).resolve().parent
D=S.parents[2]
FIX=['h04_ice_channel_edge','h06_respawn_stone','h14_rail_bollards','h18_crystal_chute']
CHANGED=['h06_respawn_stone','h18_crystal_chute']
UNCHANGED=[x for x in FIX if x not in CHANGED]
NO_CHANGE='no change needed (true mesh clearance already >= threshold)'
SANITY=['h02_lintel_left','h02_lintel_mid','h02_lintel_right','h02_rookery_drift','h05_cliff_face_e','h05_cliff_face_w','h09_conch_entry','h10_bobsled_hut','h10_snow_walls_w','h11_fishing_hut','h11_floe_frame_e','h12_icebreaker','h14_bell_gantry','h15_lip_ice','h18_halo_arch']+[f'h{n:02d}_snowpuffs' for n in (4,6,14,18)]
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write_json(path,value): Path(path).write_text(json.dumps(value,indent=2)+'\n')
def protected():
    paths=list((D/'models/fbx').glob('props_batch*/**/*'))+list((D/'models').glob('*manifest*.json'))+list((D/'models').glob('fitcheck_*.txt'))
    return {str(p.relative_to(D)).replace('\\','/'):sha(p) for p in paths if p.is_file() and p.name not in ['props_fix_overlap_manifest.json','fitcheck_props_fix_overlap.txt']}
def guard(mode):
    p=S/'protected_sha256.json'
    if mode=='init':
        if p.exists(): guard('check')
        else: write_json(p,protected())
    elif json.loads(p.read_text())!=protected(): raise RuntimeError('Protected source files changed (including additions/removals)')
    if hashlib.md5((D/'holes.json').read_bytes()).hexdigest()!='fb913741b5dd4812b6d2318e258bcc46': raise RuntimeError('holes.json MD5 mismatch')
def records(stage='before'):
    rows=[]
    for batch in (1,2,3):
        for p in json.loads((D/f'models/props_batch{batch}_manifest.json').read_text())['parts']:
            if p['id'] in FIX+SANITY:
                q=dict(p);q['source_fbx']='models/'+p['fbx'];q['source_sha256']=sha(D/q['source_fbx']);rows.append(q)
    if {p['id'] for p in rows}!=set(FIX+SANITY) or len(rows)!=len(FIX+SANITY): raise RuntimeError('Missing/duplicate approved assets')
    return rows if stage=='before' else [p for p in rows if p['id'] in CHANGED]
def load_cache(p,stage):
    path=S/'cache'/stage/(p['id']+'.npy');meta=json.loads(path.with_suffix('.json').read_text())
    fbx=D/p['source_fbx'] if stage=='before' else D/f"models/fbx/props_fix_overlap/{p['id']}.fbx"
    if meta['fbx_sha256']!=sha(fbx) or meta['npy_sha256']!=sha(path) or meta['source_sha256']!=p['source_sha256']: raise RuntimeError('Stale FBX cache')
    return np.load(path,allow_pickle=False)
if __name__=='__main__':
    import sys
    guard(sys.argv[1])
