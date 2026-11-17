#!/usr/bin/env python3
"""Verify 6 first-seen contracts from scan 0031 — read-only.
Sourcify ABI (retry once) + free views on-chain via fast_rpc race.
"""
import json, sys, time, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak
from fast_rpc import race

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
TARGETS = {
 "AgentVerse-Citizen-0031": "0x6052115065322be020b94De616e31B27EC30B0E2",
 "RIPSTACK-Genesis-0031": "0x72376F145c3e6af620b2aBEA259F9193460643Bd",
 "AgentCard-0031": "0xeE1749f66BA7e6199084813246852c0f7177b6ce",
 "Mizukairo-0031": "0x43F046F5C49E54D42913743a8fd2D146CE494C4C",
 "MOLT-0031": "0x8EcaFBA8Bf911698C13D5f14D7b7241f4F80BE5B",
 "First-Dollar-Grove-0031": "0x56466afBcC2FDB847ed2cf5Bf78Ec1B213253611",
}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def sourcify_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return ("verified", json.loads(r.read().decode()).get("abi"))
        except urllib.error.HTTPError as e:
            return (f"http_{e.code}", None)
        except Exception as e:
            if attempt == 0:
                time.sleep(5); continue
            return (f"error:{type(e).__name__}", None)

def call(addr, sig, args=""):
    try:
        return to_int(race("eth_call", [{"to": addr, "data": sel(sig) + args}, "latest"]))
    except Exception:
        return None

out = {}
for name, addr in TARGETS.items():
    t = time.time()
    status, abi = sourcify_abi(addr)
    free_funcs, mint_funcs, gate = [], [], False
    if isinstance(abi, list):
        for item in abi:
            if item.get("type") != "function": continue
            nm = item.get("name", "")
            if "free" in nm.lower() and not nm.lower().startswith("freeze"): free_funcs.append(nm)
            if "mint" in nm.lower(): mint_funcs.append(nm)
            if nm.lower() in ("agentid", "agentregistry", "agentgate", "hasagentid"): gate = True
    views = {}
    for sig in ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()"]:
        views[sig.split("(")[0]] = call(addr, sig)
    views["balanceOf_user"] = call(addr, "balanceOf(address)", enc(USER))
    views["quote_user_1"] = call(addr, "quote(address,uint256)", enc(USER) + enc_uint(1))
    if views["quote_user_1"] is None:
        views["quoteFor_user_1"] = call(addr, "quoteFor(address,uint256)", enc(USER) + enc_uint(1))
    d = {"address": addr, "sourcify": status, "free_funcs": sorted(set(free_funcs))[:12],
         "mint_funcs": sorted(set(mint_funcs))[:12], "agent_gate_fn": gate, "views": views,
         "elapsed_s": round(time.time() - t, 1)}
    out[name] = d
    print(name, json.dumps(d), flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-07-0031-firstseen-verify.json", "w"), indent=1)
print("FIRSTSEEN-VERIFY DONE", flush=True)
