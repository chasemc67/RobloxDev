# Stage ac — partial local-copy run (2026-10-12, 19:46–19:56 PDT)

## Completed
- Read game AGENTS.md and applicable workflow skills. No competing stage job was running.
- Studio visually confirmed MetavrseBuilder. `tools/studio_mcp.py list_roblox_studios` responded; the sole open place was lobby 87725688219952, PlaceRole `lobby`, PlaceVersion 246.
- Used File > Download a Copy (the cloud-place File menu has no Save to File entry). Studio unexpectedly performed a cloud save first: Output showed “Saving to Roblox…” and “Saved new changes … to Roblox.” No scripts or instances had been edited.
- Read Studio Version History: v247 was newly saved and unpublished; v246 retained its Published badge. Renamed the downloaded local file to `playtest-lobby-v247.rbxl` so it does not claim to be the exact v246 revision. It is 828199 bytes; checksum in playtests/stage-ac/result.json.
- Closed lobby before opening Lantern Grove 91438142503824 from Creator Hub. MCP verified PlaceRole `lantern_grove`, PlaceVersion 9; Studio Version History showed v9 Published. No changes or save were made there.
- Investigated Version History > Open local copy as an alternative. Did not invoke it with a cloud place open because that could open another place. Closing the cloud place also dismissed its Version History window, so this attempt did not yield a local copy.
- Stopped further cloud-save operations after the unexpected lobby save. Studio was closed: process query found no RobloxStudio app process and MCP returned an empty studios list.

## Incomplete and limits
- Required exact ab copies are incomplete: lobby is an unchanged-content download labeled v247, not a verified byte-identical v246 copy; LG and SC copies were not saved.
- Sugarloaf was not opened. Aurora converter/modules, local test place, blockout import, animations, and screenshots were not created.
- Every Aurora hole H01–H18: cupdrop NOT RUN; stuck sweep NOT RUN; escapes, lost balls, and stuck flags UNKNOWN. Clearance and Play-console checks NOT RUN. No zero-failure claim is made.
- `playtests/stage-ac/result.json` records per-hole NOT_RUN entries and the copy checksum.
- Nothing was published, no new Roblox place was created, and place 135374506016678 was not opened or touched. No binaries are staged, and no git push was attempted.
- To resume, resolve a local-only export method compatible with one open place before repeating cloud downloads. Studio's Download a Copy behavior is the observed blocker, not sign-in or MCP connectivity.

## Prior attempt notes (preserved)

# Stage ac — preflight failure (2026-10-12)

- No competing stage job found; the matching `codex exec-server` process belongs to the ChatGPT desktop infrastructure.
- Launched Roblox Studio and visually confirmed `Welcome, MetavrseBuilder`.
- Opened the existing VR Mini Golf cloud experience from Recent Experiences. Studio failed to join place 87725688219952: `Unable to verify collaboration eligibility for universeId 10769274294, with error code -1`.
- Studio MCP responded with an empty studios list; no place loaded, so PlaceRole could not be verified.
- Stopped at preflight as instructed. No retries, place edits, publishing, new places, asset imports, or tests. Place 135374506016678 was not touched.
- Closed Studio; process check confirmed no RobloxStudio application process remained.
- No local playtest copies were created or verified. Cupdrop and stuck-ball results are unavailable (not run). No commit or push was made.

RESULT=FAIL PREFLIGHT TEAM_CREATE_COLLABORATION_ELIGIBILITY_ERROR_-1
