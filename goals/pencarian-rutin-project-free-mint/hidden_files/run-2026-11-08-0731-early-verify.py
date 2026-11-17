#!/usr/bin/env python3
"""Parent verification of 2 first-seen early leads (Dafeiyu, HokiKoi), run 0731.
Read-only, single-call batches (batch reverts if one view reverts)."""
import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def single(addr, data):
    for ep in EPS:
        try:
            res = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=10)
            return res[0]
        except Exception:
            continue
    return None
def view(addr, sig, arg=None):
    data = sel(sig) + (enc(arg) if arg else "")
    r = single(addr, data)
    return to_int(r)
def addr_view(addr, sig):
    r = single(addr, sel(sig))
    if r is None: return None
    try:
        return "0x" + r[-40:]
    except Exception: return None
VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "freeCount()",
         "FREE_SUPPLY()", "FREE_CAP()", "MAX_SUPPLY()", "mintOpen()",
         "freeAgentCount()", "isFreeAgent(address)", "freeClaimed(address)", "mintedBy(address)"]
out = {}
for name, addr in [("Dafeiyu", "0xD8DE64ACB25A87D98F1E170BF082a01427772511"),
                   ("HokiKoi", "0x74055b4Afe2d8c7347e8D4c0fc23e704405F7A36")]:
    d = {}
    for sig in VIEWS:
        arg = USER if "(address)" in sig else None
        d[sig.split("(")[0] + ("_user" if arg else "")] = view(addr, sig, arg)
        time.sleep(0.2)
    d["owner"] = addr_view(addr, "owner()")
    d["AGENT_ID"] = addr_view(addr, "AGENT_ID()")
    d["agentRegistry"] = addr_view(addr, "agentRegistry()")
    d["AGENT_REGISTRY"] = addr_view(addr, "AGENT_REGISTRY()")
    d["agentIdRegistry"] = addr_view(addr, "agentIdRegistry()")
    print(name, json.dumps(d), flush=True)
    out[name] = {"address": addr, "views": d}
try:
    b = batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=10)
    out["block"] = int(b[0], 16)
except Exception as e:
    out["block"] = None
print("block", out["block"], flush=True)
json.dump(out, open("run-2026-11-08-0731-early-verify.json", "w"), indent=1)
