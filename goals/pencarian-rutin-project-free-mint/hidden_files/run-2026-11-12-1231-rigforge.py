#!/usr/bin/env python3
"""Manual RigForge re-read for run 1231 (verify2 deadline-hit-skipped it)."""
import json, subprocess, time
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
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
views = ["freeClaimed()", "freeSharesLeft()", "openedAt()", "freeBooked(address)", "sharesSold()"]
calls, keys = [], []
for i, sig in enumerate(views):
    base = sig.split("(")[0]
    if "(address)" in sig:
        data = sel(sig) + enc(USER); key = base + "_user"
    else:
        data = sel(sig); key = base
    calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                  "params": [{"to": ADDR, "data": data}, "latest"]})
    keys.append(key)
res = None
for ep in EPS:
    try:
        r = post_rpc(ep, calls)
        if isinstance(r, list) and len(r) == len(calls):
            res = {k: (None if (isinstance(it, dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it, dict) else None)) for it, k in zip(r, keys)}
            break
    except Exception:
        continue
out = {"started_wib": "2026-11-12 12:31 WIB", "RigForge": {"address": ADDR, "views": res}}
json.dump(out, open("run-2026-11-12-1231-rigforge.json", "w"), indent=1)
print(json.dumps(out, indent=1))
