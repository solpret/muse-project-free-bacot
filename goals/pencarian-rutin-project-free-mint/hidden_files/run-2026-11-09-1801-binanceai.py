#!/usr/bin/env python3
"""Track-B binanceai re-check run 1801 via dataseed curl transport. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed.binance.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        return None if v in (None, "0x") else int(v, 16)
    except Exception: return None
def post(ep, payload, timeout=25):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
        "-H","Content-Type: application/json","-d",json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout+5).stdout
    return json.loads(out)
def call(addr, sig):
    data = sel(sig) + (enc(USER) if "(address)" in sig else "")
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}, timeout=25)
            if isinstance(r, dict) and "result" in r: return to_int(r["result"])
        except Exception: continue
    return None
def block():
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}, timeout=25)
            return int(r["result"], 16)
        except Exception: continue
    return None
out = {"block": block()}
for sig in ["launched()", "failed()", "isRefundPhase()", "totalShares()", "tokenClaimed(address)"]:
    out[sig] = call(MINT, sig)
    print(sig, out[sig], flush=True)
json.dump(out, open("run-2026-11-09-1801-binanceai.json","w"), indent=1)
print("BINANCEAI DONE block", out["block"])
