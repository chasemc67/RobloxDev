"""Prepare selective Blender scripts without importing or launching Blender."""
from pathlib import Path
S=Path(__file__).resolve().parent
src=(S/'props_batch3/build_batch3_prepolish.py').read_text()
guard="""
POLISH_IDS=set(json.loads((S/'polish_ids.json').read_text()))
if ONLY != POLISH_IDS:raise SystemExit('Polish build requires -- --only '+','.join(sorted(POLISH_IDS)))
BASELINE=json.loads((S.parent/'polish_fbx_baseline.json').read_text())
# Both batches may already have legitimate polish exports.
OTHER_BATCH='props_batch1' if S.name=='props_batch3' else 'props_batch3'
EXCLUDED_IDS=ONLY | set(json.loads((S.parent/OTHER_BATCH/'polish_ids.json').read_text()))
for relative,digest in BASELINE.items():
    path=D/relative
    if path.stem not in EXCLUDED_IDS:assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,relative
for id in ONLY:
    path=D/'models/fbx'/S.name/(id+'.fbx');backup=path.with_name(path.stem+'_prepolish.fbx')
    if path.exists() and not backup.exists():
        import shutil
        shutil.copy2(path,backup)
OLDPATH=D/'models'/(S.name+'_manifest_prepolish.json')
OLDPARTS={p['id']:p for p in json.loads(OLDPATH.read_text())['parts']}
"""
src=src.replace("H={h['number']",guard+"\nH={h['number']",1)
src=src.replace("D/'props_batch3_manifest.json'", "D/'models/props_batch3_manifest.json'")
src=src.replace("rep.append(r);ROOTS", "if p['id'] not in ONLY:r=OLDPARTS[p['id']]\n    else:r={**OLDPARTS[p['id']],**r}\n    rep.append(r);ROOTS")
src=src.replace("o=mesh(p['id']+'__'+k,g,k);o.parent=root;", "o=mesh(p['id']+'__'+k,g,k);o.parent=root;\n        if p['id'] in ONLY and (('snowpuffs' in p['id'] and k in ['Ink','Snow','Beak','AuroraTeal','AuroraViolet']) or 'coral' in p['id']):\n            for polygon in o.data.polygons:polygon.use_smooth=True\n        ")
src=src.replace('            errors=[]',"            errors=[]\n            roots=[o for o in fresh.objects if o.type=='EMPTY']\n            if len(roots)!=1 or roots[0].name.split('.')[0]!=r['id'] or roots[0].location.length>1e-5:errors.append('root hierarchy/pivot')\n            if roots and any(o.parent!=roots[0] for o in meshes):errors.append('mesh parent')")
src=src.replace("assert result['all_pass'], 'FBX re-import validation failed; see fbx_validation.json'", "for relative,digest in BASELINE.items():\n        if (D/relative).stem not in EXCLUDED_IDS:assert hashlib.sha256((D/relative).read_bytes()).hexdigest()==digest,relative\n    assert result['all_pass'], 'FBX re-import validation failed; see fbx_validation.json'")
# Current generator snapshots are mandatory for both selective scripts.
src=src.replace("SOURCE_HASH=", "assert hashlib.md5((D/'holes.json').read_bytes()).hexdigest()=='fb913741b5dd4812b6d2318e258bcc46'\nSOURCE_HASH=",1)

def wrap_build(src):
    doc,body=src.split('\n',1)
    return doc+'\nimport sys\n\ndef main():\n'+''.join('    '+line if line.strip() else line for line in body.splitlines(keepends=True))+"\nif __name__ == '__main__':\n    try:\n        main()\n    except Exception:\n        import traceback\n        traceback.print_exc()\n        sys.exit(1)\n"

(S/'props_batch3/build_batch3.py').write_text(wrap_build(src))
coral=src.replace('props_batch3','props_batch1').replace("D/'props_batch1_manifest.json'", "D/'models/props_batch1_manifest.json'")
coral=coral.replace("OTHER_BATCH='props_batch1' if S.name=='props_batch1' else 'props_batch1'", "OTHER_BATCH='props_batch1' if S.name=='props_batch3' else 'props_batch3'")
# The replacement above affects the guard's original batch3 branch; use one exact path.
a=coral.index('OLDPATH=');b=coral.index('OLDPARTS=',a)
coral=coral[:a]+"OLDPATH=D/'models/props_batch1_manifest_prepolish.json'\n"+coral[b:]
coral=coral.replace("override_boxes=p['override_boxes']","override_boxes=p.get('override_boxes',[])")
coral=coral.replace('for n in [4,6,14,18]:','for n in [1,2,3,5,7,8]:')
coral=coral.replace("for view in ['front','34','eye']:","for view in ['front','34']:")
coral=coral.replace('props_batch1.blend','props_batch1_polish.blend')
(S/'props_batch1/build_polish_corals.py').write_text(wrap_build(coral))
print('Selective build scripts ready; nothing launched.')
