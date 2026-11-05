# SRV-132 H6 + H11 movers pass 3
ALL PASS against holes_rev.json, the source of truth. Both input JSON files and protected library remain unchanged. Six FBX round trips pass counts, bounds, origins, material merge and budgets.

| Prop | Hole-local export pivot | World pivot | Tris | MeshParts | Minimum |
|---|---|---|---:|---:|---|
| h06_sluice_gate | [0, 0.0, -28.0] | [280.0, 26.0, 227.0] | 300 | 4 | 0.150000007 / pocket_w19 |
| h06_sluice_frame | [0, 0, -28] | [280.0, 26.0, 227.0] | 476 | 3 | 0.050000143 / pocket_e23 |
| h11_lock_gate | [0, 0.0, -21.25] | [150.0, 116.0, -273.25] | 180 | 4 | 0.149999952 / rail4__cut1__cut0 |
| h11_lock_lift | [0, 0, -25] | [150.0, 116.0, -277.0] | 276 | 3 | 0.149999976 / rail5__cut1__cut0__cut1 |
| h11_lock_chamber | [0, 0, -23] | [150.0, 116.0, -275.0] | 1684 | 6 | 0.100000024 / rail4__cut0 |
| h11_quay_lip | [0, 3.5, -25.45] | [150.0, 119.5, -277.45] | 72 | 2 | 0.149999999 / rail6__cut0__cut2 |

Derived from revised blocker thickness .636; existing face bands lie within that envelope.
East post lower end y=2.6 clears revised pocket top y=2.55; x=3.98 unchanged. Wheel centre y=3.3, tie centres y=2.75 clear new pocket walls.
Re-pivoted to north hinge [0,0,-25]; full deck 3.2 x 3.35 centred z=-23.325, south strip removed. Red #B83A35 / cream #FFF0C9 bands .6 along x on transverse edges, .6 along z on side edges, .18 wide fascia; final renders provide readability review.
Face bands and iron inlaid inside exact .5 blocker depth to preserve .15 cut clearance.
Support/wheel x moved +/-3 to +/-4.8 to clear revised funnel backing. Signal housing centre [0,5.9,-26], size [.8,1.2,.3]; lamps [0,6.18,-25.8] and [0,5.62,-25.8]. Slot cheeks width reduced 3.9 to 3.3 to clear approach guides.
Exact revised 3.6 x 1.5 x .2, top y=5 raised / y=4 lowered. Six .6 alternating x bands #B83A35/#FFF0C9. FBX bottom-centre pivot [0,3.5,-25.45] is [0,-.75,0] offset from holes_rev centre pivot [0,4.25,-25.45].

H11 cycle 10.6 s: gate down dwell 4.85, rises 4.85-5.5, up dwell 4.45, lowers 9.95-10.6. Lift rise 5.5-7.5, tilt/release 7.5-7.65, return 7.65-9.15, north hinge tilt 4 degrees.
Lip finite-speed interpretation: speed 10 requires .1 s transitions. Sink 7.4-7.5; top is exactly y=4 only in [7.5,7.65); rise 7.65-7.75. motion.lua and sweep use this same schedule.

Approved cut targets include revised split descendants; no additional cut volumes added. Residual cut-target clearance >=.15; other non-contact pairs >=.05; H6 gate/east post >=.15. Static support felt contacts are explicit in certificate.
Overall minimum: {"prop": "h06_sluice_frame", "obstacle": "pocket_e23", "clearance": 0.050000143051147417, "time": 0.0, "offset": 0, "tilt": 0, "location": [3.696666638056437, 2.616666873296102, -27.71666665871938], "kind": "rail/wall", "residual_cut": false, "status": "PASS"}

Validation: fitcheck_movers_pass3_validated.txt (overall/per-prop minima and locations); fitcheck_results_pass3.json. Triangle/OBB SAT conservative separation, full-cycle .005 s samples and explicit tilt sweep.
Final Cycles OptiX renders: out/previews/cycles/final/<prop>_{rest,max}_{eye,34}.png, actual H11 tee rest/max, contact_sheet.png. Sequential process-gated Blender launches, 30 s polling when busy.
All six FBXs rebuilt. Re-sync exports with their manifest pivots; decorative meshes CanCollide=false, gameplay collision derives from revised JSON.