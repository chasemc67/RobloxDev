# box: /workspace/.geo/bin/python make_manifest.py  -> ../manifest.json (reads work/box_report.json + PC dump.json when present)
import json,os,math
H=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
r=json.load(open(f'{H}/work/box_report.json'));P=r['parts']
dump=json.load(open(f'{H}/previews_wreck_v1/dump.json')) if os.path.exists(f'{H}/previews_wreck_v1/dump.json') else {}
def sz(p): b=P[p]['bbox_wreck_frame'];return [round(b['max'][i]-b['min'][i],2) for i in range(3)]
parts={}
for k,kind in [('wreck_hull','hull + deck + stern-quarter cabin + pad-1 plank deck (one chunk, no split needed)'),('wreck_rig','masts + sails + rigging'),('wreck_glow','lantern globes + window panes (swap to Neon/PointLight)'),('wreck_duck','grumpy rubber-duck figurehead, own pivot')]:
    d=dict(fbx=f'{k}.fbx',kind=kind,tris=P[k]['tris'],budget=P[k].get('budget'),size_studs_xyz=sz(k),bbox=P[k]['bbox_wreck_frame'])
    if k in dump: d['tris_in_fbx_blender_import']=dump[k]['tris']
    parts[k]=d
da=r['duck_assembly']
parts['wreck_hull']['pivot']=parts['wreck_rig']['pivot']=parts['wreck_glow']['pivot']=[0,0,0]
parts['wreck_duck']['pivot_in_wreck_frame']=da['position'];parts['wreck_duck']['assembly_rotation3x3']=da['rotation3x3']
pad=dict(top_y=24.0,x=[-27,27],z=[-152,-68],size_studs=dict(across_ship=54,along_ship=84),centre=[0,24,-110],
  note='level flat plank deck, no props; centre is 50 studs from the stern end. Felt 30x60 (outer 38x68) with art-clear 54x84 fits exactly; the 54 across is the deck width. Pad centre world (0,24,-110); play axis runs along Z.')
man=dict(version='wreck_v1',look='B Golden Hour Hideaway',units='studs (1 stud = 1 Blender unit, FBX exported 1:1)',
 frame='Roblox frame: +Y up, bow toward +Z (duck faces +Z, lagoon), stern toward -Z (beach, pad 1). Origin = water line (y=0), on the deck centreline x=0, z=0 at hull midship. Place all four FBXs at the same origin with identity rotation; the duck gets its own CFrame (assembly).',
 water_line_origin='y=0 is the water line. Hull min y %s (keel at midship/stern); lowest hull point at the bow end %s (below the water line); stern end sits near the sand.'%(r['parts']['_hull_min_y'],r['parts']['_bow_end_lowest_hull_y']),
 sizes=dict(hull_local_length=320,hull_local_beam=90,hull_height_keel_to_sheer='60 at midships, 64 at the bow',mast_tip_y=r['parts']['_main_mast_tip_y'],
   note='length/beam/height are measured in the hull own axes before the 15 deg list; the world bbox is wider across X because of the list'),
 list_roll_deg=15,list_note='the hull lists 15 deg (roll about the long axis, high side +X). Deck centreline stays at x=0.',
 pad1_deck=pad,pad1_clearance_check=r['parts']['_pad1_clearance_max_height_above_pad_within_25'],
 parts=parts,generator=['src/wreck_lib.py','src/gen_wreck.py','src/build_wreck.py','src/render_wreck.py','src/make_manifest.py'],
 previews='previews_wreck_v1/',
 deviations=[
  'LIST not bow-up pitch: the art director said the bow sits in the lagoon and only the stern touches sand, so the 15 deg tilt is a roll (list) about the long axis (the sheet side view shows the deck from above), the keel stays level and the lower bow hull is under the water line.',
  'Sizes follow the art director override: hull ~320 x 90 x 60 (built at 220x70x45 and scaled 1.4545 x 1.2857 x 1.333, no added detail); mast tip y=%s.'%r['parts']['_main_mast_tip_y'],
  'Cabin moved off the very stern to z -32..-55 (just forward of the pad-1 deck, 14+ studs clear of its edge) so the stern 84 studs stay flat and empty with nothing >3 studs within 25 of the pad centre (the sheet puts the cabin at the stern).',
  'Pad-1 deck is a level plank platform (top y=24) standing on posts over the listed deck; its high-side edge is flush with the deck, the low-side edge is skirted.',
  'No rocks/loose beams/barrel at the hull base (bow is in water; keep lagoon/beach props to the course builder).',
  'Sails are red/cream stripe patchwork; palette-texture UVs instead of vertex colours (Roblox multiplies vertex colour with texture).',
  'Duck is ~35 studs tall (head ~18 wide) rather than RobloxDevBot 22: it keeps the sheet proportion against the larger hull. Hat is a plain navy captain cap, eyepatch only, no skull and crossbones.']
 ,cabin_z=[-55,-32],deck_centreline_y=round(-33.136+49.333,2))
json.dump(man,open(f'{H}/manifest.json','w'),indent=1);print('ok')
