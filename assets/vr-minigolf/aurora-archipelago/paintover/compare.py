import sys
from PIL import Image
S=sys.argv[1]; hs=sys.argv[2:]
W=640;H=360
out=Image.new('RGB',(W*2,H*len(hs)))
for i,h in enumerate(hs):
    a=Image.open(f'previews/blockout/{h}_tee.png').convert('RGB').resize((W,H))
    b=Image.open(f'paintover/{h}_paint{S}.png').convert('RGB').resize((W,H))
    out.paste(a,(0,i*H)); out.paste(b,(W,i*H))
out.save(f'paintover/_cmp{S}.jpg',quality=80)
