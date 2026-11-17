#!/usr/bin/env python3
"""AgentVOLT round-1 triage, one view per call (a reverting view must not kill the rest). Read-only."""
import json, sys
from Crypto.Hash import keccak
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0xe0DEB1A792EeBD9cbA7Fd74B70A283Bfa2630771"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def dec_str(v):
    try:
        b = bytes.fromhex(v[2:]); ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode("utf-8", "replace")
    except Exception: return None
views = ["totalSupply()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
         "freeClaimed(address)", "name()", "symbol()", "freeMinted()", "totalMinted()"]
out = {"address": ADDR, "views": {}}
from fast_rpc import race as _race
try: out["block"] = int(_race("eth_blockNumber", []), 16)
except Exception as e: out["block_error"] = str(e)
for sig in views:
    base = sig.split("(")[0]
    data = sel(sig) + (enc(USER) if "(address)" in sig else "")
    key = base + ("_user" if "(address)" in sig else "")
    val = None; err = None
    for ep in EPS:
        try:
            res = batch([("eth_call", [{"to": ADDR, "data": data}, "latest"])], endpoint=ep, timeout=8)
            val = res[0]; break
        except Exception as e:
            err = str(e)[:120]; continue
    out["views"][key] = dec_str(val) if (val and key in ("name", "symbol")) else (to_int(val) if val else None)
    if val is None: out["views"][key + "_error"] = err
print(json.dumps(out, indent=1))
json.dump(out, open(f"{HF}/run-2026-11-07-0431-agentvolt-triage.json", "w"), indent=1)
