"""PIL before/after sheet. Requires the user's current-source validated Blender builds."""
import argparse,json,hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
S=Path(__file__).resolve().parent;D=S.parents[1]
def read(p):return json.loads(p.read_text())
def font(size):
    for p in ['C:/Windows/Fonts/consola.ttf','C:/Windows/Fonts/arial.ttf']:
        if Path(p).exists():return ImageFont.truetype(p,size)
    return ImageFont.load_default()
def silhouette(tris,size):
    vs=[v for t in tris for v in t];lo=[min(v[i] for v in vs) for i in [0,1]];hi=[max(v[i] for v in vs) for i in [0,1]]
    scale=min((size[0]-40)/max(hi[0]-lo[0],.01),(size[1]-40)/max(hi[1]-lo[1],.01));cx=(lo[0]+hi[0])/2
    im=Image.new('RGB',size,'#F4F6FB');dr=ImageDraw.Draw(im)
    for t in tris:dr.polygon([(size[0]/2+(v[0]-cx)*scale,size[1]-20-(v[1]-lo[1])*scale) for v in t],fill='#222233')
    dr.line((20,size[1]-20,size[0]-20,size[1]-20),fill='#97ADA7')
    dr.text((12,8),'FRONT / X-Y orthographic',font=font(14),fill='#364050');return im
def table():
    rows=[]
    for batch in ['props_batch1','props_batch3']:
        b=S/batch;F=read(b/'fitcheck_report.json');fits={p['id']:p for p in F['parts']};shapes=read(b/'polish_shapes.json')
        for sh in shapes:
            r=fits[sh['id']];felt='source skin' if r['min_felt_clearance'] is None else f"{r['nearest_felt']} {r['min_felt_clearance']:.4f}"
            rows.append(dict(batch=batch,id=sh['id'],old_tris=sh['old_tris'],new_tris=r['total_tris'],nearest_rail=f"{r['nearest_rail']} {r['min_rail_clearance']:.4f}",nearest_felt=felt,heavy_count=F['heavy_counts'][str(r['hole'])]))
    return rows
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--table-only',action='store_true',help='Print current preflight table without rendering or accepting stale previews');args=ap.parse_args()
    rows=table();print('| ID | Old tris | New tris | Nearest rail | Nearest felt | Heavy count per hole |');print('|---|---:|---:|---|---|---:|')
    for r in rows:print(f"| {r['id']} | {r['old_tris']} | {r['new_tris']} | {r['nearest_rail']} | {r['nearest_felt']} | {r['heavy_count']} |")
    if args.table_only:return
    for batch in ['props_batch1','props_batch3']:
        b=S/batch;digest=hashlib.sha256((b/'parts.json').read_bytes()).hexdigest();B=read(b/'build_report.json');V=read(b/'fbx_validation.json');F=read(b/'fitcheck_report.json')
        assert B.get('generated_by')=='Blender bpy' and B.get('parts_sha256')==digest,'Run current-source user Blender build for '+batch
        assert V.get('all_pass') and V.get('parts_sha256')==digest and set(V['exported_ids'])==set(read(b/'polish_ids.json')),'Selective FBX validation required'
        assert F['all_pass'] and F['mode']=='Blender actual triangles' and F['parts_sha256']==digest,'Run post-build fitcheck for '+batch
        assert B['triangles_sha256']==hashlib.sha256((b/'triangles.json').read_bytes()).hexdigest()
    cell=(480,340);rowh=405;sheet=Image.new('RGB',(1440,90+rowh*len(rows)),'#E8EDF4');dr=ImageDraw.Draw(sheet)
    dr.text((18,12),'AURORA ARCHIPELAGO / POLISH / 28 ASSETS',font=font(27),fill='#222233')
    for i,label in enumerate(['BEFORE / 3-4 preview','AFTER / 3-4 preview','AFTER / front silhouette']):dr.text((i*480+15,55),label,font=font(20),fill='#364050')
    caches={b:read(S/b/'triangles.json') for b in ['props_batch1','props_batch3']}
    from datetime import datetime
    for i,r in enumerate(rows):
        y=90+i*rowh;batch=r['batch'];id=r['id'];before=S/'_prepolish_previews'/batch/(id+'_34.png');after=D/'models/previews'/batch/(id+'_34.png')
        assert before.is_file() and after.is_file(),f'Missing preview: {id}'
        started=datetime.fromisoformat(read(S/batch/'build_report.json')['started_utc']).timestamp()
        assert after.stat().st_mtime>=started-2,'Stale AFTER preview '+id
        for j,path in enumerate([before,after]):
            canvas=Image.new('RGB',cell,'#F4F6FB');im=Image.open(path).convert('RGBA');im=ImageOps.contain(im,cell);canvas.paste(im,((480-im.width)//2,(340-im.height)//2),im);sheet.paste(canvas,(j*480,y))
        sheet.paste(silhouette(caches[batch][id],cell),(960,y))
        dr.text((12,y+346),f"{id}   {r['old_tris']} -> {r['new_tris']} tris   heavy/hole {r['heavy_count']}",font=font(18),fill='#222233')
        dr.text((12,y+374),f"rail: {r['nearest_rail']}   felt: {r['nearest_felt']}",font=font(15),fill='#364050')
    target=D/'silhouettes/sheet06-polish-before-after.png';target.parent.mkdir(parents=True,exist_ok=True);sheet.save(target);print('Saved',target)
if __name__=='__main__':main()
