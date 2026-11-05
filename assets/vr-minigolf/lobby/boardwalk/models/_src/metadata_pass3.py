import json
from pathlib import Path
p=Path(__file__).parent
for c in ('lantern_grove','sugarloaf_canyon','aurora_archipelago'):
    f=p/'manifest_parts'/('bw_arch_'+c+'.json');e=json.loads(f.read_text())
    e.update(portal_trigger={'name':'PortalTrigger_'+c,'center':[0,5,0],'size':[10,10,3],'modelled':False,'CanCollide':False,'CanQuery':False,'Transparency':1},attach_points={'nameplate_center':[0,14.5,2.25],'coming_soon_sign_center':[0,12.7,2.25],'rope_loop_anchors':[[-2,13.5,2.25],[2,13.5,2.25]],'apron_origin':[0,0,4],'moving_parts_origin':[0,0,0]},portal_surface={'asset':'bw_portal_surface_'+c,'center':[0,6,1.5],'size':[10,12],'UV':[0,0,1,1]},motion_notes='Runtime only: gentle pulse; no real lights. Surface scrolling, particles, trigger/teleport controlled by Roblox.',clearance_exemptions=['Portal quad is intentionally inside opening/trigger; noncolliding runtime display.','Apron separate floor strip: top Y=0, placed Z=4 outside arch envelope.','Reused nameplate/sign attach forward of envelope; coming-soon sign bottom Y=11.7, Z=2.25 outside arch depth and trigger.'])
    e['attach_points']['lantern_cord_anchors']=([ [x,z+.5,1.3] for x,z in ((-6.5,11),(6.5,11),(-6.5,7),(6.5,7),(-3.5,14),(3.5,14))] if c=='lantern_grove' else [[-6.5,12.6,1.3],[6.5,12.6,1.3]])
    if c!='lantern_grove':e['attach_points']['lantern_cord_anchors']=[[-6.5,12.6,1.6],[6.5,12.6,1.6]]
    f.write_text(json.dumps(e,indent=1))
print('Portal metadata updated')

for c in ('lantern_grove','sugarloaf_canyon','aurora_archipelago'):
 f=p/'manifest_parts'/('bw_arch_'+c+'.json');e=json.loads(f.read_text())
 lanterns=[json.loads(q.read_text()) for q in sorted((p/'manifest_parts').glob('bw_arch_'+c+'_lantern_*.json'))]
 e['attach_points']['lantern_cord_anchors']=[q['anchor_position_arch_local'] for q in lanterns]
 e['attach_points'].pop('moving_parts_origin',None)
 e['moving_parts']=[dict(asset=q['name'],anchor_position_arch_local=q['anchor_position_arch_local'],swing_axis=q['swing_axis'],suggested_motion=q['suggested_motion']) for q in lanterns]
 e['motion_notes']='Each lantern has its own hinge origin; place at its arch-local anchor. Surface and Neon animation controlled at runtime. Snowpuff retains arch-base pivot.'
 f.write_text(json.dumps(e,indent=1))
