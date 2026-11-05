"""Make the before/after comparison sheet from rendered pass-4 outputs."""
from pathlib import Path
import sys
from PIL import Image,ImageDraw
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1])
def main():
    folder=ROOT/'previews_pass4';w,h=640,360;bar=36
    sheet=Image.new('RGB',(w*2,(h+bar)*3),'white');draw=ImageDraw.Draw(sheet)
    rows=[('Boardwalk eye','SL1_before_boardwalk_eye.png','SL1_boardwalk_eye.png'),('Boardwalk silhouette','SL1_before_boardwalk_eye_silhouette.png','SL1_after_boardwalk_eye_silhouette.png'),('3/4 silhouette','SL1_before_34_silhouette.png','SL1_after_34_silhouette.png')]
    for row,(title,before,after) in enumerate(rows):
        for col,name in enumerate((before,after)):
            y=row*(h+bar);draw.text((col*w+12,y+10),('BEFORE ? ' if col==0 else 'AFTER ? ')+title,fill='black')
            with Image.open(folder/name) as im:sheet.paste(im.convert('RGB').resize((w,h),Image.Resampling.LANCZOS),(col*w,y+bar))
    sheet.save(folder/'sheet_sl1_pass4_before_after.png')
if __name__=='__main__':
    try:main()
    except Exception:
        import traceback
        traceback.print_exc();sys.exit(1)
