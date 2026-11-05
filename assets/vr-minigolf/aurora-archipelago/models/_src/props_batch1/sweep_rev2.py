from pathlib import Path
p=Path('models/_src/props_batch1/fitcheck_batch1.py');s=p.read_text();needle="if sw[0][0]<.1-1e-5:fail.append('mover sweep clearance')";s=s.replace(needle,needle+'''
        # Geyser square contact mesh has an exact axis-aligned translation volume.
        vv=sweepT.reshape(-1,3);lo=vv.min(axis=0);hi=vv.max(axis=0)
        swept_box=dict(center=((lo+hi)/2).tolist(),size=(hi-lo).tolist())
        dressing=sorted((clearance(triangles(other),swept_box),other['id']) for other in P if other['hole']==p['hole'] and other['id']!=p['id'])
        sweep['min_dressing_clearance']=dressing[0][0];sweep['nearest_dressing']=dressing[0][1]
        if dressing[0][0]<.15-1e-5:fail.append('mover sweep dressing clearance <0.15')
''');p.write_text(s)
