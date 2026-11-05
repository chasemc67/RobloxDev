# mastfix.py - start_ship_b2_detail_v3 mast-collider fix (ORIGINAL v3, not the refined ship).
# blender.exe -b --factory-startup <original start_ship_v3.blend> --python-exit-code 1 --python mastfix.py -- <out_blend>
# Input: the ORIGINAL v3 release blend (start_ship_b2_detail_v3/out/start_ship_v3.blend, sha256 below), opened read-only.
# Change: ONLY the 8 vertex positions of mesh COL_Mast_Main. The 4 bottom vertices stay as-is; the 4 top vertices are moved
# to the measured positions of the approved donor (mast_donor_v3_2.blend), i.e. the box is shortened 157.0 -> 98.3 along its
# 18 deg axis. Donor coordinates are embedded below (exact float32 values) so the donor file is NOT needed to rebuild.
# Every guard below must hold or the script exits 1 without saving. Nothing else (objects/materials/images/anchors) is touched.
import bpy, sys, hashlib
OUT = sys.argv[sys.argv.index('--') + 1:][0]
SOURCE_SHA256 = '87b319a5b6308c1d7d3deaac91b4b4e16b651572ac569a14606a8446442cc92f'
DONOR_SHA256 = '9d75ae96912ff0ca4b7a97b5b6287e3cc10d55edefa0c2719c6cfec2dd0bf333'  # mast_donor_v3_2.blend (provenance only)
# origin matrix of COL_Mast_Main (identical in source and donor)
MATRIX = [[1.0, 0.0, 0.0, 10.0], [0.0, 1.0, 0.0, -26.729970932006836], [0.0, 0.0, 1.0, 82.26638793945312], [0.0, 0.0, 0.0, 1.0]]
# local vertex co, source (v3) and donor; index order = mesh vertex order; bottom = 0,2,4,6 top = 1,3,5,7
SRC = [(-2.5, 21.88019371032715, -75.43048095703125), (-2.5, -26.635475158691406, 73.88539123535156),
       (-2.5, 26.635475158691406, -73.88539123535156), (-2.5, -21.88019371032715, 75.43048095703125),
       (2.5, 21.88019371032715, -75.43048095703125), (2.5, -26.635475158691406, 73.88539123535156),
       (2.5, 26.635475158691406, -73.88539123535156), (2.5, -21.88019371032715, 75.43048095703125)]
DONOR = [(-2.5, 21.88019371032715, -75.43048095703125), (-2.5, -8.49617862701416, 18.05837631225586),
         (-2.5, 26.635475158691406, -73.88539123535156), (-2.5, -3.7408969402313232, 19.603466033935547),
         (2.5, 21.88019371032715, -75.43048095703125), (2.5, -8.49617862701416, 18.05837631225586),
         (2.5, 26.635475158691406, -73.88539123535156), (2.5, -3.7408969402313232, 19.603466033935547)]
POLYS = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
BOTTOM = (0, 2, 4, 6)

def fail(msg): print('MASTFIX_FAIL', msg); sys.exit(1)
src_sha = hashlib.sha256(open(bpy.data.filepath, 'rb').read()).hexdigest()
if src_sha != SOURCE_SHA256: fail('source sha256 %s != %s' % (src_sha, SOURCE_SHA256))
o = bpy.data.objects.get('COL_Mast_Main')
if o is None or o.type != 'MESH' or o.data.name != 'COL_Mast_Main' or o.data.users != 1: fail('COL_Mast_Main object/mesh datablock mismatch')
if [list(r) for r in o.matrix_world] != MATRIX or [list(r) for r in o.matrix_basis] != MATRIX: fail('origin matrix mismatch')
me = o.data
if [tuple(v.co) for v in me.vertices] != SRC: fail('source vertices differ from the measured v3 COL_Mast_Main')
if [tuple(p.vertices) for p in me.polygons] != POLYS: fail('topology mismatch')
if any(DONOR[i] != SRC[i] for i in BOTTOM): fail('donor bottom != source bottom')
flat = [c for v in DONOR for c in v]
me.attributes['position'].data.foreach_set('vector', flat)
me.update()
if [tuple(v.co) for v in me.vertices] != DONOR: fail('write-back mismatch')
bpy.ops.wm.save_as_mainfile(filepath=OUT, copy=True, check_existing=False)
if hashlib.sha256(open(bpy.data.filepath, 'rb').read()).hexdigest() != SOURCE_SHA256: fail('source changed on disk!')
print('MASTFIX_OK', OUT)
