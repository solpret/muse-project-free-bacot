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
            res={}
            for item,key in zip(out,keys):
                res[key]=None if (isinstance(item,dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item,dict) else None)
            return res
        except Exception: continue
    return None
def sourcify_abi(addr):
    for url in [f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
                f"https://sourcify.dev/server/v2/contracts/56/{addr}"]:
        try:
            req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                d=json.load(r)
            abi=d.get("abi") or d.get("results",[{}])[0].get("abi") if isinstance(d.get("results"),list) else None
            if abi: return {"verified":True,"url":url,"fns":sorted({f.get("name") for f in abi if isinstance(f,dict) and f.get("type")=="function" and f.get("name")})}
            return {"verified":False,"url":url,"note":str(d)[:200]}
        except Exception as e:
            last=str(e)
    return {"verified":False,"error":last}
FREE=["freeClaimed","freeMinted","freeLeft","freeSupply","freeFor","freeUsed","freeAvailable","freeSharesRemaining","freeSharePoolExhausted","freeSharesClaimed","freeOf","freeCount"]
MINT=["mint","mintFree","freeMint","mintWithAgentTokenId","claimFree","publicMint","claim"]
QUOTE=["quote","costOf","priceOf","price","cost"]
AGENT=["agentRegistry","AGENT_ID_REGISTRY","AGENT_REGISTRY","registry","agentIds","agentTokenIdOf"]
out={}
# DOSSIER probe
D="0xac3f9a33c653fb3ca49056cfa5edf19101debf97"
views=["owner()","totalSupply()","MAX_SUPPLY()","freeLeft()","freeClaimed()","freeMinted()","FREE_SUPPLY()","mintOpen()","price()","balanceOf(address)","freeClaimed(address)","name()","symbol()"]
# name/symbol return strings not ints; handle separately via raw call decode later - skip name/symbol int parse (will be None)
d=raw(D, views)
# owner is address: decode from eth_call raw
def raw_addr(addr, sig):
    for ep in EPS:
        try:
            r=_batch([("eth_call",[{"to":addr,"data":sel(sig)},"latest"])], endpoint=ep, timeout=15)[0]
            if r and len(r)>=66: return "0x"+r[-40:]
        except Exception: continue
    return None
owner=raw_addr(D,"owner()")
out["DOSSIER"]={"address":D,"views":d,"owner()":owner,"owner_in_discards": owner=="0x11038f4aa771d9d48b8ac7a184e37a8e5324a9dd","sourcify":sourcify_abi(D)}
print("DOSSIER:", json.dumps(out["DOSSIER"])[:1500], flush=True)
# Sourcify new contracts
for a in ["0x4Ed5ff4076eF87839ed38baDe78c085c6Bd9c7b3","0xE202FE765289F6dc90A05c9248AAF7d92D928A4A","0x15eebb55d9A0446B2D76104237C09aB97E1a3318","0x5A1EAE87d3cFa94C72c294D539F6714e3feABbA5","0xb8164afefc53910D7A74cEcE15A60a9e0C86089e"]:
    s=sourcify_abi(a)
    fns=s.get("fns",[]) if s.get("verified") else []
    low=[f.lower() for f in fns]
    shape={"address":a,"sourcify":s,
      "free":[f for f in fns if any(x.lower() in f.lower() for x in FREE)],
      "mint":[f for f in fns if any(f.lower().startswith(m.lower()) or m.lower() in f.lower() for m in MINT)],
      "quote":[f for f in fns if f.lower() in [q.lower() for q in QUOTE]],
      "agent":[f for f in fns if any(x.lower() in f.lower() for x in AGENT)]}
    shape["S1"]=bool(shape["mint"] and shape["quote"] and shape["free"] and shape["agent"])
    shape["S2"]=False
    out[a]=shape
    print(a, "verified:", s.get("verified"), "S1:", shape["S1"], "free:", shape["free"], "mint:", shape["mint"][:6], "agent:", shape["agent"], flush=True)
    time.sleep(1)
json.dump(out, open("run-2026-11-09-0231-feed-shape.json","w"), indent=1)
print("DONE")
