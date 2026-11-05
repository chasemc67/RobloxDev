"""Plain Python scope, budget, source and export-integrity audit."""
import json,hashlib,ast,sys
from pathlib import Path
import numpy as np
from polish_geometry import components,count
S=Path(__file__).resolve().parent;D=S.parents[1]
def read(p):return json.loads(p.read_text())
def bounds(p):
    v=np.array([v for g in p['groups'].values() for v in g['verts']]);return v.min(axis=0),v.max(axis=0)
def main():
    assert hashlib.md5((D/'holes.json').read_bytes()).hexdigest()=='fb913741b5dd4812b6d2318e258bcc46'
    rows=[];existing_budget_notes=[]
    for batch in ['props_batch1','props_batch3']:
        b=S/batch;old={p['id']:p for p in read(b/'parts_prepolish.json')};ps=read(b/'parts.json');ids=set(read(b/'polish_ids.json'));F=read(b/'fitcheck_report.json')
        assert F['all_pass'] and F['parts_sha256']==hashlib.sha256((b/'parts.json').read_bytes()).hexdigest()
        changed={p['id'] for p in ps if p!=old[p['id']]};assert changed==ids,(batch,changed^ids)
        records={p['id']:p for p in read(D/'models'/(batch+'_manifest.json'))['parts']};prior={p['id']:p for p in read(D/'models'/(batch+'_manifest_prepolish.json'))['parts']}
        for p in ps:
            id=p['id'];original=old[id]
            if id not in ids:
                assert records[id]==prior[id],id
                if count(p['groups'])>=3000:existing_budget_notes.append(dict(id=id,tris=count(p['groups']),note='Pre-existing, outside requested change scope; preserved exactly.'))
                continue
            for k in ['anchor','yaw_local','motion','skin_ids','felt_skins']:assert p[k]==original[k],(id,k)
            assert all(p[k] is False for k in ['can_collide','can_query','can_touch'])
            assert not any(m in ['MoveCream','MoveRed','PepRed','Cherry','CreamTaffy','FlagRed','Cream'] for m in p['groups'])
            n=count(p['groups']);assert n<3000,id
            if 'coral' in id:
                if 'giant' not in id:assert n<=900,id
                col=next(iter(original['groups']));old_domes=[g for g in components(original['groups'][col]) if len(g['verts']) in [48,70]]
                new_domes=[g for g in components(p['groups'][col]) if len(g['verts']) in [48,70]]
                assert old_domes==new_domes,(id,'crown changed')
                if p['skin_ids']:
                    # The retained exact skin box is copied as a component.
                    skin=dict(verts=original['groups'][col]['verts'][:8],faces=original['groups'][col]['faces'][:6])
                    assert skin in list(components(p['groups'][col])),(id,'skin changed')
                lo,hi=bounds(p);oldlo,oldhi=bounds(original)
                assert np.all(lo>=oldlo-1e-8) and np.all(hi<=oldhi+1e-8),(id,'original envelope exceeded',lo,hi,oldlo,oldhi)
                assert len(list(components(p['groups']['AuroraMint'])))==8
                if 'giant' in id:assert abs(hi[0]-lo[0]-4)<1e-8 and abs(hi[2]-lo[2]-4)<1e-8
            elif 'snowpuffs' in id:assert n<count(original['groups'])*1.2
            elif id!='h06_frosted_palms':assert n<=900
            rows.append(dict(id=id,old_tris=count(original['groups']),new_tris=n))
    excluded_ids=set().union(*(read(S/b/'polish_ids.json') for b in ['props_batch1','props_batch3']))
    digests={path:h for path,h in read(S/'polish_fbx_baseline.json').items() if (D/path).stem not in excluded_ids}
    for path,h in digests.items():assert hashlib.sha256((D/path).read_bytes()).hexdigest()==h,path
    missing=[str(S/'_prepolish_previews'/b/(id+'_34.png')) for b in ['props_batch1','props_batch3'] for id in read(S/b/'polish_ids.json') if not (S/'_prepolish_previews'/b/(id+'_34.png')).exists()]
    assert not missing,missing
    scripts=['polish_geometry.py','prepare_polish.py','configure_polish.py','configure_polish_builds.py','make_polish_sheet.py','finish_polish.py','verify_polish.py','props_batch1/polish_corals.py','props_batch1/build_polish_corals.py','props_batch1/finalize_polish_corals.py','props_batch1/fitcheck_batch1.py','props_batch3/gen_batch3.py','props_batch3/build_batch3.py','props_batch3/polish_shapes.py','props_batch3/fitcheck_batch3.py','props_batch3/finalize_batch3.py','props_batch3/measure_arch_rev2.py']
    for p in scripts:ast.parse((S/p).read_text())
    report=dict(all_pass=True,changed_count=len(rows),unchanged_fbx_count=len(digests),before_previews=28,syntax_checked_scripts=len(scripts),parts=rows,preexisting_out_of_scope_budget_notes=existing_budget_notes,ice_bank_width_exception='0.40 studs to retain original envelope and 0.15 rail buffer',blender_launched=False,export_stage='pending user Blender builds')
    (S/'polish_audit.json').write_text(json.dumps(report,indent=2));print('POLISH AUDIT ALL PASS:',len(rows),'changed assets;',len(digests),'original FBXs byte-identical; 28 BEFORE previews present.')
if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
