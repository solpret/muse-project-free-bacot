#!/usr/bin/env python3
"""Verify-2 run 2026-11-06 1731 WIB. Read-only.
Boltbook front-page follow-ups (~17:44-17:50 WIB):
- Botphoenix 0x221f...: post claims SOLD OUT 600/600 free -> verify freeClaimed/FREE_SUPPLY on-chain.
- Ape Agent 0x8150...: NEW name (229/4,444, mint(1) value 0) -> reads + registry-bytes check (Sourcify NOT verified).
- Teslagent FreeCarClaim 0x022e...: NEW name (5,000 free Cyberquad, 200 TAG/car) -> state reads (ABI verified: EIP-712 signature claim, X-bound, NO agent gate).
"""
import json, urllib.request, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1731"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed2.bnbchain.org"]
REGISTRY = "60b9262456de011f7d15a54cdd8c48baa8b022f"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data, timeout=6):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None

def code_has_registry(addr):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                               "params": [addr, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=6) as r:
                code = json.load(r)["result"]
            if code and code != "0x":
                return REGISTRY in code.lower(), len(code)
        except Exception:
            continue
    return None, None

def call(to, sig, args=""): return raw(to, sel(sig) + args)

ITEMS = {
 "Botphoenix": ("0x221f42a2516dd4462c572f84b777a6f4e94135a4",
                ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
                 "FREE_SUPPLY()", "FREE_PER_WALLET()", "MAX_SUPPLY()", "mintOpen()",
                 "mintedBy(address)", "freeUsed(address)", "balanceOf(address)",
                 "quote(address,uint256)"]),
 "Ape Agent": ("0x8150922eb36b7d5972b6b06254435dd755a7c54c",
               ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
                "FREE_SUPPLY()", "MAX_SUPPLY()", "MAX_PER_WALLET()", "mintOpen()",
                "mintedBy(address)", "freeUsed(address)", "balanceOf(address)",
                "quote(address,uint256)"]),
 "Teslagent-FreeCarClaim": ("0x022e36ED4D0552AAf647D8891d2A79281ed11e65",
               ["remaining()", "claimedCount()", "claimClosed()", "claimDeadline()",
                "CLAIM_PERIOD()", "PER_CAR()", "claimed(address)", "CARS()"]),
}

out = {}
for name, (addr, views) in ITEMS.items():
    d = {"address": addr}
    for sig in views:
        key = sig.split("(")[0]
        if "address" in sig and "uint256" in sig:
            v = call(addr, sig, enc(USER) + enc_uint(1)); key += "_user_1"
        elif "address" in sig:
            v = call(addr, sig, enc(USER)); key += "_user"
        else:
            v = call(addr, sig)
        d[key] = v
    print(name, json.dumps(d, default=str), flush=True)
    out[name] = d

for name, (addr, _) in ITEMS.items():
    hit, ln = code_has_registry(addr)
    out[name]["registry_bytes_hit"] = hit
    out[name]["code_len"] = ln
    print(name, "registry_bytes_hit=", hit, "code_len=", ln, flush=True)

json.dump(out, open(f"{BASE}/run-{TS}-verify2.json", "w"), indent=1, ensure_ascii=False)
print("VERIFY2 DONE", flush=True)
