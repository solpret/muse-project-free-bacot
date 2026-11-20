#!/usr/bin/env python3
"""Verify new lead run 1231: Mechfarm 0x1fab + Sourcify feed new 0x9D00/0xb43a/0xf2dD (Boltbook ZH, bdnoman.ai post ~4 min ago). Read-only."""
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
         ("mintingOpen", "mintingOpen()", None), ("minter", "minter()", None),
         ("feeRecipient", "feeRecipient()", None), ("mintOpen", "mintOpen()", None),
         ("freeMinted", "freeMinted()", None), ("freeClaimed", "freeClaimed()", None),
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
for addr, tag in [("0x0daca11f7676641f061d1cf25fe6e5ac9f1171e5", "Boltbook-new-0dac"), ("0x50823fd4c14435b8b13e8b03f4d1cfee099687bc", "Boltbook-new-5082"), ("0xa14ffdb8f9ffb5cd7003c969db0da6eee025292c", "Sourcify-new-a14f"), ("0x88ab1d80a3899b5323ac6c7ea6a605582638ff45", "Sourcify-new-88ab"), ("0xae267022c580a394cb81a6e572d68482be9484ae", "Sourcify-new-ae26"), ("0xf449d172c66b2fe8387ddda50546c468f6a019cd", "Sourcify-new-f449"), ("0x4ba4a4a76349cd860b9d3f641b2b4f3da37e2b37", "Sourcify-new-4ba4"), ("0x8b5128b4e01328d3e17c0bf0b5e0ed5006327777", "Sourcify-new-8b51"), ("0x01f9ca4ff95d49594cc8b6591022186dc5c1bc72", "Sweep-DGF-card")]:
    try:
        meta = get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi")
        abi = meta.get("abi") or []
        names = {e["name"] for e in abi if e.get("type") == "function"}
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate", "AGENT_ID_REGISTRY", "hasAgentId", "AGENT_ID"})
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
    regbytes = "60b9262456de011f7d15a54cdd8c48baaa8b022f" in (code[0].get("result", "").lower() if isinstance(code, list) else "")
    views = batch(addr, VIEWS)
    out[tag] = {"address": addr, "shape": shape, "codelen": codelen,
                "registry_bytes": regbytes, "views": views}
    print(tag, addr)
    print("  shape:", {k: shape.get(k) for k in ("verified", "verifiedAt", "S1", "S2", "has_mint", "has_quote", "free_views", "agent_ref", "is_token", "n_fns")})
    print("  codelen:", codelen, "registry_bytes:", regbytes)
    print("  views:", views)

json.dump(out, open(f"{HF}/run-2026-11-18-1231-newleads.json", "w"), indent=1)
print("saved run-2026-11-18-1231-newleads.json")
