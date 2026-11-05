from pathlib import Path
S=Path(__file__).resolve().parent;p=S/'gen_batch2.py';t=p.read_text()
a=t.index("p=part(12,'icebreaker');");b=t.index("for o in a(12,'icebreaker')",a)
t=t[:a]+"p=part(12,'icebreaker')\np.notes.append('Hull solid upper dressing starts y1.11, .11 above gameplay hull faces, preserving wheel slot. Lower source hull skins separately unresolved at adjoining rail seam.')\nskip(12,'hull_face_skins','Exact rail2/hull13 connections share endpoints with approach rail1; lower source skins have zero adjoining rail clearance. Upper icebreaker retained above y1.11.')\n"+t[b:]
t=t.replace("box(p,'HullTeal',[x,1.5,z],[w,3,d])","box(p,'HullTeal',[x,2.055,z],[w,1.89,d-.24])").replace("[w*.65,2,d*.7]","[w*.65,2,d*.7]")
p.write_text(t)
