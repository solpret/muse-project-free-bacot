#!/usr/bin/env python3
"""Route 5c track-C ERC-20 backlog shape-check, run 1901 — READ-ONLY (Sourcify ABI fetch only)."""
import json, urllib.request, time
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeMint","canFreeMint","claimedFree","freeSupply","FREE_SLOTS","FREE_SUPPLY","FREE_AMOUNT"]
def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=timeout).read()
scan = json.load(open("onchain-scan-2026-11-05-1901.json"))
checked = json.load(open("track-c-scan-checked.json"))
checked_keys = {k.lower() for k in checked}
lst = [e for e in scan["erc20_mint_contracts_list"] if e["mint_count"] >= 10]
lst.sort(key=lambda e: -e["mint_count"])
print(f"erc20 total={len(scan['erc20_mint_contracts_list'])} mint>=10: {len(lst)}")
todo = [e for e in lst if e["address"].lower() not in checked_keys][:20]
skipped_already = [e for e in lst if e["address"].lower() in checked_keys]
print(f"already-checked skipped: {len(skipped_already)}; to-check this run (max 20): {len(todo)}; sampling-dropped remainder: {max(0, len(lst)-len(skipped_already)-len(todo))}")
results=[]
for e in todo:
    a = e["address"]
    r = {"address":a,"mint_count":e["mint_count"],"distinct_minters":e["distinct_minters"],"first_block":e["first_block"]}
    try:
        d = json.loads(get(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"))
        abi = d.get("abi") or []
        fns = [f.get("name") for f in abi if f.get("type")=="function"]
        src = json.dumps(d).lower()
        has_mint = any(n and "mint" in n.lower() for n in fns)
        has_quote = any(n and ("quote" in n.lower() or n.lower() in ("costof","cost","price","getprice","getcost")) for n in fns)
        free_views = [n for n in fns if any(fv.lower()==n.lower() or fv.lower() in n.lower() for fv in FREE_VIEWS)]
        has_reg = REG in src or "agentregistry" in src or "agentgate" in src
        is_token = all(any(n==x for n in fns) for x in ("name","symbol","decimals","totalSupply"))
        noarg_free = any(n and n.lower() in ("mintfree","freemint","claimfree") for n in fns)
        s1 = has_mint and has_quote and bool(free_views) and has_reg
        s2 = is_token and noarg_free and bool(free_views) and has_reg
        r.update({"verified":True,"S1":s1,"S2":s2,"mint":has_mint,"quote":has_quote,"free_views":free_views,"registry":has_reg,"is_token":is_token,
                  "verdict":"SALE-SHAPED" if (s1 or s2) else "not-sale-shape"})
    except Exception as ex:
        r.update({"verified":False,"error":str(ex)[:150],"S1":False,"S2":False,"verdict":"abi-fetch-failed"})
    results.append(r)
    print(a, r["verdict"], "mints", e["mint_count"], "S1", r.get("S1"), "S2", r.get("S2"))
    checked[a] = {"source":"run-2026-11-05-1901-5c","status":"checked-sale-shaped" if r["verdict"]=="SALE-SHAPED" else "checked-not-sale-shape",
                  "note":f"S1={r.get('S1')} S2={r.get('S2')} mint={r.get('mint')} quote={r.get('quote')} free={r.get('free_views')} agent={r.get('registry')} token={r.get('is_token')}"}
    time.sleep(0.4)
json.dump(checked, open("track-c-scan-checked.json","w"), indent=1)
json.dump({"run":"2026-11-05-1901","window":[scan.get("from_block"),scan.get("to_block")],
           "erc20_total":len(scan["erc20_mint_contracts_list"]),"mint_ge_10":len(lst),
           "already_checked_skipped":len(skipped_already),"checked_this_run":len(todo),
           "sampling_dropped":max(0,len(lst)-len(skipped_already)-len(todo)),
           "sale_shaped":[r for r in results if r["verdict"]=="SALE-SHAPED"],
           "results":results},
          open("run-2026-11-05-1901-trackc-shape.json","w"), indent=1)
print("sale-shaped:", sum(1 for r in results if r["verdict"]=="SALE-SHAPED"))
print("WROTE run-2026-11-05-1901-trackc-shape.json; checked file updated")
