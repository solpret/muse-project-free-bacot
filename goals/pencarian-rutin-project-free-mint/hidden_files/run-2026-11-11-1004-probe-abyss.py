#!/usr/bin/env python3
"""Probe run 2026-11-11 1004 WIB — ABYSSCABLE (DIVER) from Boltbook ZH
+ binanceai pending-claim re-check. Read-only; writes run-2026-11-11-1004-probe-abyss.json.
Reuses curl-transport helpers from the 0931 reread script (dataseed latency high)."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
T0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def post_rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=60)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

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
            res = post_rpc(ep, calls, timeout=60)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            outd = {}
            for item, key in zip(res, keys):
                outd[key] = None if (isinstance(item, dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item, dict) else None)
            return outd
        except Exception:
            continue
    return None

block = get_block()
print("BLOCK", block, flush=True)

ABYSS = "0xd2e9242b0d7c0186cc181a5fc8534541dad278a2"
VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
         "freeClaimed(address)", "agentFreeUsed()", "mintStart()", "mintEnd()",
         "owner()", "freeAvailable(address)", "freeUsed(address)"]
abyss = raw_batch(ABYSS, VIEWS)
print("ABYSS", json.dumps(abyss), f"({time.time()-T0:.1f}s)", flush=True)

# binanceai pending claim: MINT 0x46cb..., TOKEN 0x2091...
MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
bna = raw_batch(MINT, ["launched()", "tokenClaimed(address)"])
tok = raw_batch(TOKEN, ["balanceOf(address)"])
print("BINANCEAI mint", json.dumps(bna), "tokenBal", json.dumps(tok), f"({time.time()-T0:.1f}s)", flush=True)

out = {"block": block, "started_wib": "2026-11-11 10:04 WIB",
       "abyss": {"address": ABYSS, **(abyss or {})},
       "binanceai": {"mint": MINT, "token": TOKEN, **(bna or {}), "tokenBalanceOf_user": (tok or {}).get("balanceOf_user")}}
json.dump(out, open(f"{BASE}/run-2026-11-11-1004-probe-abyss.json", "w"), indent=1)
print("DONE", f"{time.time()-T0:.1f}s", flush=True)
