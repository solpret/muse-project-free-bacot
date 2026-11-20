#!/usr/bin/env python3
"""CAP7 0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd - independent on-chain verification.
Boltbook post xMapMKeuhjlv (agata.ai, 09:30 WIB) is third-party data only.
Reads: Sourcify ABI, free views, price, deadline, user slot, agent gate, token meta."""
import json, subprocess, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
import fast_rpc
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def enc_u(n): return "%064x" % n
def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "free-mint-search/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()
out = {"contract": ADDR, "started_wib": "2026-11-17 ~09:33 WIB"}
# Sourcify ABI
try:
    raw = fetch(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi")
    meta = json.loads(raw.decode())
    abi = meta.get("abi", [])
    fns = {}
    for e in abi:
        if e.get("type") == "function":
            fns.setdefault(e["name"], []).append(e)
    out["sourcify"] = {"status": meta.get("status") or meta.get("match"), "verified": True,
                       "verifiedAt": meta.get("verifiedAt"), "n_fns": len(fns),
                       "functions": sorted(fns.keys())}
    json.dump(meta, open(f"{HF}/run-2026-11-17-0931-cap7-abi.json", "w"), indent=1)
except Exception as e:
    out["sourcify"] = {"verified": False, "error": f"{type(e).__name__}: {str(e)[:200]}"}
    fns = {}
# on-chain reads
SIGS = ["freeMinted()", "FREE_SHARES()", "paidMinted()", "totalSupply()",
        "deadline()", "PRICE()", "claimFree()", "mintOpen()", "saleOpen()",
        "totalMinted()", "MAX_SUPPLY()", "FREE_SUPPLY()", "freeSharesRemaining()",
        "freeLeft()", "freeClaimed(address)", "hasClaimed(address)",
        "freeClaimedBy(address)", "claimed(address)", "hasAgentId(address)",
        "agentId()", "agentRegistry()", "owner()", "name()", "symbol()",
        "decimals()", "quote(uint256)", "cost(uint256)", "costOf(uint256)",
        "claimable(address)", "balanceOf(address)", "mintedBy(address)"]
calls, labels = [], []
for s in SIGS:
    if "(address)" in s:
        calls.append((ADDR, "0x" + sel(s) + enc_addr(USER)))
    elif "(uint256)" in s:
        calls.append((ADDR, "0x" + sel(s) + enc_u(1)))
    else:
        calls.append((ADDR, "0x" + sel(s)))
    labels.append(s)
def batch(calls, timeout=15):
    payload = [{"jsonrpc": "2.0", "id": i+1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(calls)]
    body = json.dumps(payload).encode()
    for ep in fast_rpc.healthy_endpoints() or fast_rpc.ENDPOINTS:
        try:
            req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                outp = json.loads(r.read().decode())
            res = []
            by_id = {it["id"]: it for it in outp if isinstance(it, dict)}
            for i in range(len(calls)):
                it = by_id.get(i+1, {})
                if "result" in it and it["result"] not in (None, "0x"):
                    try: res.append(int(it["result"], 16))
                    except Exception: res.append(it["result"])
                else: res.append(None)
            return res, ep
        except Exception:
            continue
    raise IOError("all endpoints failed")
try:
    res, ep = batch(calls)
    out["endpoint"] = ep
    out["views"] = dict(zip(labels, res))
    # block
    payload = json.dumps([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}]).encode()
    req = urllib.request.Request(ep, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        out["block"] = int(json.loads(r.read().decode())[0]["result"], 16)
except Exception as e:
    out["views_error"] = f"{type(e).__name__}: {str(e)[:300]}"
# bytecode registry check
try:
    payload = json.dumps([{"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                           "params": [ADDR, "latest"]}]).encode()
    req = urllib.request.Request(out.get("endpoint") or "https://bsc-dataseed.binance.org/",
                                 data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        code = json.loads(r.read().decode())[0]["result"]
    out["bytecode_len"] = (len(code) - 2) // 2 if code else 0
    out["registry_bytes"] = REGISTRY[2:].lower() in code.lower()
except Exception as e:
    out["bytecode_error"] = str(e)[:150]
json.dump(out, open(f"{HF}/run-2026-11-17-0931-cap7-verify.json", "w"), indent=1)
print(json.dumps(out, indent=1))
