#!/usr/bin/env python3
"""Run 0231: cheap single-call confirmation for 0201 flags Horus / KAGENT / HOPKIN.
Read-only; writes run-2026-11-08-0231-hopkin-kagent-confirm.json.
Single eth_call per item (fast_rpc.batch whole-batch-revert quirk)."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
HOPKIN = "0x2728c134d79d34a977d6d35d8a3014abb5c97ed4"
KAGENT = "0xb34105002B19EF0ce43B59011fE848df5c8B174f"
HORUS = "0x794aD67a5590C7e5848E49181297F9cC7C6CE00E"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def call(to, sig, args=""):
    try:
        r = batch([("eth_call", [{"to": to, "data": sel(sig) + args}, "latest"])])
        return to_int(r[0]) if r else None
    except Exception as e:
        return "ERR:" + str(e)[:120]

out = {"run": "0231", "wib": "2026-11-08 ~03:00 WIB"}
try:
    out["block"] = int(batch([("eth_blockNumber", [])])[0], 16)
except Exception as e:
    out["block"] = "ERR:" + str(e)[:80]

for label, addr in [("horus", HORUS), ("kagent", KAGENT), ("hopkin", HOPKIN)]:
    d = {"address": addr}
    for sig in ["totalSupply()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()"]:
        d[sig.split("(")[0]] = call(addr, sig)
    d["balanceOf_user"] = call(addr, "balanceOf(address)", enc(USER))
    out[label] = d

json.dump(out, open(f"{BASE}/run-2026-11-08-0231-hopkin-kagent-confirm.json", "w"), indent=1)
print(json.dumps(out, indent=1))
