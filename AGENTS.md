# AGENTS.md: RobloxDev

Instructions for any coding agent (Codex, Cursor, Claude Code, Grok Bot) working in this repo. `CLAUDE.md` is a symlink to this file.

## What this repo is
- Shared dev work for Roblox games: **agent skills, per-game design notes, Blender scripts, exported assets.**
- **It is NOT game code.** Game scripts and instances live in Roblox Studio and are saved and published from Studio (Studio versioning, no Rojo or git sync). Don't try to mirror Studio scripts into this repo unless asked.
- We're vibe coding: optimize for a playable, published game. Don't do line-by-line review.

## Dev machine
Chase's Mac Mini (`chases-Mac-mini.local`, user `chase-mini`, Apple Silicon) runs:
- Roblox Studio at `/Applications/RobloxStudio.app`, with its built-in MCP server `/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP`
- Blender 5.2 LTS at `/Applications/Blender.app` (`/Applications/Blender.app/Contents/MacOS/Blender`)
- Cursor (`cursor`, `cursor-agent`), Codex (`codex`, already configured with the Roblox Studio MCP), plus `gh`, `uv`/`uvx`, `node`, and `python3` (3.9; use `uv` for newer versions)
- This repo is cloned at `~/src/RobloxDev`

## Skills (`.agents/skills/`)
| Skill | Use when |
|---|---|
| `roblox-dev-workflow` | Any Roblox task: the overall operating model, which tool to use, and where things live |
| `roblox-studio-mcp` | Reading or changing anything in an open Studio place (scripts, instances, playtests) |
| `blender-asset-pipeline` | Making meshes or textures in Blender for Roblox |
| `roblox-publishing` | Taking a place from Studio to a live, public experience |
| `new-roblox-game` | Starting a new game or prototype |

Skills live in `.agents/skills/`, which Codex and Cursor read directly. `.claude/skills` is a symlink to it for Claude Code. Edit skills only in `.agents/skills/`.

## Layout
```
.agents/skills/<skill>/SKILL.md   canonical skills
.claude/skills -> ../.agents/skills
games/<game-name>/design.md       pitch, core loop, controls, MVP scope
games/<game-name>/status.md       current state, TODO, known bugs, place/universe IDs
assets/<game-name>/               Blender generator scripts (*.py) + exports (*.fbx, textures)
```

## Conventions
- Use kebab-case for game folder names. Record the Roblox place ID and universe ID in `games/<game>/status.md` once published.
- Commit notes, skills and asset scripts often, with short clear messages. Never commit secrets or API keys.
- When a workflow gets repeated or a lesson is learned, update the matching skill.

## VR Mini Golf V2
- VR Mini Golf V2 (including Pirate Shipwreck) lives in its own repo, [chasemc67/vr-mini-golf-v2](https://github.com/chasemc67/vr-mini-golf-v2). Do V2 work there, not here.
- `assets/mini-golf-v2/` only keeps Pirate Shipwreck sources that haven't been migrated to V2 yet, pending review. Don't add to it.
- `games/vr-mini-golf/`, `assets/vr-mini-golf/` and `assets/vr-minigolf/` are V1, which is a separate game.

## VR Mini Golf (V1) lobby controls
- The VR Mini Golf V1 lobby uses OUR VR controls (`VRControls`, wrist card, VR putter, sticks, and B/Y scorecard gear) under both real VR and SimulateVR. Chase decided this on Oct 12, 2026 (stages ad/ae). Desktop keeps LobbyRoam.

## What to commit
- Commit: source (py, luau, json specs, md, scripts) and final art-direction images in art folders: `concept(s)/`, `textures/`, `ui/`, `icons/`, `marketing/`, `thumbnails/`, plus a few chosen final previews/hero renders copied into a `final/` folder (not inside `previews/`).
- Never commit: logs, stderr, debug output, iteration/per-version screenshots (`screens/`, `shots*/`, `previews/`, `prev*/`), `.npy`/`.npz`/`.pkl`, scratch/backup folders (`_work/`, `_raw/`, `_cache/`, `_props_pre*/`, `backup*/`, `*.bak-*`), generated mesh dumps, `.rbxl` place files, `.mp4`/`.mov`.
- `.fbx` is build output (gitignored): re-export it from the `.blend`.
- `.blend` is the 3D source and goes in via Git LFS (3D Model Bot sets that up and un-ignores it).
- Keep each file under ~20 MB and each push under ~80 MB. `.gitignore` enforces this; don't `git add -f` around it.
