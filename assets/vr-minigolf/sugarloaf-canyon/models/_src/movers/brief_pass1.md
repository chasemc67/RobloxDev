# SRV-132 partial H6/H11

Authority: in/holes.json, holes[5] sluice_gate; holes[10] lock_gate and lock_lift ride. Review approves H6 and H11 only. Other movers excluded.

Generate five separate source-centered FBXs: h06_sluice_gate, h06_sluice_frame, h11_lock_gate, h11_lock_lift, h11_lock_chamber. Import unchanged sclib/lglib; reference existing course textures and sc_build export conventions. All writes under out. No manifest.json edits.

Source coordinates convert Roblox (x,y,z) to Blender (x,-z,y). One MeshPart per material, decoration only, texture-embedded FBX scale 1, forward -Z/up Y. Bands restricted to movers. Static concrete uses unbanded cream.

Fine triangle/OBB swept fitcheck, static primitive envelopes, source felt/walls/rails/cup/tee. No implicit contact or pocket exemptions. Workbench views with five-stud reference capsule. Cycles OptiX script and conditional final rendering only after ALL PASS.

Known specification conflicts must remain visible: H6 continuous west rail/post through gate path, H11 uncut felt/rail interfaces, and lift rise+return exceeding fully closed dwell. Do not alter gameplay source or invent a passing report. Draft synchronization and conservative clearance bounds must be labeled.
