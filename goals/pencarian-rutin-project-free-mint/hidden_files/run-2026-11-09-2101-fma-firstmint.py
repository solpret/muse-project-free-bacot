#!/usr/bin/env python3
"""Run 2101: FMA first-mint binary search via historical eth_call totalSupply().
Read-only. Writes run-2026-11-09-2101-fma-firstmint.json."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
FMA = "0xA45CA208d015C81Bf2f5e606437e4f9d1D8C2FE8"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def post(ep, payload, timeout=20):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def ts_at(block):
    data = sel("totalSupply()")
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": FMA, "data": data}, hex(block)]})
            if isinstance(r, dict) and "result" in r and r["result"] not in (None, "0x"):
                return int(r["result"], 16)
        except Exception:
            continue
    return None

def block_ts(block):
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                          "params": [hex(block), False]})
            if isinstance(r, dict) and isinstance(r.get("result"), dict):
                return int(r["result"]["timestamp"], 16)
        except Exception:
            continue
    return None

out = {"contract": FMA}
head = None
for ep in EPS:
    try:
        r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})
        head = int(r["result"], 16); break
    except Exception: continue
out["head"] = head
print("HEAD", head, flush=True)
# establish a zero lower bound, stepping down 100k blocks until totalSupply==0
lo = head - 100000
v = ts_at(lo)
print("ts_at", lo, "=", v, flush=True)
steps = 0
while v is None or v > 0:
    lo -= 100000
    steps += 1
    if steps > 10 or lo < 130000000:
        break
    v = ts_at(lo)
    print("ts_at", lo, "=", v, flush=True)
out["zero_block"] = lo if v == 0 else None
out["zero_block_ts"] = v
if v == 0:
    hi = head
    # binary search first block with totalSupply > 0
    while hi - lo > 1:
        mid = (lo + hi) // 2
        mv = ts_at(mid)
        print("mid", mid, "=", mv, flush=True)
        if mv is None:
            time.sleep(2)
            mv = ts_at(mid)
            print("mid-retry", mid, "=", mv, flush=True)
        if mv is None:
            break
        if mv > 0:
            hi = mid
        else:
            lo = mid
    out["first_mint_block"] = hi
    t = block_ts(hi)
    out["first_mint_block_ts"] = t
    print("FIRST MINT BLOCK", hi, "ts", t, flush=True)
with open(f"{BASE}/run-2026-11-09-2101-fma-firstmint.json", "w") as f:
    json.dump(out, f, indent=1)
print("FIRSTMINT DONE", flush=True)
