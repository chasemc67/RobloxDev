#!/bin/bash
# usage: run_bg.sh <name> <cmd...>  -> runs detached in a screen session, logs to logs/<name>.log
export PATH=$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH
NAME=$1; shift
LOG=$HOME/src/RobloxDev/games/robo-clash-arena/logs/$NAME.log
CMDF=$HOME/src/RobloxDev/games/robo-clash-arena/logs/$NAME.cmd.sh
{ echo '#!/bin/bash'; echo 'export PATH=$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH'; printf '%q ' "$@"; echo " </dev/null > $LOG 2>&1"; echo "echo EXIT_CODE=\$? >> $LOG"; } > $CMDF
chmod +x $CMDF
screen -dmS "$NAME" bash $CMDF
echo "launched $NAME -> $LOG"
