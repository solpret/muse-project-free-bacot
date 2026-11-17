#!/usr/bin/env python3
"""READ-ONLY sale-shape checker (S1/S2) for Free Bacot run 1931.
Fetches Sourcify ABI, classifies shape, verifies registry via on-chain eth_call.
Registry presence is NEVER judged from ABI text alone.
Usage: python3 run-2026-11-05-1931-shapecheck.py <addr1> [addr2 ...] --out <file>
"""
import json, sys, urllib.request, time
from Crypto.Hash import keccak

REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]

def sel(sig):
    k = keccak.new(digest_bits=256)
    k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def eth_call(to, data):
    payload = json.dumps({"jsonrpc": "2.0", "method": "eth_call",
                          "params": [{"to": to, "data": data}, "latest"], "id": 1}).encode()
    last = None
    for url in RPCS:
        try:
            req = urllib.request.Request(url, data=payload,
                                         headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=10) as r:
                d = json.load(r)
            if "result" in d:
                return d["result"]
            last = d
        except Exception as e:
            last = str(e)
    return None

def call_view(to, sig):
    """eth_call a no-arg view; returns raw hex or None."""
    return eth_call(to, sel(sig))

def decode_addr(hexres):
    if not hexres or hexres == "0x":
        return None
    try:
        v = int(hexres, 16)
        return "0x" + format(v, "040x")
    except Exception:
        return None

def decode_uint(hexres):
    if not hexres or hexres == "0x":
        return None
    try:
        return int(hexres, 16)
    except Exception:
        return None

def get_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    req = urllib.request.Request(url, headers={"User-Agent": "free-bacot/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.load(r)
    abi = d.get("abi")
    if abi is None and isinstance(d, dict):
        # some responses nest under "stdJson" or return abi directly
        abi = d.get("stdJson", {}).get("abi") if isinstance(d.get("stdJson"), dict) else None
    return abi, d

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "FREE_SLOTS", "FREE_SUPPLY"]
REGISTRY_GETTERS = ["AGENT_ID()", "AGENT_REGISTRY()", "REGISTRY()", "agentRegistry()"]
QUOTE_FNS = ["quote(address,uint256)", "quote(uint256)", "cost(address,uint256)",
             "cost(uint256)", "getPrice(uint256)", "price()", "mintPrice()"]

def check(addr):
    out = {"address": addr}
    try:
        abi, raw = get_abi(addr)
    except Exception as e:
        out["sourcify"] = "error"
        out["error"] = str(e)
        return out
    if not abi:
        out["sourcify"] = "unverified"
        out["verdict"] = "unknown-shape"
        out["reason"] = "Sourcify-unverified; free shape unknown, not agent-shaped on bytecode alone"
        return out
    out["sourcify"] = "verified"
    fns = {}
    for e in abi:
        if e.get("type") == "function":
            fns[e.get("name")] = e
    out["functions"] = sorted(fns.keys())
    # name/symbol/decimals/totalSupply presence (S2 token test)
    has_token = all(n in fns for n in ("name", "symbol", "decimals", "totalSupply"))
    out["is_token"] = has_token
    if has_token:
        try:
            nm = eth_call(addr, sel("name()"))
            out["name_raw"] = nm
        except Exception:
            pass
    # mint functions
    mint_fns = [n for n in fns if n.lower().startswith("mint") or n in ("claimFree", "claim", "freeMint")]
    out["mint_functions"] = mint_fns
    noarg_free = [n for n in mint_fns if len(fns[n].get("inputs", [])) == 0]
    out["noarg_free_mint"] = noarg_free
    # quote/cost
    out["quote_functions"] = [n for n in fns if n.lower() in ("quote", "cost", "getprice", "price", "mintprice")]
    # free views present in ABI
    out["free_views_in_abi"] = [v for v in FREE_VIEWS if v in fns]
    # registry via on-chain eth_call (never ABI text)
    reg_hits = {}
    for g in REGISTRY_GETTERS:
        if g.split("(")[0] in fns:
            res = call_view(addr, g)
            dec = decode_addr(res)
            reg_hits[g] = dec
    out["registry_getter_calls"] = reg_hits
    out["registry_match"] = any(
        (v or "").lower() == REGISTRY.lower() for v in reg_hits.values() if v)
    # free pool reads (best effort)
    pool = {}
    for v in ("FREE_SUPPLY", "freeSharesRemaining", "freeLeft", "freeAvailable"):
        if v in fns:
            res = call_view(addr, v + "()")
            pool[v] = decode_uint(res)
    for v in ("freeMinted", "freeClaimed"):
        if v in fns:
            res = call_view(addr, v + "()")
            pool[v] = decode_uint(res)
    if "totalSupply" in fns:
        pool["totalSupply"] = decode_uint(call_view(addr, "totalSupply()"))
    out["pool_reads"] = pool
    # shape verdicts
    s1 = bool(mint_fns) and bool(out["quote_functions"]) and bool(out["free_views_in_abi"]) and out["registry_match"]
    s2 = has_token and bool(noarg_free) and bool(out["free_views_in_abi"]) and out["registry_match"]
    out["shape_S1"] = s1
    out["shape_S2"] = s2
    if s1 or s2:
        out["verdict"] = "SALE-SHAPED"
        out["reason"] = "S1" if s1 else "S2"
    else:
        missing = []
        if not mint_fns:
            missing.append("no mint fn")
        if not out["quote_functions"] and not noarg_free:
            missing.append("no quote/cost fn and no no-arg free mint")
        if not out["free_views_in_abi"]:
            missing.append("no free-share view")
        if not out["registry_match"]:
            missing.append("no registry match via on-chain getter")
        out["verdict"] = "not-sale-shaped"
        out["reason"] = "; ".join(missing)
    return out

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    outpath = None
    if "--out" in sys.argv:
        outpath = sys.argv[sys.argv.index("--out") + 1]
    results = []
    for a in args:
        r = check(a)
        results.append(r)
        print(a, "->", r.get("verdict"), "|", r.get("reason", ""))
        time.sleep(0.3)
    if outpath:
        with open(outpath, "w") as f:
            json.dump(results, f, indent=1)
        print("wrote", outpath)
