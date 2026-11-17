#!/usr/bin/env python3
"""Pre-window check run 2026-11-09 0901 WIB — for agent-shaped first-seen
contracts NOT owner-discarded: count Transfer-from-zero mints in
[132400000, 132503470] (before this run's scan window) via ONE Ankr
ankr_getLogs call per contract (address filter + Transfer topic + from=zero
topic; pageSize 1000, truncated flag if exactly 1000 logs). Contracts with
0 pre-window mints get totalSupply()/totalMinted() reads (dataseed) to
detect mature contracts whose launch predates 132400000.
Read-only; writes run-2026-11-09-0901-prewindow.json.
"""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
FROM, TO = 132400000, 132503470

CONTRACTS = [
    "0xCFB72b0E311796C478c6b74C1cd4592BbAa17aab",
]
# owner-discarded, NOT pre-window checked (excluded from promotion regardless):
DISCARDED = []

EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def eth_call(addr, data):
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            r = res.get("result")
            if isinstance(r, str) and r.startswith("0x"):
                return r
        except Exception:
            continue
    return None

def view_int(addr, sel):
    r = eth_call(addr, sel)
    if r is None or len(r) < 66:
        return None
    try:
        return int(r[-64:], 16)
    except Exception:
        return None

out = {"run": "2026-11-09-0901", "pre_window": [FROM, TO],
       "discarded_not_checked": DISCARDED}
for addr in CONTRACTS:
    t0 = time.time()
    try:
        res = ankr_post("ankr_getLogs", {
            "blockchain": "bsc",
            "fromBlock": str(FROM),
            "toBlock": str(TO),
            "address": addr,
            "topics": [TRANSFER, ZERO_TOPIC],
            "pageSize": 1000,
        }, timeout=55)
        logs = res.get("result", {}).get("logs", []) if isinstance(res, dict) else []
        n = len(logs)
        first_blk = min((int(l["blockNumber"], 16) for l in logs), default=None)
        entry = {"pre_window_mints": n, "first_pre_block": first_blk,
                 "truncated": n >= 1000, "seconds": round(time.time() - t0, 1)}
    except Exception as e:
        entry = {"pre_window_mints": None, "first_pre_block": None,
                 "truncated": None, "error": str(e)[:200],
                 "seconds": round(time.time() - t0, 1)}
    if entry.get("pre_window_mints") == 0:
        entry["totalSupply"] = view_int(addr, "0x18160ddd")
        entry["totalMinted"] = view_int(addr, "0x6c9f5c1d")
    out[addr] = entry
    print(addr, entry, flush=True)

json.dump(out, open(f"{HF}/run-2026-11-09-0901-prewindow.json", "w"), indent=1)
print("PREWINDOW DONE")
