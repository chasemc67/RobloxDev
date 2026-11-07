# make_downsamples.py - from out/previews/<A|B>_round2.png (1280x720) write _320x180 / _160x90 (Lanczos) and grayscale review
# copies (_gray, ITU-R 601 luma via Pillow 'L') for all three sizes, plus a side-by-side small-size review sheet (no text in
# the thumbnails themselves; the sheet has small labels only and is a review aid, not a deliverable thumbnail).
#   python out/src/make_downsamples.py [--previews out/previews] [--round1-sheet inputs/round1_small_comparison.png]
import argparse, os
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(os.path.join(HERE, '..')); ROOT = os.path.dirname(OUT)
p = argparse.ArgumentParser()
p.add_argument('--previews', default=os.path.join(OUT, 'previews'))
p.add_argument('--round1-sheet', default=os.path.join(ROOT, 'inputs', 'round1_small_comparison.png'))
a = p.parse_args()
small = {}
for k in 'AB':
    src = os.path.join(a.previews, '%s_round2.png' % k)
    im = Image.open(src).convert('RGB')
    assert im.size == (1280, 720), (src, im.size)
    im.convert('L').save(os.path.join(a.previews, '%s_round2_gray.png' % k))
    for w, h in ((320, 180), (160, 90)):
        s = im.resize((w, h), Image.LANCZOS)
        s.save(os.path.join(a.previews, '%s_round2_%dx%d.png' % (k, w, h)))
        s.convert('L').save(os.path.join(a.previews, '%s_round2_%dx%d_gray.png' % (k, w, h)))
        small[(k, w)] = s
# review sheet: round-2 320x180 + 160x90 (colour and gray), native size
W, H = 20 + 320 + 20 + 160 + 20 + 160 + 20, 20 + 2 * (20 + 180) + 10
sheet = Image.new('RGB', (W, H), (240, 240, 240)); d = ImageDraw.Draw(sheet)
for i, k in enumerate('AB'):
    y = 30 + i * 200
    d.text((20, y - 16), '%s round2: 320x180 / 160x90 / 160x90 gray' % k, fill=(20, 20, 20))
    sheet.paste(small[(k, 320)], (20, y)); sheet.paste(small[(k, 160)], (360, y))
    sheet.paste(small[(k, 160)].convert('L').convert('RGB'), (540, y))
sheet.save(os.path.join(a.previews, 'round2_small_review_sheet.png'))
if os.path.exists(a.round1_sheet):
    r1 = Image.open(a.round1_sheet).convert('RGB')
    comb = Image.new('RGB', (r1.width + W + 10, max(r1.height, H)), (255, 255, 255))
    comb.paste(r1, (0, 0)); comb.paste(sheet, (r1.width + 10, 0))
    comb.save(os.path.join(a.previews, 'round1_vs_round2_small_comparison.png'))
print('DOWNSAMPLES_OK')
