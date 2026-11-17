#!/usr/bin/env python3
"""Fresh verify NOVRA 0x75Ac13cF23a8dccC703D1496138251FD7f247890 (track-C S2 candidate from route-3 search). Read-only."""
import sys, json, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import batch
from eth_hash.auto import keccak

AGENT = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
A = "0x75Ac13cF23a8dccC703D1496138251FD7f247890"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]

def selector(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]
def enc_addr(a): return "000000000000000000000000" + a[2:].lower()
def enc_uint(n): return format(n, "064x")
def raw_call(addr, data, timeout=15):
    last = None
    for ep in EPS:
        try:
            return batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=timeout)[0]
        except Exception as e:
            last = e
    raise last
def dec_uint(h):
    if not h or h == "0x": return None
    try: return int(h, 16)
    except Exception: return None
def dec_bool(h):
    v = dec_uint(h); return None if v is None else bool(v)
def tc(sig, args=""):
    try: return raw_call(A, selector(sig) + args)
    except Exception as e: return f"ERR:{type(e).__name__}"

# ABI from Sourcify (exact_match)
req = urllib.request.Request("https://sourcify.dev/server/v2/contract/56/" + A + "?fields=abi", headers={"User-Agent": "Mozilla/5.0"})
try:
    abi = json.load(urllib.request.urlopen(req, timeout=30))["abi"]
except Exception as e:
    abi = []
    print("ABI fetch failed:", e)
fns = [f["name"] for f in abi if f.get("type") == "function"]
print("ABI functions:", fns)
out = {"address": A, "abi_functions": fns}
for sig, key in [
    ("name()", "name"), ("symbol()", "symbol"), ("decimals()", "decimals"),
    ("totalSupply()", "totalSupply"), ("freeRemaining()", "freeRemaining"),
    ("freeMinted()", "freeMinted"), ("sharesMinted()", "sharesMinted"),
    ("paidShares()", "paidShares"), ("soldOut()", "soldOut"),
    ("closed()", "closed"), ("MAX_FREE()", "MAX_FREE"),
    ("MAX_SHARES()", "MAX_SHARES"), ("PRICE()", "PRICE"),
    ("TOKENS_PER_SHARE()", "TOKENS_PER_SHARE"),
]:
    r = tc(sig)
    out[key] = dec_uint(r) if not (isinstance(r, str) and r.startswith("ERR")) else r
for sig, key in [
    ("freeClaimed(address)", "freeClaimed_agent"),
    ("hasMinted(address)", "hasMinted_agent"),
    ("freeAvailable(address)", "freeAvailable_agent"),
    ("balanceOf(address)", "balanceOf_agent"),
]:
    r = tc(sig, enc_addr(AGENT))
    out[key] = dec_uint(r) if not (isinstance(r, str) and r.startswith("ERR")) else r
for sig, key in [("quote(uint256)", "quote_1"), ("costWei(uint256)", "costWei_1")]:
    r = tc(sig, enc_uint(1))
    out[key] = dec_uint(r) if not (isinstance(r, str) and r.startswith("ERR")) else r
# agent registry reference
for sig in ["agentId()", "agentRegistry()", "AGENT_ID()", "AGENT_REGISTRY()"]:
    r = tc(sig)
    if isinstance(r, str) and r.startswith("0x") and len(r) >= 66:
        out["registry_ref_" + sig] = r[-40:]
        break
out["registry_ref"] = out.get("registry_ref_agentId()", out.get("registry_ref_agentRegistry()", "NOT FOUND"))
json.dump(out, open("run-2026-11-08-1731-novra-verify.json", "w"), indent=1)
print(json.dumps(out, indent=1))
