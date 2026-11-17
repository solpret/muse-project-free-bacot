#!/usr/bin/env python3
"""First-mint binary search for LIFTCAT 0x53aA0c94 (run 0531).
Same method as verify2. Writes run-2026-11-09-0531-liftcat-firstmint.json."""
import json, subprocess, sys, datetime
sys.set_int_max_str_digits(100000)
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def block_ts(block):
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                "params": [hex(block), False]}, timeout=25)
            if isinstance(res, dict) and isinstance(res.get("result"), dict):
                return int(res["result"]["timestamp"], 16)
        except Exception:
            continue
    return None
def any_mint(addr, frm, to):
    try:
        res = ankr_post("ankr_getLogs", {"blockchain": "bsc", "address": addr,
            "fromBlock": str(frm), "toBlock": str(to),
            "topics": [TRANSFER, ZERO_TOPIC], "pageSize": 1000}, timeout=55)
        return len(res.get("result", {}).get("logs", [])) > 0, None
    except Exception as e:
        return None, str(e)[:150]
ADDR = "0x53aA0c94b9f670866a5EDbc42A66bf5cAB59c92a"
lo, hi = 132300000, 132475221
ok, err = any_mint(ADDR, lo, hi)
print("probe range:", ok, err, flush=True)
if ok:
    while lo < hi:
        mid = (lo + hi) // 2
        ok2, err2 = any_mint(ADDR, lo, mid)
        if ok2 is None:
            print("probe error:", err2, flush=True); break
        if ok2: hi = mid
        else: lo = mid + 1
    fb = lo
else:
    fb = None
ts = block_ts(fb) if fb else None
wib = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB") if ts else None
out = {"address": ADDR, "first_mint_block": fb, "timestamp": ts, "wib": wib}
json.dump(out, open(f"{HF}/run-2026-11-09-0531-liftcat-firstmint.json", "w"), indent=1)
print("LIFTCAT FIRST-MINT:", out, flush=True)
