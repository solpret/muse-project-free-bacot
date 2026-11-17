import json, subprocess, sys
d=json.load(open("onchain-scan-2026-11-06-0331.json"))
checked=json.load(open("track-c-scan-checked.json"))
checked_l={k.lower() for k in checked}
lst=sorted(d.get("erc20_mint_contracts_list",[]), key=lambda x:-x.get("mint_count",0))
cands=[e for e in lst if e.get("mint_count",0)>=10 and e["address"].lower() not in checked_l][:20]
print("candidates:", len(cands))
FREE_VIEWS={"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted"}
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
def fetch_abi(addr):
    for attempt in range(3):
        try:
            r=subprocess.run(["curl","-s","-m","30","-A","Mozilla/5.0",
                f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                capture_output=True, text=True, timeout=40)
            if r.returncode==0 and r.stdout.strip():
                data=json.loads(r.stdout)
                if "abi" in data: return ("verified", data["abi"])
                return ("not_verified", None)
        except Exception as e:
            last=str(e)
    return ("error:fetch-failed", None)
out={}
for e in cands:
    a=e["address"]
    st, ab = fetch_abi(a)
    if ab is None:
        out[a]={"run":"0331-2026-11-06","mint_count":e.get("mint_count"),"sourcify":st,"S1":False,"S2":False}
        print(a, e.get("mint_count"), st, "S1 False S2 False", flush=True)
        continue
    names={f.get("name") for f in ab if isinstance(f,dict)}
    src=json.dumps(ab).lower()
    has_mint=any(n and "mint" in n.lower() for n in names)
    has_quote=any(n and ("quote" in n.lower() or "cost" in n.lower() or "price" in n.lower()) for n in names)
    free=sorted(FREE_VIEWS & names)
    agent=REG in src or any("agent" in (n or "").lower() for n in names)
    s1=has_mint and has_quote and bool(free) and agent
    is_token=("name" in names and "symbol" in names and "decimals" in names and "totalSupply" in names)
    s2=is_token and ("mintFree" in names) and bool(free) and agent
    out[a]={"run":"0331-2026-11-06","mint_count":e.get("mint_count"),"sourcify":st,"mint":has_mint,"quote":has_quote,"free_views":free,"agent":agent,"token_shaped":is_token,"S1":s1,"S2":s2}
    print(a, e.get("mint_count"), "S1" if s1 else "", "S2" if s2 else "", "mint",has_mint,"quote",has_quote,"free",free,"agent",agent, flush=True)
json.dump(out, open("trackc-5c-2026-11-06-0331.json","w"), indent=1)
# merge into checked file
for a,v in out.items():
    checked[a]={"source":"run-2026-11-06-0331-5c","S1":v["S1"],"S2":v["S2"],"sourcify":v["sourcify"],"mint_count":v.get("mint_count")}
json.dump(checked, open("track-c-scan-checked.json","w"), indent=1)
print("DONE checked-total:", len(checked))
