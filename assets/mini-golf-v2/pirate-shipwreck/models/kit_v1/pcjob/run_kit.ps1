Set-Location C:\Users\chase\sc_fix\kit1
Get-Content brief_kit.md -Raw | claude -p --model claude-opus-5-5 --dangerously-skip-permissions *> claude.log
