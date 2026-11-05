import pickle,sys,json
sys.path.insert(0,'.')
import wreck_lib as L
L.PAL.update({k:tuple(v) for k,v in json.load(open('../work/palette.json')).items()})
from box_preview import render
D=pickle.load(open('../work/assembled_preview.pkl','rb'));parts=list(D.values())
for name,eye,tgt,fov in [('e_34',(-230,190,330),(0,60,0),45),('e_front',(0,80,520),(0,70,0),40),('e_back',(180,170,-330),(0,60,0),45)]:
    render(parts,f'/tmp/{name}_b.png',eye,tgt,size=(1400,900),fov=fov,sand=False)
