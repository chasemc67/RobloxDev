# Stage fx1 (Claude Code): felt seams near the cup, all three courses

Status: **PASS.** The dark felt seams are gone on every hole of all three courses, and the cup area now reads as the same felt as the green around it.
- **Published:** Lantern Grove **v32**, Sugarloaf Canyon **v109**, Aurora Archipelago **v17**. Lobby is still **v251**.
- **Gameplay colliders:** identical to the published versions on all three courses: LG 396/396, SC 736/736, AU 615/615. No collider was changed, so no roll tests were needed.
- **Cups:** 27/27, 54/54, 54/54. 0 stuck, 0 escapes, 0 timeouts.

Chase's report: "A bunch of the holes have this weird gap now near the hole." His screenshot `fx1-chase-report-lg-h1.png` (Lantern Grove H1) shows a dark lengthwise seam beside the cup strip, a cross seam at the end of the strip, and a cup square that looks like a separate raised tile.

## 1. Root cause
**`VisualSeparation.luau`, protected-felt pass (zf1), applied identically in all three live places.**

`script-diff.md`: VisualSeparation is the same in LG v25, SC v103 and AU v13. CourseBuilder drift (the sc12 `cframe` piece) doesn't touch felt skins.

How the rule worked:
- Every playing-surface collider whose path ends in `.Felt` is hidden.
- A noncolliding copy, `ZF1VisualLayers.Visual_Felt`, is drawn in its place.
- That copy was shrunk **0.08 on every X/Z edge**: `Size = base - 2*GAP`, GAP 0.08, VisualSeparation line 228.
- The rule never asked whether the edge was the outside of the green or a joint with the next felt piece.

The cup builder makes many joints near the cup:
- `CourseBuilder.buildCupPiece` splits the flat piece holding the cup into up to four felt strips around a 2.2 × 2.2 CSG **`CupPlate`**.
- `cutNeighbourCup` splits a neighbouring slab into three parts when the cup is near its edge.

So every joint near the cup got a gap:
- **Felt to felt:** 0.08 + 0.08 = **0.16 stud** gap.
- **Felt to CupPlate:** **0.08** gap. The CupPlate is a CSG union, which the box pass skips, so it kept full size.
- The felt collider under each gap is transparent, so the gap shows the hole's **Base block** (WoodPlanks #5B3A22, dark brown). That's the dark line.
- Each inset skin also shows its lit 0.4-tall side faces along the gap. That made each piece look like a separate bevelled tile.

Lantern Grove H1, measured in place (`fx1-before-lg-h1.png` top-down, `fx1-lg-h1-cup-closeup-before.png` at Chase's angle):

| Piece (collider, x × z) | Visual skin | Joint |
|---|---|---|
| main 11.9 × 12 | 11.74 × 11.84 | 0.16 gap to the cup column at x = 181.6 (the long seam) |
| cup column south 2.2 × 8.4 | 2.04 × 8.24 | 0.08 gap to the CupPlate at z = 142.4 (the cross seam) |
| CupPlate 2.2 × 2.2 (union) | not resized | — |
| cup column north 2.2 × 1.4 | 2.04 × 1.24 | — |
| wall strip 0.4 × 12 | 0.24 × 11.84 | — |

Two further defects in the same pass:
- **CSG felt was resized too.** On SC H16, the `CupCut` felt union's skin was scaled down, and that scales its cup hole.
- **Narrow strips re-centred.** A strip that fell under the 0.2 minimum width re-centred over its neighbour, and the overlap solver then pushed it up to 0.47 sideways (SC H11 lock quay).

## 3b. Cup strip look
Checked with macro shots: `fx1-exp-macro*.png`, `fx1-exp-u-*.png` (temporary test parts, removed), `fx1-exp-rot*.png` (temporary rotation, restored exactly).

- **LG:** the cup-area felt already matches the adjoining main felt in every property. Same Color, Fabric, no MaterialVariant, no Texture, same part orientation (grain).
  - The CSG CupPlate shows the same Fabric grain and scale as a Part.
  - A 90° grain test showed the strip Parts already run the same way as the main felt.
  - The "lighter strip with other-way grain" was the lit side faces and dark gaps around each inset tile. It disappears when the joints are flush (`fx1-lg-h1-cup-closeup.png`).
- **SC:** **all 18 CupPlates were missing the tinted `FeltNap` texture** that every SC felt part carries, because `SubtractAsync` drops children. The H16 cut felt was missing its `SlopeFelt` chevrons for the same reason. All 19 now carry their felt's texture.
- **AU:** plain Fabric like LG. 0 cup pieces differ.
- **After, on all three courses:** every cup-area piece matches its adjoining felt in colour, material, variant, textures and grain. Scan: `cupPiecesDiffering` 0/0/0.

**For Game Art Bot sign-off:** `fx1-lg-h1-cup-closeup.png` and `fx1-lg-h1-cup-closeup-before.png` (eye height 4, about 6 studs from the cup, Chase's angle). There's also an SC pair: `fx1-sc-h1-cup-closeup(-before).png`.

## Fix (src, pushed, in place via `CourseBuilder.ApplyVisualSeparation(<course root>)`)
`src/ServerStorage/VisualSeparation.luau`:
1. **Flush joints.** A felt skin edge is inset 0.08 only if no other visible playing surface (felt, CupPlate) continues past it at the same height. A continuing edge stays on the collider joint with a **0.001 setback** (`FLUSH`).
   - The setback keeps a joint from ever becoming a coplanar overlap. At SC's z ≈ −4560, float32 rounding made exactly-flush edges overlap by 0.0002, and the z-scan flagged 60 of those.
   - A joint hidden under a rail/cap block keeps the old inset, so rails don't have to move off a newly flush felt top.
2. Overlapping felt is trimmed **to meet** its neighbour (FLUSH), not to 0.08 apart.
3. When a felt skin's side face is coplanar with another felt's face, it pulls in **on that side only** (it used to translate the whole skin, which reopened the other joint).
4. A narrow strip regains the 0.2 minimum from its insets, so its flush edges stay put.
5. **CSG felt is never resized**, so cup holes keep their exact size.
6. The fix report now lists what each conflict was against (`against`).

`src/ServerStorage/CourseBuilder.luau`:
- `buildCupPiece` gives the CupPlate the felt look via `slopeFelt` (SC FeltNap).
- `cutNeighbourCup` copies the strip's Texture/Decal children to the cut union.
- New `CourseBuilder.MatchCupFelt(course)` is the in-place equivalent: largest felt Part with the same PieceId and tilt; idempotent. `ApplyVisualSeparation` runs it first (`report.cupFelt`).

Colliders never change: VisualSeparation asserts that every collider's CFrame, size, flags and physics are unchanged. The cup hole, CupLiner, CupBottom and cup drop are untouched.

## Per course
Seam scan (`tools/fx1_seams.luau`, via `tools/fx1_stage.py seams`):
- It samples every edge of every visible playing-surface collider top every 0.1 stud.
- A sample is an **interior seam** when the point 0.006 inside the collider edge has no visible felt top over it but another surface continues past the edge. That means a gap wider than 0.005.
- Mesh/CSG bounding boxes don't count as cover. The first version did count them, and one dressing mesh hid every SC H1 seam.
- Outer edges and felt-to-mesh joints (hidden colliders rendered by an imported mesh, e.g. AU H17's light bridge) are reported separately.
- LG numbers below are from the final scanner, run on copies of the downloaded v25/v32 files. SC and AU "before" counts came from the second scanner version, which also counted felt-to-mesh edges as interior.

| | LG (9 holes) | SC (18) | AU (18) |
|---|---|---|---|
| Open place vs published | v27 save = v25 content (parts + 59 scripts identical) | v104 = v103 | v15 = v13 |
| Holes with seams before | **9/9** | **18/18** | **18/18** |
| Interior seam samples before → after | **8821 → 0** | **22489 → 19** | **24947 → 24** |
| Worst holes (samples before) | H8, H9, H4 | H16 2037, H8 1952, H11 1946 | H6 4333, H7 2169, H18 1639 |
| Collider-level gaps (pre-existing, under bank backing/rails) | 15 → 11 (H3, H9) | 7 → 5 (H18) | 6 → 2 (H18) |
| Cup pieces differing from main felt | 0 → 0 | **19 → 0** (FeltNap / SlopeFelt added) | 0 → 0 |
| z-scan total / exposed | 2973/0 → 3078/**0** | 7837/0 → 8070/**0** | 1017/0 → 1260/**0** |
| New coplanar felt-top overlaps | **0** | **0** | **0** |
| Gameplay colliders | 396 same | 736 same | 615 same |
| BaseParts | 3785 → 3788 (+3 Visual_Base) | 7501 → 7502 (+1) | 1851 → 1857 (+6) |
| Smoke | putt 7.09, 0 errors | putt 7.41, 0 errors | putt 7.60, 0 errors |
| Sweep (seed 20261014) | 27/27, 18 shots, 0/0/0 | 54/54, 36 shots, 0/0/0 | 54/54, 36 shots, 0/0/0 |
| Published / copy | **v32** `playtest-lantern_grove-v32.rbxl` 3,475,784 B, sha256 `b8295b6a…e9b6` | **v109** `playtest-sugarloaf_canyon-v109.rbxl` 5,438,808 B, `171a5084…ef74` | **v17** `playtest-aurora_archipelago-v17.rbxl` 1,424,960 B, `e9f657c8…ad4a` |

Notes on the table:
- **Smoke:** each smoke also had only the 5 known UIBlox `FoundationProvider` warnings, and 0 server entries.
- **Sweep:** every sweep matches the previous stage's result hole for hole (`*-sweep-comparison.json`, `differing []`).

**Residual samples (not visible).**
- **SC 19 and AU 24:** 0.2-stud bits at mitre corners where 45° berm strips meet with their high edge against the wall (SC H5, AU H10). There are also single corner points inside the outer inset band (SC H6/H8/H18, AU H6), and SC H18's corners lie under sandstone rail meshes.
- Shots `fx1-sugarloaf_canyon-h5-mitre.png`, `-h6-corner.png` and `-h18-collidergap.png` show no visible seam.
- **AU** also has 60 felt-to-light-bridge edge samples on H17, kept inset by design. They're felt meeting a non-felt surface, and there's no dark line (`fx1-aurora_archipelago-h17-lightspan.png`).

**New z-scan hits.** They're joint side faces (opposing interfaces) and mesh bounding-box candidates. `*-zscan-diff.json` lists them; 0 are felt tops.

**New Visual_Base copies (+3/+1/+6).** These are thick sloped felt skins whose side faces, now flush, became coplanar with the Base below. The standard ZF1 remedy applies: the Base gets a noncolliding visual copy offset 0.07–0.08, and the Base collider stays hidden and unchanged. LG H1's copy sits behind the stone rail walls (`fx1-lantern_grove-h1-base-west/east.png`).

**Rails.**
- Separation re-solves visual-only rails against the new felt faces.
- **SC:** 53 rails now resolve to different ±0.08–0.33 offsets from their build pose. v103 already had offsets up to 0.70 and the maximum is still 0.70. Every lifted rail is still sunk into the felt.
- **AU:** 12 rails moved ≤0.14.
- No rail collider changed.

**Before/after shots:**
- `fx1-lg-h1-before.png` / `-after.png`, plus `fx1-before-lg-h1.png`.
- `fx1-lantern_grove-h{1,8,9,4}-{before,after}.png`
- `fx1-sugarloaf_canyon-h{1,16,8,11}-{before,after}.png`
- `fx1-aurora_archipelago-h{1,6,7,18}-{before,after}.png`

**SC H16 edge test** (`tools/sc12_h16_edge.py`, `sugarloaf_canyon-h16-edge-after.json`): unchanged.
- Lip stops **0/80** and outside drops **0**, as in sc12.
- 56/72 slow putts drop (sc12 54/57/58). Max fall Chebyshev 0.975.
- One axis rest ball stayed at 1.175. That's the same ridge-crest variance sc12's run 3 recorded for corners.

## Versions, scripts and process
- **Order:** LG, then SC, then AU, one Studio and one place at a time. Each place was quit normally and `pgrep -x RobloxStudio` was empty before the next one opened.
- **Publishing:** via File > Publish to Roblox (System Events menu click). Each place was published once.
- **Creator Hub published-only:**
  - LG 32, 25, 19, … (`fx1-lantern_grove-v32.png`)
  - SC 109, 103, 79, … (`fx1-sugarloaf_canyon-v109.png`)
  - AU 17, 13, 8, … (`fx1-aurora_archipelago-v17.png`)
  - Lobby still 251 (`fx1-lobby-published.png`)
- **SC v109 is the 11:55 autosave marked as published.** It's the post-apply content: the last edit was before the 18-hole sweep. Publishing an unchanged autosave doesn't create a new number.
- **Copies:** File > Download a Copy, saved through temporary `~/a_*` folders, which were then removed.
- **Scripts pushed:** `VisualSeparation.luau` and `CourseBuilder.luau`, the same files to every place.
  - SC v109 and AU v17 run byte-identical copies of the final src.
  - **LG v32 runs fx1's first revision:**
    - VisualSeparation with exact-flush joints, but not yet the 0.001 setback, the side-face trim, the narrow-strip fit or the under-rail check.
    - CourseBuilder's `MatchCupFelt` limited to flat pieces.
  - LG needed none of those later refinements: its scan is 0 interior seams, 0 new felt-top overlaps and 0 exposed. A rebuild with the final src would differ only by the 0.001 setback. To stay at one publish per place, LG wasn't republished.
  - **Next LG publish should push src** (the existing drift list in `exports/script-diff.md` applies too).
- **Not touched:** lobby, 135374506016678 and the Windows PC were never opened. No assets were created, deleted or archived. No permissions were granted.
- **Screen Recording prompt:** a macOS "Screen Recording" (`universalAccessAuthWarn`) window was found behind full-screen Studio during the SC download. It was never clicked, and no Return was sent while it was up; only clicks outside its rectangle.
- **Temporary experiments:**
  - A rotated strip and test unions in `FX1Exp`. Removed, and inventories confirmed the restore.
  - Re-applying the v25/v103 scripts to measure baselines. Both reproduced the published inventories exactly.
  - Collider copies made only by intermediate script versions were removed before the final apply.

## Tools (new)
- `tools/fx1_stage.py`: preflight, inventory (with colour/appearance), compare, verify, scripts (export and diff vs `exports/`), seams, scan, apply, run, shot. `FX1_ROLE` picks the place.
- `tools/fx1_seams.luau`: the seam scan and cup-look audit.
- `tools/fx1_zdiff.py`: new/gone z-scan hits, with felt-top overlaps flagged.

## Open items
- **LG script drift:** LG v32 carries the first-revision VisualSeparation and CourseBuilder (see above). Push src on the next LG publish.
- **Pre-existing collider-level corner gaps** (0.03–0.16) where 45° corner banks meet walls: LG H3/H9, SC H18, AU H18. They're under bank backing or rails and not visible. They aren't near any cup and weren't changed.
- **SC FeltNap phase:** the texture starts at each part's own corner, so very faint tile-phase lines can show between pieces at grazing angles (SC H11). That was already true between all SC felt parts.
- Not done: `.rbxl` copies to the Linux box, a headset check.

RESULT=PASS CAUSE=VisualSeparation inset every felt skin 0.08 on all edges (0.16 felt-felt / 0.08 felt-CupPlate gaps showing the dark Base); SC CupPlates lost FeltNap in CSG LG=9/v32 SC=18/v109 AU=18/v17 STRIP_MATCHED=9/18/18 SEAMS_AFTER=0/0/0 visible (raw edge samples 0/19/24) COLLIDERS=same CUPS=27/27/54/54/54/54 SMOKE_ERRORS=0 (+5 UIBlox) STUDIO_CLOSED=yes

BUILD DONE, STUDIO CLOSED
