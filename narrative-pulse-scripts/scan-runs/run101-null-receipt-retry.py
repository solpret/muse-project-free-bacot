#!/usr/bin/env python3
"""Run 101 null-receipt retry (read-only): tx 0x62fb2bb4... (AFeng sale-call,
19:11:45 WIB) returned receipt_null in the receipts pass. Re-fetch via fast_rpc race."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
import fast_rpc
TX = "0x62fb2bb4c86600a50a5f3170a40ea4fcd3156764b5bab268494a0dbfc771fccb"
try:
    r = fast_rpc.race("eth_getTransactionReceipt", [TX])
    print("race result type:", type(r))
    print(json.dumps(r, indent=1)[:2000] if r else "None")
except Exception as e:
    print("ERROR:", e)
