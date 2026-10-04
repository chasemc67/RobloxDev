# Robo Clash Arena: status

## Now
- 2026-10-03: V1 is feature-complete in Studio (place 99842799688877) and playtested end to end. It is not yet public: Codex saves it with File > Save to Roblox, and publishing is handled separately.
- Flow:
  - Title -> Robot Select (BOLT all-rounder, CRUSHER bruiser, LANCER sniper, with lobby statues and a loadout/stat panel) -> Mode Select (Matchmaking / Battle a Bot / Back).
  - Match: cube drop-in, then READY 3-2-1 LAUNCH!, then the 1v1. It ends with K.O. / TIME UP / DRAW / OPPONENT LEFT, plus PERFECT on a no-damage KO.
  - Results: stats, Rematch, Back to Select.
- Combat (server-authoritative):
  - Guns: 3-round homing burst, 5-way spread, charge laser.
  - Arcing bombs with about 1 s blasts.
  - Pods: seeker, mine, twin orbs.
  - Endurance -> DOWN (3 pink pips) -> REBIRTH invulnerability flash.
  - Body dash attacks, pits, knockback.
  - 180 s timer; on time-out the higher HP% wins.
  - Global `DamageScale` 0.7, so a bot fight lasts about 45–60 s.
- Server bot AI: keeps its preferred range, strafes, avoids pits and walls, dodges, and fires with a reaction delay and aim error.
- Matchmaking: an in-server FIFO queue pairs two humans, and each match gets a private arena slot. Mid-match leaves give the remaining player the win ("OPPONENT LEFT"). A match with no humans left is torn down.
- Look (art direction): holo arena in a dark blue void with bloom, chunky toy robots with glowing visors, and an auto-zoom camera at about 47° with camera-side wall fade.
  - HUD: thick HP bars in the bottom corners, pink DOWN pips, a pink reticle, HIT plus red DAMAGE numbers, and floating P1/P2 tags.
  - Big tilted announcer text on a pink-edged slash band: READY / LAUNCH! / K.O.! / DOWN / REBIRTH.
- Sound: snappy sci-fi SFX plus an industrial electronic music loop, all free Creator Store audio (mostly Pro Sound Effects, APM, and Roblox). All ids are verified to load.
- Input: KB+M, gamepad (CAS bindings and menu SelectedObject), and touch (dynamic stick plus GUN/BOMB/POD/JUMP/DASH buttons; HP panels move to the top corners on touch).
- Studio settings: CharacterAutoLoads off (set by script), StreamingEnabled off, chat window hidden (bubble chat still on), EnableMouseLockOption off.
- Game scripts are authored in `~/src/rca-work/src` (outside this repo) and pushed into Studio with `~/src/rca-work/push.sh`. See `architecture.md`. The arena and robot builders live in `assets/robo-clash-arena/`.
- All temporary debug hooks used for testing (Studio-only server hook, fake matchmaking participant, bot idle flag, ForceTouch override) have been removed.

- 18:40 PT: Opus phase 1 run finished (log: logs/opus-phase1.log, ~73 min, model `claude-opus-5-5-high`). Studio saved to Roblox via Codex at ~18:10 PT. Next (orchestrator): 2-client Studio test (logs/codex-multiclient1.log), Save+Publish, dashboard config + make PUBLIC (prompts/dashboard-config.md).

- 18:50 PT: Studio 2-client test (Server + 2 clients) PASSED: Matchmaking paired Player1/BOLT vs Player2/CRUSHER, HP synced both views, OPPONENT LEFT -> YOU WIN, no script errors (logs/screens/mc-*.png).
- 19:00 PT: Dashboard configured (Codex): name, description, genre Action > Battlegrounds & Fighting, devices Computer/Phone/Tablet/Console, maturity questionnaire = Mild (Violence, repeated/mild). Still PRIVATE.
- Going public (docs, Oct 2026): Public 16+ / Trusted Friends needs an account >=2 days old in good standing + age check (facial estimation or ID) + questionnaire; it's FREE. All ages (Kids/Select) also needs ID verification + 2FA + (Plus/Premium for 2 months OR refundable 1,000 Robux fee OR 50,000 Robux expedited review). Limited > Friends audience = owner's friends only, same 16+ tier requirements. Private = Edit-permission users only (owner can play). NO fees paid.
- Opus phase 2 polish run in progress (logs/opus-phase2.log, prompts/phase2-polish.md).

## TODO
- Publish public (handled separately).
- Test real 2-human matchmaking on a live server. Two actual Studio local clients passed pairing, damage synchronization, and disconnect handling on 2026-10-03.
- Test on a real phone and a real gamepad.
- Later: FFA (3–4 players; the match code is already N-participant), part customization, more arenas.

## Known bugs / limits
- 2026-10-03 local two-client verification: Player1/BOLT vs Player2/CRUSHER paired; both HUDs agreed on Player2 HP 329 after 671 damage/38 hits. W/A/D, jump, dash, gun, bomb, and pod inputs exercised for approximately 20 seconds. Client-side disconnect produced OPPONENT LEFT then YOU WIN/results. Cube drop/countdown was not captured, so its exact sequence remains unverified in this run. Studio MCP input/capture was used because cua_repl bound only the original Studio process; disconnect used LocalPlayer:Kick after virtual Escape was rejected and start_stop_play did not disconnect the client. No place scripts or instances edited. End Session closed all three test processes; original place verified in Edit mode. Screens: logs/screens/mc-*.png. No game-script warnings/errors in LogService; Studio automation emitted a CoreGUI mouse-input error (see logs/mc-verification.md). Visual notes: strong bloom on Player2 versus Player1, tiny control captions, overlapping DOWN/DAMAGE/HP labels, and a brief stale queue player count.
- The Studio MCP's virtual gamepad presses arrive as keyboard input, and its virtual touch isn't supported. Because of that, gamepad and touch input were checked through code paths and layout screenshots only. Touch buttons call the same `Battle.DoAction` as keys.
- Lock-on always targets the nearest rival. That is fine for 1v1; FFA will need target cycling.
- The REBIRTH flash blinks fairly slowly (about 0.5 s on/off).

## IDs
- Place ID: 99842799688877 (published 2026-10-03 as a new experience under Chase's account, still PRIVATE)
- Universe ID: 10769245121
- URL (once public): https://www.roblox.com/games/99842799688877
