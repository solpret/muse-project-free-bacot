#!/usr/bin/env python3
"""Run 1401 OLIVER + Meow Cards re-read (fresh script).
OLIVER BATCH-FAIL in verify2-supplement 1401; Meow Cards is a new sweep
finding (The Colony 2026-11-10 14:40 UTC) needing an on-chain free-pool
read to complete its age-excluded record. Read-only; writes
run-2026-11-12-1401-oliver.json. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            return {key: (None if (isinstance(it, dict) and "error" in it)
                          else (to_int(it.get("result")) if isinstance(it, dict) else None))
                    for it, key in zip(res, keys)}
        except Exception:
            continue
    return None

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

block = get_block()
out = {"started_wib": "2026-11-12 14:01 WIB", "block": block}
oliver_views = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
                "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
                "freeClaimed(address)", "freeUsed(address)", "mintedBy(address)",
                "freeMintedBy(address)", "freeLeft()", "freeAvailable(address)",
                "START_TIME()", "startTime()", "mintOpensAt()", "freeRemaining()",
                "paidMinted()", "FREE_MAX()", "PAID_MAX()"]
out["OLIVER"] = {"address": "0xad86e4d52e55709d1bda08f922853d4b109e0810",
                 "views": raw_batch("0xad86e4d52e55709d1bda08f922853d4b109e0810", oliver_views)}
meow_views = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
              "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
              "freeClaimed(address)", "freeUsed(address)", "mintedBy(address)"]
out["MeowCards"] = {"address": "0xb8164afefc53910d7a74cece15a60a9e0c86089e",
                    "views": raw_batch("0xb8164afefc53910d7a74cece15a60a9e0c86089e", meow_views)}
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-12-1401-oliver.json", "w"), indent=1)
print(json.dumps(out, indent=1))
