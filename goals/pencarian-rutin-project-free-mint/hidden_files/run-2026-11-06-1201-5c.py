#!/usr/bin/env python3
"""Run 2026-11-06 1031 WIB 5c: ERC20 mint_count>=10 shape-check (max 20 new)."""
import json, urllib.request, urllib.error, datetime
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-06-1201"
scan=json.load(open(f"{BASE}/onchain-scan-2026-11-06-1201.json"))
checked=json.load(open(f"{BASE}/track-c-scan-checked.json")) if __import__("os").path.exists(f"{BASE}/track-c-scan-checked.json") else {}
checked_l={k.lower() for k in checked}
cands=[e for e in scan["erc20_mint_contracts_list"] if e["mint_count"]>=10]
cands.sort(key=lambda x:-x["mint_count"])
new=[e for e in cands if e["address"].lower() not in checked_l][:20]
print("5c candidates mint>=10:",len(cands),"new:",len(new),flush=True)
GATE_WORDS=["agentid","agent_id","agentregistry","agent_registry","agentgate","agent_gate","hasagentid","isagent"]
FREE_SHARE_VIEWS=["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freeremaining","free_slots","free_supply","free_amount"]
QUOTE_FNS=["quote","quotefor","quotemint","quotemintfor","cost","costfor","getcost","price","mintprice","feefor"]
def classify(abi):
    funcs=[it.get("name","") for it in abi if isinstance(it,dict) and it.get("type")=="function"]
    mint_fns=[f for f in funcs if "mint" in f.lower()]
    quote_fns=[f for f in funcs if f.lower() in QUOTE_FNS or f.lower().startswith("quote") or f.lower().startswith("cost")]
    free_views=[f for f in funcs if f.lower() in FREE_SHARE_VIEWS]
    gate=[f for f in funcs if any(g in f.lower() for g in GATE_WORDS)]
    token_fns=[f for f in funcs if f.lower() in ("name","symbol","decimals","totalsupply")]
    noarg_free=[f for f in funcs if f.lower() in ("mintfree","mint","claimfree")]
    s1=bool(mint_fns) and bool(quote_fns) and bool(free_views) and bool(gate)
    s2=len(token_fns)>=3 and bool(noarg_free) and bool(free_views) and bool(gate)
    return {"mint_fns":mint_fns,"quote_fns":quote_fns,"free_views":free_views,"gate_fns":gate,"token_fns":token_fns,"S1":s1,"S2":s2}
now_wib=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
out=[]
for e in new:
    a=e["address"]; r={"address":a,"mint_count":e["mint_count"],"distinct_minters":e["distinct_minters"]}
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req,timeout=10) as resp: abi=json.loads(resp.read().decode()).get("abi")
        r["sourcify"]="verified"; r.update(classify(abi))
    except urllib.error.HTTPError as ex:
        r["sourcify"]="not_verified" if ex.code==404 else f"error:{ex.code}"; r["S1"]=False; r["S2"]=False
    except Exception as ex:
        r["sourcify"]=f"error:{ex}"; r["S1"]=False; r["S2"]=False
    out.append(r)
    checked[a]={"checked_wib":now_wib,"source":"scan-1201-5c","S1":r.get("S1"),"S2":r.get("S2"),"sourcify":r["sourcify"],"mint_count_window":e["mint_count"]}
    print("5c",a,"S1=",r.get("S1"),"S2=",r.get("S2"),r["sourcify"],r.get("mint_fns"),r.get("quote_fns"),r.get("free_views"),r.get("gate_fns"),flush=True)
json.dump(checked,open(f"{BASE}/track-c-scan-checked.json","w"),indent=1)
json.dump(out,open(f"{BASE}/run-{TS}-triage-5c.json","w"),indent=1)
print("5C DONE sale shapes:",[r["address"] for r in out if r.get("S1") or r.get("S2")],flush=True)
