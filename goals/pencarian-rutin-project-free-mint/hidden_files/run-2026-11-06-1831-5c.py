#!/usr/bin/env python3
"""Run 2026-11-06 1601 WIB 5c: ERC20 mint_count>=10 shape-check (max 20 new). READ-ONLY; does NOT write track-c-scan-checked.json (parent merges)."""
import json, subprocess, datetime, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-06-1831"
scan=json.load(open(f"{BASE}/run-{TS}-scan.json"))
store=json.load(open(f"{BASE}/track-c-scan-checked.json"))
checked_dict = store.get("checked", {}) if isinstance(store, dict) else {}
already={k.lower() for k in checked_dict.keys()}
already|={k.lower() for k in store.keys() if isinstance(k,str) and k.lower().startswith("0x")}
cands=[e for e in scan["erc20_mint_contracts_list"] if e["mint_count"]>=10]
cands.sort(key=lambda x:-x["mint_count"])
new=[e for e in cands if e["address"].lower() not in already][:20]
dropped=len(cands)-len([e for e in cands if e["address"].lower() not in already][:20])-len([e for e in cands if e["address"].lower() in already])
print(f"5c: ERC20 total={scan['erc20_mint_contracts']} mint>=10={len(cands)} already_checked={len([e for e in cands if e['address'].lower() in already])} new_to_check={len(new)} dropped_sampling_limit={len(cands)-len([e for e in cands if e['address'].lower() in already])-len(new)}",flush=True)
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
    noarg_free=[f for f in funcs if f.lower() in ("mintfree","claimfree")]
    s1=bool(mint_fns) and bool(quote_fns) and bool(free_views) and bool(gate)
    s2=len(token_fns)>=3 and bool(noarg_free) and bool(free_views) and bool(gate)
    return {"mint_fns":mint_fns,"quote_fns":quote_fns,"free_views":free_views,"gate_fns":gate,"token_fns":token_fns,"noarg_free":noarg_free,"S1":s1,"S2":s2}
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
def registry_bytes(addr):
    for ep in EPS:
        try:
            code=_single(ep,"eth_getCode",[addr,"latest"],8,retries=0)
            if isinstance(code,str) and len(code)>2:
                return "60b9262456de011f7d15a54cdd8c48baaa8b022f" in code[2:].lower()
            return None
        except Exception: continue
    return None
def sourcify_abi(addr):
    # curl first (urllib IncompleteRead misclassified CHICK in backfill triage), urllib fallback
    try:
        r=subprocess.run(["curl","-sS","--max-time","20",f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],capture_output=True,text=True,timeout=30)
        if r.returncode==0 and r.stdout.strip():
            d=json.loads(r.stdout)
            if d.get("abi") is not None: return ("verified", d.get("abi"))
            return ("not_verified", None)
    except Exception as e:
        print("  curl sourcify err",addr,e,flush=True)
    import urllib.request, urllib.error
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req,timeout=15) as resp:
            d=json.loads(resp.read().decode())
            return ("verified", d.get("abi")) if d.get("abi") is not None else ("not_verified", None)
    except urllib.error.HTTPError as ex:
        return ("not_verified" if ex.code==404 else f"error:{ex.code}", None)
    except Exception as ex:
        return (f"error:{ex}", None)
now_wib=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
out=[]
for e in new:
    a=e["address"]; r={"address":a,"mint_count":e["mint_count"],"distinct_minters":e["distinct_minters"],"first_block":e["first_block"],"last_block":e["last_block"]}
    st,abi=sourcify_abi(a); r["sourcify"]=st
    if isinstance(abi,list):
        r.update(classify(abi)); r["fns"]=len(abi)
    else:
        r["S1"]=False; r["S2"]=False; r["fns"]=0
    r["registry_bytes"]=registry_bytes(a)
    r["verdict"]="SALE-SHAPE-HIT" if (r.get("S1") or r.get("S2")) else "no-shape"
    out.append(r)
    print("5c",a,"mint_count=",e["mint_count"],"S1=",r.get("S1"),"S2=",r.get("S2"),r["sourcify"],"registry_bytes=",r["registry_bytes"],"mint=",r.get("mint_fns"),"quote=",r.get("quote_fns"),"free=",r.get("free_views"),"gate=",r.get("gate_fns"),flush=True)
json.dump({"run":"2026-11-06-1831","checked_wib":now_wib,"source_scan":"run-2026-11-06-1831-scan.json","window":[scan["from_block"],scan["to_block"]],"erc20_total":scan["erc20_mint_contracts"],"mint_ge10":len(cands),"already_checked":len([e for e in cands if e["address"].lower() in already]),"new_checked":len(out),"dropped_sampling_limit":len(cands)-len([e for e in cands if e["address"].lower() in already])-len(out),"hits":[r for r in out if r.get("S1") or r.get("S2")],"checked":out},open(f"{BASE}/run-{TS}-5c-checked.json","w"),indent=1)
print("5C DONE sale shapes:",[r["address"] for r in out if r.get("S1") or r.get("S2")],flush=True)
