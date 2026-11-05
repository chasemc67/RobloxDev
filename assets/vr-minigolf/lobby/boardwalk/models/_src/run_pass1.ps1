Set-Location C:\Users\chase\bw\boardwalk\models
Remove-Item _src\pass1_exit.flag -EA SilentlyContinue
"$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') pass1 launch (Claude Code claude-opus-5-5 on PC)" | Add-Content _src\PROGRESS.md
$null | claude -p --model claude-opus-5-5 --dangerously-skip-permissions "Execute _src\brief_pass1.md fully and autonomously on this Windows PC, including all OVERRIDE sections at its end (they supersede earlier text). Resume from PROGRESS.md checkpoints if any. Do ALL steps 1-5 without stopping to ask; only finish after _src\pass1_done.flag is written." *> _src\claude_pass1_pc.log
if (!(Test-Path _src\pass1_done.flag)) { "EXITED" | Out-File _src\pass1_exit.flag }
