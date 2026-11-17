#!/usr/bin/env python3
"""Shape-check the 20 Sourcify-feed-new addresses (triage 2331 skipped them:
legs feed fetch failed, so ERR list was empty). Threaded curl ABI fetch.
Read-only except run-2026-11-12-0001-shape-feed-retry.json. No preview/mint."""
import json, subprocess
from concurrent.futures import ThreadPoolExecutor
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
        "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining","freeSupply","FREE_SUPPLY"]
def curl_json(url, timeout=75):
    r = subprocess.run(["curl","-sL","--max-time",str(timeout),url],capture_output=True,text=True,timeout=timeout+5)
    return json.loads(r.stdout)
def shape(addr):
    d = {"address": addr}
    try:
        meta = curl_json(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,sources")
        abi = meta.get("abi", [])
        fns = [f.get("name") for f in abi if isinstance(f, dict) and f.get("type") == "function"]
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        lnames = {n.lower() for n in names}
        has_quote = bool(lnames & {"quote","cost","getquote","mintcost","price","getprice","mintprice"})
        free_views = sorted(names & set(FREE))
        src = json.dumps(meta.get("sources", {}))
        agent_ref = REG in src.lower() or bool(lnames & {"agentid","agentregistry","registry","getagentid","agentgate","agentidregistry"})
        is_token = bool(names & {"name","symbol","decimals","totalSupply"}) and ("transfer" in names or "balanceOf" in names)
        is_nft = bool(names & {"tokenURI","ownerOf","safeTransferFrom"}) or "uri" in names
        mintfree = "mintFree" in names
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        early = is_nft and (agent_ref or bool(names & {"freeMint","mintFree","claimFree"}))
        d.update({"verified": True, "fn_count": len(names), "has_mint": has_mint, "has_quote": has_quote,
                  "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token, "is_nft": is_nft,
                  "S1": s1, "S2": s2, "early_shape": early})
    except Exception as e:
        d.update({"verified": None, "error": f"{type(e).__name__}: {str(e)[:120]}"})
    print(addr, {k: d.get(k) for k in ("S1","S2","early_shape","has_mint","has_quote","free_views","agent_ref","is_nft","is_token","fn_count","error")}, flush=True)
    return d
addrs = json.load(open(BASE + "run-2026-11-12-0001-feed-new.json")) + ["0xC7E70B8063F33b1ECF8eC6B8A214611A7FAa192F","0xebB62dFAc19e4633775d980246a3eA115bf43B81","0x107778f6eB10f8d9614144c9C4652143394bAeF5"]
print("N:", len(addrs), flush=True)
with ThreadPoolExecutor(max_workers=3) as ex:
    res = list(ex.map(shape, addrs))
out = {"shapes": res,
       "s1_pass": [r["address"] for r in res if r.get("S1")],
       "s2_pass": [r["address"] for r in res if r.get("S2")],
       "early_shape": [r["address"] for r in res if r.get("early_shape")]}
json.dump(out, open(BASE + "run-2026-11-12-0001-shape-feed-retry.json", "w"), indent=1)
print("S1:", out["s1_pass"], "S2:", out["s2_pass"], "EARLY:", out["early_shape"], flush=True)
print("SHAPE-FEED DONE")
