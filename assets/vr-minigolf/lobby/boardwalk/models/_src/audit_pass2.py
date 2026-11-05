from pathlib import Path
from PIL import Image
import json,datetime
SRC=Path(__file__).parent;ROOT=SRC.parent;LOBBY=ROOT.parent.parent
lines=[]
for check in (SRC/'fitcheck_pass2_validated.txt',SRC/'reimport_check_pass2.txt',LOBBY/'kit/_src/reimport_check_pass2.txt'):
    text=check.read_text();assert 'RESULT: ALL PASS' in text and 'FAIL ' not in text;lines.append('PASS '+str(check.relative_to(LOBBY)))
for root,count in ((ROOT,37),(LOBBY/'kit',21)):
    man=json.loads((root/'manifest.json').read_text());assert len(man['props'])==count
    for e in man['props']:
        assert (root/e['fbx']).stat().st_size>1000
        assert e['triangles']<=e['tris_max']
        if root==LOBBY/'kit':
            for v in ('eye','34'):
                p=root/'previews'/(e['name']+'_'+v+'.png');im=Image.open(p);im.verify()
    assert Image.open(root/'textures/bw_atlas_1024.png').size==(1024,1024)
    lines.append('PASS '+str(root.relative_to(LOBBY))+' '+str(count)+' assets/budgets/atlas')
for c in ('lantern_grove','sugarloaf_canyon','aurora_archipelago'):
    for v in ('eye','34'):Image.open(ROOT/'previews/portals'/(c+'_'+v+'.png')).verify()
for f in (ROOT/'previews/portals/portals_vs_concepts.png',LOBBY/'kit/previews/kit_contact_sheet.png'):
    Image.open(f).verify();lines.append('PASS '+str(f.relative_to(LOBBY)))
for f in (SRC/'pass2_summary.md',ROOT/'README.md',LOBBY/'kit/README.md'):
    assert f.stat().st_size>1000;lines.append('PASS documentation '+str(f.relative_to(LOBBY)))
assert (ROOT/'_backup_pass1/manifest.json').is_file()
assert (ROOT/'_backup_pass1/fbx').is_dir()
assert (ROOT/'_backup_pass1/previews').is_dir()
for log in ('build_pass2.log','reimport_pass2.log','fitcheck_pass2.log','render_pass2.log','build_kit.log','reimport_kit.log','render_kit.log'):
    text=(SRC/log).read_text(encoding='utf-16' if (SRC/log).read_bytes()[:2]==b'\xff\xfe' else 'utf-8',errors='replace')
    assert 'Traceback' not in text and ('RESULT: ALL PASS' in text if log=='fitcheck_pass2.log' else 'Blender quit' in text),log
lines.append('RESULT: ALL PASS')
(SRC/'artifact_audit_pass2.txt').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
