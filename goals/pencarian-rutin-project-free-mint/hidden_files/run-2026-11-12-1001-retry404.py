#!/usr/bin/env python3
"""Run 1001 retry404: re-check the 18 still-404 addresses from run 0931."""
import json, urllib.request, concurrent.futures
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
prev = json.load(open(BASE + "run-2026-11-12-0931-retry404.json"))
addrs = prev["still_404"]
def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "free-bacot/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode(errors="replace")
def shape(addr):
    try:
        meta = json.loads(get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=20))
        abi = meta.get("abi", [])
    except Exception as e:
        return {"address": addr, "status": "still-404", "error": f"{type(e).__name__}: {str(e)[:80]}"}
    fns = {}
    for e in abi:
        if e.get("type") == "function":
            fns.setdefault(e["name"], []).append(e)
    names = set(fns); lnames = {n.lower() for n in names}
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(lnames & {"quote", "cost", "getquote", "mintcost", "price", "getprice", "mintprice"})
    free_views = sorted(names & set(FREE_VIEWS))
    agent_ref = bool(lnames & {"agentid", "agentregistry", "registry", "getagentid", "agentgate", "agentidregistry"})
    is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
    mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
    s1 = has_mint and has_quote and bool(free_views) and agent_ref
    s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
    is_nft = bool(names & {"tokenURI", "ownerOf", "safeTransferFrom"}) or "uri" in names
    free_mint_fn = bool(names & {"freeMint", "mintFree", "claimFree"}) or any(n.lower().startswith("freemint") for n in names)
    early_shape = is_nft and (agent_ref or free_mint_fn)
    return {"address": addr, "status": "verified-now", "S1": s1, "S2": s2, "early_shape": early_shape,
            "n_fns": len(abi), "free_views": free_views, "agent_ref": agent_ref}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    res = list(ex.map(shape, addrs))
out = {"run": "2026-11-12 10:01 WIB", "retried": len(addrs),
       "now_verified": [r for r in res if r["status"] == "verified-now"],
       "still_404": [r["address"] for r in res if r["status"] == "still-404"]}
json.dump(out, open(BASE + "run-2026-11-12-1001-retry404.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:3000])
