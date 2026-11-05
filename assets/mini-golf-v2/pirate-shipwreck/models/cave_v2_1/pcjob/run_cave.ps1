Set-Location C:\Users\chase\sc_fix\cave21
Get-Content brief_cave.md -Raw | claude -p --model claude-opus-5-5 --dangerously-skip-permissions *> claude.log
