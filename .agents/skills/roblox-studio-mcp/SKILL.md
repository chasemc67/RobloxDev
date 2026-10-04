---
name: roblox-studio-mcp
description: How to reach and use Roblox Studio's built-in MCP server (StudioMCP) on Chase's Mac Mini to read and change scripts and instances, run Luau, playtest, and capture the screen in an open Studio place. Covers the launch command, verification, the tool list, running it through codex exec from a remote agent, and troubleshooting. Use whenever you need to act inside Roblox Studio.
---

# Roblox Studio MCP

## What it is
Roblox Studio ships its own MCP server: `/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP` ("MCP proxy for Roblox Studio").
- **Transport: stdio.** Launch it with no arguments. (`--stdio` is accepted but does nothing; `-v` turns on verbose logging.)
- Internally, StudioMCP listens on `127.0.0.1:13469` and the running Studio connects to it over a websocket. That port is **not** an MCP HTTP endpoint (`GET /` returns 404), so don't point clients at it.
- Several StudioMCP processes can run at once (e.g. Cursor's plus a `codex exec` one). Extra ones act as proxies to the first.

## Where it's configured
- Codex, `~/.codex/config.toml`:
  ```toml
  [mcp_servers.Roblox_Studio]
  command = "/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP"
  ```
- Cursor, `~/.cursor/mcp.json`:
  ```json
  { "mcpServers": { "Roblox_Studio": { "transport": "stdio", "command": "/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP" } } }
  ```
- Any other MCP client: the same stdio command, with no args or env.

## Requirements
1. Roblox Studio is running, signed in, with the **place open** (not just the start page).
2. MCP is enabled in Studio (Assistant settings; the exact label varies by version). Studio may ask for confirmation on third-party MCP tool calls (`FFlagEnableToolConfirmationforThirdPartyMCP` is on), so a call can wait for a click in Studio.

## Verify it's connected
```bash
codex mcp list                      # Roblox_Studio ... enabled
lsof -nP -iTCP:13469                # RobloxStudio ... ESTABLISHED to StudioMCP
```
Then call `list_roblox_studios`. It should return each open place with an `id`, for example `Place1 — ac40af23-...`. **Most tools need that `studio_id`.** Call `list_roblox_studios` first, and again whenever a call says the studio may have closed.

## From a remote agent (e.g. Grok Bot over SSH or remote shell)
Run Codex non-interactively on the Mac Mini. It starts StudioMCP itself:
```bash
cd /tmp && codex exec --skip-git-repo-check --sandbox read-only \
  "Use the Roblox_Studio MCP. Call list_roblox_studios, then <task>. Report what you changed." </dev/null
```
- This was tested and works (about 40 s round trip). The `--sandbox` flag only limits Codex's local shell. MCP calls still change the Studio place, so state clearly in the prompt whether changes are allowed.
- Give one focused task per run. Ask for a short report (what changed, errors, console output).
- `cursor-agent -p "<prompt>"` (Cursor CLI, same MCP config) should work as an alternative, but it has not been tested yet.

## Tools (28)
- **Discover and inspect**: `list_roblox_studios`, `get_studio_state`, `search_game_tree`, `inspect_instance`, `script_search`, `script_grep`, `script_read`, `get_console_output`, `screen_capture`
- **Edit**: `execute_luau` (run arbitrary Luau in Studio; best for building and batch changes), `multi_edit` (edit scripts), `insert_asset`, `search_asset`
- **Playtest**: `start_stop_play`, `character_navigation`, `user_keyboard_input`, `user_mouse_input`, `wait_job_finished`
- **Generate (AI)**: `generate_mesh`, `generate_procedural_model`, `generate_material`, `generate_texture`, `segment_mesh`, `store_image`, `upload_image`
- **Other**: `http_get`, `skill`, `subagent`

## Working patterns
- Read before writing: use `search_game_tree` and `script_read` before editing.
- Build worlds with `execute_luau` (create Parts and Models, set CFrame, Anchored, Material). Put scripts in the right service: `ServerScriptService` for server code, `StarterPlayer.StarterPlayerScripts` or `StarterGui` for client code, and `ReplicatedStorage` for shared modules and RemoteEvents.
- After changes: `start_stop_play` → `get_console_output` → `screen_capture` → stop play → fix.
- Saving and publishing happen in Studio (File > Save / Publish to Roblox). Use computer use if no tool covers it. See `roblox-publishing`.

## Playtest gotchas (learned on robo-clash-arena)
- `execute_luau` needs `datamodel_type` (`Edit` / `Server` / `Client`) and `studio_id`. `screen_capture` needs a `capture_id`.
- `get_console_output` can be huge. To read only problems, run this in both `Server` and `Client`: `LogService:GetLogHistory()` filtered to `MessageWarning` / `MessageError`.
- `user_mouse_input` clicks are reliable only with `instance_path` (for example `LocalPlayer.PlayerGui.MyUI.Root.Btn_PLAY`). Raw x/y clicks often miss. Give buttons and their containers stable names, and hide the CoreGui chat window or it can steal clicks.
- `user_mouse_input` actions are `moveTo` (with `instance_path`) followed by `mouseButtonClick` with `mouse_button="left"`. There is no `click` action.
- Virtual gamepad keys (`ButtonA` and so on) arrive as keyboard input, and there is no virtual touch. Test touch layout by forcing the touch UI with a temporary flag, then remove the flag.
- Phone layout test: from `Edit`, call `game:GetService("StudioDeviceSimulatorService"):SetDeviceAsync("iphone_17_pro")`, then start play. The playtest gets `TouchEnabled = true`, a 750x361 viewport and a 58 px Roblox top bar. Call `StopSimulationAsync()` when done.
  - `GuiService.TopbarInset` is in screen space, but `AbsolutePosition` is relative to the inset origin. The screen-space top is `AbsolutePosition.Y + GuiService:GetGuiInset().Y`.
  - In the simulator, virtual clicks can stop landing on GUI buttons. Drive menus by firing the game's remotes from `Client` instead.
- `camera.Focus` isn't updated for a Scriptable camera. Measure camera distance from `camera.CFrame` (height above the floor divided by `-LookVector.Y`).
- `screen_capture` lags about 2 s behind the game, so short announcer text is easy to miss. Check timing-critical states numerically from `Client` (attributes, `LocalTransparencyModifier`, `Highlight` values) instead.
- BillboardGuis didn't render in captures. Screen-space frames positioned with `Camera:WorldToViewportPoint` work and look the same.
- For temporary test hooks, use a `BindableFunction` created only when `RunService:IsStudio()` (call it from `Server` `execute_luau`). Delete it before shipping.
- `screen_capture` only returns the image to the agent and can't save a file. It also hides CoreGui (Roblox top-bar buttons, player-list popups), so check real top-left overlap separately. To save PNGs:
  - Find the Studio window id with pyobjc: `uv run --with pyobjc-framework-Quartz`, then `CGWindowListCopyWindowInfo`, owner "Roblox".
  - Capture it with `screencapture -x -o -l<id> win.png`.
  - Crop the game viewport with Pillow. Find the viewport edges from the 2 px blue border in play mode. Its size is `Camera.ViewportSize`, in 1x pixels on a 1080p display.
- Raw x/y in `user_mouse_input` are in GUI space, which excludes the 58 px top bar. Clicks that land on CoreGui are rejected ("hits CoreGUI"). To clear CoreGui popups before window captures, call `StarterGui:SetCoreGuiEnabled(PlayerList/Chat, false)` from `Client`.
- In Edit, the Studio camera re-aims at `camera.Focus`. To frame a shot off-center, move the look-at point and set both `CFrame` and `Focus` to it; offsetting `CFrame` alone gets cancelled.

## Audio
- `search_asset` with `assetType=Audio, scope=creator_store, priceFilter=free` returns a lot of ripped game audio, and `verifiedCreatorsOnly` barely filters. Prefer the licensed library uploads: **ProSoundEffects** (descriptions end "Courtesy of Pro Sound Effects", ids around 9.1e9), **APMOfficial** music, and **Roblox** UI sounds.
- Before using an id, confirm it loads: create `Sound`s, call `ContentProvider:PreloadAsync(list, cb)`, and check that `AssetFetchStatus.Success` and `TimeLength > 0`. Built-in `rbxasset://sounds/` only has a few files (an explosion, jump/land, oof).

## Troubleshooting
- **`list_roblox_studios` is empty**: Studio isn't open, no place is loaded, or MCP is off in Studio. Open the place, check the Assistant MCP setting, and check `lsof -nP -iTCP:13469`.
- **Tool call hangs**: Studio is probably showing a confirmation prompt. Approve it in Studio (computer use) or ask Chase to.
- **Stale studio id**: call `list_roblox_studios` again.
- **Binary missing after a Studio update**: `ls /Applications/RobloxStudio.app/Contents/MacOS/` and run `StudioMCP --help`.
- **Logs**: `~/Library/Logs/Roblox/`. To see the processes: `ps aux | grep -i -E 'RobloxStudio|StudioMCP'`.
