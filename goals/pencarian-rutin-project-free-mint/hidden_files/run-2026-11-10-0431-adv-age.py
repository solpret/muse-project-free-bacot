#!/usr/bin/env python3
"""Binary-search Adventure Agent first-mint block via totalMinted() at historical blocks.
Read-only. Writes run-2026-11-10-0431-adv-age.json."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADV = "0x7635ef16370ef490298649a188c9205d1d7fda67"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
T0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
DATA = sel("totalMinted()")

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def total_minted_at(block):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [{"to": ADV, "data": DATA}, hex(block)]}, timeout=25)
            if isinstance(r, dict) and "error" not in r and r.get("result") not in (None, "0x"):
                return int(r["result"], 16)
            if isinstance(r, dict) and "error" not in r:
                return 0
        except Exception:
            continue
    return None

def block_ts(block):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                              "params": [hex(block), False]}, timeout=25)
            if isinstance(r, dict) and isinstance(r.get("result"), dict):
                return int(r["result"]["timestamp"], 16)
        except Exception:
            continue
    return None

def head():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

h = head()
print("HEAD", h, flush=True)
LO = h - 400000  # ~50h back, safely before any plausible launch
HI = h
lo_val = total_minted_at(LO)
print(f"totalMinted@{LO} = {lo_val}", flush=True)
if lo_val is None:
    print("LO read failed; aborting", flush=True)
    raise SystemExit(1)
# binary search: first block with totalMinted > 0
lo, hi = LO, HI
steps = []
while lo < hi:
    mid = (lo + hi) // 2
    v = total_minted_at(mid)
    steps.append([mid, v])
    print(f"mid {mid} -> {v}", flush=True)
    if v is None:
        print("read failed at mid; aborting", flush=True)
        break
    if v > 0:
        hi = mid
    else:
        lo = mid + 1
first = lo
ts = block_ts(first)
print(f"FIRST-MINT BLOCK {first} ts={ts}", flush=True)
if ts:
    from datetime import datetime, timezone, timedelta
    wib = datetime.fromtimestamp(ts, tz=timezone(timedelta(hours=7)))
    print("FIRST-MINT WIB", wib.strftime("%Y-%m-%d %H:%M:%S WIB"), flush=True)
json.dump({"head": h, "lo_block": LO, "lo_val": lo_val, "first_mint_block": first,
           "first_mint_ts": ts, "steps": steps, "elapsed_s": round(time.time() - T0, 1)},
          open(f"{BASE}/run-2026-11-10-0431-adv-age.json", "w"), indent=1)
print(f"DONE in {time.time()-T0:.1f}s", flush=True)
