#!/bin/bash
# Run 133 chained inbound legs (launched ~06:25 WIB, detached via setsid):
#  (b) run-130 window residual (132445937-132456148), 31 slices
#  (a) run-131 own window (132456149-132466646), 35 slices
#  (c) run-132 own window (132466647-132470262), 35 slices
#  (d) run-133 own window (132470263-132478154), 35 slices
# Sequential chain; each driver runs 6 slices in parallel per round.
# LESSON run 132: chain launched via exec background:true DIED mid-round-0
# (~2 min in, slices r00-r05 killed, 0 JSON written) - launch this one with
# setsid so it survives the launching exec session / turn end.
# Run 134 aggregates finished slices; do NOT re-run completed slices.
cd /home/hatch/workspace/narrative-pulse/scan-runs
echo "=== chain start $(date -u +%H:%M:%S) ===" >> run133-inbound-chain.log
echo "--- (b) run-130 residual ---" >> run133-inbound-chain.log
bash run131-inbound-residual-driver.sh >> run133-inbound-chain.log 2>&1
echo "--- (b) done $(date -u +%H:%M:%S) ---" >> run133-inbound-chain.log
echo "--- (a) run-131 window ---" >> run133-inbound-chain.log
bash run131-inbound-driver.sh >> run133-inbound-chain.log 2>&1
echo "--- (a) done $(date -u +%H:%M:%S) ---" >> run133-inbound-chain.log
echo "--- (c) run-132 window ---" >> run133-inbound-chain.log
bash run132-inbound-driver.sh >> run133-inbound-chain.log 2>&1
echo "--- (c) done $(date -u +%H:%M:%S) ---" >> run133-inbound-chain.log
echo "--- (d) run-133 window ---" >> run133-inbound-chain.log
bash run133-inbound-driver.sh >> run133-inbound-chain.log 2>&1
echo "--- (d) done $(date -u +%H:%M:%S) ---" >> run133-inbound-chain.log
echo "=== chain complete $(date -u +%H:%M:%S) ===" >> run133-inbound-chain.log
