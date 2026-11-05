Set-Location C:\Users\chase\sc_fix\cave22
Get-Content brief_cave.md -Raw | claude -p --model claude-opus-5-5 --dangerously-skip-permissions *> claude.log
