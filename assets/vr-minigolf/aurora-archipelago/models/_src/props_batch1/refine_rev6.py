from pathlib import Path
s=Path('models/_src/props_batch1');p=s/'rev6.py';t=p.read_text().replace("ps=read(S/'parts.json');old=read(M/'props_batch1_manifest.json')","ps=read(S/'_backup_rev5_corals/models/_src/props_batch1/parts.json');old=read(S/'_backup_rev5_corals/models/props_batch1_manifest.json')")
t=t.replace('for j in range(9):','n=4 if mat==\'CoralMint\' else 8;steps=2 if mat==\'CoralMint\' else 4\n   for j in range(steps+1):').replace('math.pi*j/8','math.pi*j/steps').replace('math.tau*i/12','math.tau*i/n').replace('for i in range(12)','for i in range(n)').replace('thick/pw,n=8','thick/pw,n=4')
p.write_text(t)
(s/'failed_rev6.flag').unlink()
