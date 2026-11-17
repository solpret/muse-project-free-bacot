#!/usr/bin/env python3
"""Kicks first-mint via binary search on totalMinted() at historical blocks
+ metaURI/tokenURI reads. Run 2026-11-14 05:31 WIB. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0x5726100e0D9ACB20cFB13e80e0fe42DF146730A8"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def post_rpc(ep, payload, timeout=90):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)
def call_at(ep, data, block):
    r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                      "params": [{"to": ADDR, "data": data}, hex(block)]}, timeout=90)
    if isinstance(r, dict) and isinstance(r.get("result"), str) and r["result"] not in ("0x",):
        return int(r["result"], 16)
    return None

TM = "0x" + sel("totalMinted()")
# metaURI + tokenURI(1) at latest
views = {}
for name, data in [("metaURI", "0x" + sel("metaURI()")),
                   ("tokenURI_1", "0x" + sel("tokenURI(uint256)") + format(1, "064x"))]:
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [{"to": ADDR, "data": data}, "latest"]}, timeout=90)
            if isinstance(r, dict) and isinstance(r.get("result"), str):
                views[name] = r["result"]; break
        except Exception: continue
print("metaURI/tokenURI done", round(time.time() - t0, 1), "s", flush=True)

# binary search: first block where totalMinted > 0, in [133415000, 133426358]
lo, hi = 133415000, 133426358
def total_at(block):
    for ep in EPS:
        try:
            v = call_at(ep, TM, block)
            if v is not None: return v
        except Exception: continue
    return None
v_hi = total_at(hi); v_lo = total_at(lo)
print("totalMinted at", lo, "=", v_lo, "| at", hi, "=", v_hi, flush=True)
first_block = None
if v_hi and v_hi > 0:
    if v_lo and v_lo > 0:
        first_block = "BEFORE_RANGE"
    else:
        a, b = lo, hi  # invariant: total(a)==0 or unknown, total(b)>0
        while b - a > 1:
            m = (a + b) // 2
            v = total_at(m)
            print(f"  mid {m} = {v} ({time.time()-t0:.0f}s)", flush=True)
            if v is None:
                print("  mid read failed, aborting binary search", flush=True); break
            if v > 0: b = m
            else: a = m
        first_block = b
ts = None
if isinstance(first_block, int):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                              "params": [hex(first_block), False]}, timeout=90)
            if isinstance(r, dict) and isinstance(r.get("result"), dict):
                ts = int(r["result"]["timestamp"], 16); break
        except Exception: continue
out = {"started_wib": "2026-11-14T05:31+07:00", "metaURI_raw": views.get("metaURI"),
       "tokenURI_1_raw": views.get("tokenURI_1"), "first_mint_block": first_block,
       "first_mint_ts": ts, "totalMinted_lo": v_lo, "totalMinted_hi": v_hi,
       "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open(BASE + "run-2026-11-14-0531-kicks-firstmint2.json", "w"), indent=1)
print(json.dumps({k: (v[:120] if isinstance(v, str) else v) for k, v in out.items()}, indent=1))
