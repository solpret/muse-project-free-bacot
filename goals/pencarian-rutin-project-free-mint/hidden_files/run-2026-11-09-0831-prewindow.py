#!/usr/bin/env python3
"""Pre-window check run 2026-11-09 0831 WIB — for agent-shaped first-seen
contracts NOT owner-discarded: count Transfer-from-zero mints in
[132400000, 132497913] (before this run's scan window) via ONE Ankr
ankr_getLogs call per contract (address filter + Transfer topic + from=zero
topic; pageSize 1000, truncated flag if exactly 1000 logs). Contracts with
0 pre-window mints get totalSupply()/totalMinted() reads (dataseed) to
detect mature contracts whose launch predates 132400000.
Read-only; writes run-2026-11-09-0831-prewindow.json.
"""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
FROM, TO = 132400000, 132497913

CONTRACTS = [
    "0x5c04392641c81F1b69826E13d8f3F78c58464970",
    "0x9fd3e0a352269820717B373E140D3709Dc279851",
    "0x253a002E4D03F1b49C4739f2165dfA00F17feE25",
    "0x74830117F86af8a8D39e56B2bcD4D34B30D7B027",
    "0xf4dC5600D2546E1e52b8cA81169D3Cec53264b68",
    "0x18042D2E0bFd11fc2cc8ee1E59a6601e530C3dF5",
    "0x4AB41152EdB3E2853b19828e51927db36508cd64",
    "0x99dE10fc70EbEEc6C32e108f48793459628b41a5",
    "0x1B72ceC52A74537b06F713FCebA0e491f53679aE",
    "0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17",
]
# owner-discarded, NOT pre-window checked (excluded from promotion regardless):
DISCARDED = [
    "0x00eD52465ffD558Fd1743CA7E9Eef5817e42Ac07",
    "0x169F9cfC148ba462Bb0073466939e8Eae32C0be5",
    "0xaf620aEac150A3C3122274F1D372a4A216719327",
    "0xf4BaCF30fB8F69373F63D99C657F53DD7774Af1D",
    "0x69Dc6eB49E4cA2508C09778a211F8D6DFECE0049",
    "0x6c1a1Fad4b1Aee87f041b25b5a7D4646633584E6",
]

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

out = {"run": "2026-11-09-0831", "pre_window": [FROM, TO],
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

json.dump(out, open(f"{HF}/run-2026-11-09-0831-prewindow.json", "w"), indent=1)
print("PREWINDOW DONE")
