# writes build args json for Blender: verts already prop-local Roblox coords
import json,sys
ids=sys.argv[1:];out={}
for id in ids:
    g=json.load(open(f'/workspace/aa3/geom_{id}.json'))
    out[id]=dict(src=f'C:\\Users\\chase\\aa_fix3\\in\\appr_{id}.fbx',objects={o['name']:dict(verts=o['verts'],tris=o['tris']) for o in g['objects']})
json.dump(out,open('/workspace/aa3/build_geom.json','w'))
print({id:{n:len(o['tris']) for n,o in v['objects'].items()} for id,v in out.items()})
