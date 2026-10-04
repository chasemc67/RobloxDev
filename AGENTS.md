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
- Claude Code CLI (`claude`, native install at `~/.local/bin/claude`, signed in with Chase's Claude Max subscription, Roblox Studio MCP at user scope). Claude Desktop is also installed.
- Cursor (`cursor`, `cursor-agent`), Codex (`codex`, already configured with the Roblox Studio MCP), plus `gh`, `uv`/`uvx`, `node`, and `python3` (3.9; use `uv` for newer versions)
- This repo is cloned at `~/src/RobloxDev`

## Running a headless agent on the Mac Mini
Order of preference:
1. **Claude Code + Opus 5.5 (preferred for coding/building work).** Uses Chase's Claude Max subscription (not an API key, never set `ANTHROPIC_API_KEY`). Has the `Roblox_Studio` MCP and the user skills in `~/.claude/skills`.
   ```bash
   cd /tmp && perl -e 'alarm 1800; exec @ARGV' \
     claude -p --model opus --dangerously-skip-permissions "<task>" </dev/null
   ```
   `--model opus` resolves to `claude-opus-5-5` (pin it with `--model claude-opus-5-5`). Add `--output-format json` to get `result` plus `modelUsage` (shows the model id). Run it from the repo dir instead of `/tmp` when it should edit repo files.
2. **Codex (`codex exec`, GPT-6 Astra)** is still used for Studio MCP work and for **computer-use clicks** (`cua_repl`): Studio dialogs, browser logins, the create.roblox.com dashboard. See `roblox-studio-mcp`.
3. **`cursor-agent -p`** is the fallback (Cursor's third-party model quota runs low).

GNU `timeout` isn't installed; use `perl -e 'alarm N; exec @ARGV' <cmd>`. `~/.zshenv` puts `~/.local/bin` and Homebrew on PATH, so `claude`, `codex` and `cursor-agent` resolve in non-interactive `zsh -c` shells.

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
