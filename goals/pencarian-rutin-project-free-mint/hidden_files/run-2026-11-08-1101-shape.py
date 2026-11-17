import json, urllib.request, concurrent.futures
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
def fetch(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"free-mint-search/1101"})
        with urllib.request.urlopen(req, timeout=20) as r:
            meta = json.loads(r.read().decode())
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names) or bool(names & {"claimFreeShare","claimFree","claim"})
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId","agentRegistry","registry","REGISTRY","getAgentId","agentGate","AgentGate","AGENT_ID","AGENT_ID_REGISTRY","agentIdOf","AGENT_REGISTRY","hasAgentId"})
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        mint_shaped = has_mint and bool(free_views)
        return {"address": addr, "verified": True, "S1": s1, "S2": s2, "mint_shaped": mint_shaped, "mint": has_mint, "quote": has_quote, "free": free_views, "agent": agent_ref, "token": is_token, "n_fns": len(names)}
    except Exception as ex:
        return {"address": addr, "verified": False, "error": f"{type(ex).__name__}: {str(ex)[:100]}"}
addrs = json.load(open('/tmp/shape-addrs-1101.json'))
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    out = list(ex.map(fetch, addrs))
for o in out:
    print(json.dumps(o))
json.dump(out, open('run-2026-11-08-1101-shape.json','w'), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
print("MINT_SHAPED:", [o["address"] for o in out if o.get("mint_shaped")])
