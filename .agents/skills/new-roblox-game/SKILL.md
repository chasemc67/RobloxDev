---
name: new-roblox-game
description: Kick off a new Roblox game or prototype. Write games/<name>/design.md (pitch, core loop, controls, MVP scope), create the place in Studio, build a playable MVP loop fast with the Studio MCP, playtest, and iterate. Use when Chase asks for a new game, prototype or game idea.
---

# New Roblox game

## 1. Write the design (5 minutes, not more)
Create `games/<game-name>/design.md` (kebab-case) in this repo:
```markdown
# <Game Name>
## Pitch        one or two sentences; why it's fun
## Core loop    what the player does every 30 seconds (do → reward → upgrade/progress → repeat)
## Controls     PC (WASD/mouse/keys) and mobile (touch buttons) equivalents
## MVP scope    the smallest playable version: 3-6 bullets. Everything else goes under "Later"
## Later        nice-to-haves
## Art/feel     style, palette, reference games
```
Also create `games/<game-name>/status.md` with three sections, *Now*, *TODO* and *Known bugs*, plus IDs once they exist. Commit both.

## 2. Create the place
- In Studio: start from a template such as **Baseplate** (File > New, or the start page). This is a UI click, so use computer use. Save it to Roblox under the game name.
- Check that the MCP sees it: `list_roblox_studios` should show the place name. Use that `studio_id` (see `roblox-studio-mcp`).

## 3. Build the MVP loop fast
Use the Studio MCP (`execute_luau`, `multi_edit`, `insert_asset`):
1. World: a simple playable space built from parts and models (use `generate_procedural_model` or `insert_asset` for props; use Blender only when it's needed).
2. Server logic in `ServerScriptService`, client and UI in `StarterPlayerScripts` / `StarterGui`, and shared modules and `RemoteEvent`s in `ReplicatedStorage`.
3. Core loop working end to end, with a visible score or currency (e.g. `leaderstats`) and a clear goal.
4. Basic UI: objective text plus mobile-friendly buttons if the game needs them.
Get it playable first, then polish. Use a strong model for spatial and level work and cheaper subagents for routine scripts (see `roblox-dev-workflow`).

## 4. Playtest and iterate
`start_stop_play` → play with `character_navigation` / `user_keyboard_input` → `get_console_output` (fix every error) → `screen_capture` (check that it looks right) → stop → fix → repeat. Save in Studio after each good iteration and update `status.md`.

## 5. Ship
When the MVP loop is fun and has no errors, follow `roblox-publishing`. If the game is going to be maintained long-term, plan to spin it off into its own bot (and maybe repo).
