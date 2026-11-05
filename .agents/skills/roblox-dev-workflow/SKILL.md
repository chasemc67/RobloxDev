---
name: roblox-dev-workflow
description: Operating model for building Roblox games on Chase's Mac Mini. Covers which tool to use (Roblox Studio MCP first, computer use as a fallback), where code, notes and assets live, model choice, and the goal of shipping complete published games. Use at the start of any Roblox game-dev task or when unsure how to approach one.
---

# Roblox dev workflow

## Goal
Ship complete, playable games that are **published on Roblox**. Prioritize a working game loop over polish. We vibe code: no line-by-line review.

## Machine and tools (Mac Mini, `chases-Mac-mini.local`)
- **Roblox Studio** at `/Applications/RobloxStudio.app`. Its MCP server (`StudioMCP`) is the main way to work in a place. See the `roblox-studio-mcp` skill.
- **Blender 5.2** at `/Applications/Blender.app/Contents/MacOS/Blender`, for meshes and textures. See `blender-asset-pipeline`.
- **Codex** (`codex`, including `codex exec` for runs nobody is watching) and **Cursor** (`cursor`, `cursor-agent`). Both already have the `Roblox_Studio` MCP configured.
- **Grok Bot** reaches the Mac Mini over remote shell. It drives Studio through `codex exec` (see `roblox-studio-mcp`) and Blender through headless scripts.

## Order of preference for doing things in Studio
1. **Roblox Studio MCP**: use it for scripts, instances, terrain and lighting via Luau, inserting assets, playtesting, reading console output and screenshots.
2. **Computer use** (Codex computer use, Cursor, or Grok Bot's desktop) **only** for things the MCP can't do: Studio UI clicks (File > Save/Publish, Game Settings dialogs, plugin or MCP toggles), the 3D Importer dialog, and the create.roblox.com dashboard.
3. Keep work reproducible: save Luau snippets or asset generator scripts in this repo when they're worth reusing.

## Where things live
- **Game code**: in Studio (the place file / cloud place), saved and published from Studio. Studio's version history is the source of truth. Don't use Rojo or git sync for now.
- **This repo (`~/src/RobloxDev`)**: skills (`.agents/skills/`), per-game notes (`games/<game-name>/design.md`, `status.md`), and asset scripts and exports (`assets/<game-name>/`).
- Update `games/<game>/status.md` at the end of each work session: what changed, what's next, known bugs, place and universe IDs.

## Models and delegation
- Use the strongest available model (e.g. Opus 5.5 or GPT-6 Astra) for hard 3D and spatial work: level layout, CFrame and rotation math, physics, camera, procedural geometry, debugging odd behavior.
- Hand routine work to cheaper or faster subagents: UI text, simple scripts, renaming, notes, asset searches, repetitive edits.
- Check spatial results visually (MCP `screen_capture`, or a playtest plus a screenshot). Don't trust coordinates alone.

## Loop
Design (`games/<game>/design.md`) → build in Studio via MCP → playtest (`start_stop_play` + `get_console_output` + `screen_capture`) → fix → save → update `status.md` → publish (`roblox-publishing`).

## Long-term games
Once a game is maintained long-term, spin it off into its own dedicated bot (and maybe its own repo). Copy its `games/<game>/` notes and any game-specific skills there.
