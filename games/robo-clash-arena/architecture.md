# Robo Clash Arena: architecture

Studio is the source of truth (place 99842799688877). Scripts are authored in `~/src/rca-work/src`, which mirrors the Studio hierarchy outside this repo. They are pushed into the open place with `~/src/rca-work/push.sh`, which lints with luau-lsp and bundles an `.rbxmx`. Then run the one-liner it prints in the Edit datamodel, with play stopped. The arena and robot builders also live in `assets/robo-clash-arena/`.

## Layout in Studio
```
ReplicatedStorage/RoboClash
  Config            all tunables: Match timings, robots + parts (Bodies/Guns/Bombs/Pods/Legs), colors, Sounds
  Remotes/          Match, FX (server->client), Intent, Menu (client->server) RemoteEvents
  Shared/Mover      robot locomotion (run, jump/air jump/hover, ground + air dash, knockback); runs on the physics owner
  Shared/ProjectileSim  deterministic projectile paths (homing guns, arcing bombs, slow pods), shared by server + client FX
  Shared/Util
ServerScriptService/RoboClash
  Main.server       remote wiring, intent validation + token-bucket rate limit, Heartbeat -> MatchService.Step
  MatchService      sessions (Menu/Queue/Match/Results), Match objects, arena slots, intro/fight/KO/results, rematch groups, leave handling
  MatchmakingService  FIFO in-server queue; pairs two humans into a PvP match
  CombatService     server-authoritative weapons, damage, endurance -> DOWN -> REBIRTH, pits, dash attacks, FX events
  BotAI             CPU opponent (range keeping, strafing, dodges, reaction delay + aim error)
  RobotSpawner      clones a robot template from ServerStorage/RoboClash/Robots, reads its fixed hitbox attributes, sets up the Humanoid
ServerStorage/RoboClash/Robots          built robot templates (Scout, Kitsune, Aero): invisible hitbox root + Motor6D pivots + welded visual MeshParts
ServerStorage/RoboClash/ArenaTemplate   Homework Desk arena (Geometry = collidable, Decor = visuals, Spawns)
ServerStorage/RoboClashAssets/Meshes    imported Blender meshes: Scout, Kitsune, Aero, DeskProps
ServerStorage/RoboClashTools            editor-only modules: Sync (applies pushes), Rebuild/WorldBuilder/RobotBuilder/RobotRigs (regenerate robots, arena, lighting, lobby, statues)
StarterPlayerScripts
  ClientMain.client  creates ScreenGuis (BG / World overlay / HUD / UI, each with a 1280x720 UIScale root, or 1100x600 on screens under 560 px tall such as phones), routes Match remote events
  RoboClashClient/
    UI         Title, Robot Select (lobby statues), Mode Select (+ per-input HOW TO PLAY panel), Queue overlay, Results; gamepad SelectedObject + B back + re-select when cleared
    Battle     input (CAS: KB+M, gamepad, touch) -> local Mover + Intent remotes, lock-on, auto-zoom camera (fit feet..head per robot, dist 32..105, larger margins on touch), cube intro, KO camera, wall fades, center-emblem fade under the HUD
    HUD        P panels (local bottom-left, rivals bottom-right; on touch: top corners at 0.78 scale, below the Roblox top bar), timer, chips, tags, reticle, HIT/DAMAGE, announcer
    FX         client visuals for server events (projectiles, blasts, sparks, dash trails, shake, flashes) + sound cues
    RobotAnim  procedural Motor6D animation (run, recoil, throw, flinch, DOWN, victory) + REBIRTH flashing
    Touch      dynamic stick (left) + GUN with POD/JUMP/DASH/BOMB on an arc (right); calls Battle.DoAction like keys do
    Sound, State, Style
```

## Art pipeline (robots and desk props)
1. `assets/robo-clash-arena/blender/make_<robot>.py` (shared helpers in `rca_common.py`) builds each model headless, authored in Roblox coordinates (1 stud = 1 unit, forward -Z). Each model is written to `export/<robot>.fbx`, with a `_preview.png` and a `_rig.json` (joints + attachments). `make_props.py` does the same for the desk props.
2. `blender/gen_rigs.py` turns the `_rig.json` files into `RobotRigs.luau`.
3. The FBX files are imported through Studio's 3D Importer (driven by Codex, `games/robo-clash-arena/codex_import.sh`) and moved to `ServerStorage/RoboClashAssets/Meshes/<Id>`.
4. In Edit, `Rebuild('robots')` runs `RobotBuilder.BuildAll`. Visuals are Massless, CanCollide/CanQuery/CanTouch off, CollisionFidelity Box. The hitbox root size, HipHeight and `HitRadius/CapDown/CapUp` attributes are fixed per robot, so the meshes never change balance.
5. `RobotAnim` drives the joints: idle/run/recoil/throw/DOWN/REBIRTH/victory, plus extra joints tagged `Anim` = spin (Aero fans), wobble (Kitsune tail), and glow pulses (visors, flames). Config `GlowTint` recolors Neon glow meshes per limb.

`Rebuild('arena' | 'lobby' | 'lighting')` regenerates the world from `WorldBuilder.luau`. Delete `workspace._ArenaPreview` if you made one, because it sits where match arena slot 0 goes.

## Data flow
1. **Menu.** Client `Menu:FireServer(action)` with action `Select`, `Queue`, `CancelQueue`, `Bot`, `Rematch`, or `Back`. The server owns session status and replies on the `Match` remote (`Queue`, `Start`, `Rematch`, `Results`).
2. **Match start.** `MatchService.Create(specs, mode)` clones `ArenaTemplate` into `workspace.Arenas` at its own X slot (`ArenaBaseX + slot * ArenaSpacing`). This gives each match a private arena on one server. It then spawns a robot per spec and fires `Start`, which carries the roster, spawns, center, and timings. Clients run the cube drop-in and READY 3-2-1 from server time, and the server fires `Launch` with `endTime`.
3. **Movement.** Each player's client owns its robot's physics through network ownership and runs `Shared/Mover`. Bots run the same Mover on the server. The server computes knockback and sends it to the owning client as a `Knock` message on the `Match` remote.
4. **Combat.** The client sends intents only: `GunDown`, `GunUp`, `Bomb`, `Pod`, and `Dash{dir, air}`. `Main` checks the action name, the payload types, and the per-player rate limit. `CombatService` checks state, cooldowns, and ammo, simulates projectiles with `ProjectileSim`, and applies all damage, endurance, DOWN, and REBIRTH on the server. Clients get `FX` events (`Fire`, `Proj`, `ProjSync`, `ProjEnd`, `Blast`, `Hit`, `Down`, `Rebirth`, `Dash`, `Charge`, `Pit`, `ClearProj`) and only draw them.
5. **End.** KO, timer expiry (higher HP% wins; equal is a DRAW), or the last team left standing triggers `Match:Finish(reason, winner)`. The reason is `KO`, `TIME`, or `LEFT`. The server fires `Match:KO`, poses the winner (`Pose=Victory`), and sends `Results` with per-player stats after `ResultsDelay`. Rematch needs every human in the group to accept. If anyone leaves, the group closes with "Opponent left".
6. **Leaving.** `PlayerRemoving` calls `MatchService.DropCombatants`. If one team remains it wins by `LEFT`, and a match with no humans left is torn down and its arena destroyed.

## N participants / FFA
Matches are already N-sized. `specs` is a list, each participant gets its own `team = index`, the template has 4 spawns, the HUD stacks rival panels, and `aliveTeams()` decides the winner. To add FFA:
- Add a queue mode that pops 3–4 entries in `MatchmakingService.tryPair`.
- Add a Mode Select button.
- Lock-on should cycle targets. `Battle` currently picks the nearest live rival.
- For teams, assign the same `team` value to teammates.

## Tuning
Everything lives in `Config`.
- `Match.DamageScale` (0.7) is the global pacing knob. Bot fights run about 45–60 s.
- Per-weapon numbers live in the part tables.
- Bot difficulty is set at the top of `BotAI` (aim error, turn rate, reaction time, fire gaps).
- Sounds are `Config.Sounds`. These are free Creator Store audio ids (mostly Pro Sound Effects, APM, and Roblox uploads), each confirmed to load through `ContentProvider`. Volume and pitch per sound are in `Sound.luau`.
