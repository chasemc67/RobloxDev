"""Preflight manifest now, validated exported handoff after user Blender run."""
import json,hashlib,math,sys
from pathlib import Path
S=Path(__file__).resolve().parent;D=S.parents[2];M=D/'models'
def read(p):return json.loads(p.read_text())
def main():
    assert hashlib.md5((D/'holes.json').read_bytes()).hexdigest()=='fb913741b5dd4812b6d2318e258bcc46'
    ps=read(S/'parts.json');F=read(S/'fitcheck_report.json');ids=set(read(S/'polish_ids.json'));digest=hashlib.sha256((S/'parts.json').read_bytes()).hexdigest()
    assert F['all_pass'] and F['parts_sha256']==digest
    actual=F['mode']=='Blender actual triangles'
    old=read(M/'props_batch1_manifest_prepolish.json');prev={p['id']:p for p in old['parts']};fits={p['id']:p for p in F['parts']}
    if actual:
        B=read(S/'build_report.json');V=read(S/'fbx_validation.json')
        assert B['generated_by']=='Blender bpy' and B['parts_sha256']==digest
        assert V['all_pass'] and V['parts_sha256']==digest and set(V['exported_ids'])==ids
        rows={p['id']:p for p in B['parts']}
    else:rows={}
    pal=read(S/'palette.json');shapes={r['id']:r for r in read(S/'polish_shapes.json')}
    for p in ps:
        id=p['id']
        if id not in ids:rows[id]=prev[id];continue
        if not actual:
            r=dict(prev[id]);v=[v for g in p['groups'].values() for v in g['verts']];lo=[min(q[i] for q in v) for i in range(3)];hi=[max(q[i] for q in v) for i in range(3)]
            r.update(tris=fits[id]['total_tris'],max_mesh_tris=max(fits[id]['tris'].values()),meshes=[dict(mesh=id+'__'+m,material=m,colour=pal[m][0],color=pal[m][0],roblox_material=pal[m][1],transparency=pal[m][3],tris=fits[id]['tris'][m]) for m in p['groups']],bbox_asset_local=[lo,hi],bbox=[lo,hi],bbox_hole_local=[[lo[i]+p['anchor'][i] for i in range(3)],[hi[i]+p['anchor'][i] for i in range(3)]],dimensions=[hi[i]-lo[i] for i in range(3)],notes=p['notes'],export_status='pending user Blender run')
            rows[id]=r
        r=rows[id]
        for k in ['pivot_hole_local','pivot_world','yaw_local','placement_yaw','motion']:assert r[k]==prev[id][k],(id,k)
        r.update(can_collide=False,can_query=False,can_touch=False,polish=shapes[id],fitcheck=fits[id])
        if actual:r['export_status']='validated Blender export'
    out={**old,'parts':[rows[p['id']] for p in ps],'validation_stage':F['mode'],'source_md5':'fb913741b5dd4812b6d2318e258bcc46','all_pass':True}
    (M/'props_batch1_manifest.json').write_text(json.dumps(out,indent=2))
    summary=(S/'summary_prepolish.md').read_text(encoding='utf-8')+'\n\n## Polish\n\n18 requested corals: original rev6 crowns and giant rev7 three stacked domes retained; exact bases and placements preserved. Thin leaning trunks fork twice into the retained lumps, with eight small rounded AuroraMint Neon gap cores. Small corals <=900 triangles; giant <3000, 4-stud cap retained. Collision/query/touch disabled.\n\nCurrent-source '+F['mode']+': ALL PASS. FBX re-import: '+('PASS' if actual else 'pending user Blender run')+'.\n\n'
    summary+='| ID | Old tris | New tris | Nearest rail | Nearest felt | Heavy per hole |\n|---|---:|---:|---|---|---:|\n'
    for id in sorted(ids):
        f=fits[id];shape=shapes[id];felt='source skin' if f['min_felt_clearance'] is None else f"{f['nearest_felt']} {f['min_felt_clearance']:.4f}"
        summary+=f"| {id} | {shape['old_tris']} | {f['total_tris']} | {f['nearest_rail']} {f['min_rail_clearance']:.4f} | {felt} | {F['heavy_counts'][str(f['hole'])]} |\n"
    exposure=[v for shape in shapes.values() for v in shape['core_proud_studs']]
    summary+='\nPre-existing out-of-scope budget note: h07_mogul_trim remains 3,200 triangles, unchanged; every requested polished asset is below 3,000.\n'
    summary+=f'\nGlow cores emerge {min(exposure):.3f}-{max(exposure):.3f} studs beyond retained crown surfaces; the original envelope limits a few narrow bumper cores. Most cores emerge 0.200 studs.\n'
    summary+='\nRun `python polish_corals.py`, `python fitcheck_batch1.py --preflight`, `python finalize_polish_corals.py`. After the selective user Blender build, run `python fitcheck_batch1.py` and `python finalize_polish_corals.py`. Build requires `-- --only '+','.join(sorted(ids))+'`.\n'
    (S/'summary.md').write_text(summary,encoding='utf-8')
    excluded_ids=ids | set(read(S.parent/'props_batch3/polish_ids.json'))
    for path,h in read(S.parent/'polish_fbx_baseline.json').items():
        if (D/path).stem not in excluded_ids:assert hashlib.sha256((D/path).read_bytes()).hexdigest()==h,path
    print('Polish coral finalize:',F['mode'],'ALL PASS; FBX '+('validated' if actual else 'pending'))
if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
