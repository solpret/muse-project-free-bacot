#!/usr/bin/env python3
"""Verify new lead run 1101: Mechfarm 0x1fab + Sourcify feed new 0x9D00/0xb43a/0xf2dD (Boltbook ZH, bdnoman.ai post ~4 min ago). Read-only."""
import json, subprocess
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC = "https://bsc-dataseed.binance.org/"
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted", "freeCardsRemaining"}

def get(url, timeout=25):
    r = subprocess.run(["curl", "-s", "-L", "--max-time", str(timeout), url],
                       capture_output=True, timeout=timeout + 5)
    return json.loads(r.stdout.decode())

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

def post(payload, timeout=25):
    r = subprocess.run(["curl", "-s", "-L", "--max-time", str(timeout), RPC,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, timeout=timeout + 5)
    return json.loads(r.stdout.decode())

def batch(addr, views):
    calls = []
    for label, sig, arg in views:
        data = "0x" + sel(sig)
        if arg == "user":
            data += enc_addr(USER)
        elif arg == "one":
            data += "%064x" % 1
        elif arg == "user1":
            data += enc_addr(USER) + "%064x" % 1
        calls.append({"jsonrpc": "2.0", "id": len(calls) + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
    try:
        resp = post(calls)
        out = {}
        for (label, sig, arg), it in zip(views, resp):
            if isinstance(it, dict) and "result" in it and it["result"] not in (None, "0x"):
                try:
                    out[label] = int(it["result"], 16)
                except Exception:
                    out[label] = it["result"]
            elif isinstance(it, dict) and "error" in it:
                out[label] = "revert"
            else:
                out[label] = None
        return out
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:120]}"}

VIEWS = [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
         ("freeMinted", "freeMinted()", None), ("freeClaimed", "freeClaimed()", None),
         ("freeLeft", "freeLeft()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None),
         ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
         ("name", "name()", None), ("symbol", "symbol()", None),
         ("agentRegistry", "agentRegistry()", None), ("agentId", "agentId()", None),
         ("quote_user_1", "quote(address,uint256)", "user1"),
         ("cost_user_1", "cost(address,uint256)", "user1"),
         ("balanceOf_user", "balanceOf(address)", "user"),
         ("freeMintedBy_user", "freeMintedBy(address)", "user"),
         ("mintedBy_user", "mintedBy(address)", "user"),
         ("freeClaimed_user", "freeClaimed(address)", "user"),
         ("freeUsed_user", "freeUsed(address)", "user")]

out = {}
for addr, tag in [("0x1fab92b937572c79550aeee51cee77d3add20367", "Mechfarm"), ("0x9D00CF2e1d01c2ecB30BE831ceFf5768976c8396", "SOURCIFY-9D00"), ("0xb43aDB14965ac4470aCe875d06674230bC91B7BB", "SOURCIFY-b43a"), ("0xf2dDE6877dC857f24956d92b972192aC4EF47777", "SOURCIFY-f2dD")]:
    try:
        meta = get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi")
        abi = meta.get("abi") or []
        names = {e["name"] for e in abi if e.get("type") == "function"}
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        mintfree = "mintFree" in names
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        shape = {"verified": True, "verifiedAt": meta.get("verifiedAt"), "n_fns": len(names),
                 "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                 "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token,
                 "fns": sorted(names)}
    except Exception as e:
        shape = {"verified": False, "error": f"{type(e).__name__}: {str(e)[:120]}"}
    code = post([{"jsonrpc": "2.0", "id": 1, "method": "eth_getCode", "params": [addr, "latest"]}])
    codelen = len(code[0].get("result", "")) if isinstance(code, list) else 0
    regbytes = "60b9262456de011f7d15a54cdd8c48baa8b022f" in (code[0].get("result", "").lower() if isinstance(code, list) else "")
    views = batch(addr, VIEWS)
    out[tag] = {"address": addr, "shape": shape, "codelen": codelen,
                "registry_bytes": regbytes, "views": views}
    print(tag, addr)
    print("  shape:", {k: shape.get(k) for k in ("verified", "verifiedAt", "S1", "S2", "has_mint", "has_quote", "free_views", "agent_ref", "is_token", "n_fns")})
    print("  codelen:", codelen, "registry_bytes:", regbytes)
    print("  views:", views)

json.dump(out, open(f"{HF}/run-2026-11-18-1101-newleads.json", "w"), indent=1)
print("saved run-2026-11-18-1101-newleads.json")
