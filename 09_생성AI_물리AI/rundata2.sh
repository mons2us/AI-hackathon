#!/bin/bash
for s in $(seq 201 208); do GEN_HEAVY=1 python3 -u mkdata.py 40 $s part_$s.npz >> data.log 2>&1; done
echo ALLDONE2 >> data.log
