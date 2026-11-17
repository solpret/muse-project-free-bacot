#!/bin/bash
# Run 114 inbound leg as 35x ~50-contract slices, 6 parallel per round.
# Lesson from run 109: full-chunk processes died silently ~15 min in; slices are the safe shape.
cd /home/hatch/workspace/narrative-pulse/scan-runs
run_slice() {
  i=$1
  start=$((i*50))
  end=$(( (i+1)*50 ))
  if [ $end -gt 1734 ]; then end=1734; fi
  part=$(printf "s%02d" $i)
  python3 run117-inbound117.py "$part" "$start" "$end" > "run117-inbound117-$part.log" 2>&1
}
for round in 0 1 2 3 4 5; do
  for j in 0 1 2 3 4 5; do
    i=$((round*6+j))
    if [ $i -lt 35 ]; then run_slice "$i" & fi
  done
  wait
  echo "round $round done $(date -u +%H:%M:%S)"
done
echo "ALL SLICES DONE"
ls run117-inbound117-s*.json | wc -l
