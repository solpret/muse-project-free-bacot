#!/usr/bin/env python3
"""hot-leg 2026-11-09 12:19 shape-check: Sourcify metadata ABI first, then
on-chain selector probing via fast_rpc (single-call race, no batch, so one
revert cannot poison the rest). Read-only. Writes JSON to stdout."""
import json, sys, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak

REGISTRY = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedTotal"]
MINT_FNS = ["mint", "mintFree", "claimFree", "claim"]
QUOTE_FNS = ["quote", "cost", "PRICE", "price"]
AGENT_MARKERS = ["agentRegistry", "registry", "AGENT_ID", "AgentGate",
                 "agentGate", "isAgent", "hasAgentId", "agentIdRequired"]
TOKEN_FNS = ["name", "symbol", "decimals", "totalSupply"]

def sel(sig):
    k = keccak.new(digest_bits=256)
    k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def fetch_abi(addr):
    for kind in ("full_match", "partial_match"):
        url = f"https://repo.sourcify.dev/contracts/{kind}/56/{addr}/metadata.json"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "hot-leg/1.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                meta = json.load(r)
            abi = meta.get("output", {}).get("abi") or meta.get("abi")
            if abi:
                return abi, kind, None
            return None, kind, "metadata-no-abi"
        except urllib.error.HTTPError as e:
            err = f"HTTP {e.code}"
            continue
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
            continue
    return None, None, err

def probe(addr):
    """Probe no-arg + address-arg views with single eth_call races."""
    out = {}
    # eth_getCode for registry bytes
    try:
        code = race("eth_getCode", [addr, "latest"])
        out["code_len"] = (len(code) - 2) // 2 if isinstance(code, str) and code.startswith("0x") else None
        out["registry_bytes_in_code"] = REGISTRY in (code or "").lower()
    except Exception as e:
        out["code_error"] = str(e)
    views = {}
    for fn in ["name()", "symbol()", "decimals()", "totalSupply()",
               "freeClaimed()", "freeMinted()", "freeSharesRemaining()",
               "freeLeft()", "freeAvailable()", "freeSharePoolExhausted()",
               "freeSharesClaimed()", "FREE_SLOTS()", "FREE_SUPPLY()",
               "FREE_CAP()", "FREE_AMOUNT()", "agentRegistry()", "registry()",
               "AGENT_ID()", "mintOpen()", "totalMinted()", "mintedCount()"]:
        try:
            r = race("eth_call", [{"to": addr, "data": sel(fn)}, "latest"])
            views[fn] = "ok" if r and r != "0x" else ("empty" if r == "0x" else "null")
            if r and r != "0x":
                try:
                    views[fn + "_val"] = int(r, 16)
                except Exception:
                    views[fn + "_raw"] = (r or "")[:66]
        except Exception as e:
            views[fn] = f"err:{type(e).__name__}"
    out["views"] = views
    # quote(address,uint256) with zero address + 1
    try:
        data = sel("quote(address,uint256)") + "00" * 32 + "01".rjust(64, "0")
        r = race("eth_call", [{"to": addr, "data": data}, "latest"])
        out["quote_zero_addr_1"] = "ok" if r and r != "0x" else ("empty" if r == "0x" else "null")
    except Exception as e:
        out["quote_zero_addr_1"] = f"err:{type(e).__name__}"
    return out

def shape_from_abi(abi):
    names = [f.get("name") for f in abi if isinstance(f, dict) and f.get("type") == "function" and f.get("name")]
    fns = set(names)
    mint = [n for n in MINT_FNS if n in fns] or [n for n in fns if n.startswith("mint")]
    quote = [n for n in QUOTE_FNS if n in fns]
    free = [n for n in FREE_VIEWS if n in fns]
    agent = [n for n in AGENT_MARKERS if n in fns]
    token = [n for n in TOKEN_FNS if n in fns]
    s1 = bool(mint and quote and free and agent)
    s2 = bool(token == TOKEN_FNS and "mintFree" in fns and free and agent)
    return {"fns": sorted(fns), "mint": mint, "quote": quote, "free": free,
            "agent": agent, "token": token, "S1": s1, "S2": s2}

def main(addrs):
    res = {}
    for a in addrs:
        abi, kind, err = fetch_abi(a)
        if abi:
            sh = shape_from_abi(abi)
            sh["abi_source"] = kind
            res[a] = sh
        else:
            res[a] = {"abi_error": err, "probe": probe(a)}
    print(json.dumps(res, indent=1))

if __name__ == "__main__":
    main(sys.argv[1:])
