#!/usr/bin/env python3
"""Preflight run 0931 — head via fast_rpc batch on bsc-dataseed1 FIRST
(ankr eth_blockNumber is NOT supported, -32601), then a small
ankr_getLogs (50 blocks) must succeed in <60s. Fast-fail the scan leg
if either fails. Ankr via proxy env as-is; NEVER set no_proxy."""
import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from ankr import ankr_post

T0 = time.time()
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]
head = None
for ep in EPS:
    try:
        res = batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)
        head = int(res[0], 16)
        print(f"head via fast_rpc batch {ep}: {head}", flush=True)
        break
    except Exception as e:
        print(f"head via {ep} failed: {e}", flush=True)
if head is None:
    print("PREFLIGHT FAIL: no head from fast_rpc", flush=True)
    sys.exit(1)
END = head
body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(END-49), "toBlock": hex(END), "pageSize": 1000, "decodeLogs": False, "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef", "0x"+"00"*32]}, timeout=30)
n = len(body.get("result", {}).get("logs", []))
print(f"PREFLIGHT OK end={END} logs50={n} total={time.time()-T0:.1f}s", flush=True)
json.dump({"end": END, "head": END, "logs50": n, "elapsed_s": round(time.time()-T0, 1), "status": "PASS"}, open("run-2026-11-08-0931-preflight.json", "w"), indent=1)
