#!/usr/bin/env python3
"""Fresh reads run 0901: ONI-74bD (upcoming), ONI-d576 (early lead, backfill-owned),
Pea Fun Pod (early lead). Read-only; writes run-2026-11-07-0901-oni-peapod.json."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak
from fast_rpc import batch, race

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def read_views(addr, views):
    calls, keys = [], []
    for sig in views:
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append(("eth_call", [{"to": addr, "data": data}, "latest"]))
        keys.append(key)
    for ep in EPS:
        try:
            res = batch(calls, endpoint=ep, timeout=10)
            return {k: to_int(v) for k, v in zip(keys, res)}
        except Exception:
            continue
    return {k: None for k in keys}

blk = int(race("eth_blockNumber", []), 16)
print("BLOCK", blk, flush=True)
out = {"block": blk}

ONI74 = "0x74bDA11E34EB02121104Ff38471D91Fe1C37F81A"
out["ONI-74bD"] = read_views(ONI74, ["mintOpensAt()", "totalMinted()", "freeMinted()",
    "FREE_POOL()", "MAX_SUPPLY()", "poolSeeded()", "registry()", "token()", "pair()"])
print("ONI-74bD", json.dumps(out["ONI-74bD"]), flush=True)

ONID = "0xd576F638b5eF8906C13CE9Ca534113DdBd0a9038"
out["ONI-d576"] = read_views(ONID, ["mintOpensAt()", "totalMinted()", "freeMinted()",
    "FREE_POOL()", "MAX_SUPPLY()", "poolSeeded()", "registry()", "token()", "pair()",
    "freeClaimed(address)", "freeUsed(address)", "owner()"])
print("ONI-d576", json.dumps(out["ONI-d576"]), flush=True)

PEA = "0x25F3EFb465685692EF3DdC47Ed040baF216B5D38"
out["PeaFunPod"] = read_views(PEA, ["freePodsClaimed()", "freePodsRemaining()",
    "FREE_PODS_TOTAL()", "totalPodsMinted()", "freeWindowOpen()",
    "freeClaimedBy(address)", "gateStart()"])
print("PeaFunPod", json.dumps(out["PeaFunPod"]), flush=True)

json.dump(out, open(f"{BASE}/run-2026-11-07-0901-oni-peapod.json", "w"), indent=1)
print("DONE", flush=True)
