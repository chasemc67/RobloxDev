"""Plain-Python SL1 pass-4 fitcheck. Usage: python script.py [workspace]."""
import sys,json,math,hashlib
from pathlib import Path
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1])
def main():
    old=json.loads((ROOT/'manifest.json').read_text())['zones']['SL1']
    new=json.loads((ROOT/'manifest_sl1_pass4.json').read_text())
    checks=[]
    def check(name,ok,detail=''):
        checks.append(bool(ok));lines.append(('PASS ' if ok else 'FAIL ')+name+' '+detail)
    lines=[]
    check('triangle budget',new['tris']==sum(m['tris'] for m in new['meshes']) and new['tris']<=15000,str(new['tris'])+' / 15000')
    for m in new['meshes']:lines.append('MESH '+m['name']+' '+str(m['tris'])+' tris')
    for key in ('placement_cframe','position','offset_from_arch','arch_position','yaw_deg','baked_scale','primary_part','front','motion','cable_local_unscaled','cabin_centre_local_unscaled','neon_parts'):
        check('unchanged '+key,new[key]==old[key])
    check('mesh names',set(m['name'] for m in new['meshes'])==set(m['name'] for m in old['meshes'])|{'SL1_spires'})
    for m in old['meshes']:
        if m['name']!='SL1_mesas':check('fixed mesh '+m['name'],m==next(v for v in new['meshes'] if v['name']==m['name']))
    heights=new['pylon_top_heights_unscaled']
    check('pylon footprints',len(heights)==2 and all(abs(h['after']-v)<=0.05 and abs(h['before']-v)<=0.05 and all(abs(y-v)<=0.05 for y in h['footprint_samples']) for h,v in zip(heights,(47.4,55.4))),str(heights))
    for i,axis in enumerate('XYZ'):
        margin=old['bbox']['size'][i]*0.1
        check('bbox '+axis,new['bbox']['min'][i]>=old['bbox']['min'][i]-margin and new['bbox']['max'][i]<=old['bbox']['max'][i]+margin,
              str((new['bbox']['min'][i],new['bbox']['max'][i]))+' allowed '+str((old['bbox']['min'][i]-margin,old['bbox']['max'][i]+margin)))
    a=[v*3 for v in old['cable_local_unscaled']['a']];b=[v*3 for v in old['cable_local_unscaled']['b']]
    d=[y-x for x,y in zip(a,b)];dd=sum(v*v for v in d)
    def distance(p):
        t=max(0,min(1,sum((p[i]-a[i])*d[i] for i in range(3))/dd))
        return math.sqrt(sum((p[i]-a[i]-t*d[i])**2 for i in range(3)))
    # AABB distance is a conservative lower bound over all faces, not only vertices.
    verts=new['spires_vertices_local_scaled']
    lo=[min(v[i] for v in verts) for i in range(3)];hi=[max(v[i] for v in verts) for i in range(3)]
    # Cable endpoint AABB contains the whole segment; separation proves corridor clearance.
    gap=[max(0,lo[i]-max(a[i],b[i]),min(a[i],b[i])-hi[i]) for i in range(3)]
    lower=math.sqrt(sum(v*v for v in gap));nearest=min(map(distance,verts))
    check('spires outside cable corridor',lower>=6,'conservative face clearance >= %.3f scaled studs; closest vertex %.3f'%(lower,nearest))
    specs=new['spires_local_unscaled'];check('spire count and dimensions',4<=len(specs)<=6 and all(3<=v['radius']<=7 and 25<=v['height']<=60 for v in specs))
    check('far scenery flags',all(new['decoration'][k] is False for k in ('CanCollide','CanQuery','CanTouch')))
    re=json.loads((ROOT/'_src/reimport_sl1_pass4.json').read_text());check('FBX reimport',re['all_pass'])
    expected=json.loads((ROOT/'_src/sl1_pass4_approved_sha256.json').read_text())
    paths=list(ROOT.glob('fbx/*.fbx'))+[ROOT/'manifest.json',ROOT/'_src/build_backdrops.py']+[p for p in ROOT.glob('previews/*') if p.is_file()]
    actual={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    check('approved SHA256 guard',actual==expected)
    lines.append('all_pass='+str(all(checks)))
    (ROOT/'fitcheck_sl1_pass4.txt').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
    return 0 if all(checks) else 1
if __name__=='__main__':
    try:sys.exit(main())
    except Exception:
        import traceback
        error=traceback.format_exc();(ROOT/'fitcheck_sl1_pass4.txt').write_text('FAIL exception\n'+error);print(error);sys.exit(1)
