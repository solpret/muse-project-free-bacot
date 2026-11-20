#!/usr/bin/env python3
"""Verify ARKYN (Boltbook lead, first launched read this run) + Orin-2 contract 0xa045 (Boltbook recheck)."""
import json, subprocess, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
import fast_rpc
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def call(to, sig, arg=None):
    d = "0x" + sel(sig)
    if arg == "user": d += enc_addr(USER)
    return (to, d)
def batch(calls):
    payload = [{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":t,"data":d},"latest"]} for i,(t,d) in enumerate(calls)]
    body = json.dumps(payload).encode()
    for ep in fast_rpc.healthy_endpoints() or fast_rpc.ENDPOINTS:
        try:
            req = urllib.request.Request(ep, data=body, headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                outp = json.loads(r.read().decode())
            by = {it["id"]: it for it in outp if isinstance(it, dict)}
            res = []
            for i in range(len(calls)):
                it = by.get(i+1, {})
                if "result" in it and it["result"] not in (None, "0x"):
                    try: res.append(int(it["result"], 16))
                    except Exception: res.append(it["result"])
                else: res.append(None)
            return res, ep
        except Exception:
            continue
    raise IOError("all endpoints failed")
ARKYN = "0x69b0b5756671680766d232eb4b0f39a34be5d852"
ORIN2 = "0xa04513d85e02e1a1623a985269b3ebd46fa76b98"
views = ["totalSupply()","totalMinted()","freeMinted()","freeClaimed()","FREE_SUPPLY()","MAX_SUPPLY()",
         "mintActive()","mintOpen()","freeRemaining()","freeLeft()","mintPrice()","PAID_PRICE()",
         "freeMintedBy(address)","mintedBy(address)","freeUsed(address)","balanceOf(address)"]
calls, meta = [], []
for addr, name in ((ARKYN,"ARKYN"), (ORIN2,"ORIN2")):
    for v in views:
        arg = "user" if "(address)" in v else None
        calls.append(call(addr, v, arg)); meta.append((name, addr, v))
res, ep = batch(calls)
out = {"endpoint": ep}
for (name, addr, v), val in zip(meta, res):
    out.setdefault(name, {"address": addr, "views": {}})["views"][v] = val
# Sourcify ARKYN ABI (agent refs + free views)
for addr, name in ((ARKYN,"ARKYN"), (ORIN2,"ORIN2")):
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
                                     headers={"User-Agent":"free-mint-search/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            meta2 = json.loads(r.read().decode())
        abi = meta2.get("abi", [])
        fns = sorted({e["name"] for e in abi if e.get("type")=="function"})
        out[name]["sourcify"] = {"verified": True, "verifiedAt": meta2.get("verifiedAt"),
            "agent_fns": [f for f in fns if any(k in f.lower() for k in ("agent","registry"))],
            "free_fns": [f for f in fns if "free" in f.lower()],
            "mint_fns": [f for f in fns if "mint" in f.lower()],
            "n_fns": len(fns)}
    except Exception as e:
        out[name]["sourcify"] = {"verified": False, "error": f"{type(e).__name__}: {str(e)[:120]}"}
# head block
try:
    payload = json.dumps([{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}]).encode()
    req = urllib.request.Request(ep, data=payload, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        out["block"] = int(json.loads(r.read().decode())[0]["result"], 16)
except Exception as e:
    out["block_error"] = str(e)[:120]
json.dump(out, open("run-2026-11-17-1531-verify.json","w"), indent=1)
print(json.dumps(out, indent=1))
