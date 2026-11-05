#!/bin/zsh
# usage: shoot14.sh <name.png>   (run after the camera script and a 3 s wait). Captures the whole screen then crops to the 3D viewport only.
# Viewport rectangle in screen pixels comes from ~/stage/vp14.env (VX VY VW VH), calibrated once by the build.
source ~/stage/vp14.env
mkdir -p ~/stage/shots14
screencapture -x ~/stage/shots14/.full.png
sips -c $VH $VW --cropOffset $VY $VX ~/stage/shots14/.full.png --out ~/stage/shots14/$1 >/dev/null 2>&1
echo "shot $1 $(sips -g pixelWidth -g pixelHeight ~/stage/shots14/$1 | tr '\n' ' ')"
