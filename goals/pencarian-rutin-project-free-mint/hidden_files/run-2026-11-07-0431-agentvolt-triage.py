#!/usr/bin/env python3
"""Light on-chain triage for AgentVOLT (round 1) 0xe0DEB1A792EeBD9cbA7Fd74B70A283Bfa2630771
— MINTS-index new entry, run 2026-11-07 04:31 WIB. Read-only; writes only
run-2026-11-07-0431-agentvolt-triage.json. Uses the same pinned-endpoint
fast_rpc batch helper as the reread leg."""
import json, sys, time
from Crypto.Hash import keccak
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0xe0DEB1A792EeBD9cbA7Fd74B70A283Bfa2630771"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def dec_str(v):
    try:
        b = bytes.fromhex(v[2:])
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode("utf-8", "replace")
    except Exception:
        return None

views = ["totalSupply()", "freeClaimed()",
         "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
         "freeClaimed(address)", "name()", "symbol()"]
calls, keys = [], []
for sig in views:
    base = sig.split("(")[0]
    if "(address)" in sig:
        data = sel(sig) + enc(USER); key = base + "_user"
    else:
        data = sel(sig); key = base
    calls.append(("eth_call", [{"to": ADDR, "data": data}, "latest"]))
    keys.append(key)

out = {"address": ADDR, "name": "AgentVOLT (round 1)", "source": "MINTS index thecolony.ai, run 2026-11-07 0431",
       "block": None, "views": {}, "started_wib": "2026-11-07 04:31 WIB"}
from fast_rpc import race as _race
try:
    out["block"] = int(_race("eth_blockNumber", []), 16)
except Exception as e:
    print("BLOCK-FAIL", e, flush=True)
got = None
for ep in EPS:
    try:
        got = batch(calls, endpoint=ep, timeout=8)
        break
    except Exception as e:
        print("EP-FAIL", ep, e, flush=True)
if got is None:
    out["error"] = "all endpoints failed"
else:
    for k, v in zip(keys, got):
        out["views"][k] = dec_str(v) if k in ("name", "symbol") else to_int(v)
print(json.dumps(out, indent=1))
json.dump(out, open(f"{HF}/run-2026-11-07-0431-agentvolt-triage.json", "w"), indent=1)
