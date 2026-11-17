import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch as _batch
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def raw(addr, views):
    calls=[]; keys=[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc("0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"); key=base+"_user"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        try:
            out=_batch(calls, endpoint=ep, timeout=20)
            if not isinstance(out,list) or len(out)!=len(calls): continue
            return {key:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,key in zip(out,keys)}
        except Exception as e: continue
    return None
def sourcify_abi(addr):
    url=f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r: d=json.load(r)
        abi=d.get("abi")
        if isinstance(abi,list) and abi:
            return {"verified":True,"fns":sorted({f.get("name") for f in abi if isinstance(f,dict) and f.get("type")=="function" and f.get("name")})}
        return {"verified":False,"note":str(d)[:300]}
    except Exception as e:
        return {"verified":False,"error":str(e)}
FREE=["freeClaimed","freeMinted","freeLeft","freeSupply","freeFor","freeUsed","freeAvailable","freeSharesRemaining","freeSharePoolExhausted","freeSharesClaimed","freeOf","freeCount"]
AGENT=["agentRegistry","AGENT_ID_REGISTRY","AGENT_REGISTRY","registry","agentIds","agentTokenIdOf"]
out=json.load(open("run-2026-11-09-0231-feed-shape.json"))
D="0xac3f9a33c653fb3ca49056cfa5edf19101debf97"
out["DOSSIER"]["views"]=raw(D,["totalSupply()","MAX_SUPPLY()","freeLeft()","freeClaimed()","freeMinted()","FREE_SUPPLY()","mintOpen()","price()","balanceOf(address)","freeClaimed(address)"])
out["DOSSIER"]["sourcify"]=sourcify_abi(D)
print("DOSSIER views:", out["DOSSIER"]["views"], "sourcify fns:", out["DOSSIER"]["sourcify"].get("fns"), flush=True)
for a in ["0x4Ed5ff4076eF87839ed38baDe78c085c6Bd9c7b3","0xE202FE765289F6dc90A05c9248AAF7d92D928A4A","0x15eebb55d9A0446B2D76104237C09aB97E1a3318","0x5A1EAE87d3cFa94C72c294D539F6714e3feABbA5","0xb8164afefc53910D7A74cEcE15A60a9e0C86089e"]:
    s=sourcify_abi(a); fns=s.get("fns",[])
    shape={"address":a,"sourcify_verified":s.get("verified"),
      "free":[f for f in fns if any(x.lower() in f.lower() for x in FREE)],
      "mint":[f for f in fns if "mint" in f.lower() or "claim" in f.lower()],
      "quote":[f for f in fns if f.lower() in ("quote","costof","priceof","price","cost")],
      "agent":[f for f in fns if any(x.lower() in f.lower() for x in AGENT)],
      "all_fns":fns}
    shape["S1"]=bool(shape["mint"] and shape["quote"] and shape["free"] and shape["agent"])
    out[a]=shape
    print(a, "verified:", s.get("verified"), "S1:", shape["S1"], "fns:", len(fns), "free:", shape["free"], "mint:", shape["mint"][:8], "agent:", shape["agent"], "err:", s.get("error",""), flush=True)
    time.sleep(1)
json.dump(out, open("run-2026-11-09-0231-feed-shape.json","w"), indent=1)
print("DONE")
