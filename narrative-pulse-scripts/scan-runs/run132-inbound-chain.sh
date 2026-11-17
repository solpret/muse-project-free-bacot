#!/bin/bash
# Run 132 chained inbound legs (launched ~05:35 WIB, background):
#  (b) run-130 window residual (132445937-132456148), 31 slices
#  (a) run-131 own window (132456149-132466646), 35 slices
#  (c) run-132 own window (132466647-132470262), 35 slices
# Sequential chain; each driver runs 6 slices in parallel per round.
# Run 133 aggregates whatever slices finished; do NOT re-run completed slices.
cd /home/hatch/workspace/narrative-pulse/scan-runs
echo "=== chain start $(date -u +%H:%M:%S) ===" >> run132-inbound-chain.log
echo "--- (b) run-130 residual ---" >> run132-inbound-chain.log
bash run131-inbound-residual-driver.sh >> run132-inbound-chain.log 2>&1
echo "--- (b) done $(date -u +%H:%M:%S) ---" >> run132-inbound-chain.log
echo "--- (a) run-131 window ---" >> run132-inbound-chain.log
bash run131-inbound-driver.sh >> run132-inbound-chain.log 2>&1
echo "--- (a) done $(date -u +%H:%M:%S) ---" >> run132-inbound-chain.log
echo "--- (c) run-132 window ---" >> run132-inbound-chain.log
bash run132-inbound-driver.sh >> run132-inbound-chain.log 2>&1
echo "--- (c) done $(date -u +%H:%M:%S) ---" >> run132-inbound-chain.log
echo "=== chain complete $(date -u +%H:%M:%S) ===" >> run132-inbound-chain.log
