#!/bin/bash
# resumable: rerun anytime; skips finished frames
cd /workspace/RobloxDev/assets/vr-minigolf/lantern-grove/models
w(){ for i in 1 2 3 4 5; do /home/box/.local/bin/blender -b --factory-startup -P _src/flythrough.py -- --taa 2 --step 2 --start $1 --end $2 >> /tmp/fly_$1.log 2>&1; done; }
w 0 1824
echo ALLDONE >> /tmp/fly_0.log
