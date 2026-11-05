# Aurora batch 3 REV 2 (only two assets). Same HARD RULES as brief_batch3.md / brief_rev1.md. Do NOT launch Blender. Back up gen_batch3.py -> gen_batch3_rev1.py, build_batch3.py -> build_batch3_rev1.py.
1. h18_halo_arch: tube about 2x thicker than rev1 (measure the current cross-section and double it), faceted/bevelled cross-section (8-12 sided with chamfered
   edges = thick faceted ice ring), Ice outer, plus a lighter inner edge (IceCore or a new light material 'IceFrost' #E6FBFF Glass) along the inside of the ring.
   Keep the FEET EXACTLY where they are (same foot footprints/positions as rev1). Gates: < 3000 tris; 8-stud head room over ALL felt (nothing between felt top
   and felt+8 above any felt) and >= 0.15 plan clearance otherwise; tee-eye(5.5)->flag-top sightline clear. If the thicker tube breaks head room, raise the
   crown or widen the span above the feet while keeping the feet. Report: min vertical clearance of the arch above felt (felt top -> arch underside) over every
   felt it crosses, and over the ball path (the ace/ball path line from tee to cup through the hole, use ai_waypoints if present else tee->cup straight segments).
2. h06_kettle_pool: remove ALL Steam geometry from the mesh (steam will be particles). Keep everything else identical.
3. build_batch3.py: add an --only id1,id2 argument (read from sys.argv after --) so ONLY those FBXs/previews are exported and re-imported (fbx_validation for them);
   all other FBX files must stay byte-identical. Still write full triangles.json/build_report.json for all parts (scene geometry from parts.json) so the fitcheck runs on all 23.
4. fitcheck_batch3.py: add per-asset 'head_room_min_over_felt' (min of underside - felt top for geometry over felt, or 'none over felt') and for h18_halo_arch
   'ball_path_vertical_clearance'. finalize: update manifest, fitcheck file, summary.md (rev2 section), sheet05.
Run gen + preflight until ALL PASS; print h18_halo_arch and h06_kettle_pool tris and the numbers above.

## Game Art Bot update (overrides item 1 detail): thicken the tube OUTWARD and UPWARD only. The INNER opening (inner edge profile of rev1) stays exactly the
same size/position, so head room and ball-path clearance do not get worse. Feet stay in place (inner faces fixed; extra thickness goes to the outside).
Report the inner-edge max deviation vs rev1 (should be ~0).
