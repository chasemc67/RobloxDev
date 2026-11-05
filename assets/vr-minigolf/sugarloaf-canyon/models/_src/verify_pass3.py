from pathlib import Path
import time,json
p=Path('_src/sc_fitcheck.py');t=p.read_text().replace("'elevation_deg':-3.0","'elevation_deg':2.0").replace('crown = [-370.0, 196.0, 165.0]','crown = [-370.0, 170.0, 165.0]').replace('"fitcheck_pass2_validated.txt"','"fitcheck_pass3_validated.txt"');p.write_text(t)
p=Path('_src/sc_pieces.py');t=p.read_text().replace('Striped shell over the terrain dome h = 18 + 190 cos^2(pi/2 q), r 72.','Rounded shell over terrain h=18+110*sqrt(1-q^4), r72, flattened top.');p.write_text(t)
p=Path('_src/PROGRESS.md');f=p.open('a');f.write(time.strftime('%Y-%m-%d %H:%M:%S')+' Final self-review: six renders inspected; arch sun partially touches lintel, visible beneath it; dam plain spillway sheet visible. Remaining sparse layout/kit seams and illustration gap recorded.\n');f.close()
