#!/bin/bash
# Run 111 inbound leg, remaining slices s18-s34 (contracts 900-1733).
# Round 3 slices died with the parent exec session; re-run detached via setsid/nohup.
cd /home/hatch/workspace/narrative-pulse/scan-runs
run_slice() {
  i=$1
  start=$((i*50))
  end=$(( (i+1)*50 ))
  if [ $end -gt 1734 ]; then end=1734; fi
  part=$(printf "s%02d" $i)
  python3 run111-inbound110.py "$part" "$start" "$end" > "run111-inbound110-$part.log" 2>&1
}
for round in 3 4 5; do
  for j in 0 1 2 3 4 5; do
    i=$((round*6+j))
    if [ $i -lt 35 ]; then run_slice "$i" & fi
  done
  wait
  echo "round $round done $(date -u +%H:%M:%S)"
done
echo "ALL REMAINING SLICES DONE"
ls run111-inbound110-s*.json | wc -l
