#!/usr/bin/env python3
"""Track B BINANCEAI + Grove re-check — run 2026-11-07 20:01 WIB. Read-only.
Single-call reads (revert-prone views one at a time); None = read failure,
never zero. Retry pass if first pass yields nulls (1831 precedent: first
race() pass timed out on all RPCs, retry via dataseed/publicnode succeeded).
No preview / claim / execution.
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
    print("BLOCK-FAIL", e, flush=True)
out["block"] = blk

def read_one(to, data):
    try:
        return to_int(race("eth_call", [{"to": to, "data": data}, "latest"]))
    except Exception:
        return None

bai = {}
for sig in ["launched()", "failed()", "isRefundPhase()", "totalShares()"]:
    bai[sig] = read_one(MINT, sel(sig))
    print(f"BINANCEAI {sig} = {bai[sig]}", flush=True)
bai["tokenClaimed(user)"] = read_one(MINT, sel("tokenClaimed(address)") + enc(USER))
bai["tokenBalance(user)"] = read_one(TOKEN, sel("balanceOf(address)") + enc(USER))
print("BINANCEAI pass1", json.dumps(bai), flush=True)

# Retry pass for any nulls (RPC timeout artifact, per 1831 precedent)
if any(v is None for v in bai.values()):
    print("BINANCEAI retry pass for nulls", flush=True)
    for sig in ["launched()", "failed()", "isRefundPhase()", "totalShares()"]:
        if bai[sig] is None:
            bai[sig] = read_one(MINT, sel(sig))
            print(f"BINANCEAI retry {sig} = {bai[sig]}", flush=True)
    if bai["tokenClaimed(user)"] is None:
        bai["tokenClaimed(user)"] = read_one(MINT, sel("tokenClaimed(address)") + enc(USER))
    if bai["tokenBalance(user)"] is None:
        bai["tokenBalance(user)"] = read_one(TOKEN, sel("balanceOf(address)") + enc(USER))
    print("BINANCEAI pass2", json.dumps(bai), flush=True)
out["binanceai"] = bai
json.dump(bai, open(f"{BASE}/run-2026-11-07-2001-binanceai.json", "w"), indent=1)

# Grove fase 2
grove = {}
try:
    fo, fc = call_many([(GROVE, sel("freeOpen()")), (GROVE, sel("freeClaimed(address)") + enc(USER))], timeout=15)
    grove = {"block": blk, "freeOpen": to_int(fo),
             "freeClaimed_user": (bool(to_int(fc)) if to_int(fc) is not None else None),
             "elapsed_s": round(time.time() - t0, 2)}
except Exception as e:
    grove = {"block": blk, "freeOpen": None, "freeClaimed_user": None,
             "error": str(e)[:150], "elapsed_s": round(time.time() - t0, 2)}
    print("GROVE FAIL", e, flush=True)
print("GROVE", json.dumps(grove), flush=True)
json.dump(grove, open(f"{BASE}/run-2026-11-07-2001-grove-check.json", "w"), indent=1)

out["grove"] = grove
out["elapsed_s"] = round(time.time() - t0, 2)
json.dump(out, open(f"{BASE}/run-2026-11-07-2001-binanceai-grove.json", "w"), indent=1)
print(f"BINANCEAI+GROVE DONE in {time.time()-t0:.1f}s", flush=True)
