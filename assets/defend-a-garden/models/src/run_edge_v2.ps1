Set-Location C:\Users\chase\sc_fix\edge2
Get-Content brief_edge_v2.md -Raw | claude -p --model claude-opus-5-5 --dangerously-skip-permissions *> claude.log
