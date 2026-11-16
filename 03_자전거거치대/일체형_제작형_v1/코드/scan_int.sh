#!/bin/bash
cd /tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/opt
for F in ${FTS:-95 80}; do
  TAG=int35f${F}${SFX} AM=${AM:-1} RF=${RF:-5} ETAE=${ETAE:-0.6} TILT=35 FT=$F TLIM=21 DLIM=0.3 ITERS=120 SCHED='{"0":1,"20":2,"40":4,"60":8,"80":16,"100":32}' python3 opt_int.py > int35f${F}${SFX}.log 2>&1
done
