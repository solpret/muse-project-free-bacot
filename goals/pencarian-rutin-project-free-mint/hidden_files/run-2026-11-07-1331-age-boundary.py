#!/usr/bin/env python3
"""Age boundary test run 1331: earliest Transfer-from-zero in last 48h
(fromBlock=head-384000) via Ankr getLogs, pageSize 5 (ascending order ->
first log = earliest mint in range). Read-only."""
import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
head=int(ankr_post("eth_blockNumber",[],timeout=30)["result"],16) if isinstance(ankr_post("eth_blockNumber",[],timeout=30).get("result"),str) else None
print("HEAD-ANKR-FAIL?",head)
