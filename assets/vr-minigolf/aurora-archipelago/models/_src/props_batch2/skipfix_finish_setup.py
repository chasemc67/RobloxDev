import json
from pathlib import Path
S=Path(__file__).resolve().parent;M=S.parents[1];D=S.parents[2]
old=json.loads((S/'_backup_pre_skipfix/props_batch2_manifest.json').read_text());falls=next(p for p in old['parts'] if p['id']=='h15_great_frozen_falls')
mf=M/'props_batch2_manifest.json';m=json.loads(mf.read_text());m['parts'].append(falls);m['skipped']=[p for p in m['skipped'] if p['id']!=falls['id']];mf.write_text(json.dumps(m,indent=2));(S/'skipped.json').write_text(json.dumps(m['skipped'],indent=2))
p=json.loads((S/'h15_part.json').read_text());p['anchor']=falls['pivot_hole_local'];parts=json.loads((S/'parts.json').read_text());parts.append(p)
guard=next(p for p in parts if p['id']=='h15_ice_parapet');guard['groups']['IceGuard']=guard['groups'].pop('Ice');(S/'parts.json').write_text(json.dumps(parts))
pal=json.loads((S/'palette.json').read_text());pal['IceGuard']=list(pal['Ice']);pal['IceGuard'][3]=.9;(S/'palette.json').write_text(json.dumps(pal,indent=2))
build=(S/'build_skipfix.py').read_text().replace("CHANGED=set(json.loads((S/'skipfix_ids.json').read_text()))","CHANGED={'h15_ice_parapet'}")
build=build.replace("if k=='Ice':", "if k in ['Ice','IceGuard']:")
build=build.replace("    return m\n", "    if k=='IceGuard':b.inputs['Transmission Weight'].default_value=.98;b.inputs['Roughness'].default_value=.08\n    return m\n")
build=build.replace('for n in [9,10,11,12,15,16,17]:\n    visible=', 'for n in [15]:\n    visible=')
(S/'build_skipfix_guard.py').write_text(build)
