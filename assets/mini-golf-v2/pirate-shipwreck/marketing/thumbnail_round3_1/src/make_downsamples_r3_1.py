# make_downsamples_r3_1.py - from the single 1920x1080 render write 1280x720 / 320x180 / 160x90 (Lanczos) + grayscale (ITU-R 601 luma) of all four sizes.
#   python make_downsamples_r3_1.py --source out/previews/B_round3_1_1920x1080.png --output out/previews
import argparse, os
from PIL import Image
p = argparse.ArgumentParser()
p.add_argument('--source', required=True, help='B_round3_1_1920x1080.png'); p.add_argument('--output', required=True, help='previews dir')
p.add_argument('--stem', default='B_round3_1')
a = p.parse_args()
im = Image.open(a.source).convert('RGB'); assert im.size == (1920, 1080), im.size
os.makedirs(a.output, exist_ok=True)
for w, h in ((1920, 1080), (1280, 720), (320, 180), (160, 90)):
    s = im if (w, h) == im.size else im.resize((w, h), Image.LANCZOS)
    fn = os.path.join(a.output, '%s_%dx%d.png' % (a.stem, w, h))
    if os.path.abspath(fn) != os.path.abspath(a.source):
        s.save(fn)
    s.convert('L').save(os.path.join(a.output, '%s_%dx%d_gray.png' % (a.stem, w, h)))
print('DOWNSAMPLES_R3_1_OK')
