#!/usr/bin/env python3
"""First-Minted lookup for the 5 new S1 contracts (hot-leg 2026-11-07 15:04 WIB).
Ankr getLogs for earliest Minted event; block timestamp via dataseed (Ankr timestamps are fake).
Read-only."""
import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _fast_single
from Crypto.Hash import keccak

ADDRS = [
    "0x8717fc8751b8Ebd6832EA145974AA77D86bE9EaD",
    "0xe8b5E3ca9f4F51366f9f4860ed70b8e929e80470",
    "0x16A8aFdc97F8Cf48617bF15E47b4dA2217ea04A5",
    "0xab3F2dA0b63F5A823510095263789E9e6F26329a",
    "0x2a71CEF7101B8b19c4ab18BeD40C3ec5EC87B9b7",
]
ANKR = "https://rpc.ankr.com/bsc"
_k = keccak.new(digest_bits=256); _k.update(b"Minted(address,uint256,uint256,bool)")
TOPIC = "0x" + _k.hexdigest()

def ankr_logs(addr, frm, to):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                       "params": [{"address": addr, "fromBlock": hex(frm), "toBlock": hex(to),
                                   "topics": [TOPIC]}]}).encode()
    req = urllib.request.Request(ANKR, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        o = json.load(r)
    if "error" in o:
        return {"error": o["error"]}
    return o.get("result", [])

def block_ts(blocknum):
    for ep in ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]:
        try:
            v = _fast_single(ep, "eth_getBlockByNumber", [hex(blocknum), False], 8, retries=0)
            if v and v.get("timestamp"):
                return int(v["timestamp"], 16)
        except Exception:
            continue
    return None

# current block for window end
cur = None
for ep in ["https://bsc-dataseed.binance.org/"]:
    try:
        cur = int(_fast_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        break
    except Exception:
        pass
print("current block:", cur)
out = {}
for a in ADDRS:
    # binary-search earliest Minted: scan backwards in 200k-block windows from now
    found = None
    hi = cur
    lo = max(0, cur - 2000000)  # ~10 days back is plenty; narrow below
    # walk windows of 100k blocks from recent to old, stop at first window with logs
    step = 100000
    end = cur
    while end > cur - 2000000 and found is None:
        start = max(0, end - step + 1)
        try:
            logs = ankr_logs(a, start, end)
        except Exception as e:
            print(a, "logs error", e); break
        if isinstance(logs, dict):
            print(a, "logs error", logs); break
        if logs:
            found = min(logs, key=lambda l: int(l["blockNumber"], 16))
            # narrow within this window: re-query smaller windows to find earliest
            w_end = int(found["blockNumber"], 16)
            w_start = start
            while w_end - w_start > 2000:
                mid = (w_start + w_end) // 2
                try:
                    sub = ankr_logs(a, w_start, mid)
                except Exception:
                    break
                if isinstance(sub, dict) or not sub:
                    w_start = mid + 1
                else:
                    w_end = min(int(l["blockNumber"], 16) for l in sub)
            try:
                sub = ankr_logs(a, w_start, w_end)
                if isinstance(sub, list) and sub:
                    found = min(sub, key=lambda l: int(l["blockNumber"], 16))
            except Exception:
                pass
        end = start - 1
    if found:
        bn = int(found["blockNumber"], 16)
        ts = block_ts(bn)
        out[a] = {"firstMintBlock": bn, "firstMintTs": ts, "tx": found.get("transactionHash")}
        print(a, "first Minted block", bn, "ts", ts)
    else:
        out[a] = {"firstMintBlock": None}
        print(a, "NO Minted logs found in 2M-block window (suspicious - sharesSold>0)")

json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-07-1504-leg3-age.json", "w"), indent=1)
