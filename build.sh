#!/usr/bin/env bash
set -euo pipefail
REC="${1:-$(ls recording/*.webm 2>/dev/null | head -1)}"
DUR="${2:-14}"
mkdir -p out
[ -z "${REC:-}" ] && { echo "No recording found — run 'node capture.js' first."; exit 1; }
echo "▸ recording: $REC   cap: ${DUR}s"

echo "▸ compositing flip-through into laptop screen..."
ffmpeg -y -i "$REC" -i assets/gallery-frame.png -filter_complex \
"[0:v]setpts=0.75*PTS,scale=800:500,fps=30,setpts=PTS-STARTPTS[scr]; \
 color=c=0xF4E8D0:s=1200x900:d=${DUR}[bg]; \
 [bg][scr]overlay=200:330[m]; \
 [m][1:v]overlay=0:0[out]" \
-map "[out]" -t "$DUR" -c:v libx264 -crf 20 -pix_fmt yuv420p -an out/_stage.mp4 -loglevel error

echo "▸ floating in the four badges..."
ffmpeg -y -i out/_stage.mp4 \
 -loop 1 -t "$DUR" -i assets/badge-animated.png \
 -loop 1 -t "$DUR" -i assets/badge-browser.png \
 -loop 1 -t "$DUR" -i assets/badge-noapp.png \
 -loop 1 -t "$DUR" -i assets/badge-swipe.png \
-filter_complex \
"[1]scale=190:190,fade=in:st=8.0:d=0.5:alpha=1[b1]; \
 [2]scale=190:190,fade=in:st=9.0:d=0.5:alpha=1[b2]; \
 [3]scale=190:190,fade=in:st=10.0:d=0.5:alpha=1[b3]; \
 [4]scale=190:190,fade=in:st=11.0:d=0.5:alpha=1[b4]; \
 [0][b1]overlay=952:298[o1]; [o1][b2]overlay=58:600[o2]; \
 [o2][b3]overlay=952:600[o3]; [o3][b4]overlay=58:298[o4]" \
-map "[o4]" -t "$DUR" -c:v libx264 -crf 20 -pix_fmt yuv420p -an out/etsy-final.mp4 -loglevel error

rm -f out/_stage.mp4
echo "▸ done → out/etsy-final.mp4"
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 out/etsy-final.mp4
