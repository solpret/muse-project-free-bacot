"""Shape-check 5 new Boltbook-mention contracts, run 1934. Read-only."""
import json, time, urllib.request, urllib.error, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REG_BYTES="60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def rpc(m,p,t=10):
    for ep in EPS:
        try: return _single(ep,m,p,t,retries=0)
        except Exception: continue
    raise Exception("rpc fail")
def sourcify_abi(a, tries=4):
    url=f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"
    for i in range(tries):
        try:
            req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=25) as r:
                return ("verified", json.loads(r.read().decode()).get("abi"))
        except urllib.error.HTTPError as e:
            if e.code==404: return ("not_verified", None)
            time.sleep(4)
        except Exception: time.sleep(4)
    return ("error", None)
def shape(abi, reg):
    if not isinstance(abi,list): return {"S1":False,"S2":False,"reason":"no ABI"}
    fns={i.get("name",""):i for i in abi if i.get("type")=="function"}
    names=set(fns)
    has_mint=any("mint" in n.lower() for n in names)
    quote=[n for n in names if "quote" in n.lower() or "cost" in n.lower()]
    free=[n for n in names if "free" in n.lower() and not n.lower().startswith("freeze")]
    gate=("agentRegistry" in names or "agentId" in names or reg or any("agentgate" in n.lower() for n in names))
    s1=bool(has_mint and quote and free and gate)
    is_token=all(n in names for n in ("name","symbol","decimals","totalSupply"))
    noarg=any(n in names for n in ("mintFree",)) or any(fns[n].get("inputs")==[] and "free" in n.lower() for n in names)
    s2=bool(is_token and noarg and free and gate)
    return {"S1":s1,"S2":s2,"has_mint":has_mint,"quote_fns":quote,"free_views":sorted(free)[:12],"has_gate":gate,"is_token":is_token,"noarg_free":noarg,"fn_count":len(fns)}
ADDRS={
 "0xa5c88342455829fa6e6311ce444475e1a7ff64a2":"Dumpster Royalty/DUMP (6-mints post #3, sensus 326/650)",
 "0x13b8a5dca4e160f115988ba7b6ded26b48f81b26":"MEDUSA SBT (6-mints post #5, soulbound, 205/888)",
 "0x08393dad165d90e7258501fe1dfb5f3498644011":"AgentBox (6-mints post #6, 3839 opened)",
 "0x3c1Be64A8c62f68B442E4189BCEf5Aaf23eA6B3d":"UNIT-404 (unit-404.pages.dev, 1147/2222)",
 "0x9578f8a40228f44f31a9e4bc179e1112f7fa4157":"Gugu Squad/GUGU (192/500, freeMint value 0)",
}
out={}
for a,note in ADDRS.items():
    st,abi=sourcify_abi(a)
    try:
        code=rpc("eth_getCode",[a,"latest"]); reg=REG_BYTES in code[2:].lower()
    except Exception: reg="error"
    sh=shape(abi, reg is True)
    fn=sorted({i.get("name","") for i in abi if i.get("type")=="function"}) if isinstance(abi,list) else None
    out[a]={"note":note,"sourcify":st,"registry_bytes":reg,"shape":sh,"fn_names":fn}
    print(a, note[:40], "->", st, "S1",sh.get("S1"),"S2",sh.get("S2"),"mint",sh.get("has_mint"),"quote",sh.get("quote_fns"),"free",sh.get("free_views"),"gate",sh.get("has_gate"),"fns",sh.get("fn_count"), flush=True)
    time.sleep(1)
json.dump(out, open(HF+"run-2026-11-05-1934-boltbook-shape.json","w"), indent=1)
print("WROTE run-2026-11-05-1934-boltbook-shape.json")
