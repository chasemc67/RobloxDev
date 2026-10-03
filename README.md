# RobloxDev

Shared workspace for building Roblox games with AI agents (Codex, Cursor, Claude Code, Grok Bot) on Chase's Mac Mini.

**This repo does not hold game code.** Game code lives in Roblox Studio and is saved and published from there (we use Studio's built-in versioning, with no Rojo or git sync for now). This repo holds the shared dev work around the games:

- `.agents/skills/`: agent skills in the open Agent Skills format (one folder per skill, each with a `SKILL.md`)
- `games/<game-name>/`: design notes, status and TODOs for each game
- `assets/<game-name>/`: Blender generator scripts and exported meshes and textures

Start with [`AGENTS.md`](AGENTS.md). Games that get maintained long-term are later spun off into their own dedicated bot and maybe their own repo.
