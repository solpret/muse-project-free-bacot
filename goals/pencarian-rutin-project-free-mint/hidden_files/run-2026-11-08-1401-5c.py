"""Track-C 5c run 1401: ERC-20 backlog from scan output, mint_count>=10, max 20 new, Sourcify ABI sale-shape test."""
import json, subprocess
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
scan=json.load(open(f"{BASE}/onchain-scan-2026-11-08-1401.json"))
checked=json.load(open(f"{BASE}/track-c-scan-checked.json"))
lst=sorted(scan["erc20_mint_contracts_list"], key=lambda c: -c["mint_count"])
cands=[c for c in lst if c["mint_count"]>=10 and c["address"] not in checked and c["address"].lower() not in {k.lower() for k in checked}]
print(f"ERC20 mint>=10: {sum(1 for c in lst if c['mint_count']>=10)} unique; already-checked skipped: {len(lst)-len(cands)}; to check (cap 20): {min(20,len(cands))}")
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeMint"]
out={}
n=0
for c in cands[:20]:
    a=c["address"]; n+=1
    try:
        p=subprocess.run(["curl","-s","-m","20","-A","Mozilla/5.0",f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"], capture_output=True, text=True, timeout=30)
        d=json.loads(p.stdout); abi=d.get("abi")
        if not isinstance(abi,list):
            out[a]={"mint_count":c["mint_count"],"sourcify":"no-abi","shape":"unknown"}; print(a, c["mint_count"], "no-abi", flush=True); checked[a]="no-abi-1401"; continue
        fns=[e.get("name","") for e in abi if e.get("type")=="function"]
        has_mint=any(x in fns for x in ["mint","mintFree","freeMint","mintShare","buyShare"])
        has_quote=any(x in fns for x in ["quote","cost","price","getQuote","mintQuote"])
        fv=[x for x in fns if any(f.lower() in x.lower() for f in FREE)]
        reg=REG in json.dumps(d).lower()
        is_token=all(x in fns for x in ["name","symbol","decimals","totalSupply"])
        s1=has_mint and has_quote and bool(fv) and reg
        s2=is_token and ("mintFree" in fns or "freeMint" in fns) and bool(fv) and reg
        out[a]={"mint_count":c["mint_count"],"sourcify":"verified","fns":len(fns),"has_mint":has_mint,"has_quote":has_quote,"free_views":fv,"registry":reg,"is_token":is_token,"S1":s1,"S2":s2}
        print(a, c["mint_count"], "fns=",len(fns), "mint=",has_mint,"quote=",has_quote,"fv=",fv,"reg=",reg,"S1=",s1,"S2=",s2, flush=True)
        checked[a]="checked-1401"
    except Exception as e:
        out[a]={"mint_count":c["mint_count"],"error":str(e)[:100]}; print(a, "ERR", str(e)[:100], flush=True); checked[a]="error-1401"
json.dump(out, open(f"{BASE}/run-2026-11-08-1401-5c.json","w"), indent=1)
json.dump(checked, open(f"{BASE}/track-c-scan-checked.json","w"), indent=1)
print(f"5c DONE: checked {n} new, hits S1/S2: {[a for a,v in out.items() if v.get('S1') or v.get('S2')]}")
