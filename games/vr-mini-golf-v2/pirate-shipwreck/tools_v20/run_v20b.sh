#!/bin/zsh
cd ~/stage && mkdir -p shots14
~/bin/unlock-keychain.sh >/dev/null 2>&1
claude -p --model claude-opus-5-5 --dangerously-skip-permissions "$(cat ~/stage/v20b_prompt.md)" < /dev/null > ~/stage/v20b_claude.log 2>&1
echo "exit $?" >> ~/stage/v20b_claude.log
