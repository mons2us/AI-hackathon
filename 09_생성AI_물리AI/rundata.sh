#!/bin/bash
# 메모리 누수 회피: 40개씩 별도 프로세스
for s in $(seq 101 118); do python3 -u mkdata.py 40 $s part_$s.npz >> data.log 2>&1; done
echo ALLDONE >> data.log
