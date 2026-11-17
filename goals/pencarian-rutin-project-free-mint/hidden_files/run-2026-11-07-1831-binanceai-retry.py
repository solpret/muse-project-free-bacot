#!/usr/bin/env python3
"""BINANCEAI retry run 1831 — race() timed out on all endpoints; retry with
direct dataseed/publicnode batch + endpoint fallback. Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
GROVE = "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def call(addr, sig, arg=None):
    data = sel(sig) + (enc(arg) if arg else "")
    for ep in EPS:
        try:
            r = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=10)
            return to_int(r[0])
        except Exception:
            continue
    return None
t0 = time.time()
out = {"retry_wib": "2026-11-07 ~18:48 WIB"}
for ep in EPS:
    try:
        r = batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)
        out["head"] = int(r[0], 16)
        break
    except Exception:
        continue
bai = {}
for v in ["launched()", "failed()", "isRefundPhase()", "totalShares()"]:
    bai[v] = call(MINT, v)
bai["tokenClaimed(user)"] = call(MINT, "tokenClaimed(address)", USER)
bai["tokenBalance(user)"] = call(TOKEN, "balanceOf(address)", USER)
out["binanceai"] = bai
grove = {"freeOpen": call(GROVE, "freeOpen()")}
fc = call(GROVE, "freeClaimed(address)", USER)
grove["freeClaimed_user"] = bool(fc) if fc is not None else None
out["grove"] = grove
out["elapsed_s"] = round(time.time() - t0, 2)
print(json.dumps(out, indent=1), flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-07-1831-binanceai-retry.json", "w"), indent=1)
