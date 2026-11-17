#!/bin/bash
# *** DO NOT RUN - DEAD PATTERN (run 134 verdict) ***
# This wait-loop chain shape dies when its launching exec session ends
# (~5 min in; run-132 chain pid 6141 and run-133 chain pid 23588 both died
# in residual round 0 with 0 slices finished). The working shape is:
# launch each 6-slice round as detached nohup python processes (no wait),
# e.g. `nohup python3 -u run131-inbound-residual.py r06 300 350 > ... &`
# Drivers now skip finished slices (skip-if-exists). Run 135: aggregate
# r00-r11, then launch round 2 (r12-r17) detached. Kept for reference only.
# Run 134 chained inbound legs (SUPERSEDED - see header above):
#  (b) run-130 window residual (132445937-132456148), 31 slices
#  (a) run-131 own window (132456149-132466646), 35 slices
#  (c) run-132 own window (132466647-132470262), 35 slices
#  (d) run-133 own window (132470263-132478154), 35 slices
#  (e) run-134 own window (132478155-<max_block>), 35 slices
# Sequential chain; each driver runs 6 slices in parallel per round.
# LESSON runs 132+133: chains died mid-round-0 of leg (b) both times (run132:
# exec background:true; run133: setsid, pid 23588, verified alive after launch,
# 0 slices finished, dead by run 134). Run 134 aggregates finished slices;
# do NOT re-run completed slices. If this chain also dies, the inbound leg
# needs a foreground-slice approach inside a run instead of a background chain.
cd /home/hatch/workspace/narrative-pulse/scan-runs
echo "=== chain start $(date -u +%H:%M:%S) ===" >> run134-inbound-chain.log
echo "--- (b) run-130 residual ---" >> run134-inbound-chain.log
bash run131-inbound-residual-driver.sh >> run134-inbound-chain.log 2>&1
echo "--- (b) done $(date -u +%H:%M:%S) ---" >> run134-inbound-chain.log
echo "--- (a) run-131 window ---" >> run134-inbound-chain.log
bash run131-inbound-driver.sh >> run134-inbound-chain.log 2>&1
echo "--- (a) done $(date -u +%H:%M:%S) ---" >> run134-inbound-chain.log
echo "--- (c) run-132 window ---" >> run134-inbound-chain.log
bash run132-inbound-driver.sh >> run134-inbound-chain.log 2>&1
echo "--- (c) done $(date -u +%H:%M:%S) ---" >> run134-inbound-chain.log
echo "--- (d) run-133 window ---" >> run134-inbound-chain.log
bash run133-inbound-driver.sh >> run134-inbound-chain.log 2>&1
echo "--- (d) done $(date -u +%H:%M:%S) ---" >> run134-inbound-chain.log
echo "--- (e) run-134 window ---" >> run134-inbound-chain.log
bash run134-inbound-driver.sh >> run134-inbound-chain.log 2>&1
echo "--- (e) done $(date -u +%H:%M:%S) ---" >> run134-inbound-chain.log
echo "=== chain complete $(date -u +%H:%M:%S) ===" >> run134-inbound-chain.log
