# Personal best: live DataStore test (stage n, 2026-10-11)
Studio access to API services: OFF -> ON (Codex, Game Settings > Security; other toggles unchanged, logs/codex-api-access-n.log).
Store VRMiniGolf_PB_v1 (the universe's real DataStore), test key u_-424242 (mock player, no real account touched), Play-mode Server,
workspace PBInStudio = true for the test only (removed afterwards). Each session is a fresh clone of GolfServer.PersonalBest (= a new server).

| Step | Result |
|---|---|
| raw GetAsync before | nil |
| s1 load | SettingsLoaded, best nil |
| s1 recordRound 30 | best 30, new true, prev nil; raw `{"best":{"lantern_grove":30}}` |
| s2 load (fresh module) | best 30, player attribute Best_lantern_grove 30 |
| s2 recordRound 33 | best 30, new false, prev 30 |
| s2 recordRound 26 | best 26, new true, prev 30; raw `{"best":{"lantern_grove":26}}` |
| s3 load (fresh module) | best 26 |
| cleanup RemoveAsync | raw nil |
| real Studio player | SettingsLoaded true (loaded from the real store), Best nil |

0 console errors/warnings. **PASS**: save and load of the personal best work against the live DataStore.
