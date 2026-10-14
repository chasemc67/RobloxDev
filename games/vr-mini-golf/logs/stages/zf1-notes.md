# Stage zf1 — menu border, Sugarloaf visual separation, Aurora card v2

Status: validation in progress; no publish performed yet.

## Preflight
- No competing `codex exec -m` / `claude -p` stage process. Closed the prior Sugarloaf local session without saving, launched fresh Studio, and visually confirmed “Welcome, MetavrseBuilder”. One Studio and one place throughout.
- Creator Hub Version History, “Show published only”: lobby 249; Lantern Grove 9; Sugarloaf 21; Aurora 3. Protected place 135374506016678 not opened.
- Source input: `playtest/playtest-sugarloaf_canyon-v21.rbxl`. Existing zf1 uploads reused; no duplicate asset uploads.

## Menu root cause and replacement
- The old local PNG is 1200×800, but Roblox serves asset 101738563295695 at **1023×682**. Measured directly with `AssetService:CreateEditableImageAsync(Content.fromUri(...)).Size` in Studio.
- Old code used `SliceCenter=Rect.new(64,64,1136,736)`: its right and bottom coordinates exceed the served texture. This explains the malformed corner/offset top edge and missing right/bottom border in Chase’s screenshot. There was one frame image and the UIStroke was only a fallback; stacked frame layers were not the root cause.
- Uses Game Art Bot’s supplied `menu_frame_9slice.png`, asset **125693854537650**, 256×256; `ScaleType=Slice`, exact `SliceCenter=(32,32,224,224)`, `SliceScale=.35`, zero native border. Content’s smallest inset is 12 design pixels (frame band 11.2).
- Aurora playable card uses **119746292850007** (`card_auroraarchipelago_v2.png`). Old asset IDs remain commented in Config.

## Sugarloaf source rule
- `VisualSeparation.Apply(course)` runs after geometry/imports/hints/decals through SugarloafOverrides; CourseBuilder and SugarloafBuilder already invoke Overrides.
- Default exposed visual separation .08 studs (minimum .05); visible part dimensions ≥.2. Existing collider instances, CFrames, sizes, collision/query/touch flags, groups and physical properties stay unchanged. Needed appearances use untagged, noncollidable, nonqueryable visual copies.
- Joint isolation prevents welded visual edits moving whole collider assemblies; joints reconnect with updated relative visual transforms. An early local attempt correctly failed the collider assertion and was discarded without saving or publishing.
- Every placeholder retained: baseline **175 parts = 97 visible +78 hidden**. Decal-only placeholder appearances may become transparent; no placeholder instance is deleted.
- 29 uploaded decal IDs reused; 29 placements, none missing. H3/H13 route arrows use the authored route positions. H15 image-right chevrons follow gravity projected onto the felt slope; UV orientation accounts for Roblox Top image-right being local -X.
- Asset-owner files under untracked assets/ and Lantern Grove assets were not edited. Geometry is emitted by the source CourseBuilder; the post-build rule is shared/reproducible there, without editing bot-owned asset generators.

## Scan methodology and limitations
`tools/zf1_zscan.luau` uses OBB face planes, rectangle SAT overlap and .02-stud tolerance, all visible Workspace parts excluding characters. It also checks active decorated faces, placeholders, exact transforms, translucent/material layers, script transparency candidates, and terrain-only center/corner rays. Raw counts include buried interfaces and conservative mesh/CSG/curved bounding boxes. Raw counts are never replaced by a smaller claimed count; exposed planar candidates are separately classified. Model Bot candidates retain full names, holes, positions and MeshIds in `model-bot-mesh-hits.json`.

Before: coplanar 10852; decorated 357; placeholders 201; transparency 411; total **11821**. Terrain samples flagged 177; imported-mesh category entries 4958.

## Validation and publication
Final independent part scan: coplanar 5073; decorated 101; placeholder 41; transparency 402; total **5617**. Exposed planar candidates in categories 1–3: **0**. Remaining category 1–3 hits: 4648 non-planar/mesh-bbox candidates and 567 opposing/internal interfaces. These are conservative bounds or buried joins, not automatically evidence of an exposed rendered overlap. Model Bot before/after entries: 4958/4888. Terrain ray candidates119 remain separately reported (mesh bounds and terrain/felt intersections); no terrain voxels or physics were changed.

Final source pass: 1377 changes, zero unresolved, zero thin visible parts, 183 felt skins constrained to original visual top height, 177 joints reconnected. All 705 original collider transforms/sizes/query/touch/collision/physical properties match the untouched v21 inventory exactly. 175 placeholders remain; 65 are visible after decal replacement (110 hidden).29/29 decals placed, no missing IDs. H15 downhill tangent Y=-0.0995037 confirms chevrons point downhill.

Native18-hole test: 54 successful cup drops, 36 completed random shots, no stuck/escape findings, zero console errors/warnings. H17 required two refused setup retries before its third successful cup drop. H15's two random shots hit the 20-second timeout; the identical seeded shots against untouched v21 also produced two timeouts, zero stuck/escapes and all three cup drops. This is a pre-existing slope behavior, not a collider regression. Baseline evidence: baseline-h15/.

Final Sugarloaf desktop smoke passed, zero errors/warnings; ball arrival 0.09 studs from tee. Published exact existing Sugarloaf Canyon row, verified Creator Hub published-only **v23** and MCP PlaceId124440050576723/PlaceVersion23/role sugarloaf_canyon/29decals. Saved `playtest/playtest-sugarloaf_canyon-v23.rbxl`,3546633bytes,SHA256`71c20a41eff4d3ea8d3f9ac9fd40268a75b76528344bf6b5c9dbc301225a0dc9`. Lobby completed below. LG/Aurora local scans deferred because this was not a quick extension; neither protected place was opened or modified in Studio.

## Lobby visual verification
- Cloud lobby opened with PlaceRole=lobby, PlaceId87725688219952,**saved PlaceVersion250**, not249. CreatorHub showed250 saved 8:49 PM/unpublished; 249 published 8:47 PM. This pre-existing post-publish save was recorded rather than falsely claiming the opened revision was 249. Its menu/card IDs matched the old published assets. No restore was performed.
- Pushed all source and rebuilt LobbyBuilder.BuildPortals for the three existing courses.
- Actual Studio Play images preloaded successfully: exactly one menu frame 125693854537650, SliceCenter 32,32,224,224, SliceScale .35; Aurora card 119746292850007 IsLoaded=true.
- Screenshot checks: iPhone 13 preset 844x390 (camera safe viewport 750x390), iPhone 7 viewport 667x375, and HD 1080 viewport 1920x1080. Every corner meets cleanly with one border. Before screenshot captures the old missing right/bottom border; after screenshots and Aurora card title are readable at the tested sizes.
- Device presets/resolutions were controlled through [StudioDeviceSimulatorService](https://create.roblox.com/docs/reference/engine/classes/StudioDeviceSimulatorService), with overrides reset afterward.
- Sugarloaf shutdown stalled on Applying script changes after verified publish and local save. No Escape; TERM then KILL per runbook, confirmed no Studio before opening lobby.

Top recorded visual fixes: 618 thickness corrections, 546 exposed parallel-face offsets/trims, 183 protected felt skins, 19 decal/felt offsets, 11 imported-deck/terrain model offsets. Full part names, hole, category and changes are in fixes.json. Imported models are moved as units so their material components stay aligned.

## Final publication and cleanup
- Lobby desktop smoke passed all three course cards and all three walk-in arches with the correct existing place IDs and loading art. Server/client errors and warnings: zero.
- Published the cloud lobby to its own place with File > Publish to Roblox. Creator Hub Show published only verified **251**. Evidence: `zf1-lobby-v251.png`.
- Saved `playtest/playtest-lobby-v251.rbxl` (870,467 bytes), SHA-256 `a0ebd0432bbf701d096e0dd4adf93113c2527b7dc559ec71a7973443963ca241`.
- Lobby Studio closed normally. Verified no Studio application process remains.
- Final read-only published histories: **Lantern Grove 9**, **Aurora Archipelago 3**, unchanged. Neither was opened in Studio or published. Place 135374506016678 was never accessed. No PC use.
- No git push, no RBXL commit, no unrelated asset edits. Optional protected-course scans were not run. Live VR/headset rendering and actual cross-place teleport remain live-game checks; Studio verified request destinations.

RESULT=PASS LOBBY_NEW=251 SC_NEW=23 LG=9 AU=3 ZSCAN_BEFORE=11821 ZSCAN_AFTER=5617 PLACEHOLDERS=175 CARD=119746292850007 DECALS=29/29
