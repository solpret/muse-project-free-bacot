#!/usr/bin/env python3
"""Targeted on-chain check run 2331: NAOMI GENESIS 0xC7Ad (snapshot says free pool sold out run 2001; Colony post claims 338/777 free remain) + S1-0895 pending verification."""
import json, subprocess
from Crypto.Hash import keccak
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        return None if v is None or v == "0x" else int(v, 16)
    except Exception: return None
def post(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep, "-H", "Content-Type: application/json", "-d", json.dumps(payload)], capture_output=True, text=True, timeout=timeout+5).stdout
    return json.loads(out)
def batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig: data, key = sel(sig) + enc(USER), base + "_user"
        else: data, key = sel(sig), base
        calls.append({"jsonrpc": "2.0", "id": i+1, "method": "eth_call", "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post(ep, calls)
            if not isinstance(res, list) or len(res) != len(calls): continue
            return {k: (None if isinstance(it, dict) and "error" in it else (to_int(it.get("result")) if isinstance(it, dict) else None)) for it, k in zip(res, keys)}
        except Exception: continue
    return None
NAOMI = "0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9"
S10895 = "0x0895398c932E602152B8F27723C2F5bf1413A87d"
VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "freeLeft()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)", "freeClaimed(address)", "freeSharesRemaining()", "freeFor(address)"]
out = {"NAOMI": batch(NAOMI, VIEWS), "S1-0895": batch(S10895, VIEWS)}
print(json.dumps(out, indent=1))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-11-2331-verify-naomi.json", "w"), indent=1)
