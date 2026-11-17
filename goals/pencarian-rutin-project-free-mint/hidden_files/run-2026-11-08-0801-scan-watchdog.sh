#!/bin/bash
# Watchdog: kill scan if progress log silent >300s, hard cap 780s from start.
BASE=/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files
LOG=$BASE/run-2026-11-08-0801-scan-progress.log
PID=$1
START=$(date +%s)
while kill -0 $PID 2>/dev/null; do
  NOW=$(date +%s)
  ELAPSED=$((NOW-START))
  if [ $ELAPSED -gt 780 ]; then
    echo "WATCHDOG: hard cap 780s reached, killing scan pid $PID" >> $LOG
    kill -9 $PID 2>/dev/null
    break
  fi
  if [ -f "$LOG" ]; then
    MTIME=$(stat -c %Y "$LOG")
    SILENT=$((NOW-MTIME))
    if [ $SILENT -gt 300 ]; then
      echo "WATCHDOG: no log progress for ${SILENT}s (>300s), killing scan pid $PID" >> $LOG
      kill -9 $PID 2>/dev/null
      break
    fi
  fi
  sleep 30
done
echo "WATCHDOG done elapsed $(( $(date +%s) - START ))s" >> $LOG
