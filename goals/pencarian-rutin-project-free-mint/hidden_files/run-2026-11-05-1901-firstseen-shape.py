#!/usr/bin/env python3
"""First-seen shape-check for run 1901 — READ-ONLY. No preview/mint/tx."""
import json, urllib.request, time, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
from eth_utils import keccak
def sel(sig): return "0x"+keccak(text=sig).hex()[:8]
def enc_addr(a): return "0x"+a.lower().replace("0x","").rjust(64,"0")
def rpc_call(method, params, timeout=10):
    last=None
    for ep in EPS:
        try: return _single(ep, method, params, timeout, retries=0)
        except Exception as e: last=e
    raise last
def call(addr, data):
    return rpc_call("eth_call", [{"to": addr, "data": data}, "latest"])
def call_int(addr, sig, arg=None):
    data = sel(sig) + (enc_addr(arg)[2:] if arg else "")
    try:
        out = call(addr, data)
        if out in (None,"0x","0x"+"00"*32): return None
        return int(out, 16)
    except Exception: return None
def call_bool(addr, sig, arg=None):
    v = call_int(addr, sig, arg)
    return None if v is None else bool(v)
def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=timeout).read()

scan = json.load(open("onchain-scan-2026-11-05-1901.json"))
seen = json.load(open("onchain-scan-seen.json"))
snap = json.load(open("onchain-snapshot.json"))
seen_keys = {k.lower() for k in seen.get("contracts", {})} | {k.lower() for k in seen.get("known_older_leads", {})}
snap_keys = {k.lower() for k in snap.get("contracts", {})}
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
first_seen = [c for c in scan["contracts"] if c["address"].lower() not in seen_keys and c["address"].lower() not in snap_keys]
print(f"scan contracts={len(scan['contracts'])} first_seen={len(first_seen)}")
results=[]
for c in first_seen:
    a = c["address"]
    r = {"address":a,"kind":c.get("kind"),"name":c.get("name"),"symbol":c.get("symbol"),
         "mint_count":c.get("mint_count"),"distinct_minters":c.get("distinct_minters"),
         "first_block":c.get("first_block"),"last_block":c.get("last_block"),
         "registry_bytes_hit":c.get("registry_bytes_hit"),"sourcify":c.get("sourcify"),
         "scan_free_shaped":c.get("free_shaped"),"scan_mint_funcs":c.get("mint_funcs")}
    # Sourcify ABI
    try:
        d = json.loads(get(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"))
        abi = d.get("abi") or []
        fns = [f.get("name") for f in abi if f.get("type")=="function"]
        src = json.dumps(d).lower()
        r["abi_functions"]=len(fns)
        r["mint_funcs_abi"]=[n for n in fns if n and "mint" in n.lower()][:10]
        r["free_views_abi"]=[n for n in fns if n and any(k in n.lower() for k in ("free","claim"))][:12]
        r["has_registry_ref"]= REG in src or "agentregistry" in src or "agentgate" in src
        r["abi_ok"]=True
    except Exception as e:
        r["abi_ok"]=False; r["abi_error"]=str(e)[:150]; r["has_registry_ref"]=False
        fns=[]
    # on-chain free views (read-only eth_call)
    views={}
    for sig in ["freeMinted()","freeClaimed()","totalMinted()","totalSupply()","MAX_SUPPLY()","FREE_SUPPLY()","FREE_CAP()","freeSupply()","freeLeft()","freeClaimed()"]:
        v = call_int(a, sig)
        if v is not None: views[sig]=v
    for sig in ["canFreeMint(address)","claimedFree(address)","freeClaimed(address)","freeMintedBy(address)","balanceOf(address)"]:
        v = call_int(a, sig, USER)
        if v is not None: views[sig+"(user)"]=v
    for sig in ["mintOpen()","freeMintOpen()"]:
        v = call_bool(a, sig)
        if v is not None: views[sig]=v
    r["onchain_views"]=views
    # registry bytes in deployed code
    try:
        code = rpc_call("eth_getCode", [a, "latest"])
        r["registry_in_code"] = REG in code.lower()
    except Exception:
        r["registry_in_code"]=None
    agent_shaped = bool(r.get("has_registry_ref") or r.get("registry_in_code") or r.get("registry_bytes_hit") or r.get("free_views_abi"))
    free_pool = views.get("FREE_SUPPLY()") is not None and views.get("freeMinted()") is not None and views["freeMinted()"] < views["FREE_SUPPLY()"]
    paid_only = False
    r["agent_shaped"]=agent_shaped
    if agent_shaped and (r.get("mint_count",0) or 0) > 0:
        r["verdict"]="EARLY LEAD"
    elif agent_shaped:
        r["verdict"]="agent-shaped, no mints verified in window"
    else:
        r["verdict"]="not agent-shaped"
    results.append(r)
    print(a, r["name"], r["symbol"], r["verdict"], "views:", views)
    time.sleep(0.3)
json.dump({"scan_window":[scan.get("from_block"),scan.get("to_block")],"latest_block":scan.get("latest_block"),
           "ankr_calls":scan.get("ankr_calls"),"errors":scan.get("errors"),
           "first_seen_count":len(first_seen),"results":results},
          open("run-2026-11-05-1901-scan-firstseen.json","w"), indent=1)
print("WROTE run-2026-11-05-1901-scan-firstseen.json")
