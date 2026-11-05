"""import/terrain_only.luau = import_world.luau with parts/lighting/standIns off, fast restart, and the material-colour / water lines left as set in Studio (v9/v10 re-terrain runs; v10 keeps the MAT_COLORS line active so the new palette is applied)."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(f'{ROOT}/import/import_world.luau').read()
for a, b in (('parts = true,  ', 'parts = false, '), ('lighting = true,', 'lighting = false,'), ('standIns = true,', 'standIns = false,'),
             ('budgetSeconds = 22,', 'budgetSeconds = 80,'), ('restartTerrain = false,', 'restartTerrain = true,')):
    assert a in s, a
    s = s.replace(a, b, 1)
for pat in ('Terrain.WaterColor =', 'Terrain.WaterTransparency =', 'Terrain.WaterReflectance ='):
    s = re.sub(r'^(\s*)(' + re.escape(pat) + ')', r'\1-- (v9: left as set in Studio) \2', s, count=1, flags=re.M)
open(f'{ROOT}/import/terrain_only.luau', 'w').write(s); print(len(s))
