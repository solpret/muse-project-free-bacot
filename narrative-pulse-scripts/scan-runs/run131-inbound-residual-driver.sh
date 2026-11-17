#!/bin/bash
# Run 131 inbound RESIDUAL leg for the run-130 window (132445937-132456148):
# 1537 contracts (slices 300-1733 + 103 failed round-0), 31 slices of ~50, 6 parallel per round.
cd /home/hatch/workspace/narrative-pulse/scan-runs
# Build the residual contract list first (also validates the count).
python3 -c "
import json
allc=json.load(open('run112-inbound-contracts.json'))
agg=json.load(open('run130-inbound-agg.json'))
failed=[f['contract'] for f in agg.get('failed',[])]
res=allc[300:]+[c for c in failed if c not in allc[300:]]
json.dump(res, open('run131-inbound-residual-contracts.json','w'), indent=1)
print('residual contracts:', len(res))
"
run_slice() {
  i=$1
  start=$((i*50))
  end=$(( (i+1)*50 ))
  if [ $end -gt 1537 ]; then end=1537; fi
  part=$(printf "r%02d" $i)
  if [ -f "run131-inbound-res130-$part.json" ]; then echo "skip $part (done)"; return; fi
  python3 run131-inbound-residual.py "$part" "$start" "$end" > "run131-inbound-res130-$part.log" 2>&1
}
for round in 0 1 2 3 4 5; do
  for j in 0 1 2 3 4 5; do
    i=$((round*6+j))
    if [ $i -lt 31 ]; then run_slice "$i" & fi
  done
  wait
  echo "round $round done $(date -u +%H:%M:%S)"
done
echo "ALL RESIDUAL SLICES DONE"
ls run131-inbound-res130-r*.json | wc -l
