#!/bin/bash
cd /workspace/RobloxDev/assets/vr-minigolf/lantern-grove/models
until grep -q ALLDONE /tmp/fly_0.log 2>/dev/null; do sleep 60; done
ffmpeg -y -framerate 12 -pattern_type glob -i 'previews/fly_frames/f_*.png' -vf "minterpolate=fps=24:mi_mode=blend" -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -movflags +faststart previews/flythrough_v1.mp4 > /tmp/fly_enc.log 2>&1
cp previews/fly_frames/f_0000.png previews/flythrough_v1_poster.png
echo ENCODED >> /tmp/fly_enc.log
