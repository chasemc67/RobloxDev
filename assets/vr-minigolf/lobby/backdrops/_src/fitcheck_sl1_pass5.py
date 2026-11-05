"""Plain-Python SL1 pass-5 fitcheck. Usage: python script.py [workspace]."""
import sys,json,math,hashlib
from pathlib import Path
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1])
def main():
    old=json.loads((ROOT/'manifest.json').read_text())['zones']['SL1']
    new=json.loads((ROOT/'manifest_sl1_pass5.json').read_text())
    pass4=json.loads((ROOT/'manifest_sl1_pass4.json').read_text())
    checks=[]
    def check(name,ok,detail=''):
        checks.append(bool(ok));lines.append(('PASS ' if ok else 'FAIL ')+name+' '+detail)
    lines=[]
    check('triangle budget',new['tris']==sum(m['tris'] for m in new['meshes']) and new['tris']<=15000,str(new['tris'])+' / 15000')
    for m in new['meshes']:lines.append('MESH '+m['name']+' '+str(m['tris'])+' tris')
    for key in ('placement_cframe','position','offset_from_arch','arch_position','yaw_deg','baked_scale','primary_part','front','motion','cable_local_unscaled','cabin_centre_local_unscaled','neon_parts'):
        check('unchanged '+key,new[key]==old[key])
    check('mesh names',set(m['name'] for m in new['meshes'])==set(m['name'] for m in old['meshes']))
    for m in old['meshes']:
        if m['name']!='SL1_mesas':check('fixed mesh '+m['name'],m==next(v for v in new['meshes'] if v['name']==m['name']))
    heights=new['pylon_top_heights_unscaled']
    check('pylon footprints',len(heights)==2 and all(abs(h['after']-v)<=0.05 and abs(h['before']-v)<=0.05 and all(abs(y-v)<=0.05 for y in h['footprint_samples']) for h,v in zip(heights,(47.4,55.4))),str(heights))
    for i,axis in enumerate('XYZ'):
        margin=old['bbox']['size'][i]*0.1
        check('bbox '+axis,new['bbox']['min'][i]>=old['bbox']['min'][i]-margin and new['bbox']['max'][i]<=old['bbox']['max'][i]+margin,
              str((new['bbox']['min'][i],new['bbox']['max'][i]))+' allowed '+str((old['bbox']['min'][i]-margin,old['bbox']['max'][i]+margin)))
    check('pass number',new['pass']==5)
    check('no SL1_spires mesh',all(m['name']!='SL1_spires' for m in new['meshes']))
    check('no spire fields',all('spire' not in key.lower() for key in new))
    check('mesa tris equal pass 4',next(m['tris'] for m in new['meshes'] if m['name']=='SL1_mesas')==next(m['tris'] for m in pass4['meshes'] if m['name']=='SL1_mesas'))
    check('far scenery flags',all(new['decoration'][k] is False for k in ('CanCollide','CanQuery','CanTouch')))
    re=json.loads((ROOT/'_src/reimport_sl1_pass5.json').read_text());check('FBX reimport',re['all_pass'])
    check('no reimported SL1_spires mesh',all(m['name']!='SL1_spires' for m in re['meshes']))
    expected={'fbx/bd_au2_aurora_archipelago.fbx': 'ee29faf9f49ba44d24394cf7e1f4d41b393815892559d8a96d41a2697edc75c3', 'fbx/bd_lg2_lantern_grove.fbx': 'b53d1abdfb0345b298db995d198de09f217632fb7be58a2bdc5b234af0b764b5', 'fbx/bd_sl1_sugarloaf_canyon.fbx': '98191fe690cf5bb0f1e4b917f51aa144131cd467d2d50e249952e5c0fd1d49f3', 'fbx_pass4/bd_sl1_sugarloaf_canyon_pass4.fbx': '87413ccc766b4cf695f2cf2814db286ed2ed5defc76a8f237be20021324fed65', 'manifest.json': 'ffd6b2c43e8b0c77deb6bba263ebdeae8c59426cc287a0cc5e9c777941c2054f', 'manifest_sl1_pass4.json': '8622a820be5c701427070b0c2e4e62d2112b981ccbfc3127aae3e263bc41f50b', 'previews/all_zones_from_spawn.png': 'd5a78a3dee238741ac6af43e59808675ff775f12723a538c6e13e0f5102e5da5', 'previews/AU2_boardwalk_eye.png': 'baaf3c698e0933c668bdebafd1b5690aa27dadacb12d2ba850f9d747edc738a1', 'previews/concept_vs_build.jpg': '330d5f6da6e329e3beaa1a89711bf1ebe01c6cde035f9069708332dfc2438a7a', 'previews/LG2_boardwalk_eye.png': 'd173c7193fd9a0eadd07793c3ad90a59a63debd49049e342c9dd54d149f050b2', 'previews/SL1_boardwalk_eye.png': '385b46d604af157e912dbcc898e12fe452fa8c4844bec56d20eba15339cf9261', 'previews/SL1_concept_vs_build.jpg': '8ed396ca733f035eaa87af13cabe785aad03ab95a4565d6cbc05bb92ef2d86f7', 'previews_pass4/sheet_sl1_pass4_before_after.png': '949f4d21694946b5d05455e36ab883656b15ba0e192a36b6f99813774a98fe56', 'previews_pass4/SL1_34.png': 'bc77c95ae65ea2f3a0c85dfc283f7c177673ec0f208c9a8ba7b8ceada52af48e', 'previews_pass4/SL1_after_34_silhouette.png': 'b980222ece86d51f0cef7a5ecd06f22835c8b65033a5d7eb1866ebb5ea13c1d1', 'previews_pass4/SL1_after_boardwalk_eye_silhouette.png': 'cd15e5ce9f7a2c4aef5f01e1547a318a36cf573593ab19c58081168c2f762dca', 'previews_pass4/SL1_before_34.png': '6a11619b27bfade87cdee88b2b0e5752e23f8f950c0d4f2959c7772ef6c3e035', 'previews_pass4/SL1_before_34_silhouette.png': '15353c60b0dde5b566b6fb32d097d650148bb836814bec4d55969146755a5ff0', 'previews_pass4/SL1_before_boardwalk_eye.png': '1969400638ef74533359f7e189ab85259f3312382def6606b7fc1db7a0dff549', 'previews_pass4/SL1_before_boardwalk_eye_silhouette.png': 'f40af3bab10af0b062a682357f733e610107c3ca068417efa20689498e632c62', 'previews_pass4/SL1_boardwalk_eye.png': 'd97aa452a50bbc4094393fe567cffdf8d7acdfe4fc52469cc62083d0e96d7b01'}
    paths=[ROOT/'manifest.json',ROOT/'manifest_sl1_pass4.json']
    for directory in ('fbx','fbx_pass4','previews','previews_pass4'):
        paths.extend(p for p in (ROOT/directory).rglob('*') if p.is_file())
    actual={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    check('approved SHA256 guard',actual==expected)
    lines.append('all_pass='+str(all(checks)))
    (ROOT/'fitcheck_sl1_pass5.txt').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
    return 0 if all(checks) else 1
if __name__=='__main__':
    try:sys.exit(main())
    except Exception:
        import traceback
        error=traceback.format_exc();(ROOT/'fitcheck_sl1_pass5.txt').write_text('FAIL exception\n'+error);print(error);sys.exit(1)
