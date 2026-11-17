#!/usr/bin/env python3
"""Scan PRE-FLIGHT ONLY for free-mint-search run 2026-11-16 05:01 WIB.
One small ankr_getLogs call (~50 blocks) via the module code path in
onchain_nft_scan.py (ankr_logs -> ankr_post). Read-only. If it fails,
FAST-FAIL: do NOT launch the full scan, do NOT advance the watermark.
Ankr has returned HTTP 401 since 2026-11-09 (freemium exhausted)."""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/")
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"

t0 = time.time()
log_lines = []
def log(s):
    log_lines.append(s); print(s, flush=True)

log("Free Bacot run 2026-11-16 05:01 WIB — SCAN PRE-FLIGHT leg (read-only)")
log("Run time: 2026-11-16 ~05:01 WIB")
log("")
# Head cross-check via bsc-dataseed
head = None
for ep in ("https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed.binance.org/"):
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "30", "-X", "POST", ep,
                            "-H", "Content-Type: application/json",
                            "-d", json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})],
                           capture_output=True, text=True, timeout=40)
        j = json.loads(r.stdout)
        if j.get("result"):
            head = int(j["result"], 16)
            log(f"Head cross-check: eth_blockNumber via {ep} OK in {time.time()-t0:.2f}s -> head {head}")
            break
    except Exception as e:
        log(f"Head cross-check via {ep} failed: {e}")
        continue
if head is None:
    log("Head cross-check FAILED on all endpoints; using reread block 133804394 as head reference.")
    head = 133804394

from onchain_nft_scan import ankr_logs, TRANSFER, ZERO_TOPIC
frm, to = head - 50, head - 1
log("")
log("1. PRE-FLIGHT (Ankr, module ankr_logs, same code path as onchain_nft_scan.py)")
log(f"   - Call: ankr_getLogs, blockchain bsc, 1 chunk ~50 blocks ({frm}..{to}), timeout 30s")
t1 = time.time()
try:
    logs, pages = ankr_logs(frm, to, [TRANSFER, ZERO_TOPIC])
    log(f"   - RESULT: OK in {time.time()-t1:.2f}s — {len(logs)} logs, {pages} page(s)")
    log("   - Verdict: pre-flight PASSED (unexpected vs 401 streak since 2026-11-09). Full scan still NOT launched by this pre-flight script; parent decides.")
    verdict = "pass"
except Exception as e:
    log(f"   - RESULT: FAIL — {str(e)[:200]} in {time.time()-t1:.2f}s")
    log("   - Verdict: scan leg FAST-FAIL for this run per 2026-11-06 amendment. Full scan driver NOT launched, watermark NOT advanced.")
    verdict = "fast-fail"

state = json.load(open(BASE + "onchain-scan-state.json"))
wm = state.get("last_scanned_block")
gap = head - wm if wm else None
log("")
log("2. WATERMARK / GAP")
log(f"   - last_scanned_block (onchain-scan-state.json): {wm} (unchanged)")
log(f"   - Head: {head}")
log(f"   - Gap: {gap:,} blocks and growing (~8,000 blocks/hour). Same blocker as run 08:31 WIB: Ankr credential/surrogate rejected — needs parent review.")
log("")
log("Files NOT written: onchain-snapshot.json, onchain-scan-state.json, scan-bridge.json (all untouched).")
log("No scan output written. No mint/preview attempted.")
log(f"Log written: hidden_files/run-2026-11-16-0501-scanpreflight.log (this file).")
open(BASE + "run-2026-11-16-0501-scanpreflight.log", "w").write("\n".join(log_lines) + "\n")
print("PREFLIGHT verdict:", verdict, "head:", head, "watermark:", wm, "gap:", gap)
