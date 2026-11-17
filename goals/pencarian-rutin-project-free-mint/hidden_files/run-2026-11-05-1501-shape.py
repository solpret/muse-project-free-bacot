import json, urllib.request
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-05-1501"
RPCS=["https://bsc.publicnode.com","https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def raw(to,data,frm=None):
    tx={"to":to,"data":data}
    if frm: tx["from"]=frm
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[tx,"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: out=json.load(r)
            if "error" in out: return {"error":str(out["error"])[:80]}
            return out["result"]
        except Exception: continue
    return {"error":"rpc-fail"}
def cint(v):
    if isinstance(v,dict): return v
    try: return int(v,16) if v and v!="0x" else 0
    except Exception: return v
def cstr(v):
    if isinstance(v,dict) or not v or v=="0x": return v
    try:
        h=v[2:]; ln=int(h[64:128],16); return bytes.fromhex(h[128:128+ln*2]).decode(errors="replace")
    except Exception: return v
def abi_of(a):
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",headers={"User-Agent":"curl"})
        with urllib.request.urlopen(req,timeout=15) as r: d=json.load(r)
        return d.get("abi") or d.get("stdJson",{}).get("abi") or []
    except Exception as e: return {"error":str(e)[:100]}

# --- Sourcify: 4 new vs hot-leg-seen ---
feed=json.load(open(f"{BASE}/run-{TS}-sourcify.json"))
seen=json.load(open(f"{BASE}/hot-leg-seen.json")); seen_l={k.lower() for k in seen}
new=[x["address"] for x in feed["results"] if x["address"].lower() not in seen_l]
excluded=["0x827e83e49bd7e15b67efa0e90fc25f17b8d96124","0x8b47354e7b76b1970a0d06365c8244a810d37493"]
new=[a for a in new if a.lower() not in excluded]
FREE=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed"]
shape={}
for a in new:
    abi=abi_of(a)
    if isinstance(abi,dict):
        shape[a]={"error":abi.get("error"),"S1":False,"S2":False}; print("SHAPE",a,"ABI-ERR",abi.get("error")); continue
    fns=sorted({f.get("name") for f in abi if f.get("type")=="function" and f.get("name")})
    has_mint=any(n.startswith("mint") for n in fns)
    has_quote="quote" in fns
    free=[f for f in fns if any(x in f for x in FREE)]
    agent=("agentRegistry" in fns or "AGENT_REGISTRY" in fns or "registry" in fns or REG in json.dumps(abi).lower())
    is_token=("name" in fns and "symbol" in fns and "decimals" in fns and "totalSupply" in fns)
    has_mintfree="mintFree" in fns
    s1=has_mint and has_quote and bool(free) and agent
    s2=is_token and has_mintfree and ("freeClaimed" in fns or "freeMinted" in fns) and ("FREE_SLOTS" in fns or "FREE_SUPPLY" in fns) and agent
    nft_agent=has_mint and bool(free) and agent
    entry={"abi_functions":fns,"S1":s1,"S2":s2,"nft_agent_shape":nft_agent,"mint":has_mint,"quote":has_quote,"free":free,"agent":agent,"token":is_token,
           "verifiedAt":[x["verifiedAt"] for x in feed["results"] if x["address"].lower()==a.lower()]}
    if s1 or s2 or nft_agent:
        for fn in ["name()","symbol()","totalSupply()"]:
            v=raw(a,sel(fn)); entry[fn]=cstr(v) if fn in ("name()","symbol()") else cint(v)
    shape[a]=entry
    print("SHAPE",a,"S1",s1,"S2",s2,"nft",nft_agent,"mint",has_mint,"quote",has_quote,"free",free,"agent",agent,"token",is_token)
json.dump(shape,open(f"{BASE}/run-{TS}-sourcify-shape.json","w"),indent=1)
print("saved sourcify-shape")

# --- Boltbook light on-chain checks ---
checks={}
# RACKRUSH
a="0x5e42db19a22f5c858dc72df6352495ffff9abb62"
e={}
for fn in ["name()","symbol()","totalSupply()","freeMinted()","FREE_CAP()","MAX_SUPPLY()","paused()"]:
    v=raw(a,sel(fn)); e[fn]=cstr(v) if fn in ("name()","symbol()") else cint(v)
v=raw(a,sel("claimedFree(address)")+enc(USER)); e["claimedFree(user)"]=cint(v)
v=raw(a,sel("contractURI()")); e["contractURI()"]=cstr(v)
checks["RACKRUSH"]=dict(address=a,**e)
print("RACKRUSH",e)
# 0xUN minter: ABI first
a2="0x1E49F0a56D3A431472FBCf50d1cC9C45c9b3c82a"
abi2=abi_of(a2)
if isinstance(abi2,list):
    fns2=sorted({f.get("name") for f in abi2 if f.get("type")=="function" and f.get("name")})
    checks["0xUN_minter"]=dict(address=a2,abi_functions=fns2)
    print("0xUN fns",fns2)
else:
    checks["0xUN_minter"]=dict(address=a2,error=abi2.get("error"))
    print("0xUN ABI err",abi2)
# SWARM mint: ABI + free views
a3="0xC069bE71bf873989a4Ccdb93b65d6667F81DA539"
abi3=abi_of(a3)
if isinstance(abi3,list):
    fns3=sorted({f.get("name") for f in abi3 if f.get("type")=="function" and f.get("name")})
    checks["SWARM_mint"]=dict(address=a3,abi_functions=fns3)
    print("SWARM fns",fns3)
else:
    checks["SWARM_mint"]=dict(address=a3,error=abi3.get("error"))
    print("SWARM ABI err",abi3)
json.dump(checks,open(f"{BASE}/run-{TS}-boltbook-onchain.json","w"),indent=1)
print("saved boltbook-onchain")
