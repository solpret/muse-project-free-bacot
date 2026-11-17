#!/bin/bash
cd /home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files
echo "=== LEG1 DRIVER 2001 start $(date -u +%H:%M:%S) UTC ==="
python3 run-2026-11-07-2001-reread.py 2>&1 | tee run-2026-11-07-2001-reread.log
echo "REREAD exit: ${PIPESTATUS[0]}"
python3 run-2026-11-07-2001-velocity.py 2>&1 | tee run-2026-11-07-2001-velocity.log
echo "VELOCITY exit: ${PIPESTATUS[0]}"
python3 run-2026-11-07-2001-age-sweep.py 2>&1 | tee run-2026-11-07-2001-age-sweep.log
echo "AGE-SWEEP exit: ${PIPESTATUS[0]}"
echo "=== LEG1 DRIVER 2001 done $(date -u +%H:%M:%S) UTC ==="
