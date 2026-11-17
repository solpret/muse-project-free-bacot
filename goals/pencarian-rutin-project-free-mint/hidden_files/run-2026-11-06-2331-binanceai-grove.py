#!/usr/bin/env python3
"""Track B BINANCEAI + Agent Grove fase 2 — run 2026-11-06 23:31 WIB. Read-only.
Tight timeouts: each race() <= ~10s; whole script bounded by outer `timeout 120`.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak
from fast_rpc import race, call_many

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
PAIR = "0x903ACC22B9BABCD427bfb9AF2C27a27a5aC7c698"
GROVE = "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

t0 = time.time()
out = {}
try:
    blk = int(race("eth_blockNumber", []), 16)
except Exception as e:
    blk = None
    print("BINANCEAI BLOCK-FAIL", e, flush=True)
out["block"] = blk
bai = {}
for sig in ["launched()", "failed()", "isRefundPhase()", "totalShares()"]:
    try:
        bai[sig] = to_int(race("eth_call", [{"to": MINT, "data": sel(sig)}, "latest"]))
    except Exception as e:
        bai[sig] = None
        print(f"BINANCEAI {sig} FAIL {type(e).__name__}", flush=True)
try:
    bai["tokenClaimed(user)"] = to_int(race("eth_call", [{"to": MINT, "data": sel("tokenClaimed(address)") + enc(USER)}, "latest"]))
except Exception:
    bai["tokenClaimed(user)"] = None
try:
    bai["tokenBalance(user)"] = to_int(race("eth_call", [{"to": TOKEN, "data": sel("balanceOf(address)") + enc(USER)}, "latest"]))
except Exception:
    bai["tokenBalance(user)"] = None
out["binanceai"] = bai
print("BINANCEAI", json.dumps(bai), flush=True)
json.dump(bai, open(f"{BASE}/run-2026-11-06-2331-binanceai.json", "w"), indent=1)

# Grove fase 2
grove = {}
try:
    fo, fc = call_many([(GROVE, sel("freeOpen()")), (GROVE, sel("freeClaimed(address)") + enc(USER))], timeout=15)
    grove = {"block": blk, "freeOpen": to_int(fo), "freeClaimed_user": (bool(to_int(fc)) if to_int(fc) is not None else None), "elapsed_s": round(time.time() - t0, 2)}
except Exception as e:
    grove = {"block": blk, "freeOpen": None, "freeClaimed_user": None, "error": str(e)[:150], "elapsed_s": round(time.time() - t0, 2)}
    print("GROVE FAIL", e, flush=True)
print("GROVE", json.dumps(grove), flush=True)
json.dump(grove, open(f"{BASE}/run-2026-11-06-2331-grove-check.json", "w"), indent=1)
print(f"BINANCEAI+GROVE DONE in {time.time()-t0:.1f}s", flush=True)
