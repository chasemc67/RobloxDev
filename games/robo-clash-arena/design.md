# Robo Clash Arena

Working public name: **Robo Clash Arena** (no Nintendo trademarks in public text).

## Pitch
Fast 1v1 robot battles in a small enclosed holo-arena, modeled on the Nintendo DS *Custom Robo Arena* battle mode: pick a robot with its own gun / bomb / pod loadout, then out-dash, out-jump and out-shoot your rival (a human via matchmaking, or an AI bot).

## Core loop (per match, 1-2 min)
Robot select -> mode select (Matchmaking vs human | Battle a Bot) -> "READY... FIGHT!" -> dash/jump/strafe, fire gun, lob bombs, deploy pods, knock the rival DOWN -> rival rebirths with invincibility flash -> first to 0 HP loses (or lowest HP% when timer ends) -> results (Rematch / Back to Select).

## Flow / screens
1. Title ("ROBO CLASH ARENA", Press Start / tap). 2. Robot select (3+ robots, stats bars, loadout names, 3D or viewport preview). 3. Mode select: Matchmaking (queue, pairs 2 humans) or Battle a Bot. 4. Battle (HUD: both HP bars, timer, cooldown indicators, down/rebirth state). 5. Results (WIN/LOSE/DRAW, damage dealt, Rematch, Back to Select).

## Battle mechanics (Custom Robo style)
- Small enclosed 3D arena (~110x110 studs), walls + 4-6 obstacles (pillars/blocks/ramp) + 1-2 pits, holo look (Holosseum).
- Camera: high angle (~50-60 deg pitch), follows the midpoint of both robots and zooms to frame both; player-relative movement is camera-relative.
- HP 1000 each. No healing.
- Lock-on: guns/bombs/pods auto-aim toward the opponent (horizontal aim at rival; bombs target rival's position).
- Main gun: unique per robot, with fire cadence / reload (ammo clip + reload time).
- Bomb: arcing lob toward opponent with splash damage + knockback, cooldown.
- Pod: homing/seeking orb or stationary mine, cooldown, limited lifetime.
- Movement: run, ground dash (quick burst, short cooldown), jump + double jump OR air dash (per robot legs).
- Knockback on hits; an "endurance" meter: after enough damage/hits in a short window the robot is knocked DOWN (flies back, lies down ~1.2s, can't act, takes greatly reduced damage), then gets up with REBIRTH invincibility (~3s flashing, can't be damaged). While DOWN: gun unavailable, damage taken greatly reduced (~10-20%), short exploitable window.
- Body dash attack: each body has a dash/charge attack (dashing into the rival deals light damage + knockback).
- Firing/reloading briefly limits mobility (e.g. slowed while firing the gun, short stall on bomb throw).
- Arena hazards: walls, pillars, and 1-2 pits (falling in = ~100 dmg and respawn at a safe point with brief invincibility).
- Opening: robots drop into the arena (optional V1: as cubes that transform) during READY.
- Match ends at 0 HP (KO) or timer (180s, ~3 min like the original) -> higher HP% wins; equal = draw.
- "READY..." (1.5s) "FIGHT!" intro with controls locked until FIGHT.

## Loadout model
Each robot = body (HP stats, dash attack) + gun (right hand, rapid/direct) + bomb (left hand, slower arcing splash, stronger) + pod (delayed/tracking/trap) + legs (speed, jump, air-dash). Keep these as separate data entries in Config so part customization is easy later.

## Robots (phase 3 roster, live in Studio)
Concept picks C01, R05 and C05 (turnarounds, parts sheets and hex palettes in `assets/robo-clash-arena/concepts/`). Exact numbers live in Studio `Config.luau`.

| Robot | Style | Gun | Bomb | Pod | Legs | Dash attack |
|---|---|---|---|---|---|---|
| **Scout** (white/cyan, skater) | all-rounder | Twin Blaster: rapid homing 4-round bursts alternating between the twin barrels | Arc Bomb: lingering splash blast | Sticky Mine: sticks to walls, floor or the rival, then pops | Sprint Legs: fast run + double jump | Jet Tackle |
| **Kitsune** (red robe, fox mask, no legs) | long-range sniper | Spirit Cannon (lantern): tap = homing fireball, hold = big fireball | Foxfire Bomb: three spirit-flame lobs | Paper Charms: three seeking ofuda | Spirit Step: two blink air dashes | Fox Strike |
| **Aero** (round, twin ducted fans) | close-range bruiser | Gale Scatter: 5-way spread | Cluster Bomb: splits into 4 bomblets | Hover Drone: slow, relentless homing drone | Hover Fans: hold jump to hover | Turbine Ram |

### Original V1 roster (archived; replaced in phase 3)
| Robot | Style | Gun | Bomb | Pod | Legs |
|---|---|---|---|---|---|
| **Bolt** (blue, sleek) | all-rounder | Rapid Blaster: fast bullets, 3-round bursts, ~25 dmg each, clip+reload | Standard Bomb: medium arc, 90 dmg splash | Seeker Pod: slow homing orb, 80 dmg, 5s life | balanced speed, double jump |
| **Crusher** (red, bulky) | close-range bruiser | Spread Gun: 5-way fan (shotgun), big knockback at close range | Heavy Bomb: slow, big splash 120 dmg | Mine Pod: stationary proximity mine, 100 dmg, 8s life | slower, strong ground dash, single jump + hover |
| **Lancer** (green/yellow, tall) | long-range sniper | Charge Laser: hold to charge (0.8s), fast piercing beam/bolt 150 dmg + knockdown; tap = weak shot | Triple Bomb: 3 small lobs in a spread | Orbit Pod: 2 orbs that drift toward the rival, 50 dmg each | light, fast air dash |

## Controls
| Action | Keyboard/Mouse | Gamepad | Touch |
|---|---|---|---|
| Move | WASD | Left stick | on-screen thumbstick (left) |
| Gun | LMB / J | R2 / RT (ButtonR2) | big GUN button |
| Bomb | RMB / K | L2 / LT (ButtonL2) or ButtonX | BOMB button |
| Pod | E / L | R1 / RB or ButtonY | POD button |
| Jump / double jump / air dash | Space | A / Cross (ButtonA) | JUMP button |
| Dash | Shift | B / Circle (ButtonB) or L1 | DASH button |
| Camera nudge | (auto) | Right stick small offset | - |
| Menu nav | mouse/click, arrows+Enter | D-pad/stick + A/B with GuiService.SelectedObject | tap |

## Multiplayer (V1 architecture)
Single place, multiple private arenas inside one server: each match clones an arena template to its own offset in Workspace. Matchmaking queue lives on the server and pairs the first two queued humans in that server (Chase + a friend join the same server via "Join" on the friend). Battle a Bot creates a match vs a server-run AI. Server-authoritative: projectiles and hits simulated on the server; HP/state on server; clients only send intents (move is client physics via Humanoid, fire/bomb/pod/dash requests are validated). Match code supports N participants so free-for-all can be added later.
Later: cross-server matchmaking via MemoryStoreService + TeleportService:ReserveServer.

## MVP scope
- 3 robots with distinct looks and loadouts, full flow, bot AI, in-server matchmaking, KB/M + gamepad + touch, effects/sounds/screen shake.

## Later
Free-for-all (4 players), part customization (mix guns/bombs/pods/legs), more arenas, ranked, cross-server matchmaking, cosmetics.

## Art/feel (superseded by ART DIRECTION below)
Bright toy-robot / holosseum style: dark arena floor with neon grid lines, glowing team colors, punchy hit sparks, screen shake on heavy hits, clear readable UI with big fonts.

## Gameplay-video analysis (3 battle clips of Custom Robo Arena): AUTHORITATIVE where it differs from above
- **Camera**: ~45 deg angle tracking BOTH robots; pans and zooms dynamically (zoom in when close, pull back when far).
- **Arena**: floating square or octagonal platform ~4-5x a max dash distance wide, static walls that block movement and shots. Variants have conveyors, ice, hazard pillars emitting expanding damaging pulses. V1: one good arena with walls (+ pillars/pit); a hazard is optional.
- **Movement**: moderate jog pace. Jump = quick leap, ~1.5-2.5s airtime. Ground dash fast and snappy with a motion trail. Air dash repositions horizontally and extends airtime. Legs set number of jumps and air dashes.
- **Gun**: auto-aim lock-on. A pink/red reticle snaps onto the enemy; shots track toward the target, ~0.5-1.5s to cross the arena (projectiles, not hitscan). Examples: 3-round straight burst; 4 rounds that accelerate.
- **Bomb**: high slow arc that clears walls, reaches ~1/2 to 3/4 of the arena. Large spherical blast lingers ~1s. Usable every 2-3s.
- **Pod**: slow deployable (slower than walking) that homes aggressively. Some sit on the ground, some hover. Lasts 4-6s or until contact, then explodes.
- **Hits**: flinch + slight knockback, floating "HIT" text, red damage numbers (e.g. "DAMAGE 278").
- **Down**: 3 pink DOWN pips per robot that hits deplete. At 0 pips, or from a big hit, robot falls flat with "DOWN" text for ~1.5-2s. Then "REBIRTH" with white/transparent flashing and 2-3s invincibility. (Pips refill after rebirth.)
- **HUD**: P1 bottom-left, P2 bottom-right: thick HP bar, numeric HP (1000), down pips. Floating tag over each robot: P1/P2 (or name), HP, down pips. No explicit cooldown rings (a subtle ammo/cooldown hint is fine). Minimap optional.
- **Start**: robots drop in as cubes/capsules, then READY, 3-2-1, LAUNCH! over ~3-4s.
- **End**: time freezes at 0 HP, a big "KO" slams in, winner does a victory pose. "PERFECT" if winner took no damage. Then results.
- **Pacing**: VERY fast. Standard matches ~45-60s, hits land every 3-5s. Tune damage for ~1 minute fights; 3 min timer cap. Robots differ by role: nimble all-rounder, bulky short-range grappler, long-range sniper.

## ART DIRECTION from Chase (2026-10-03, authoritative; added while you were working, apply it)
Style the game to LOOK like Custom Robo for now, with original assets only (no ripped Nintendo assets/logos/names):
- **Robots**: chunky, toy-like, colorful mech robots with bold primary-color armor (big shoulders/helmets, clear silhouettes, contrasting trim, glowing visor/eyes).
- **Arena (Holosseum)**: bright glowing holographic arena floating in a dark or blue digital void; grid floor, neon edges, clean geometric walls/pillars; dark/blue skybox, bloom.
- **UI**: punchy arcade UI with big angled/skewed READY / LAUNCH! / KO / DOWN / REBIRTH text, thick HP bars in the bottom corners (P1 left, P2 right), pink down pips.
- **SFX**: snappy sci-fi sounds.
- Chase may swap assets later. Don't make other asset changes beyond applying this look.

## Phase 3 re-theme (2026-10-03, supersedes the Holosseum look)
- Robots: Blender-built chunky toy meshes (Scout C01, Kitsune R05, Aero C05), each under 20k tris with separately named parts, rigged onto the unchanged hitbox controllers.
- Arena: S04 Homework Desk playset on a wooden desk: green cutting mat with white guide lines, a knee-high toy-brick fence, brick "buildings" as pillars (blue on -X, red on +X), eraser covers, crates, a sticky-note stack and a blue block in the corners, a star emblem in the center, and hazard-striped pits. Same 110x110 collision layout, cover and pits as V1. Desk props (lamp, pencil, notebook, books) stay off the camera side.
- Lobby: warm desk/bedroom (wood desk, mat, corkboard, books, lamp) with lit robot statues on book pedestals.
