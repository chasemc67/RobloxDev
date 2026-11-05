# H9 emissive dim (30%) — task for Claude Code on the PC
Working dir: C:\lg_h9dim\models (a copy of lantern-grove/models with fbx/ and _src/h9dim/).
1. Run: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python C:\lg_h9dim\models\_src\h9dim\h9dim.py -- C:\lg_h9dim\models
   (log to C:\lg_h9dim\blender.log).
2. If it errors (Blender 5.2 API differences, e.g. EEVEE engine name, compositor), make the minimal fix to h9dim.py and rerun. Do not change what is dimmed (Glow/Firefly/ShroomGlow base+emission x0.7 in sRGB) or the output names.
3. Check _src/h9dim/h9dim_report.json: every prop has dims_match true and non-empty "dimmed". Check preview_raw.png exists and top row (before) is visibly brighter than bottom row (after).
4. Write a 5-line result to C:\lg_h9dim\RESULT.txt (OK/FAIL, any script fixes). Only one Blender at a time. Touch nothing outside C:\lg_h9dim.
