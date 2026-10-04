# Robo Clash Arena: status

## Now
- 2026-10-03: Design written. Building V1 in Studio via cursor-agent (Opus 5.5, `claude-opus-5-5-high`).

- Published empty place early via Codex computer use so work saves to the cloud (File > Save to Roblox).
- V1 build in progress in Studio (place 99842799688877). Playable end to end:
  - Title -> Robot Select (BOLT all-rounder, CRUSHER bruiser, LANCER sniper; lobby statues + loadout/stat panel) -> Mode Select (Matchmaking / Battle a Bot / Back) -> cube drop-in, READY 3-2-1 LAUNCH! -> 1v1 -> K.O. / TIME UP / DRAW / PERFECT -> Results (stats, Rematch, Back to Select).
  - Server-authoritative combat: homing guns (3-round burst, 5-way spread, charge laser), arcing bombs with lingering blasts, pods (seeker, mine, twin orbs), endurance -> DOWN (3 pink pips) -> REBIRTH invulnerability, body dash attacks, pits, knockback, 180 s timer (higher HP% wins).
  - Server bot AI (strafe, preferred range, pit/wall avoidance, reaction delay + aim error, dodges, bombs/pods).
  - In-server matchmaking queue (FIFO, pairs 2 humans into a private arena slot); tested with a fake participant harness.
  - Auto-framing ~47 deg camera (zoom-to-fit, HUD-safe), floating P1/P2 tags with HP + pips, pink lock-on reticle, HIT + red DAMAGE combo numbers, P1 panel bottom-left / P2 bottom-right.
- Studio-side changes made: CharacterAutoLoads off (set by script), StreamingEnabled off, chat window hidden (bubble chat still on), EnableMouseLockOption off.
- Game scripts are authored in `~/src/rca-work/src` (outside this repo) and pushed into Studio with `~/src/rca-work/push.sh`; Studio is the source of truth for the place. The arena/robot builders live in `assets/robo-clash-arena/`.

## TODO
- Sounds (Config.Sounds ids), touch layout pass at phone resolution, gamepad pass, polish (art direction: skewed announcer text, thicker HP bars), pacing tune, remove Studio debug hook, architecture.md.
- Publish public (handled separately).

## Known bugs
- Studio MCP virtual gamepad presses arrive as keyboard input, so gamepad menu navigation could not be exercised by the agent (bindings are in place: A confirm via SelectedObject, B back).

## IDs
- Place ID: 99842799688877 (published 2026-10-03 as a new experience under Chase's account, still PRIVATE)
- Universe ID: 10769245121
- URL (once public): https://www.roblox.com/games/99842799688877
