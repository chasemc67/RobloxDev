# Sugarloaf Canyon models — pass 5 (gondola + 0.15 fitcheck + staged V1 hero render)
Working dir: C:\Users\chase\sc\sugarloaf-canyon (models\ = kit). Read models\README.md, models\_src\pass2_summary.md, pass4_summary.md, sclib.py, sc_pieces.py, sc_build.py, sc_fitcheck.py, render_hero.py first and reuse them.
Log every step with a timestamp to models\_src\PROGRESS.md. Write models\_src\pass5_summary.md at the end and create models\_src\pass5_done.flag (or pass5_failed.flag with the reason).

HARD RULES
- Blender 5.2 headless ONLY via models\_src\run_blender.ps1 (it waits for other Blender processes). Exactly one Blender at a time. Never restart the PC. Don't kill Blender processes you didn't start.
- Back up any file before overwriting it (copy to models\_src\backup_pass5\). manifest.json, layout.json, README.md and contact_sheet.png are already backed up there, but back up anything else you change.
- Do NOT create collision meshes/FBX. Don't change existing FBX, cliffs, terrain, or props. Never hand-edit exports; add generator code.
- Every mesh < 20k tris; low-poly Roblox style; existing palette/materials. 1 Blender unit = 1 stud, FBX forward -Z, up Y, scale 1, embed textures, pivot rules from README. One MeshPart per material, named <part>__<Material>.
- holes.json is the source of truth over world.json/course.md.

TASK 1 — Sunset Gondola cable + cabin
- world.json lifts "Sunset Gondola": bottom [130,18,540] (Junction), top [-420,190,136] (Sunset Point), straight cable, 6 studs/s, seated enclosed cabin. Stations in layout.json: gondola_station at (-420,190.1,128) yaw -126.84 and (132,18,544) yaw 53.53, "open end + bull wheel face along the cable". The 3 cableway_trestle instances at x=-330 are the OLD ORE cableway (H14 area), NOT on the gondola line; don't use them as supports unless they truly lie on the line (verify and state it).
- Derive the actual bull-wheel/cable attach points from the exported gondola_station geometry (both stations, placed). Build `gondola_cable` as a world-placed static piece: two parallel haul ropes (up/down line, spacing to suit the cabin hanger) with a gentle catenary sag (state sag value), low tri tubes (6-sided), Iron/Licorice material, CastShadow off note. If one span > ~700 studs looks implausible, you MAY add intermediate support towers as part of `gondola_cable` only if they clear every hole/walkway; otherwise free span. Pivot: world origin of the line start, documented.
- Build `gondola_cabin`: seated enclosed low-poly candy-style cabin (~6w x 7h x 6d studs for 2-4 seated players, adjust to station opening), hanger arm + grip on top, windows (Window material), PepRed/MintWhite stripes allowed (it moves). Pivot at the cable grip point (moving part). Separate hanger and body meshes per material.
- Export both to models\fbx\, textures embedded, add pieces to manifest.json (bbox, tris, materials, pivot, motion: travel along cable from bottom to top at 6 studs/s, parametric formula for position at t along the catenary) and instances to layout.json (cabin: one instance at the bottom station boarding point plus document the travel path). Update README.md and models\_src\pieces_table.md.
- Reimport check: re-import each new FBX into a clean Blender scene and verify tris, bbox, material names, scale 1, axes; write models\_src\reimport_pass5.txt.
- Previews: eye-height (5 studs, with reference capsule) + 3/4 views for both pieces in models\previews\ using the existing naming (<id>_eye.png, <id>_34.png); one view of the whole span with both stations; regenerate models\contact_sheet.png including the new pieces.

TASK 2 — Full-kit fitcheck vs current holes.json at 0.15 clearance
- Extend sc_fitcheck.py (new script models\_src\sc_fitcheck_holes.py is fine) to test EVERY placed instance's exported triangles (refresh the tri cache for new/changed pieces) against each hole's play area from holes.json, transformed by world_offset/world_yaw (check holes.json schema & world.json placement convention for direction): felt pieces (with slope), walls/rails (full 3D boxes), cup + flag, tee, drops, hazards, moving_parts swept ranges, teleports. Fail any triangle within 0.15 studs (3D) of a felt/rail/cup volume, or inside the vertical play column above felt (felt y up to +8 studs) within 0.15 XZ. Also keep the existing walkway head-clearance and footprint checks. Include the gondola cable+cabin (cabin swept along its full path).
- Output models\fitcheck_pass5.txt, and if ALL PASS copy to models\_src\fitcheck_pass5_validated.txt. List every intrusion: piece, instance, hole, element, min distance, location. Do NOT move or delete pieces to fix intrusions; just report them.

TASK 3 — one staged hero render (render-only, don't change kit geometry)
- Shot `V1-hub-tee1`: from the H1 tee area at Sugarloaf Junction looking at Old Sugarloaf, framed to match the old_sugarloaf_skyline concept (see models\previews\hero\compare_vs_vistas.png, left/concept panel for V1; also the vista images referenced in pass4_summary). Start from render_hero.py (back it up; write render_hero_pass5.py rather than editing in place).
- Stage the hole greens and rails visible in frame from holes.json (felt as green felt lanes with a slight felt texture, rails as timber/candy rails, cups/flags) — render-scene-only geometry.
- Light: low warm sun (~5-10° elevation from the west, bearing ~277), orange rim light, peach-to-violet sky gradient. Cycles OptiX, 1920x1080, 128 samples, denoised.
- Save models\previews\hero\V1-hub-tee1_staged.png and models\previews\hero\V1-hub-tee1_vs_concept.png (side by side, labeled). Don't rework cliffs/ground/props.

If you hit a usage limit or a blocker, stop, write pass5_failed.flag with the reason, and exit. Don't use Codex.
