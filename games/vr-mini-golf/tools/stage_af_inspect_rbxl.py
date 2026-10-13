"""Read-only binary-place content inspection (uv --with lz4 --with zstandard)."""
import struct,json,sys,re
from pathlib import Path
import lz4.block,zstandard
p=Path(sys.argv[1]); b=p.read_bytes();o=32;chunks=[];props=[];strings=[]
def string(data,pos):
 n=struct.unpack_from('<I',data,pos)[0];pos+=4
 return data[pos:pos+n],pos+n
while o+16<=len(b):
 name=b[o:o+4].decode('latin1');cl,ul,res=struct.unpack_from('<III',b,o+4);o+=16
 raw=b[o:o+(cl or ul)];o+=cl or ul
 if cl:
  try: raw=lz4.block.decompress(raw,uncompressed_size=ul)
  except:raw=zstandard.ZstdDecompressor().decompress(raw,max_output_size=ul)
 chunks.append({'name':name,'compressed':cl,'uncompressed':ul})
 if name=='PROP':
  cid=struct.unpack_from('<I',raw)[0];pn,pos=string(raw,4);pn=pn.decode('utf8');typ=raw[pos];pos+=1
  row={'classId':cid,'property':pn,'type':typ,'bytes':len(raw)-pos}
  if typ==1:
   vals=[]
   while pos<len(raw):
    v,pos=string(raw,pos)
    if pn in ['MeshId','MeshContent','TextureID','TextureContent','MeshData','PhysicsData','Name']: vals.append(v.decode('utf8','replace'))
   if vals:row['values']=vals
  if pn in ['MeshId','MeshContent','TextureID','TextureContent']:row['assetIds']=sorted(set(x.decode() for x in re.findall(rb'rbxassetid://\d+',raw)))
  props.append(row)
 if name.startswith('END'):break
out={'file':str(p),'bytes':len(b),'chunks':chunks,'properties':props}
Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'bytes':len(b),'chunkTypes':sorted(set(x['name'] for x in chunks)),'meshProperties':[x for x in props if any(z in x['property'] for z in ['Mesh','Physics','Content'])]},indent=2)[:6000])
