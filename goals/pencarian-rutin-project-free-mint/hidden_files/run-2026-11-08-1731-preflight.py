#!/usr/bin/env python3
"""Pre-flight for run 1731 (2026-11-08): one small ankr_getLogs call, one 50-block chunk.
Must succeed in <60s or the scan leg fast-fails for this run.
Read-only. Never sets no_proxy; Ankr goes through existing proxy env."""
import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
import onchain_nft_scan as scan

t0 = time.time()
latest = int(scan.rpc_call("eth_blockNumber", []), 16)
print(f"head block: {latest} (eth_blockNumber took {time.time()-t0:.1f}s)", flush=True)
frm, to = latest - 49, latest
t1 = time.time()
logs, pages = scan.ankr_logs(frm, to, [scan.TRANSFER, scan.ZERO_TOPIC])
dt = time.time() - t1
print(f"PREFLIGHT OK: ankr_getLogs {frm}-{to} (50 blocks) -> {len(logs)} logs, {pages} page(s), {dt:.1f}s", flush=True)
print(f"total elapsed {time.time()-t0:.1f}s", flush=True)
print(json.dumps({"head": latest, "from": frm, "to": to, "logs": len(logs), "pages": pages, "seconds": round(dt, 1)}))
