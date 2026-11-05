Set-Location C:\Users\chase\sc\sugarloaf-canyon
Get-Content -Raw models\_src\brief_pass5b.md | claude -p --model claude-opus-5-5 --dangerously-skip-permissions --output-format text *> models\_src\claude_pass5b.log
"exit $LASTEXITCODE" | Add-Content models\_src\claude_pass5b.log
