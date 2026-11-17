#!/usr/bin/env python3
"""Run 0231 parent close-out: fresh single-call reads for 3 flagged items.
- AgentBook: remainingFree()/freeClaimed() fresh (sellout already reported by
  hot-leg ~22:19 WIB Nov 7; confirm before moving to excluded).
- SPACE ROT: agent-shape + free pool + user slot (discovery flag).
- Ticker Pets: agent-shape + free pool + user slot (discovery flag).
Single eth_call per batch (fast_rpc.batch whole-batch-revert quirk).
Read-only; writes run-2026-11-08-0231-closeout.json (own file)."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

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
        return "ERR:" + str(e)[:100]

def code_has_registry(addr):
    try:
        code = batch([("eth_getCode", [addr, "latest"])])[0]
        return REG[2:].lower() in (code or "").lower()
    except Exception as e:
        return "ERR:" + str(e)[:80]

out = {"run": "0231", "wib": "2026-11-08 ~02:55 WIB"}
try:
    out["block"] = int(batch([("eth_blockNumber", [])])[0], 16)
except Exception as e:
    out["block"] = "ERR:" + str(e)[:80]

ABOOK = "0xEECaCBE6eAC6D6F2a38e8daA9049C7AA08aD43b0"
out["agentbook"] = {
    "remainingFree": call(ABOOK, "remainingFree()"),
    "freeClaimed": call(ABOOK, "freeClaimed()"),
    "totalSupply": call(ABOOK, "totalSupply()"),
    "FREE_QUOTA": call(ABOOK, "FREE_QUOTA()"),
    "mintOpen": call(ABOOK, "mintOpen()"),
    "balanceOf_user": call(ABOOK, "balanceOf(address)", enc(USER)),
    "freeUsed_user": call(ABOOK, "freeUsed(address)", enc(USER)),
}

for label, addr in [("spacerot", "0x6c724401f0C99E63d0119c17c97665f07c978Ef3"),
                    ("tickerpets", "0x31975837d5c68eea0b66b5fd27de3506c2f109ba")]:
    d = {}
    for sig in ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
                "freeLeft()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()"]:
        d[sig.split("(")[0]] = call(addr, sig)
    d["AGENT_ID"] = call(addr, "AGENT_ID()")
    d["agentRegistry"] = call(addr, "agentRegistry()")
    d["balanceOf_user"] = call(addr, "balanceOf(address)", enc(USER))
    d["freeClaimed_user"] = call(addr, "freeClaimed(address)", enc(USER))
    d["quote_user_1"] = call(addr, "quote(address,uint256)", enc(USER) + format(1, "064x"))
    d["registry_bytes"] = code_has_registry(addr)
    out[label] = d

json.dump(out, open(f"{BASE}/run-2026-11-08-0231-closeout.json", "w"), indent=1)
print(json.dumps(out, indent=1))
