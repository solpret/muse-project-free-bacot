#!/usr/bin/env python3
"""First-mint binary search for Ghostling + Voltoad (run 0601). Read-only.
Ankr getLogs existence probes (pageSize 10) for Transfer-from-zero on each
contract; binary search over block range; block timestamp via dataseed
(Ankr timestamps are fake - never use)."""
import sys, time, json, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from ankr import ankr_post
from fast_rpc import batch
ZERO = "0x" + "00"*32
TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
def has_mint(addr, lo, hi):
    body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(lo),
        "toBlock": hex(hi), "pageSize": 10, "decodeLogs": False,
        "address": addr, "topics": [TOPIC, ZERO]}, timeout=30)
    logs = body.get("result", {}).get("logs", [])
    return len(logs) > 0, len(logs)
def block_time_wib(blk):
    for ep in ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]:
        try:
            res = batch([("eth_getBlockByNumber", [hex(blk), False])], endpoint=ep, timeout=10)
            ts = int(res[0]["timestamp"], 16)
            return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
        except Exception:
            continue
    return None
def first_mint(addr, lo, hi):
    """Binary search first block with a mint log in [lo,hi]. Assumes at least one mint in range."""
    while lo < hi:
        mid = (lo + hi) // 2
        ok, _ = has_mint(addr, lo, mid)
        if ok: hi = mid
        else: lo = mid + 1
        time.sleep(0.3)
    return lo
out = {}
HEAD = int(batch([("eth_blockNumber", [])], endpoint="https://bsc-dataseed1.bnbchain.org/", timeout=10)[0], 16)
out["head"] = HEAD
for name, addr in {"Ghostling": "0x6a4847cb5f658943222fbd23d2520049f824789d",
                   "Voltoad": "0xbc95e0a5bb1305958ba3263c6e9943b7a2554757"}.items():
    # 48h-ago boundary: ~0.45s/block -> 384000 blocks
    b48 = HEAD - 384000
    ok48, n48 = has_mint(addr, b48, b48 + 999)
    r = {"address": addr, "block_48h_ago": b48, "mints_in_48h_boundary_window": n48}
    if ok48:
        r["age_verdict"] = "AGE >48h (mints already happening at 48h-ago block)"
        # find first mint for the record, bounded search from contract-creation guess
        lo = max(0, b48 - 2000000)
        # check whether any mint exists before b48 at all in coarse probe
        ok, _ = has_mint(addr, lo, b48 - 1)
        r["mints_before_48h"] = ok
    else:
        # no mints at 48h boundary: first mint is after b48; binary search [b48, HEAD]
        fb = first_mint(addr, b48, HEAD)
        r["first_mint_block"] = fb
        r["first_mint_time_wib"] = block_time_wib(fb)
        if r["first_mint_time_wib"]:
            dt = datetime.datetime.strptime(r["first_mint_time_wib"], "%Y-%m-%d %H:%M:%S WIB").replace(tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
            r["age_hours"] = round((now - dt).total_seconds()/3600, 1)
            r["age_verdict"] = "AGE <=48h" if r["age_hours"] <= 48 else "AGE >48h"
    out[name] = r
    print(name, json.dumps(r), flush=True)
json.dump(out, open("run-2026-11-08-0601-firstmint.json", "w"), indent=1)
print("DONE")
