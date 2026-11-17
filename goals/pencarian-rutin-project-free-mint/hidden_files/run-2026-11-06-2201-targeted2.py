#!/usr/bin/env python3
"""Run 2201 targeted2: BNBFLY (early, slot MIN_BALANCE-blocked) + CLEP (track-C
lead, gate-blocked). Read-only; writes run-2026-11-06-2201-targeted2.json."""
import json, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-2201"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC = "https://bsc-dataseed1.bnbchain.org"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")

def raw(to, data):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": to, "data": data}, "latest"]}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r: out = json.load(r)
        if "error" in out: return None
        v = out["result"]
        if not v or v == "0x": return None
        try: return int(v, 16)
        except Exception: return v
    except Exception:
        return None

def call(to, sig, args=""): return raw(to, sel(sig) + args)

TARGETS = {
    "BNBFLY Agent Pass": ("0x7fe03C055588bd5018825175D791103c5CBEd8be",
        ["totalSupply()", "claimOpen()", "CLAIM_START()", "CLAIM_END()", "MIN_BALANCE()"]),
    "CLEPSYDRA": ("0x9e2738B3DD3773c6c71cA24Fbc92660B501C0B6b",
        ["totalSupply()", "freeClaimed()", "freeTaken()", "FREE_TOKENS()",
         "FREE_PER_WALLET()", "listed()", "soldTokens()", "raised()"]),
}
out = {"run": TS}
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {}
    for name, (addr, views) in TARGETS.items():
        for v in views:
            futs[(name, v)] = ex.submit(call, addr, v)
    futs[("BNBFLY Agent Pass", "hasSBT(user)")] = ex.submit(
        call, TARGETS["BNBFLY Agent Pass"][0], "hasSBT(address)", enc(USER))
    futs[("BNBFLY Agent Pass", "balanceOf(user)")] = ex.submit(
        call, TARGETS["BNBFLY Agent Pass"][0], "balanceOf(address)", enc(USER))
    futs[("CLEPSYDRA", "claimed(user)")] = ex.submit(
        call, TARGETS["CLEPSYDRA"][0], "claimed(address)", enc(USER))
    futs[("CLEPSYDRA", "balanceOf(user)")] = ex.submit(
        call, TARGETS["CLEPSYDRA"][0], "balanceOf(address)", enc(USER))
    futs[("CLEPSYDRA", "pair()")] = ex.submit(
        call, TARGETS["CLEPSYDRA"][0], "pair()")
    for (name, v), f in futs.items():
        out.setdefault(name, {})[v] = f.result()
    # user BNB balance (MIN_BALANCE check for BNBFLY)
    try:
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBalance",
                           "params": [USER, "latest"]}).encode()
        req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            out["user_bnb_wei"] = int(json.load(r)["result"], 16)
    except Exception as e:
        out["user_bnb_error"] = str(e)
print(json.dumps(out, indent=1))
json.dump(out, open(f"{BASE}/run-{TS}-targeted2.json", "w"), indent=1)
print("TARGETED2 DONE")
