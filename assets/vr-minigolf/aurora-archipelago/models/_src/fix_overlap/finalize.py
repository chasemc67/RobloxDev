"""After-cache clearance, fitcheck, source-schema manifest, and labelled contact sheet."""
import json
from PIL import Image,ImageDraw,ImageFont
from common import S,D,CHANGED,UNCHANGED,NO_CHANGE,records,guard,write_json
from clearance import main as clearance_main

def main():
    guard('check');clearance_main('after')
    before=json.loads((S/'clearance_before.json').read_text());after=json.loads((S/'clearance_after.json').read_text())
    build=json.loads((S/'build_fix.json').read_text());validation=json.loads((S/'fbx_validation.json').read_text())
    if {p['id'] for p in build}!=set(CHANGED):raise RuntimeError('Build must contain only the two changed assets')
    unchanged=[]
    for id in UNCHANGED:
        q=next(dict(p) for p in records() if p['id']==id)
        q.update(before=before[id],after=before[id],notes=[NO_CHANGE],exported=False)
        unchanged.append(q)
    lines=['Aurora overlap fixes: real freshly imported FBX triangles; signed 3D clearance; no exemptions.','']
    passed=validation['all_pass']
    for p in build:
        id=p['id'];rail=.30 if id in ['h14_rail_bollards','h18_crystal_chute'] else .15
        ok=after[id]['rail']['clearance']>=rail-1e-5 and after[id]['felt']['clearance']>=.15-1e-5 and p['tris']<3000
        passed &= ok;p.update(before=before[id],after=after[id],pass_fitcheck=ok)
        lines.append(f"{id}: rail {before[id]['rail']['clearance']:.6f} -> {after[id]['rail']['clearance']:.6f} (>= {rail:.2f}); felt {before[id]['felt']['clearance']:.6f} -> {after[id]['felt']['clearance']:.6f} (>= .15); tris {p['tris']}; lift {p['lift_y']:.6f}; {'PASS' if ok else 'FAIL'}")
        if id=='h06_respawn_stone' and after[id]['rail']['clearance']<.15-1e-5:lines.append('Stone felt-only minimum lift cannot clear rail; no tilt, scale or sideways edit performed.')
    for p in unchanged:
        id=p['id'];r=before[id];rail=.30 if id=='h14_rail_bollards' else .15
        ok=r['rail']['clearance']>=rail and r['felt']['clearance']>=.15
        passed &= ok
        lines.append(f"{id}: {NO_CHANGE}; before = after: rail {r['rail']['clearance']:.6f}; felt {r['felt']['clearance']:.6f}; {'PASS' if ok else 'FAIL'}")
    (D/'models/fitcheck_props_fix_overlap.txt').write_text('\n'.join(lines)+'\n')
    source=json.loads((D/'models/props_batch3_manifest.json').read_text());source.update(batch='fix_overlap',parts=build,unchanged_assets=unchanged,all_pass=bool(passed),validation_stage='fresh FBX reimport, true 3D signed clearance')
    write_json(D/'models/props_fix_overlap_manifest.json',source)
    sheet=Image.new('RGB',(1800,len(CHANGED)*780+150),(22,25,34));draw=ImageDraw.Draw(sheet)
    try:font=ImageFont.truetype('arial.ttf',24)
    except OSError:font=ImageFont.load_default()
    for row,id in enumerate(CHANGED):
        for col,stage in enumerate(['before','after']):
            pic=Image.open(S/f'renders/{id}_{stage}.png').convert('RGB');pic.thumbnail((900,700));sheet.paste(pic,(col*900,row*780+75))
            r=before[id] if stage=='before' else after[id]
            draw.text((col*900+15,row*780+8),f'{id}  {stage.upper()}',fill='white',font=font)
            draw.text((col*900+15,row*780+38),f"rail {r['rail']['id']}: {r['rail']['clearance']:.4f}   felt {r['felt']['id']}: {r['felt']['clearance']:.4f}",fill='white',font=font)
    for row,p in enumerate(unchanged):
        r=p['before']
        draw.text((15,len(CHANGED)*780+10+row*65),f"{p['id']}: {NO_CHANGE}\nbefore = after: rail {r['rail']['clearance']:.4f}; felt {r['felt']['clearance']:.4f}",fill='white',font=font)
    target=D/'silhouettes/sheet08-overlap-fixes.png';target.parent.mkdir(parents=True,exist_ok=True);sheet.save(target)
    guard('check')
    if not passed:raise RuntimeError('Overlap fitcheck failed; see report')
if __name__=='__main__':main()
