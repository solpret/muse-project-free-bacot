#!/usr/bin/env python3
"""Lean retry run 0001 (service restart killed verify-early2 mid-run):
SEVEN + AgentPals (freeMinted/totalSupply) + 0x79b0 + 0xE1a4 (lean views).
Read-only; writes run-2026-11-12-0031-verify-lean.json. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def post(ep, payload, timeout=40):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig: data, key = sel(sig) + enc(USER), base + "_user"
        else: data, key = sel(sig), base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post(ep, calls, timeout=40)
            if not isinstance(res, list) or len(res) != len(calls): continue
            return {k: (None if isinstance(it, dict) and "error" in it else (to_int(it.get("result")) if isinstance(it, dict) else None)) for it, k in zip(res, keys)}
        except Exception: continue
    return None
def get_block():
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=40)
            return int(r["result"], 16)
        except Exception: continue
    return None
VIEWS = ["totalSupply()", "totalMinted()", "freeMinted()", "FREE_SUPPLY()", "FREE_CAP()",
         "freeLeft()", "MAX_SUPPLY()", "maxSupply()", "mintOpen()", "balanceOf(address)",
         "freeClaimed(address)", "mintStart()", "mintOpensAt()", "mintOpenedAt()", "owner()"]
TARGETS = {
    "SEVEN": "0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96",
    "AgentPals": "0xD265a929D0E50bD5ee4675e4E97F38D8380802E2",
    "0x79b0": "0x79b0CE8b39c3Ed230487172751612b4F631398Bc",
    "0xE1a4": "0xE1a4fFb104e5BF2b7aA5aD77969D43B56FCEE91A",
}
out = {"block": get_block(), "started_wib": "2026-11-12 00:31 WIB", "verify": {}}
print("BLOCK", out["block"], flush=True)
for name, addr in TARGETS.items():
    t = time.time()
    got = batch(addr, VIEWS)
    d = {"address": addr}
    if got is None:
        d["_batch_fail"] = True
    else:
        d.update(got)
    out["verify"][name] = d
    print(name, {k: v for k, v in d.items() if v is not None}, "(%.1fs)" % (time.time() - t), flush=True)
json.dump(out, open(BASE + "run-2026-11-12-0031-verify-lean.json", "w"), indent=1)
print("VERIFY-LEAN DONE")
