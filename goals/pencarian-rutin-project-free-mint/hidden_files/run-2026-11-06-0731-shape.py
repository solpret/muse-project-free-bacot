import json, urllib.request, urllib.error, subprocess
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR="0x6d5950B0d93672BAc882251Eb44A5b8c8F1688f5"
FREE=["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freeremaining","free_slots","free_supply","free_amount"]
QUOTE=["quote","quotefor","quotemint","quotemintfor","cost","costfor","getcost","price","mintprice","feefor"]
GATE=["agentid","agentregistry","agent_registry","agentgate","hasagentid","isagent"]
def classify(abi):
    funcs=[it.get("name","") for it in abi if isinstance(it,dict) and it.get("type")=="function"]
    low=[f.lower() for f in funcs]
    mint=[f for f in funcs if "mint" in f.lower()]
    quote=[f for f in funcs if f.lower() in QUOTE or f.lower().startswith("quote") or f.lower().startswith("cost")]
    free=[f for f in funcs if f.lower() in FREE]
    gate=[f for f in funcs if any(g in f.lower() for g in GATE)]
    token=[f for f in funcs if f.lower() in ("name","symbol","decimals","totalsupply")]
    noarg=[f for f in funcs if f.lower() in ("mintfree","mint","claimfree")]
    s1=bool(mint) and bool(quote) and bool(free) and bool(gate)
    s2=len(token)>=3 and bool(noarg) and bool(free) and bool(gate)
    return {"functions":len(funcs),"mint_fns":mint,"quote_fns":quote,"free_views":free,"gate_fns":gate,"token_fns":token,"S1":s1,"S2":s2,"all_funcs":funcs}
abi=None; status="error"
url=f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi"
for attempt in range(3):
    try:
        req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            abi=json.loads(r.read().decode()).get("abi"); status="verified"; break
    except urllib.error.HTTPError as e:
        if e.code==404: status="not_verified"; break
    except Exception as e:
        print("attempt",attempt,"fail",repr(e),flush=True)
if abi is None and status=="error":
    try:
        out=subprocess.run(["curl","-s","--max-time","15",url],capture_output=True,text=True,timeout=20)
        abi=json.loads(out.stdout).get("abi"); status="verified-via-curl"
    except Exception as e:
        print("curl fallback fail",repr(e),flush=True)
res={"address":ADDR,"status":status}
if abi is not None: res.update(classify(abi))
else: res.update({"S1":False,"S2":False})
print(json.dumps(res,indent=1))
json.dump(res, open(f"{BASE}/run-2026-11-06-0731-sourcify-shape.json","w"), indent=1)
