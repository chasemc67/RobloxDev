# Custom Robo Arena — battle mechanics brief

- **Battle setup / Holosseum:** Fights occur in 3-D arenas called *Holosseums*. A Robo starts as a cube fired from a Robo Cannon; the cube's landing side affects how quickly it transforms and becomes combat-ready, so the opening can confer an advantage. Holosseums use cover and hazards: walls, pillars, fences, holes/pits or lava, and (depending on stage) conveyors, tilting floors, rising water/magma, destructible terrain, or other moving obstacles. Use cover to break lines of fire and avoid falling/being pushed into hazards.
- **Win condition and length:** Each Robo normally starts at **1,000 HP**. Reduce the opponent to 0 (KO), or win on HP when time expires. Standard bouts are about **3 minutes**, commonly played best-of-three.
- **Loadout:** A Robo is built from a **body, gun, bomb, pod, and legs**. The body supplies the chassis' basic stats and its model-specific dash/charge attack. The gun is the right-hand primary weapon (usually rapid and comparatively direct); guns vary in damage, speed, homing, rate of fire, and knockdown power. The bomb is the left-hand secondary weapon (typically slower, larger/spreading, and stronger); bombs vary in trajectory, blast size/time, damage, and knockdown. The pod launches a delayed/tracking/trap-like attack from the back; pods vary in homing, spread, duration, and placement. Legs alter ground speed, jump/air movement, endurance/mobility, and air-dash behavior.
- **Movement / attacks:** Robos run, jump, perform limited air-dashes (class-dependent), and use gun, bomb, pod, and body dash attacks. Movement and attack timing matter because firing/reloading can briefly limit mobility. Arena geometry is part of the matchup: short-range builds like confined cover-heavy layouts, while long-range builds benefit from sightlines and elevated/open sections.
- **Down / knockdown / rebirth:** In addition to HP, each Robo has endurance. Taking enough impact/damage in a short window depletes endurance and causes a **Down** state: the Robo falls/staggers and its primary gun is unavailable; damage while down is greatly reduced, but the vulnerable window can be exploited quickly. After getting up it enters **Rebirth**, with roughly **3 seconds of invincibility**, preventing an endless down-lock. The goal is to front-load damage before the down, then capitalize immediately before rebirth.
- **Holosseum-specific play:** Stages can include ordinary walls/pillars and dangerous holes/pits, plus dynamic hazards such as rising magma/water, conveyors, tilting floors, or shrinking/destructible platforms. Some stages give a “field advantage” to particular ranges or weapon behaviors.

## Sources consulted

- https://customrobo.fandom.com/wiki/Custom_robo (loadout, 1,000 HP, down/rebirth, Holosseum start)
- https://customrobo.fandom.com/wiki/Custom_Robo_gameplay (battle objective and down/rebirth summary)
- https://wiki-origin.giantbomb.com/wiki/Games/Custom%5FRobo%5FArena (attack roles, movement, obstacles, Holosseum, rebirth)
- https://gamefaqs.gamespot.com/ds/930297-custom-robo-arena/faqs/55916 (downed damage reduction and combo window)
- https://www.pocketgamer.com/custom-robo-arena/review/ (3-minute best-of-three format and Holosseum presentation)
- https://customrobo.fandom.com/wiki/Field_Advantage and https://customrobo.fandom.com/wiki/Magma_Ruins (arena hazards/field effects)

## ART DIRECTION from Chase (2026-10-03, authoritative; added while you were working, apply it)
Style the game to LOOK like Custom Robo for now, with original assets only (no ripped Nintendo assets/logos/names):
- **Robots**: chunky, toy-like, colorful mech robots with bold primary-color armor (big shoulders/helmets, clear silhouettes, contrasting trim, glowing visor/eyes).
- **Arena (Holosseum)**: bright glowing holographic arena floating in a dark or blue digital void; grid floor, neon edges, clean geometric walls/pillars; dark/blue skybox, bloom.
- **UI**: punchy arcade UI with big angled/skewed READY / LAUNCH! / KO / DOWN / REBIRTH text, thick HP bars in the bottom corners (P1 left, P2 right), pink down pips.
- **SFX**: snappy sci-fi sounds.
- Chase may swap assets later. Don't make other asset changes beyond applying this look.
