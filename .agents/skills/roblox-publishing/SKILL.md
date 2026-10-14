---
name: roblox-publishing
description: Take a Roblox place from Studio to a live, playable public experience. Covers saving and publishing from Studio, configuring the experience on create.roblox.com (name, description, icon, thumbnails, genre, maturity questionnaire, devices, public access) and checking that it's playable. Mostly UI clicks, so it needs computer use. Use when a game's MVP is playable and ready to ship, or when updating a live game.
---

# Publishing a Roblox game

Most of this is UI work that the Studio MCP can't do. Use **computer use** (Codex computer use, Cursor, or Grok Bot's desktop) on the Mac Mini, where Studio and the browser are already signed in. Don't paste credentials anywhere.

## 1. Before publishing
- Playtest via MCP: `start_stop_play`, then `get_console_output` should show no errors, and `screen_capture` should look right.
- Make sure the core loop works from a fresh join (spawn, UI shows, goal reachable).
- **File > Save to Roblox** (or Save As) in Studio. Studio keeps the version history.

## 2. Publish from Studio
- **File > Publish to Roblox**. The first time, choose *Create new experience* and give it a name and genre. After that, publishing updates the existing place.
- Record the **place ID** and **universe (experience) ID** in `games/<game>/status.md`. Look up the universe ID with:
  `curl -s https://apis.roblox.com/universes/v1/places/<placeId>/universe`
- To publish without Studio (optional, not set up): Open Cloud Place Publishing, `POST https://apis.roblox.com/universes/v1/{universeId}/places/{placeId}/versions?versionType=Published` with an `.rbxl` and an API key. Ask Chase before creating API keys.

## 3. Configure on create.roblox.com
Go to `https://create.roblox.com/dashboard/creations`, open the experience, then **Configure**:
- **Basic info**: name, description (clear pitch plus controls), genre, and **devices** (Computer, Phone, Tablet, Console, VR; enable phone and tablet unless the game needs a keyboard).
- **Icon**: 512×512 PNG. **Thumbnails**: 16:9 screenshots (e.g. 1920×1080). Use Studio `screen_capture` or computer-use screenshots and keep them in `assets/<game>/marketing/`.
- **Maturity & Compliance questionnaire**: must be completed before the game can be public. Answer truthfully based on the content.
- **Audience / Privacy**: set it to **Public** when ready (Private while testing). Check any account or verification prompts and stop to ask Chase if one appears.
- Optional: server size, monetization (passes, products), social links.

## 4. Verify it's live
- Public metadata (no auth needed):
  `curl -s "https://games.roblox.com/v1/games?universeIds=<universeId>"` should show the right name and description, and the experience page `https://www.roblox.com/games/<placeId>` should load.
- Join it once from the Roblox player (or have Chase join) to confirm it's playable outside Studio.
- Update `games/<game>/status.md` with the published version, URL and date.

## Updates
Change in Studio → playtest → File > Publish to Roblox. Publishing updates the live place, and new servers pick it up. Use **Restart servers** on the dashboard for urgent fixes. If something breaks, roll back from the place's version history on the dashboard.

## More than one place in an experience (learned on vr-mini-golf, stage z)
- **Adding a place**: this Studio's Asset Manager ("Places in Experience") has no "Add New Place". Instead, open a local `.rbxl` with the new place's content, then File > **Publish to Roblox As** > pick the existing experience > create a new place. It gets a default name ("<user>'s Place: <date>_1"); rename it in Creator Hub (`create.roblox.com/dashboard/creations/experiences/<universeId>/places`). Never pick the start place in that dialog: that would overwrite it. Codex computer use did this reliably when told the place IDs it must not touch.
- List a universe's places from Studio with `AssetService:GetGamePlacesAsync()` (ids + names), and record them in `games/<game>/places.json`.
- Open a cloud place directly with `open "roblox-studio:1+launchmode:edit+task:EditPlace+placeId:<id>+universeId:<universe>"`, and a local file with `open -a /Applications/RobloxStudio.app <file>.rbxl`. Keep one place open at a time and call `list_roblox_studios` again after each switch (the studio id changes).
- **Quitting Studio on a Team Create place can hang** on "Applying script changes. Studio will close automatically when complete" (seen three times in stage z). Don't press Escape on it. Once the place has been saved and published, it's safe to `kill -TERM` the RobloxStudio process (then `-KILL`).
- If Version History won't open in Studio, read it in Creator Hub: `.../experiences/<universe>/places/<placeId>/version-history` (read-only; don't click Restore).
- TeleportService doesn't work in Studio playtests. Guard teleports with `RunService:IsStudio()` and record the request (an attribute or a log line) so tests can check it.

## Exact version targets (stage au5)
Published-only history does not reveal consumed revision numbers. Before a task that requires an exact next version, inspect both published-only and unfiltered history: a saved/unpublished revision advances the next publish number too. Aurora showed published v4 but already had saved/unpublished v5, so one overwrite produced v6. Report an impossible exact-version target before overwriting; do not restore or republish to try to force the numbering. Preserve screenshots of both histories and save the local copy under the actual published version.
