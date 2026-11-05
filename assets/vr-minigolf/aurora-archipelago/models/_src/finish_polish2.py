"""Plain Python finish: all ten polish fitchecks and lantern/snowpuff review sheet."""
import json,sys,subprocess,hashlib,traceback
from pathlib import Path
from polish_guard import start_guard
VERIFY=start_guard()
S=Path(__file__).resolve().parent;M=S.parent

def read(path):return json.loads(path.read_text())

def main():
    subprocess.run([sys.executable,str(S/'props_batch3/fitcheck_batch3.py'),'--polish2'],cwd=S,check=True)
    B=read(S/'props_batch3/polish2_build_report.json')
    V=read(S/'props_batch3/polish2_fbx_validation.json')
    F=read(S/'props_batch3/polish2_fitcheck_report.json')
    ids=set(read(S/'props_batch3/polish_ids.json'))
    if len(ids)!=10 or set(V['exported_ids'])!=ids or not V['all_pass'] or not F['all_pass']:raise RuntimeError('All ten polish validations required')
    if B['parts_sha256']!=V['parts_sha256'] or B['parts_sha256']!=F['parts_sha256']:raise RuntimeError('Polish provenance mismatch')
    records={p['id']:p for p in B['parts']};fits={p['id']:p for p in F['parts']}
    if set(records)!=ids or set(fits)!=ids:raise RuntimeError('Incomplete polish records')
    manifest_path=M/'props_batch3_polish_manifest.json';manifest=read(manifest_path)
    for asset in ids:
        record=records[asset];fbx=M/record['fbx']
        if fbx.parent!=M/'fbx/props_batch3_polish' or hashlib.sha256(fbx.read_bytes()).hexdigest()!=B['fbx_sha256'][asset]:raise RuntimeError('FBX mismatch: '+asset)
        matches=[p for p in manifest['parts'] if p['id']==asset]
        if len(matches)!=1:raise RuntimeError('Expected one manifest record: '+asset)
        matches[0].update(record,fitcheck=fits[asset],export_status='validated Blender export')
    manifest.update(all_pass=True,hole_tris=F['hole_tris'],heavy_counts=F['heavy_counts'])
    from PIL import Image,ImageOps,ImageDraw,ImageFont
    pv=M/'previews/props_batch3_polish';lantern='h18_ramp_lanterns'
    rows=[('Lantern: BEFORE / AFTER / DUSK',[M/'previews/props_batch3'/(lantern+'_34.png'),pv/(lantern+'_34.png'),pv/(lantern+'_dusk.png')])]
    for n in (4,6,14,18):
        asset=f'h{n:02d}_snowpuffs'
        for label,suffix in [('BEFORE','_v1'),('AFTER','')]:
            rows.append((asset+' '+label+' : 3/4 / SIDE / TOP',[pv/(asset+'_closeup_'+angle+suffix+'.png') for angle in ('34','side','top')]))
    started=__import__('datetime').datetime.fromisoformat(B['started_utc']).timestamp()
    refreshed=set(B.get('refreshed_preview_ids',ids))
    # Approved BEFORE images and earlier snowpuff previews are not this run's outputs.
    after_paths={pv/(asset+'_'+view+'.png') for asset in refreshed
                 for view in ('34','front','eye','dusk') if asset==lantern}
    after_paths.update(pv/(asset+'_closeup_'+angle+'.png') for asset in refreshed
                       if 'snowpuffs' in asset for angle in ('34','side','top'))
    for path in after_paths:
        if path.parent==pv and path.stat().st_mtime<started-2:
            raise RuntimeError('Stale after preview: '+str(path))
    cell=(480,360);sheet=Image.new('RGB',(1440,80+410*len(rows)),'#E8EDF4');draw=ImageDraw.Draw(sheet)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22) if Path('C:/Windows/Fonts/arial.ttf').exists() else ImageFont.load_default()
    draw.text((20,20),'AURORA / P5 / LANTERNS + SNOWPUFF BEFORE / AFTER',font=font,fill='#222233')
    for i,(label,paths) in enumerate(rows):
        y=80+i*410;draw.text((18,y),label,font=font,fill='#222233')
        for j,path in enumerate(paths):
            with Image.open(path) as im:
                tile=ImageOps.contain(im.convert('RGB'),cell);sheet.paste(tile,(j*480+(480-tile.width)//2,y+35+(360-tile.height)//2))
    roundness=read(pv/'closeup_roundness.json')
    if {p['id'] for p in roundness['puffs']}!={f'h{n:02d}_snowpuffs' for n in (4,6,14,18)} or not all(p['roundness_pass'] for p in roundness['puffs']):raise RuntimeError('Snowpuff roundness failed')
    target=M.parent/'silhouettes/sheet07-lanterns-snowpuff-closeups.png';target.parent.mkdir(parents=True,exist_ok=True)
    VERIFY();sheet.save(target)
    manifest_path.write_text(json.dumps(manifest,indent=2))
    (M/'fitcheck_props_batch3_polish.txt').write_text('\n'.join(fits[i]['status']+' '+i+' '+json.dumps(fits[i]) for i in sorted(ids))+'\nALL PASS: YES\n')
    VERIFY();print('P5: all ten polish assets PASS. Saved',target)

if __name__=='__main__':
    try:main()
    except Exception:traceback.print_exc();sys.exit(1)
