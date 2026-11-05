# SRV-132 H6 + H11 movers pass 1 — DRAFT / FITCHECK FAILED
Five props built reproducibly under out. No manifest.json or library file modified. Decoration meshes: CanCollide=false. Import FBX at scale 1, forward -Z / up Y, textures embedded.
| Prop / FBX | Hole-local pivot | World pivot | Tris | MeshParts |
|---|---|---|---:|---:|
| fbx\h06_sluice_gate.fbx | [0, 0.0, -28.0] | [280.0, 26.0, 227.0] | 300 | 4 |
| fbx\h06_sluice_frame.fbx | [0, 0, -28] | [280.0, 26.0, 227.0] | 476 | 3 |
| fbx\h11_lock_gate.fbx | [0, 0.0, -21.25] | [150.0, 116.0, -273.25] | 180 | 4 |
| fbx\h11_lock_lift.fbx | [0.0, 0.0, -23.0] | [150.0, 116.0, -275.0] | 312 | 4 |
| fbx\h11_lock_chamber.fbx | [0, 0, -23] | [150.0, 116.0, -275.0] | 1684 | 6 |

H6 slide axis +X, range -7..0, speed 3, dwells closed 1.2/open 2.0, phase 0. Exact period 7.8666667 (source rounds to 7.8667).
H11 gate axis +Y, range -1.3..0, speed 2, dwells open 5.5/closed 2.8, phase -1.3, period 9.6.
H11 lift: 3.2 x 4.0 timber deck, 0.15 thick below its top-center pivot, rise 4 at 2 studs/s; tilt 4 degrees toward north around the north edge z=-25 on Roblox -X (raises the south edge). Return 1.5 seconds. Draft schedule begins rise at t=5.45 while gate is still closing and returns by t=8.95. This is explicitly not approved synchronization.
Signal at [0,5,-25.4], world [150,121,-277.4]; separate h11_lock_chamber__SignalRed and __SignalGreen Neon MeshParts. Optional Studio PointLight range 6, brightness 1, appropriate color; green when gate down, red otherwise. Red/green are separate toggle materials; no Blender light is exported.
Workbench eye camera height 5 studs; five-stud capsule; eye and 3/4 views per prop and contact_sheet.png. Blend sources and mesh triangle/component caches included.

## Validation
Read fitcheck_movers_pass1_failed.txt for full swept minima, times, offsets and locations. Fine sampling uses dt<=0.005 s, <=0.015 stud translations, <=0.134 degree return tilt, with a separate <=0.25 degree top tilt sweep. Triangles versus oriented source boxes use SAT signed separation lower bounds, not exact Euclidean distances. Base primitives are conservative AABBs. Bank slope checks use conservative enclosing boxes. Threshold 0.05; no contact exemptions.
| Prop | Obstacle class | Minimum signed lower bound | Time / offset | Location |
|---|---|---:|---|---|
| h06_sluice_gate | rail/wall: rail5 | -1.500000 | 1.6343 / -1.3029 | [-2.3695891730313785, 0.6666666666666666, -28.300025403499603] |
| h06_sluice_gate | felt: felt_neck | -0.000500 | 0.0000 / 0.0000 | [1.0666666825612385, 0.3333333333333333, -28.300016939640045] |
| h06_sluice_gate | cup: cup | 16.182000 | 0.0000 / 0.0000 | [-2.6000001430511475, 0.350000003973643, -28.311999986569088] |
| h06_sluice_gate | tee: tee | 26.680000 | 0.0000 / 0.0000 | [-2.4650001525878906, 0.6533333559830984, -27.686666667461395] |
| h06_sluice_gate | base_primitive_AABB_conservative: h06_sluice_frame_0 | -0.597084 | 1.4344 / -0.7032 | [-1.7698433026374776, 1.0, -28.10001693169276] |
| h06_sluice_frame | rail/wall: rock18 | -0.200000 | 0.0000 / 0.0000 | [3.316666523615519, 0.016666730244954426, -27.71666665871938] |
| h06_sluice_frame | felt: felt_neck | 0.300000 | 0.0000 / 0.0000 | [-3.316666523615519, 0.016666730244954426, -27.71666665871938] |
| h06_sluice_frame | cup: cup | 15.640000 | 0.0000 / 0.0000 | [-4.577038923899333, 3.1754328409830728, -28.71333332856496] |
| h06_sluice_frame | tee: tee | 26.310000 | 0.0000 / 0.0000 | [-10.5, 1.4750000635782878, -27.356666664282482] |
| h11_lock_gate | rail/wall: rail4 | -0.200000 | 0.0000 / -1.3000 | [-1.7999999523162842, -0.4999999682108562, -21.166666666666668] |
| h11_lock_gate | felt: felt_lock | -0.518000 | 5.8400 / -0.6200 | [-1.0000000198682149, 0.1600000707308448, -21.51800000667572] |
| h11_lock_gate | cup: cup | 20.982000 | 0.0000 / -1.3000 | [-1.2000000476837158, -0.519999929269155, -21.50600000222524] |
| h11_lock_gate | tee: tee | 19.980000 | 0.0000 / -1.3000 | [-1.3599998950958252, -0.519999929269155, -20.986666684349377] |
| h11_lock_gate | base_primitive_AABB_conservative: h11_lock_chamber_29 | 0.090000 | 0.0000 / -1.3000 | [-1.3599998950958252, -0.519999929269155, -20.986666684349377] |
| h11_lock_lift | rail/wall: quay_rail20 | -0.500000 | 7.4500 / 4.0000 | [-1.600000023841858, 3.9499999980131784, -24.666666666666668] |
| h11_lock_lift | felt: felt_lock | -0.070500 | 5.4900 / 0.0800 | [-0.5333333412806193, -0.020000003973642915, -24.50250005722046] |
| h11_lock_lift | cup: cup | 17.220974 | 7.4500 / 4.0000 | [-1.600000023841858, 3.973373953419735, -24.944647205770707] |
| h11_lock_lift | tee: tee | 20.000000 | 0.0000 / 0.0000 | [-1.5499999523162842, -0.09166666368643443, -21.016666650772095] |
| h11_lock_lift | base_primitive_AABB_conservative: h11_lock_chamber_28 | -0.150000 | 0.0000 / 0.0000 | [-1.600000023841858, -0.10000000397364299, -21.833333333333332] |
| h11_lock_chamber | rail/wall: rail4 | -0.420000 | 0.0000 / 0.0000 | [-2.7799999713897705, 0.009999990463256836, -21.193333347638447] |
| h11_lock_chamber | felt: felt_approach | -0.000500 | 0.0000 / 0.0000 | [-1.9500000476837158, -0.4666666587193807, -20.836666584014893] |
| h11_lock_chamber | cup: cup | 16.950000 | 0.0000 / 0.0000 | [-0.373333344856898, 4.426666736602783, -25.52333339055379] |
| h11_lock_chamber | tee: tee | 19.810000 | 0.0000 / 0.0000 | [-1.9500000476837158, -0.4666666587193807, -20.836666584014893] |

## Conflicts requiring source/design decisions
- H6 board at bottom-center felt pivot has zero felt clearance. Its exact 7-stud pointed board crosses unbroken rail5 and the specified west frame post; pocket/track apertures are absent from source boxes.
- H11 gate intentionally sinks through the lock felt and touches/overlaps chamber rails at its edges. Strict clearance cannot pass with an uncut felt and unaltered rails.
- Lift top flush at rest means zero felt clearance and its thin body occupies the felt thickness. Lock felt must be replaced or visually masked by the moving platform; exit rail requires a designed opening.
- A 3.5-second rise+return does not fit a 2.8-second fully closed dwell. Need a timing decision before approved Lua synchronization. North-edge hinge selected so south edge rises toward north downhill release.
- Static foundations contact source felt and specified winches overlap rail geometry. Required 0.05 separation conflicts with mounted bases.
- H6 exact blocker union is 7.000051 long due to rounded source .4243 end boxes. Painted skins project .018 beyond blockers. H11 source blocker fully covered; platform plank gaps .005. Mesh visual versus blocker differences are decorative only.

## Render and handoff status
ALL PASS has not been reached. No passing certificate is fabricated. Final Cycles OptiX renders are conditional on ALL PASS and were not run. render_pc.py supports blend/FBX inputs and rest/max states; refuses final rendering without a passing certificate, and refuses CPU fallback if OptiX is unavailable.
Do not import these as validated final movers. Studio calibration still required: H11 ball release clamp(entrySpeed*0.5,1.5,7), exact maximum 7 for the ace. H9/H14/H17 untouched.