## Import scale note

The FBX header reports UnitScaleFactor 100 (metres): that is what Blender writes for unit system NONE + FBX_SCALE_UNITS.
The vertex values are already studs (a re-import into Blender gives 1:1 sizes). In Studio's Import 3D dialog,
**set the scale unit to Stud** (or check that `lantern_large` comes in 2 studs tall). If a prop comes in 3.57x too big,
the importer treated the file as metres: re-import with Stud, or scale the model by 0.28.

## Deviations from props.md (and why)

- **Mill wheel pivot**: matches holes.json (the collision source) and the corrected props.md (2026-10-09): axle
  centre (7.5, 3.6, -8.5), axis +Z, **2** opposed paddles. The axle runs 12.2 long, from the north bearing
  trestle (outside rail5) into the mill-house wall, so the bbox z is 12.2.
- **Water mill position**: the anchor [7.5, 0, 0] would overlap the millrace hazard and rail2. The house sits at
  x 4.2..12.8, z -1..7 (placement [8.5, -1, 3]), just behind the millrace, and the axle enters its north wall.
- **Hollow tree footprint**: H9's chamber + heart rails span 19 x 37 studs, which won't fit inside a 34-stud round
  trunk. The trunk is 31 x 46 (superellipse) and the canopy spreads to about 49 x 59. Height is 57 (target 60).
  The origin is at [23, -1, -36] (anchor x 22). The tunnel opening, root gate and south window line up with
  holes.json (see `previews/assembly_h09_top.png`).
- **Carousel bar** (9 x 3.7 x 3.2) and **lantern bar** (6 x 3.1 x 1.1): props.md gives the swept / blocker sizes.
  The arms/beam match the blocker boxes exactly. The puffballs, hub cap, upper arm and lanterns sit above the ball.
- **Lantern post** bbox x 1.3: the arm that holds the lantern is included.
- **Firefly ring entry** is 4 x 4.1 x 4.8 (target 3 x 4 x 4). The arch feet are pushed onto the alcove end-rail line
  so nothing visual stands on the felt.
- **Trunk tunnel arch** z 9.2 (target 8): it needs a clear 7-wide opening plus rib feet on the rail lines.
- **Root bridge** y 3.4 (target 3): the arch roots dive into the banks.
- Extra props not in props.md but listed in the hole notes: `h8_root_door` (moving), `h6_wheel_trestle`,
  `h9_lantern_post_static`, `stump_cladding`, `toadstool_stool`, `bank_backing_stone`, `drop_face_stone`,
  `root_arch_large` (H8 "hollow-tree base & arching roots"), `heart_lantern_cluster`.

## Known issues / TODO

- The H6 wheel rims and paddles pass through the north visual rail (rail5) at x 5..10. Cut a notch there, or stop the
  visual rail at the wheel (collision is unaffected).
- Moving-part pivots depend on the importer keeping the FBX origin; set PivotOffset from `parts[].bbox_center_from_origin` if not.
- Waterfall sheets are meshes (Water + Foam ribbons). For animated water, hide them and use Beams/ParticleEmitters
  along the same lines.
- Lantern glow is a Neon core inside an opaque paper shell. It needs a PointLight (and/or Paper transparency 0.15)
  to read as lit. The previews show paper with a slight emission.
- Rail-kit pieces stretch along Z, and since pass 2 the limestone block texture stretches with them. Repeat
  `rail_straight_4` every ~4 studs on long runs (the assembly previews do this).
- `tee_sign_hNN` uses Lilita One (SIL OFL) for the numbers, and `welcome_sign` uses it for its lettering.

## Pass 2 notes (dressing + textures)

_Superseded in pass 4 where noted: dressing is now world-placed on terrain-4stud.json, checked against the real
walkway polylines, and budgeted for Quest (see "Set dressing" above and the pass 4 notes below)._

- **Dressing ground height**: `pos.y` comes from a preview-only stepped ground (nearest felt top - 0.6, under water
  surface - 0.5). Terrain in Studio will differ, so raycast each instance down onto Terrain (see the dressing section).
  Trees sink 0.1 and small props 0.04 into that ground, and the root flares reach 0.3 below their origin.
- **Neighbouring holes share space**: layouts are checked in world space against every hole, so each hole's dressing
  never touches another hole's felt, rails or walking path. The holes are packed closely (H4/H5/H6/H7), so H6 has
  few trees of its own. Its tee view is framed by H4/H5/H7 dressing, and the previews draw neighbours' dressing too
  (snapped onto the previewed hole's ground).
- **Walking paths** are modelled as straight 5-stud corridors from each cup to the next tee. If the real paths
  curve, re-run `dressing.py` after adding them to `dressing_lib.build_keepouts`.
- **Overhead clearance** is 6.5 studs above any felt or path (lantern spans, overhanging maples). That is enough for
  a 5-stud VR player plus a raised putter. Raise `dressing_lib.CLEAR` if playtests show people hitting lanterns.
- **Triangles**: dressing runs 80k-200k tris per hole. Imported as instances, it renders as a few dozen unique meshes.
  The merged `dressing_hNN_*` groups don't instance, so prefer instances in production. They also cull worse.
- **Textures**: box projection leaves visible seams on curved shapes, such as where a texture changes axis on a trunk.
  At these texel sizes that's acceptable for a stylised look. Foliage is a 2D leaf pattern, not leaf cards, so canopies
  stay chunky low-poly blobs.
- **Preview look** (golden-hour sun, haze, glare) comes from the Blender renders. Match it in Studio with the
  course.md Lighting/Atmosphere/Bloom values.


## Pass 4 notes (world placement, Quest budget, art-director fixes)

- **World placement**: dressing positions come from `dressing_world.py` (world.json placements), not holes.json
  `world_offset`. Ground heights are bilinear samples of `../world/terrain-4stud.json`. If Studio Terrain is built
  differently (smoothing, the felt Air carve), raycast down from `world_pos + (0, 20, 0)`.
- **Budget first**: the near field of the packed holes (H5-H8 sit within 11-60 studs of each other) is shared, so
  those holes keep fewer trees of their own. Their views are framed by the world pieces (tree roots, cliff kits,
  falls), neighbours' dressing and card treelines. Raise `NEAR_BUDGET` in `dressing_world.py` if Quest profiling
  allows it.
- **Cards**: `treeline_card_red/_gold` need an alpha-cut texture in Studio (SurfaceAppearance AlphaMode =
  Transparency, or MeshPart.TextureID). Their back faces are real geometry, so DoubleSided is not needed. Set CastShadow off.
- **Felt** (`textures/felt.png` + `felt_normal.png`): softer and slightly darker, with a faint nap running along
  each felt piece's long axis. Use a SurfaceAppearance with ColorMap = felt.png and NormalMap = felt_normal.png on
  Fabric so slopes catch the light.
- **H9 interior**: `hollow_tree_world_shell_part8.fbx` adds 18 low lantern clusters and 24 glowing mushroom clumps
  along the inner wall. Add PointLights at `manifest.world.h9_interior_lights` (30 spots; Range/Brightness in the note).
  H9 dressing adds floor-level glowing mushrooms, ferns and toadstools inside the ring.
- **Previews**: `assembly_world.py` renders over a preview-only terrain mesh with 4-stud cells, so slopes look
  faceted and water cells look stepped. Studio Terrain will be smooth.

## Pass 5 notes (playtest review: dark holes, lane clutter, moving-part colours)

- **Dark holes H8/H9**: use `hole_skins` (above). The felt Parts get `FeltBright` (`#6CBF4C`, Fabric,
  SurfaceAppearance ColorMap = `textures/felt_bright.png`, NormalMap = `felt_normal.png`), and the rails use the
  `rail_*_trim` kit (light stone + cream cap) so the lane edge separates from the bark floor. Add the
  `spot_lights[]` PointLights (pooling over the H8 door, H9 gate, H9 lantern bar and both cups) and a PointLight on
  each `cup_lantern_stake` Neon core (Range 10, Brightness 2, `#FFC873`).
- **H6**: `rail_*_mill` kit (dark blue-grey MillSlate blocks + painted MillBlue cap), so the mill hole reads as a
  different place from H5/H7.
- **Moving parts**: MoveRed/MoveCream bands. If Studio lighting makes the cream glare, drop MoveCream to `#F2E4C4`.
  Keep both colours off static props, so red-and-cream always means "this moves".
- **Lane clearance**: no dressing prop taller than 2 studs within 3 studs of any rail (footprint, and everything below
  eye height). When hand-placing extra props in Studio, keep to the same rule; short ground cover (grass, ferns, small
  bushes, the cup lantern stakes) may still sit by the rails.
