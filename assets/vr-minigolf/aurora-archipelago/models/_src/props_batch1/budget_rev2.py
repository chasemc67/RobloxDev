from pathlib import Path
p=Path('models/_src/props_batch1/fitcheck_batch1.py');s=p.read_text();s=s.replace("totals={n:","heavy={n:sum(r['total_tris']>900 for r,p in zip(results,P) if p['hole']==n and 'coral_' in p['id']) for n in [7,8]}\nlines.append('Heavy small coral props (>900): '+json.dumps(heavy)+'; limit 2 per hole')\ntotals={n:")
s=s.replace("and all(v<=34000 for v in totals.values())","and all(v<=34000 for v in totals.values()) and all(v<=2 for v in heavy.values())")
p.write_text(s)
