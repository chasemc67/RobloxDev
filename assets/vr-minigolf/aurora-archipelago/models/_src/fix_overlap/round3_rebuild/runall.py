import json,sys,time;sys.path.insert(0,'/workspace/aa3');from rebuild import *;from metrics import *
d=json.load(open('/workspace/aa3/dump_before.json'))
import custom
CUSTOM={'h18_ramp_lanterns':custom.ramp_lanterns,'h10_bobsled_hut':custom.bobsled,'h15_lip_ice':custom.lip_ice,'h15_great_frozen_falls':custom.falls}
SRC={'h02_lintel_left':'r2','h02_lintel_mid':'r2','h02_lintel_right':'r2','h02_rookery_drift':'r2','h10_bobsled_hut':'appr','h15_lip_ice':'appr',
     'h10_snow_walls_e':'appr','h10_snow_walls_w':'appr','h15_great_frozen_falls':'appr','h18_ramp_lanterns':'appr'}
ids=sys.argv[1:] or list(SRC)
for id in ids:
    t=time.time()
    src=d[f'{SRC[id]}_{id}']['objects']
    if id in CUSTOM: src=CUSTOM[id](src)
    objs,log=rebuild(id,src)
    asset=[dict(name=n,**o) for n,o in objs.items()]
    json.dump(dict(objects=asset,log=log,src=SRC[id]),open(f'/workspace/aa3/geom_{id}.json','w'))
    r=report(id,asset);r['silhouette']=silhouette(d[f'appr_{id}']['objects'],asset);r['ray_thickness_min']=local_thickness(asset)
    json.dump(r,open(f'/workspace/aa3/pre_{id}.json','w'))
    print(id,round(time.time()-t),[l for l in log if 'WARN' in l or 'removed' in l or 'hull' in l],r,flush=True)
