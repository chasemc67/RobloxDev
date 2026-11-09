---
name: roblox-blender-asset-handoff
description: Recipe for taking a Roblox 3D asset from editable Blender source through FBX export and validation to a builder handoff. Covers where Blender runs (the Windows PC), the saved .blend in Git LFS as the source of truth, manifests, orientation checks, LFS verification, and who owns what. Use when you model, revise, export or hand off a Blender asset (props, lobby pieces, course meshes) for a Roblox game, or when you review such a handoff.
---

# Roblox Blender asset handoff

Path: editable `.blend` source, then FBX export, then validation, then handoff to the builder. For Roblox mesh limits, PBR and importer quirks, see `blender-asset-pipeline`. Where the two skills disagree on where Blender runs or on axis settings, this skill wins.

## Where and how Blender runs
- **All Blender modeling, rendering and export runs on the Windows PC (`ssh pc`)**, not on the Mac Mini or the cloud box. If the PC can't be reached, stop and coordinate recovery with Chase or the other bots. Don't fall back to another machine.
- Blender scripting uses **Claude Code with Opus 5.5** (Chase's current choice).
- The PC is shared. Run **one Blender job at a time** and check that no other `blender.exe` is running before you start. Never close or touch another bot's Studio session. Don't render a flythrough unless someone asks for one.
- Run long Blender jobs as **detached scheduled tasks** so an ssh disconnect doesn't kill them. Write stdout/stderr and the exit code to local log files and poll them. `assets/mini-golf-v2/pirate-shipwreck/models/start_ship_whimsy_v5_1/src/run_blender.ps1` is an existing example. Copy the pattern, not its hard-coded paths.
- Keep secrets, tokens and machine-specific auth setup out of scripts, manifests and this repo.

## Before you start
1. Pull first (`git pull origin main`). Serialize source commits with any other bot touching the same asset folder. Never reset, stash or overwrite someone else's uncommitted files.
2. Get the inputs and confirm they are approved:
   - **Art direction**: Game Art owns the approved concepts and silhouette references. Model to them. Don't invent art direction. If no approved reference exists, ask Game Art for one.
   - **Course geometry**: for course blockouts, the authoritative approved `holes.json` is the geometry input. Snapshot it and record which version you used. Generic lobby props and scenery don't need a `holes.json`.
3. Decide what is decorative and what is playable. Decorative mesh changes stay separate from authored playable geometry and collision. Never change hole geometry, collision or difficulty silently. If a visual change needs a geometry change, flag it to the builder and the owner instead.

## Source layout (one folder per asset version)
Follow `AGENTS.md` and `.gitignore` for what may be committed. A typical folder looks like this:
```text
assets/<game>/<area>/models/<asset>_v<N>/
  <asset>_v<N>.blend      # source of truth, Git LFS
  manifest.json           # see "Manifest" below
  README.md               # short status, caveats, handoff summary
  src/*.py                # generator / edit / export / validate scripts
  textures/*.png          # final textures (also packed or relatively referenced in the .blend)
  final/*.png             # optional: a few chosen final previews only
```
- The **saved `.blend` is the source of truth**. Give objects clear names and group them in collections (for example `Visual`, `Collision`, `Movers`). Pack textures, or reference them with relative paths that resolve inside the repo.
- The scripts in `src/` plus the saved `.blend` must reproduce every export. Re-export from the saved `.blend`. Don't rebuild the asset ad hoc at export time.
- **FBX is derived output** and gitignored. Regenerate it from the saved `.blend`. Never hand-edit an export.
- Keep a revision you are replacing untouched. Make a new versioned folder or `.blend` and record the base file's commit and sha256 in the manifest.
- Never commit previews, iteration screenshots, logs, debug or validation dumps, backups, scratch folders, `.npy`, videos or `.rbxl`. Generate local diagnostics, then summarize their results in the manifest or README.

## Roblox-friendly modeling
- At most **20k triangles per mesh**. Keep UVs clean. Use PBR / `SurfaceAppearance`-ready textures where they help, or a shared palette texture or flat per-material meshes for stylized props.
- Typically **1 Blender unit = 1 stud** (Unit System None). Record the scale you actually used.
- Moving pieces (doors, hinges, windmills, pendulums) are **separate objects with their origin at the hinge or pivot**. Record the axis, range and pivot of each one.
- Far scenery gets one pass, with no fine polish. Spend detail where players look.
- Don't carry over fixed clearance or keep-out numbers from old course examples. Derive clearances from the current approved geometry and gameplay requirements, and record where each one came from.

## Export and orientation
- Record the exact exporter settings in the manifest: forward/up axes, `apply_scale_options`, global scale, path mode, texture embedding, and which collections were exported. Older notes give conflicting axis shorthand (for example `Z` vs `-Z` forward), so don't trust shorthand from memory.
- **Check the orientation with an asymmetric marker.** Include, or temporarily add, an object that can't be mistaken when mirrored or rotated (for example an arrow or L-shape pointing at the asset's front). Re-import the FBX, or have the builder import it, and confirm that front, up and handedness match the manifest. Record the result.
- Record the front direction, the origin/pivot of each exported object, and each bbox in both Blender and Roblox coordinates.

## Validation (Blender-side only)
Run automated checks on the PC against the saved `.blend` and its exports, and keep the raw output local. Typical checks:
- per-mesh triangle counts against the 20k limit, plus a total
- bbox and scale against the approved reference dimensions or `holes.json`
- materials and textures resolve (no missing images), and UVs exist where textures are used
- unchanged objects really are unchanged when this is a revision (names, transforms, mesh data)
- movers: pivot location and clearance swept through their full motion range
- the orientation marker check above

Render previews: one at **eye level** (player or VR eye height) plus one **useful overview**. Compare them side by side with the approved art.

**Blender fitchecks are not acceptance.** Studio integration and publishing belong to RobloxDevBot. In-engine gameplay and physics validation belongs to Playtest. Say exactly what you validated and what you didn't.

## Manifest
`manifest.json` should cover, as they apply:
- asset name, version, Blender version, source `.blend` path, base revision (commit + sha256)
- exported FBX and texture paths (regenerated, not committed) and committed texture paths
- units/scale and exact export settings, with the orientation check result
- per mesh: triangles, materials and texture mapping, pivot, bbox, collection
- movers: hinge/pivot, axis, motion range, clearances
- placement in the place, if known (CFrame or anchor points), and which inputs it came from
- collision provenance: authored where, exported or not, verified against what (or "not verified")
- what changed against the base, and any unresolved caveats

## Commit and verify LFS
1. Stage only allowed source files. Run `git check-attr filter -- <file>.blend` and expect `filter: lfs`.
2. Commit with a short, clear message and push your branch.
3. Verify the pointer and the remote copy, not only the local commit:
```bash
git show origin/<branch>:<path>.blend          # must be an LFS pointer: version / oid sha256:... / size
tmp=$(mktemp -d)
GIT_LFS_SKIP_SMUDGE=1 git clone -q --depth 1 --branch <branch> <remote-url> "$tmp/c"
cd "$tmp/c" && git lfs pull --include="<path>.blend" && sha256sum "<path>.blend"
```
The sha256 must equal the pointer's `oid` and the hash of the file you saved on the PC. Record it in the manifest and the handoff. (Run this on any machine with repo access, then delete the temp clone.)

## Handoff to the builder
Send RobloxDevBot (cc Game Art for art review) a short message covering:
- source branch and commit, `.blend` path, LFS sha256 and how you verified it remotely
- export, texture and manifest paths, and how to regenerate the FBX from the saved `.blend`
- coordinates, pivots, scale, front direction and the orientation check result
- what changed against the previous version, and what didn't
- validation scope (what was checked in Blender), what still needs Studio or Playtest acceptance, and the caveats
- preview images (eye level + overview) next to the approved art
