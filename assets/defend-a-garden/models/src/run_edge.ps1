Set-Location C:\Users\chase\sc_fix\edge
Get-Content brief_edge.md -Raw | claude -p --model claude-opus-5-5 --dangerously-skip-permissions *> claude.log
