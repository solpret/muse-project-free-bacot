#!/usr/bin/env python3
"""Sourcify shape-check for free-mint-search run 2026-11-13 22:31 WIB.
20 newly verified BSC contracts (verifiedAt 15:30-15:53Z). Read-only.
Checks ABI for agent-mint shape (registry/AgentGate/free-mint) and sale shapes S1/S2.
Writes run-2026-11-13-2231-sourcify-shape.json."""
import json, subprocess, time
REG="0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS={"freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freesupply","free_slots","free_supply","freeamount","freeclaimedbyagent"}
ADDRS=json.load(open('/tmp/sourcify-new-2231.json'))
def fetch_abi(addr):
    url=f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    for att in range(3):
        try:
            out=subprocess.run(["curl","-sL","--max-time","30",url],capture_output=True,text=True,timeout=35).stdout
            d=json.loads(out)
            abi=d.get("abi")
            if abi: return abi, d.get("match","?")
            if "message" in d: return None, d.get("message","")[:80]
        except Exception as e:
            time.sleep(3)
    return None, "fetch-failed"
res={}
for a in ADDRS:
    abi,info=fetch_abi(a)
    if abi is None:
        res[a]={"status":"abi-unavailable","info":info}; print(a,"ABI-UNAVAIL",info,flush=True); continue
    fns=[f.get("name","") for f in abi if f.get("type")=="function"]
    low=[f.lower() for f in fns]
    has_mint=any("mint" in f for f in low)
    has_quote=any(q in f for f in low for q in ("quote","costof","cost","price"))
    has_freeview=any(f in FREE_VIEWS for f in low)
    has_registry=any("agentregistry" in f or "agentgate" in f or "registry" in f for f in low)
    has_free_fn=any(f in ("mintfree","claimfree","freemint","freemintfor","claim") for f in low)
    is_token=all(x in low for x in ("name","symbol","decimals","totalsupply"))
    s1 = has_mint and has_quote and has_freeview and has_registry
    s2 = is_token and has_free_fn and has_freeview and has_registry
    agent = has_registry or has_free_fn or any("free" in f for f in low)
    print(a,"fns=%d"%len(fns),"mint=%s quote=%s freeview=%s registry=%s freefn=%s token=%s -> S1=%s S2=%s agent=%s"%(has_mint,has_quote,has_freeview,has_registry,has_free_fn,is_token,s1,s2,agent),flush=True)
    print("   fns:",",".join(fns)[:300],flush=True)
    res[a]={"status":"checked","fns":fns,"mint":has_mint,"quote":has_quote,"freeview":has_freeview,"registry":has_registry,"freefn":has_free_fn,"token":is_token,"S1":s1,"S2":s2,"agent_shaped":agent,"match":info}
json.dump(res,open("run-2026-11-13-2231-sourcify-shape.json","w"),indent=1)
print("DONE",len(res))
