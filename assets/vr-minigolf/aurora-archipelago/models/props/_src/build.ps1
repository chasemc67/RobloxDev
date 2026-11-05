# Rebuild every Aurora P1 prop: textures -> FBX/previews/manifest -> fitcheck -> FBX re-import check -> tee views -> docs.
# Run from the workspace root (C:\Users\chase\aurora_p2). One Blender process at a time.
$B = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
python out_props\_src\textures.py
& $B -b --factory-startup -P out_props\_src\build_all.py
& $B -b --factory-startup -P out_props\_src\fitcheck.py
& $B -b --factory-startup -P out_props\_src\verify_fbx.py
& $B -b out_p2b\models\blockout\aurora_blockout.blend -P out_props\_src\tee_views.py
python out_props\_src\make_docs.py
