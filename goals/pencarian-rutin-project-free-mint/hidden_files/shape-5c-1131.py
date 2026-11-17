#!/usr/bin/env python3
"""Route 5c shape-check, run 1131. Read-only."""
import json, sys, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
REGISTRY_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
FREE_SHARE_VIEWS = ["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freeslots","freesupply"]
QUOTE_FNS = ["quote","cost","price","getprice","mintprice","mintcost"]
ADDRS = json.load(open("scan-1131-5c-tocheck.json"))
def sourcify_abi(a):
    url = f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r: return ("verified", json.loads(r.read().decode()).get("abi"))
    except urllib.error.HTTPError as e: return ("not_verified" if e.code==404 else f"http_{e.code}", None)
    except Exception as e: return (f"error:{type(e).__name__}", None)
def code(a):
    for ep in EPS:
        try: return _single(ep, "eth_getCode", [a, "latest"], 8, retries=0)
        except Exception: continue
    return None
out=[]
for a in ADDRS:
    st, abi = sourcify_abi(a)
    fns = [f for f in (abi or []) if f.get("type")=="function"] if isinstance(abi,list) else []
    names=[f.get("name","") for f in fns]; lower=[n.lower() for n in names]
    has_mint=any("mint" in n for n in lower)
    has_quote=any(any(q in n for q in QUOTE_FNS) for n in lower)
    free_views=[n for n in names if n.lower() in FREE_SHARE_VIEWS]
    gate=[n for n in names if "agentregistry" in n.lower() or "agentgate" in n.lower() or "agentid" in n.lower() or "agent_id" in n.lower()]
    c=code(a); reg_bytes = bool(c) and REGISTRY_BYTES in c.lower()
    agent = bool(gate) or reg_bytes
    s1 = has_mint and has_quote and bool(free_views) and agent
    is_token = "totalSupply" in names and "decimals" in names
    noarg_free = any(n.lower()=="mintfree" for n in lower)
    s2 = is_token and noarg_free and bool(free_views) and agent
    print(f"{a} {st} mint={has_mint} quote={has_quote} free={free_views} gate={gate} reg_bytes={reg_bytes} S1={s1} S2={s2} fns={len(names)}", flush=True)
    out.append({"address":a,"sourcify":st,"S1":s1,"S2":s2,"has_mint":has_mint,"has_quote":has_quote,"free_views":free_views,"gate":gate,"reg_bytes":reg_bytes,"n_fns":len(names)})
json.dump(out, open("sourcify-feed-1131-5c-shape.json","w"), indent=1)
print("HITS:", [o["address"] for o in out if o["S1"] or o["S2"]])
