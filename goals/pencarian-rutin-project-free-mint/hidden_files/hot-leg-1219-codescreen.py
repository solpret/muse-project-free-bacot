#!/usr/bin/env python3
"""Fast shape screen: one batched eth_getCode for all addrs on a single healthy
dataseed, then selector-presence + registry-bytes analysis of runtime code.
Read-only. Prints JSON."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak

EP = "https://bsc-dataseed2.bnbchain.org/"
REGISTRY = "60b9262456de011f7d15a54cdd8c48baaa8b022f"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return k.hexdigest()[:8]

SIGS = {
 "mint(uint256)": "mint(uint256)",
 "mint(uint256,address)": "mint(uint256,address)",
 "mintFree()": "mintFree()",
 "claimFree()": "claimFree()",
 "quote(address,uint256)": "quote(address,uint256)",
 "freeClaimed(address)": "freeClaimed(address)",
 "freeClaimed()": "freeClaimed()",
 "freeMinted()": "freeMinted()",
 "freeLeft()": "freeLeft()",
 "freeLeft(address)": "freeLeft(address)",
 "freeFor(address)": "freeFor(address)",
 "freeUsed(address)": "freeUsed(address)",
 "freeAvailable()": "freeAvailable()",
 "freeSharesRemaining()": "freeSharesRemaining()",
 "freeSharePoolExhausted()": "freeSharePoolExhausted()",
 "freeSharesClaimed()": "freeSharesClaimed()",
 "agentRegistry()": "agentRegistry()",
 "registry()": "registry()",
 "AGENT_ID()": "AGENT_ID()",
 "name()": "name()",
 "symbol()": "symbol()",
 "decimals()": "decimals()",
 "totalSupply()": "totalSupply()",
 "FREE_SLOTS()": "FREE_SLOTS()",
 "FREE_SUPPLY()": "FREE_SUPPLY()",
 "FREE_CAP()": "FREE_CAP()",
}

def batch_getcode(addrs):
    calls = [("eth_getCode", [a, "latest"]) for a in addrs]
    res = batch(calls, endpoint=EP)
    out = {}
    for a, r in zip(addrs, res):
        out[a] = r
    return out

def main(addrs):
    codes = batch_getcode(addrs)
    res = {}
    for a in addrs:
        code = codes.get(a)
        if not isinstance(code, str):
            res[a] = {"error": str(code)[:120]}
            continue
        cl = code.lower()
        present = {name: (sel(sig) in cl) for name, sig in SIGS.items()}
        mint = any(present[k] for k in ("mint(uint256)", "mint(uint256,address)", "mintFree()", "claimFree()"))
        quote = present["quote(address,uint256)"]
        free = any(present[k] for k in ("freeClaimed(address)", "freeClaimed()", "freeMinted()",
                                        "freeLeft()", "freeLeft(address)", "freeFor(address)",
                                        "freeUsed(address)", "freeAvailable()",
                                        "freeSharesRemaining()", "freeSharePoolExhausted()",
                                        "freeSharesClaimed()"))
        agent = (REGISTRY in cl) or present["agentRegistry()"] or present["registry()"] or present["AGENT_ID()"]
        token = all(present[k] for k in ("name()", "symbol()", "decimals()", "totalSupply()"))
        res[a] = {"code_len": (len(code) - 2) // 2, "registry_bytes": REGISTRY in cl,
                  "mint_sel": mint, "quote_sel": quote, "free_sel": free, "agent_ref": agent,
                  "token_fns": token, "S1_screen": bool(mint and quote and free and agent),
                  "S2_screen": bool(token and present["mintFree()"] and free and agent),
                  "selectors": {k: v for k, v in present.items() if v}}
    print(json.dumps(res, indent=1))

if __name__ == "__main__":
    main(sys.argv[1:])
