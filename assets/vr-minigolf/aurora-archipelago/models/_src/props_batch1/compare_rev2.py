from pathlib import Path
p=Path('models/_src/props_batch1/finalize_rev2.py');s=p.read_text();start=s.index('rows={');end=s.index('\nfor n,rr in rows.items():',start)
s=s[:start]+'''def row(name,source,lo,hi):return (name,source,(0,lo*2,source.width,hi*2))
rows={1:[row('harbour_lantern',A,30,170),row('snow_boulder',A,170,306)],2:[row('lantern_crook',A,306,444),row('lintel_left',A,444,580),row('rookery_drift',A,580,716)],3:[row('ice_plank',A,716,854),row('ice_bridge',A,854,990),row('glimmer_islet',A,990,1134)],5:[row('steamwhistle_geyser',B,30,164),row('geyser_column',B,164,308),row('cliff_face_w',B,308,446),row('signal_lamp',B,446,584),row('geyser_steps',B,584,716)],7:[row('coral_w2',B,716,848)],8:[row('giant_coral',B,848,986),row('coral_2',B,986,1134)]}
'''+s[end:];p.write_text(s)
