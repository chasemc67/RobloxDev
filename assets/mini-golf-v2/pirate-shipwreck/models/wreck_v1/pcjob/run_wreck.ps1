Set-Location C:\Users\chase\sc_fix\wreck1
Get-Content brief_wreck.md -Raw | claude -p --model claude-opus-5-5 --dangerously-skip-permissions *> claude.log
