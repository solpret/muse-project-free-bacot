#!/usr/bin/env python3
"""Free-mint-search run 2026-11-12 08:31 WIB — tc-age re-check (fresh script).
Re-reads CLEPSYDRA + MoonAgent launch-time views to confirm age-exclusion
still holds, and WNO totalShares. Read-only; writes run-2026-11-12-0831-tc-age.json.
"""
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
    try:
        return int(v, 16) if v and v != "0x" else None
    except Exception:
        return None

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
            outd = {}
            for item, key in zip(res, keys):
                outd[key] = None if (isinstance(item, dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item, dict) else None)
            return outd
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

out = {"started_wib": "2026-11-12 08:31 WIB", "block": get_block()}
out["CLEPSYDRA"] = raw_batch("0x9e2738B3DD3773c6c71cA24Fbc92660B501C0B6b",
    ["totalSupply()", "freeClaimed()", "FREE_TOKENS()", "startTime()"])
out["MoonAgent"] = raw_batch("0xc4695f19dE428EA37169bBD058463588D511554a",
    ["totalMints()", "MAX_MINTS()", "mintOpen()", "MINT_DEADLINE()", "balanceOf(address)"])
out["WNO"] = raw_batch("0x8C969a4CD49E4774908e667702C3d7C3ece164D0",
    ["totalSupply()", "totalShares()", "balanceOf(address)"])
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-12-0831-tc-age.json", "w"), indent=1)
print(json.dumps(out, indent=1))
