until ssh mini '~/bin/unlock-keychain.sh >/dev/null && claude -p "say ok" --model claude-opus-5-5' 2>&1 | grep -qv "session limit"; do sleep 60; done
scp -q prompt.txt mini:/tmp/r6prompt.txt
ssh mini 'mkdir -p ~/src/RobloxDev/games/vr-mini-golf/playtests/round6; cd ~/src/RobloxDev/games/vr-mini-golf && ~/bin/unlock-keychain.sh >/dev/null && claude -p "$(cat /tmp/r6prompt.txt)" --model claude-opus-5-5 --dangerously-skip-permissions'
