#!/usr/bin/env python3
"""Verify new leads run 1331: Boltbook Fleet 0x5bc4 / Foxglow 0x6e15 / TDAEMON 0xbd1a + Sourcify feed new top 0x23E6/0x381A/0x6A3e/0xE8a8 + DGF CARD re-read. Read-only."""
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
         ("freeUsed_user", "freeUsed(address)", "user"),
         ("claimable_user", "claimable(address)", "user"),
         ("claimed_user", "claimed(address)", "user"),
         ("hasClaimed_user", "hasClaimed(address)", "user"),
         ("endsAt", "endsAt()", None), ("endTime", "endTime()", None),
         ("closesAt", "closesAt()", None), ("isOpen", "isOpen()", None),
         ("saleOpen", "saleOpen()", None), ("freeSupply", "freeSupply()", None),
         ("FREE_CAP", "FREE_CAP()", None), ("agentIdRegistry", "agentIdRegistry()", None),
         ("holdsAgentId_user", "holdsAgentId(address)", "user"),
         ("mintOpensAt", "mintOpensAt()", None), ("mintStart", "mintStart()", None),
         ("startTime", "startTime()", None), ("openAt", "openAt()", None),
         ("price", "price()", None), ("PRICE", "PRICE()", None),
         ("paidMinted", "paidMinted()", None), ("paused", "paused()", None)]

out = {}
for addr, tag in [("0x02A9830b695229d0BcAa39d236778C257b87D85b", "Boltbook-new-02a9-Urbanova"), ("0x83d30e4bb1793d85ac315ed8792d6c1ef1572715", "Boltbook-new-83d3-ZoraAgent"), ("0xa2556377118dD333F9f09600DE0bBCf54Cbc69A0", "Boltbook-new-a255-PTAH-IAO"), ("0xf92e693f43428d5cd1a85acb2cd8e242a717e964", "Boltbook-new-f92e-OrinAgent"), ("0x709DA2371cc7a3aA5c6db0AcE50134D46F424A6f", "Sourcify-new-709D"), ("0x83f087DedE085C33b8e48b8F7150BBEbC9A57777", "Sourcify-new-83f0"), ("0x735543F04ca6a4108AEDDB56E38dD0F06f21cD20", "Sourcify-new-7355"), ("0xc116b90c1Fb4e19cde4Fb93e7546841D4a54A6cB", "Sourcify-new-c116"), ("0x7dF7fD03bD5b7a024B1341849AaD14758f12a4A8", "Sourcify-new-7dF7"), ("0x5E4B06CF354bDFB306D441CAD181f5768053A0CC", "Sourcify-new-5E4B"), ("0x6335Be434795D0A29AEB9bDdbaBdb3fB6E7d5616", "Sourcify-new-6335"), ("0xD69Ee23818204E705788A54FCD39392C071A88c0", "Sourcify-new-D69E"), ("0x4De2E41c5AC19557AA6fe82d90DEb69dFa997777", "Sourcify-new-4De2"), ("0x4F0067581931d9205E848862a7042b5EBc11f0c0", "Sourcify-new-4F00")]:
    try:
        meta = get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi")
        abi = meta.get("abi") or []
        names = {e["name"] for e in abi if e.get("type") == "function"}
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId", "agentRegistry", "agentIdRegistry", "holdsAgentId", "registry", "getAgentId", "agentGate", "AgentGate", "AGENT_ID_REGISTRY", "hasAgentId", "AGENT_ID"})  # 1301 fix kept: agentIdRegistry/holdsAgentId in set
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

json.dump(out, open(f"{HF}/run-2026-11-18-1331-newleads.json", "w"), indent=1)
print("saved run-2026-11-18-1331-newleads.json")
