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
- Opus phase 2 polish run done (logs/opus-phase2.log, prompts/phase2-polish.md). Scripts are pushed into Studio but NOT saved, so the orchestrator needs to Save to Roblox. Changes:
  - Camera: a tighter zoom-to-fit (distance 32–105, down from 40–115). The fit follows each robot's real height, so jumps stay in frame, and touch uses larger bottom and side margins for the controls. Measured: robots off-screen in 0–1 of 400 samples. Robot visuals and hitboxes are unchanged.
  - Cyan ring over the P1 HUD: this was the arena's neon CenterRing floor emblem seen up close. The template's CenterRing transparency is now 0.75, and the client fades the ring and disc when they fall in the bottom HUD band.
  - REBIRTH flash: a 0.1 s blink between a white highlight and a see-through ghost for the whole 2.6 s invulnerability window. Measured at about 0.093 s per phase.
  - Phone layout, checked on the iPhone 17 Pro simulator (750x361):
    - A compact 1100x600 design canvas is used when the screen is under 560 px tall.
    - Touch HP panels are scaled to 0.78 at the top corners and pushed below the Roblox top bar where it covers them.
    - GUN plus an arc of POD/JUMP/DASH/BOMB on the right, the stick on the left, and no default TouchGui.
  - Gamepad: Select defaults to the current robot and Results to Back when Rematch is gone. NextSelection now links the robot list to the bottom row. The menu re-selects a default when Roblox clears SelectedObject, and a default is selected when the gamepad becomes the active input.
  - Lobby: `World.LightStatues` adds key and rim spotlights, a fill light, and a neon halo disc behind each statue.
  - Mode Select has a HOW TO PLAY panel for the active input (keyboard, gamepad or touch). The matchmaking search panel adds: "Playing with a friend? Join their server, then both pick Matchmaking."
  - Results content is centered.
  - Bug bash: one bot match each as Bolt, Crusher and Lancer reached KO and Results. Rematch (clicked within 30 s) and Back to Select both work, with 0 game warnings or errors on client and server.

- 19:35 PT: Opus phase 2 polish done (logs/opus-phase2.log): tighter camera (32-105 studs), floor emblem no longer covers the HUD, fast REBIRTH blink (0.1 s, 2.6 s), phone layout checked in Studio's iPhone simulator, gamepad selection defaults/watchdog, lit lobby statues, HOW TO PLAY panel, friend hint in the queue panel, bug bash with all 3 robots clean.
- ~19:10 PT: Saved and PUBLISHED to Roblox from Studio (version 19). The live place is current. Audience is still Private (owner/editors only).
- Account eligibility (read-only check): age check 21+ done, government ID done, 2FA (email) done, publishing reach = "All ages", no Premium/Plus. Setting Audience = Public is FREE now (reaches age-checked 16+ users and Trusted Friends; "Maturity: Mild, Ages 16+"). The 1,000 Robux refundable fee / 50k expedited review is only to reach under-16 Kids/Select accounts before the 250-HEP evaluation. Not paid.

- 19:20 PT: Audience set to **PUBLIC** (Configure > Audience > Public > Save, via Codex; free, no fees paid or enrolled). Dashboard reload shows Public; Audience reach "Current reach" = "Ages 16+ and trusted friends". Signed-out check: games API returns name "Robo Clash Arena" (not Title Unavailable), creator MetavrseBuilder, server size 50. Page: https://www.roblox.com/games/99842799688877 (Maturity: Mild, Ages 16+, Play button). Screenshot: logs/public.jpg (local, gitignored). Thumbnail/icon still the Roblox default.

## TODO
- Add an icon (512x512) and thumbnails (16:9) on the dashboard.
- Under-16 reach (Kids/Select) unlocks after 250 highly engaged 16+ players in 60 days, or with Plus/Premium for 2 months, or the refundable 1,000 Robux fee (not paid).
- Test real 2-human matchmaking on a live server. Two actual Studio local clients passed pairing, damage synchronization, and disconnect handling on 2026-10-03.
- Test on a real phone and a real gamepad.
- Later: FFA (3–4 players; the match code is already N-participant), part customization, more arenas.

## Known bugs / limits
- 2026-10-03 local two-client verification: Player1/BOLT vs Player2/CRUSHER paired; both HUDs agreed on Player2 HP 329 after 671 damage/38 hits. W/A/D, jump, dash, gun, bomb, and pod inputs exercised for approximately 20 seconds. Client-side disconnect produced OPPONENT LEFT then YOU WIN/results. Cube drop/countdown was not captured, so its exact sequence remains unverified in this run. Studio MCP input/capture was used because cua_repl bound only the original Studio process; disconnect used LocalPlayer:Kick after virtual Escape was rejected and start_stop_play did not disconnect the client. No place scripts or instances edited. End Session closed all three test processes; original place verified in Edit mode. Screens: logs/screens/mc-*.png. No game-script warnings/errors in LogService; Studio automation emitted a CoreGUI mouse-input error (see logs/mc-verification.md). Visual notes: strong bloom on Player2 versus Player1, tiny control captions, overlapping DOWN/DAMAGE/HP labels, and a brief stale queue player count.
- The Studio MCP's virtual gamepad presses arrive as keyboard input, and its virtual touch isn't supported. Because of that, gamepad and touch input were checked through code paths and layout screenshots only. Touch buttons call the same `Battle.DoAction` as keys.
- Lock-on always targets the nearest rival. That is fine for 1v1; FFA will need target cycling.
- In the Studio device simulator, virtual mouse clicks sometimes stop reaching the GUI. Phone menus were checked by layout plus `Menu:FireServer` instead.
- Rematch closes 30 s after Results (`RematchTimeout`). After that only Back to Select is shown.

## IDs
- Place ID: 99842799688877 (published 2026-10-03 under Chase's account @MetavrseBuilder; PUBLIC since 19:20 PT, reach: Ages 16+ and trusted friends)
- Universe ID: 10769245121
- URL: https://www.roblox.com/games/99842799688877
