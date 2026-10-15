# Stage lbcheck: does a fresh join of the live game land in the lobby? (read-only)

Oct 14, 2026, 11:50 PM to 11:59 PM PT, on the Mac Mini. No Studio sessions opened, nothing saved or published, no settings changed, no permissions granted, no Robux spent.

## Preflight (Creator Hub, read-only)
- **Start place: 87725688219952 ("VR Mini Golf").** It's the starred place on Places for universe 10769274294 (`lbcheck-places.png`). The develop API lists the universe's places as 87725688219952 VR Mini Golf, 79649062523043 Aurora Archipelago, 91438142503824 Lantern Grove and 124440050576723 Sugarloaf Canyon. `apis.roblox.com/universes/v1/places/87725688219952/universe` returns 10769274294.
- **Lobby's latest published version: 251** (Oct 13, 2026, 9:58 PM). v252 (Oct 13, 10:33 PM) is a save only, with no published check (`lbcheck-versions.png`).
- The public games API returns `isContentRestricted: true` / "[TITLE UNAVAILABLE]" for this universe. The player also shows a "Ready to playtest?" banner, so the experience isn't fully public yet. This didn't block the joins.

## Joins
Each join launched with `open "roblox://experiences/start?placeId=87725688219952"`.

| Join | Fresh process | PlaceId (player log) | IsTeleport | Scene | Result |
|---|---|---|---|---|---|
| 1 (`lbcheck-join1.png`) | yes (PID 9426, new launch) | 87725688219952, job ac279c9f | false | Plank boardwalk deck with rail, windmill, signpost, crystal arch and autumn tree arch. Title menu open (Play / Settings / How to play) with the text "Close (X) to walk around the lobby, or walk through an arch". No golf HUD, ball or holes. | **LOBBY** |
| 2 (`lbcheck-join2.png`) | yes (PID 10128) | 87725688219952, job 9d4d7bb5 | false | Same lobby deck view, same menu open | **LOBBY** |
| 3 (`lbcheck-join3.png`) | yes (PID 10006) | 87725688219952, job 9d4d7bb5 | false | Same lobby deck view, same menu open | **LOBBY** |

- Spawn: in all three joins the camera sits at deck height facing north up the boardwalk, toward the arches and the windmill. The view was identical in a second screenshot about 15 to 20 s later, so the character wasn't falling or moving. No Lantern Grove Welcome Plaza or hole 1 tee was visible.
- The player is signed in as **MetavrsePlumber** (UserId 2021224569), not MetavrseBuilder as the brief said.
- Retries, recorded for honesty:
  - The first tries at joins 2 and 3 ran in the same RobloxPlayer process (`pkill` didn't stop it). Each started a new server (job f1053805, then the same job 8f0bf271) and both landed in the same lobby, but they weren't counted as fresh joins.
  - The next try at join 2 opened the Roblox home page instead of the game, because the player had just auto-updated from 0.742.460 to 0.743.0 and dropped the deep link (`lbcheck-join2-retry0-homepage.png`). This was a launcher issue, not a game result.
  - Join 2 was then redone in a fresh process and is the row above.
- Afterwards: the Roblox player was quit. No RobloxPlayer, Roblox.app helpers or RobloxStudio process remain. Only the StudioMCP bridge processes left by other sessions are still running.

## Conclusion
**LOBBY (fixed).** 3/3 fresh joins of start place 87725688219952 (lobby v251) put the player on the lobby boardwalk deck with the title menu open. None of them went to a course.

CHECK DONE, ROBLOX CLOSED
