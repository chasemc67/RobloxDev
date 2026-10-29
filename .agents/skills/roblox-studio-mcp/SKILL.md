---
name: roblox-studio-mcp
description: How to reach and use Roblox Studio's built-in MCP server (StudioMCP) on Chase's Mac Mini to read and change scripts and instances, run Luau, playtest, and capture the screen in an open Studio place. Covers the launch command, verification, the tool list, running it headless from a remote agent (Claude Code + Opus 5.5 preferred, then codex exec, then cursor-agent), and troubleshooting. Use whenever you need to act inside Roblox Studio.
---

# Roblox Studio MCP

## What it is
Roblox Studio ships its own MCP server: `/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP` ("MCP proxy for Roblox Studio").
- **Transport: stdio.** Launch it with no arguments. (`--stdio` is accepted but does nothing; `-v` turns on verbose logging.)
- Internally, StudioMCP listens on `127.0.0.1:13469` and the running Studio connects to it over a websocket. That port is **not** an MCP HTTP endpoint (`GET /` returns 404), so don't point clients at it.
- Several StudioMCP processes can run at once (e.g. Cursor's plus a `codex exec` one). Extra ones act as proxies to the first.

## Where it's configured
- Claude Code, user scope in `~/.claude.json` (added with `claude mcp add --scope user Roblox_Studio -- /Applications/RobloxStudio.app/Contents/MacOS/StudioMCP`). Check it with `claude mcp list` or `claude mcp get Roblox_Studio`.
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
claude mcp list                     # Roblox_Studio: ... ✔ Connected
codex mcp list                      # Roblox_Studio ... enabled
lsof -nP -iTCP:13469                # RobloxStudio ... ESTABLISHED to StudioMCP
```
Then call `list_roblox_studios`. It should return each open place with an `id`, for example `Place1 — ac40af23-...`. **Most tools need that `studio_id`.** Call `list_roblox_studios` first, and again whenever a call says the studio may have closed.

## From a remote agent (e.g. Grok Bot over SSH or remote shell)
Run an agent CLI non-interactively on the Mac Mini. Each one starts its own StudioMCP. GNU `timeout` isn't installed, so wrap runs in `perl -e 'alarm N; exec @ARGV'`.

### 1. Preferred: Claude Code + Opus 5.5
Runs on Chase's Claude Max subscription (`claude auth status` shows `"authMethod": "claude.ai"`, `"subscriptionType": "max"`). Don't use an API key.
```bash
cd /tmp && perl -e 'alarm 1800; exec @ARGV' \
  claude -p --model opus --dangerously-skip-permissions \
  "Use the Roblox_Studio MCP. Call list_roblox_studios, then <task>. Report what you changed." </dev/null
```
- `--model opus` resolves to **`claude-opus-5-5`**. You can also pin `--model claude-opus-5-5`. Add `--output-format json` to get `result` plus `modelUsage`, which shows the model id.
- `--dangerously-skip-permissions` is required headless, or MCP tool calls stop at a permission prompt. Studio may still show its own confirmation for third-party MCP calls (see Requirements).
- User skills in `~/.claude/skills` (symlink to `~/.agents/skills`) are loaded. Run from `~/src/RobloxDev` instead of `/tmp` to also pick up this repo's `CLAUDE.md`.
- Optional: `ENABLE_CLAUDEAI_MCP_SERVERS=false` hides the claude.ai web connectors (Gmail, Drive, and so on), which otherwise show up and nag about auth.
- Tested 2026-10-03: `list_roblox_studios` round trip took about 7 to 15 s.

### 2. Codex (GPT-6 Astra)
Still used for Studio MCP work, and it's **the tool for computer-use clicks** (`cua_repl`: Studio dialogs, browser logins, dashboards).
```bash
cd /tmp && codex exec --skip-git-repo-check --sandbox read-only \
  "Use the Roblox_Studio MCP. Call list_roblox_studios, then <task>. Report what you changed." </dev/null
```
- This was tested and works (about 40 s round trip). The `--sandbox` flag only limits Codex's local shell. MCP calls still change the Studio place, so state clearly in the prompt whether changes are allowed.
- For computer use, use `--dangerously-bypass-approvals-and-sandbox` and say in the prompt which windows it may touch.

### 3. Fallback: cursor-agent
`cursor-agent -p "<prompt>"` (Cursor CLI, same MCP config). Use it only when the others are unavailable, because Cursor's third-party model quota runs low. Not tested yet.

For all three: give one focused task per run, say whether changes are allowed (`list_roblox_studios` is read-only), and ask for a short report (what changed, errors, console output). If another job is editing a place, don't touch that studio.

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
- If `user_mouse_input` stops reaching the game (no `MouseEnter`/`Activated` on the button), activate a GUI button with gamepad selection instead: from `Client` set `GuiService.SelectedObject = <button>`, then `user_keyboard_input` `keyPress` `Return`. That fires its `Activated` (used by `run_playtests.py smoke` for the course card, stage x).
- A GUI selection left over from the step above (`GuiService.SelectedObject`) swallows later key presses (W won't walk the character). Set it back to `nil` before sending movement keys. Also, W walks the way the camera looks, so after a `PivotTo`, aim the camera too (stage z).
- Top-right top-bar buttons: give their ScreenGui `ScreenInsets = Enum.ScreenInsets.TopbarSafeInsets` (the ScreenGui becomes exactly the free top-bar area), then anchor the button to `(1, 0.5)` at `UDim2.new(1, -8, 0.5, 0)`. With `ScreenInsets.None`, the ScreenGui's origin shifts by the phone safe area, and `TopbarInset` offsets land about 60 px short on an iPhone.
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

## Limits and timing (learned on vr-mini-golf, stage ab)
- **A script's Source is capped at 200,000 characters.** Setting a longer string errors ("Provided string length ... greater than or equal to max length (200000)"), and a push that swallows the error leaves the module empty. Split big generated data into chunk modules (and have the main module `require` them by absolute path, because builders often `require(x:Clone())`, which has no siblings).
- **Terrain collision lags a frame behind `WriteVoxels` / `FillBlock`.** Raycasts in the same `execute_luau` call (with no yield) still see the old surface. `task.wait()` before measuring.
- **The smoothed Terrain surface steps, it doesn't follow occupancy.** A voxel at 0.76 occupancy under full neighbours still read flush with the surface above; 0.5 dropped it a whole 2 studs. To keep Terrain under something, aim ~1.5 studs lower than the occupancy math says, and cap the neighbouring columns too.
- **Team Create places show a NetworkClient in Edit mode.** A computer-use agent may read that as "in a playtest". Say so in its prompt and confirm the mode with `get_studio_state` first.

## Audio
- `search_asset` with `assetType=Audio, scope=creator_store, priceFilter=free` returns a lot of ripped game audio, and `verifiedCreatorsOnly` barely filters. Prefer the licensed library uploads: **ProSoundEffects** (descriptions end "Courtesy of Pro Sound Effects", ids around 9.1e9), **APMOfficial** music, and **Roblox** UI sounds.
- Before using an id, confirm it loads: create `Sound`s, call `ContentProvider:PreloadAsync(list, cb)`, and check that `AssetFetchStatus.Success` and `TimeLength > 0`. Built-in `rbxasset://sounds/` only has a few files (an explosion, jump/land, oof).

## Troubleshooting
- **`list_roblox_studios` is empty**: Studio isn't open, no place is loaded, or MCP is off in Studio. Open the place, check the Assistant MCP setting, and check `lsof -nP -iTCP:13469`.
- **Tool call hangs**: Studio is probably showing a confirmation prompt. Approve it in Studio (computer use) or ask Chase to.
- **Stale studio id**: call `list_roblox_studios` again.
- **Binary missing after a Studio update**: `ls /Applications/RobloxStudio.app/Contents/MacOS/` and run `StudioMCP --help`.
- **`codex exec` hangs with 0 CPU** (seen 2026-10-12 with Homebrew `/opt/homebrew/bin/codex` 0.153.4, even `--version`): use the CLI bundled with the ChatGPT app, `/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex` (0.160.1 worked).
- **Logs**: `~/Library/Logs/Roblox/`. To see the processes: `ps aux | grep -i -E 'RobloxStudio|StudioMCP'`.

## Local import is not an offline asset guarantee (stage af)
- In Studio 0.742, importing FBX with **Upload to Roblox unchecked** still created child RenderMesh assets owned by the signed-in creator. The checkbox controls the inventory Model, not necessarily mesh uploads. Stage af verified all 51 child MeshIds through read-only asset metadata.
- For future strict **zero cloud asset creation** tasks, explain this before importing; do not promise that unchecked means offline. Local `.rbxl` MeshId/MeshContent URI references do not embed their render geometry or grant a different account access. See `games/vr-mini-golf/logs/stages/af-portability.md`.

- VR Mini Golf per-hole tests must pass an explicit `GolfTestOpts.course` (for example `sugarloaf_canyon`) even when only that course is in the place: the spec remote otherwise defaults to Lantern Grove. Require completed-shot counts, not placement-attempt counts, in fuzz and slow-roller evidence.

## Lessons from vr-mini-golf stage sc12
- **Keep CFrame rotations right-handed.** `CFrame.new(x, y, z, R00..R22)` stores a left-handed (det −1) matrix as given in Edit and on the server, but clients receive a different rotation. A collider built that way was in a different place on the client, so the client-simulated ball never met it. Build frames with `CFrame.fromMatrix(pos, X, Y)` (Z = X × Y), or assert det = +1.
- **`AssetService:CreateAssetAsync` is not available from MCP `execute_luau`** ("not available yet"). To persist an edited EditableMesh, export the edit to FBX in Blender and run one 3D Importer pass. Then `MeshPart:ApplyMesh(imported)` and restore Size/CFrame.
- **Importer file dialog over SSH:** Studio swallows some typed letters in the Go-to sheet (e, m, x, v), and the sheet's XPC service can die and freeze the panel; killing `com.apple.appkit.xpc.openAndSavePanelService` cancels the dialog. Opening Desktop/Documents/Downloads triggers a macOS TCC prompt; click **Don't Allow**. What worked: copy the FBX into a temporary home folder that sorts first (for example `~/a_<stage>imp/`), click through the column view, then delete the folder.
- **`upload_image` deduplicates:** a byte-identical PNG returns the existing asset id (no new upload).
- **VisualSeparation and decals:** a Decal/Texture turns a part into a "decal carrier", which the separation pass lifts at least 0.08 above the protected felt visual, measured against the felt's bounding box. On a sloped piece that can float the part by studs (sc12: H10 chevron bars lifted 0.35–1.33). Check positions after Apply before keeping decals on thin felt-level placeholders.

## Lessons from vr-mini-golf stage lg14
- **`upload_image` with local paths fails** ("Only http/https URLs are supported"). Upload PNGs through the Asset Manager's **Import** button instead (temporary `~/a_<stage>imp/` folder, shift-click both files, Open, **Start Import**). To get each id, right-click its Import Queue row and choose **Copy AssetId**, then `pbpaste`. The Asset Manager search doesn't find fresh images. The trash icon above Recent > Uploads is **Clear All** (it clears only the list), and it sits where the refresh button is in other views.
- **Typing goes astray:** `cliclick t:` into the Asset Manager search lost letters and sent the rest to macOS (System Settings > Keyboard opened). Cmd+V is ignored in Studio's Save sheet. Type only short names without e/m/x/v (for example `lg14`), then rename the file in the shell. Diff an inventory afterwards to prove stray keys changed nothing.
- **Don't click the place tab title to focus Studio.** After a publish the tab title gets shorter ("Lantern Grove ×"), so a click at the old title position hits **×** and closes the place. Click an empty toolbar area instead. Recovery: reopen with `EditPlace`, then check that `PlaceVersion` equals the published number and that the inventory matches.
- **A closed place leaves the start page open.** `list_roblox_studios` then has an entry with `"name": null` (`run_playtests.Studio` now skips it). ⌘Q on a place window closes only that place; press ⌘Q again on the start page to quit the app.
- **Top-face Decals on a UV-less MeshPart project straight down** over the bounding-box top. That works for a flat disc whose square texture has transparent corners; SurfaceAppearance needs mesh UVs. For a glow-ish layer, add a second Decal (ZIndex 2) with an alpha-masked image and `Color3` above 1 (overbright, not true emissive). A Top-decal carrier that sits above the felt isn't lifted by VisualSeparation.

## Lessons from vr-mini-golf stage fx1
- **Studio menus without key presses:** `osascript -e 'tell application "System Events" to tell process "RobloxStudio" to click menu item "Publish to Roblox" of menu "File" of menu bar 1'` (also "Download a Copy"). It works while Studio is full screen with the macOS menu bar hidden, and needs no Return.
- **Publishing an unchanged autosave doesn't make a new number.** If nothing changed since Studio's last autosave, Publish marks that autosave version as published (Creator Hub shows its autosave time). Read the number in Creator Hub and don't expect "latest + 1".
- **A macOS "Screen Recording" prompt (`universalAccessAuthWarn`) can sit behind full-screen Studio.** List every on-screen window (Quartz `CGWindowListCopyWindowInfo`), not only Roblox's, before sending keys. Use clicks outside its rectangle and never Return.
- **Chrome can't be scripted with AppleScript here** (error -1743, and don't grant it). Re-run `open -a "Google Chrome" <url>` to reload a Creator Hub page.
- **Geometry audits: mesh/CSG bounding boxes are not surfaces.** One dressing MeshPart's box can span a whole hole and hide every seam under it. Use exact block Parts as occluders only.
- **A local `.rbxl` copy is a safe read-only probe.** Open a copy in `/tmp` with `open -a RobloxStudio.app`, run Luau with `GOLF_STUDIO=<file name>`, then `pkill -KILL -x RobloxStudio` (discards; never answer the save prompt).

## Lessons from vr-mini-golf stage bd1
- **`upload_image` works from a localhost HTTP server.** Copy the PNG into an empty temp dir, run `python3 -m http.server 8765 --bind 127.0.0.1` there, and pass `http://127.0.0.1:8765/<file>.png`. No Asset Manager clicks needed. Byte-identical PNGs still dedupe to the existing id.
- **3D Importer frame:** the "Studio Default" preset imports at 100× (cm) and turned 180° about Y. Place each MeshPart at `root * CFrame.new(fbx_bounds centre) * CFrame.Angles(0, math.pi, 0)` with `Size` = the `tools/fbx_bounds.py` size (sc10/sc12 method), then verify with `EditableMesh` vertices against the target surface.
- **Opt-out from VisualSeparation:** a noncolliding part with attribute `ZF1KeepPose=true` is skipped by `VisualSeparation.Apply` (keeps its exact CFrame/Size). Use it for textured decor meshes sunk into the felt.
- **Team Create "Server did not start [0]"** on EditPlace: click **Retry** in the dialog; the place then opens normally.

## Lessons from vr-mini-golf stage gg1
- **EditPlace opens the latest saved version, not the published one.** Check `game.PlaceVersion` against Creator Hub Version History (with "Show published only" off). An unpublished save made after the last publish means the open place may not be the published one. Diff the inventory before you do any work.
- **Closing a Team Create place saves a new (unpublished) version**, even when nothing was edited (gg1: read-only preflight, then quit, produced LG v38). Say so in the report; it is not a publish.
- **Quit Studio without keystrokes:** `osascript -e 'tell application id "com.roblox.RobloxStudio" to quit'`. It returned "User canceled (-128)", but Studio still quit; confirm with `pgrep -x RobloxStudio`. This avoids sending ⌘Q to a frontmost Chrome.
- **Studio in a full-screen Space can't be captured** with `screencapture -l<id>` ("could not create image from window"). Use MCP `screen_capture` for the viewport. Chrome windows capture fine (`tools/gg1_window.py grab "Google Chrome" out.png`).

## Lessons from vr-mini-golf stage gg2
- **Studio's File menu item is now "Publish"** (and "Publish As"), not "Publish to Roblox": `click menu item "Publish" of menu "File" of menu bar 1` publishes to the open place with no dialog. List the items first if a click fails (`get name of every menu item of menu "File" of menu bar 1`). Read the number in Creator Hub Version History afterwards.
- **"Download a Copy" without typing:** the panel is the window "Download a Copy". Through System Events, `set value of text field "Save As:" of splitter group 1` to a short name, pick the home folder with `click pop up button "Where:"` and then `click menu item "chase-mini" of menu 1`, then `click button "Save"`. Move the file in the shell afterwards. No keystrokes, and no Desktop/Documents TCC prompt.
- **MCP `execute_luau` replies are capped at about 100k characters.** A harness result that is bigger gets cut and won't parse. Keep it in `_G` and fetch it in 40k `:sub()` chunks (`tools/gg2_sweeps.py`).
