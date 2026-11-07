# make_downsamples_r3.py - from B_round3.png (1280x720) write _320x180 / _160x90 (Lanczos) + grayscale copies of all three
# (ITU-R 601 luma, Pillow 'L'), and round2_vs_round3_small_comparison.png (review aid with small labels; thumbnails have no text).
#   python out/src/make_downsamples_r3.py --previews out/previews --round2 out/logs/round2_A_reference.png
import argparse, os
from PIL import Image, ImageDraw
p = argparse.ArgumentParser()
p.add_argument('--previews', required=True)
p.add_argument('--round2', required=True, help='round-2 scene A render (1280x720, the frame of the sketch) from the unmodified round-2 input file')
a = p.parse_args()
def smalls(path, stem, save):
    im = Image.open(path).convert('RGB'); assert im.size == (1280, 720), (path, im.size)
    out = {1280: im}
    for w, h in ((320, 180), (160, 90)):
        out[w] = im.resize((w, h), Image.LANCZOS)
    if save:
        im.convert('L').save(os.path.join(a.previews, stem + '_gray.png'))
        for w, h in ((320, 180), (160, 90)):
            out[w].save(os.path.join(a.previews, '%s_%dx%d.png' % (stem, w, h)))
            out[w].convert('L').save(os.path.join(a.previews, '%s_%dx%d_gray.png' % (stem, w, h)))
    return out
r3 = smalls(os.path.join(a.previews, 'B_round3.png'), 'B_round3', True)
r2 = smalls(a.round2, 'B_round2', False)
W = 20 + 320 + 20 + 160 + 20 + 160 + 20 + 320 + 20; H = 20 + 2 * 210
sheet = Image.new('RGB', (W, H), (240, 240, 240)); d = ImageDraw.Draw(sheet)
for i, (lab, s) in enumerate((('Round 2 A (sketch frame)', r2), ('Round 3 lead (B_round3)', r3))):
    y = 34 + i * 210
    d.text((20, y - 16), '%s: 320x180 | 160x90 | 160x90 gray | 320x180 gray' % lab, fill=(20, 20, 20))
    x = 20
    for im in (s[320], s[160], s[160].convert('L').convert('RGB'), s[320].convert('L').convert('RGB')):
        sheet.paste(im, (x, y)); x += im.width + 20
sheet.save(os.path.join(a.previews, 'round2_vs_round3_small_comparison.png'))
print('DOWNSAMPLES_R3_OK')
